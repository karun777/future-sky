# fsbot/cogs/astro_cog.py
# Future Sky — Astrology Cog (v0)
#
# Exposes:
# - !astro [YYYY-MM-DD]
#
# Uses:
# - fsbot.astrology.compute_planet_signs (pure calc, no houses/aspects)
#
# Persists:
# - characters[user_id]["extra"]["astrology"] = result
#
# Notes:
# - If no arg provided, uses character.birthdate
# - If character missing, prompts to create

from __future__ import annotations

import discord
from discord.ext import commands
from datetime import datetime

from fsbot.astrology import compute_planet_signs


def _format_astro(result: dict) -> str:
    placements = result.get("placements", {}) if isinstance(result, dict) else {}
    if not placements:
        return "⚠️ No placements computed."

    order = ["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto"]

    lines = []
    for k in order:
        p = placements.get(k)
        if not isinstance(p, dict):
            continue
        sign = p.get("sign", "?")
        lines.append(f"**{k.title():<8}** {sign}")

    return "\n".join(lines) if lines else "⚠️ No placements computed."



class AstroCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="astro")
    async def astro_cmd(self, ctx: commands.Context, birthdate: str | None = None):
        """
        Compute planetary sign placements.

        Usage:
          !astro                -> uses your saved birthdate
          !astro YYYY-MM-DD     -> uses provided date (does NOT overwrite saved birthdate)
        """
        s = self.bot.storage
        user_id = str(ctx.author.id)

        # Ensure character exists
        if user_id not in s.characters:
            await ctx.send("🧬 You don’t have a character yet. Use `!create_character <name> <YYYY-MM-DD> <class_id>`.")
            return

        c = s.characters[user_id]
        saved_birthdate = c.get("birthdate")

        # Determine birthdate to compute
        if birthdate is None:
            birthdate = saved_birthdate

        # Validate birthdate
        try:
            _ = datetime.strptime(birthdate, "%Y-%m-%d").date()
        except Exception:
            await ctx.send("⚠️ Invalid date. Use `YYYY-MM-DD`.")
            return

        # Compute
        try:
            result = compute_planet_signs(birthdate)
        except Exception as e:
            await ctx.send(f"⚠️ Astrology compute failed: `{type(e).__name__}`")
            return

        # Persist into extra.astrology
        extra = c.get("extra")
        if not isinstance(extra, dict):
            extra = {}
            c["extra"] = extra

        extra["astrology"] = result
        s.save_characters()

        # Display nicely
        embed = discord.Embed(
            title="🪐 Astrology — Planetary Signs (v0)",
            description=f"Birthdate used: `{birthdate}`",
        )
        embed.add_field(name="Placements", value=_format_astro(result), inline=False)

        assumptions = result.get("assumptions", {})
        if isinstance(assumptions, dict):
            ephem = assumptions.get("ephemeris_mode", "unknown")
            time_assumed = assumptions.get("time_assumed", False)
            tz_assumed = assumptions.get("tz_assumed", False)
            embed.set_footer(text=f"ephem={ephem} | time_assumed={time_assumed} | tz_assumed={tz_assumed}")

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(AstroCog(bot))
