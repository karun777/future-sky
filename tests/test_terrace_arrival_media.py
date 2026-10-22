"""Capsule arrival art and read-only memory, actual callbacks on fixtures."""
import hashlib
import json
from pathlib import Path
import unittest
import test_terrace_delivery as terrace_fixture
from fsbot.terrace_delivery import KEY, state_of
from fsbot.terrace_media import ASSET_ROOT, ARRIVAL_URL, BOX_URL

class ArrivalMediaTests(unittest.IsolatedAsyncioTestCase):
    setUp = terrace_fixture.TerraceDeliveryTests.setUp
    reload = terrace_fixture.TerraceDeliveryTests.reload
    char = terrace_fixture.TerraceDeliveryTests.char
    performer = terrace_fixture.TerraceDeliveryTests.performer
    action = terrace_fixture.TerraceDeliveryTests.action
    sequence = terrace_fixture.TerraceDeliveryTests.sequence

    def test_exact_approved_asset(self):
        root = Path(__file__).resolve().parents[1] / ASSET_ROOT
        meta = json.loads((root / "manifest.json").read_text())
        data = (root / meta["file"]).read_bytes()
        self.assertEqual(meta["generation"], "exec-1140a863-af07-4778-906f-8687adc7b71a.png")
        self.assertEqual(hashlib.sha256(data).hexdigest(), meta["sha256"])
        self.assertEqual(len(data), meta["bytes"])
        self.assertEqual(data[8:12], b"WEBP")

    async def test_attend_quiet_first_arrival_illustrated_repeat_quiet(self):
        self.performer()
        await self.action("attend")
        self.assertFalse(self.ctx.messages[-1]["embed"].image.url)
        await self.action("sky")
        self.assertEqual(self.ctx.messages[-1]["embed"].image.url, ARRIVAL_URL)
        self.assertIn("straight course", self.ctx.text())
        self.assertIn("small capsule", self.ctx.text())
        self.reload()
        before = self.path.read_bytes()
        await self.action("sky")
        self.assertFalse(self.ctx.messages[-1]["embed"].image.url)
        self.assertEqual(self.path.read_bytes(), before)

    async def test_memory_unavailable_until_witnessed_then_no_state_write(self):
        self.performer()
        before = self.path.read_bytes()
        await self.action("arrival")
        self.assertIn("No arrival", self.ctx.text())
        self.assertEqual(self.path.read_bytes(), before)
        await self.sequence(("attend", "sky"))
        self.reload()
        before = self.path.read_bytes()
        await self.action("arrival")
        self.assertIn("remembered", self.ctx.text())
        self.assertEqual(self.ctx.messages[-1]["embed"].image.url, ARRIVAL_URL)
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(len(state_of(self.char())["objects"]), 1)

    async def test_capsule_aliases_preserve_old_instance_and_no_contents_leak(self):
        self.performer()
        await self.sequence(("attend", "sky"))
        await self.action("inspect capsule")
        self.assertNotIn("antique", self.ctx.text())
        package_id = state_of(self.char())["objects"]["package"]["instance_id"]
        await self.action("take capsule")
        await self.action("open capsule")
        self.assertIn("antique locked box", self.ctx.text())
        self.assertEqual(state_of(self.char())["objects"]["package"]["instance_id"], package_id)
        self.assertIn("usb", state_of(self.char())["objects"])
        self.assertEqual(self.ctx.messages[-1]["embed"].image.url, BOX_URL)
        self.assertEqual(state_of(self.char())["stage"], "open")

    async def test_combined_reveal_is_atomic_and_legacy_open_capsule_can_continue(self):
        self.performer()
        await self.sequence(("attend", "sky", "take capsule"))
        before = self.path.read_bytes()
        self.storage.fail_next = True
        await self.action("open capsule")
        self.assertEqual(self.path.read_bytes(), before)
        self.assertNotIn("embed", self.ctx.messages[-1])
        await self.action("open capsule")
        self.assertEqual(self.ctx.messages[-1]["embed"].image.url, BOX_URL)
        state = state_of(self.char())
        self.assertEqual(state["objects"]["usb"]["temporal_validity"], "provisional")
        # Previously deployed intermediate state uses the same generic transition.
        state["stage"] = "unwrapped"
        state["objects"].pop("usb")
        state["discoveries"] = [d for d in state["discoveries"] if not d.startswith(("box.", "usb."))]
        self.storage.save_characters()
        await self.action("open capsule")
        self.assertEqual(state_of(self.char())["stage"], "open")
        await self.action("take tunes")
        identity = state_of(self.char())["objects"]["usb"]["instance_id"]
        before = self.path.read_bytes()
        await self.sequence(("open capsule", "take tunes"))
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(state_of(self.char())["objects"]["usb"]["instance_id"], identity)

    async def test_unsaved_arrival_cannot_show_its_image(self):
        self.performer()
        await self.action("attend")
        before = self.path.read_bytes()
        self.storage.fail_next = True
        await self.action("sky")
        self.assertNotIn("embed", self.ctx.messages[-1])
        self.assertEqual(self.path.read_bytes(), before)
        await self.action("sky")
        self.assertEqual(self.ctx.messages[-1]["embed"].image.url, ARRIVAL_URL)

if __name__ == "__main__":
    unittest.main()
