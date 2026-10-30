"""Recovery commands, global body-action gate and durable heartbeat completion."""
import logging
from discord.ext import commands
from fsbot.recovery import RecoveryService, record, recovering, DAY


class RecoveryCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.service = RecoveryService(bot)

    async def cog_load(self):
        self.bot.events.subscribe("heartbeat.advanced", self.on_heartbeat)

    async def cog_unload(self):
        self.bot.events.unsubscribe("heartbeat.advanced", self.on_heartbeat)

    async def on_heartbeat(self, event):
        for uid, character in list(self.bot.storage.characters.items()):
            if recovering(character):
                try:
                    self.service.refresh(uid)
                except Exception:
                    logging.getLogger("futuresky.recovery").exception("Recovery completion failed; retained for retry")

    async def bot_check(self, ctx):
        ctx._recovery_denial_sent = False
        uid = str(ctx.author.id)
        character = self.bot.storage.characters.get(uid)
        if not isinstance(character, dict) or not recovering(character):
            return True
        try:
            self.service.refresh(uid)
        except Exception:
            await ctx.send("Recovery could not be checked safely. Please try again.")
            ctx._recovery_denial_sent = True
            return False
        if not recovering(self.bot.storage.characters[uid]):
            return True
        name = getattr(ctx.command, "qualified_name", "")
        if name in {"recovery", "pod_delivery", "help", "commands", "command", "time", "feed7"}:
            return True
        await ctx.send("Your body is in recovery. Use `!recovery` for its status; bodily actions must wait.")
        ctx._recovery_denial_sent = True
        return False

    @commands.command(name="recovery")
    async def recovery(self, ctx):
        uid = str(ctx.author.id)
        if uid not in self.bot.storage.characters:
            await ctx.send("Create a character first.")
            return
        try:
            self.service.refresh(uid)
            state = record(self.bot.storage.characters[uid])
            if not state:
                text = "No bodily recovery is recorded."
            elif state["stage"] == "brain_review":
                text = "Brain continuity is unresolved. No automatic reanimation or progress wipe will occur."
            elif state["stage"] == "ready":
                text = "Reanimation is complete. Your possessions await in the pod: `!pod_delivery collect`. Find your bearings with `!awaken`."
            else:
                remaining = max(0, state["ready_at"] - self.service.now())
                text = (f"Reanimation: {remaining / DAY:.3f} in-world days remaining. "
                        "Your possessions have been secured in your pod. Memory reintegration is a separate process.")
            await ctx.send(text)
        except Exception:
            await ctx.send("Recovery could not be checked safely. Please try again.")

    @commands.command(name="pod_delivery")
    async def pod_delivery(self, ctx, action: str = ""):
        uid = str(ctx.author.id)
        if uid not in self.bot.storage.characters:
            await ctx.send("Create a character first.")
            return
        try:
            if action == "collect":
                self.service.collect(uid)
                await ctx.send("Your pod delivery is back in your possession. Repeating collection adds nothing twice.")
            elif action:
                await ctx.send("Use `!pod_delivery` or `!pod_delivery collect`.")
            else:
                pod = self.bot.storage.characters[uid].get("extra", {}).get("pod_delivery", {})
                from fsbot.terrace_delivery import secured_inventory_lines
                count = sum(pod.get("items", {}).values()) + len(secured_inventory_lines(self.bot.storage.characters[uid]))
                await ctx.send(f"Your private pod delivery holds {count} item(s). Collect in the pod after reanimation: `!pod_delivery collect`.")
        except Exception:
            await ctx.send("Delivery could not be collected. Be in the pod after reanimation; retry if saving failed.")


async def setup(bot):
    await bot.add_cog(RecoveryCog(bot))
