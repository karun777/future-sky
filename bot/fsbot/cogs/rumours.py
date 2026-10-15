"""Hear the rumours attached to the current room."""
from discord.ext import commands
from fsbot.rumours import local_rumours


class RumoursCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="rumours")
    async def rumours(self, ctx):
        character = self.bot.storage.characters.get(str(ctx.author.id))
        if not isinstance(character, dict):
            await ctx.send("Create a character first.")
            return
        rumours = local_rumours(character)
        if not rumours:
            await ctx.send("No rumours about you have reached your ears here.")
            return
        lines = [f"Overheard ({r['status']}): {r['claim']}" for r in rumours]
        await ctx.send("\n".join(lines))


async def setup(bot):
    await bot.add_cog(RumoursCog(bot))
