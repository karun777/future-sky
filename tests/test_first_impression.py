import unittest
from fsbot.first_impression import first_impression


class FirstImpressionTests(unittest.TestCase):
    def test_each_uniform(self):
        for choice in ("utility", "formal", "technical", "freeform"):
            ch = {"extra": {"arrival": {"pod_uniform_selected": "pod_" + choice}},
                  "equipped": {"chest": "itm_pod_uniform_" + choice}}
            self.assertIsNotNone(first_impression(ch, "neptune_lounge"))
            self.assertIsNone(first_impression(ch, "pod_room"))

    def test_changed_clothes_no_reaction(self):
        ch = {"extra": {"arrival": {"pod_uniform_selected": "pod_freeform"}},
              "equipped": {"chest": "itm_leather_jacket"}}
        self.assertIsNone(first_impression(ch, "neptune_lounge"))

    def test_only_once(self):
        ch = {"extra": {"arrival": {"pod_uniform_selected": "pod_freeform",
                                     "first_impression_seen": True}},
              "equipped": {"chest": "itm_pod_uniform_freeform"}}
        self.assertIsNone(first_impression(ch, "neptune_lounge"))


if __name__ == "__main__":
    unittest.main()
