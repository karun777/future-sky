# ============================================================
# FILE META — run_bot.py
# Canonical name: FutureSkyBot Entrypoint (runtime wiring + cog loader)
#
# Version: v3.8.0
# Last edited: 2026-07-17 (Australia/Perth)
#
# Authority:
# - This file is the RUNTIME AUTHORITY for what code is live.
# - The EXTENSIONS list below is the canonical set of loaded cogs (load order matters).
#
# Purpose:
# - Defines the executable entrypoint for the Future Sky Discord bot
# - Instantiates and wires core singletons (Storage, GameState, Presence, ScenarioService, EventBus)
# - Forces RunRoutedContext globally for all commands
# - Loads all gameplay cogs and skill-expression layers
# - Enforces global command gating (flags.unlocked_commands)
# - Starts world heartbeat, audio system, and realm feed integration
#
# Creates / owns:
# - FutureSkyBot (discord.py Bot subclass)
# - bot.storage : Storage
# - bot.state    : GameState
# - bot.presence : Presence
# - bot.scenarios: ScenarioService
# - bot.events   : EventBus
# - bot.unlock_command(...) helper (thread-nodes / effects)
# - bot.send_to_realm_feed(...) helper
#
# Reads (authoritative runtime config / JSON):
# - fsbot.config.VERSION
# - fsbot.config.LAYERS_FILE
# - data/modifiers/layers.json (observability only)
# - Environment:
#   - DISCORD_TOKEN / DISCORD_BOT_TOKEN
#   - FS_RESET_ROOMS_ON_BOOT (indirectly via Storage)
#
# Writes:
# - None directly (delegates persistence to Storage + cogs)
#
# Depends on:
# - fsbot.config (runtime constants, env helpers)
# - fsbot.storage.Storage (JSON authority)
# - fsbot.state.GameState (world clock, heartbeat, era + room resolution)
# - fsbot.presence.Presence (canonical runtime presence queries)
# - fsbot.events.EventBus (fact publication + subscriber dispatch)
# - fsbot.cogs.router.RunRoutedContext
# - discord.py (commands extension)
#
# Operational notes / hazards:
# - Duplicate command names across loaded cogs will cause instability
#   (EXTENSIONS load order matters).
# - Skill commands are gated via flags.unlocked_commands unless DPC/admin.
# - Missing or malformed layers.json is non-fatal but degrades modifiers.
# ============================================================

from __future__ import annotations

import json
import logging
import os
from typing import Set

import discord
from discord.ext import commands
from discord.ext.commands import BadArgument, CommandNotFound, MissingRequiredArgument
from dotenv import load_dotenv

from fsbot.config import (
    VERSION,
    LAYERS_FILE,
    REALM_FEED_CHANNEL_ID,
)
from fsbot.cogs.router import RunRoutedContext
from fsbot.state import GameState
from fsbot.storage import Storage
from fsbot.events import EventBus
from fsbot.presence import Presence
from fsbot.scenarios import ScenarioService

# ---- Env ----
# Loads .env from current working directory (safe no-op if missing)
load_dotenv()

# ---- Logging ----
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("futuresky")

# ---- Intents ----
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = False


# ---- Bot (subclass to force routed context) ----
class FutureSkyBot(commands.Bot):
    async def get_context(self, origin, *, cls=RunRoutedContext):
        # Force our routed context unless an explicit cls is passed
        return await super().get_context(origin, cls=cls)


bot = FutureSkyBot(command_prefix="!", intents=intents, help_command=None)

# ---- Singletons shared across cogs ----
storage = Storage()
state = GameState(storage=storage)
presence = Presence(storage=storage, state=state)
scenarios = ScenarioService(
    world_time_provider=lambda: state.world_time_seconds,
    logger=log,
)

# Attach for easy access in cogs via ctx.bot.<service>
bot.storage = storage    # type: ignore[attr-defined]
bot.state = state        # type: ignore[attr-defined]
bot.presence = presence  # type: ignore[attr-defined]
bot.scenarios = scenarios  # type: ignore[attr-defined]
bot.events = EventBus(logger=log)  # type: ignore[attr-defined]


# ---- Boot integrity checks (observability, not architecture) ----
def _read_layers_count() -> int:
    try:
        if not os.path.exists(LAYERS_FILE):
            return 0
        with open(LAYERS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return len(data) if isinstance(data, list) else 0
    except Exception:
        return 0


def _boot_integrity_check() -> None:
    """
    Non-fatal checks. We do not block startup unless Storage itself failed earlier.
    """
    # Check core singletons
    try:
        assert getattr(bot, "storage", None) is not None
        assert getattr(bot, "state", None) is not None
        assert getattr(bot, "presence", None) is not None
        assert getattr(bot, "scenarios", None) is not None
        assert getattr(bot, "events", None) is not None
    except Exception as e:
        log.error(
            f"❌ Boot integrity failed: bot missing core runtime service: "
            f"{type(e).__name__}: {e}"
        )

    # Check resolve_for_combat exists (combat resolver wiring)
    try:
        if not hasattr(bot.storage, "resolve_for_combat"):
            log.warning("⚠️ Storage has no resolve_for_combat(); resolver wiring may be missing.")
        else:
            log.info("🧩 Resolver bridge: Storage.resolve_for_combat() present.")
    except Exception as e:
        log.warning(f"⚠️ Could not verify resolver bridge: {type(e).__name__}: {e}")

    # Check layers file presence
    try:
        if not os.path.exists(LAYERS_FILE):
            log.warning(f"⚠️ Missing {LAYERS_FILE}. (Storage should auto-create; check perms/paths.)")
        else:
            log.info(f"🧬 Modifier layers file present: {LAYERS_FILE} ({_read_layers_count()} layers)")
    except Exception as e:
        log.warning(f"⚠️ Could not verify modifier layers file: {type(e).__name__}: {e}")


_boot_integrity_check()


# ---- DPC/Admin helper (used for command gate bypass) ----
def is_dpc(ctx: commands.Context) -> bool:
    """
    DPC/admin bypass:
    - Admin perms OR role named 'DPC'
    """
    try:
        if getattr(ctx.author, "guild_permissions", None) and ctx.author.guild_permissions.administrator:
            return True
        role = discord.utils.get(getattr(ctx.author, "roles", []), name="DPC")
        return role is not None
    except Exception:
        return False


# ---- Command Gating ----
GATED_COMMANDS: Set[str] = {
    "sneak",
    "absorb",
    "descalate",
    "catalyse",
    "perceive",
    "hold",
    "attune",
}

GATE_BYPASS_COMMANDS: Set[str] = {
    "help",
    "commands",
    "command",
}


def _get_unlocked_commands(char: dict) -> Set[str]:
    flags = char.setdefault("flags", {})
    raw = flags.get("unlocked_commands", [])
    if not isinstance(raw, list):
        raw = []
        flags["unlocked_commands"] = raw
    return {str(x).strip().lower() for x in raw if str(x).strip()}


async def unlock_command(user_id: str, command_name: str) -> bool:
    """
    Helper for thread-nodes/effects:
      await bot.unlock_command(user_id, "sneak")
    Returns True if newly added, False if it was already unlocked or invalid.
    """
    cmd = str(command_name or "").strip().lower()
    if not cmd:
        return False

    char = bot.presence.get_character(str(user_id), ensure=True)
    if not isinstance(char, dict):
        return False

    flags = char.setdefault("flags", {})
    unlocked = flags.setdefault("unlocked_commands", [])
    if not isinstance(unlocked, list):
        unlocked = []
        flags["unlocked_commands"] = unlocked

    already = {str(x).strip().lower() for x in unlocked if str(x).strip()}
    if cmd in already:
        return False

    unlocked.append(cmd)

    try:
        bot.storage.save_characters()
    except Exception as e:
        log.error(f"Failed to persist unlock_command({cmd}) for {user_id}: {type(e).__name__}: {e}")

    return True


bot.unlock_command = unlock_command  # type: ignore[attr-defined]


@bot.check
async def global_command_gate(ctx: commands.Context) -> bool:
    """
    Hard gate:
    - Only affects commands in GATED_COMMANDS
    - DPC/admin bypass
    - Requires char["flags"]["unlocked_commands"] to include the command
    - Non-spoiler block message
    """
    if ctx.command is None:
        return True

    cmd = (ctx.command.qualified_name or ctx.command.name or "").strip().lower()

    if cmd in GATE_BYPASS_COMMANDS:
        return True

    if cmd not in GATED_COMMANDS:
        return True

    if is_dpc(ctx):
        return True

    user_id = str(ctx.author.id)
    char = bot.presence.get_character(user_id, ensure=True)
    if not isinstance(char, dict):
        return True

    unlocked = _get_unlocked_commands(char)
    if cmd in unlocked:
        return True

    await ctx.send("🚫 You don’t know how to do that yet. Keep exploring — the Lounge teaches in whispers.")
    return False


# ---- Realm Feed (optional) ----
async def send_to_realm_feed(message: str) -> None:
    """
    Best-effort broadcast to the realm feed channel if configured (non-zero).
    """
    if not REALM_FEED_CHANNEL_ID:
        return
    try:
        ch = bot.get_channel(int(REALM_FEED_CHANNEL_ID))
        if ch:
            await ch.send(message)
    except Exception:
        return


bot.send_to_realm_feed = send_to_realm_feed  # type: ignore[attr-defined]


# ---- Extensions (load order matters) ----
EXTENSIONS = [
    # Routing must exist before anything emits output
    "fsbot.cogs.router",

    # Core gameplay layer
    "fsbot.cogs.core",
    "fsbot.cogs.navigation",
    "fsbot.cogs.scenario_engine",
    "fsbot.cogs.combat",
    "fsbot.cogs.ambient",
    "fsbot.cogs.threadnodes",
    "fsbot.cogs.narrator",
    "fsbot.cogs.hud",

    # Social/UX
    "fsbot.cogs.help",
    "fsbot.cogs.emotes",
    "fsbot.cogs.speech",
    "fsbot.cogs.activity",
    "fsbot.cogs.rebirth",

    # Skill Expression Layer (v0 exemplars)
    "fsbot.cogs.perceive",
    "fsbot.cogs.hold",
    "fsbot.cogs.attune",
    "fsbot.cogs.sneak",
    "fsbot.cogs.descalate",
    "fsbot.cogs.absorb",
    "fsbot.cogs.catalyse",

    # Astrology Interface (v0)
    "fsbot.cogs.astro_cog",

    # Cube Interface (v0, optional/parked; safe to fail)
    "fsbot.cogs.cubes",
]


async def _event_probe(event: dict) -> None:
    source = event.get("source") if isinstance(event.get("source"), dict) else {}
    scope = event.get("scope") if isinstance(event.get("scope"), dict) else {}
    log.info(
        "[EVENT_PROBE] type=%s actor=%s room=%s",
        event.get("event_type"),
        source.get("actor_id"),
        scope.get("room_id"),
    )


bot.events.subscribe("character.entered_room", _event_probe)  # type: ignore[attr-defined]


async def load_extensions() -> None:
    for ext in EXTENSIONS:
        try:
            await bot.load_extension(ext)
            log.info(f"🔌 Loaded: {ext}")
        except Exception as e:
            log.error(f"❌ Failed to load {ext}: {type(e).__name__}: {e}")


@bot.event
async def on_ready():
    log.info(f"✅ Future Sky v{VERSION} logged in as {bot.user}")

    try:
        log.info(f"🧬 Modifier layers loaded (count): {_read_layers_count()}")
    except Exception:
        pass

    # 🕰️ EraTimeProfiles sanity check
    try:
        p = bot.state.get_era_time_profile()
        log.info(f"🕰️ EraTimeProfiles loaded: {p.get('label')} mult={p.get('era_time_multiplier')}")
    except Exception as e:
        log.warning(f"⚠️ EraTimeProfiles load check failed: {type(e).__name__}: {e}")

    # ❤️ Heartbeat (v0)
    try:
        bot.state.start_heartbeat(interval_seconds=60)
    except Exception as e:
        log.warning(f"⚠️ Heartbeat start failed: {type(e).__name__}: {e}")

    # Optional audio
    await bot.state.init_audio(bot)


@bot.event
async def on_command(ctx: commands.Context):
    # Proof line — should say RunRoutedContext once working
    log.info(
        f"[CTX] {ctx.author} in #{getattr(ctx.channel, 'name', 'dm')} "
        f"ctx={type(ctx).__name__} cmd={ctx.command}"
    )


@bot.event
async def on_command_error(ctx: commands.Context, error: Exception):
    """
    Friendly error handling:
    - Quiet unknown commands (lets people experiment without journald spam)
    - Usage hints for missing args
    """
    try:
        if ctx.command and hasattr(ctx.command, "on_error"):
            return
    except Exception:
        pass

    if isinstance(error, CommandNotFound):
        return

    if isinstance(error, MissingRequiredArgument):
        name = getattr(ctx.command, "qualified_name", None) or getattr(ctx.command, "name", None) or "command"
        sig = getattr(ctx.command, "signature", "") if ctx.command else ""
        usage = f"!{name} {sig}".strip()
        await ctx.send(f"Usage: `{usage}`")
        return

    if isinstance(error, BadArgument):
        await ctx.send("That didn’t parse. Try again, or use `!help`.")
        return

    log.error(f"Command error: {type(error).__name__}: {error}")
    try:
        await ctx.send("⚠️ Something went wrong. Try again.")
    except Exception:
        pass


async def _setup_hook():
    await load_extensions()


bot.setup_hook = _setup_hook  # type: ignore


def main():
    token = os.getenv("DISCORD_TOKEN") or os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        print("ERROR: Set DISCORD_TOKEN (preferred) or DISCORD_BOT_TOKEN in environment/.env")
        return
    bot.run(token)


if __name__ == "__main__":
    main()
