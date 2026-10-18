"""Discord item cards and the explicitly entered pod-opening strand."""
import discord
from discord.ext import commands
from fsbot.item_inspection import inspect_item
from fsbot.pod_opening import (GUIDANCE, opening_state, scene_target, prepare_observation, pod_bearings)


class InspectionCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def _pod_view(self, ctx, target=None):
        storage = self.bot.storage
        uid = str(ctx.author.id)
        original = storage.characters.get(uid)
        if not isinstance(original, dict):
            await ctx.send("Create a character first.")
            return False
        if original.get("in_cube") or original.get("current_room") != "pod_room":
            await ctx.send("This awakening begins in the pod.")
            return False
        try:
            updated, view = prepare_observation(original, target)
        except (ValueError, TypeError, AttributeError) as exc:
            await ctx.send(str(exc))
            return False
        if updated != original:
            storage.characters[uid] = updated
            try:
                storage.save_characters()
            except Exception:
                storage.characters[uid] = original
                await ctx.send("The pod could not remember that discovery. Please try again.")
                return False
        title, text, guidance = view
        if target == "garment":
            item_id = (original.get("equipped") or {}).get("chest")
            definition = storage.items_db.get(item_id, {})
            if definition:
                title = definition.get("name", "Your clothing")
                text = ("You are wearing **" + title + "**. A thin chain rests beneath the collar. "
                        "Clothes alone do not establish a job, a faction or a remembered identity.")
        embed = discord.Embed(title=title, description=text, color=discord.Color.dark_teal())
        embed.add_field(name="Your attention", value=guidance, inline=False)
        if target is None or target == "pod":
            exits = storage.rooms.get("pod_room", {}).get("exits", {})
            if isinstance(exits, dict) and exits:
                embed.add_field(name="Beyond the pod", value=" · ".join(
                    f"\x60!go {direction}\x60" for direction in exits), inline=False)
        await ctx.send(embed=embed)
        return True

    @commands.command(name="awaken")
    async def awaken(self, ctx):
        """Enter this performance-arrival strand without resetting a character."""
        character = self.bot.storage.characters.get(str(ctx.author.id))
        if isinstance(character, dict):
            threads = (character.get("extra") or {}).get("thread_nodes") or {}
            if threads.get("active_thread_node") or threads.get("active_encounter_id"):
                await ctx.send("A moment is already open. Finish its listed choice before beginning this awakening.")
                return
            if opening_state(character) and character.get("current_room") == "pod_room" and not character.get("in_cube"):
                await self.present_pod_bearings(ctx)
                return
        await self._pod_view(ctx)

    async def present_pod_bearings(self, ctx):
        character = self.bot.storage.characters.get(str(ctx.author.id))
        state = opening_state(character) if isinstance(character, dict) else None
        if not state or character.get("current_room") != "pod_room" or character.get("in_cube"):
            return False
        text = pod_bearings(character)
        embed = discord.Embed(title="POD // FINDING YOUR BEARINGS", description=text,
                              color=discord.Color.dark_teal())
        embed.add_field(name="Your attention", value=GUIDANCE, inline=False)
        await ctx.send(embed=embed)
        return True

    @commands.command(name="inspect", aliases=["examine"])
    async def inspect(self, ctx, *, item: str = ""):
        storage = self.bot.storage
        character = storage.characters.get(str(ctx.author.id))
        if not isinstance(character, dict):
            await ctx.send("Create a character first.")
            return
        target = scene_target(item)
        if (target and character.get("current_room") == "pod_room"
                and not character.get("in_cube")):
            if not opening_state(character):
                await ctx.send("Begin finding your bearings with `!awaken`.")
                return
            await self._pod_view(ctx, target)
            return
        room = storage.rooms.get(character.get("current_room"), {})
        try:
            item_id, definition, attributes, unlocked = inspect_item(
                item, character, room, storage.items_db)
        except (ValueError, TypeError) as exc:
            await ctx.send(str(exc))
            return
        embed = discord.Embed(
            title=definition.get("name", item_id),
            description=definition.get("description") or "You examine the object, but learn little.",
            color=discord.Color.dark_teal())
        embed.add_field(name="Type", value=str(definition.get("type", "unknown")).title())
        embed.add_field(name="Rarity", value=str(definition.get("rarity", "unknown")).title())
        if attributes:
            embed.add_field(name="Known attributes",
                            value="\n".join(f"**{k.replace('_', ' ').title()}:** {v}" for k, v in attributes.items()),
                            inline=False)
        else:
            embed.add_field(name="Known attributes", value="None discovered yet.", inline=False)
        uses = definition.get("uses", [])
        if isinstance(uses, list) and uses:
            public_uses = [u.get("label", "") for u in uses
                           if isinstance(u, dict) and (not u.get("discovery") or u["discovery"] in unlocked)]
            if public_uses:
                embed.add_field(name="Known uses", value=", ".join(public_uses), inline=False)
        image = definition.get("image")
        if isinstance(image, str) and image.startswith("https://"):
            embed.set_image(url=image)
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(InspectionCog(bot))
