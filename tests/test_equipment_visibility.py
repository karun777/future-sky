import unittest
from fsbot.utils import fmt_equipped, EQUIP_SLOTS


class EquipmentVisibilityTests(unittest.TestCase):
    def test_chest_and_hand_visible(self):
        rendered = fmt_equipped({"chest": "Freeform Attire", "main_hand": "Rusty Knife"})
        self.assertIn("chest: Freeform Attire", rendered)
        self.assertIn("main_hand: Rusty Knife", rendered)

    def test_canonical_slots(self):
        self.assertIn("chest", EQUIP_SLOTS)
        self.assertIn("ring_1", EQUIP_SLOTS)
        self.assertNotIn("body", EQUIP_SLOTS)


if __name__ == "__main__":
    unittest.main()
