"""Talk your way past the Neptune Lounge bouncer."""
from discord.ext import commands
from fsbot.bouncer import BouncerError, resolve_bouncer


class BouncerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="bouncer")
    async def bouncer(self, ctx, *, choice: str = ""):
        storage = self.bot.storage
        uid = str(ctx.author.id)
        character = storage.characters.get(uid)
        if not isinstance(character, dict):
            await ctx.send("Create a character first.")
            return
        try:
            updated, message = resolve_bouncer(character, choice)
        except BouncerError as exc:
            await ctx.send(str(exc))
            return
        storage.characters[uid] = updated
        try:
            storage.save_characters()
        except Exception:
            storage.characters[uid] = character
            await ctx.send("The conversation could not be saved.")
            return
        await ctx.send(message)


async def setup(bot):
    await bot.add_cog(BouncerCog(bot))
