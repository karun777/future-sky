# fsbot/cogs/sneak.py — Skill Expression: Sneak (v0)
#
# Sneak is a Permission skill:
# - It grants safe access to a class of action that was previously blocked.
# - It does NOT reveal information (Perceive)
# - It does NOT transform the world (Attune)
# - It does NOT confer mechanical advantage (no stealth math)
#
# Persistence:
# - Stored only in characters.json under extra.status (contract allows this)
#
# Gating:
# - Command is gated via run_bot.py global gate using flags.unlocked_commands
# - Unlock via: await bot.unlock_command(user_id, "sneak")
#
# Note:
# - Sneak is a posture. Other systems may choose to respect it (thread nodes, NPCs, movement, etc.)
# - This cog does not change movement rules yet.

from __future__ import annotations

from typing import Any, Dict, Optional

from discord.ext import commands


def _ensure_status(char: Dict[str, Any]) -> Dict[str, Any]:
    extra = char.setdefault("extra", {})
    if not isinstance(extra, dict):
        extra = {}
        char["extra"] = extra
    status = extra.setdefault("status", {})
    if not isinstance(status, dict):
        status = {}
        extra["status"] = status
    return status


class SneakCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="sneak")
    async def sneak(self, ctx: commands.Context, *, note: Optional[str] = None):
        """
        Skill: Sneak (Permission)
        Usage:
          !sneak          -> enter sneak posture (toggle)
          !sneak <note>   -> enter sneak posture with a short intent line
          !sneak          (again) -> release sneak posture
        """
        s = self.bot.storage
        user_id = str(ctx.author.id)

        self.bot.state.ensure_player_records(user_id)

        char = s.characters.get(user_id)
        if not isinstance(char, dict):
            await ctx.send("🫧 You try to sneak… but you feel unplaced. Try `!look` first.")
            return

        status = _ensure_status(char)

        sneaking = bool(status.get("sneaking", False))

        if sneaking:
            status["sneaking"] = False
            status.pop("sneak_note", None)
            status.pop("sneak_since_world_time", None)
            try:
                s.save_characters()
            except Exception:
                pass
            await ctx.send("🫧 You step back out of the shadows. Your presence returns to normal weight.")
            return

        status["sneaking"] = True

        cleaned = (note or "").strip()
        if cleaned:
            status["sneak_note"] = cleaned[:180]

        try:
            status["sneak_since_world_time"] = int(getattr(self.bot.state, "world_time_seconds", 0))
        except Exception:
            pass

        try:
            s.save_characters()
        except Exception:
            pass

        if cleaned:
            await ctx.send(
                "🫧 You move in a quieter register.\n"
                f"• _{status.get('sneak_note')}_\n\n"
                "_Sneak is permission earned — not invisibility claimed._"
            )
        else:
            await ctx.send(
                "🫧 You move in a quieter register.\n\n"
                "_Sneak is permission earned — not invisibility claimed._"
            )


async def setup(bot):
    await bot.add_cog(SneakCog(bot))
