# fsbot/cogs/narrator.py — Internal Narrator v0.3
#
# Purpose:
# - Delivers private subjective impressions to players.
# - Non-blocking: no choices, no prompts, no entanglement.
# - Sibling system to ThreadNodes, but lighter.
#
# Data:
#   data/narratives/internal_narratives.json
#
# Character state:
#   char["extra"]["narrator"]["seen"]

from __future__ import annotations

import json
import os
import time
import logging
from fsbot.ui.console import internal_embed
from fsbot.cogs.router import get_run_channel_by_guild_if_any
from typing import Any, Dict, Optional, Tuple

from discord.ext import commands

INTERNAL_NARRATIVES_FILE = "data/narratives/internal_narratives.json"
log = logging.getLogger("futuresky")


def _load_narratives() -> Dict[str, Dict[str, Any]]:
    if not os.path.exists(INTERNAL_NARRATIVES_FILE):
        return {}

    with open(INTERNAL_NARRATIVES_FILE, "r", encoding="utf-8-sig") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        return {}

    return {
        str(k): v
        for k, v in data.items()
        if isinstance(v, dict) and not str(k).startswith("_")
    }


class NarratorCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.narratives = _load_narratives()

        # user_id, room_id -> first idle timestamp
        self._idle_seen: Dict[Tuple[str, str], float] = {}

        # user_id -> last sent timestamp
        self._last_sent: Dict[str, float] = {}

        self._min_seconds_between = 8.0
        self._event_subscribed = False

    async def cog_load(self) -> None:
        events = getattr(self.bot, "events", None)
        if events is None or self._event_subscribed:
            return
        events.subscribe("character.entered_room", self._on_character_entered_room)
        self._event_subscribed = True
        log.info("[NARRATOR] subscribed to character.entered_room")

    def cog_unload(self) -> None:
        events = getattr(self.bot, "events", None)
        if events is None or not self._event_subscribed:
            return
        try:
            events.unsubscribe("character.entered_room", self._on_character_entered_room)
        except Exception:
            pass
        self._event_subscribed = False

    def reload_narratives(self):
        self.narratives = _load_narratives()

    def _get_char(self, user_id: str) -> dict:
        ch = self.bot.presence.get_character(str(user_id), ensure=True)
        return ch if isinstance(ch, dict) else {}

    def _save_chars(self):
        if hasattr(self.bot.storage, "save_characters"):
            self.bot.storage.save_characters()

    def _state(self, char: dict) -> dict:
        extra = char.get("extra")
        if not isinstance(extra, dict):
            extra = {}
            char["extra"] = extra

        narrator = extra.get("narrator")
        if not isinstance(narrator, dict):
            narrator = {}
            extra["narrator"] = narrator

        if not isinstance(narrator.get("seen"), list):
            narrator["seen"] = []

        return narrator

    def _seen(self, char: dict) -> list[str]:
        st = self._state(char)
        return st["seen"]

    def _has_seen(self, char: dict, narrative_id: str) -> bool:
        return str(narrative_id) in self._seen(char)

    def _mark_seen(self, char: dict, narrative_id: str):
        seen = self._seen(char)
        nid = str(narrative_id)
        if nid not in seen:
            seen.append(nid)

    def _flags(self, char: dict) -> dict:
        flags = char.get("flags")
        if not isinstance(flags, dict):
            flags = {}
            char["flags"] = flags
        return flags

    def _status(self, char: dict) -> dict:
        extra = char.get("extra")
        if not isinstance(extra, dict):
            return {}
        status = extra.get("status")
        return status if isinstance(status, dict) else {}

    def _requirements_met(self, char: dict, narrative: dict) -> bool:
        triggers = narrative.get("triggers") or {}
        if not isinstance(triggers, dict):
            return False

        flags = self._flags(char)

        flag_set = triggers.get("flag_set")
        if isinstance(flag_set, str) and flag_set.strip():
            if not bool(flags.get(flag_set.strip(), False)):
                return False

        flag_not_set = triggers.get("flag_not_set")
        if isinstance(flag_not_set, str) and flag_not_set.strip():
            if bool(flags.get(flag_not_set.strip(), False)):
                return False

        status_req = triggers.get("status")
        if isinstance(status_req, dict):
            status = self._status(char)

            for key, val in status_req.items():
                try:
                    if str(key).endswith("_min"):
                        stat = str(key).replace("_min", "")
                        if int(status.get(stat, 0)) < int(val):
                            return False

                    if str(key).endswith("_max"):
                        stat = str(key).replace("_max", "")
                        if int(status.get(stat, 0)) > int(val):
                            return False
                except Exception:
                    return False

        return True

    def _pick_on_enter(self, char: dict, room_id: str) -> Optional[str]:
        rid = (room_id or "").strip().lower()
        if not rid:
            return None

        for nid, narrative in self.narratives.items():
            triggers = narrative.get("triggers") or {}
            rooms = triggers.get("on_enter_room") or []
            rooms_norm = {str(r).strip().lower() for r in rooms if str(r).strip()}

            if rid not in rooms_norm:
                continue

            if bool(triggers.get("once_per_character", False)) and self._has_seen(char, nid):
                continue

            if not self._requirements_met(char, narrative):
                continue

            return nid

        return None

    def _pick_on_idle(self, char: dict, room_id: str, user_id: str) -> Optional[str]:
        rid = (room_id or "").strip().lower()
        if not rid:
            return None

        key = (str(user_id), rid)
        now = time.time()

        first_seen = self._idle_seen.get(key)
        if first_seen is None:
            self._idle_seen[key] = now
            return None

        for nid, narrative in self.narratives.items():
            triggers = narrative.get("triggers") or {}

            rooms = triggers.get("on_idle_room") or []
            rooms_norm = {str(r).strip().lower() for r in rooms if str(r).strip()}

            if rid not in rooms_norm:
                continue

            if bool(triggers.get("once_per_character", False)) and self._has_seen(char, nid):
                continue

            min_seconds = int(triggers.get("min_seconds") or 0)
            if min_seconds > 0 and (now - first_seen) < min_seconds:
                continue

            if not self._requirements_met(char, narrative):
                continue

            return nid

        return None

    def _source_label(self, source: str) -> str:
        s = (source or "self").strip().lower()

        if s == "cube":
            return "🧊 CUBE"

        if s == "future_self":
            return "🪶 FUTURE SELF"

        if s == "familiar":
            return "🐾 FAMILIAR"

        if s == "comet":
            return "☄️ COMET"

        return "💭 INTERNAL"

    def _format(self, narrative: dict) -> str:
        source = self._source_label(str(narrative.get("source") or "self"))

        text = narrative.get("text") or []
        if isinstance(text, str):
            lines = [text]
        elif isinstance(text, list):
            lines = [str(x).strip() for x in text if str(x).strip()]
        else:
            lines = []

        if not lines:
            lines = ["A thought passes through you before you can name it."]

        return "\n".join(lines)

    def _record_delivery(self, char: dict, user_id: str, narrative_id: str, narrative: dict, now: float) -> None:
        if bool((narrative.get("triggers") or {}).get("once_per_character", False)):
            self._mark_seen(char, narrative_id)
            self._save_chars()
        self._last_sent[str(user_id)] = now

    async def _send_narrative(self, ctx: commands.Context, user_id: str, narrative_id: str) -> bool:
        now = time.time()
        last = self._last_sent.get(str(user_id), 0)
        if now - last < self._min_seconds_between:
            return False
        narrative = self.narratives.get(str(narrative_id))
        if not isinstance(narrative, dict):
            return False
        char = self._get_char(user_id)
        await ctx.send(embed=internal_embed(self._format(narrative)))
        self._record_delivery(char, user_id, narrative_id, narrative, now)
        return True

    async def _send_narrative_to_run_channel(self, user_id: str, narrative_id: str) -> bool:
        now = time.time()
        last = self._last_sent.get(str(user_id), 0)
        if now - last < self._min_seconds_between:
            return False
        narrative = self.narratives.get(str(narrative_id))
        if not isinstance(narrative, dict):
            return False
        char = self._get_char(user_id)
        embed = internal_embed(self._format(narrative))
        for guild in getattr(self.bot, "guilds", []):
            try:
                channel = await get_run_channel_by_guild_if_any(self.bot, guild, str(user_id))
                if channel is None:
                    continue
                await channel.send(embed=embed)
                self._record_delivery(char, user_id, narrative_id, narrative, now)
                return True
            except Exception as exc:
                log.warning("[NARRATOR] event delivery failed user=%s narrative=%s guild=%s error=%s: %s", user_id, narrative_id, getattr(guild, "id", None), type(exc).__name__, exc)
        log.warning("[NARRATOR] no run channel for event delivery user=%s narrative=%s", user_id, narrative_id)
        return False

    async def _on_character_entered_room(self, event: Dict[str, Any]) -> None:
        source = event.get("source")
        scope = event.get("scope")
        payload = event.get("payload")
        if not isinstance(source, dict) or not isinstance(scope, dict) or not isinstance(payload, dict):
            return
        user_id = source.get("actor_id")
        room_id = payload.get("to_room_id") or scope.get("room_id")
        if user_id is None or not isinstance(room_id, str) or not room_id.strip():
            return
        uid = str(user_id)
        rid = room_id.strip().lower()
        self.reload_narratives()
        char = self._get_char(uid)
        self._idle_seen[(uid, rid)] = time.time()
        narrative_id = self._pick_on_enter(char, rid)
        if not narrative_id:
            return
        delivered = await self._send_narrative_to_run_channel(uid, narrative_id)
        log.info("[NARRATOR_EVENT] event=%s user=%s room=%s narrative=%s delivered=%s", event.get("event_id"), uid, rid, narrative_id, delivered)

    async def maybe_trigger_on_enter(self, ctx: commands.Context, user_id: str, room_id: str):
        try:
            self.reload_narratives()

            char = self._get_char(user_id)

            rid = (room_id or "").strip().lower()
            if rid:
                self._idle_seen[(str(user_id), rid)] = time.time()

            nid = self._pick_on_enter(char, room_id)
            if nid:
                await self._send_narrative(ctx, user_id, nid)

        except Exception:
            return

    async def maybe_trigger_on_idle(self, ctx: commands.Context, user_id: str, room_id: str):
        try:
            self.reload_narratives()

            char = self._get_char(user_id)

            nid = self._pick_on_idle(char, room_id, user_id)
            if nid:
                await self._send_narrative(ctx, user_id, nid)

        except Exception:
            return

    @commands.command(name="narrator_reload")
    async def narrator_reload_cmd(self, ctx: commands.Context):
        self.reload_narratives()
        await ctx.send(f"✅ Reloaded internal narratives ({len(self.narratives)} loaded).")

    @commands.command(name="narrate")
    async def narrate_cmd(self, ctx: commands.Context, narrative_id: str):
        self.reload_narratives()
        await self._send_narrative(ctx, str(ctx.author.id), narrative_id.strip())


async def setup(bot):
    await bot.add_cog(NarratorCog(bot))
