import unittest
from fsbot.rumours import witness_drinking, local_rumours


class RumourTests(unittest.TestCase):
    def test_witness_and_claim(self):
        original = {"name": "Efiishent", "current_room": "neptune_lounge"}
        changed, message = witness_drinking(original, 3)
        self.assertIn("whisper", message)
        self.assertEqual(len(local_rumours(changed)), 1)
        self.assertEqual(local_rumours(original), [])
        self.assertEqual(local_rumours(changed)[0]["status"], "unverified")

    def test_no_duplicate(self):
        c, _ = witness_drinking({"current_room": "neptune_lounge"}, 3)
        c2, message = witness_drinking(c, 4)
        self.assertIsNone(message)
        self.assertEqual(len(local_rumours(c2)), 1)

    def test_not_elsewhere_or_sober(self):
        for room, level in [("neptune_lounge", 2), ("pod_room", 3)]:
            c = {"current_room": room}
            changed, message = witness_drinking(c, level)
            self.assertIsNone(message)
            self.assertEqual(changed, c)
