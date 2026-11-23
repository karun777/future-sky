"""The crew call uses normal character saves, with only fictional actors on disk."""
import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from fsbot import vela
from fsbot.cogs.vela import VelaCog
from fsbot.encounter_memory import EncounterMemory, EncounterUnavailable
from fsbot.storage import Storage


class VelaTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.path = Path(tmp.name) / "characters.json"
        override = patch("fsbot.storage.CHARACTERS_FILE", str(self.path))
        override.start()
        self.addCleanup(override.stop)
        self.storage = Storage.__new__(Storage)
        self.storage.characters = {"17": {"name": "Pilot", "current_room": vela.POD,
                                        "extra": {"keepsake": ["blue"]}, "credits": 19},
                                   "18": {"name": "Other", "current_room": vela.TABLE}}
        self.other = deepcopy(self.storage.characters["18"])
        self.ch = self.storage.characters["17"]
        self.storage.save_characters()
        self.cog = VelaCog(SimpleNamespace(storage=self.storage))

    def act(self, action):
        return vela.act(self.storage, "17", action)

    async def move(self, room):
        prev, self.ch["current_room"] = self.ch["current_room"], room
        self.storage.save_characters()
        return await self.cog.on_entry({"source": {"actor_id": "17"},
                                        "payload": {"from_room_id": prev, "to_room_id": room}})

    def test_missing_invitation_does_not_start_a_chapter(self):
        before = self.path.read_bytes()
        self.assertIsNone(vela.view(self.ch))
        with self.assertRaises(EncounterUnavailable):
            self.act("read crew call")
        with self.assertRaises(EncounterUnavailable):
            vela.offer_crew_call(self.storage, "absent")
        self.assertEqual(self.path.read_bytes(), before)
        self.assertNotIn("absent", self.storage.characters)

    async def test_table_briefing_return_and_reload(self):
        vela.offer_crew_call(self.storage, "17")
        self.assertIn("routine comet catch", self.act("read crew call"))
        await self.move(vela.TABLE)
        before = self.path.read_bytes()
        self.act("inspect chart")
        self.assertEqual(self.path.read_bytes(), before)
        self.act("tap back")
        with self.assertRaises(EncounterUnavailable):
            self.act("count with vela")
        ctx = SimpleNamespace(author=SimpleNamespace(id=17), send=AsyncMock())
        await self.cog.vela_cmd.callback(self.cog, ctx, action="wait for flash")
        self.assertIn("thumb", ctx.send.await_args.args[0])
        self.assertEqual(vela.view(self.ch)["marks"], ["runup"])
        await self.move(vela.BRIEFING)
        self.assertIn("Start at the inner mark.", self.act("stay quiet"))
        with self.assertRaises(EncounterUnavailable):
            self.act("show torn packet")
        self.assertIn("Start the approach one mark farther out.", self.act("unfold the chart"))
        self.storage.characters = json.loads(self.path.read_text())
        self.ch = self.storage.characters["17"]
        self.assertIn("Start the approach one mark farther out.", self.act(""))
        await self.move(vela.TABLE)
        self.assertIn("First pass", self.act("count with vela"))
        self.act("turn at crease")
        await self.move(vela.BRIEFING)
        self.act("show torn packet")
        card = self.act("tap the interval")
        for row in vela.FACTS:
            self.assertIn(row["order"], card)
        self.assertEqual(self.ch["credits"], 19)
        self.assertEqual(self.ch["extra"]["keepsake"], ["blue"])
        self.assertEqual(self.other, self.storage.characters["18"])
        self.assertIsNone(vela.view(self.other))

    async def test_unread_invitation_and_quiet_briefing(self):
        vela.offer_crew_call(self.storage, "17")
        await self.move(vela.BRIEFING)
        before = self.path.read_bytes()
        for row in vela.FACTS:
            self.assertIn(row["draft"], self.act("stay quiet"))
        self.assertEqual(before, self.path.read_bytes())
        self.assertNotIn("read", EncounterMemory.read(self.ch, vela.KEY).seen)

    def test_failure_retry_and_unrelated_fields(self):
        before = deepcopy(self.ch)
        with patch.object(self.storage, "save_characters", side_effect=OSError):
            with self.assertRaises(OSError):
                vela.offer_crew_call(self.storage, "17")
        self.assertEqual(before, self.ch)
        vela.offer_crew_call(self.storage, "17")
        self.ch["extra"][vela.KEY]["future_field"] = 4
        self.act("read crew call")
        with patch.object(self.storage, "save_characters", side_effect=AssertionError):
            self.act("read crew call")
        self.assertEqual(self.ch["extra"][vela.KEY]["future_field"], 4)
        with self.assertRaises(EncounterUnavailable):
            EncounterMemory.read(self.ch, vela.KEY).report("gap")

    def test_recovery_or_conflicting_encounter(self):
        vela.offer_crew_call(self.storage, "17")
        for extra in ({"recovery": {"stage": "reanimating"}},
                      {"thread_nodes": {"active_thread_node": "choice"}}):
            self.ch["extra"].update(extra)
            self.assertIsNone(vela.view(self.ch))
            self.ch["extra"].pop(next(iter(extra)))
        self.ch["in_cube"] = True
        self.assertIsNone(vela.view(self.ch))
