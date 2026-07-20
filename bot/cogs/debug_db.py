# cogs/debug_db.py
from discord.ext import commands

class DebugDB(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="db_status", help="Show what DB handle is attached to the bot.")
    @commands.guild_only()
    async def db_status(self, ctx: commands.Context):
        rows = []
        for name in ("db_pool", "pool", "db"):
            obj = getattr(self.bot, name, None)
            if obj is None:
                rows.append(f"{name}: ❌")
            else:
                rows.append(f"{name}: ✅ {type(obj).__name__} ({obj.__class__.__module__})")
        await ctx.reply(" | ".join(rows) or "No DB attributes found.")

async def setup(bot: commands.Bot):
    await bot.add_cog(DebugDB(bot))
