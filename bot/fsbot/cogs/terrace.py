"""Discord bridge for the private terrace-delivery passage."""
import discord
from discord.ext import commands
from fsbot.terrace_delivery import (
    TerraceError, prepare, register_room, state_of, ROOM, TARGETS,
)


class TerraceCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        register_room(self.bot.storage.rooms)

    async def present(self, ctx, request=""):
        storage = self.bot.storage
        uid = str(ctx.author.id)
        original = storage.characters.get(uid)
        if not isinstance(original, dict):
            await ctx.send("Create a character first.")
            return
        try:
            updated, (title, text, hint) = prepare(original, uid, request)
        except (TerraceError, TypeError, KeyError, AttributeError) as exc:
            message = str(exc) if isinstance(exc, TerraceError) else "Your delivery record is unavailable."
            await ctx.send(message)
            return
        if updated != original:
            storage.characters[uid] = updated
            try:
                storage.save_characters()
            except Exception:
                storage.characters[uid] = original
                await ctx.send("The delivery could not remember that action. Please try again.")
                return
        embed = discord.Embed(title=title, description=text, color=discord.Color.dark_teal())
        embed.add_field(name="Your attention", value=hint, inline=False)
        await ctx.send(embed=embed, allowed_mentions=discord.AllowedMentions.none())

    async def inspect_target(self, ctx, query):
        action = TARGETS.get(" ".join(query.casefold().split()).strip(".!?"))
        if not action:
            return False
        character = self.bot.storage.characters.get(str(ctx.author.id))
        if not isinstance(character, dict):
            return False
        try:
            state = state_of(character)
        except TerraceError:
            state = True  # route to the guarded presenter
        if character.get("current_room") != ROOM and not state:
            return False
        await self.present(ctx, action)
        return True

    @commands.command(name="terrace")
    async def terrace(self, ctx, *, action=""):
        await self.present(ctx, action)


async def setup(bot):
    await bot.add_cog(TerraceCog(bot))
