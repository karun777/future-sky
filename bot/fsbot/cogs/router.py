# ============================================================
# FILE META — fsbot/cogs/router.py
# Canonical name: Router (run-channel routing & delivery)
#
# Version: v3.6.5
# Last edited: 2026-11-11 (Australia/Perth)
# Amended:
# - W7-F10: recipient ownership checks, safe adoption, private fallback
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

import asyncio
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
    "create_character",
    "awaken",
    "terrace",
    "rat",
    "rehearsal",
    "queen",
    "sequence",
    "idlehome",
    "hud",
    "hud_on",
    "hud_off",
    "hud_state",
    "reincarnate",
    "recovery",
    "pod_delivery",
    "feed7",
    "wardrobe",
    "wear",
    "remove",
    "uniform",
    "fit",
    "search",
    "offer",
    "bar",
    "buy",
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


def _owned_run_channel(bot, guild, channel, user_id):
    """Verify a private account channel; labels and character names are not identity.

    Explicit extra human grants are ambiguous (e.g. an invited visitor), so they
    require operator review. Administrators retain Discord's platform access.
    This does not change world-presence or event-broadcast audience rules.
    """
    try:
        if not isinstance(channel, discord.TextChannel):
            return False
        if channel.guild.id != guild.id:
            return False
        category_id = _players_category_id()
        if category_id:
            if channel.category_id != category_id:
                return False
        elif str(bot.storage.characters.get(user_id, {}).get("run_channel_id")) != str(channel.id):
            # Legacy saved mappings remain usable without creation configuration.
            # Missing category never authorises discovery/adoption.
            return False
        member = guild.get_member(int(user_id))
        if not isinstance(member, discord.Member) or member.bot:
            return False
        if channel.overwrites_for(guild.default_role).view_channel is not False:
            return False
        if channel.overwrites_for(member).view_channel is not True:
            return False
        if not channel.permissions_for(member).view_channel:
            return False
        for target, overwrite in channel.overwrites.items():
            if overwrite.view_channel is not True:
                continue
            if isinstance(target, discord.Role):
                if not target.permissions.administrator:
                    return False
            elif isinstance(target, discord.Member):
                if str(target.id) != user_id and not target.bot:
                    return False
            else:
                return False
        for uid, character in bot.storage.characters.items():
            if str(uid) != user_id and isinstance(character, dict):
                if str(character.get("run_channel_id")) == str(channel.id):
                    return False
        return True
    except Exception:
        return False


def _bind_run_channel(bot, user_id, channel):
    """Do not claim successful attachment after failed persistence."""
    record = bot.storage.characters[user_id]
    present = "run_channel_id" in record
    previous = record.get("run_channel_id")
    record["run_channel_id"] = str(channel.id)
    try:
        bot.storage.save_characters()
    except Exception:
        if present:
            record["run_channel_id"] = previous
        else:
            record.pop("run_channel_id", None)
        return False
    return True


async def ensure_player_run_channel(bot, ctx, user_id, char_name):
    """Resolve the recipient's private play space, independent of caller/name."""
    user_id = str(user_id)
    guild = getattr(ctx, "guild", None)
    if not guild:
        return None
    # Broadcasts can arrive concurrently. Serialize resolution per guild/account.
    locks = getattr(bot, "_run_channel_locks", None)
    if locks is None:
        locks = bot._run_channel_locks = {}
    lock = locks.setdefault((guild.id, user_id), asyncio.Lock())
    async with lock:
        return await _ensure_player_run_channel_locked(bot, guild, user_id, char_name)


async def _ensure_player_run_channel_locked(bot, guild, user_id, char_name):
    try:
        s = bot.storage
        if not isinstance(s.characters.get(user_id), dict):
            return None
        # Resolve recipient, never ctx.author: caller may be another player.
        member = guild.get_member(int(user_id))
        if not isinstance(member, discord.Member) or member.bot:
            return None
        run_id = s.characters[user_id].get("run_channel_id")
        if run_id:
            existing = guild.get_channel(int(run_id))
            # A conflicting saved mapping requires review, not silent replacement.
            if not _owned_run_channel(bot, guild, existing, user_id):
                return None
            await _seed_run_channel_once(bot, user_id, existing)
            return existing

        category = guild.get_channel(_players_category_id())
        if not isinstance(category, discord.CategoryChannel):
            return None

        # Legacy/reset recovery uses explicit recipient permissions, never a slug.
        candidates = [
            ch for ch in category.channels
            if _owned_run_channel(bot, guild, ch, user_id)
        ]
        if len(candidates) > 1:
            return None
        if candidates:
            channel = candidates[0]
        else:
            # If any channel explicitly grants this member access but cannot be
            # verified, do not create a duplicate and conceal the ambiguity.
            if any(isinstance(ch, discord.TextChannel)
                   and ch.overwrites_for(member).view_channel is True
                   for ch in category.channels):
                return None
            bot_member = _resolve_bot_member(guild, bot)
            if bot_member is None:
                return None
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                member: discord.PermissionOverwrite(
                    view_channel=True, send_messages=True, read_message_history=True),
                bot_member: discord.PermissionOverwrite(
                    view_channel=True, send_messages=True, read_message_history=True),
            }
            channel = await guild.create_text_channel(
                name=f"fs-{_slug(char_name)}", category=category, overwrites=overwrites,
                reason="Future Sky: create recipient-owned private run channel")
            if not _owned_run_channel(bot, guild, channel, user_id):
                return None
        if not _bind_run_channel(bot, user_id, channel):
            return None
        await _seed_run_channel_once(bot, user_id, channel)
        return channel
    except Exception:
        return None


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
            if _owned_run_channel(bot, guild, ch, str(user_id)):
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

        if dest:
            return await super().send(content=content, **kwargs)

        # Never leak private output into the command's public/other-player channel.
        # Caller receives its own output by DM; if DM fails, send no payload here.
        try:
            return await self.author.send(content=content, **kwargs)
        except Exception:
            return None


class RouterCog(commands.Cog):
    """
    Infrastructure cog (no commands).
    Exists so this module can be loaded as an extension safely.
    """
    def __init__(self, bot: commands.Bot):
        self.bot = bot


async def setup(bot: commands.Bot):
    await bot.add_cog(RouterCog(bot))
