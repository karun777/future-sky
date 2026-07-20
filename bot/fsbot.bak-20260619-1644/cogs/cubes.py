# ============================================================
# FILE META — fsbot/cogs/cubes.py
# Canonical name: CubesCog (cube inspection + safe ensure)
#
# Version: v0.2.0
# Last edited: 2026-01-23
#
# Authority:
# - UI / command surface for cubes. NOT persistence authority.
#
# Purpose:
# - !cube           -> show your personal cube
# - !cube prime     -> show THE Cube (DPC-only)
# - Best-effort ensure personal cube exists (delegates to Storage)
#
# Boundaries:
# - Must not write to characters.json
# - Must not create/alter cube session keys on character records
# - May call Storage.ensure_personal_cube() and Storage.save_cubes() (Storage boundary)
#
# Depends on:
# - bot.storage (Storage)
# - Storage.get_cube / get_personal_cube / ensure_personal_cube / save_cubes
# ============================================================

from __future__ import annotations

from typing import Optional, Dict, Any

import discord
from discord.ext import commands


def _is_dpc(ctx: commands.Context) -> bool:
    try:
        if getattr(ctx.author, "guild_permissions", None) and ctx.author.guild_permissions.administrator:
            return True
        role = discord.utils.get(getattr(ctx.author, "roles", []), name="DPC")
        return role is not None
    except Exception:
        return False


def _owner_text(owner: Any) -> str:
    if isinstance(owner, dict):
        otype = owner.get("type")
        if otype == "player":
            return f"player:{owner.get('user_id', '?')}"
        if otype == "npc":
            return f"npc:{owner.get('name', '?')}"
        if otype:
            return str(otype)
    return "unknown"


def _integrity_text(integ: Any) -> str:
    # Contract expects integrity as dict {current,max}; tolerate legacy scalars
    if isinstance(integ, dict):
        cur = integ.get("current", "?")
        mx = integ.get("max", "?")
        return f"{cur}/{mx}"
    return str(integ) if integ is not None else "?/?"


def _cube_brief(cube: Dict[str, Any]) -> str:
    cid = cube.get("id", "unknown")
    ctype = cube.get("cube_type", "unknown")
    owner_txt = _owner_text(cube.get("owner"))
    integ_txt = _integrity_text(cube.get("integrity"))

    # Keep it compact + consistent for embeds
    return (
        f"**{cid}**\n"
        f"Type: `{ctype}`\n"
        f"Owner: `{owner_txt}`\n"
        f"Integrity: `{integ_txt}`"
    )


class CubesCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="cube")
    async def cube_cmd(self, ctx: commands.Context, which: Optional[str] = None):
        """
        !cube           -> show your personal cube
        !cube prime     -> show THE Cube (DPC-only)
        """
        s = getattr(self.bot, "storage", None)
        if not s:
            await ctx.send("⚠️ Storage not available.")
            return

        which = (which or "").strip().lower()
        user_id = str(ctx.author.id)

        # Prime cube (DPC-only)
        if which in ("prime", "efiishent", "the"):
            if not _is_dpc(ctx):
                await ctx.send("⛔ DPC only.")
                return

            cube = None
            try:
                if hasattr(s, "ensure_efiishent_prime_cube"):
                    s.ensure_efiishent_prime_cube(dpc_user_id=user_id)
                    if hasattr(s, "save_cubes"):
                        s.save_cubes()
                cube = s.get_cube("cube_efiishent_prime") if hasattr(s, "get_cube") else None
            except Exception:
                cube = None

            if not cube or not isinstance(cube, dict):
                await ctx.send("⚠️ Prime cube not found.")
                return

            embed = discord.Embed(title="🧊 THE Cube (Prime)")
            embed.description = _cube_brief(cube)
            await ctx.send(embed=embed)
            return

        # Personal cube
        cube = None
        try:
            cube = s.get_personal_cube(user_id) if hasattr(s, "get_personal_cube") else None
        except Exception:
            cube = None

        # If missing, try to ensure it exists (safe, Storage-owned)
        if not cube and hasattr(s, "ensure_personal_cube"):
            try:
                s.ensure_personal_cube(user_id)
                if hasattr(s, "save_cubes"):
                    s.save_cubes()
                cube = s.get_personal_cube(user_id) if hasattr(s, "get_personal_cube") else None
            except Exception:
                cube = None

        if not cube or not isinstance(cube, dict):
            await ctx.send("⚠️ Personal cube not found (and could not be created).")
            return

        embed = discord.Embed(title="🧊 Personal Cube")
        embed.description = _cube_brief(cube)
        await ctx.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(CubesCog(bot))
