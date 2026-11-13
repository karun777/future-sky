"""Static release transactions; all assets, runtime files and players are fictional."""
import base64
from copy import deepcopy
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from tools.deploy.w6f10.activate import (
    StaticRelease, Refused, SOURCES, ORDER, RUNTIME, PREVIOUS, MANIFEST, sha, snapshot,
)


class StaticReleaseTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.repo, self.live, self.state = [self.base / n for n in ("repo", "live", "transaction")]
        for r in ORDER:
            self.put(self.live / r, "baseline " + r)
            (self.live / r).chmod(0o640)
        self.put(self.repo / SOURCES[ORDER[0]], "reviewed script")
        script_hash = sha(self.repo / SOURCES[ORDER[0]])
        self.put(self.repo / SOURCES[ORDER[1]], '<script src="game.js?v=w6f10-' + script_hash[:12] + '"></script>')
        for root in (self.repo, self.live):
            self.put(root / "bot/fsbot/arrival.py", "reviewed arrival")
        self.put(self.live / "bot/fsbot/router.py", "protected installed router")
        self.put(self.live / "assets/experiments/w6-f8/live/frame.css", "accepted frame")
        runtime = {"files": {"fsbot/arrival.py": {"source": sha(self.live / "bot/fsbot/arrival.py")}},
                   "pins": {"fsbot/router.py": sha(self.live / "bot/fsbot/router.py")}}
        self.put_json(self.repo / RUNTIME, runtime)
        for name in ("character_reset_adapter.py", "character_reset_rehearsal.py"):
            self.put(self.repo / "tools" / name, "fictional operator hash fixture")
        previous = {"files": {"bot/fsbot/arrival.py": {"source": sha(self.live / "bot/fsbot/arrival.py")}},
                    "pins": {r: sha(self.live / r) for r in (*ORDER, "bot/fsbot/router.py",
                             "assets/experiments/w6-f8/live/frame.css")}}
        self.put_json(self.repo / PREVIOUS, previous)
        baseline = {r: e["source"] for r, e in previous["files"].items()}
        baseline.update(previous["pins"])
        manifest = {
            "basis": {"runtime_sha256": sha(self.repo / RUNTIME),
                      "previous_sha256": sha(self.repo / PREVIOUS)},
            "files": {r: {"source_path": source, "source": sha(self.repo / source),
                           "live": baseline[r]} for r, source in SOURCES.items()},
            "pins": {r: h for r, h in baseline.items() if r not in ORDER},
        }
        self.put_json(self.repo / MANIFEST, manifest)
        self.before = self.release().current()
        self.put(self.live / "data/characters.json", '{"other_player":"present"}')
        self.put(self.live / "private/archive.json", '{"retained":"archive"}')
        self.put(self.live / "data/reset_receipt.json", '{"retained":"receipt"}')

    def put(self, path, value):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(value)

    def put_json(self, path, value):
        self.put(path, json.dumps(value))

    def release(self):
        return StaticRelease(self.repo, self.live, self.state)

    def test_install_order_rollback_order_exact_bytes_metadata_and_runtime(self):
        release = self.release()
        runtime = (self.repo / RUNTIME).read_bytes()
        steps = []
        release.install(lambda i: steps.append(release.current()))
        self.assertEqual(steps[0][ORDER[1]], self.before[ORDER[1]])
        self.assertNotEqual(steps[0][ORDER[0]], self.before[ORDER[0]])
        self.assertEqual(release.check(installed=True)["deployment_manifest"], sha(self.repo / RUNTIME))
        for r, snap in release.current().items():
            self.assertEqual({k: snap[k] for k in ("mode", "uid", "gid")},
                             {k: self.before[r][k] for k in ("mode", "uid", "gid")})
        steps = []
        release.rollback(lambda i: steps.append(release.current()))
        self.assertEqual(steps[0][ORDER[1]], self.before[ORDER[1]])
        self.assertNotEqual(steps[0][ORDER[0]], self.before[ORDER[0]])
        self.assertEqual(release.current(), self.before)
        self.assertEqual((self.repo / RUNTIME).read_bytes(), runtime)
        self.assertTrue((self.state / "transaction.json").exists())

    def test_interruption_after_each_asset_recovers_after_reopen(self):
        for stop in (0, 1):
            with self.subTest(stop=stop):
                def interrupted(i):
                    if i == stop:
                        raise RuntimeError("interrupted")
                with self.assertRaises(RuntimeError):
                    self.release().install(interrupted)
                self.release().rollback()
                self.assertEqual(self.release().current(), self.before)
                shutil.rmtree(self.state)

    def test_interrupted_rollback_retries(self):
        self.release().install()
        def interrupted(i):
            if i == 0:
                raise RuntimeError("interrupted rollback")
        with self.assertRaises(RuntimeError):
            self.release().rollback(interrupted)
        self.release().rollback()
        self.assertEqual(self.release().current(), self.before)

    def test_source_asset_and_dependency_drift_refuse_without_overwrite(self):
        for p in (self.repo / SOURCES[ORDER[0]], self.live / ORDER[1],
                  self.live / "bot/fsbot/router.py",
                  self.live / "assets/experiments/w6-f8/live/frame.css"):
            with self.subTest(path=p):
                old = p.read_bytes()
                p.write_bytes(b"outside change")
                current = self.release().current()
                with self.assertRaises(Refused):
                    self.release().install()
                self.assertEqual(self.release().current(), current)
                p.write_bytes(old)

    def test_contract_drift_extra_asset_and_rewritten_pins_refused(self):
        original = json.loads((self.repo / MANIFEST).read_text())
        for kind in ("extra", "pin", "runtime", "source_path"):
            m = deepcopy(original)
            if kind == "extra":
                m["files"]["data/characters.json"] = deepcopy(m["files"][ORDER[0]])
            elif kind == "pin":
                m["pins"]["bot/fsbot/router.py"] = "0" * 64
            elif kind == "runtime":
                m["basis"]["runtime_sha256"] = "0" * 64
            else:
                m["files"][ORDER[0]]["source_path"] = "data/characters.json"
            self.put_json(self.repo / MANIFEST, m)
            with self.assertRaises(Refused):
                self.release().install()
            self.assertEqual(self.release().current(), self.before)
        self.put_json(self.repo / MANIFEST, original)

    def test_capture_drift_refuses_before_journal_and_asset_write(self):
        for target in (self.live / ORDER[0], self.repo / SOURCES[ORDER[0]]):
            with self.subTest(target=target):
                release = self.release()
                original_check = release.check
                saved = target.read_bytes()
                def changed_after_check():
                    result = original_check()
                    target.write_bytes(b"concurrent capture change")
                    return result
                with patch.object(release, "check", changed_after_check):
                    with self.assertRaises(Refused):
                        release.install()
                self.assertFalse((self.state / "transaction.json").exists())
                self.assertEqual(snapshot(self.live / ORDER[1]), self.before[ORDER[1]])
                if target.is_relative_to(self.repo):
                    self.assertEqual(release.current(), self.before)
                else:
                    self.assertEqual(target.read_bytes(), b"concurrent capture change")
                target.write_bytes(saved)

    def test_journal_write_failure_changes_no_assets(self):
        with patch("tools.deploy.w6f10.activate.atomic", side_effect=OSError("disk full")):
            with self.assertRaises(OSError):
                self.release().install()
        self.assertEqual(self.release().current(), self.before)

    def test_corrupt_transaction_and_foreign_assets_block_rollback(self):
        self.release().install()
        path = self.state / "transaction.json"
        original = path.read_bytes()
        record = json.loads(original)
        record["payload"]["before"][ORDER[0]]["bytes"] = base64.b64encode(b"wrong").decode()
        self.put_json(path, record)
        current = self.release().current()
        with self.assertRaises(Refused):
            self.release().rollback()
        self.assertEqual(self.release().current(), current)
        path.write_bytes(original)
        (self.live / ORDER[0]).write_bytes(b"later external change")
        current = self.release().current()
        with self.assertRaises(Refused):
            self.release().rollback()
        self.assertEqual(self.release().current(), current)

    def test_data_and_archive_never_read_and_later_progress_survives(self):
        original_read = Path.read_bytes
        def read_code_only(path):
            if path.is_relative_to(self.live / "data") or path.is_relative_to(self.live / "private"):
                raise AssertionError("Static release read player state")
            return original_read(path)
        with patch.object(Path, "read_bytes", read_code_only):
            self.release().install()
            self.put(self.live / "data/characters.json", '{"other_player":"later progress"}')
            self.release().rollback()
        self.assertEqual((self.live / "data/characters.json").read_text(), '{"other_player":"later progress"}')
        self.assertEqual((self.live / "private/archive.json").read_text(), '{"retained":"archive"}')
        self.assertEqual((self.live / "data/reset_receipt.json").read_text(), '{"retained":"receipt"}')

    def test_duplicate_install_lock_and_private_state_requirements(self):
        with self.release().locked():
            with self.assertRaises(BlockingIOError):
                with self.release().locked():
                    pass
        self.state.chmod(0o755)
        with self.assertRaises(Refused):
            self.release().install()
        self.state.chmod(0o700)
        self.release().install()
        with self.assertRaises(Refused):
            self.release().install()
        self.release().rollback()
        with self.assertRaises(Refused):
            self.release().install()

    def test_symlink_asset_rejected(self):
        path = self.live / ORDER[0]
        real = self.base / "foreign.js"
        real.write_bytes(path.read_bytes())
        path.unlink()
        path.symlink_to(real)
        with self.assertRaises(Refused):
            self.release().install()
        self.assertEqual(real.read_bytes(), b"baseline " + ORDER[0].encode())


class ReviewedStaticPackageTests(unittest.TestCase):
    def test_exact_baseline_two_asset_overlay_and_unchanged_runtime(self):
        from tools.deploy.w6f10.activate import ROOT
        package = json.loads((ROOT / MANIFEST).read_text())
        previous = json.loads((ROOT / PREVIOUS).read_text())
        expected = {r: e["source"] for r, e in previous["files"].items()}
        expected.update(previous["pins"])
        self.assertEqual(set(package["files"]), set(ORDER))
        self.assertEqual(package["pins"], {r: h for r, h in expected.items() if r not in ORDER})
        # Sealed W6-F10 binds its reviewed bytes, not a later client draft.
        # GameFrameReturnTests checks the current client's cache/hash pairing.
        reviewed = {
            ORDER[0]: "b41f6e1f1619615be2d2c3639ce0f85f1ebbcf2b69f286ea9fe1c942b2da84cb",
            ORDER[1]: "e8a1e6df857f878031facec83b4a6c05ba0d5d9fc0ae4975a22d599c53fe8486",
        }
        for r, source in SOURCES.items():
            self.assertEqual(package["files"][r]["live"], expected[r])
            self.assertEqual(package["files"][r]["source_path"], source)
            self.assertEqual(package["files"][r]["source"], reviewed[r])
        self.assertEqual(package["basis"]["runtime_sha256"], sha(ROOT / RUNTIME))
        self.assertEqual(package["basis"]["previous_sha256"], sha(ROOT / PREVIOUS))
