import copy
import unittest
from interactions import load, resolve

class InteractionTests(unittest.TestCase):
    def setUp(self):
        self.rows = load()
    def test_character_context_changes_thought_not_physical_evidence(self):
        a = resolve(self.rows, "workshop_demo", "touch", "panel")
        b = resolve(self.rows, "workshop_demo", "touch", "panel", ["maintenance_training"])
        self.assertEqual(a["observation"], b["observation"])
        self.assertIsNone(a["thought"])
        self.assertIn("training", b["thought"])
    def test_repeated_observation_does_not_mutate_context(self):
        before = copy.deepcopy(self.rows)
        facts = set()
        a = resolve(self.rows, "pod", "examine", "hands", facts)
        self.assertEqual(a, resolve(self.rows, "pod", "examine", "hands", facts))
        self.assertEqual(self.rows, before)
        self.assertEqual(facts, set())
        self.assertEqual(a["discoveries"], ["unfamiliar_hands"])
    def test_scene_and_verb_do_not_leak_content(self):
        for scene, verb in [("garden_demo","touch"), ("workshop_demo","listen")]:
            result = resolve(self.rows, scene, verb, "panel")
            self.assertEqual(result["status"], "unsupported")
            self.assertNotIn("observation", result)
    def test_unmodelled_and_explicit_sense_availability(self):
        self.assertEqual(resolve(self.rows,"pod","examine","hands")["status"],"observed")
        self.assertEqual(resolve(self.rows,"pod","examine","hands",senses={"hearing"})["status"],"sense_unavailable")
    def test_condition_failure_does_not_reveal_content(self):
        rows = copy.deepcopy(self.rows)
        rows[0]["requires"] = ["near_wall"]
        result = resolve(rows,"pod","listen","pod")
        self.assertEqual(result["status"],"unavailable")
        self.assertNotIn("thought",result)
    def test_ambiguous_content_fails_instead_of_picking_arbitrarily(self):
        rows = copy.deepcopy(self.rows)
        row = copy.deepcopy(rows[0]); row["id"] += "_other"; rows.append(row)
        with self.assertRaises(ValueError):
            resolve(rows,"pod","listen","pod")
    def test_alias_and_spacing(self):
        self.assertEqual(resolve(self.rows,"pod"," TOUCH "," BED ")["status"],"observed")

if __name__ == "__main__":
    unittest.main()
