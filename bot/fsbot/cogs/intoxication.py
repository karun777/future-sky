"""Check your character's current intoxication."""
from discord.ext import commands
from fsbot.intoxication import status


class IntoxicationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="sober")
    async def sober(self, ctx):
        character = self.bot.storage.characters.get(str(ctx.author.id))
        if not isinstance(character, dict):
            await ctx.send("Create a character first.")
            return
        level, feeling = status(character)
        await ctx.send(f"Microvita intensity: {level}/6. {feeling}")


async def setup(bot):
    await bot.add_cog(IntoxicationCog(bot))
