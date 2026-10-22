"""Discord presenter for the non-combat messenger."""
import discord
from discord.ext import commands
from fsbot.rat_messenger import prepare
from fsbot.terrace_delivery import APPROACH

class RatMessengerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def present(self, ctx, action=""):
        storage = self.bot.storage
        uid = str(ctx.author.id)
        original = storage.characters.get(uid)
        if not isinstance(original, dict):
            await ctx.send("Create a character first.")
            return
        try:
            updated, (title, text, hint) = prepare(original, action)
        except (ValueError, TypeError, KeyError, AttributeError) as exc:
            await ctx.send(str(exc) if isinstance(exc, ValueError) else "Your messenger record is unavailable.")
            return
        if updated != original:
            storage.characters[uid] = updated
            try:
                storage.save_characters()
            except Exception:
                storage.characters[uid] = original
                await ctx.send("The message could not be remembered. Please try again.")
                return
        embed = discord.Embed(title=title, description=text, color=discord.Color.dark_teal())
        embed.add_field(name="Your attention", value=hint, inline=False)
        await ctx.send(embed=embed, allowed_mentions=discord.AllowedMentions.none())

    async def inspect_target(self, ctx, query):
        if " ".join(query.casefold().split()).strip(".!?") not in {"rat", "messenger", "messenger rat"}:
            return False
        ch = self.bot.storage.characters.get(str(ctx.author.id))
        if not isinstance(ch, dict) or ch.get("current_room") != APPROACH:
            return False
        await self.present(ctx, "inspect")
        return True

    @commands.command(name="rat")
    async def rat(self, ctx, *, action=""):
        await self.present(ctx, action)

async def setup(bot):
    await bot.add_cog(RatMessengerCog(bot))
