# fsbot/cogs/absorb.py — Skill Expression: Absorb (v0)
#
# Absorb is a Transformative / Integrative skill:
# - It does NOT reveal more data (Perceive)
# - It does NOT grant permission (Sneak)
# - It does NOT de-escalate a social loop directly (Descalate)
# - It DOES change the relationship to experience: letting it land, metabolise, integrate
#
# Persistence:
# - Stored only in characters.json under extra.status (contract allows this)
#
# Gating:
# - Command is gated via run_bot.py global gate using flags.unlocked_commands
# - Unlock via: await bot.unlock_command(user_id, "absorb")
#
# Note:
# - This cog does not implement memory accumulation yet.
# - It only records posture so reflection/memory systems can notice later.

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
        "You stop reaching for meaning and let meaning reach you.",
        "You let the moment enter you without turning it into a story yet.",
        "You soften the urge to react. You become a vessel for what’s here.",
        "You allow the room to imprint — gently, without possession.",
        "You don’t harvest the experience. You compost it.",
    ]
    return random.choice(candidates)


class AbsorbCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="absorb")
    async def absorb(self, ctx: commands.Context, *, note: Optional[str] = None):
        """
        Skill: Absorb (Transformative/Integrative)
        Usage:
          !absorb          -> enter absorb posture (toggle)
          !absorb <note>   -> enter with a short intent line
          !absorb          (again) -> release posture
        """
        s = self.bot.storage
        user_id = str(ctx.author.id)

        self.bot.state.ensure_player_records(user_id)

        char = s.characters.get(user_id)
        if not isinstance(char, dict):
            await ctx.send("🫧 You try to absorb… but you feel unplaced. Try `!look` first.")
            return

        status = _ensure_status(char)

        active = bool(status.get("absorbing", False))

        if active:
            status["absorbing"] = False
            status.pop("absorb_note", None)
            status.pop("absorb_since_world_time", None)
            try:
                s.save_characters()
            except Exception:
                pass
            await ctx.send("🫧 You release the absorb posture. The moment can move again.")
            return

        status["absorbing"] = True

        cleaned = (note or "").strip()
        if cleaned:
            status["absorb_note"] = cleaned[:180]

        try:
            status["absorb_since_world_time"] = int(getattr(self.bot.state, "world_time_seconds", 0))
        except Exception:
            pass

        try:
            s.save_characters()
        except Exception:
            pass

        p = _phrase()

        if cleaned:
            await ctx.send(
                "🫧 You absorb.\n"
                f"• _{status.get('absorb_note')}_\n"
                f"• {p}\n\n"
                "_Nothing is gained instantly. Something is integrated._"
            )
        else:
            await ctx.send(
                "🫧 You absorb.\n"
                f"• {p}\n\n"
                "_Nothing is gained instantly. Something is integrated._"
            )


async def setup(bot):
    await bot.add_cog(AbsorbCog(bot))
