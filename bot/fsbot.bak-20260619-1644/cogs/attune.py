# fsbot/cogs/attune.py — Skill Expression: Attune (v0)
#
# Attune is a Transformative skill:
# - It does NOT reveal more data (that's Perceive)
# - It does NOT grant permission (that's Sneak/Permission skills)
# - It does NOT create tactical advantage
# - It DOES change the relationship between player and place (resonance posture)
#
# Persistence:
# - Stored only in characters.json under extra.status (contract allows this)
#
# Gating:
# - Command is gated via run_bot.py global gate using flags.unlocked_commands
# - Unlock via: await bot.unlock_command(user_id, "attune")

from __future__ import annotations

import random
from typing import Any, Dict, Optional, List

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


def _pick_attune_phrase(room: Dict[str, Any]) -> str:
    """
    Pure tone. No mechanics. No spoilers.
    We allow the room's description/era to flavour the invitation.
    """
    era = str(room.get("era") or "").strip().lower()
    desc = str(room.get("description") or "").strip()

    candidates: List[str] = [
        "You slow your breathing until it matches the room’s tempo.",
        "You stop trying to interpret. You let presence do the work.",
        "You meet the place without asking it to perform for you.",
        "You listen for the room’s consent before you move within it.",
        "You let the moment notice you — gently, without demand.",
    ]

    if "manzo" in era:
        candidates += [
            "A faint hum from the city’s systems seems to recognise your stillness.",
            "The dome-light feels less like illumination and more like a pulse.",
        ]

    if desc:
        candidates += [
            "The details don’t change. Your relationship to them does.",
        ]

    return random.choice(candidates)


class AttuneCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="attune")
    async def attune(self, ctx: commands.Context, *, note: Optional[str] = None):
        """
        Skill: Attune (Transformative)
        Usage:
          !attune            -> attune to current place (toggle)
          !attune <note>     -> attune with a short intent line
          !attune            (again) -> release attunement
        """
        s = self.bot.storage
        user_id = str(ctx.author.id)

        self.bot.state.ensure_player_records(user_id)

        char = s.characters.get(user_id)
        if not isinstance(char, dict):
            await ctx.send("🫧 You try to attune… but you feel unplaced. Try `!look` first.")
            return

        room_id = str(char.get("current_room") or "").strip()
        if not room_id:
            await ctx.send("🫧 You can’t find your footing. Try `!look`.")
            return

        room = s.rooms.get(room_id, {})
        if not isinstance(room, dict):
            await ctx.send("🫧 The world blurs. That place doesn’t resolve right now.")
            return

        status = _ensure_status(char)

        # Toggle
        attuned = bool(status.get("attuned", False))

        if attuned:
            status["attuned"] = False
            status.pop("attune_note", None)
            status.pop("attuned_room_id", None)
            status.pop("attuned_since_world_time", None)
            try:
                s.save_characters()
            except Exception:
                pass
            await ctx.send("🫧 You release the attunement. The room becomes ordinary again — but you remember.")
            return

        # Enter attunement
        status["attuned"] = True
        status["attuned_room_id"] = room_id

        cleaned = (note or "").strip()
        if cleaned:
            status["attune_note"] = cleaned[:180]

        try:
            status["attuned_since_world_time"] = int(getattr(self.bot.state, "world_time_seconds", 0))
        except Exception:
            pass

        try:
            s.save_characters()
        except Exception:
            pass

        phrase = _pick_attune_phrase(room)

        if cleaned:
            await ctx.send(
                "🫧 You attune.\n"
                f"• _{status.get('attune_note')}_\n"
                f"• {phrase}\n\n"
                "_Attunement never forces response. It invites reciprocity._"
            )
        else:
            await ctx.send(
                "🫧 You attune.\n"
                f"• {phrase}\n\n"
                "_Attunement never forces response. It invites reciprocity._"
            )


async def setup(bot):
    await bot.add_cog(AttuneCog(bot))
