"""Run from repository root: PYTHONPATH=bot python -m unittest discover -s tests -p test_pod_wardrobe.py"""
import json
import unittest
from pathlib import Path

from fsbot.pod_wardrobe import WardrobeError, current_fit, select_uniform


ROOT = Path(__file__).resolve().parents[1]


class PodWardrobeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalogue = json.loads((ROOT / "data/arrival/pod_uniforms.json").read_text())
        cls.items = json.loads((ROOT / "data/items/items.json").read_text())

    def test_each_uniform_equips_without_mutating_input(self):
        for uniform in self.catalogue["uniforms"]:
            with self.subTest(uniform=uniform["id"]):
                character = {"bag": {}, "equipped": {"chest": None}, "extra": {}}
                result = select_uniform(character, uniform["id"], self.catalogue, self.items)
                self.assertIsNone(character["equipped"]["chest"])
                self.assertEqual(result["equipped"]["chest"], uniform["item_id"])
                self.assertEqual(result["extra"]["arrival"]["pod_uniform_selected"], uniform["id"])
                self.assertEqual(current_fit(result, self.items)["appearance_key"], uniform["id"])

    def test_existing_chest_item_returns_to_bag(self):
        character = {"bag": {}, "equipped": {"chest": "itm_leather_jacket"}, "extra": {}}
        result = select_uniform(character, "pod_utility", self.catalogue, self.items)
        self.assertEqual(result["bag"]["itm_leather_jacket"], 1)

    def test_duplicate_selection_rejected(self):
        result = select_uniform({"bag": {}, "equipped": {}, "extra": {}}, "pod_formal", self.catalogue, self.items)
        with self.assertRaises(WardrobeError):
            select_uniform(result, "pod_utility", self.catalogue, self.items)

    def test_invalid_selection_does_not_mutate(self):
        original = {"bag": {}, "equipped": {"chest": None}, "extra": {}}
        with self.assertRaises(WardrobeError):
            select_uniform(original, "missing", self.catalogue, self.items)
        self.assertEqual(original["extra"], {})


if __name__ == "__main__":
    unittest.main()
