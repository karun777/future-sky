"""Production adapter rehearsed exclusively against fictional temporary data."""
from copy import deepcopy
import json
import os
from pathlib import Path
import stat
import tempfile
import unittest
from unittest.mock import Mock, patch

from tools.character_reset_adapter import (
    Adapter, FILES, Refused, snapshot, document, replace, updated, envelope,
    offline_guard, runtime_check,
)
from fsbot.reset_binding import validate_reset_binding


def fixture():
    return {
        "characters": {"101": {"id": "101", "name": "Test Traveller",
            "run_channel_id": "500", "run_seeded_channel_id": 500,
            "bag": {"old-item": 2}, "extra": {"arrival": {"performance_booking": True}}},
            "202": {"id": "202", "name": "Protected Player", "run_channel_id": "600", "bag": {"gift": 1}}},
        "lockers": {"101": {"items": {"old": 1}}, "202": {"items": {"gift": 1}}},
        "vault": {"101": {}, "202": {"balance": 7}},
        "cubes": {"cube_personal_101": {
            "id": "cube_personal_101", "cube_type": "personal_cube_v0",
            "owner": {"type": "player", "user_id": "101"}, "stash": {"items": {"old": 1}}},
            "cube_efiishent_prime": {"cube_type": "prime", "meta": {"dpc_user_id": "101"}},
            "cube_personal_202": {"owner": {"user_id": "202"}, "items": {"gift": 1}}},
    }


class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "data"
        self.state = Path(self.tmp.name) / "private"
        self.original = fixture()
        for name, value in self.original.items():
            path = self.root / FILES[name]
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(value, indent=2))
            path.chmod(0o640)
        for relative in ("characters/data/characters/characters.json", "time/world_clock.json",
                         "rooms/rooms.json"):
            p = self.root / relative
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text('{"preserve":"exact bytes"}\n')
        self.guard = Mock()
        self.a = Adapter(self.root, self.state, self.guard)
        self.a.__enter__()
        self.addCleanup(lambda: self.a.__exit__() if not self.a.lock.closed else None)
        self.initial = self.a.read()
        self.protected = self.a.protected()

    def plan(self, **kwargs):
        return self.a.plan("101", "Test Traveller", **kwargs)

    def put(self, name, value):
        path = self.root / FILES[name]
        replace(path, updated(snapshot(path), value, path.parent))

    def test_plan_is_readonly_and_full_roundtrip(self):
        plan = self.plan()
        self.assertEqual(self.initial, self.a.read())
        old = self.a.apply(plan)
        reset = self.a.read()
        for name, key in (("characters","101"),("lockers","101"),("vault","101"),("cubes","cube_personal_101")):
            expected = deepcopy(self.original[name]); expected.pop(key)
            self.assertEqual(expected, document(reset[name]))
        receipt = document(reset["receipt"])
        new = {"id":"101", "name":"Different Name", "bag":{}}
        validate_reset_binding(receipt, new, document(reset["characters"]))
        self.assertEqual("500", new["run_channel_id"])
        self.assertEqual({}, new["bag"])
        self.assertNotIn("extra", new)
        self.a.apply(self.plan(restore=old))
        for name in self.original:
            self.assertEqual(self.original[name], document(self.a.read()[name]))
        self.assertIsNone(self.a.read()["receipt"])
        self.assertEqual(self.protected, self.a.protected())

    def test_restore_archives_replacement_and_preserves_other_new_progress(self):
        old = self.a.apply(self.plan())
        chars = document(self.a.read()["characters"])
        chars["101"] = {"id":"101", "name":"New Life", "run_channel_id":"500",
                        "run_seeded_channel_id":500, "bag":{"new":1}}
        chars["202"]["bag"]["new-gift"] = 2
        self.put("characters",chars)
        replacement = self.a.apply(self.a.plan("101","New Life",restore=old))
        restored = document(self.a.read()["characters"])
        self.assertEqual(self.original["characters"]["101"], restored["101"])
        self.assertEqual(chars["202"],restored["202"])
        self.a.apply(self.a.plan("101","Test Traveller",restore=replacement))
        self.assertEqual(chars,document(self.a.read()["characters"]))

    def test_interrupt_every_write_reopen_and_recover_exact_bytes_and_modes(self):
        for stop in range(5):
            with self.subTest(stop=stop):
                plan = self.plan()
                def crash(index):
                    if index == stop: raise RuntimeError("simulated loss")
                with self.assertRaises(RuntimeError): self.a.apply(plan,crash)
                with self.assertRaises(Refused): self.plan()
                self.a.__exit__()
                self.a = Adapter(self.root,self.state,self.guard)
                self.a.__enter__()
                self.a.recover()
                self.assertEqual(self.initial,self.a.read())
                self.assertEqual(self.protected,self.a.protected())

    def test_recovery_can_be_interrupted_and_retried(self):
        def crash(index): raise RuntimeError("loss")
        with self.assertRaises(RuntimeError): self.a.apply(self.plan(),crash)
        with self.assertRaises(RuntimeError): self.a.recover(crash)
        self.a.recover()
        self.assertEqual(self.initial,self.a.read())

    def test_stale_plan_rejects_target_and_unrelated_changes(self):
        plan=self.plan()
        chars=deepcopy(self.original["characters"]);chars["202"]["bag"]["new"]=3
        self.put("characters",chars)
        with self.assertRaises(Refused):self.a.apply(plan)
        self.assertEqual(chars,document(self.a.read()["characters"]))
        self.assertFalse((self.state/"journal.json").exists())

    def test_changed_runtime_contract_blocks_apply(self):
        self.a.contract = lambda: {"reviewed_code": "before"}
        plan = self.plan()
        self.a.contract = lambda: {"reviewed_code": "after"}
        with self.assertRaises(Refused): self.a.apply(plan)
        self.assertEqual(self.initial, self.a.read())

    def test_crafted_plan_cannot_change_other_player(self):
        plan=self.plan()
        data=document(plan["payload"]["after"]["characters"])
        data["202"]["name"]="Tampered"
        plan["payload"]["after"]["characters"]=updated(plan["payload"]["before"]["characters"],data,self.root/"characters")
        plan=envelope(plan["payload"])
        with self.assertRaises(Refused):self.a.apply(plan)
        self.assertEqual(self.initial,self.a.read())

    def test_protected_file_changed_blocks_apply(self):
        plan=self.plan()
        (self.root/"time/world_clock.json").write_text("{}")
        with self.assertRaises(Refused):self.a.apply(plan)
        self.assertEqual(self.initial,self.a.read())

    def test_external_writer_after_interrupt_blocks_recovery_without_overwrite(self):
        def crash(index):raise RuntimeError("loss")
        with self.assertRaises(RuntimeError):self.a.apply(self.plan(),crash)
        chars=document(self.a.read()["characters"]);chars["202"]["name"]="Changed"
        self.put("characters",chars)
        before=self.a.read()
        with self.assertRaises(Refused):self.a.recover()
        self.assertEqual(before,self.a.read())
        self.assertTrue((self.state/"journal.json").exists())

    def test_archive_failure_leaves_all_data_untouched(self):
        with patch.object(self.a,"archive",side_effect=OSError("full")):
            with self.assertRaises(OSError):self.a.apply(self.plan())
        self.assertEqual(self.initial,self.a.read())
        self.assertFalse((self.state/"journal.json").exists())

    def test_store_replace_failure_leaves_recoverable_journal(self):
        from tools import character_reset_adapter as module
        original=module.replace
        count=0
        def fail(path,value):
            nonlocal count
            count+=1
            if count==2:raise OSError("full")
            original(path,value)
        with patch.object(module,"replace",side_effect=fail):
            with self.assertRaises(OSError):self.a.apply(self.plan())
        self.a.recover()
        self.assertEqual(self.initial,self.a.read())

    def test_damaged_journal_refused(self):
        def crash(index):raise RuntimeError("loss")
        with self.assertRaises(RuntimeError):self.a.apply(self.plan(),crash)
        p=self.state/"journal.json"
        value=json.loads(p.read_text());value["sha256"]="0"*64;p.write_text(json.dumps(value))
        before=self.a.read()
        with self.assertRaises(Refused):self.a.recover()
        self.assertEqual(before,self.a.read())

    def test_damaged_archive_refused(self):
        key=self.a.apply(self.plan())
        p=self.state/(key+".archive.json");p.write_text("{}")
        before=self.a.read()
        with self.assertRaises(Refused):self.plan(restore=key)
        self.assertEqual(before,self.a.read())

    def test_ownership_and_additional_cube_refused(self):
        cubes=deepcopy(self.original["cubes"])
        cubes["cube_personal_101"]["owner"]["user_id"]="202"
        self.put("cubes",cubes)
        with self.assertRaises(Refused):self.plan()
        cubes=deepcopy(self.original["cubes"]);cubes["101"]={"items":{"legacy":1}}
        self.put("cubes",cubes)
        with self.assertRaises(Refused):self.plan()

    def test_duplicate_channel_claim_and_conflicting_receipt_refused(self):
        chars=deepcopy(self.original["characters"]);chars["202"]["run_channel_id"]="500"
        self.put("characters",chars)
        with self.assertRaises(ValueError):self.plan()
        self.put("characters",self.original["characters"])
        self.put("receipt",{"version":1,"bindings":{"101":{"run_channel_id":"700","run_seeded_channel_id":700}}})
        with self.assertRaises(Refused):self.plan()

    def test_existing_other_receipt_and_empty_receipt_preserved_on_restore(self):
        for receipt in ({"version":1,"bindings":{}},
                        {"version":1,"bindings":{"303":{"run_channel_id":"800","run_seeded_channel_id":800}}}):
            with self.subTest(receipt=receipt):
                self.put("receipt",receipt)
                key=self.a.apply(self.plan())
                self.a.apply(self.plan(restore=key))
                self.assertEqual(receipt,document(self.a.read()["receipt"]))

    def test_symlink_and_missing_store_refused(self):
        path=self.root/FILES["vault"]
        saved=path.read_bytes();path.unlink();path.symlink_to(self.root/FILES["lockers"])
        with self.assertRaises(Refused):self.plan()
        path.unlink()
        with self.assertRaises(Refused):self.plan()
        path.write_bytes(saved)

    def test_account_name_and_ids_required(self):
        for uid in ("../101","0101","", "0"):
            with self.assertRaises(Refused):self.a.plan(uid,"Test Traveller")
        with self.assertRaises(Refused):self.a.plan("101","Wrong")

    def test_lock_excludes_second_adapter(self):
        with self.assertRaises(Refused):
            with Adapter(self.root,self.state,self.guard):pass

    def test_guard_rechecked_and_failure_keeps_journal(self):
        plan=self.plan()
        def turn_on(index):self.guard.side_effect=Refused("service active")
        with self.assertRaises(Refused):self.a.apply(plan,turn_on)
        self.guard.side_effect=None
        self.a.recover()
        self.assertEqual(self.initial,self.a.read())

    def test_private_permissions_and_live_metadata(self):
        old=self.a.apply(self.plan())
        self.assertEqual(0o700,stat.S_IMODE(self.state.stat().st_mode))
        for p in self.state.glob("*.json"):
            self.assertEqual(0o600,stat.S_IMODE(p.stat().st_mode))
        for name in self.original:
            for field in ("uid","gid","mode"):
                self.assertEqual(self.initial[name][field],self.a.read()[name][field])
        self.assertEqual(0o600,self.a.read()["receipt"]["mode"])

    def test_service_guard_refuses_active_without_inspecting_proc(self):
        result=Mock(stdout="MainPID=123\nActiveState=active\nSubState=running\n")
        with patch("tools.character_reset_adapter.subprocess.run",return_value=result):
            with self.assertRaises(Refused):offline_guard()

