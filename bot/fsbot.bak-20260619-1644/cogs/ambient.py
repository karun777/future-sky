# fsbot/cogs/ambient.py
# Ambient system v2.3 (router-aligned, Storage-owned IO)
#
# Contract notes:
# - Ambient NEVER creates channels.
# - Ambient NEVER mutates run_channel_id.
# - Ambient NEVER resolves channels independently.
# - Ambient routes ALL player-facing output through router canonical send helpers.
# - All state here is ephemeral (memory-only), safe to lose on restart.
#
# v2.3 changes:
# - Removed local JSON IO helpers (_load_json/_save_json) + json/os imports for persistence.
# - Global ambient config is loaded via Storage boundary:
#     self._global = self.bot.storage.load_global_ambient(DEFAULT_GLOBAL_AMBIENT)

import asyncio
import random
import re
import time
from typing import Optional

import discord
from discord.ext import commands, tasks

from fsbot.cogs.router import send_to_player_run_channel_if_any


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
        "max_events_per_5min": 2,
    },
    "fallback_events": [
        "You feel a small hunger arrive like a forgotten message.",
        "You suddenly need to pee. Not urgently. Just… narratively.",
        "A distant thrum reminds you the Lounge is alive.",
    ],
    "cube_whispers": [
        "The Cube hums once, low and intimate.",
        "A thin static crawls across your thoughts. It leaves no tracks.",
    ],
}


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
        # Router helper should deliver to player's run-channel (or safe fallback)
        try:
            return await send_to_player_run_channel_if_any(
                self.bot,
                self._guild,
                self._user_id,
                content,
                embed=embed,
            )
        except TypeError:
            # Fallback if router helper uses a different signature
            if embed is not None:
                return await send_to_player_run_channel_if_any(self.bot, self._guild, self._user_id, content, embed)
            return await send_to_player_run_channel_if_any(self.bot, self._guild, self._user_id, content)


class AmbientCog(commands.Cog):
    """
    Ambient v2:
    - Local room ambient first (room["ambient_events"])
    - Then global ambient fallback after sustained idle
    - Per-player pacing (cooldowns + rolling cap)
    - Anti-repeat memory (per-player)
    - Router-aligned delivery (no channel creation)
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

        # user_id -> last time they ran a command (monotonic seconds)
        self._last_action: dict[str, float] = {}

        # user_id -> last time we sent ambient
        self._last_ambient: dict[str, float] = {}

        # user_id -> timestamps of ambient (rolling window)
        self._ambient_history: dict[str, list[float]] = {}

        # user_id -> recent ambient lines
        self._recent_lines: dict[str, list[str]] = {}

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
        self._last_action[str(ctx.author.id)] = time.monotonic()

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

    def _pick_local_then_global(self, user_id: str, room: dict) -> Optional[str]:
        local_lines = room.get("ambient_events") or []
        line = self._pick_line(user_id, list(local_lines)) if local_lines else None
        if line:
            return f"🌫️ [ROOM] {line}"

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
            return f"🧊 [CUBE] {gline}"

        return f"🌫️ [WORLD] {gline}"

    # -------------------------
    # Main loop
    # -------------------------

    @tasks.loop(seconds=30)
    async def ambient_loop(self):
        await asyncio.sleep(1)

        s = getattr(self.bot, "storage", None)
        state = getattr(self.bot, "state", None)
        if not s or not state:
            return

        guild = self._get_guild()
        if not guild:
            return

        now = time.monotonic()
        min_idle = int(self._global.get("cooldowns", {}).get("min_idle_seconds", 120))

        for user_id, char in list(getattr(s, "characters", {}).items()):
            try:
                # IMPORTANT: no cube session keys live on character records.
                # If any legacy key exists, we simply ignore it here (non-authoritative).
                if isinstance(char, dict) and char.get("in_cube"):
                    continue

                # Entanglement guard: do not fire ambient or idle threadnodes while a narrative fork is active
                if isinstance(char, dict) and _is_entangled(char):
                    continue

                last_action = self._last_action.get(user_id, now)
                idle_for = (now - last_action)

                if idle_for < min_idle:
                    continue

                # Respect ambient pacing (this controls BOTH ambient + idle threadnodes)
                if not self._allowed_by_pacing(user_id, now):
                    continue

                room_key = state.resolve_room_for_user(user_id)

                # --- ThreadNodes: on_idle_room triggers (if available) ---
                # This is intentionally fail-safe and no-op if threadnodes isn't patched yet.
                try:
                    tn = self.bot.get_cog("ThreadNodesCog")
                    if tn and hasattr(tn, "maybe_trigger_on_idle"):
                        ctx = _AmbientCtx(self.bot, guild, user_id)

                        # Try the simplest signature first
                        try:
                            await tn.maybe_trigger_on_idle(ctx, user_id, room_key)
                        except TypeError:
                            # Tolerate extended signatures (idle seconds / timestamp)
                            await tn.maybe_trigger_on_idle(ctx, user_id, room_key, idle_for)
                except Exception:
                    pass

                room = s.rooms.get(room_key, {})
                msg = self._pick_local_then_global(user_id, room if isinstance(room, dict) else {})
                if not msg:
                    continue

                delivered = await send_to_player_run_channel_if_any(self.bot, guild, user_id, msg)
                if delivered:
                    self._last_ambient[user_id] = now

            except Exception:
                continue

    @ambient_loop.before_loop
    async def before_ambient_loop(self):
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot):
    await bot.add_cog(AmbientCog(bot))
