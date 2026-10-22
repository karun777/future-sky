"""Executed boundary cases for the offline authoring interpretation."""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest
from terrace_rehearsal import (
    FixtureStore, Rehearsal, fictional_character, object_id,
    TERRACE, LOUNGE, DEMO, transition,
)

OPENING = ("attend", "notice sky", "take package", "open package",
           "unlock box", "open box", "take usb")


class TerraceTests(unittest.TestCase):
    def setUp(self):
        self.store = FixtureStore()
        self.addCleanup(self.store.close)
        self.run = Rehearsal(self.store)

    def actions(self, actions, uid="fixture-a"):
        return [self.run.act(action, uid) for action in actions]

    def character(self, uid="fixture-a"):
        return self.store.load()["characters"][uid]

    def test_complete_passage_reloads_every_action_and_preserves_other(self):
        other = deepcopy(self.character("fixture-b"))
        for action in DEMO:
            self.run.act(action)
            self.run = Rehearsal(self.store)  # no in-memory progress survives
        state = self.store.load()
        self.assertEqual(state["characters"]["fixture-b"], other)
        uid = "fixture-a"
        usb = state["objects"][object_id(uid, "usb")]
        self.assertEqual(usb["holder"], uid)
        self.assertEqual(self.character()["inventory"].count(object_id(uid, "usb")), 1)
        self.assertEqual(sum(f["kind"] == "package.landed" for f in state["facts"]), 1)
        self.assertEqual(sum(f["kind"] == "usb.collected" for f in state["facts"]), 1)

    def test_no_delivery_from_looking_or_moving_alone(self):
        self.actions(("look", "look", "leave", "return", "look"))
        self.assertEqual(self.store.load()["objects"], {})
        self.assertFalse(self.character()["attention"])

    def test_sky_requires_attention(self):
        before = self.store.path.read_bytes()
        self.assertIn("First take a moment", self.run.act("notice sky"))
        self.assertEqual(self.store.path.read_bytes(), before)

    def test_eligibility_and_knowledge_are_distinct(self):
        for enrolled, known in [(False, True), (True, False), (False, False)]:
            with self.subTest(enrolled=enrolled, known=known):
                store = FixtureStore({"fixture-a": fictional_character(
                    "Synthetic", enrolled=enrolled, booking_known=known)})
                try:
                    run = Rehearsal(store)
                    before = store.path.read_bytes()
                    self.assertIn("No performance-delivery encounter", run.act("attend"))
                    self.assertEqual(store.path.read_bytes(), before)
                    self.assertEqual(store.load()["objects"], {})
                finally:
                    store.close()

    def test_no_arrival_away_from_terrace(self):
        self.actions(("attend", "leave"))
        before = self.store.path.read_bytes()
        self.assertIn("not in view", self.run.act("notice sky"))
        self.assertEqual(self.store.path.read_bytes(), before)

    def test_package_may_be_taken_without_reading_address_first(self):
        self.actions(("attend", "notice sky"))
        self.assertIn("Warm", self.run.act("take package"))
        self.assertNotIn("package_address", self.character()["knowledge"])

    def test_departure_before_pickup_retains_landed_package(self):
        self.actions(("attend", "notice sky", "leave"))
        self.assertIn("not within reach", self.run.act("take package"))
        self.run.act("return")
        self.assertIn("package lies", self.run.act("look"))
        self.assertIn("Warm", self.run.act("take package"))
        self.assertEqual(sum(f["kind"] == "package.landed"
                             for f in self.store.load()["facts"]), 1)

    def test_package_can_be_opened_elsewhere_after_collection(self):
        self.actions(("attend", "notice sky", "take package", "leave"))
        self.assertIn("locked box", self.run.act("open package"))
        self.assertEqual(self.character()["room"], LOUNGE)

    def test_no_opening_uncollected_package_or_locked_box(self):
        self.actions(("attend", "notice sky"))
        self.assertIn("Pick up", self.run.act("open package"))
        self.actions(("take package", "open package"))
        self.assertIn("locked", self.run.act("open box"))
        self.assertIn("Open the box", self.run.act("take usb"))
        self.assertNotIn(object_id("fixture-a", "usb"), self.store.load()["objects"])

    def test_key_does_not_appear_by_wanting_to_unlock(self):
        ch = fictional_character("Synthetic", neck_key=False)
        state = self.store.load()
        state["characters"]["fixture-a"] = ch
        self.store.save(state)
        self.actions(("attend", "notice sky", "take package", "open package"))
        before = self.store.path.read_bytes()
        self.assertIn("No matching neck key", self.run.act("unlock box"))
        self.assertEqual(self.store.path.read_bytes(), before)
        self.assertTrue(self.store.load()["objects"][object_id("fixture-a", "box")]["locked"])

    def test_name_is_not_automatically_recognised(self):
        self.actions(("attend", "notice sky"))
        text = self.run.act("inspect package")
        self.assertIn("Rehearsal Traveller", text)
        self.assertIn("remains open", text)
        self.assertEqual(self.character()["knowledge"], ["package_address"])

    def test_authored_name_recognition_variants(self):
        for recognition, expected in [(True, "Yours."), (False, "does not yet feel")]:
            state = self.store.load()
            state["characters"]["fixture-a"]["recognises_name"] = recognition
            self.store.save(state)
            if not state["objects"]:
                self.actions(("attend", "notice sky"))
            self.assertIn(expected, self.run.act("inspect package"))

    def test_contents_are_not_revealed_before_each_layer(self):
        text = self.run.act("look") + " " + " ".join(self.actions(("attend", "notice sky", "inspect package")))
        self.assertNotIn("USB", text)
        self.assertNotIn("antique", text)
        self.run.act("take package")
        text = self.run.act("open package")
        self.assertIn("antique locked box", text)
        self.assertNotIn("USB", text)
        self.run.act("unlock box")
        self.assertNotIn("usb_label_tunes", self.character()["knowledge"])
        self.assertIn("tunes", self.run.act("open box"))
        self.assertNotIn(object_id("fixture-a", "usb"), self.character()["inventory"])
        self.assertIn("usb_label_tunes", self.character()["knowledge"])

    def test_repeated_actions_do_not_repeat_occurrences_or_inventory(self):
        self.actions(OPENING)
        before = self.store.path.read_bytes()
        for action in ["attend", "notice sky", "take package", "open package",
                       "unlock box", "open box", "take usb"]:
            self.run.act(action)
        self.assertEqual(self.store.path.read_bytes(), before)

    def test_failed_save_on_every_mutation_has_safe_retry(self):
        sequence = ("attend", "notice sky", "inspect package", "take package",
                    "open package", "inspect box", "unlock box", "open box",
                    "take usb", "leave", "return")
        for action in sequence:
            with self.subTest(action=action):
                before = self.store.path.read_bytes()
                self.store.fail_next_save = True
                response = self.run.act(action)
                self.assertIn("could not save", response)
                self.assertEqual(self.store.path.read_bytes(), before)
                self.run = Rehearsal(self.store)
                self.assertNotIn("could not save", self.run.act(action))
                self.assertNotEqual(self.store.path.read_bytes(), before)
        self.assertEqual(sum(f["kind"] == "package.landed"
                             for f in self.store.load()["facts"]), 1)

    def test_two_fictional_players_get_distinct_fixture_instances(self):
        self.actions(OPENING)
        first = deepcopy(self.character())
        self.actions(OPENING, uid="fixture-b")
        state = self.store.load()
        self.assertEqual(state["characters"]["fixture-a"], first)
        for uid in ("fixture-a", "fixture-b"):
            self.assertEqual(state["objects"][object_id(uid, "usb")]["holder"], uid)
        self.assertNotEqual(object_id("fixture-a", "usb"), object_id("fixture-b", "usb"))

    def test_future_conditions_remain_unresolved_and_no_send_or_vanish(self):
        self.actions(OPENING)
        before = self.store.path.read_bytes()
        for action in ["send", "invalidate", "give usb", "drop usb", "copy usb"]:
            self.assertIn("listed rehearsal actions", self.run.act(action))
        self.assertEqual(self.store.path.read_bytes(), before)
        usb = self.store.load()["objects"][object_id("fixture-a", "usb")]
        self.assertEqual(usb["temporal_validity"], "provisional")
        self.assertEqual(usb["future_condition"], "unresolved")
        self.assertEqual(usb["content_integrity"], "unexamined")
        all_text = self.run.act("inventory")
        for spoiler in ["Dark Rat Queen", "Vitriol", "princess", "future", "provisional"]:
            self.assertNotIn(spoiler, all_text)

    def test_pure_transition_and_disposable_save_boundary(self):
        before = self.store.load()
        snapshot = deepcopy(before)
        updated, _ = transition(before, "fixture-a", "attend")
        self.assertEqual(before, snapshot)
        self.assertNotEqual(updated, before)
        self.assertTrue(str(self.store.path).startswith(tempfile.gettempdir()))
        with self.assertRaises(ValueError):
            self.store.save({"characters": {}})
        self.assertEqual(self.store.load(), snapshot)


if __name__ == "__main__":
    unittest.main()
