"""Optional loopback-only portal. Disabled unless explicitly configured."""
import logging
import os
from aiohttp import web
from discord.ext import commands

class WebPortalCog(commands.Cog):
    def __init__(self, bot, app):
        self.bot = bot
        self.runner = web.AppRunner(app, access_log=None)

    async def cog_load(self):
        try:
            await self.runner.setup()
            await web.TCPSite(self.runner, "127.0.0.1", 8787).start()
        except Exception:
            await self.runner.cleanup()
            raise
        logging.getLogger("futuresky").info(
            "Read-only game portal listening on loopback port 8787")

    async def cog_unload(self):
        await self.runner.cleanup()

async def setup(bot):
    if os.environ.get("FS_WEB_ENABLED") != "1":
        return
    from fsbot.web_portal import WebConfig, create_app
    config = WebConfig(
        client_id=os.environ.get("FS_WEB_DISCORD_CLIENT_ID", ""),
        client_secret=os.environ.get("FS_WEB_DISCORD_CLIENT_SECRET", ""),
        allowed_ids=frozenset(x.strip() for x in
            os.environ.get("FS_WEB_ALLOWED_DISCORD_IDS", "").split(",") if x.strip()))
    await bot.add_cog(WebPortalCog(bot, create_app(bot, config)))
