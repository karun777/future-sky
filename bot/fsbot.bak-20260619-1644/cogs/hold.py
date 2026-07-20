# fsbot/cogs/hold.py — Skill Expression: Hold (v0)
#
# Hold is a Stance / Mode skill:
# - It does NOT reveal information (that's Perceive)
# - It does NOT grant permission to new actions (that's Permission skills)
# - It does NOT transform the world (that's Attune)
# - It DOES legitimise non-action as an active posture
#
# Persistence:
# - Stored only in characters.json under extra.status (contract allows this)
#
# Gating:
# - Command is gated via run_bot.py global gate using flags.unlocked_commands
# - Unlock via: await bot.unlock_command(user_id, "hold")

from __future__ import annotations

from typing import Any, Dict, Optional

from discord.ext import commands


def _safe_get(d: Any, *keys: str, default=None):
    cur = d
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur


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


class HoldCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="hold")
    async def hold(self, ctx: commands.Context, *, note: Optional[str] = None):
        """
        Skill: Hold (Stance/Mode)
        Usage:
          !hold          -> enter hold stance
          !hold <note>   -> enter hold stance with a short intent line
          !hold          (again) -> release hold stance
        """
        s = self.bot.storage
        user_id = str(ctx.author.id)

        # Ensure records exist
        self.bot.state.ensure_player_records(user_id)

        char = s.characters.get(user_id)
        if not isinstance(char, dict):
            await ctx.send("🫧 You try to hold… but you feel unplaced. Try `!look` first.")
            return

        status = _ensure_status(char)

        # Toggle behaviour keeps it reversible without adding a second command
        holding = bool(status.get("holding", False))

        if holding:
            status["holding"] = False
            status.pop("hold_note", None)
            status.pop("hold_since_world_time", None)
            try:
                s.save_characters()
            except Exception:
                pass
            await ctx.send("🫧 You release the hold. The moment starts moving again.")
            return

        # Enter hold stance
        status["holding"] = True

        cleaned = (note or "").strip()
        if cleaned:
            # Keep it short; avoid turning this into journaling UI
            status["hold_note"] = cleaned[:180]

        # Best-effort timestamp from world clock (soft time)
        try:
            status["hold_since_world_time"] = int(getattr(self.bot.state, "world_time_seconds", 0))
        except Exception:
            pass

        try:
            s.save_characters()
        except Exception:
            pass

        if cleaned:
            await ctx.send(
                "🫧 You hold the moment.\n"
                f"• _{status.get('hold_note')}_\n\n"
                "_You don’t fill the silence. You let it become information._"
            )
        else:
            await ctx.send(
                "🫧 You hold the moment.\n\n"
                "_You don’t fill the silence. You let it become information._"
            )


async def setup(bot):
    await bot.add_cog(HoldCog(bot))
