"""Character HUD preferences and one presentation path for commands/navigation."""
from copy import deepcopy
import discord
from discord.ext import commands

DEFAULT_HUD = {"enabled": True, "state": "normal"}
STATES = {"normal", "signal_degraded", "dark_mode"}


def hud_preferences(character):
    value = (character.get("extra") or {}).get("hud")
    return value if isinstance(value, dict) else DEFAULT_HUD


def render_panel(character, *, explicit=False):
    hud = hud_preferences(character)
    if not hud.get("enabled", True):
        return discord.Embed(title="◉ DISPLAY OFFLINE", description="No active telemetry.", color=0x555555) if explicit else None
    state = hud.get("state", "normal")
    if state == "dark_mode":
        return discord.Embed(title="◉ DISPLAY DIMMED", description="Telemetry is concealed.", color=0x555555)
    if state == "signal_degraded":
        return discord.Embed(title="◉ SIGNAL DEGRADED", description="Readings unavailable.", color=0x555555)
    embed = discord.Embed(title="◉ TELEMETRY", description="Calibration incomplete. No current assessment is available.", color=0x555555)
    # Legacy 97/78/LOW fields are authored defaults, not measured assessments.
    # Preserve them in storage, but do not display them as current truth.
    for label in ("♆ COHERENCE", "♄ PARALLELISM", "✦ COMMOTION"):
        embed.add_field(name=label, value="UNCALIBRATED", inline=True)
    return embed


class HudCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def _get_hud(self, user_id):
        character = self.bot.presence.get_character(str(user_id))
        return deepcopy(hud_preferences(character)) if isinstance(character, dict) else None

    def panel(self, user_id, *, explicit=False):
        character = self.bot.presence.get_character(str(user_id))
        return render_panel(character, explicit=explicit) if isinstance(character, dict) else None

    async def _update(self, ctx, **values):
        uid = str(ctx.author.id)
        original = self.bot.storage.characters.get(uid)
        if not isinstance(original, dict):
            await ctx.send("Create a character first.")
            return
        updated = deepcopy(original)
        hud = updated.setdefault("extra", {}).setdefault("hud", deepcopy(DEFAULT_HUD))
        hud.update(values)
        if updated != original:
            self.bot.storage.characters[uid] = updated
            try:
                self.bot.storage.save_characters()
            except Exception:
                self.bot.storage.characters[uid] = original
                await ctx.send("The display could not save that setting. Please try again.")
                return
        await ctx.send(embed=render_panel(updated, explicit=True))

    @commands.command(name="hud")
    async def hud(self, ctx):
        panel = self.panel(str(ctx.author.id), explicit=True)
        if panel is None:
            await ctx.send("Create a character first.")
        else:
            await ctx.send(embed=panel)

    @commands.command(name="hud_on")
    async def hud_on(self, ctx):
        await self._update(ctx, enabled=True)

    @commands.command(name="hud_off")
    async def hud_off(self, ctx):
        await self._update(ctx, enabled=False)

    @commands.command(name="hud_state")
    async def hud_state(self, ctx, state: str):
        if state not in STATES:
            await ctx.send("Valid display states: normal, signal_degraded, dark_mode.")
            return
        await self._update(ctx, state=state)


async def setup(bot):
    await bot.add_cog(HudCog(bot))
