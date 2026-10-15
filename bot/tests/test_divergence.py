import unittest
from fsbot.events.divergence import divergent_historical_continuations


class DivergenceTests(unittest.TestCase):
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
        return divergent_historical_continuations(self.pattern, self.contexts)

    def test_distinct_historical_continuations(self):
        result = self.result()
        self.assertEqual(result["status"], "divergent_historical_continuations")
        self.assertEqual([g["following_pressure_band"] for g in result["historical_continuation_groups"]], ["medium", "low"])
        self.assertEqual(result["historical_continuation_groups"][0]["historical_evidence"][0]["following_source_observation_event_id"], "o3")

    def test_same_continuation_is_not_divergence(self):
        self.pattern["pressure_bands"][-1] = "medium"
        self.assertEqual(self.result()["status"], "single_historical_continuation")
        self.assertEqual(len(self.result()["historical_continuation_groups"][0]["historical_evidence"]), 2)

    def test_terminal_history_without_following_observation(self):
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

    def test_missing_provenance(self):
        self.pattern["source_observation_event_ids"] = []
        self.assertEqual(self.result()["status"], "insufficient_evidence")

    def test_no_mutation(self):
        before = list(self.pattern["pressure_bands"])
        self.result()
        self.assertEqual(self.pattern["pressure_bands"], before)


if __name__ == "__main__":
    unittest.main()
