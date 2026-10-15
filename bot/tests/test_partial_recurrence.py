import unittest
from fsbot.events.partial_recurrence import historical_continuations_for_present_context


class PartialRecurrenceTests(unittest.TestCase):
    def setUp(self):
        self.pattern = {
            "pattern_type": "comet_pressure_sequence",
            "pressure_bands": ["low", "high", "medium", "low", "high", "low"],
            "source_observation_event_ids": [f"o{i}" for i in range(1, 7)],
        }
        self.contexts = [
            {"event_type": "world_moment.context", "event_id": f"c{i}",
             "payload": {"moment_world_time_seconds": i * 100,
                         "comet": {"pressure_band": band}}}
            for i, band in enumerate(["low", "high"], 1)
        ]

    def result(self):
        return historical_continuations_for_present_context(self.pattern, self.contexts)

    def test_multiple_historical_continuations(self):
        result = self.result()
        self.assertEqual(result["status"], "historical_continuations_observed")
        self.assertEqual([c["following_pressure_band"] for c in result["historical_continuations"]], ["medium", "low"])
        self.assertEqual([c["following_source_observation_event_id"] for c in result["historical_continuations"]], ["o3", "o6"])

    def test_terminal_match_is_not_predicted(self):
        self.pattern["pressure_bands"] = ["medium", "low", "high"]
        self.pattern["source_observation_event_ids"] = ["o1", "o2", "o3"]
        self.assertEqual(self.result()["status"], "no_observed_continuation")

    def test_no_match(self):
        self.contexts[0]["payload"]["comet"]["pressure_band"] = "medium"
        self.contexts[1]["payload"]["comet"]["pressure_band"] = "medium"
        self.assertEqual(self.result()["status"], "no_observed_continuation")

    def test_invalid_chronology(self):
        self.contexts[1]["payload"]["moment_world_time_seconds"] = 50
        self.assertEqual(self.result()["status"], "insufficient_evidence")

    def test_duplicate_context(self):
        self.contexts[1]["event_id"] = "c1"
        self.assertEqual(self.result()["status"], "insufficient_evidence")

    def test_missing_provenance(self):
        self.pattern["source_observation_event_ids"] = []
        self.assertEqual(self.result()["status"], "insufficient_evidence")

    def test_no_mutation(self):
        before = list(self.pattern["pressure_bands"])
        self.result()
        self.assertEqual(self.pattern["pressure_bands"], before)


if __name__ == "__main__":
    unittest.main()
