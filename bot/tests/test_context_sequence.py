import unittest
from fsbot.events.context_relevance import relevance_for_context_sequence


class ContextSequenceTests(unittest.TestCase):
    def setUp(self):
        self.pattern = {
            "pattern_type": "comet_pressure_sequence",
            "pressure_bands": ["low", "medium", "high", "low"],
            "source_observation_event_ids": ["o1", "o2", "o3", "o4"],
        }
        self.events = [
            {"event_type": "world_moment.context", "event_id": f"c{i}",
             "payload": {"moment_world_time_seconds": i * 100, "comet": {"pressure_band": band}}}
            for i, band in enumerate(["medium", "high", "low"], start=1)
        ]

    def result(self):
        return relevance_for_context_sequence(self.pattern, self.events)

    def test_matching_three_context_suffix(self):
        result = self.result()
        self.assertEqual(result["status"], "applicable")
        self.assertEqual(result["context_event_ids"], ["c1", "c2", "c3"])
        self.assertEqual(result["source_observation_event_ids"], ["o1", "o2", "o3", "o4"])

    def test_mismatch(self):
        self.events[-1]["payload"]["comet"]["pressure_band"] = "medium"
        self.assertEqual(self.result()["status"], "not_applicable")

    def test_insufficient_pattern_length(self):
        self.pattern["pressure_bands"] = ["high", "low"]
        self.pattern["source_observation_event_ids"] = ["o3", "o4"]
        self.assertEqual(self.result()["status"], "insufficient_evidence")

    def test_two_contexts_not_a_sequence(self):
        self.events.pop()
        self.assertEqual(self.result()["status"], "insufficient_evidence")

    def test_reversed_time(self):
        self.events[-1]["payload"]["moment_world_time_seconds"] = 50
        self.assertEqual(self.result()["status"], "insufficient_evidence")

    def test_duplicate_event_identity(self):
        self.events[-1]["event_id"] = "c1"
        self.assertEqual(self.result()["status"], "insufficient_evidence")

    def test_missing_provenance(self):
        self.pattern["source_observation_event_ids"] = []
        self.assertEqual(self.result()["status"], "insufficient_evidence")

    def test_wrong_event_type(self):
        self.events[0]["event_type"] = "observation.comet_state"
        self.assertEqual(self.result()["status"], "insufficient_evidence")


if __name__ == "__main__":
    unittest.main()
