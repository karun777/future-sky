import unittest
from fsbot.intoxication import drink, status


class IntoxicationTests(unittest.TestCase):
    def test_drinking_accumulates(self):
        character = {}
        for _ in range(3):
            character, feeling = drink(character, now=1000)
        self.assertEqual(status(character, now=1000)[0], 3)
        self.assertIn("sway", feeling)

    def test_decay(self):
        character, _ = drink({}, now=1000)
        self.assertEqual(status(character, now=1899)[0], 1)
        self.assertEqual(status(character, now=1900)[0], 0)

    def test_cap_and_purity(self):
        original = {}
        current = original
        for _ in range(9):
            current, _ = drink(current, now=1000)
        self.assertEqual(status(current, now=1000)[0], 6)
        self.assertEqual(original, {})
