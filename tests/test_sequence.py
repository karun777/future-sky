import asyncio
from datetime import datetime, timezone
from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import AsyncMock
import unittest
import discord
from discord.ext import commands
import test_queen_audience as fixture
from fsbot.cogs.sequence import SequenceCog
from fsbot.cogs.navigation import NavigationCog
from fsbot.cogs.work import WorkCog
from fsbot.cogs.queen_audience import QueenAudienceCog
from fsbot.sequence import parse_sequence, result
from fsbot.terrace_delivery import APPROACH
from fsbot.queen_audience import KEY

class TestContext(commands.Context):
    async def send(self, content=None, **kwargs):
        return await self.bot.capture.send(content, **kwargs)

class SequenceTests(unittest.IsolatedAsyncioTestCase):
    setUp=fixture.QueenTests.setUp
    reload=fixture.QueenTests.reload
    char=fixture.QueenTests.char
    performer=fixture.QueenTests.performer
    sequence=fixture.QueenTests.sequence
    action=fixture.QueenTests.action
    ready=fixture.QueenTests.ready
    call=fixture.QueenTests.call
    eligible=fixture.QueenTests.eligible

    async def registry(self):
        old=self.bot
        bot=commands.Bot(command_prefix="!",intents=discord.Intents.none())
        await bot._async_setup_hook()
        self.addAsyncCleanup(bot.close)
        bot._connection.user=SimpleNamespace(id=0)
        bot.storage=old.storage;bot.state=old.state;bot.presence=old.presence
        bot.capture=self.ctx
        self.registry_bot=bot
        for cog in [NavigationCog(bot),WorkCog(bot),QueenAudienceCog(bot),SequenceCog(bot)]:
            await bot.add_cog(cog)
        return bot

    async def run_script(self,script):
        b=self.registry_bot
        message=SimpleNamespace(content="!sequence "+script,author=self.ctx.author,
            channel=self.ctx.channel,guild=None,id=901,_state=b._connection,attachments=[],
            edited_at=None,created_at=datetime.now(timezone.utc))
        self.ctx.messages.clear()
        context=await b.get_context(message,cls=TestContext)
        try:
            await context.command.invoke(context)
        except commands.CheckFailure:
            pass
        return self.ctx.text()

    async def test_real_six_steps_and_single_fee(self):
        await self.eligible()
        self.char()["extra"][KEY]={"version":1,"stage":"rapport","approval":"unresolved","fee":1}
        self.storage.save_characters()
        b=await self.registry()
        cash=self.char()["credits"]
        text=await self.run_script("go north; go outside; work bar; go inside; go south; queen pay")
        self.assertIn("Sequence complete: 6/6",text)
        self.assertEqual(self.char()["extra"][KEY]["stage"],"received")
        self.assertEqual(self.char()["current_room"],APPROACH)
        self.assertGreaterEqual(self.char()["credits"],cash-1)

    async def test_failed_move_stops_before_work(self):
        await self.eligible();await self.registry()
        before=deepcopy(self.char())
        text=await self.run_script("go nowhere; work bar")
        self.assertIn("stopped after 0/2",text)
        self.assertEqual(self.char(),before)

    async def test_failed_work_preserves_prior_move(self):
        await self.eligible();await self.registry()
        text=await self.run_script("go north; work bar; go south")
        self.assertIn("stopped after 1/3",text)
        self.assertEqual(self.char()["current_room"],"lounge_main_floor")

    async def test_checks_and_call_once_are_not_bypassed(self):
        await self.eligible();b=await self.registry()
        seen=[]
        async def check(ctx):
            seen.append(ctx.command.name)
            return ctx.command.name!="go"
        b.add_check(check)
        text=await self.run_script("go north; go south")
        self.assertIn("stopped after 0/2",text)
        self.assertEqual(self.char()["current_room"],APPROACH)
        self.assertIn("go",seen)
        b.remove_check(check)
        b.add_check(check,call_once=True)
        text=await self.run_script("go north")
        self.assertIn("stopped after 0/1",text)

    async def test_invalid_script_preflight_and_alias(self):
        await self.eligible();b=await self.registry()
        for script in ["go north; sequence go south","go north; queen talk","go north;;go south","go north;"*13,"teleport pod_room"]:
            before=deepcopy(self.char())
            await self.run_script(script)
            self.assertEqual(self.char(),before)
        text=await self.run_script("!move north; !move south")
        self.assertIn("complete: 2/2",text)

    async def test_save_failure_and_recovery_guard(self):
        await self.eligible();b=await self.registry()
        before=deepcopy(self.char())
        self.storage.fail_next=True
        text=await self.run_script("go north; go outside")
        self.assertIn("stopped after 0/2",text)
        self.assertEqual(self.char()["current_room"],before["current_room"])
        from fsbot.cogs.recovery import RecoveryCog
        guard=RecoveryCog(b)
        self.char()["extra"]["recovery"]={"stage":"reanimating"}
        guard.service.refresh=lambda uid:False
        b.add_check(guard.bot_check)
        text=await self.run_script("go north")
        self.assertIn("body is in recovery",text)
        self.assertEqual(self.char()["current_room"],APPROACH)

    async def test_choice_stops_before_or_after_movement(self):
        await self.eligible();b=await self.registry()
        self.char()["extra"]["thread_nodes"]={"active_thread_node":"test"}
        text=await self.run_script("go north")
        self.assertIn("stopped after 0/1",text)
        self.char()["extra"]["thread_nodes"]={}
        async def open_choice(cog,ctx):
            self.char()["extra"]["thread_nodes"]={"active_thread_node":"test"}
        b.get_command("go").after_invoke(open_choice)
        text=await self.run_script("go north; go south")
        self.assertIn("stopped after 1/2",text)
        self.assertEqual(self.char()["current_room"],"lounge_main_floor")

    async def test_overlap_blocked_and_lock_released(self):
        await self.eligible();b=await self.registry()
        cog=b.get_cog("SequenceCog")
        entered=asyncio.Event();release=asyncio.Event()
        async def hold(cog,ctx):
            entered.set();await release.wait()
        b.get_command("go").before_invoke(hold)
        task=asyncio.create_task(self.run_script("go north"))
        await asyncio.wait_for(entered.wait(),timeout=3)
        foreign=SimpleNamespace(author=self.ctx.author,send=AsyncMock(),_sequence_child=False)
        self.assertFalse(await cog.bot_check(foreign))
        foreign._sequence_child=True
        self.assertFalse(await cog.bot_check(foreign))
        release.set();await task
        self.assertFalse(cog.running)

    async def test_payment_failure_stops_following_move(self):
        await self.eligible();await self.registry()
        self.char()["extra"][KEY]={"version":1,"stage":"rapport","fee":1,"approval":"unresolved"}
        self.char()["credits"]=0
        text=await self.run_script("queen pay; go north")
        self.assertIn("stopped after 0/2",text)
        self.assertEqual(self.char()["current_room"],APPROACH)
        self.assertEqual(self.char()["extra"][KEY]["stage"],"rapport")

    async def test_command_cooldown_checked_for_each_step(self):
        await self.eligible();b=await self.registry()
        go=b.get_command("go")
        go._buckets=commands.CooldownMapping.from_cooldown(1,60,commands.BucketType.user)
        text=await self.run_script("go north; go south")
        self.assertIn("CommandOnCooldown",text)
        self.assertIn("stopped after 1/2",text)
        self.assertEqual(self.char()["current_room"],"lounge_main_floor")
