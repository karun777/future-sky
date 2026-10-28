from copy import deepcopy
import unittest
import test_terrace_delivery as fixture
from fsbot.rehearsal import KEY, ROOM, register_room, prepare, listing
from fsbot.rat_messenger import KEY as RAT
from fsbot.terrace_delivery import APPROACH, KEY as USB
from fsbot.cogs.rehearsal import RehearsalCog
from fsbot.cogs.core import CoreCog

class RehearsalTests(unittest.IsolatedAsyncioTestCase):
    setUp = fixture.TerraceDeliveryTests.setUp
    char = fixture.TerraceDeliveryTests.char
    performer = fixture.TerraceDeliveryTests.performer
    sequence = fixture.TerraceDeliveryTests.sequence
    action = fixture.TerraceDeliveryTests.action

    def reload(self):
        fixture.TerraceDeliveryTests.reload(self)
        register_room(self.storage.rooms)

    async def ready(self):
        self.performer()
        await self.sequence()
        self.char()["current_room"] = APPROACH
        self.char()["extra"][RAT] = {"version":1,"stage":"tip"}
        self.storage.save_characters()

    async def call(self, action):
        self.ctx.messages.clear()
        await RehearsalCog.rehearsal.callback(RehearsalCog(self.bot), self.ctx, action=action)
        return self.ctx.text()

    async def test_feed_booking_complete_return_persisted_and_music_untouched(self):
        await self.ready()
        before = deepcopy(self.char()["extra"][USB])
        others = deepcopy(self.storage.characters["other"])
        await CoreCog.feed7.callback(CoreCog(self.bot),self.ctx)
        self.assertIn("ELEMENTAL SOUND",self.ctx.text())
        for action in ["book","go","start","return"]:
            await self.call(action)
            self.assertIn("embed", self.ctx.messages[-1])
            self.reload()
        s=self.char()["extra"][KEY]
        self.assertEqual(s["elapsed_minutes"],110)
        self.assertEqual(s["practice_minutes"],60)
        self.assertEqual(s["mode"],"conscious")
        self.assertEqual(self.char()["current_room"],APPROACH)
        self.assertEqual(self.char()["extra"][USB],before)
        self.assertEqual(self.storage.characters["other"],others)
        before=self.path.read_bytes()
        await self.call("return")
        self.assertEqual(self.path.read_bytes(),before)

    async def test_atomic_save_failure_every_transition(self):
        await self.ready()
        for action in ["book","wait 5","go","start","return"]:
            before=self.path.read_bytes()
            memory=deepcopy(self.char())
            self.storage.fail_next=True
            self.assertIn("could not be remembered",await self.call(action))
            self.assertEqual(self.path.read_bytes(),before)
            self.assertEqual(self.char(),memory)
            await self.call(action)

    async def test_late_shortened_missed_and_rebook(self):
        await self.ready()
        for action in ["book","wait 30","go","start"]:
            await self.call(action)
        self.assertEqual(self.char()["extra"][KEY]["practice_minutes"],40)
        await self.ready()
        # Start a fresh synthetic rehearsal, without touching production records.
        self.char()["extra"].pop(KEY,None)
        for action in ["book","wait 70","go","start"]:
            await self.call(action)
        self.assertEqual(self.char()["extra"][KEY]["stage"],"missed")
        self.assertNotIn("practice_minutes",self.char()["extra"][KEY])
        await self.call("rebook")
        self.assertEqual(self.char()["extra"][KEY]["elapsed_minutes"],0)

    async def test_routine_is_explicit_no_approval(self):
        await self.ready()
        for action in ["book","go","routine"]:
            await self.call(action)
        self.assertEqual(self.char()["extra"][KEY]["mode"],"habitual")
        self.assertNotIn("approval",self.char()["extra"][KEY])
        before=self.path.read_bytes()
        await self.call("routine")
        self.assertEqual(self.path.read_bytes(),before)

    async def test_guards_routes_and_registration(self):
        await self.ready()
        self.char()["in_cube"]=True
        self.assertNotIn("embed", (await self.call("book"),self.ctx.messages[-1])[1])
        self.char()["in_cube"]=False
        await self.call("book")
        self.storage.rooms["main_square"]["exits"]["up"]="elsewhere"
        before=deepcopy(self.char())
        self.assertIn("route is unavailable",await self.call("go"))
        self.assertEqual(self.char(),before)
        self.char()["extra"][KEY]={"version":1}
        self.assertIn("record is unavailable",await self.call("start"))
        rooms={"sector_42":{"exits":{"east":"other"}}}
        before=deepcopy(rooms)
        with self.assertRaises(ValueError): register_room(rooms)
        self.assertEqual(rooms,before)
