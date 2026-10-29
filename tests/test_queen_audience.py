import unittest
from copy import deepcopy
import test_rehearsal as fixture
from fsbot.queen_audience import KEY, prepare
from fsbot.cogs.queen_audience import QueenAudienceCog
from fsbot.cogs.rat_messenger import RatMessengerCog
from fsbot.rehearsal import KEY as REHEARSAL, ROOM
from fsbot.rat_messenger import KEY as RAT
from fsbot.terrace_delivery import APPROACH, KEY as DELIVERY, inventory_lines

class QueenTests(unittest.IsolatedAsyncioTestCase):
    setUp=fixture.RehearsalTests.setUp
    reload=fixture.RehearsalTests.reload
    char=fixture.RehearsalTests.char
    performer=fixture.RehearsalTests.performer
    sequence=fixture.RehearsalTests.sequence
    action=fixture.RehearsalTests.action
    ready=fixture.RehearsalTests.ready
    call=fixture.RehearsalTests.call

    async def audience(self,action=""):
        self.ctx.messages.clear()
        await QueenAudienceCog.queen.callback(QueenAudienceCog(self.bot),self.ctx,action=action)
        return self.ctx.text()

    async def eligible(self):
        await self.ready()
        await RatMessengerCog.rat.callback(RatMessengerCog(self.bot),self.ctx,action="message")
        for a in ["book","go","start","return","wait 10"]:await self.call(a)

    async def test_new_rat_wait_and_rehearsal_both_required(self):
        await self.ready()
        await RatMessengerCog.rat.callback(RatMessengerCog(self.bot),self.ctx,action="message")
        self.assertEqual(self.char()["extra"][RAT]["stage"],"pending")
        self.assertIn("Finish your rehearsal",await self.audience())
        for a in ["book","go","start","return"]:await self.call(a)
        self.assertIn("10 more minutes",await self.audience())
        await self.call("wait 10")
        await self.audience()
        self.assertEqual(self.char()["extra"][RAT]["stage"],"arranged")
        self.assertEqual(self.char()["extra"][KEY]["stage"],"met")

    async def test_payment_music_provenance_and_repeat_no_duplicate(self):
        await self.eligible()
        original=deepcopy(self.char()["extra"][DELIVERY])
        cash=self.char()["credits"]
        for a in ["","talk","pay"]:
            await self.audience(a);self.reload()
        s=self.char()["extra"][KEY]
        self.assertEqual(s["stage"],"received")
        self.assertEqual(s["approval"],"unresolved")
        self.assertEqual(self.char()["credits"],cash-1)
        self.assertEqual(s["music"]["source"],"dark_rat_queen")
        self.assertEqual(self.char()["extra"][DELIVERY],original)
        self.assertIn("Queen’s music", "\n".join(inventory_lines(self.char())))
        before=self.path.read_bytes()
        for a in ["pay","talk",""]:await self.audience(a)
        self.assertEqual(self.path.read_bytes(),before)

    async def test_save_failures_roll_back_including_money(self):
        await self.eligible()
        for a in ["","talk","pay"]:
            before=self.path.read_bytes();memory=deepcopy(self.char())
            self.storage.fail_next=True
            self.assertIn("could not be remembered",await self.audience(a))
            self.assertEqual(self.char(),memory)
            self.assertEqual(self.path.read_bytes(),before)
            await self.audience(a)

    async def test_no_cash_bar_tab_cannot_pay(self):
        await self.eligible()
        await self.audience();await self.audience("talk")
        self.char()["credits"]=0
        self.char()["extra"]["performance_bar_tab_v1"]={"granted":True,"balance":20}
        before=deepcopy(self.char())
        self.assertIn("bar tab cannot",await self.audience("pay"))
        self.assertEqual(self.char(),before)

    async def test_legacy_meeting_still_requires_wait_and_location(self):
        await self.eligible()
        self.char()["extra"][RAT]={"version":1,"stage":"arranged",
            "meeting":{"contact":"dark_rat_queen","room":APPROACH,"status":"arranged"}}
        self.char()["extra"][REHEARSAL]["elapsed_minutes"]=110
        self.assertIn("10 more minutes",await self.audience())
        self.char()["extra"][REHEARSAL]["elapsed_minutes"]=120
        self.char()["current_room"]=ROOM
        self.assertIn("Stardock",await self.audience())
        self.char()["current_room"]=APPROACH
        self.char()["in_cube"]=True
        self.assertIn("Return from the Cube",await self.audience())
