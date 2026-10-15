import unittest
from fsbot.events.recurrence import find_comet_pressure_recurrences


class RecurrenceTests(unittest.TestCase):
    def setUp(self):
        self.pattern = {
            "pattern_type": "comet_pressure_sequence",
            "pressure_bands": ["low", "high", "low", "high", "medium"],
            "source_observation_event_ids": ["o1", "o2", "o3", "o4", "o5"],
        }

    def check(self, bands):
        return find_comet_pressure_recurrences(self.pattern, pressure_bands=bands)

    def test_two_nonoverlapping_occurrences(self):
        result = self.check(["low", "high"])
        self.assertEqual(result["status"], "recurring")
        self.assertEqual([o["start_index"] for o in result["occurrences"]], [0, 2])
        self.assertEqual(result["occurrences"][1]["source_observation_event_ids"], ["o3", "o4"])

    def test_once(self):
        self.assertEqual(self.check(["high", "medium"])["status"], "observed_once")

    def test_absent(self):
        self.assertEqual(self.check(["medium", "low"])["status"], "not_observed")

    def test_no_overlap_double_count(self):
        self.pattern["pressure_bands"] = ["low"] * 3
        self.pattern["source_observation_event_ids"] = ["o1", "o2", "o3"]
        self.assertEqual(self.check(["low", "low"])["status"], "observed_once")

    def test_missing_provenance(self):
        self.pattern["source_observation_event_ids"] = []
        self.assertEqual(self.check(["low", "high"])["status"], "insufficient_evidence")

    def test_duplicate_source_ids(self):
        self.pattern["source_observation_event_ids"][2] = "o1"
        self.assertEqual(self.check(["low", "high"])["status"], "insufficient_evidence")

    def test_query_needs_transition(self):
        self.assertEqual(self.check(["low"])["status"], "insufficient_evidence")

    def test_no_mutation(self):
        original = list(self.pattern["pressure_bands"])
        self.check(["low", "high"])
        self.assertEqual(self.pattern["pressure_bands"], original)


if __name__ == "__main__":
    unittest.main()
