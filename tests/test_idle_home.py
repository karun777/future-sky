from copy import deepcopy, copy
from types import SimpleNamespace
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch
import unittest
import test_sequence as fixture
from fsbot.events import EventBus
from fsbot.idle_home import KEY, configure, touch, record, next_step
from fsbot.cogs.idle_home import IdleHomeCog
from fsbot.cogs.ambient import AmbientCog

class IdleHomeTests(unittest.IsolatedAsyncioTestCase):
    setUp=fixture.SequenceTests.setUp
    reload=fixture.SequenceTests.reload
    char=fixture.SequenceTests.char
    performer=fixture.SequenceTests.performer
    sequence=fixture.SequenceTests.sequence
    action=fixture.SequenceTests.action
    ready=fixture.SequenceTests.ready
    call=fixture.SequenceTests.call
    eligible=fixture.SequenceTests.eligible
    registry=fixture.SequenceTests.registry

    async def start(self,home=None):
        await self.eligible()
        b=await self.registry()
        b.events=EventBus()
        self.clock=[1000]
        cog=IdleHomeCog(b);cog.now=lambda:self.clock[0]
        await b.add_cog(cog)
        self.idle=cog
        self.message=SimpleNamespace(id=333,channel=self.ctx.channel,author=self.ctx.author,
            guild=None,_state=b._connection,attachments=[],content="!idlehome on 60",
            edited_at=None,created_at=datetime.now(timezone.utc))
        self.char()["run_channel_id"]=str(self.ctx.channel.id)
        cog.commit(self.uid,configure(self.char(),1000,idle_seconds=60,message=self.message,home=home))
        cog.contexts[self.uid]=self.message
        return cog

    async def test_due_walks_normal_route_no_input_refresh_and_durable_completion(self):
        cog=await self.start()
        before=deepcopy(self.char())
        await cog.tick(self.uid)
        self.assertEqual(self.char(),before)
        self.clock[0]=1060
        other=deepcopy(self.storage.characters["other"])
        for _ in range(15):
            await cog.tick(self.uid)
            if self.char()["current_room"]=="pod_room":break
            self.clock[0]+=60
        self.assertEqual(self.char()["current_room"],"pod_room")
        self.assertEqual(record(self.char())["last_input_at"],1000)
        self.assertEqual(record(self.char())["status"],"home")
        self.assertIn("made your way home",record(self.char())["pending_notice"])
        self.assertEqual(self.storage.characters["other"],other)
        # Reload the real persisted JSON, rather than relying on the current object.
        import json
        saved=json.loads(self.path.read_text())[self.uid]
        self.assertEqual(saved["current_room"],"pod_room")
        before=self.path.read_bytes()
        await cog.tick(self.uid)
        self.assertEqual(self.path.read_bytes(),before)

    async def test_human_typing_and_command_cancel_but_auto_does_not(self):
        cog=await self.start()
        self.clock[0]=1060
        generation=record(self.char())["generation"]
        ctx=SimpleNamespace(author=self.ctx.author,_automatic_action=True,
            _idle_generation=generation,_idle_home="pod_room")
        self.assertTrue(await cog.bot_check(ctx))
        self.assertEqual(record(self.char())["last_input_at"],1000)
        await cog.on_typing(self.ctx.channel,self.ctx.author,None)
        self.assertEqual(record(self.char())["last_input_at"],1060)
        self.assertFalse(cog.allow_step(ctx))
        before=self.char()["current_room"]
        await cog.tick(self.uid)
        self.assertEqual(self.char()["current_room"],before)
        ctx=SimpleNamespace(author=self.ctx.author,message=self.message)
        self.clock[0]=1070
        await cog.bot_check(ctx)
        self.assertEqual(record(self.char())["last_input_at"],1070)

    async def test_input_during_departure_stops_before_move(self):
        cog=await self.start()
        self.clock[0]=1060
        nav=self.registry_bot.get_cog("NavigationCog")
        async def interrupt(*args,**kwargs):
            cog.observe(self.uid)
        nav._broadcast_room=interrupt
        original=self.char()["current_room"]
        await cog.tick(self.uid)
        self.assertEqual(self.char()["current_room"],original)
        self.assertEqual(record(self.char())["last_input_at"],1060)

    async def test_blocked_recovery_cube_choice_combat_and_unknown_route(self):
        cog=await self.start()
        self.clock[0]=1060
        original=deepcopy(self.char())
        for extra,flag in [("cube",True),("recovery",True),("choice",True),("combat",True)]:
            self.storage.characters[self.uid]=deepcopy(original)
            ch=self.char()
            if extra=="cube":ch["in_cube"]=True
            if extra=="recovery":ch["extra"]["recovery"]={"stage":"reanimating"}
            if extra=="choice":ch["extra"]["thread_nodes"]={"active_thread_node":"choice"}
            if extra=="combat":ch.setdefault("flags",{})["in_combat"]=True
            await cog.tick(self.uid)
            self.assertEqual(self.char()["current_room"],original["current_room"])
        self.storage.characters[self.uid]=deepcopy(original)
        self.char()["current_room"]="security_checkpoint"
        await cog.tick(self.uid)
        self.assertEqual(self.char()["current_room"],"security_checkpoint")
        self.assertEqual(record(self.char())["status"],"blocked")

    async def test_home_changed_resolves_current_target(self):
        cog=await self.start(home="main_square")
        self.clock[0]=1060
        for _ in range(10):
            await cog.tick(self.uid)
            if self.char()["current_room"]=="main_square":break
        self.assertEqual(self.char()["current_room"],"main_square")
        self.assertEqual(record(self.char())["status"],"home")

    async def test_restart_fetches_verified_original_message_and_resumes(self):
        cog=await self.start()
        cog.contexts.clear()
        self.registry_bot.get_channel=lambda cid:SimpleNamespace(id=self.ctx.channel.id,
            fetch_message=AsyncMock(return_value=self.message))
        self.clock[0]=1060
        before=self.char()["current_room"]
        await cog.tick(self.uid)
        self.assertNotEqual(self.char()["current_room"],before)
        self.assertIn(self.uid,cog.contexts)

    async def test_failed_move_save_retains_room_and_retries(self):
        cog=await self.start()
        self.clock[0]=1060
        original=self.char()["current_room"]
        self.storage.fail_next=True
        await cog.tick(self.uid)
        self.assertEqual(self.char()["current_room"],original)
        self.assertNotIn(self.uid,cog.active)
        await cog.tick(self.uid)
        self.assertNotEqual(self.char()["current_room"],original)

    async def test_activity_save_failure_suspends_auto_until_successful_input(self):
        cog=await self.start()
        self.clock[0]=1060
        self.storage.fail_next=True
        cog.observe(self.uid)
        self.assertIn(self.uid,cog.suspended)
        room=self.char()["current_room"]
        await cog.tick(self.uid)
        self.assertEqual(self.char()["current_room"],room)
        cog.observe(self.uid)
        self.assertNotIn(self.uid,cog.suspended)

    async def test_legacy_rest_does_not_teleport_with_new_cog(self):
        await self.start()
        cog=object.__new__(AmbientCog);cog.bot=self.registry_bot
        original=deepcopy(self.char())
        self.assertFalse(await cog._maybe_handle_rest(guild=None,user_id=self.uid,
            char=self.char(),idle_for=999999,now=999999))
        self.assertEqual(self.char(),original)

    async def test_explicit_sequence_busy_defers_and_off_stays_off(self):
        cog=await self.start()
        self.clock[0]=1060
        runner=self.registry_bot.get_cog("SequenceCog")
        runner.running[self.uid]=object()
        room=self.char()["current_room"]
        await cog.tick(self.uid)
        self.assertEqual(self.char()["current_room"],room)
        runner.running.clear()
        cog.commit(self.uid,configure(self.char(),1060,enabled=False,idle_seconds=60))
        self.clock[0]=10000
        await cog.tick(self.uid)
        self.assertEqual(self.char()["current_room"],room)

    async def test_settings_command_enable_disable_and_change_home(self):
        cog=await self.start()
        ctx=await self.registry_bot.get_context(self.message,cls=fixture.TestContext)
        await IdleHomeCog.idlehome.callback(cog,ctx,action="on 60")
        self.assertTrue(record(self.char())["enabled"])
        await IdleHomeCog.idlehome.callback(cog,ctx,action="home main_square")
        self.assertEqual(record(self.char())["home"],"main_square")
        await IdleHomeCog.idlehome.callback(cog,ctx,action="off")
        self.assertFalse(record(self.char())["enabled"])
        before=deepcopy(self.char())
        await IdleHomeCog.idlehome.callback(cog,ctx,action="on 0")
        self.assertEqual(self.char(),before)

    async def test_notice_retained_without_channel_then_delivered_once(self):
        cog=await self.start(home="lounge_main_floor")
        self.clock[0]=1060
        await cog.tick(self.uid)
        self.assertIn("pending_notice",record(self.char()))
        self.registry_bot._connection._guilds[1]=SimpleNamespace(id=1)
        with patch("fsbot.cogs.idle_home.send_to_player_run_channel_if_any",new=AsyncMock(return_value=True)) as send:
            await cog.deliver(self.uid)
            self.assertNotIn("pending_notice",record(self.char()))
            await cog.deliver(self.uid)
            self.assertEqual(send.await_count,1)

    async def test_restart_wrong_author_message_cannot_move(self):
        cog=await self.start()
        cog.contexts.clear()
        wrong=copy(self.message);wrong.author=SimpleNamespace(id="other")
        self.registry_bot.get_channel=lambda cid:SimpleNamespace(id=self.ctx.channel.id,
            fetch_message=AsyncMock(return_value=wrong))
        self.clock[0]=1060
        before=self.char()["current_room"]
        await cog.tick(self.uid)
        self.assertEqual(self.char()["current_room"],before)

    async def test_auto_and_sequence_children_do_not_bump_ambient_activity(self):
        cog=await self.start()
        ambient=object.__new__(AmbientCog);ambient.note_activity=lambda uid:self.fail("automatic activity")
        for field in ["_automatic_action","_sequence_child"]:
            ctx=SimpleNamespace(author=self.ctx.author,**{field:True})
            await ambient.on_command(ctx)
