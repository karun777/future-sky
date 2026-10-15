import unittest
from fsbot.bar_shop import buy_from_bar, bar_menu, BarError

class BarTests(unittest.TestCase):
    def test_purchase(self):
        character = {"current_room": "neptune_lounge", "bag": {}}
        items = {"Triton Lager": {"name": "Triton Lager"}}
        self.assertIn("20 credits", bar_menu(character, items))
        bought, message = buy_from_bar(character, items, "Triton Lager")
        self.assertEqual(bought["credits"], 15)
        self.assertEqual(bought["bag"]["Triton Lager"], 1)
        self.assertEqual(character["bag"], {})
        self.assertIn("bartender", message)
        bought_again, _ = buy_from_bar(bought, items, "Triton Lager")
        self.assertEqual(bought_again["credits"], 10)
        self.assertEqual(bought_again["bag"]["Triton Lager"], 2)

    def test_restrictions(self):
        items = {"Triton Lager": {"name": "Triton Lager"}}
        for character, item in [({"current_room": "other", "bag": {}}, "Triton Lager"), ({"current_room": "neptune_lounge", "bag": {}, "credits": 0}, "Triton Lager"), ({"current_room": "neptune_lounge", "bag": {}}, "Tiny Book")]:
            with self.assertRaises(BarError):
                buy_from_bar(character, items, item)
