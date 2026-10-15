import unittest
from fsbot.events.reunion import historical_divergence_and_reunion


class ReunionTests(unittest.TestCase):
    def setUp(self):
        self.pattern = {
            "pattern_type": "comet_pressure_sequence",
            "pressure_bands": ["low", "high", "medium", "low", "low", "high", "low", "low"],
            "source_observation_event_ids": [f"o{i}" for i in range(1, 9)],
        }
        self.contexts = [
            {"event_type": "world_moment.context", "event_id": f"c{i}",
             "payload": {"moment_world_time_seconds": i * 100,
                         "comet": {"pressure_band": band}}}
            for i, band in enumerate(["low", "high"], 1)
        ]

    def result(self, steps=2):
        return historical_divergence_and_reunion(self.pattern, self.contexts, steps=steps)

    def test_diverge_then_reunite(self):
        result = self.result()
        self.assertEqual(result["status"], "historical_reunion_observed")
        reunion = result["historical_reunions"][0]
        self.assertEqual(reunion["reunion_offset"], 2)
        self.assertEqual(reunion["reunion_pressure_band"], "low")
        self.assertEqual(reunion["left_reunion_source_observation_event_id"], "o4")
        self.assertEqual(reunion["right_reunion_source_observation_event_id"], "o8")

    def test_diverge_without_reunion(self):
        self.pattern["pressure_bands"][-1] = "high"
        self.assertEqual(self.result()["status"], "no_observed_reunion")

    def test_identical_paths_are_not_divergence(self):
        self.pattern["pressure_bands"][6] = "medium"
        self.assertEqual(self.result()["status"], "no_observed_reunion")

    def test_one_step_cannot_reunite(self):
        self.assertEqual(self.result(1)["status"], "no_observed_reunion")

    def test_terminal_history_is_not_invented(self):
        self.pattern["pressure_bands"] = ["low", "high", "medium", "low", "low", "high"]
        self.pattern["source_observation_event_ids"] = [f"o{i}" for i in range(1, 7)]
        self.assertEqual(self.result()["status"], "no_observed_reunion")

    def test_invalid_horizon(self):
        self.assertEqual(self.result(11)["status"], "insufficient_evidence")

    def test_invalid_context(self):
        self.contexts[1]["event_id"] = "c1"
        self.assertEqual(self.result()["status"], "insufficient_evidence")

    def test_missing_provenance(self):
        self.pattern["source_observation_event_ids"] = []
        self.assertEqual(self.result()["status"], "insufficient_evidence")

    def test_no_mutation(self):
        original = list(self.pattern["pressure_bands"])
        self.result()
        self.assertEqual(self.pattern["pressure_bands"], original)


if __name__ == "__main__":
    unittest.main()
