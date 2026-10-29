"""Authorization boundary and information disclosure tests; fictional state only."""
from copy import deepcopy
from types import SimpleNamespace
import unittest

from fsbot.web_character_view import character_view, CharacterAccessDenied


class WebCharacterViewTests(unittest.TestCase):
    def setUp(self):
        self.storage = SimpleNamespace(
            characters={
                "123": {"name": "Pilot", "current_room": "pod_room", "credits": 7,
                        "bag": {"coat": 2}, "equipped": {"chest": "coat"},
                        "extra": {"queen_secret": "DO NOT DISCLOSE"},
                        "flags": {"admin": True}, "run_channel_id": "secret"},
                "456": {"name": "Other", "current_room": "other"}},
            rooms={"pod_room": {"title": "Pod", "secret": "hidden route",
                                "exits": {"secret": "other"}}},
            items_db={"coat": {"name": "Coat", "secret": "hidden effect"}})

    def view(self, uid="123"):
        return character_view(self.storage, uid, allowed_discord_ids={"123"})

    def test_owner_gets_existing_character_and_approved_art(self):
        view = self.view()
        self.assertEqual(view["character"], {"name": "Pilot", "credits": 7})
        self.assertTrue(view["location"]["image"].endswith("/pod/v1/p01.png"))
        self.assertEqual(view["inventory"]["bag"][0]["name"], "Coat")

    def test_unapproved_and_invalid_identities_are_denied(self):
        for uid in ("456", "missing", "１２３", 123, None, ""):
            with self.subTest(uid=uid), self.assertRaises(CharacterAccessDenied):
                self.view(uid)

    def test_missing_character_is_not_created(self):
        before = deepcopy(self.storage.characters)
        with self.assertRaises(CharacterAccessDenied):
            character_view(self.storage, "789", allowed_discord_ids={"789"})
        self.assertEqual(before, self.storage.characters)

    def test_internal_fields_and_other_characters_are_not_exposed(self):
        import json
        serialized = json.dumps(self.view())
        for secret in ("DO NOT DISCLOSE", "admin", "run_channel_id",
                       "hidden route", "hidden effect", "Other", "exits"):
            self.assertNotIn(secret, serialized)

    def test_reads_and_returned_objects_cannot_mutate_game(self):
        before = deepcopy(vars(self.storage))
        view = self.view()
        view["inventory"]["equipped"]["chest"]["name"] = "Changed"
        self.assertEqual(before, vars(self.storage))

    def test_invalid_quantities_are_not_shown(self):
        self.storage.characters["123"]["bag"].update(
            {"negative": -1, "boolean": True, "text": "5", "empty": 0})
        self.assertEqual(len(self.view()["inventory"]["bag"]), 1)

    def test_cube_does_not_reveal_outside_location(self):
        self.storage.characters["123"]["in_cube"] = True
        self.assertEqual(self.view()["location"],
                         {"id": None, "title": None, "image": None})

    def test_external_or_placeholder_image_is_not_used(self):
        self.storage.characters["123"]["current_room"] = "other"
        self.storage.rooms["other"] = {"image": "https://other.example/image.png"}
        self.assertIsNone(self.view()["location"]["image"])

    def test_projection_does_not_claim_action_support(self):
        self.assertEqual(self.view()["capabilities"],
                         {"read_only": True, "actions": []})


if __name__ == "__main__":
    unittest.main()
