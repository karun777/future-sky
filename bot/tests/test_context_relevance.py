import unittest

from fsbot.events.context_relevance import relevance_for_world_moment_context


class ContextRelevanceTests(unittest.TestCase):
    def setUp(self):
        self.pattern = {
            "pattern_type": "comet_pressure_sequence",
            "pressure_bands": ["low", "high"],
            "source_observation_event_ids": ["obs-1", "obs-2"],
        }
        self.context = {
            "event_id": "ctx-1",
            "event_type": "world_moment.context",
            "payload": {"comet": {"pressure_band": "high"}},
        }

    def test_existing_context_applies(self):
        result = relevance_for_world_moment_context(self.pattern, self.context)
        self.assertEqual(result["status"], "applicable")
        self.assertEqual(result["context_event_id"], "ctx-1")
        self.assertEqual(result["source_observation_event_ids"], ["obs-1", "obs-2"])

    def test_other_band_does_not_apply(self):
        self.context["payload"]["comet"]["pressure_band"] = "low"
        self.assertEqual(relevance_for_world_moment_context(self.pattern, self.context)["status"], "not_applicable")

    def test_unrelated_event_not_accepted(self):
        self.context["event_type"] = "comet.state_changed"
        self.assertEqual(relevance_for_world_moment_context(self.pattern, self.context)["status"], "insufficient_evidence")

    def test_context_without_identity_not_accepted(self):
        self.context.pop("event_id")
        self.assertEqual(relevance_for_world_moment_context(self.pattern, self.context)["status"], "insufficient_evidence")


if __name__ == "__main__":
    unittest.main()
