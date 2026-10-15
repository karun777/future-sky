import unittest
from fsbot.events.present_recurrence import recurrence_for_present_context


class PresentRecurrenceTests(unittest.TestCase):
    def setUp(self):
        self.pattern = {
            "pattern_type": "comet_pressure_sequence",
            "pressure_bands": ["low", "high", "medium", "low", "high"],
            "source_observation_event_ids": ["o1", "o2", "o3", "o4", "o5"],
        }
        self.events = [
            {"event_type": "world_moment.context", "event_id": f"c{i}",
             "payload": {"moment_world_time_seconds": i * 100,
                         "comet": {"pressure_band": band}}}
            for i, band in enumerate(["low", "high"], start=1)
        ]

    def result(self):
        return recurrence_for_present_context(self.pattern, self.events)

    def test_present_corresponds_to_repeated_history(self):
        result = self.result()
        self.assertEqual(result["status"], "recurring")
        self.assertEqual(result["context_event_ids"], ["c1", "c2"])
        self.assertEqual([o["start_index"] for o in result["historical_occurrences"]], [0, 3])

    def test_present_observed_once(self):
        self.events[0]["payload"]["comet"]["pressure_band"] = "high"
        self.events[1]["payload"]["comet"]["pressure_band"] = "medium"
        self.assertEqual(self.result()["status"], "observed_once")

    def test_absent(self):
        self.events[0]["payload"]["comet"]["pressure_band"] = "medium"
        self.events[1]["payload"]["comet"]["pressure_band"] = "high"
        self.assertEqual(self.result()["status"], "not_observed")

    def test_out_of_order(self):
        self.events[1]["payload"]["moment_world_time_seconds"] = 50
        self.assertEqual(self.result()["status"], "insufficient_evidence")

    def test_duplicate_context_id(self):
        self.events[1]["event_id"] = "c1"
        self.assertEqual(self.result()["status"], "insufficient_evidence")

    def test_unrelated_event(self):
        self.events[0]["event_type"] = "comet.state_changed"
        self.assertEqual(self.result()["status"], "insufficient_evidence")

    def test_one_context_insufficient(self):
        self.events.pop()
        self.assertEqual(self.result()["status"], "insufficient_evidence")

    def test_missing_historical_provenance(self):
        self.pattern["source_observation_event_ids"] = []
        self.assertEqual(self.result()["status"], "insufficient_evidence")


if __name__ == "__main__":
    unittest.main()
