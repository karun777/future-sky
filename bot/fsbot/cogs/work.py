"""Neptune Lounge paid work."""
from discord.ext import commands
from fsbot.bar_work import WorkError, work_bar


class WorkCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="work")
    async def work(self, ctx, *, job: str = ""):
        if job.strip().casefold() != "bar":
            await ctx.send("Try !work bar.")
            return
        storage = self.bot.storage
        uid = str(ctx.author.id)
        character = storage.characters.get(uid)
        if not isinstance(character, dict):
            await ctx.send("Create a character first.")
            return
        try:
            updated, message = work_bar(character)
        except (WorkError, ValueError, TypeError) as exc:
            await ctx.send(str(exc))
            return
        storage.characters[uid] = updated
        try:
            storage.save_characters()
        except Exception:
            storage.characters[uid] = character
            await ctx.send("Your shift could not be saved. No credits were paid.")
            return
        await ctx.send(message)


async def setup(bot):
    await bot.add_cog(WorkCog(bot))
