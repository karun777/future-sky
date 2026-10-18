"""Actual command callbacks and production JSON writer, exclusively in temporary fixtures."""
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
import json
import unittest

from fsbot.cogs.core import CoreCog
from fsbot.cogs.inspection import InspectionCog
from fsbot.cogs.navigation import NavigationCog
from fsbot.cogs.router import _should_route_ctx
from fsbot.cogs.wardrobe import WardrobeCog
from fsbot.pod_opening import opening_state
from fsbot.storage import save_json


class Capture:
    def __init__(self, uid="fictional-arrival"):
        self.author = SimpleNamespace(id=uid, display_name="Fictional Arrival")
        self.channel = SimpleNamespace(id=500, name="fictional-run")
        self.message = SimpleNamespace(id=900)
        self.messages = []

    async def send(self, content=None, **kwargs):
        self.messages.append({"content": content, **kwargs})

    def text(self):
        return "\n".join(str(m.get("content") or "") + (
            (m["embed"].title or "") + "\n" + (m["embed"].description or "") + "\n"
            + "\n".join(f.value for f in m["embed"].fields) if "embed" in m else "")
            for m in self.messages)


class FixtureStorage:
    def __init__(self, path):
        self.path = path
        self.characters = json.loads(path.read_text())
        root = Path(__file__).resolve().parents[1]
        self.items_db = json.loads((root / "data/items/items.json").read_text())
        self.rooms = json.loads((root / "data/rooms/rooms.json").read_text())
        self.lockers = {}
        self.efi_vault = {}
        self.fail_next = False
        self.save_calls = 0

    def save_characters(self):
        self.save_calls += 1
        if self.fail_next:
            self.fail_next = False
            raise OSError("injected pre-write fixture failure")
        save_json(str(self.path), self.characters)

    def save_lockers(self):
        pass

    def save_efi_vault(self):
        pass

    def save_cubes(self):
        pass


class PodOpeningTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.temp = TemporaryDirectory(prefix="pod-opening-fixture-")
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "characters.json"
        self.other = {"id": "other", "name": "Other Fictional Person",
                      "current_room": "neptune_lounge", "bag": {"keepsake": 1},
                      "extra": {"private_fixture_note": "keep"}}
        save_json(str(self.path), {"other": self.other})
        self.ctx = Capture()
        self.reload()

    def reload(self):
        self.storage = FixtureStorage(self.path)
        self.bot = SimpleNamespace(storage=self.storage)
        self.bot.state = SimpleNamespace(ensure_player_records=lambda uid: None,
            resolve_room_for_user=lambda uid: self.storage.characters[uid]["current_room"])
        self.bot.presence = SimpleNamespace(get_players_in_room=lambda room, exclude_user_id=None: [])
        self.inspection = InspectionCog(self.bot)
        self.wardrobe = WardrobeCog(self.bot)
        self.core = CoreCog(self.bot)
        self.bot.get_cog = lambda name: self.inspection if name == "InspectionCog" else None

    def disk(self):
        return json.loads(self.path.read_text())

    async def create(self):
        with patch("fsbot.cogs.core.ensure_player_run_channel", new=AsyncMock(
                return_value=SimpleNamespace(id=500, mention="#fictional-run"))), \
             patch("fsbot.cogs.core.ASTRO_OK", False), \
             patch.object(self.core, "_is_dpc", return_value=False):
            await CoreCog.create_character.callback(
                self.core, self.ctx, "Fictional Arrival", "2000-01-01", "dreamer_technician")
        self.assertEqual(self.storage.characters[str(self.ctx.author.id)]["current_room"], "pod_room")

    async def awaken(self):
        await InspectionCog.awaken.callback(self.inspection, self.ctx)

    async def inspect(self, target):
        await InspectionCog.inspect.callback(self.inspection, self.ctx, item=target)

    def character(self):
        return self.storage.characters[str(self.ctx.author.id)]

    async def test_fresh_creation_hands_discovery_feed_wardrobe_booking_reload(self):
        await self.create()
        self.assertIn("!awaken", self.ctx.text())
        self.assertNotIn("stumble through", self.ctx.text())
        await self.awaken()
        self.assertIn("You do not recognise them", self.ctx.text())
        for target in ["my hands", "garment", "pod", "panels", "display"]:
            await self.inspect(target)
            self.reload()
        self.assertIn("!feed7", self.ctx.text())
        await CoreCog.feed7.callback(self.core, self.ctx)
        self.assertIn("https://future-sky.net/feed7.html", self.ctx.text())
        await self.inspect("wardrobe")
        await WardrobeCog.wardrobe.callback(self.wardrobe, self.ctx)
        self.assertIn("!uniform utility", self.ctx.text())
        await self.inspect("booking")
        self.reload()
        state = opening_state(self.character())
        self.assertIn("booking", state["discoveries"])
        self.assertIn("PERFORMANCE BOOKING", self.ctx.text())
        self.assertIn("TOMORROW NIGHT", self.ctx.text())
        self.assertEqual(self.disk()["other"], self.other)
        before = deepcopy(self.disk())
        await self.awaken()
        self.assertEqual(self.disk(), before)
        self.assertIn("gig tomorrow night", self.ctx.text())

    async def test_clothing_inspection_reflects_persisted_uniform(self):
        await self.create()
        await self.awaken()
        await WardrobeCog.uniform.callback(self.wardrobe, self.ctx, choice="formal")
        self.reload()
        equipped = self.character()["equipped"]["chest"]
        self.ctx.messages.clear()
        await self.inspect("garment")
        self.assertIn(self.storage.items_db[equipped]["name"], self.ctx.text())
        self.assertEqual(self.disk()[str(self.ctx.author.id)]["equipped"]["chest"], equipped)

    async def test_booking_is_discovered_not_guessed(self):
        await self.create()
        await self.awaken()
        before = deepcopy(self.disk())
        await self.inspect("booking")
        self.assertEqual(self.disk(), before)
        self.assertNotIn("booking", opening_state(self.character())["discoveries"])
        self.assertIn("not located", self.ctx.text())

    async def test_inspection_failure_rolls_back_and_retries_without_success(self):
        await self.create()
        await self.awaken()
        await self.inspect("display")
        before = deepcopy(self.disk())
        self.ctx.messages.clear()
        self.storage.fail_next = True
        await self.inspect("booking")
        self.assertEqual(self.disk(), before)
        self.assertEqual(self.storage.characters, before)
        self.assertNotIn("TOMORROW NIGHT", self.ctx.text())
        self.assertIn("could not remember", self.ctx.text())
        await self.inspect("booking")
        self.reload()
        self.assertIn("booking", opening_state(self.character())["discoveries"])

    async def test_start_failure_does_not_publish_opening(self):
        await self.create()
        before = deepcopy(self.disk())
        self.ctx.messages.clear()
        self.storage.fail_next = True
        await self.awaken()
        self.assertEqual(self.disk(), before)
        self.assertIsNone(opening_state(self.character()))
        self.assertNotIn("WHOSE HANDS", self.ctx.text())

    async def test_repeated_observation_is_non_mutating_and_preserves_unrelated_state(self):
        await self.create()
        self.character()["extra"]["earlier_fixture"] = {"remember": True}
        self.character()["credits"] = 31
        self.storage.save_characters()
        await self.awaken()
        await self.inspect("hands")
        before = deepcopy(self.disk())
        count = self.storage.save_calls
        await self.inspect("hands")
        self.assertEqual(self.storage.save_calls, count)
        self.assertEqual(self.disk(), before)
        self.assertEqual(self.character()["extra"]["earlier_fixture"], {"remember": True})
        self.assertEqual(self.character()["credits"], 31)

    async def test_other_room_or_cube_does_not_start_or_mutate(self):
        await self.create()
        for room, cube in [("neptune_lounge", False), ("pod_room", True)]:
            self.character()["current_room"] = room
            self.character()["in_cube"] = cube
            self.storage.save_characters()
            before = deepcopy(self.disk())
            await self.awaken()
            self.assertEqual(self.disk(), before)
            self.assertIsNone(opening_state(self.character()))

    async def test_no_character_is_created_by_awaken(self):
        await self.awaken()
        self.assertNotIn(str(self.ctx.author.id), self.disk())
        self.assertIn("Create a character first", self.ctx.text())

    async def test_existing_thread_node_is_not_replaced(self):
        await self.create()
        self.character()["extra"]["thread_nodes"]["active_thread_node"] = "existing-fixture-node"
        self.storage.save_characters()
        before = deepcopy(self.disk())
        await self.awaken()
        self.assertEqual(self.disk(), before)
        self.assertIsNone(opening_state(self.character()))
        self.assertIn("moment is already open", self.ctx.text())

    async def test_look_resumes_without_reawakening_or_rewriting(self):
        await self.create()
        await self.awaken()
        await self.inspect("display")
        await self.inspect("booking")
        self.reload()
        self.ctx.messages.clear()
        before = deepcopy(self.disk())
        navigation = NavigationCog(self.bot)
        await NavigationCog.look.callback(navigation, self.ctx)
        self.assertIn("You are in the pod", self.ctx.text())
        self.assertIn("gig tomorrow night", self.ctx.text())
        self.assertNotIn("You lift your hands", self.ctx.text())
        self.assertEqual(self.disk(), before)

    async def test_scene_aliases_and_item_inspection_coexist(self):
        await self.create()
        await self.awaken()
        for target in ["my hands", "breathing", "clothes", "neck", "room", "window",
                       "mirror", "hatch", "red light", "red button", "leaflet", "storage", "screen", "bed"]:
            self.ctx.messages.clear()
            await self.inspect(target)
            self.assertIn("embed", self.ctx.messages[-1])
        self.character()["bag"]["itm_i_have_no_compass"] = 1
        self.storage.save_characters()
        before = deepcopy(self.disk())
        await self.inspect("I Have No Compass")
        self.assertEqual(self.disk(), before)
        self.assertEqual(self.ctx.messages[-1]["embed"].title, "I Have No Compass")

    async def test_inspection_does_not_press_button_or_acquire_neck_objects(self):
        await self.create()
        await self.awaken()
        bag = deepcopy(self.character()["bag"])
        await self.inspect("button")
        await self.inspect("chain")
        self.assertEqual(self.character()["bag"], bag)
        self.assertNotIn("pressed_red_button", self.character()["flags"])

    def test_exposed_commands_are_routed(self):
        for name in ["create_character", "awaken", "inspect", "feed7", "wardrobe",
                     "uniform", "fit", "search", "look"]:
            ctx = SimpleNamespace(command=SimpleNamespace(qualified_name=name, name=name))
            self.assertTrue(_should_route_ctx(ctx), name)


if __name__ == "__main__":
    unittest.main()
