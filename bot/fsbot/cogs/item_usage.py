"""Discord item use command."""
from discord.ext import commands
from fsbot.item_usage import use_item, ItemUseError
from fsbot.intoxication import drink


class ItemUsageCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="use")
    async def use(self, ctx, *, item: str = ""):
        storage = self.bot.storage
        uid = str(ctx.author.id)
        character = storage.characters.get(uid)
        if not isinstance(character, dict):
            await ctx.send("Create a character first.")
            return
        try:
            updated, message, changed = use_item(character, storage.items_db, item)
        except (ItemUseError, ValueError, TypeError) as exc:
            await ctx.send(str(exc))
            return
        if changed and item.strip().casefold() == 'triton lager':
            updated, feeling = drink(updated)
            message = message + ' ' + feeling
        if updated != character:
            storage.characters[uid] = updated
            try:
                storage.save_characters()
            except Exception:
                storage.characters[uid] = character
                await ctx.send("The item use could not be saved.")
                return
        await ctx.send(message)


async def setup(bot):
    await bot.add_cog(ItemUsageCog(bot))
