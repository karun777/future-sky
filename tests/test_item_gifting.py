import unittest
from fsbot.item_gifting import give_item, GiftError


class GiftTests(unittest.TestCase):
    def setUp(self):
        self.a = {"name": "efiishent", "current_room": "neptune_lounge", "bag": {"itm_tiny_book": 1}}
        self.b = {"name": "The Dark Rat Queen", "current_room": "neptune_lounge", "bag": {}}
        self.items = {"itm_tiny_book": {"name": "Tiny Book"}}

    def test_gift_and_discovery(self):
        a, b, name = give_item(self.a, self.b, self.items, "tiny book")
        self.assertEqual(name, "Tiny Book")
        self.assertEqual(a["bag"], {})
        self.assertEqual(b["bag"]["itm_tiny_book"], 1)
        self.assertEqual(a["item_discoveries"]["itm_tiny_book"], ["queen_interest"])
        self.assertEqual(self.a["bag"]["itm_tiny_book"], 1)

    def test_not_present(self):
        self.b["current_room"] = "dark_rat_queen_den"
        with self.assertRaises(GiftError):
            give_item(self.a, self.b, self.items, "tiny book")

    def test_not_owned(self):
        self.a["bag"] = {}
        with self.assertRaises(GiftError):
            give_item(self.a, self.b, self.items, "tiny book")

    def test_transfer_restriction(self):
        self.items["itm_tiny_book"]["transfer_policy"] = "not_transferable"
        with self.assertRaises(GiftError):
            give_item(self.a, self.b, self.items, "tiny book")


if __name__ == "__main__":
    unittest.main()
