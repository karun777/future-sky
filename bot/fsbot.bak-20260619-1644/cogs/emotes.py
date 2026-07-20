from __future__ import annotations

from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple

from discord.ext import commands

from fsbot.cogs.router import ensure_player_run_channel


# --- Emote text (Future Sky slant, MajorMUD spirit) ---
EMOTES = {
    "smile": [
        "You smile like you’ve seen this room before — and decided to come back anyway.",
        "A small smile slips through. The dome hum answers, almost imperceptibly.",
        "You smile. Somewhere, a cleaner drone pauses as if it felt it."
    ],
    "grin": [
        "You grin — a little too wide — like you’re in on a loop no one else remembers.",
        "A grin flashes across your face, sharp as neon on wet pavement.",
        "You grin at the Lounge. The Lounge does not grin back. It simply *continues*."
    ],
    "dance": [
        "You dance in the neon spill, boots tapping out a rhythm the city half-remembers.",
        "You dance like the gravity here is negotiable.",
        "You dance. The chips smell briefly becomes the beat."
    ],
    "nod": [
        "You nod once — a quiet agreement with whatever thread is holding reality together.",
        "You nod, as if receiving instructions from a future version of yourself.",
        "You nod to the room. The room nods back, in its own way."
    ],
    "shrug": [
        "You shrug. The universe shrugs with you. Nothing admits it.",
        "You shrug off the weirdness. It clings anyway, politely.",
        "You shrug — a small rebellion against prophecy."
    ],
    "wave": [
        "You wave like you’re signalling across timelines.",
        "You wave to no one in particular. Someone, somewhere, answers.",
        "You wave. A smuggler mistakes it for a code and looks away quickly."
    ],
    "bow": [
        "You bow, old-world etiquette in a city built from future salvage.",
        "You bow to the dome and the storm beyond it.",
        "You bow. The Lounge accepts it as payment in manners."
    ],
    "laugh": [
        "You laugh — and for a moment the loop loosens its grip.",
        "A laugh bursts out of you, bright enough to cut the hum.",
        "You laugh quietly. The sound returns to you half a second late."
    ],
    "stare": [
        "You stare, steady and present, as if daring reality to blink first.",
        "You stare into the dome’s reflection until you almost see another you staring back.",
        "You stare. A small flicker in the air suggests you hit something real."
    ],
    "hum": [
        "You hum along with the Lounge’s low-frequency throb.",
        "You hum a tune you don’t remember learning. The Cube might.",
        "You hum. The sound seems to travel further than it should."
    ],
    "toast": [
        "You raise an imaginary glass to continuity. It doesn’t spill. Good sign.",
        "You toast the storm outside. Neptune does not acknowledge you. Yet.",
        "You toast. The Lounge smells briefly like celebration and ozone."
    ],
}


class EmotesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def _record_last_action(self, user_id: str, action: str, payload: Optional[Dict[str, Any]] = None) -> None:
        """Tiny hook for thread nodes later."""
        try:
            s = self.bot.storage
            self.bot.state.ensure_player_records(user_id)
            c = s.characters[user_id]
            c["last_action"] = {
                "type": "emote",
                "action": action,
                "payload": payload or {},
                "ts": datetime.utcnow().isoformat(timespec="seconds") + "Z",
            }
            s.save_characters()
        except Exception:
            pass

    def _find_other_players_in_same_room(self, user_id: str) -> List[Tuple[str, Dict[str, Any]]]:
        """
        Returns list of (other_user_id, other_character_dict) who are in the same room.
        Minimal + reliable: scan storage.characters and compare resolved rooms.
        """
        s = self.bot.storage
        self.bot.state.ensure_player_records(user_id)

        my_room = self.bot.state.resolve_room_for_user(user_id)
        others: List[Tuple[str, Dict[str, Any]]] = []

        for uid, ch in s.characters.items():
            if uid == user_id:
                continue
            try:
                # skip cube players: they shouldn't receive room broadcasts
                if ch.get("in_cube"):
                    continue
                their_room = self.bot.state.resolve_room_for_user(uid)
                if their_room == my_room:
                    others.append((uid, ch))
            except Exception:
                continue

        return others

    async def _broadcast_to_room(self, ctx: commands.Context, user_id: str, action_word: str) -> None:
        """
        Broadcast a simple third-person message to other players in the same room,
        delivered to *their* run channels.
        """
        s = self.bot.storage
        self.bot.state.ensure_player_records(user_id)
        me = s.characters[user_id]
        name = me.get("name", ctx.author.display_name)

        others = self._find_other_players_in_same_room(user_id)
        if not others:
            return

        # Simple, readable, MajorMUD-esque
        msg = f"✨ **{name}** {action_word}."

        # Deliver to each other player's run channel
        for ouid, och in others:
            try:
                other_name = och.get("name", "Wanderer")
                ch = await ensure_player_run_channel(self.bot, ctx, ouid, other_name)
                if ch:
                    await ch.send(msg)
            except Exception:
                pass

    async def _do_emote(self, ctx: commands.Context, emote_key: str, action_word: str) -> None:
        user_id = str(ctx.author.id)
        self._record_last_action(user_id, emote_key)

        # Self-facing flavour
        lines = EMOTES.get(emote_key, [])
        if lines:
            idx = (int(ctx.author.id) + datetime.utcnow().minute) % len(lines)
            msg_self = lines[idx]
        else:
            msg_self = f"You {action_word}."

        await ctx.send(f"✨ {msg_self}")

        # Room broadcast (others only)
        await self._broadcast_to_room(ctx, user_id, action_word)

    @commands.command()
    async def emote(self, ctx: commands.Context, *, text: str):
        """Freeform emote. v0: shows to self + broadcasts simple third-person to room."""
        user_id = str(ctx.author.id)
        cleaned = " ".join(text.strip().split())
        if not cleaned:
            await ctx.send("Usage: `!emote <action>`")
            return

        self._record_last_action(user_id, "emote", {"text": cleaned})

        # Self
        await ctx.send(f"✨ You {cleaned}.")

        # Others see: "**Name** <text>."
        # Ensure punctuation
        action = cleaned
        if not action.endswith((".", "!", "?")):
            action += "."
        # strip trailing period for our formatter (it adds one)
        action_word = action[:-1] if action.endswith(".") else action

        await self._broadcast_to_room(ctx, user_id, action_word)

    # --- Presets (MajorMUD style) ---
    @commands.command()
    async def smile(self, ctx: commands.Context):
        await self._do_emote(ctx, "smile", "smiles")

    @commands.command()
    async def grin(self, ctx: commands.Context):
        await self._do_emote(ctx, "grin", "grins")

    @commands.command()
    async def dance(self, ctx: commands.Context):
        await self._do_emote(ctx, "dance", "dances")

    @commands.command()
    async def nod(self, ctx: commands.Context):
        await self._do_emote(ctx, "nod", "nods")

    @commands.command()
    async def shrug(self, ctx: commands.Context):
        await self._do_emote(ctx, "shrug", "shrugs")

    @commands.command()
    async def wave(self, ctx: commands.Context):
        await self._do_emote(ctx, "wave", "waves")

    @commands.command()
    async def bow(self, ctx: commands.Context):
        await self._do_emote(ctx, "bow", "bows")

    @commands.command()
    async def laugh(self, ctx: commands.Context):
        await self._do_emote(ctx, "laugh", "laughs")

    @commands.command()
    async def stare(self, ctx: commands.Context):
        await self._do_emote(ctx, "stare", "stares")

    @commands.command()
    async def hum(self, ctx: commands.Context):
        await self._do_emote(ctx, "hum", "hums")

    @commands.command()
    async def toast(self, ctx: commands.Context):
        await self._do_emote(ctx, "toast", "toasts")


async def setup(bot):
    await bot.add_cog(EmotesCog(bot))
