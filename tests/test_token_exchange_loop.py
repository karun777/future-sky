"""Offline command-callback loop: search pod -> reload -> relocate fixture -> offer.
No bot login, event loop service, live Storage instance, or Discord send is used.
"""
import json
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest

from fsbot.cogs.wardrobe import WardrobeCog
from fsbot.storage import save_json
from fsbot.token_exchange import TOKEN


class JsonFixtureStorage:
    """Uses production atomic JSON writer, exclusively on a temporary path."""

    def __init__(self, path):
        self.path = path
        self.characters = json.loads(path.read_text())
        self.fail_next = False
        self.save_calls = 0

    def save_characters(self):
        self.save_calls += 1
        if self.fail_next:
            self.fail_next = False
            raise OSError("injected failure before fixture write")
        save_json(str(self.path), self.characters)


class CaptureContext:
    def __init__(self, uid="fixture-a"):
        self.author = SimpleNamespace(id=uid)
        self.messages = []

    async def send(self, message):
        self.messages.append(message)


class TokenExchangeLoopTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.temp = TemporaryDirectory(prefix="futuresky-token-loop-")
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "characters.json"
        self.original = {
            "fixture-a": {
                "name": "Fixture Traveller", "current_room": "pod_room",
                "bag": {"fixture_keepsake": 1}, "flags": {"fixture_flag": True},
                "credits": 17, "extra": {"fixture_note": "preserve"},
            },
            "fixture-b": {
                "name": "Other Fixture", "current_room": "neptune_lounge",
                "bag": {"fixture_other": 2}, "flags": {},
            },
        }
        save_json(str(self.path), self.original)
        self.reload()
        self.ctx = CaptureContext()

    def reload(self):
        self.storage = JsonFixtureStorage(self.path)
        self.cog = WardrobeCog(SimpleNamespace(storage=self.storage))

    def disk(self):
        return json.loads(self.path.read_text())

    async def search(self):
        await WardrobeCog.search_pod.callback(self.cog, self.ctx, target="panel")

    async def offer(self):
        await WardrobeCog.offer_item.callback(self.cog, self.ctx, target="token")

    def relocate_fixture(self):
        # Validated room path, NOT a test of NavigationCog, gating or entry events.
        room_path = Path(__file__).resolve().parents[1] / "data/rooms/rooms.json"
        rooms = json.loads(room_path.read_text())
        expected = ["hostel_hallway", "hostel_stairwell", "neptune_lounge"]
        for direction, destination in zip(["west", "down", "down"], expected):
            character = self.storage.characters["fixture-a"]
            self.assertEqual(rooms[character["current_room"]]["exits"][direction],
                             destination)
            character["current_room"] = destination
            self.storage.save_characters()
            self.reload()

    async def test_command_loop_survives_reload_and_prevents_replay(self):
        await self.search()
        found = self.disk()
        self.assertEqual(found["fixture-a"]["bag"][TOKEN], 1)
        self.assertTrue(found["fixture-a"]["extra"]["arrival"]["brass_token_found"])
        self.assertIn("Unmarked Brass Token", self.ctx.messages[-1])
        self.assertEqual(found["fixture-b"], self.original["fixture-b"])
        self.assertEqual(found["fixture-a"]["credits"], 17)
        self.assertEqual(found["fixture-a"]["bag"]["fixture_keepsake"], 1)
        self.reload()
        before = deepcopy(self.disk())
        await self.search()
        self.assertEqual(self.disk(), before)
        self.assertEqual(self.storage.characters, before)
        self.assertIn("already searched", self.ctx.messages[-1])
        self.relocate_fixture()
        await self.offer()
        exchanged = self.disk()
        self.assertNotIn(TOKEN, exchanged["fixture-a"]["bag"])
        self.assertTrue(exchanged["fixture-a"]["extra"]["arrival"]["brass_token_exchanged"])
        self.assertTrue(exchanged["fixture-a"]["flags"]["counterkeeper_token_received"])
        self.assertTrue(exchanged["fixture-a"]["flags"]["fixture_flag"])
        self.assertEqual(exchanged["fixture-a"]["extra"]["fixture_note"], "preserve")
        self.assertEqual(exchanged["fixture-b"], self.original["fixture-b"])
        self.assertIn("exchange is remembered", self.ctx.messages[-1])
        self.reload()
        before = deepcopy(self.disk())
        await self.offer()
        self.assertEqual(self.disk(), before)
        self.assertEqual(self.storage.characters, before)
        self.assertIn("already has your token", self.ctx.messages[-1])

    async def test_discovery_save_failure_rolls_back_and_can_retry(self):
        before = deepcopy(self.disk())
        self.storage.fail_next = True
        await self.search()
        self.assertEqual(self.storage.characters, before)
        self.assertEqual(self.disk(), before)
        self.assertIn("failed to remember", self.ctx.messages[-1])
        self.assertNotIn("You pocket it", self.ctx.messages[-1])
        self.reload()
        await self.search()
        self.assertEqual(self.disk()["fixture-a"]["bag"][TOKEN], 1)

    async def test_exchange_save_failure_preserves_token_for_retry(self):
        await self.search()
        self.relocate_fixture()
        before = deepcopy(self.disk())
        self.storage.fail_next = True
        await self.offer()
        self.assertEqual(self.storage.characters, before)
        self.assertEqual(self.disk(), before)
        self.assertEqual(self.disk()["fixture-a"]["bag"][TOKEN], 1)
        self.assertIn("failed to remember", self.ctx.messages[-1])
        self.assertNotIn("exchange is remembered", self.ctx.messages[-1])
        self.reload()
        await self.offer()
        self.assertNotIn(TOKEN, self.disk()["fixture-a"]["bag"])
        self.assertTrue(self.disk()["fixture-a"]["flags"]["counterkeeper_token_received"])


if __name__ == "__main__":
    unittest.main()
