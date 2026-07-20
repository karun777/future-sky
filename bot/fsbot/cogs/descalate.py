# fsbot/cogs/descalate.py — Skill Expression: Descalate (v0)
#
# Descalate is a Stance / Mode skill:
# - It is not information (Perceive)
# - It is not permission (Sneak)
# - It is not transformation (Attune)
# - It is a posture that reduces force and lowers temperature
#
# Persistence:
# - Stored only in characters.json under extra.status (contract allows this)
#
# Gating:
# - Command is gated via run_bot.py global gate using flags.unlocked_commands
# - Unlock via: await bot.unlock_command(user_id, "descalate")
#
# Note:
# - This cog does not rewrite combat or NPC behaviour yet.
# - It only records stance so other systems can notice later.

from __future__ import annotations

import random
from typing import Dict, Any, Optional, List

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


def _phrase() -> str:
    candidates: List[str] = [
        "You lower your voice — not to persuade, but to reduce harm.",
        "You loosen your grip on certainty and make room for the other to breathe.",
        "You stop feeding the loop. The moment has less fuel now.",
        "You choose non-domination. You choose the smallest gesture that still matters.",
        "You hold your boundaries without sharpening them into weapons.",
    ]
    return random.choice(candidates)


class DescalateCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="descalate")
    async def descalate(self, ctx: commands.Context, *, note: Optional[str] = None):
        """
        Skill: Descalate (Stance/Mode)
        Usage:
          !descalate          -> enter de-escalation stance (toggle)
          !descalate <note>   -> enter with a short intent line
          !descalate          (again) -> release stance
        """
        s = self.bot.storage
        user_id = str(ctx.author.id)

        self.bot.state.ensure_player_records(user_id)

        char = s.characters.get(user_id)
        if not isinstance(char, dict):
            await ctx.send("🫧 You try to de-escalate… but you feel unplaced. Try `!look` first.")
            return

        status = _ensure_status(char)

        active = bool(status.get("deescalating", False))

        if active:
            status["deescalating"] = False
            status.pop("descalate_note", None)
            status.pop("descalate_since_world_time", None)
            try:
                s.save_characters()
            except Exception:
                pass
            await ctx.send("🫧 You release the de-escalation stance. Your presence returns to neutral.")
            return

        status["deescalating"] = True

        cleaned = (note or "").strip()
        if cleaned:
            status["descalate_note"] = cleaned[:180]

        try:
            status["descalate_since_world_time"] = int(getattr(self.bot.state, "world_time_seconds", 0))
        except Exception:
            pass

        try:
            s.save_characters()
        except Exception:
            pass

        p = _phrase()

        if cleaned:
            await ctx.send(
                "🫧 You de-escalate.\n"
                f"• _{status.get('descalate_note')}_\n"
                f"• {p}\n\n"
                "_You don’t win. You reduce harm._"
            )
        else:
            await ctx.send(
                "🫧 You de-escalate.\n"
                f"• {p}\n\n"
                "_You don’t win. You reduce harm._"
            )


async def setup(bot):
    await bot.add_cog(DescalateCog(bot))
