# fsbot/cogs/ambient.py
# Ambient system v2.5
#
# Contract notes:
# - Ambient NEVER creates channels.
# - Ambient NEVER mutates run_channel_id.
# - Ambient NEVER resolves channels independently.
# - Ambient routes ALL player-facing output through router canonical send helpers.
# - All state here is ephemeral (memory-only), safe to lose on restart.
#
# v2.5 changes:
# - Routes canonical character iteration through bot.presence.
# - Routes room resolution through bot.presence.
# - Removes direct ambient-loop iteration over storage.characters.
# - Preserves all existing pacing, Rest, ThreadNodes, routing, and rendering behaviour.
#
# Earlier v2.4 changes retained:
# - Introduces World Moment rendering for ambient output.
# - Introduces Rest v0.1:
#     after long idle, a character gently returns to their reset location.
# - Rest state is memory-only.
# - Reset destination defaults to pod_room.
# - After resting, ambient pauses until the player runs a command again.

import asyncio
import inspect
import random
import re
import time
from typing import Optional

import discord
from discord.ext import commands, tasks

from fsbot.cogs.router import send_to_player_run_channel_if_any


# ============================================================
# Local Console colours
# ============================================================

FS_AMBIENT = 0x555555
FS_ROOM = 0x2F6BFF
FS_CUBE = 0x7C4DFF
FS_REST = 0x1F2633


def _sanitize_run_channel_name(char_name: str) -> str:
    """
    Best-effort legacy helper (no longer used for routing).
    Retained only to avoid breaking imports / expectations.
    """
    base = char_name.strip().lower()
    base = re.sub(r"[^a-z0-9\s-]", "", base)
    base = re.sub(r"\s+", "-", base)
    base = re.sub(r"-+", "-", base).strip("-")
    return f"fs-{base}"


# ============================================================
# Entanglement guard (Thread Nodes)
# ============================================================

def _is_entangled(ch: dict) -> bool:
    """True if the character is in a protected narrative moment."""
    try:
        extra = ch.get("extra")
        if not isinstance(extra, dict):
            return False
        tn = extra.get("thread_nodes")
        if not isinstance(tn, dict):
            return False
        if tn.get("active_thread_node"):
            return True
        if tn.get("active_encounter_id"):
            return True
    except Exception:
        return False
    return False


DEFAULT_GLOBAL_AMBIENT = {
    "cooldowns": {
        "min_idle_seconds": 120,
        "min_seconds_between_events": 90,
        "max_events_per_5min": 2
    },
    "rest": {
        "enabled": True,
        "idle_seconds": 2700,
        "stage_gap_seconds": 30,
        "default_reset_location": "pod_room"
    },
    "fallback_events": [
        "You feel a small hunger arrive like a forgotten message.",
        "You suddenly need to pee. Not urgently. Just… narratively.",
        "A distant thrum reminds you the Lounge is alive."
    ],
    "cube_whispers": [
        "The Cube hums once, low and intimate.",
        "A thin static crawls across your thoughts. It leaves no tracks."
    ]
}


# ============================================================
# Render helpers
# ============================================================

def _moment_embed(kind: str, text: str) -> discord.Embed:
    """
    Render a small World Moment.

    kind is internal grammar:
    - room
    - world
    - cube
    """
    kind = (kind or "world").lower()

    if kind == "room":
        title = "🌫️ THE ROOM BREATHES"
        color = FS_ROOM
        footer = "WORLD MOMENT // ROOM"
    elif kind == "cube":
        title = "🧊 CUBE WHISPER"
        color = FS_CUBE
        footer = "WORLD MOMENT // CUBE"
    else:
        title = "🌫️ WORLD MOMENT"
        color = FS_AMBIENT
        footer = "WORLD MOMENT"

    embed = discord.Embed(
        title=title,
        description=text,
        color=color,
    )
    embed.set_footer(text=footer)
    return embed


def _rest_embed(stage: str) -> discord.Embed:
    """
    Render Rest v0.1 moments.

    stage:
    - first: player begins to wind down
    - second: character returns to anchor
    """
    if stage == "first":
        text = (
            "The music continues without asking anything more of you.\n\n"
            "Some part of you begins to drift back toward safety."
        )
        footer = "REST // WINDING DOWN"
    else:
        text = (
            "You do not remember the journey back.\n\n"
            "When you open your eyes..."
        )
        footer = "REST // ANCHOR FOUND"

    embed = discord.Embed(
        title="🌙 REST",
        description=text,
        color=FS_REST,
    )
    embed.set_footer(text=footer)
    return embed


# ============================================================
# ThreadNodes idle trigger bridge (ctx shim)
# ============================================================

class _AmbientCtx:
    """
    Minimal ctx-like shim so ThreadNodes can send embeds/messages
    without needing a real commands.Context.
    Routes via router canonical send helper.
    """
    def __init__(self, bot: commands.Bot, guild: discord.Guild, user_id: str):
        self.bot = bot
        self._guild = guild
        self._user_id = str(user_id)

    async def send(self, content: str | None = None, *, embed=None):
        try:
            return await send_to_player_run_channel_if_any(
                self.bot,
                self._guild,
                self._user_id,
                content,
                embed=embed,
            )
        except TypeError:
            if embed is not None:
                return await send_to_player_run_channel_if_any(
                    self.bot,
                    self._guild,
                    self._user_id,
                    content,
                    embed,
                )
            return await send_to_player_run_channel_if_any(
                self.bot,
                self._guild,
                self._user_id,
                content,
            )


class AmbientCog(commands.Cog):
    """
    Ambient v2.5:
    - Local room ambient first (room["ambient_events"])
    - Then global ambient fallback after sustained idle
    - Per-player pacing (cooldowns + rolling cap)
    - Anti-repeat memory (per-player)
    - Router-aligned delivery (no channel creation)
    - Ambient output rendered as World Moments
    - Rest v0.1 gently returns long-idle characters to their reset anchor
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

        # user_id -> last time they ran a command (monotonic seconds)
        self._last_action: dict[str, float] = {}

        # user_id -> last time we sent ambient/rest
        self._last_ambient: dict[str, float] = {}

        # user_id -> timestamps of ambient (rolling window)
        self._ambient_history: dict[str, list[float]] = {}

        # user_id -> recent ambient lines
        self._recent_lines: dict[str, list[str]] = {}

        # user_id -> rest sequence started at monotonic seconds
        self._resting: dict[str, float] = {}

        # user_id -> after reset/rest, suppress ambient until player acts again
        self._sleeping: set[str] = set()

        # Storage-owned global ambient config (single persistence boundary)
        s = getattr(self.bot, "storage", None)
        if s and hasattr(s, "load_global_ambient"):
            try:
                self._global = s.load_global_ambient(DEFAULT_GLOBAL_AMBIENT)
            except Exception:
                self._global = dict(DEFAULT_GLOBAL_AMBIENT)
        else:
            self._global = dict(DEFAULT_GLOBAL_AMBIENT)

        self.ambient_loop.start()

    def cog_unload(self):
        self.ambient_loop.cancel()

    # -------------------------
    # Activity tracking
    # -------------------------

    @commands.Cog.listener()
    async def on_command(self, ctx: commands.Context):
        user_id = str(ctx.author.id)
        self._last_action[user_id] = time.monotonic()

        # A player command means consciousness has returned.
        self._resting.pop(user_id, None)
        self._sleeping.discard(user_id)

    def _get_guild(self) -> Optional[discord.Guild]:
        return self.bot.guilds[0] if self.bot.guilds else None

    # -------------------------
    # Selection helpers
    # -------------------------

    def _remember_line(self, user_id: str, line: str) -> None:
        recent = self._recent_lines.get(user_id, [])
        recent = (recent + [line])[-6:]
        self._recent_lines[user_id] = recent

    def _pick_line(self, user_id: str, lines: list[str]) -> Optional[str]:
        if not lines:
            return None
        recent = self._recent_lines.get(user_id, [])
        candidates = [ln for ln in lines if ln not in recent] or lines
        chosen = random.choice(candidates)
        self._remember_line(user_id, chosen)
        return chosen

    def _allowed_by_pacing(self, user_id: str, now: float) -> bool:
        cooldowns = self._global.get("cooldowns", {})
        min_between = int(cooldowns.get("min_seconds_between_events", 90))
        max_per_5min = int(cooldowns.get("max_events_per_5min", 2))

        last = self._last_ambient.get(user_id, 0.0)
        if now - last < min_between:
            return False

        window = 300.0
        hist = [t for t in self._ambient_history.get(user_id, []) if (now - t) <= window]
        if len(hist) >= max_per_5min:
            self._ambient_history[user_id] = hist
            return False

        hist.append(now)
        self._ambient_history[user_id] = hist
        return True

    def _pick_local_then_global(self, user_id: str, room: dict) -> Optional[tuple[str, str]]:
        """
        Returns (kind, line), where kind is room/world/cube.
        """
        local_lines = room.get("ambient_events") or []
        line = self._pick_line(user_id, list(local_lines)) if local_lines else None
        if line:
            return ("room", line)

        fallback = self._global.get("fallback_events", []) or []
        whispers = self._global.get("cube_whispers", []) or []

        if fallback and whispers:
            pool = whispers if random.random() < 0.25 else fallback
        else:
            pool = fallback or whispers

        gline = self._pick_line(user_id, list(pool)) if pool else None
        if not gline:
            return None

        if gline in whispers:
            return ("cube", gline)

        return ("world", gline)

    # -------------------------
    # Rest helpers
    # -------------------------

    def _rest_config(self) -> dict:
        rest = self._global.get("rest", {})
        return rest if isinstance(rest, dict) else {}

    def _rest_enabled(self) -> bool:
        return bool(self._rest_config().get("enabled", True))

    def _rest_after_seconds(self) -> int:
        return int(self._rest_config().get("idle_seconds", 2700))

    def _rest_stage_gap_seconds(self) -> int:
        return int(self._rest_config().get("stage_gap_seconds", 30))

    def _resolve_reset_location(self, char: dict) -> str:
        """
        Reset v0.1 destination resolver.

        Priority:
        1. char["reset_location"]
        2. char["extra"]["reset_location"]
        3. char["extra"]["reset_anchor"]["room"]
        4. global rest.default_reset_location
        5. pod_room
        """
        default = str(self._rest_config().get("default_reset_location", "pod_room"))

        if not isinstance(char, dict):
            return default

        direct = char.get("reset_location")
        if isinstance(direct, str) and direct.strip():
            return direct.strip()

        extra = char.get("extra")
        if isinstance(extra, dict):
            nested = extra.get("reset_location")
            if isinstance(nested, str) and nested.strip():
                return nested.strip()

            anchor = extra.get("reset_anchor")
            if isinstance(anchor, dict):
                room = anchor.get("room")
                if isinstance(room, str) and room.strip():
                    return room.strip()

        return default

    async def _save_characters_if_possible(self) -> None:
        """
        Persist character movement if the active Storage object exposes
        a known save method.

        This is intentionally defensive because storage method names have
        changed during development.
        """
        s = getattr(self.bot, "storage", None)
        if not s:
            return

        candidate_names = (
            "save_characters",
            "save_character_data",
            "save_characters_data",
            "save_all",
            "save",
        )

        for name in candidate_names:
            method = getattr(s, name, None)
            if not callable(method):
                continue

            result = method()
            if inspect.isawaitable(result):
                await result
            return

    async def _send_embed(self, guild: discord.Guild, user_id: str, embed: discord.Embed) -> bool:
        delivered = await send_to_player_run_channel_if_any(
            self.bot,
            guild,
            user_id,
            None,
            embed=embed,
        )
        return bool(delivered)

    async def _maybe_handle_rest(
        self,
        *,
        guild: discord.Guild,
        user_id: str,
        char: dict,
        idle_for: float,
        now: float,
    ) -> bool:
        """
        Returns True if the loop handled this player with a rest action
        and should not continue to normal ambient.
        """
        if not self._rest_enabled():
            return False

        if idle_for < self._rest_after_seconds():
            return False

        # Stage 2: already winding down, now return to anchor.
        if user_id in self._resting:
            started = self._resting[user_id]
            if now - started < self._rest_stage_gap_seconds():
                return True

            reset_location = self._resolve_reset_location(char)
            if isinstance(char, dict):
                char["current_room"] = reset_location

                # Preserve a tiny trace for later debugging / future memory systems.
                extra = char.setdefault("extra", {})
                if isinstance(extra, dict):
                    extra["last_reset"] = {
                        "type": "idle_rest_v0",
                        "location": reset_location,
                    }

            delivered = await self._send_embed(guild, user_id, _rest_embed("second"))
            if delivered:
                self._last_ambient[user_id] = now

            self._resting.pop(user_id, None)
            self._sleeping.add(user_id)
            self._last_action[user_id] = now

            await self._save_characters_if_possible()
            return True

        # Stage 1: initiate winding down.
        delivered = await self._send_embed(guild, user_id, _rest_embed("first"))
        if delivered:
            self._resting[user_id] = now
            self._last_ambient[user_id] = now

        return True

    # -------------------------
    # Main loop
    # -------------------------

    @tasks.loop(seconds=30)
    async def ambient_loop(self):
        await asyncio.sleep(1)

        s = getattr(self.bot, "storage", None)
        presence = getattr(self.bot, "presence", None)
        if not s or not presence:
            return

        guild = self._get_guild()
        if not guild:
            return

        now = time.monotonic()
        min_idle = int(self._global.get("cooldowns", {}).get("min_idle_seconds", 120))

        for user_id, char in list(presence.iter_character_records()):
            try:
                if not isinstance(char, dict):
                    continue

                # After Rest v0.1 completes, suppress ambient until the player acts again.
                if user_id in self._sleeping:
                    continue

                # IMPORTANT: no cube session keys live on character records.
                # If any legacy key exists, we simply ignore it here (non-authoritative).
                if char.get("in_cube"):
                    continue

                # Entanglement guard: do not fire ambient, rest, or idle threadnodes while a narrative fork is active.
                if _is_entangled(char):
                    continue

                last_action = self._last_action.get(user_id, now)
                idle_for = now - last_action

                if idle_for < min_idle:
                    continue

                # Rest v0.1 has priority over normal ambient.
                # It is intentionally not governed by the ambient rolling cap.
                if await self._maybe_handle_rest(
                    guild=guild,
                    user_id=user_id,
                    char=char,
                    idle_for=idle_for,
                    now=now,
                ):
                    continue

                # Respect ambient pacing (this controls BOTH ambient + idle threadnodes).
                if not self._allowed_by_pacing(user_id, now):
                    continue

                room_key = presence.resolve_room_for_user(user_id)

                # --- ThreadNodes: on_idle_room triggers (if available) ---
                # This is intentionally fail-safe and no-op if threadnodes is not patched yet.
                try:
                    tn = self.bot.get_cog("ThreadNodesCog")
                    if tn and hasattr(tn, "maybe_trigger_on_idle"):
                        ctx = _AmbientCtx(self.bot, guild, user_id)

                        try:
                            await tn.maybe_trigger_on_idle(ctx, user_id, room_key)
                        except TypeError:
                            await tn.maybe_trigger_on_idle(ctx, user_id, room_key, idle_for)
                except Exception:
                    pass

                room = s.rooms.get(room_key, {})
                picked = self._pick_local_then_global(
                    user_id,
                    room if isinstance(room, dict) else {},
                )
                if not picked:
                    continue

                kind, line = picked
                delivered = await self._send_embed(guild, user_id, _moment_embed(kind, line))
                if delivered:
                    self._last_ambient[user_id] = now

            except Exception:
                continue

    @ambient_loop.before_loop
    async def before_ambient_loop(self):
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot):
    await bot.add_cog(AmbientCog(bot))
