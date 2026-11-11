from copy import deepcopy
import json
import os
import unittest
from unittest.mock import patch
from tools.character_reset_rehearsal import Rehearsal, Refused, atomic, digest


def fixtures():
    return {
        "characters": {"101": {"id": "101", "name": "Fictional traveller", "extra": {"old": True}},
                       "202": {"id": "202", "name": "Other"}},
        "lockers": {"101": {"capacity": 20, "items": {"old": 1}}, "202": {"items": {}}},
        "vault": {"101": {}, "202": {"kept": 1}},
        "cubes": {"cube_personal_101": {"owner": {"user_id": "101"}, "cube_type": "personal_cube_v0"},
                  "cube_efiishent_prime": {"meta": {"dpc_user_id": "101"}},
                  "cube_personal_202": {"owner": {"user_id": "202"}, "cube_type": "personal_cube_v0"}},
    }


class ResetRehearsalTests(unittest.TestCase):
    def setUp(self):
        self.original = fixtures()
        self.r = Rehearsal(self.original)
        self.addCleanup(self.r.close)

    def test_reset_restore_roundtrip_preserves_unrelated(self):
        archive = self.r.apply(self.r.plan("101"))
        reset = self.r.read()
        for name, key in self.r._keys("101").items():
            self.assertNotIn(key, reset[name])
            expected = deepcopy(self.original[name])
            expected.pop(key)
            self.assertEqual(expected, reset[name])
        self.r.apply(self.r.plan("101", restore=archive))
        self.assertEqual(self.original, self.r.read())

    def test_restore_archives_replacement_first(self):
        old = self.r.apply(self.r.plan("101"))
        current = self.r.read()
        current["characters"]["101"] = {"id": "101", "name": "New life"}
        current["vault"]["101"] = {"new": 9}
        for name, value in current.items():
            atomic(self.r.root / (name + ".json"), value)
        replacement = self.r.apply(self.r.plan("101", restore=old))
        self.assertEqual(self.original, self.r.read())
        self.r.apply(self.r.plan("101", restore=replacement))
        self.assertEqual(current, self.r.read())

    def test_absent_and_empty_are_distinct(self):
        initial = fixtures()
        del initial["lockers"]["101"]
        r = Rehearsal(initial)
        self.addCleanup(r.close)
        saved = r.apply(r.plan("101"))
        r.apply(r.plan("101", restore=saved))
        self.assertEqual(initial, r.read())
        self.assertNotIn("101", r.read()["lockers"])
        self.assertEqual({}, r.read()["vault"]["101"])

    def test_interruption_after_each_store_recovers(self):
        for cut in range(4):
            with self.subTest(cut=cut):
                r = Rehearsal(fixtures())
                self.addCleanup(r.close)
                def interrupt(index):
                    if index == cut:
                        raise RuntimeError("simulated process interruption")
                with self.assertRaises(RuntimeError):
                    r.apply(r.plan("101"), after_write=interrupt)
                with self.assertRaises(Refused):
                    r.plan("101")
                r.recover()
                self.assertEqual(fixtures(), r.read())

    def test_stale_plan_rejected_without_archive(self):
        plan = self.r.plan("101")
        changed = self.r.read()["vault"]
        changed["202"] = {"new_other_progress": 1}
        atomic(self.r.root / "vault.json", changed)
        before = self.r.read()
        with self.assertRaises(Refused):
            self.r.apply(plan)
        self.assertEqual(before, self.r.read())
        self.assertEqual([], list(self.r.archive_dir.iterdir()))

    def test_crafted_plan_cannot_modify_other_player(self):
        plan = self.r.plan("101")
        plan["payload"]["after"]["characters"]["202"]["name"] = "Tampered"
        plan["sha256"] = digest(plan["payload"])
        with self.assertRaises(Refused):
            self.r.apply(plan)
        self.assertEqual(self.original, self.r.read())

    def test_ownership_mismatch_blocks(self):
        for name in ("characters", "cubes"):
            data = fixtures()
            if name == "characters":
                data[name]["101"]["id"] = "202"
            else:
                data[name]["cube_personal_101"]["owner"]["user_id"] = "202"
            r = Rehearsal(data)
            self.addCleanup(r.close)
            with self.assertRaises(Refused):
                r.plan("101")
            self.assertEqual(data, r.read())

    def test_damaged_or_wrong_identity_archive_blocks(self):
        archive = self.r.archive("101")
        with self.assertRaises(Refused):
            self.r.plan("202", restore=archive)
        path = self.r.archive_dir / (archive + ".json")
        envelope = json.loads(path.read_text())
        envelope["payload"]["selected"]["vault"]["value"] = {"tampered": 1}
        atomic(path, envelope)
        with self.assertRaises(Refused):
            self.r.plan("101", restore=archive)
        self.assertEqual(self.original, self.r.read())

    def test_recovery_refuses_external_write_before_any_rollback(self):
        def interrupt(index):
            if index == 0:
                raise RuntimeError()
        with self.assertRaises(RuntimeError):
            self.r.apply(self.r.plan("101"), after_write=interrupt)
        data = self.r.read()["vault"]
        data["202"] = {"new": 3}
        atomic(self.r.root / "vault.json", data)
        before = self.r.read()
        with self.assertRaises(Refused):
            self.r.recover()
        self.assertEqual(before, self.r.read())
        self.assertTrue((self.r.root / "journal.json").exists())

    def test_damaged_journal_blocks_recovery(self):
        def interrupt(index):
            raise RuntimeError()
        with self.assertRaises(RuntimeError):
            self.r.apply(self.r.plan("101"), after_write=interrupt)
        path = self.r.root / "journal.json"
        envelope = json.loads(path.read_text())
        envelope["sha256"] = "broken"
        atomic(path, envelope)
        before = self.r.read()
        with self.assertRaises(Refused):
            self.r.recover()
        self.assertEqual(before, self.r.read())


    def test_archive_failure_never_changes_stores(self):
        with patch("tools.character_reset_rehearsal.atomic", side_effect=OSError("disk full")):
            with self.assertRaises(OSError):
                self.r.apply(self.r.plan("101"))
        self.assertEqual(self.original, self.r.read())
        self.assertFalse((self.r.root / "journal.json").exists())

    def test_store_write_failure_has_durable_rollback(self):
        real_atomic = atomic
        def fail(path, value):
            if path.name == "lockers.json":
                raise OSError("write failed")
            real_atomic(path, value)
        with patch("tools.character_reset_rehearsal.atomic", side_effect=fail):
            with self.assertRaises(OSError):
                self.r.apply(self.r.plan("101"))
        # A fresh object with only a path can recover: no in-memory plan required.
        reopened = Rehearsal.__new__(Rehearsal)
        reopened.root = self.r.root
        reopened.recover()
        self.assertEqual(self.original, self.r.read())

    def test_interrupted_rollback_can_be_retried(self):
        def interrupt(index):
            if index == 2:
                raise RuntimeError()
        with self.assertRaises(RuntimeError):
            self.r.apply(self.r.plan("101"), after_write=interrupt)
        def fail(path, value):
            if path.name == "vault.json":
                raise OSError("interrupted rollback")
            atomic(path, value)
        with patch("tools.character_reset_rehearsal.atomic", side_effect=fail):
            with self.assertRaises(OSError):
                self.r.recover()
        self.assertTrue((self.r.root / "journal.json").exists())
        self.r.recover()
        self.assertEqual(self.original, self.r.read())

    def test_private_files_and_no_second_reset(self):
        saved = self.r.apply(self.r.plan("101"))
        self.assertEqual(0o600, os.stat(self.r.archive_dir / (saved + ".json")).st_mode & 0o777)
        self.assertEqual(0o700, os.stat(self.r.root).st_mode & 0o777)
        with self.assertRaises(Refused):
            self.r.plan("101")

    def test_no_filesystem_path_input_or_path_traversal(self):
        with self.assertRaises((Refused, AttributeError)):
            Rehearsal("/opt/futuresky/data")
        with self.assertRaises(Refused):
            self.r.plan("../101")
        with self.assertRaises(Refused):
            self.r.load_archive("../../anything", "101")


if __name__ == "__main__":
    unittest.main()
