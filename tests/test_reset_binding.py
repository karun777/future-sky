from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from fsbot.reset_binding import apply_reset_binding

class ResetBindingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "receipt.json"
        p = patch("fsbot.reset_binding.RESET_RUN_BINDINGS_FILE", str(self.path))
        p.start(); self.addCleanup(p.stop)
        self.binding = {"run_channel_id":"500", "run_seeded_channel_id":500}
        self.receipt = {"version":1, "bindings":{"101":self.binding}}
        self.character = {"id":"101", "name":"New Name", "bag":{}}
    def write(self): self.path.write_text(json.dumps(self.receipt))
    def test_only_identity_carried_and_receipt_survives_retry(self):
        self.write(); before = self.path.read_bytes()
        apply_reset_binding(self.character, {})
        self.assertEqual({"id":"101","name":"New Name","bag":{},**self.binding},self.character)
        apply_reset_binding(self.character, {})
        self.assertEqual(before,self.path.read_bytes())
    def test_absent_receipt_or_other_account_no_effect(self):
        before = deepcopy(self.character)
        apply_reset_binding(self.character,{})
        self.write(); self.character["id"]="202";before["id"]="202"
        apply_reset_binding(self.character,{})
        self.assertEqual(before,self.character)
    def test_malformed_receipt_refused(self):
        self.path.write_text("{")
        with self.assertRaises(ValueError):apply_reset_binding(self.character,{})
        self.assertNotIn("run_channel_id",self.character)
    def test_progress_fields_refused(self):
        self.binding["bag"]={"old":1};self.write()
        with self.assertRaises(ValueError):apply_reset_binding(self.character,{})
    def test_duplicate_or_existing_other_claim_refused(self):
        self.write()
        with self.assertRaises(ValueError):
            apply_reset_binding(self.character,{"202":{"run_channel_id":"500"}})
        self.receipt["bindings"]["202"]=dict(self.binding);self.write()
        with self.assertRaises(ValueError):apply_reset_binding(self.character,{})
    def test_seed_marker_must_match(self):
        self.binding["run_seeded_channel_id"]=501;self.write()
        with self.assertRaises(ValueError):apply_reset_binding(self.character,{})
