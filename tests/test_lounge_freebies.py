import unittest
from fsbot.lounge_freebies import seed_freebies, record_free_take


class LoungeFreebiesTests(unittest.TestCase):
    def test_seed_three_once(self):
        room = {"items": []}
        seeded, changed = seed_freebies(room)
        self.assertTrue(changed)
        self.assertEqual(seeded["items"], ["Triton Lager"] * 3)
        self.assertEqual(room["items"], [])
        again, changed = seed_freebies(seeded)
        self.assertFalse(changed)
        self.assertEqual(len(again["items"]), 3)

    def test_preserve_existing_stock(self):
        room = {"items": ["Tiny Book", "Triton Lager"]}
        updated, changed = seed_freebies(room)
        self.assertTrue(changed)
        self.assertEqual(updated["items"].count("Triton Lager"), 3)
        self.assertIn("Tiny Book", updated["items"])

    def test_freebie_count_and_flavour(self):
        original = {"bag": {}}
        one, first = record_free_take(original, "neptune_lounge", "Triton Lager")
        two, second = record_free_take(one, "neptune_lounge", "Triton Lager")
        three, third = record_free_take(two, "neptune_lounge", "Triton Lager")
        self.assertEqual(original, {"bag": {}})
        self.assertEqual(three["social_counters"]["neptune_free_lagers_taken"], 3)
        self.assertIn("bartender", second)
        self.assertIn("keeping count", third)

    def test_other_items_and_rooms_do_not_count(self):
        original = {"bag": {}}
        for room, item in [("main_square", "Triton Lager"), ("neptune_lounge", "Tiny Book")]:
            result, message = record_free_take(original, room, item)
            self.assertIsNone(message)
            self.assertNotIn("social_counters", result)


if __name__ == "__main__":
    unittest.main()
