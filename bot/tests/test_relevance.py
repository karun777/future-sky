import unittest

from fsbot.events.relevance import comet_pressure_relevance


class CometPressureRelevanceTests(unittest.TestCase):
    def setUp(self):
        self.pattern = {
            "pattern_type": "comet_pressure_sequence",
            "pressure_bands": ["low", "high"],
            "source_observation_event_ids": ["obs-1", "obs-2"],
        }

    def test_applicable_with_provenance(self):
        result = comet_pressure_relevance(self.pattern, current_pressure_band="high")
        self.assertEqual(result["status"], "applicable")
        self.assertEqual(result["source_observation_event_ids"], ["obs-1", "obs-2"])

    def test_different_band_is_not_applicable(self):
        result = comet_pressure_relevance(self.pattern, current_pressure_band="low")
        self.assertEqual(result["status"], "not_applicable")

    def test_missing_context_is_insufficient(self):
        result = comet_pressure_relevance(self.pattern, current_pressure_band="")
        self.assertEqual(result["status"], "insufficient_evidence")

    def test_missing_provenance_is_insufficient(self):
        self.pattern["source_observation_event_ids"] = []
        result = comet_pressure_relevance(self.pattern, current_pressure_band="high")
        self.assertEqual(result["status"], "insufficient_evidence")


if __name__ == "__main__":
    unittest.main()
