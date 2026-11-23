from discord.ext import commands

from fsbot import vela
from fsbot.encounter_memory import EncounterUnavailable
from fsbot.events import EventResult


class VelaCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        self.bot.events.subscribe("character.entered_room", self.on_entry)

    def cog_unload(self):
        self.bot.events.unsubscribe("character.entered_room", self.on_entry)

    async def on_entry(self, event):
        uid = str(event["source"].get("actor_id", ""))
        move = event["payload"]
        if vela.returned_to_table(self.bot.storage, uid, move.get("from_room_id"), move.get("to_room_id")):
            return EventResult.applied("Returned to Vela’s table.")
        return EventResult.no_match("No table memory changed.")

    @commands.command(name="vela")
    async def vela_cmd(self, ctx, *, action=""):
        uid = str(ctx.author.id)
        try:
            message = vela.act(self.bot.storage, uid, action)
            available = vela.view(self.bot.storage.characters[uid])["commands"]
            message += "\n\n" + " · ".join("!vela " + cmd for cmd in available)
        except EncounterUnavailable as exc:
            message = str(exc)
        except OSError:
            message = "Your observation could not be saved. Try again."
        await ctx.send(message)


async def setup(bot):
    await bot.add_cog(VelaCog(bot))
