import unittest
from fsbot.events.context_relevance import relevance_for_context_transition


class ContextTransitionTests(unittest.TestCase):
    def setUp(self):
        self.pattern = {
            "pattern_type": "comet_pressure_sequence",
            "pressure_bands": ["low", "high"],
            "source_observation_event_ids": ["obs1", "obs2"],
        }
        self.previous = {
            "event_type": "world_moment.context",
            "event_id": "ctx1",
            "payload": {"moment_world_time_seconds": 100, "comet": {"pressure_band": "low"}},
        }
        self.current = {
            "event_type": "world_moment.context",
            "event_id": "ctx2",
            "payload": {"moment_world_time_seconds": 200, "comet": {"pressure_band": "high"}},
        }

    def evaluate(self):
        return relevance_for_context_transition(self.pattern, self.previous, self.current)

    def test_matching_transition(self):
        result = self.evaluate()
        self.assertEqual(result["status"], "applicable")
        self.assertEqual(result["context_event_ids"], ["ctx1", "ctx2"])
        self.assertEqual(result["source_observation_event_ids"], ["obs1", "obs2"])

    def test_different_transition(self):
        self.current["payload"]["comet"]["pressure_band"] = "low"
        self.assertEqual(self.evaluate()["status"], "not_applicable")

    def test_reversed_time_is_insufficient(self):
        self.current["payload"]["moment_world_time_seconds"] = 50
        self.assertEqual(self.evaluate()["status"], "insufficient_evidence")

    def test_same_context_identity_is_insufficient(self):
        self.current["event_id"] = "ctx1"
        self.assertEqual(self.evaluate()["status"], "insufficient_evidence")

    def test_missing_history_provenance_is_insufficient(self):
        self.pattern["source_observation_event_ids"] = []
        self.assertEqual(self.evaluate()["status"], "insufficient_evidence")

    def test_unrelated_event_is_insufficient(self):
        self.previous["event_type"] = "comet.state_changed"
        self.assertEqual(self.evaluate()["status"], "insufficient_evidence")


if __name__ == "__main__":
    unittest.main()
