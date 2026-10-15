import unittest
from fsbot.bar_work import work_bar, WorkError


class BarWorkTests(unittest.TestCase):
    def test_earn_and_cooldown(self):
        original = {"current_room": "neptune_lounge", "credits": 0}
        changed, message = work_bar(original, now=1000)
        self.assertEqual(changed["credits"], 5)
        self.assertEqual(original["credits"], 0)
        self.assertEqual(changed["work"]["bar_shifts_completed"], 1)
        with self.assertRaises(WorkError):
            work_bar(changed, now=1299)
        again, _ = work_bar(changed, now=1300)
        self.assertEqual(again["credits"], 10)

    def test_not_in_lounge(self):
        with self.assertRaises(WorkError):
            work_bar({"current_room": "pod_room"}, now=1000)

    def test_too_intoxicated(self):
        with self.assertRaises(WorkError):
            work_bar({"current_room": "neptune_lounge", "intoxication": {"level": 3, "updated_at": 1000}}, now=1000)
        updated, _ = work_bar({"current_room": "neptune_lounge", "intoxication": {"level": 3, "updated_at": 1000}}, now=1900)
        self.assertEqual(updated["credits"], 25)
