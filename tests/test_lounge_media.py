"""Approved assets and real render callbacks, fictional records only."""
from pathlib import Path
from copy import deepcopy
import hashlib
import json
import unittest
from unittest.mock import AsyncMock
import test_display
from fsbot.lounge_media import ASSET_ROOT, ROOM_IMAGES, lounge_image

class LoungeMediaTests(unittest.IsolatedAsyncioTestCase):
    setUp = test_display.DisplayTests.setUp
    reload = test_display.DisplayTests.reload
    char = test_display.DisplayTests.char
    look = test_display.DisplayTests.look
    inspect = test_display.DisplayTests.inspect

    def rooms(self):
        root = Path(__file__).resolve().parents[1]
        self.storage.rooms = json.loads((root / "data/rooms/rooms.json").read_text())
        self.bot.state.play_music = AsyncMock()

    def test_assets_match_manifest(self):
        root = Path(__file__).resolve().parents[1] / ASSET_ROOT
        manifest = json.loads((root / "manifest.json").read_text())
        self.assertEqual(set(manifest), set(ROOM_IMAGES.values()) | {"counterkeeper.webp"})
        for filename, record in manifest.items():
            data = (root / filename).read_bytes()
            self.assertEqual(len(data), record["bytes"])
            self.assertEqual(hashlib.sha256(data).hexdigest(), record["sha256"])
            self.assertEqual(data[:4], b"RIFF")
            self.assertEqual(data[8:12], b"WEBP")

    async def test_room_callbacks_bind_three_images_without_state_writes(self):
        self.rooms()
        for room in ROOM_IMAGES:
            self.char()["current_room"] = room
            self.storage.save_characters()
            before = self.path.read_text()
            rooms = deepcopy(self.storage.rooms)
            await self.look()
            self.assertEqual(self.ctx.messages[0]["embed"].image.url, lounge_image(self.char()))
            self.assertEqual(self.path.read_text(), before)
            self.assertEqual(self.storage.rooms, rooms)

    async def test_counterkeeper_image_before_and_after_exchange(self):
        self.rooms()
        self.char()["current_room"] = "neptune_lounge"
        for exchanged in (False, True):
            self.char()["extra"]["arrival"] = {"brass_token_exchanged": exchanged}
            self.storage.save_characters()
            before = self.path.read_text()
            await self.inspect("counterkeeper")
            self.assertEqual(self.ctx.messages[-1]["embed"].image.url, lounge_image(self.char(), "counterkeeper"))
            self.assertEqual(self.path.read_text(), before)

    async def test_main_floor_preserves_existing_art(self):
        self.rooms()
        self.char()["current_room"] = "lounge_main_floor"
        expected = self.storage.rooms["lounge_main_floor"]["image"]
        await self.look()
        self.assertEqual(self.ctx.messages[0]["embed"].image.url, expected)
        self.assertIsNone(lounge_image(self.char()))

    def test_no_portrait_elsewhere_or_in_cube(self):
        for room in ["pod_room", "hostel_hallway", "lounge_main_floor"]:
            self.assertIsNone(lounge_image({"current_room": room}, "counterkeeper"))
        for target in ["room", "counterkeeper"]:
            self.assertIsNone(lounge_image({"current_room": "neptune_lounge", "in_cube": True}, target))
        self.assertIsNone(lounge_image({"current_room": "neptune_lounge"}, "unknown"))

if __name__ == "__main__":
    unittest.main()
