#python
# ============================================================
# FILE META — fsbot/cogs/hud.py
#
# HUD v0.1
# Future Sky telemetry layer
#
# Commands:
#   !hud
#   !hud_on
#   !hud_off
#   !hud_state <state>
#
# States:
#   normal
#   signal_degraded
#   dark_mode
# ============================================================

from __future__ import annotations

import discord
from discord.ext import commands


DEFAULT_HUD = {
    "enabled": True,
    "state": "normal",
    "coherence": 97,
    "parallelism": 78,
    "commotion": "LOW",
}


class HudCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --------------------------------------------------------
    # Helpers
    # --------------------------------------------------------

    def _get_hud(self, user_id: str):
        char = self.bot.presence.get_character(user_id)
        if not isinstance(char, dict):
            return None

        extra = char.setdefault("extra", {})
        hud = extra.setdefault("hud", dict(DEFAULT_HUD))

        return hud

    def _save(self):
        try:
            self.bot.storage.save_characters()
        except Exception:
            pass

    def _render_hud(self, hud: dict) -> str:

        if not hud.get("enabled", True):
            return (
                "```"
                "\nNO ACTIVE TELEMETRY"
                "\n```"
            )

        state = hud.get("state", "normal")

        if state == "dark_mode":
            return (
                "```"
                "\n..."
                "\n```"
            )

        coherence = hud.get("coherence", 97)
        parallelism = hud.get("parallelism", 78)
        commotion = hud.get("commotion", "LOW")

        if state == "signal_degraded":
            coherence = "???"
            parallelism = "???"

        return (
            "```"
            "\n╔════════════════════╗"
            f"\n║ COHERENCE      {str(coherence).rjust(3)} ║"
            f"\n║ PARALLELISM    {str(parallelism).rjust(3)} ║"
            f"\n║ COMMOTION   {str(commotion).ljust(6)} ║"
            "\n╚════════════════════╝"
            "\n```"
        )

    # --------------------------------------------------------
    # Commands
    # --------------------------------------------------------

    @commands.command(name="hud")
    async def hud(self, ctx):

        user_id = str(ctx.author.id)

        hud = self._get_hud(user_id)

        if not hud:
            await ctx.send("No character found.")
            return

        await ctx.send(self._render_hud(hud))

    @commands.command(name="hud_on")
    async def hud_on(self, ctx):

        user_id = str(ctx.author.id)
        hud = self._get_hud(user_id)

        if not hud:
            return

        hud["enabled"] = True

        self._save()

        await ctx.send("📡 HUD ONLINE")

    @commands.command(name="hud_off")
    async def hud_off(self, ctx):

        user_id = str(ctx.author.id)
        hud = self._get_hud(user_id)

        if not hud:
            return

        hud["enabled"] = False

        self._save()

        await ctx.send("📴 HUD OFFLINE")

    @commands.command(name="hud_state")
    async def hud_state(self, ctx, state: str):

        allowed = {
            "normal",
            "signal_degraded",
            "dark_mode",
        }

        if state not in allowed:
            await ctx.send(
                "Valid states: normal, signal_degraded, dark_mode"
            )
            return

        user_id = str(ctx.author.id)

        hud = self._get_hud(user_id)

        if not hud:
            return

        hud["state"] = state

        self._save()

        await ctx.send(f"HUD STATE → {state}")


async def setup(bot):
    await bot.add_cog(HudCog(bot))