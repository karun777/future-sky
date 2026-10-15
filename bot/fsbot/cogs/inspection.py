"""Discord item inspection cards."""
import discord
from discord.ext import commands
from fsbot.item_inspection import inspect_item


class InspectionCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="inspect")
    async def inspect(self, ctx, *, item: str = ""):
        storage = self.bot.storage
        character = storage.characters.get(str(ctx.author.id))
        if not isinstance(character, dict):
            await ctx.send("Create a character first.")
            return
        room = storage.rooms.get(character.get("current_room"), {})
        try:
            item_id, definition, attributes, unlocked = inspect_item(
                item, character, room, storage.items_db)
        except (ValueError, TypeError) as exc:
            await ctx.send(str(exc))
            return
        embed = discord.Embed(
            title=definition.get("name", item_id),
            description=definition.get("description") or "You examine the object, but learn little.",
            color=discord.Color.dark_teal())
        embed.add_field(name="Type", value=str(definition.get("type", "unknown")).title())
        embed.add_field(name="Rarity", value=str(definition.get("rarity", "unknown")).title())
        if attributes:
            embed.add_field(name="Known attributes",
                            value="\n".join(f"**{k.replace('_', ' ').title()}:** {v}" for k, v in attributes.items()),
                            inline=False)
        else:
            embed.add_field(name="Known attributes", value="None discovered yet.", inline=False)
        uses = definition.get("uses", [])
        if isinstance(uses, list) and uses:
            public_uses = [u.get("label", "") for u in uses
                           if isinstance(u, dict) and (not u.get("discovery") or u["discovery"] in unlocked)]
            if public_uses:
                embed.add_field(name="Known uses", value=", ".join(public_uses), inline=False)
        image = definition.get("image")
        if isinstance(image, str) and image.startswith("https://"):
            embed.set_image(url=image)
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(InspectionCog(bot))
