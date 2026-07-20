# fsbot/cogs/catalyse.py — Skill Expression: Catalyse (v0)
#
# Catalyse is a Transformative / Ignition skill:
# - It does NOT reveal information (Perceive)
# - It does NOT grant permission (Sneak)
# - It does NOT de-escalate (Descalate)
# - It is not "energy gain" or "buff"
# - It DOES mark the choice to begin a process (commitment without force)
#
# Persistence:
# - Stored only in characters.json under extra.status (contract allows this)
#
# Gating:
# - Command is gated via run_bot.py global gate using flags.unlocked_commands
# - Unlock via: await bot.unlock_command(user_id, "catalyse")
#
# Note:
# - This cog does not implement consequence chains yet.
# - It records posture so other systems can notice later.

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
        "You stop orbiting the choice and step into it.",
        "A small spark: not intensity, but direction.",
        "You commit to the next honest motion — without forcing the outcome.",
        "You begin the process gently, like lighting a lamp instead of a fire.",
        "You shift from contemplation to initiation. The world can respond now.",
    ]
    return random.choice(candidates)


class CatalyseCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="catalyse")
    async def catalyse(self, ctx: commands.Context, *, note: Optional[str] = None):
        """
        Skill: Catalyse (Transformative/Ignition)
        Usage:
          !catalyse          -> enter catalyse posture (toggle)
          !catalyse <note>   -> enter with a short intent line
          !catalyse          (again) -> release posture
        """
        s = self.bot.storage
        user_id = str(ctx.author.id)

        self.bot.state.ensure_player_records(user_id)

        char = s.characters.get(user_id)
        if not isinstance(char, dict):
            await ctx.send("🫧 You try to catalyse… but you feel unplaced. Try `!look` first.")
            return

        status = _ensure_status(char)

        active = bool(status.get("catalysing", False))

        if active:
            status["catalysing"] = False
            status.pop("catalyse_note", None)
            status.pop("catalyse_since_world_time", None)
            try:
                s.save_characters()
            except Exception:
                pass
            await ctx.send("🫧 You release the catalyse posture. You can wait again without self-betrayal.")
            return

        status["catalysing"] = True

        cleaned = (note or "").strip()
        if cleaned:
            status["catalyse_note"] = cleaned[:180]

        try:
            status["catalyse_since_world_time"] = int(getattr(self.bot.state, "world_time_seconds", 0))
        except Exception:
            pass

        try:
            s.save_characters()
        except Exception:
            pass

        p = _phrase()

        if cleaned:
            await ctx.send(
                "🫧 You catalyse.\n"
                f"• _{status.get('catalyse_note')}_\n"
                f"• {p}\n\n"
                "_Not force. Not speed. Just ignition._"
            )
        else:
            await ctx.send(
                "🫧 You catalyse.\n"
                f"• {p}\n\n"
                "_Not force. Not speed. Just ignition._"
            )


async def setup(bot):
    await bot.add_cog(CatalyseCog(bot))
