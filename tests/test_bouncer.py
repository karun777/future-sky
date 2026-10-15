import unittest
from fsbot.bouncer import resolve_bouncer, BouncerError
from fsbot.lounge_freebies import record_free_take


class BouncerTests(unittest.TestCase):
    def setUp(self):
        self.character = {"current_room": "neptune_lounge", "credits": 10,
                          "social_counters": {"neptune_free_lagers_taken": 3}}

    def test_existing_scavenger_can_apologise(self):
        updated, message = resolve_bouncer(self.character, "apologise")
        self.assertIn("steps aside", message)
        self.assertTrue(updated["social_flags"]["neptune_bouncer_resolved"])
        self.assertNotIn("social_flags", self.character)

    def test_buy_round_deducts(self):
        updated, _ = resolve_bouncer(self.character, "buy")
        self.assertEqual(updated["credits"], 5)

    def test_cannot_buy_without_credits(self):
        with self.assertRaises(BouncerError):
            resolve_bouncer({**self.character, "credits": 0}, "buy")

    def test_no_repeat_resolution(self):
        updated, _ = resolve_bouncer(self.character, "charm")
        with self.assertRaises(BouncerError):
            resolve_bouncer(updated, "bluff")

    def test_third_pickup_triggers(self):
        character = {"current_room": "neptune_lounge"}
        for index in range(3):
            character, message = record_free_take(character, "neptune_lounge", "Triton Lager")
        self.assertTrue(character["social_flags"]["neptune_bouncer_pending"])
        self.assertIn("bouncer", message)
