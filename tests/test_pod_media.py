"""Production pod media bindings and actual callbacks, fictional records only."""
from pathlib import Path
from copy import deepcopy
import unittest
import test_display
from fsbot.cogs.inspection import InspectionCog
from fsbot.cogs.navigation import NavigationCog
from fsbot.cogs.wardrobe import WardrobeCog
from fsbot.pod_media import pod_image, BINDINGS, ASSET_ROOT
from fsbot.pod_opening import scene_target, opening_state


class PodMediaTests(unittest.IsolatedAsyncioTestCase):
    setUp = test_display.DisplayTests.setUp
    reload = test_display.DisplayTests.reload
    char = test_display.DisplayTests.char
    start = test_display.DisplayTests.start
    inspect = test_display.DisplayTests.inspect
    look = test_display.DisplayTests.look

    def test_all_bound_files_are_versioned_pngs(self):
        root = Path(__file__).resolve().parents[1]
        for filename in set(BINDINGS.values()):
            data = (root / ASSET_ROOT / filename).read_bytes()
            self.assertTrue(data.startswith(b"\x89PNG\r\n\x1a\n"), filename)
            self.assertGreater(len(data), 10000)

    async def test_room_view_replaces_placeholder_without_room_data_mutation(self):
        before = deepcopy(self.storage.rooms)
        await self.look()
        self.assertEqual(self.ctx.messages[0]["embed"].image.url, pod_image(self.char(), "room"))
        self.assertNotIn("placeholder", self.ctx.messages[0]["embed"].image.url)
        self.assertEqual(self.storage.rooms, before)

    async def test_opening_body_has_no_room_image_until_survey(self):
        await self.start()
        self.assertFalse(self.ctx.messages[-1]["embed"].image.url)
        await self.inspect("hands")
        self.assertFalse(self.ctx.messages[-1]["embed"].image.url)
        await self.inspect("pod")
        self.assertTrue(self.ctx.messages[-1]["embed"].image.url.endswith("p01.png"))

    async def test_target_images_follow_approved_bindings(self):
        await self.start()
        for target, filename in [("panels", "p02.png"), ("light", "p05.png"),
                                 ("button", "p05.png"), ("brochure", "p05.png"),
                                 ("viewport", "p06.png"), ("reflection", "p06.png")]:
            await self.inspect(target)
            self.assertTrue(self.ctx.messages[-1]["embed"].image.url.endswith(filename), target)

    async def test_display_unread_image_disappears_after_booking_and_reload(self):
        await self.start()
        await self.inspect("display")
        self.assertTrue(self.ctx.messages[-1]["embed"].image.url.endswith("p03.png"))
        await self.inspect("booking")
        self.assertFalse(self.ctx.messages[-1]["embed"].image.url)
        self.reload()
        await self.inspect("display")
        self.assertFalse(self.ctx.messages[-1]["embed"].image.url)
        self.assertIn("booking", opening_state(self.char())["discoveries"])

    async def test_wardrobe_remains_text_only_and_does_not_grant_items(self):
        await self.start()
        before = deepcopy(self.char()["bag"])
        await self.inspect("wardrobe")
        self.assertFalse(self.ctx.messages[-1]["embed"].image.url)
        wardrobe = WardrobeCog(self.bot)
        await WardrobeCog.wardrobe.callback(wardrobe, self.ctx)
        self.assertFalse(self.ctx.messages[-1]["embed"].image.url)
        self.assertEqual(self.char()["bag"], before)

    async def test_architecture_and_printed_art_are_inspectable(self):
        await self.start()
        for target in ["floor", "ceiling", "seams", "scuffs", "carpet", "hinges", "frame", "screws",
                       "handle", "drawer", "cabinet", "lower storage", "cover", "bedding", "warm light",
                       "strip light", "brochure picture", "printed landscape"]:
            self.assertIsNotNone(scene_target(target), target)
            await self.inspect(target)
            self.assertIn("embed", self.ctx.messages[-1])
        self.assertIn("promotional artwork", self.ctx.text())

    async def test_failed_observation_never_publishes_image_or_discovery(self):
        await self.start()
        before = self.path.read_text()
        self.storage.fail_next = True
        await self.inspect("panels")
        self.assertNotIn("embed", self.ctx.messages[-1])
        self.assertEqual(self.path.read_text(), before)
        await self.inspect("panels")
        self.assertTrue(self.ctx.messages[-1]["embed"].image.url.endswith("p02.png"))

    async def test_other_room_and_cube_do_not_receive_pod_media(self):
        for room, cube in [("neptune_lounge", False), ("pod_room", True)]:
            character = deepcopy(self.char())
            character.update(current_room=room, in_cube=cube)
            for target in BINDINGS:
                self.assertIsNone(pod_image(character, target))

    async def test_repeated_visual_inspection_preserves_other_character_and_inventory(self):
        await self.start()
        await self.inspect("panels")
        before = deepcopy(self.storage.characters)
        await self.inspect("panels")
        self.assertEqual(self.storage.characters, before)

    async def test_non_pod_look_retains_existing_room_image(self):
        self.char()["current_room"] = "neptune_lounge"
        self.storage.rooms["neptune_lounge"]["image"] = "https://example.test/lounge.png"
        await self.look()
        self.assertEqual(self.ctx.messages[0]["embed"].image.url, "https://example.test/lounge.png")


if __name__ == "__main__":
    unittest.main()
