"""Discord-facing pod wardrobe. No world mutation until explicit selection."""
from __future__ import annotations

import json
from pathlib import Path

import discord
from discord.ext import commands

from fsbot.pod_wardrobe import WardrobeError, current_fit, select_uniform
from fsbot.first_impression import first_impression
from fsbot.dressing import resolve_clothing, clothing_slots, normal
from fsbot.token_exchange import ExchangeError, discover_token, exchange_token
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
    async def wardrobe(self, ctx: commands.Context, *, action: str = ""):
        character = self._character(ctx)
        if not isinstance(character, dict):
            await ctx.send("🧬 You need a character before opening the wardrobe.")
            return
        if character.get("current_room") != "pod_room":
            await ctx.send("The pod wardrobe is back in your pod.")
            return
        catalogue = load_catalogue()
        selected = (character.get("extra") or {}).get("arrival", {}).get("pod_uniform_selected")
        if action:
            query = action.strip()
            if not query.casefold().startswith("inspect "):
                await ctx.send("Use !wardrobe or !wardrobe inspect <outfit>.")
                return
            query = normal(query[8:])
            options = [o for o in catalogue.get("uniforms", []) if query in
                       {normal(o["name"]), normal(o["id"]), normal(o["id"].removeprefix("pod_"))}]
            if len(options) != 1:
                await ctx.send("That outfit is not listed. Use !wardrobe to browse.")
                return
            option = options[0]
            await ctx.send(embed=discord.Embed(title=option["name"], description=option["description"],
                                             color=0x555555))
            return
        guidance = ("Your first outfit has already been selected. You can change into clothes you carry "
                    "with !wear <clothing name>, or remove them with !remove <clothing name>."
                    if selected else
                    "Choose your first outfit with !uniform utility, !uniform formal, "
                    "!uniform technical or !uniform freeform.")
        embed = discord.Embed(
            title="POD // WARDROBE",
            description="The clothing compartment opens.\n\n" + guidance +
                        "\n\nExamine an option with !wardrobe inspect <outfit>. Check what you wear with !fit.",
            color=0x555555,
        )
        for option in catalogue.get("uniforms", []):
            embed.add_field(name=option["name"], value=option["description"], inline=False)
        if selected:
            embed.set_footer(text="The listed outfits are the existing first-selection catalogue; browsing grants nothing.")
        await ctx.send(embed=embed)

    @commands.command(name="uniform")
    async def uniform(self, ctx: commands.Context, *, choice: str = ""):
        character = self._character(ctx)
        if not isinstance(character, dict):
            await ctx.send("🧬 You need a character first.")
            return
        if character.get("current_room") != "pod_room":
            await ctx.send("You can only make your first uniform selection inside the pod.")
            return
        if (character.get("extra") or {}).get("arrival", {}).get("pod_uniform_selected"):
            await ctx.send("Your first outfit is already selected. Use !inventory, then !wear <clothing name> "
                           "or !remove <clothing name>. Check your appearance with !fit.")
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

    @commands.command(name="wear")
    async def wear(self, ctx: commands.Context, *, garment: str = ""):
        character = self._character(ctx)
        if not isinstance(character, dict):
            await ctx.send("You need a character first.")
            return
        try:
            key, slot = resolve_clothing(character, self.bot.storage.items_db, garment)
        except (ValueError, TypeError) as exc:
            await ctx.send(str(exc))
            return
        core = self.bot.get_cog("CoreCog")
        if core is None:
            await ctx.send("Equipment is unavailable. Please try again later.")
            return
        await core.equip_cmd.callback(core, ctx, key, slot)

    @commands.command(name="remove")
    async def remove(self, ctx: commands.Context, *, garment: str = ""):
        character = self._character(ctx)
        if not isinstance(character, dict):
            await ctx.send("You need a character first.")
            return
        try:
            key, slot = resolve_clothing(character, self.bot.storage.items_db, garment, worn=True)
        except (ValueError, TypeError) as exc:
            await ctx.send(str(exc))
            return
        core = self.bot.get_cog("CoreCog")
        if core is None:
            await ctx.send("Equipment is unavailable. Please try again later.")
            return
        await core.unequip_cmd.callback(core, ctx, slot)

    @commands.command(name="counterkeeper")
    async def counterkeeper(self, ctx: commands.Context):
        """Follow up the freeform motif recognition through Thread Nodes."""
        character = self._character(ctx)
        if not isinstance(character, dict):
            await ctx.send("You need a character first.")
            return
        if character.get("current_room") != "neptune_lounge":
            await ctx.send("The counterkeeper is at the Neptune Lounge arrival counter.")
            return
        arrival = (character.get("extra") or {}).get("arrival") or {}
        if not arrival.get("first_impression_seen") or arrival.get("pod_uniform_selected") != "pod_freeform":
            await ctx.send("The counterkeeper gives you a polite nod, then returns to work.")
            return
        if (character.get("equipped") or {}).get("chest") != "itm_pod_uniform_freeform":
            await ctx.send("Without the embroidered attire, the counterkeeper has nothing to ask.")
            return
        nodes = self.bot.get_cog("ThreadNodesCog")
        if nodes is None:
            await ctx.send("The counterkeeper seems distracted. Try again later.")
            return
        node_id = "nl_counterkeeper_motif"
        nodes.reload_nodes()
        if nodes._has_completed(character, node_id):
            await ctx.send({"invented_story": "The counterkeeper looks up. “How is that story of yours coming along?” A flicker of amusement. “Don’t worry. I haven’t told anyone.”", "pod_truth": "The counterkeeper lowers their voice. “I have been thinking about that pod. Who stocked it, I mean.”", "asked_about_motif": "The counterkeeper glances at the embroidery. “I said I had seen it. I never said I understood it.”"}.get((character.get("flags") or {}).get("counterkeeper_motif_answer"), "The counterkeeper recognises you, but says nothing more."))
            return
        if nodes._get_active_node_id(character):
            await nodes.present_active_node(ctx, str(ctx.author.id))
            return
        await nodes._start_node(ctx, str(ctx.author.id), node_id)

    async def _persist_item_action(self, ctx, updated, original):
        uid = str(ctx.author.id)
        self.bot.storage.characters[uid] = updated
        try:
            self.bot.storage.save_characters()
        except Exception:
            self.bot.storage.characters[uid] = original
            await ctx.send("The world failed to remember that action. Try again.")
            return False
        return True

    @commands.command(name="search")
    async def search_pod(self, ctx: commands.Context, *, target: str = ""):
        character = self._character(ctx)
        if not isinstance(character, dict):
            await ctx.send("You need a character first.")
            return
        if character.get("current_room") != "pod_room":
            await ctx.send("You search the area, but find nothing tucked away.")
            return
        if target.strip().lower() not in ("", "pod", "panel", "loose panel"):
            await ctx.send("You find no hidden compartment there. Try `!search panel`.")
            return
        try:
            updated = discover_token(character)
        except ExchangeError as exc:
            await ctx.send(str(exc))
            return
        if await self._persist_item_action(ctx, updated, character):
            await ctx.send("Your fingertips catch a loose panel beneath the pod berth. Behind it: an **Unmarked Brass Token**, warm despite the cold metal around it. You pocket it. (`!inventory`)")

    @commands.command(name="offer")
    async def offer_item(self, ctx: commands.Context, *, target: str = ""):
        character = self._character(ctx)
        if not isinstance(character, dict):
            await ctx.send("You need a character first.")
            return
        if target.strip().lower() not in ("token", "brass token", "counterkeeper token", "token counterkeeper"):
            await ctx.send("To offer the found object, use `!offer token`.")
            return
        try:
            updated = exchange_token(character)
        except ExchangeError as exc:
            await ctx.send(str(exc))
            return
        if await self._persist_item_action(ctx, updated, character):
            await ctx.send("You place the brass token on the counter. The counterkeeper stops polishing. They turn it over, find the notch, and close their fingers around it. “Where did you find this?” They glance at your clothes, then back at the token. “No. Don't answer that here.” The token disappears beneath the counter. **The exchange is remembered.**")

    @commands.command(name="fit")
    async def fit(self, ctx: commands.Context):
        character = self._character(ctx)
        if not isinstance(character, dict):
            await ctx.send("🧬 You need a character first.")
            return
        fit = current_fit(character, self.bot.storage.items_db)
        embed = discord.Embed(title=f"{character.get('name', 'Wanderer')} // CURRENT FIT", color=0x555555)
        embed.add_field(name="Attire", value=fit["label"] if fit["chest_item_id"] else "No chest garment equipped.", inline=False)
        equipped = character.get("equipped") or {}
        other = []
        for slot, item_id in equipped.items():
            if slot == "chest" or not item_id:
                continue
            item = self.bot.storage.items_db.get(item_id, {})
            other.append(f"**{slot.replace('_', ' ').title()}** — {item.get('name', item_id)}")
        embed.add_field(name="Other equipment", value="\n".join(other) if other else "None", inline=False)
        embed.set_footer(text="Change clothes with !wear <name> or !remove <name>. Check !inventory for carried clothes.")
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(WardrobeCog(bot))
