"""Capture the existing Compass inspection embed without Discord delivery."""
from copy import deepcopy
import json
from pathlib import Path
from types import SimpleNamespace
import unittest

from fsbot.cogs.inspection import InspectionCog

ITEM_ID = "itm_i_have_no_compass"


class CaptureContext:
    def __init__(self):
        self.author = SimpleNamespace(id="fixture-viewer")
        self.messages = []

    async def send(self, content=None, **kwargs):
        self.messages.append({"content": content, **kwargs})


class InspectionCardTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        catalogue = json.loads((Path(__file__).resolve().parents[1] /
                                "data/items/items.json").read_text())
        self.definition = deepcopy(catalogue[ITEM_ID])
        self.character = {
            "name": "Fixture Viewer", "current_room": "fixture-room",
            "bag": {ITEM_ID: 1}, "equipped": {}, "item_discoveries": {},
        }
        self.storage = SimpleNamespace(
            characters={"fixture-viewer": self.character},
            rooms={"fixture-room": {"items": []}},
            items_db={ITEM_ID: self.definition},
            save_characters=self.unexpected_save,
            save_rooms=self.unexpected_save,
        )
        self.cog = InspectionCog(SimpleNamespace(storage=self.storage))
        self.ctx = CaptureContext()

    def unexpected_save(self):
        self.fail("Inspection must not request a persistence write")

    def snapshot(self):
        return deepcopy({
            "characters": self.storage.characters,
            "rooms": self.storage.rooms,
            "items": self.storage.items_db,
        })

    async def inspect(self):
        before = self.snapshot()
        await InspectionCog.inspect.callback(self.cog, self.ctx,
                                             item="I Have No Compass")
        self.assertEqual(self.snapshot(), before)
        return self.ctx.messages[-1]

    def fields(self, card):
        return {field["name"]: field["value"] for field in card["fields"]}

    async def test_public_card_has_real_copy_and_image_without_secrets(self):
        message = await self.inspect()
        card = message["embed"].to_dict()
        fields = self.fields(card)
        self.assertEqual(card["title"], "I Have No Compass")
        self.assertEqual(card["description"], self.definition["description"])
        self.assertEqual(fields["Type"], "Artifact")
        self.assertEqual(fields["Rarity"], "Unique")
        self.assertIn("Cannot be removed", fields["Known attributes"])
        self.assertIn("Always inside the casing", fields["Known attributes"])
        self.assertEqual(fields["Known uses"], "Attempt to reseat the needle")
        self.assertEqual(card["image"]["url"], self.definition["image"])
        self.assertTrue(card["image"]["url"].startswith("https://"))
        serial = json.dumps(card)
        self.assertNotIn("stasis", serial)
        self.assertNotIn("entrapment", serial)
        self.assertNotIn("seven times", serial)
        self.assertNotIn(self.definition["notes"], serial)
        self.assertNotIn("Repair DC", serial)
        self.assertEqual(self.character["item_discoveries"], {})

    async def test_navigation_discovery_reveals_only_that_knowledge(self):
        self.character["item_discoveries"][ITEM_ID] = ["restored_navigation"]
        first = (await self.inspect())["embed"].to_dict()
        attrs = self.fields(first)["Known attributes"]
        self.assertIn("meaningful direction forward", attrs)
        self.assertIn("seven times daily in the left direction", attrs)
        self.assertNotIn("stasis", json.dumps(first))
        self.assertNotIn("entrapment", json.dumps(first))
        second = (await self.inspect())["embed"].to_dict()
        self.assertEqual(first, second)
        self.assertEqual(self.character["item_discoveries"][ITEM_ID],
                         ["restored_navigation"])

    async def test_both_discoveries_show_authored_attributes_without_mechanics(self):
        self.character["item_discoveries"][ITEM_ID] = [
            "restored_navigation", "temporal_compulsion"]
        card = (await self.inspect())["embed"].to_dict()
        attrs = self.fields(card)["Known attributes"]
        self.assertIn("temporal stasis loop", attrs)
        self.assertIn("Advanced bearer", attrs)
        self.assertIn("left direction", attrs)
        self.assertEqual(self.fields(card)["Known uses"],
                         "Attempt to reseat the needle")
        # Displaying knowledge does not add action/repair/entrapment state.
        self.assertNotIn("temporal_stasis", self.character)
        self.assertNotIn("repair", self.character["flags"]
                         if "flags" in self.character else {})

    async def test_access_is_limited_to_carried_equipped_or_nearby_item(self):
        for visibility in ["bag", "equipped", "ground", "absent"]:
            with self.subTest(visibility=visibility):
                self.character["bag"] = {ITEM_ID: 1} if visibility == "bag" else {}
                self.character["equipped"] = (
                    {"main_hand": ITEM_ID} if visibility == "equipped" else {})
                self.storage.rooms["fixture-room"]["items"] = (
                    [ITEM_ID] if visibility == "ground" else [])
                message = await self.inspect()
                if visibility == "absent":
                    self.assertNotIn("embed", message)
                    self.assertEqual(message["content"],
                                     "You cannot see that item here.")
                else:
                    self.assertEqual(message["embed"].title,
                                     "I Have No Compass")

    async def test_unknown_discovery_key_does_not_grant_hidden_attributes(self):
        self.character["item_discoveries"][ITEM_ID] = ["fixture_unknown_key"]
        card = (await self.inspect())["embed"].to_dict()
        attrs = self.fields(card)["Known attributes"]
        self.assertIn("Always inside the casing", attrs)
        self.assertNotIn("stasis", json.dumps(card))
        self.assertNotIn("seven times", json.dumps(card))


if __name__ == "__main__":
    unittest.main()
