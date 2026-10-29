"""Invoke supported commands through fresh normal contexts and command checks."""
import asyncio
from copy import copy
import logging
from discord.ext import commands
from fsbot.sequence import parse_sequence, requires_choice

class SequenceCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.running = {}

    async def bot_check(self, ctx):
        owner = self.running.get(str(ctx.author.id))
        if owner is not None and not (owner is asyncio.current_task() and getattr(ctx, "_sequence_child", False)):
            await ctx.send("Your sequence is running. Wait for it to finish before issuing another command.")
            return False
        return True

    @commands.command(name="sequence")
    async def sequence(self, ctx, *, script=""):
        try:
            steps = parse_sequence(self.bot, script)
        except ValueError as exc:
            await ctx.send(str(exc))
            return
        uid = str(ctx.author.id)
        nav = self.bot.get_cog("NavigationCog")
        if nav and uid in nav.walking:
            await ctx.send("A movement is finishing. Try your sequence again shortly.")
            return
        if uid in self.running:
            await ctx.send("Your sequence is already running.")
            return
        self.running[uid] = asyncio.current_task()
        completed = 0
        stopped = False
        try:
            for index, step in enumerate(steps, 1):
                character = self.bot.storage.characters.get(uid)
                if not isinstance(character, dict):
                    await ctx.send("Create a character first.")
                    stopped = True
                    break
                if requires_choice(character):
                    await ctx.send("A choice or encounter needs your attention.")
                    stopped = True
                    break
                message = copy(ctx.message)
                message.content = str(ctx.prefix or "!") + step
                child = await self.bot.get_context(message, cls=type(ctx))
                child._sequence_child = True
                child.sequence_result = None
                try:
                    if child.command is None:
                        raise commands.CommandNotFound()
                    if not await self.bot.can_run(child, call_once=True):
                        raise commands.CheckFailure()
                    self.bot.dispatch("command", child)
                    await child.command.invoke(child)
                except commands.CommandError as exc:
                    if child.sequence_result in {"success", "choice"}:
                        completed += 1
                    if not isinstance(exc, commands.CheckFailure):
                        await ctx.send(f"Step {index} could not complete ({type(exc).__name__}).")
                    stopped = True
                    break
                except Exception:
                    if child.sequence_result in {"success", "choice"}:
                        completed += 1
                    logging.getLogger("futuresky.sequence").exception("Sequence stopped at step %s", index)
                    await ctx.send(f"Step {index} could not complete.")
                    stopped = True
                    break
                if child.sequence_result not in {"success", "choice"}:
                    stopped = True
                    break
                completed += 1
                if child.sequence_result == "choice":
                    stopped = True
                    break
                self.bot.dispatch("command_completion", child)
                if requires_choice(self.bot.storage.characters[uid]):
                    await ctx.send("A new choice or encounter needs your attention.")
                    stopped = True
                    break
            if completed == len(steps) and not stopped:
                await ctx.send(f"Sequence complete: {completed}/{len(steps)} actions.")
            else:
                remaining = "; ".join(steps[completed:]) or "none"
                await ctx.send(f"Sequence stopped after {completed}/{len(steps)} completed actions. "
                               f"Earlier actions remain. Remaining: {remaining}")
        finally:
            self.running.pop(uid, None)

async def setup(bot):
    await bot.add_cog(SequenceCog(bot))
