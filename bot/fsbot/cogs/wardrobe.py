"""Discord-facing pod wardrobe. No world mutation until explicit selection."""
from __future__ import annotations

import json
from pathlib import Path

import discord
from discord.ext import commands

from fsbot.pod_wardrobe import WardrobeError, current_fit, select_uniform
from fsbot.first_impression import first_impression
from fsbot.cogs.router import get_run_channel_by_guild_if_any

CATALOGUE_PATH = Path(__file__).resolve().parents[3] / "data/arrival/pod_uniforms.json"


def load_catalogue() -> dict:
    with CATALOGUE_PATH.open(encoding="utf-8") as stream:
        return json.load(stream)


class WardrobeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        events = getattr(self.bot, "events", None)
        if events:
            events.subscribe("character.entered_room", self._on_room_entry)

    def cog_unload(self):
        events = getattr(self.bot, "events", None)
        if events:
            try:
                events.unsubscribe("character.entered_room", self._on_room_entry)
            except Exception:
                pass

    async def _on_room_entry(self, event):
        source = event.get("source") or {}
        payload = event.get("payload") or {}
        uid = str(source.get("actor_id") or "")
        room = payload.get("to_room_id")
        character = self.bot.storage.characters.get(uid)
        if not isinstance(character, dict):
            return
        reaction = first_impression(character, room)
        if not reaction:
            return
        channel = None
        for guild in getattr(self.bot, "guilds", []):
            channel = await get_run_channel_by_guild_if_any(self.bot, guild, uid)
            if channel:
                break
        if channel is None:
            return
        # Mark only after we have somewhere to deliver. Save before sending
        # to prevent repeated first impressions after later room entries.
        arrival = character.setdefault("extra", {}).setdefault("arrival", {})
        arrival["first_impression_seen"] = True
        try:
            self.bot.storage.save_characters()
        except Exception:
            arrival.pop("first_impression_seen", None)
            return
        title, dialogue = reaction
        await channel.send(embed=discord.Embed(
            title=title + " // FIRST IMPRESSION",
            description=dialogue,
            color=0x555555,
        ))

    def _character(self, ctx):
        return self.bot.storage.characters.get(str(ctx.author.id))

    @commands.command(name="wardrobe")
    async def wardrobe(self, ctx: commands.Context):
        character = self._character(ctx)
        if not isinstance(character, dict):
            await ctx.send("🧬 You need a character before opening the wardrobe.")
            return
        if character.get("current_room") != "pod_room":
            await ctx.send("The pod wardrobe is back in your pod.")
            return
        catalogue = load_catalogue()
        selected = (character.get("extra") or {}).get("arrival", {}).get("pod_uniform_selected")
        embed = discord.Embed(
            title="POD // WARDROBE",
            description="A concealed compartment opens. Four uniforms hang within. Each fits you perfectly.\n\n"
                        "Choose with `!uniform utility`, `!uniform formal`, `!uniform technical` or `!uniform freeform`.",
            color=0x555555,
        )
        for option in catalogue.get("uniforms", []):
            embed.add_field(name=option["name"], value=option["description"], inline=False)
        if selected:
            embed.set_footer(text="Your first selection is recorded. Change your outfit with normal equipment commands.")
        await ctx.send(embed=embed)

    @commands.command(name="uniform")
    async def uniform(self, ctx: commands.Context, choice: str = ""):
        character = self._character(ctx)
        if not isinstance(character, dict):
            await ctx.send("🧬 You need a character first.")
            return
        if character.get("current_room") != "pod_room":
            await ctx.send("You can only make your first uniform selection inside the pod.")
            return
        choice = choice.strip().lower()
        if not choice:
            await ctx.send("Choose: `!uniform utility|formal|technical|freeform`. See `!wardrobe`.")
            return
        try:
            catalogue = load_catalogue()
            updated = select_uniform(character, "pod_" + choice, catalogue, self.bot.storage.items_db)
        except (WardrobeError, OSError, ValueError) as exc:
            await ctx.send(f"⚠️ {exc}")
            return
        user_id = str(ctx.author.id)
        self.bot.storage.characters[user_id] = updated
        try:
            self.bot.storage.save_characters()
        except Exception:
            # Revert in-memory change when durable write fails.
            self.bot.storage.characters[user_id] = character
            await ctx.send("⚠️ The wardrobe could not save your selection. Please try again.")
            return
        fit = current_fit(updated, self.bot.storage.items_db)
        embed = discord.Embed(
            title="POD // ATTIRE CONFIRMED",
            description=f"You step into **{fit['label']}**. The fabric settles against your skin as though it remembers you.\n\n"
                        "Your choice is recorded. Others may draw their own conclusions.",
            color=0x555555,
        )
        embed.add_field(name="Current fit", value=fit["label"])
        embed.add_field(name="Next", value="Try `!fit`, `!inventory` or `!sheet`.", inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="fit")
    async def fit(self, ctx: commands.Context):
        character = self._character(ctx)
        if not isinstance(character, dict):
            await ctx.send("🧬 You need a character first.")
            return
        fit = current_fit(character, self.bot.storage.items_db)
        embed = discord.Embed(title=f"{character.get('name', 'Wanderer')} // CURRENT FIT", color=0x555555)
        embed.add_field(name="Attire", value=fit["label"], inline=False)
        equipped = character.get("equipped") or {}
        other = []
        for slot, item_id in equipped.items():
            if slot == "chest" or not item_id:
                continue
            item = self.bot.storage.items_db.get(item_id, {})
            other.append(f"**{slot.replace('_', ' ').title()}** — {item.get('name', item_id)}")
        embed.add_field(name="Other equipment", value="\n".join(other) if other else "None", inline=False)
        embed.set_footer(text="Your appearance follows what you currently have equipped.")
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(WardrobeCog(bot))
