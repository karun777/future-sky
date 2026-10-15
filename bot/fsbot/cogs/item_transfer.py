"""Room item take/drop commands."""
from discord.ext import commands
from fsbot.item_transfer import transfer, TransferError


class ItemTransferCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def _move(self, ctx, item, direction):
        storage = self.bot.storage
        uid = str(ctx.author.id)
        character = storage.characters.get(uid)
        if not isinstance(character, dict):
            await ctx.send("Create a character first.")
            return
        room_id = character.get("current_room")
        room = storage.rooms.get(room_id)
        if not isinstance(room, dict):
            await ctx.send("You are not in a valid room.")
            return
        try:
            updated_character, updated_room, name = transfer(
                character, room, storage.items_db, item, direction)
        except (TransferError, ValueError, TypeError) as exc:
            await ctx.send(str(exc))
            return
        # Save both sides, restoring in-memory state if either write fails.
        storage.characters[uid] = updated_character
        storage.rooms[room_id] = updated_room
        try:
            storage.save_characters()
            storage.save_rooms()
        except Exception:
            storage.characters[uid] = character
            storage.rooms[room_id] = room
            # Restore the first file if the second save failed.
            try:
                storage.save_characters()
                storage.save_rooms()
            except Exception:
                pass
            await ctx.send("The transfer could not be saved.")
            return
        verb = "take" if direction == "take" else "drop"
        await ctx.send("You " + verb + " **" + name + "**.")

    @commands.command(name="take")
    async def take(self, ctx, *, item: str = ""):
        await self._move(ctx, item, "take")

    @commands.command(name="drop")
    async def drop(self, ctx, *, item: str = ""):
        await self._move(ctx, item, "drop")


async def setup(bot):
    await bot.add_cog(ItemTransferCog(bot))
