"""Discoverable HUD capabilities; navigation stays quiet unless explicitly requested."""
from copy import deepcopy
import discord
from discord.ext import commands
from fsbot.pod_opening import opening_state

DEFAULT_HUD = {"enabled": True, "state": "normal"}
STATES = {"normal", "signal_degraded", "dark_mode"}
USAGE = "Use `!hud`, `!hud on`, `!hud off`, or `!hud state normal|signal degraded|dark mode`."


def hud_preferences(character):
    extra = character.get("extra")
    value = extra.get("hud") if isinstance(extra, dict) else None
    return value if isinstance(value, dict) else DEFAULT_HUD


def display_state(value):
    words = " ".join(str(value).casefold().replace("_", " ").split())
    return {"normal": "normal", "signal degraded": "signal_degraded", "dark mode": "dark_mode"}.get(words)


def render_panel(character, *, explicit=False):
    # No speculative meters or repeated automatic panel after room descriptions.
    if not explicit:
        return None
    hud = hud_preferences(character)
    if not hud.get("enabled", True):
        return discord.Embed(title="◉ DISPLAY OFFLINE", description="Use `!hud on` to restore the display.", color=0x555555)
    state = hud.get("state", "normal")
    if state == "dark_mode":
        return discord.Embed(title="◉ DISPLAY DIMMED", description="Information is concealed. Use `!hud state normal` to restore it.", color=0x555555)
    if state == "signal_degraded":
        return discord.Embed(title="◉ SIGNAL DEGRADED", description="Information is unavailable. Use `!hud state normal` to restore the display.", color=0x555555)
    embed = discord.Embed(title="◉ YOUR DISPLAY", description="The interface rests at the edge of your vision.", color=0x555555)
    discovered = (opening_state(character) or {}).get("discoveries", [])
    if "display" in discovered:
        embed.add_field(name="FEED7", value="A signal you found in the pod. Open it with `!feed7`.", inline=False)
    if "booking" in discovered:
        embed.add_field(name="Remembered booking", value="A gig tomorrow night. Format still unclear. Revisit the notice in the pod with `!inspect booking`.", inline=False)
    elif any(target in discovered for target in ("panels", "display")):
        embed.add_field(name="Unread notice", value="You found a performance notification in the pod. Read it there with `!inspect booking`.", inline=False)
    if not embed.fields:
        embed.description += " No signals or notices have been discovered yet."
    embed.set_footer(text="!hud on · !hud off · !hud state normal")
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
    async def hud(self, ctx, *, action: str = ""):
        """Inspect or configure your display: on, off, state normal/signal degraded/dark mode."""
        words = " ".join(action.casefold().split())
        if words in {"on", "off"}:
            await self._update(ctx, enabled=words == "on")
            return
        if words.startswith("state "):
            state = display_state(words[6:])
            if state:
                await self._update(ctx, state=state)
                return
        if words:
            await ctx.send(USAGE)
            return
        panel = self.panel(str(ctx.author.id), explicit=True)
        if panel is None:
            await ctx.send("Create a character first.")
        else:
            await ctx.send(embed=panel)

    # Compatibility entry points; player-facing help teaches spaced commands.
    @commands.command(name="hud_on", hidden=True)
    async def hud_on(self, ctx, *, extra: str = ""):
        if extra:
            await ctx.send(USAGE)
            return
        await self._update(ctx, enabled=True)

    @commands.command(name="hud_off", hidden=True)
    async def hud_off(self, ctx, *, extra: str = ""):
        if extra:
            await ctx.send(USAGE)
            return
        await self._update(ctx, enabled=False)

    @commands.command(name="hud_state", hidden=True)
    async def hud_state(self, ctx, *, state: str):
        value = display_state(state)
        if value is None:
            await ctx.send(USAGE)
            return
        await self._update(ctx, state=value)


async def setup(bot):
    await bot.add_cog(HudCog(bot))
