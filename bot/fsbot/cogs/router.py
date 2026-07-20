# ============================================================
# FILE META — fsbot/cogs/router.py
# Canonical name: Router (run-channel routing & delivery)
#
# Version: v3.6.4
# Last edited: 2026-01-23 (Australia/Perth)
# Amended:
# - Feather A1 (lifecycle invoked from routed send): 2026-01-23 (Australia/Perth)
# - Feather A2 (run_channel_id string normalization): 2026-01-23 (Australia/Perth)
# - v3.6.4: harden overwrites + broaden routing allowlist + add extension setup()
#
# Authority:
# - AUTHORITATIVE for run-channel routing and delivery behaviour
#
# Purpose:
# - Routes gameplay command output into per-player run channels
# - Ensures run channels are created, reused, and seeded safely
# - Provides canonical helpers for background systems (combat, ambient,
#   thread nodes, etc.) to deliver player-scoped output without duplicating
#   channel resolution logic
#
# Owns:
# - Run-channel lifecycle (create → seed → reuse)
# - Routing decision logic for gameplay vs non-gameplay commands
# - Best-effort delivery helpers for async/background loops
#
# Reads (authoritative runtime data):
# - storage.characters[user_id]:
#   - run_channel_id
#   - run_seeded_channel_id
#   - character name (for channel slugging)
#
# Writes (minimal, explicit):
# - storage.characters[user_id].run_channel_id  (string channel id OR null)
# - storage.characters[user_id].run_seeded_channel_id (int channel id OR null)
#
# Contract assumptions:
# - Character records already exist and are minimally valid
#   (created/guaranteed elsewhere; see state.ensure_player_records)
# - Router MUST fail soft if:
#     - storage is unavailable
#     - Discord API calls fail
#     - configuration (category id, perms) is missing or invalid
# - Router MUST NOT introduce, mirror, or persist gameplay state
#
# Depends on:
# - discord.py channel/category APIs
# - fsbot.storage (read-mostly, minimal writes)
# - run_bot.py (RunRoutedContext injection)
#
# Used by:
# - All gameplay cogs via ctx.send(...) routing
# - Combat / Ambient / ThreadNodes via send_to_player_run_channel_if_any()
#
# Non-goals:
# - Does not create or validate characters
# - Does not enforce JSON_CONTRACTS
# - Does not own permissions beyond run-channel visibility
# - Does not own narrative or gameplay logic
#
# Status:
# - STABLE (infrastructure layer)
# ============================================================

from __future__ import annotations

import os
import re
from typing import Optional, Set

import discord
from discord.ext import commands

# ---- Routing policy ----
# Only these commands get routed into the player's run channel.
#
# NOTE:
# - This is an allowlist by design (prevents routing admin/mod ops unexpectedly).
# - Keep it broad for player-facing gameplay so UX is consistent.
ROUTE_GAMEPLAY_COMMANDS: Set[str] = {
    # Core / onboarding
    "help",
    "commands",
    "command",
    "time",
    "gametime",

    # Character spine
    "claim_character",
    "character",
    "character_sheet",
    "sheet",

    # Navigation / perception
    "look",
    "here",
    "move",
    "go",

    # Inventory / items
    "inventory",
    "inv",
    "inspect",
    "equip",
    "unequip",
    "use",
    "take",
    "drop",

    # Combat
    "attack",
    "auto_combat",
    "combat_status",

    # Thread nodes / encounters
    "respond",
    "choose",

    # Speech / emotes (player-facing)
    "say",
    "emote",

    # Skill-expression layer (gated elsewhere; routing is harmless)
    "perceive",
    "hold",
    "attune",
    "sneak",
    "descalate",
    "absorb",
    "catalyse",

    # Storage / locker (if you have these commands in core)
    "locker",
    "stash",
    "withdraw",
    "deposit",
    "deposit_efi",
    "claim_efi",
    "efi_tab",

    # Cubes (current cube cog uses !cube)
    "cube",
}

# ---- Run-channel onboarding / pinned guidance ----
RUN_TOPIC = "Future Sky: your private run channel. Commands route here. Ask in #general if stuck."

WELCOME_TEXT = (
    "**This is your run.**\n\n"
    "Everything the game sends *to you* arrives here:\n"
    "- movement, combat, encounters\n"
    "- ambient events\n"
    "- whispers from the Cube\n\n"
    "You can type commands anywhere — responses route here.\n"
    "If you’re stuck, ask in **#general**.\n"
)

DOCS_TO_PIN = [
    ("docs/FS_QUICKSTART.md", "Quickstart"),
    ("docs/FS_COMMANDS.md", "Commands"),
]


def _players_category_id() -> int:
    raw = os.getenv("FS_PLAYERS_CATEGORY_ID", "").strip()
    if not raw:
        return 0
    try:
        return int(raw)
    except ValueError:
        return 0


def _slug(text: str) -> str:
    text = (text or "").strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-{2,}", "-", text).strip("-")
    return text[:40] if text else "player"


def _should_route_ctx(ctx: commands.Context) -> bool:
    """
    Decide whether to route ctx.send(...) into the player's run channel.
    Only route for commands in ROUTE_GAMEPLAY_COMMANDS.
    """
    cmd = getattr(ctx, "command", None)
    if not cmd:
        return False

    # Prefer qualified_name if present (handles groups), but fall back.
    cmd_name = (getattr(cmd, "qualified_name", "") or getattr(cmd, "name", "") or "").lower().strip()

    # If this is a subcommand (e.g. "foo bar"), allow routing if either:
    # - exact qualified name is allowlisted, OR
    # - the root command is allowlisted
    if cmd_name in ROUTE_GAMEPLAY_COMMANDS:
        return True
    root = cmd_name.split(" ", 1)[0] if cmd_name else ""
    return root in ROUTE_GAMEPLAY_COMMANDS


def _is_seeded_for_channel(bot: commands.Bot, user_id: str, channel_id: int) -> bool:
    """
    Hard guard: if we already seeded this exact run channel id for this user,
    never spam welcome/docs again, even if pins/history are unavailable.
    """
    try:
        s = bot.storage
        ch = s.characters.get(user_id) or {}
        return int(ch.get("run_seeded_channel_id") or 0) == int(channel_id)
    except Exception:
        return False


def _mark_seeded_for_channel(bot: commands.Bot, user_id: str, channel_id: int) -> None:
    """Persist that seeding has been done for this channel."""
    try:
        s = bot.storage
        if user_id in s.characters and isinstance(s.characters.get(user_id), dict):
            s.characters[user_id]["run_seeded_channel_id"] = int(channel_id)
            s.save_characters()
    except Exception:
        # seeding guard is best-effort; do not fail gameplay
        pass


async def _seed_run_channel_once(bot: commands.Bot, user_id: str, channel: discord.TextChannel) -> None:
    """
    Seed run channel exactly once per channel id.
    Uses storage guard first; then best-effort topic + welcome + docs (+ pins if possible).
    """
    if _is_seeded_for_channel(bot, user_id, channel.id):
        return

    # Set topic (best-effort)
    try:
        await channel.edit(topic=RUN_TOPIC)
    except Exception:
        pass

    # Welcome (required for marking seeded)
    try:
        welcome_msg = await channel.send(WELCOME_TEXT)
    except Exception:
        return

    # Pin welcome (optional)
    try:
        await welcome_msg.pin()
    except Exception:
        pass

    # Docs (optional)
    for rel_path, label in DOCS_TO_PIN:
        if not os.path.exists(rel_path):
            continue
        try:
            dm = await channel.send(content=f"📎 **{label}**", file=discord.File(rel_path))
            try:
                await dm.pin()
            except Exception:
                pass
        except Exception:
            continue

    # ✅ Mark seeded last, after we have at least posted welcome
    _mark_seeded_for_channel(bot, user_id, channel.id)


def _resolve_bot_member(guild: discord.Guild, bot: commands.Bot) -> Optional[discord.Member]:
    """
    Safely resolve the bot's guild Member for permission overwrites.
    guild.me can be None depending on cache/intents.
    """
    try:
        if getattr(guild, "me", None):
            return guild.me  # type: ignore[return-value]
    except Exception:
        pass

    try:
        if getattr(bot, "user", None) and getattr(bot.user, "id", None):
            m = guild.get_member(int(bot.user.id))
            if isinstance(m, discord.Member):
                return m
    except Exception:
        pass

    return None


async def ensure_player_run_channel(
    bot: commands.Bot,
    ctx: commands.Context,
    user_id: str,
    char_name: str,
) -> Optional[discord.TextChannel]:
    """
    Ensure a per-player run channel exists under the configured Players category.
    Returns the channel (discord.TextChannel) or None.

    Side-effect: when creating or recovering a run channel, we auto-seed it with
    guidance + docs (exactly once per channel id).

    Contract: router never creates characters; if user_id has no character, returns None.
    """
    cat_id = _players_category_id()
    if not cat_id:
        return None

    guild = ctx.guild
    if not guild:
        return None

    # Player must already have a character record
    try:
        s = bot.storage
        if user_id not in s.characters or not isinstance(s.characters.get(user_id), dict):
            return None
    except Exception:
        return None

    category = guild.get_channel(cat_id)
    if not isinstance(category, discord.CategoryChannel):
        # misconfig: fail soft
        return None

    # If we already know it, reuse it (and seed)
    try:
        run_id = s.characters[user_id].get("run_channel_id")
        if run_id:
            existing = guild.get_channel(int(run_id))
            if isinstance(existing, discord.TextChannel):
                try:
                    await _seed_run_channel_once(bot, user_id, existing)
                except Exception:
                    pass
                return existing
    except Exception:
        pass

    channel_name = f"fs-{_slug(char_name)}"

    # Try find existing channel in the category by name
    for ch in category.channels:
        if isinstance(ch, discord.TextChannel) and ch.name == channel_name:
            try:
                # Feather A2: persist as string
                s.characters[user_id]["run_channel_id"] = str(ch.id)
                s.save_characters()
            except Exception:
                pass
            try:
                await _seed_run_channel_once(bot, user_id, ch)
            except Exception:
                pass
            return ch

    bot_member = _resolve_bot_member(guild, bot)

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        ctx.author: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
    }

    # Only set bot overwrite if we can resolve bot member
    if bot_member is not None:
        overwrites[bot_member] = discord.PermissionOverwrite(
            view_channel=True, send_messages=True, read_message_history=True
        )

    try:
        new_ch = await guild.create_text_channel(
            name=channel_name,
            category=category,
            overwrites=overwrites,
            reason="Future Sky: auto-create player run channel",
        )
    except Exception:
        return None

    try:
        # Feather A2: persist as string
        s.characters[user_id]["run_channel_id"] = str(new_ch.id)
        s.save_characters()
    except Exception:
        pass

    try:
        await _seed_run_channel_once(bot, user_id, new_ch)
    except Exception:
        pass

    return new_ch


async def get_run_channel_by_guild_if_any(
    bot: commands.Bot,
    guild: discord.Guild,
    user_id: str,
) -> Optional[discord.TextChannel]:
    """
    Canonical run-channel lookup (non-creating), usable by background loops.

    - Does NOT create channels.
    - Requires only (bot, guild, user_id).
    - Returns discord.TextChannel or None.
    """
    if not guild:
        return None

    try:
        s = bot.storage
        if user_id not in s.characters or not isinstance(s.characters.get(user_id), dict):
            return None

        run_id = s.characters[user_id].get("run_channel_id")
        if run_id:
            ch = guild.get_channel(int(run_id))
            if isinstance(ch, discord.TextChannel):
                return ch
    except Exception:
        return None

    return None


async def send_to_player_run_channel_if_any(
    bot: commands.Bot,
    guild: discord.Guild,
    user_id: str,
    content: str,
    **kwargs,
) -> bool:
    """
    Canonical best-effort delivery for player-scoped output from background loops.

    - Does NOT create channels.
    - Does NOT mutate run_channel_id.
    - Returns True if delivered, False otherwise.
    """
    if not content:
        return False

    try:
        ch = await get_run_channel_by_guild_if_any(bot, guild, user_id)
        if not ch:
            return False
        await ch.send(content=content, **kwargs)
        return True
    except Exception:
        return False


async def get_run_channel_if_any(
    bot: commands.Bot,
    ctx: commands.Context,
    user_id: str,
) -> Optional[discord.TextChannel]:
    """Return the player's run channel if configured and resolvable. Does NOT create."""
    if not ctx or not getattr(ctx, "guild", None):
        return None
    return await get_run_channel_by_guild_if_any(bot, ctx.guild, user_id)


class RunRoutedContext(commands.Context):
    """Routes ctx.send(...) into the player's run channel ONLY for gameplay commands."""

    async def send(self, content=None, **kwargs):
        # DMs / missing guild => no routing
        if not self.guild:
            return await super().send(content=content, **kwargs)

        # Only route gameplay commands
        if not _should_route_ctx(self):
            return await super().send(content=content, **kwargs)

        user_id = str(self.author.id)

        # Player must have a character
        try:
            s = self.bot.storage
            if user_id not in s.characters:
                return await super().send(content=content, **kwargs)
        except Exception:
            return await super().send(content=content, **kwargs)

        # Feather A1: ensure a run channel exists (router owns lifecycle)
        dest = await get_run_channel_by_guild_if_any(self.bot, self.guild, user_id)
        if not dest:
            try:
                char_name = (s.characters.get(user_id) or {}).get("name") or f"wanderer-{user_id[-4:]}"
                dest = await ensure_player_run_channel(self.bot, self, user_id, char_name)
            except Exception:
                dest = None

        # If we have a run channel and it's not the current channel, send there
        if dest and dest.id != self.channel.id:
            return await dest.send(content=content, **kwargs)

        # Otherwise, fall back to current channel
        return await super().send(content=content, **kwargs)


class RouterCog(commands.Cog):
    """
    Infrastructure cog (no commands).
    Exists so this module can be loaded as an extension safely.
    """
    def __init__(self, bot: commands.Bot):
        self.bot = bot


async def setup(bot: commands.Bot):
    await bot.add_cog(RouterCog(bot))
