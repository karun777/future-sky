from __future__ import annotations

from discord.ext import commands

from fsbot.cogs.router import ensure_player_run_channel


class SpeechCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def _room_members(self, user_id: str):
        """Return list of (uid, character) for players in same room (excluding cube)."""
        s = self.bot.storage
        self.bot.state.ensure_player_records(user_id)

        my_room = self.bot.state.resolve_room_for_user(user_id)
        out = []
        for uid, ch in s.characters.items():
            if ch.get("in_cube"):
                continue
            try:
                if self.bot.state.resolve_room_for_user(uid) == my_room:
                    out.append((uid, ch))
            except Exception:
                continue
        return out, my_room

    def _find_user_id_by_character_name(self, name: str):
        """Find a user's id by exact character name (case-insensitive)."""
        s = self.bot.storage
        lookup = name.strip().lower().lstrip("@")
        for uid, ch in s.characters.items():
            cname = str(ch.get("name", "")).strip().lower()
            if cname and cname == lookup:
                return uid
        return None

    async def _send_to_player_run(self, ctx: commands.Context, uid: str, ch: dict, msg: str):
        """Send a message to a specific player's run channel."""
        try:
            other_name = ch.get("name", "Wanderer")
            run_ch = await ensure_player_run_channel(self.bot, ctx, uid, other_name)
            if run_ch:
                await run_ch.send(msg)
        except Exception:
            pass

    @commands.command()
    async def say(self, ctx: commands.Context, *, message: str):
        """Speak to the room."""
        user_id = str(ctx.author.id)
        s = self.bot.storage
        self.bot.state.ensure_player_records(user_id)
        me = s.characters[user_id]
        name = me.get("name", ctx.author.display_name)

        msg = " ".join(message.strip().split())
        if not msg:
            await ctx.send("Usage: `!say <message>`")
            return

        out = f"💬 **{name}** says: {msg}"

        members, _room = self._room_members(user_id)
        for uid, ch in members:
            await self._send_to_player_run(ctx, uid, ch, out)

    @commands.command()
    async def think(self, ctx: commands.Context, *, message: str):
        """Telepath / speak to the room in mind-voice."""
        user_id = str(ctx.author.id)
        s = self.bot.storage
        self.bot.state.ensure_player_records(user_id)
        me = s.characters[user_id]
        name = me.get("name", ctx.author.display_name)

        msg = " ".join(message.strip().split())
        if not msg:
            await ctx.send("Usage: `!think <message>`")
            return

        out = f"🧠 **{name}** projects: _{msg}_"

        members, _room = self._room_members(user_id)
        for uid, ch in members:
            await self._send_to_player_run(ctx, uid, ch, out)

    @commands.command()
    async def pose(self, ctx: commands.Context, *, action: str):
        """Roleplay action to the room (Name <action>)."""
        user_id = str(ctx.author.id)
        s = self.bot.storage
        self.bot.state.ensure_player_records(user_id)
        me = s.characters[user_id]
        name = me.get("name", ctx.author.display_name)

        act = " ".join(action.strip().split())
        if not act:
            await ctx.send("Usage: `!pose <action>`")
            return

        if not act.endswith((".", "!", "?")):
            act += "."

        out = f"🎭 **{name}** {act}"

        members, _room = self._room_members(user_id)
        for uid, ch in members:
            await self._send_to_player_run(ctx, uid, ch, out)

    @commands.command()
    async def tell(self, ctx: commands.Context, member, *, message: str):
        """Direct message another player (to their run channel). Usage: !tell @user <msg>"""
        if not getattr(ctx.message, "mentions", None):
            await ctx.send("Usage: `!tell @user <message>`")
            return

        if not ctx.message.mentions:
            await ctx.send("Usage: `!tell @user <message>` (select the user so it becomes a real mention)")
            return

        target = ctx.message.mentions[0]
        if getattr(target, "bot", False):
            await ctx.send("You can’t `!tell` a bot.")
            return

        user_id = str(ctx.author.id)
        target_id = str(target.id)

        s = self.bot.storage
        self.bot.state.ensure_player_records(user_id)
        self.bot.state.ensure_player_records(target_id)

        me = s.characters[user_id]
        name = me.get("name", ctx.author.display_name)

        msg = " ".join(message.strip().split())
        if not msg:
            await ctx.send("Usage: `!tell @user <message>`")
            return

        await ctx.send(f"📨 You tell **{target.display_name}**: {msg}")

        out = f"📨 **{name}** tells you: {msg}"
        await self._send_to_player_run(ctx, target_id, s.characters[target_id], out)

    @commands.command()
    async def whisper(self, ctx: commands.Context, target: str, *, message: str):
        """
        Private message to a player in the SAME room only.
        Usage:
        - !whisper Kruza <msg>
        - !whisper @user <msg>  (real mention)
        """
        user_id = str(ctx.author.id)
        s = self.bot.storage
        self.bot.state.ensure_player_records(user_id)

        msg = " ".join(message.strip().split())
        if not msg:
            await ctx.send("Usage: `!whisper <Name|@mention> <message>`")
            return

        target_id = None

        if getattr(ctx.message, "mentions", None) and ctx.message.mentions:
            m = ctx.message.mentions[0]
            if getattr(m, "bot", False):
                await ctx.send("You can’t whisper to a bot.")
                return
            target_id = str(m.id)
        else:
            target_id = self._find_user_id_by_character_name(target)

        if not target_id or target_id not in s.characters:
            await ctx.send("I couldn’t find that character. (Try exact character name, or a real mention.)")
            return

        if target_id == user_id:
            await ctx.send("You whisper to yourself. It’s… not helpful, but it counts.")
            return

        my_room = self.bot.state.resolve_room_for_user(user_id)
        their_room = self.bot.state.resolve_room_for_user(target_id)
        if my_room != their_room:
            await ctx.send("You can only whisper to someone who is **here** with you.")
            return

        me = s.characters[user_id]
        them = s.characters[target_id]
        my_name = me.get("name", ctx.author.display_name)
        their_name = them.get("name", "Wanderer")

        await ctx.send(f"🤫 You whisper to **{their_name}**: {msg}")

        out = f"🤫 **{my_name}** whispers: {msg}"
        await self._send_to_player_run(ctx, target_id, them, out)


async def setup(bot):
    await bot.add_cog(SpeechCog(bot))
