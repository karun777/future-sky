import discord
from discord.ext import commands
from fsbot.queen_audience import prepare
from fsbot.sequence import result as sequence_result

class QueenAudienceCog(commands.Cog):
    def __init__(self,bot):
        self.bot=bot

    @commands.command(name="queen")
    async def queen(self,ctx,*,action=""):
        sequence_result(ctx, "failed")
        uid=str(ctx.author.id)
        storage=self.bot.storage
        original=storage.characters.get(uid)
        if not isinstance(original,dict):
            await ctx.send("Create a character first.")
            return
        try:
            updated,(title,text)=prepare(original,uid,action)
        except (ValueError,TypeError,KeyError,AttributeError) as exc:
            await ctx.send(str(exc) if isinstance(exc,ValueError) else "Your audience record is unavailable.")
            return
        if updated!=original:
            storage.characters[uid]=updated
            try:
                storage.save_characters()
            except Exception:
                storage.characters[uid]=original
                await ctx.send("The audience could not be remembered. Please try again.")
                return
        await ctx.send(embed=discord.Embed(title=title,description=text,color=discord.Color.dark_teal()),
                       allowed_mentions=discord.AllowedMentions.none())
        sequence_result(ctx, "success" if updated["extra"]["queen_audience_v1"]["stage"] == "received" else "choice")

async def setup(bot):
    await bot.add_cog(QueenAudienceCog(bot))
