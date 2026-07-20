# fsbot/cogs/perceive.py — Skill Expression: Perceive (v0)
#
# Perceive is a Perceptual skill:
# - It does NOT grant access or power.
# - It clarifies signal without increasing raw data.
# - It must remain non-mechanical: no rolls, no %s, no stat talk.
#
# Gating:
# - Command is gated via run_bot.py global gate using flags.unlocked_commands.
# - Unlock via: await bot.unlock_command(user_id, "perceive")

from __future__ import annotations

import random
from typing import Dict, Any, List, Optional

from discord.ext import commands


def _safe_get(d: Any, *keys: str, default=None):
    cur = d
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur


def _awareness_label(char: Dict[str, Any]) -> str:
    """
    Best-effort awareness resolution.
    We do NOT store awareness as a skill stat.
    If absent, default to 'automatic'.
    """
    raw = _safe_get(char, "extra", "status", "awareness_state", default=None)
    if not raw:
        return "automatic"
    s = str(raw).strip().lower()
    if s in {"unconscious", "automatic", "attentive", "insightful"}:
        return s
    return "automatic"


def _format_perceive(
    room_id: str,
    room: Dict[str, Any],
    awareness: str,
) -> str:
    """
    Generate a small set of 'signals' without dumping data.
    """
    desc = str(room.get("description") or "").strip()
    exits = room.get("exits") if isinstance(room.get("exits"), dict) else {}
    items = room.get("items") if isinstance(room.get("items"), list) else []
    enemies = room.get("enemies") if isinstance(room.get("enemies"), list) else []

    lines: List[str] = []

    # Start line varies by awareness (tone only, not power)
    opener = {
        "unconscious": "👁️ You try to take it in, but your attention skims the surface.",
        "automatic": "👁️ You let your eyes soften and listen for what the room is already saying.",
        "attentive": "👁️ You slow down. You watch the edges, not the centre.",
        "insightful": "👁️ You notice the shape of the moment, not just the room.",
    }.get(awareness, "👁️ You take a careful look.")

    lines.append(opener)

    # Signal: one exit cue (never full exit list unless it's already obvious)
    exit_keys = list(exits.keys()) if exits else []
    if exit_keys:
        k = random.choice(exit_keys)
        # Phrase differently to avoid 'menu' feel
        exit_line = {
            "unconscious": f"Something about the {k} way pulls at you, but you can’t name why.",
            "automatic": f"The {k} way feels more travelled than it looks.",
            "attentive": f"You catch a subtle rhythm of movement toward the {k} way.",
            "insightful": f"The {k} way isn’t just an exit — it’s a decision the room remembers.",
        }.get(awareness, f"You sense a draw toward the {k} way.")
        lines.append(f"• {exit_line}")

    # Signal: item presence as texture, not inventory disclosure
    if items:
        i = random.choice(items)
        name = str(i.get("name") if isinstance(i, dict) else i).strip() or "something"
        item_line = {
            "unconscious": f"You glance past {name} without really seeing it.",
            "automatic": f"{name} sits a little too neatly to be accidental.",
            "attentive": f"You notice {name} — not as an object, but as a clue.",
            "insightful": f"{name} feels like a hinge-point. Small. Important. Quiet.",
        }.get(awareness, f"You notice {name}.")
        lines.append(f"• {item_line}")

    # Signal: enemy presence as atmosphere (no stats)
    if enemies:
        e = random.choice(enemies)
        ename = str(e.get("name") if isinstance(e, dict) else e).strip() or "someone"
        enemy_line = {
            "unconscious": f"A prickle in your spine warns you, but your mind stays foggy.",
            "automatic": f"The air tightens. You’re not alone — not really.",
            "attentive": f"You catch a tell: {ename} is here, and it’s watching patterns.",
            "insightful": f"{ename} isn’t just a threat — it’s part of the room’s current story.",
        }.get(awareness, "You sense a presence.")
        lines.append(f"• {enemy_line}")

    # If nothing else, reflect on the description rather than staying empty
    if len(lines) == 1:
        if desc:
            lines.append("• The room doesn’t reveal more — it reveals itself more clearly.")
        else:
            lines.append("• Nothing obvious shifts… but your attention feels cleaner.")

    # Soft guidance, never mechanical
    tail = {
        "unconscious": "You could try again when you feel more here.",
        "automatic": "Stay a moment. Let the room answer without forcing it.",
        "attentive": "If you move, move gently — the room is sensitive.",
        "insightful": "Notice what you’re about to do next. That’s where the signal is.",
    }.get(awareness, "Stay with it a moment.")
    lines.append(f"\n_{tail}_")

    return "\n".join(lines)


class PerceiveCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="perceive")
    async def perceive(self, ctx: commands.Context):
        """
        Skill: Perceive (Perceptual)
        Read-only. No stats. No rolls. No spoilers.
        """
        s = self.bot.storage
        user_id = str(ctx.author.id)

        # Ensure records exist
        self.bot.state.ensure_player_records(user_id)

        char = s.characters.get(user_id, {})
        if not isinstance(char, dict):
            await ctx.send("👁️ You try to perceive… but you feel unplaced. Try `!look` first.")
            return

        room_id = str(char.get("current_room") or "").strip()
        if not room_id:
            await ctx.send("👁️ You can’t find your footing. Try `!look`.")
            return

        room = s.rooms.get(room_id, {})
        if not isinstance(room, dict):
            await ctx.send("👁️ The world blurs. That place doesn’t resolve right now.")
            return

        awareness = _awareness_label(char)
        msg = _format_perceive(room_id, room, awareness)
        await ctx.send(msg)


async def setup(bot):
    await bot.add_cog(PerceiveCog(bot))
