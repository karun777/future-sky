import unittest
from fsbot.item_usage import use_item, ItemUseError


class ItemUseTests(unittest.TestCase):
    def setUp(self):
        self.ch = {"bag": {"Triton Lager": 2, "itm_tiny_book": 1},
                   "pools": {"hp": {"current": 7, "max": 10}}}
        self.items = {
            "Triton Lager": {"name": "Triton Lager", "use_action": {"kind": "heal", "amount": 4, "consume": True}},
            "itm_tiny_book": {"name": "Tiny Book", "use_action": {"kind": "read", "text": "The pages rustle."}},
        }

    def test_heal_and_consume(self):
        ch, message, consumed = use_item(self.ch, self.items, "triton lager")
        self.assertEqual(ch["pools"]["hp"]["current"], 10)
        self.assertEqual(ch["bag"]["Triton Lager"], 1)
        self.assertTrue(consumed)
        self.assertEqual(self.ch["pools"]["hp"]["current"], 7)

    def test_no_waste_at_full_hp(self):
        self.ch["pools"]["hp"]["current"] = 10
        with self.assertRaises(ItemUseError):
            use_item(self.ch, self.items, "Triton Lager")
        self.assertEqual(self.ch["bag"]["Triton Lager"], 2)

    def test_read_does_not_consume(self):
        ch, message, consumed = use_item(self.ch, self.items, "Tiny Book")
        self.assertEqual(message, "The pages rustle.")
        self.assertEqual(ch["bag"]["itm_tiny_book"], 1)
        self.assertFalse(consumed)

    def test_legacy_stats_hp_preserves_elemental_pools(self):
        self.ch.pop("pools")
        self.ch["stats"] = {"hp": 7, "max_hp": 10}
        self.ch["pools"] = {"earth": {"current": 2, "max": 5}}
        updated, message, consumed = use_item(self.ch, self.items, "Triton Lager")
        self.assertEqual(updated["stats"]["hp"], 10)
        self.assertEqual(updated["pools"], self.ch["pools"])
        self.assertEqual(updated["bag"]["Triton Lager"], 1)
        self.assertTrue(consumed)

    def test_legacy_full_health_does_not_consume(self):
        self.ch["pools"] = {"earth": {"current": 0, "max": 0}}
        self.ch["stats"] = {"hp": 10, "max_hp": 10}
        with self.assertRaisesRegex(ItemUseError, "full health"):
            use_item(self.ch, self.items, "Triton Lager")
        self.assertEqual(self.ch["bag"]["Triton Lager"], 2)

    def test_missing_item(self):
        with self.assertRaises(ItemUseError):
            use_item(self.ch, self.items, "Rusty Knife")

    def test_no_invented_mechanics(self):
        self.items["itm_tiny_book"].pop("use_action")
        with self.assertRaises(ItemUseError):
            use_item(self.ch, self.items, "Tiny Book")


if __name__ == "__main__":
    unittest.main()
