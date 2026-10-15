"""Give items to another present character."""
from discord.ext import commands
from fsbot.item_gifting import give_item, GiftError


class GiftingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="give")
    async def give(self, ctx, *, request: str = ""):
        if " to " not in request.casefold():
            await ctx.send("Usage: !give <item> to <character>")
            return
        split_at = request.casefold().rfind(" to ")
        item_name, target_name = request[:split_at].strip(), request[split_at + 4:].strip()
        storage = self.bot.storage
        giver_id = str(ctx.author.id)
        giver = storage.characters.get(giver_id)
        if not isinstance(giver, dict):
            await ctx.send("Create a character first.")
            return
        candidates = [(uid, ch) for uid, ch in storage.characters.items()
                      if uid != giver_id and isinstance(ch, dict)
                      and ch.get("name", "").casefold() == target_name.casefold()
                      and ch.get("current_room") == giver.get("current_room")]
        if len(candidates) != 1:
            await ctx.send("That character isn't here." if not candidates else "Recipient is ambiguous.")
            return
        recipient_id, recipient = candidates[0]
        try:
            new_giver, new_recipient, name = give_item(giver, recipient, storage.items_db, item_name)
        except (GiftError, ValueError, TypeError) as exc:
            await ctx.send(str(exc))
            return
        storage.characters[giver_id] = new_giver
        storage.characters[recipient_id] = new_recipient
        try:
            storage.save_characters()
        except Exception:
            storage.characters[giver_id] = giver
            storage.characters[recipient_id] = recipient
            await ctx.send("The gift could not be saved.")
            return
        await ctx.send(f"You give **{name}** to **{recipient.get('name', target_name)}**.")
        if name == "Tiny Book" and recipient.get("name", "").casefold() == "the dark rat queen":
            await ctx.send("The tiny volume passes into the Queen's keeping. Its significance is no longer entirely a mystery.")


async def setup(bot):
    await bot.add_cog(GiftingCog(bot))
