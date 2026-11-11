"""Fictional storage, with actual atomic persistence in a temporary directory."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from fsbot.storage import Storage

class PersonalCubeLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "cubes.json"
        self.s = Storage.__new__(Storage)
        self.s.characters = {"101": {"id": "101"}}
        self.s.cubes = {"cube_efiishent_prime": {"cube_type": "prime"},
                        "unrelated": {"items": {"gift": 1}}}
        self.before = deepcopy(self.s.cubes)
        p = patch("fsbot.storage.CUBES_FILE", str(self.path))
        p.start(); self.addCleanup(p.stop)

    def test_lazy_creation_is_durable_idempotent_and_preserves_others(self):
        key = self.s.ensure_personal_cube("101")
        first = deepcopy(self.s.cubes)
        self.assertEqual(key, self.s.ensure_personal_cube("101"))
        self.assertEqual(first, self.s.cubes)
        self.assertEqual(first, json.loads(self.path.read_text()))
        for k, v in self.before.items(): self.assertEqual(v, self.s.cubes[k])
        self.assertNotIn("stash", self.s.get_personal_cube("101"))
        self.assertEqual({"current":100,"max":100}, self.s.cubes[key]["integrity"])

    def test_absent_or_mismatched_character_cannot_create(self):
        for char in [None, {"id":"202"}]:
            self.s.characters = {} if char is None else {"101": char}
            with self.assertRaises(ValueError): self.s.ensure_personal_cube("101")
        self.assertEqual(self.before, self.s.cubes)
        self.assertFalse(self.path.exists())

    def test_conflicting_or_malformed_cube_never_overwritten(self):
        for value in [None, {}, {"id":"cube_personal_101","cube_type":"personal_cube_v0",
                               "owner":{"type":"player","user_id":"202"}}]:
            self.s.cubes["cube_personal_101"] = value
            before = deepcopy(self.s.cubes)
            with self.assertRaises(ValueError): self.s.ensure_personal_cube("101")
            self.assertEqual(before, self.s.cubes)

    def test_duplicate_owner_under_other_key_refused(self):
        self.s.cubes["other"] = {"cube_type":"personal_cube_v0","owner":{"user_id":"101"}}
        with self.assertRaises(ValueError): self.s.ensure_personal_cube("101")
        self.assertNotIn("cube_personal_101", self.s.cubes)

    def test_failed_save_rolls_back_and_retry_succeeds(self):
        with patch.object(self.s, "save_cubes", side_effect=OSError("full")):
            with self.assertRaises(OSError): self.s.ensure_personal_cube("101")
        self.assertEqual(self.before, self.s.cubes)
        self.s.ensure_personal_cube("101")
        self.assertTrue(self.path.exists())

    def test_existing_holdings_preserved(self):
        key = self.s.ensure_personal_cube("101")
        self.s.cubes[key]["stash"] = {"items":{"gift":2}}
        self.s.save_cubes()
        self.s.ensure_personal_cube("101")
        self.assertEqual({"gift":2}, self.s.get_personal_cube("101")["stash"]["items"])

    def test_invalid_account_refused(self):
        with self.assertRaises(ValueError): self.s.ensure_personal_cube("../101")
        self.assertEqual(self.before, self.s.cubes)
