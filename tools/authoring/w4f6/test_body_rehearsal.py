import unittest
from copy import deepcopy
from body_rehearsal import load, attempt

class BodyRehearsalTests(unittest.TestCase):
    def test_actions_preserve_unrelated_state_and_inputs(self):
        content=load(); saved=deepcopy(content)
        state=dict(content["initial"], inventory=["example"], memory="unchanged")
        before=deepcopy(state)
        updated,_=attempt(content,state,"stand")
        self.assertEqual(state,before)
        self.assertEqual(content,saved)
        self.assertEqual(updated["inventory"],["example"])
        self.assertEqual(updated["memory"],"unchanged")
        self.assertEqual(updated["posture"],"standing")
    def test_complete_sequence_and_repeat(self):
        content=load(); state=deepcopy(content["initial"])
        state,_=attempt(content,state,"stand")
        self.assertEqual(state["discomfort"],"sharp_ache")
        state,_=attempt(content,state,"shift weight")
        self.assertEqual(state["discomfort"],"eased_ache")
        touched,_=attempt(content,state,"touch hip")
        self.assertEqual(touched,state)
        state,_=attempt(content,state,"sit")
        self.assertEqual(state,content["initial"])
        repeat,text=attempt(content,state,"sit")
        self.assertEqual(repeat,state)
        self.assertIn("No authored",text)
    def test_out_of_order_and_unsupported_do_not_change_state(self):
        content=load()
        for verb in ["shift weight","sit","heal"]:
            state=deepcopy(content["initial"])
            updated,_=attempt(content,state,verb)
            self.assertEqual(updated,state)
    def test_overlap_is_an_authoring_error(self):
        content=load(); content["actions"].append(deepcopy(content["actions"][0]))
        with self.assertRaises(ValueError):
            attempt(content,content["initial"],"stand")

if __name__ == "__main__":
    unittest.main()
