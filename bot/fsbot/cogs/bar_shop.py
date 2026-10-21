"""Neptune Lounge bartender commands."""
from discord.ext import commands
from fsbot.bar_shop import BarError, bar_menu, buy_from_bar
from fsbot.performance_tab import claim_tab

class BarShopCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="bar")
    async def bar(self, ctx):
        storage = self.bot.storage
        character = storage.characters.get(str(ctx.author.id))
        if not isinstance(character, dict):
            await ctx.send("Create a character first.")
            return
        try:
            message = bar_menu(character, storage.items_db)
            character, revelation = claim_tab(storage, str(ctx.author.id))
            message = bar_menu(character, storage.items_db)
            if revelation:
                message = revelation + "\n\n" + message
        except (BarError, ValueError) as exc:
            message = str(exc)
        await ctx.send(message)

    @commands.command(name="buy")
    async def buy(self, ctx, *, item: str = ""):
        storage = self.bot.storage
        uid = str(ctx.author.id)
        character = storage.characters.get(uid)
        if not isinstance(character, dict):
            await ctx.send("Create a character first.")
            return
        try:
            updated, message = buy_from_bar(character, storage.items_db, item)
        except (BarError, TypeError, ValueError) as exc:
            await ctx.send(str(exc))
            return
        storage.characters[uid] = updated
        try:
            storage.save_characters()
        except Exception:
            storage.characters[uid] = character
            await ctx.send("The purchase could not be saved. No credits were charged.")
            return
        await ctx.send(message)

async def setup(bot):
    await bot.add_cog(BarShopCog(bot))
