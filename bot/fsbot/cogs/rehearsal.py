"""Rehearsal presenter; no autonomous scheduling is enabled."""
import discord
from discord.ext import commands
from fsbot.rehearsal import prepare, register_room

class RehearsalCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        register_room(self.bot.storage.rooms)

    @commands.command(name="rehearsal")
    async def rehearsal(self, ctx, *, action=""):
        uid = str(ctx.author.id)
        storage = self.bot.storage
        original = storage.characters.get(uid)
        if not isinstance(original, dict):
            await ctx.send("Create a character first.")
            return
        try:
            updated, (title,text) = prepare(original, action, storage.rooms)
        except (ValueError, TypeError, KeyError, AttributeError) as exc:
            await ctx.send(str(exc) if isinstance(exc,ValueError) else "Your rehearsal record is unavailable.")
            return
        if updated != original:
            storage.characters[uid] = updated
            try:
                storage.save_characters()
            except Exception:
                storage.characters[uid] = original
                await ctx.send("The rehearsal could not be remembered. Please try again.")
                return
        if updated.get("current_room") != original.get("current_room"):
            from fsbot.cogs.navigation import _publish_character_entered_room
            await _publish_character_entered_room(self.bot, user_id=uid,
                from_room_id=original["current_room"], to_room_id=updated["current_room"],
                movement_type="walk", direction=None)
        embed = discord.Embed(title=title, description=text, color=discord.Color.dark_teal())
        await ctx.send(embed=embed, allowed_mentions=discord.AllowedMentions.none())

async def setup(bot):
    await bot.add_cog(RehearsalCog(bot))
