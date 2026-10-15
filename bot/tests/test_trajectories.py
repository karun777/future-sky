import unittest
from fsbot.events.trajectories import historical_trajectories_for_present_context


class HistoricalTrajectoryTests(unittest.TestCase):
    def setUp(self):
        self.pattern = {
            "pattern_type": "comet_pressure_sequence",
            "pressure_bands": ["low", "high", "medium", "low", "high", "low", "medium"],
            "source_observation_event_ids": [f"o{i}" for i in range(1, 8)],
        }
        self.contexts = [
            {"event_type": "world_moment.context", "event_id": f"c{i}",
             "payload": {"moment_world_time_seconds": i * 100,
                         "comet": {"pressure_band": band}}}
            for i, band in enumerate(["low", "high"], 1)
        ]

    def result(self, steps=2):
        return historical_trajectories_for_present_context(self.pattern, self.contexts, steps=steps)

    def test_two_distinct_trajectories(self):
        result = self.result()
        self.assertEqual(result["status"], "historical_trajectories_observed")
        self.assertEqual([t["following_pressure_bands"] for t in result["historical_trajectories"]], [["medium", "low"], ["low", "medium"]])
        self.assertEqual(result["historical_trajectories"][1]["following_source_observation_event_ids"], ["o6", "o7"])
        self.assertTrue(all(t["complete_horizon_observed"] for t in result["historical_trajectories"]))

    def test_terminal_truncated_horizon(self):
        result = self.result(3)
        self.assertFalse(result["historical_trajectories"][1]["complete_horizon_observed"])
        self.assertEqual(result["historical_trajectories"][1]["following_pressure_bands"], ["low", "medium"])

    def test_terminal_match_without_continuation(self):
        self.pattern["pressure_bands"] = ["medium", "low", "high"]
        self.pattern["source_observation_event_ids"] = ["o1", "o2", "o3"]
        self.assertEqual(self.result()["status"], "no_observed_trajectory")

    def test_invalid_horizon(self):
        self.assertEqual(self.result(0)["status"], "insufficient_evidence")
        self.assertEqual(self.result(11)["status"], "insufficient_evidence")
        self.assertEqual(self.result(True)["status"], "insufficient_evidence")

    def test_invalid_context(self):
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
