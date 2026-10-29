"""Installer tests using only temporary directories and mocked service commands."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location(
    "w7f5_activate", Path(__file__).resolve().parents[1] / "tools/deploy/w7f5/activate.py")
deploy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(deploy)


class DeploymentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.source, self.live = root / "source", root / "live"
        self.files = ["bot/fsbot/example.py", "bot/fsbot/web_static/index.html"]
        self.manifest = {"files": {}}
        for f in self.files:
            for base, content in ((self.source, "new"), (self.live, "old")):
                target = base / f
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content)
            self.manifest["files"][f] = {
                "source": deploy.sha(self.source / f), "live": deploy.sha(self.live / f)}
        self.data = self.live / "bot/data/characters/characters.json"
        self.data.parent.mkdir(parents=True)
        self.data.write_text('{"fictional": {"current_room": "a"}}')
        self.before = self.data.read_bytes()
        for key, value in (("SOURCE", self.source), ("LIVE", self.live)):
            p = patch.object(deploy, key, value)
            p.start()
            self.addCleanup(p.stop)

    def check_data(self):
        self.assertEqual(self.data.read_bytes(), self.before)

    def test_success_installs_only_source_and_keeps_backups(self):
        with patch.object(deploy, "command", return_value=""), \
             patch.object(deploy, "wait_ready", return_value="123"), \
             patch.object(deploy, "status", side_effect=[200, 401, 401]):
            deploy.activate(self.manifest)
        for f in self.files:
            self.assertEqual((self.live / f).read_text(), "new")
        backup = next((self.live / "backups").iterdir())
        self.assertEqual((backup / self.files[0]).read_text(), "old")
        self.assertEqual(json.loads((backup / "result.json").read_text())["status"], "activated")
        self.check_data()

    def test_public_failure_restores_old_code_and_preserves_data(self):
        with patch.object(deploy, "command", return_value=""), \
             patch.object(deploy, "wait_ready", return_value="123"), \
             patch.object(deploy, "status", return_value=503):
            with self.assertRaisesRegex(RuntimeError, "Public portal"):
                deploy.activate(self.manifest)
        for f in self.files:
            self.assertEqual((self.live / f).read_text(), "old")
        self.check_data()

    def test_startup_failure_restores_then_checks_old_service(self):
        with patch.object(deploy, "command", return_value=""), \
             patch.object(deploy, "wait_ready", side_effect=[RuntimeError("failed"), "123"]) as ready:
            with self.assertRaisesRegex(RuntimeError, "failed"):
                deploy.activate(self.manifest)
        self.assertFalse(ready.call_args.kwargs["walking"])
        self.assertEqual((self.live / self.files[0]).read_text(), "old")
        self.check_data()

    def test_changed_baseline_before_overlay_is_not_overwritten_by_rollback(self):
        def command(*args):
            if args[:2] == ("systemctl", "stop"):
                (self.live / self.files[0]).write_text("concurrent-change")
            return ""
        with patch.object(deploy, "command", side_effect=command), \
             patch.object(deploy, "wait_ready", return_value="123"):
            with self.assertRaisesRegex(RuntimeError, "Live file changed"):
                deploy.activate(self.manifest)
        self.assertEqual((self.live / self.files[0]).read_text(), "concurrent-change")
        self.assertEqual((self.live / self.files[1]).read_text(), "old")
        self.check_data()


class ReadinessTests(unittest.TestCase):
    def test_actual_lowercase_login_and_both_portal_modes(self):
        for walking in (False, True):
            def command(*args):
                if args[0] == "systemctl":
                    return "917782\n"
                self.assertIn("_PID=917782", args)
                return "INFO:futuresky:✅ Future Sky v3.6.2 logged in as Future Sky#1526\n"
            def status(url, **kwargs):
                return 200 if url.endswith("/play/") else 401
            with patch.object(deploy, "command", side_effect=command), \
                 patch.object(deploy, "status", side_effect=status) as http, \
                 patch.object(deploy.time, "sleep") as sleep:
                self.assertEqual(deploy.wait_ready("2026-10-29 11:41:00 UTC", walking=walking), "917782")
                self.assertEqual(http.call_count, 3 if walking else 2)
                sleep.assert_not_called()

    def test_gateway_connection_alone_is_not_login_readiness(self):
        with patch.object(deploy, "command", side_effect=lambda *a:
                          "123" if a[0] == "systemctl" else "Shard connected to Gateway"), \
             patch.object(deploy, "status", return_value=200), \
             patch.object(deploy.time, "sleep"):
            with self.assertRaisesRegex(RuntimeError, "timed out"):
                deploy.wait_ready("2026-10-29 11:41:00 UTC", walking=False)

    def test_missing_walk_endpoint_fails_despite_login(self):
        with patch.object(deploy, "command", side_effect=lambda *a:
                          "123" if a[0] == "systemctl" else "logged in as Future Sky#1526"), \
             patch.object(deploy, "status", side_effect=lambda url, **kw:
                          200 if url.endswith("/play/") else 404 if url.endswith("walk") else 401), \
             patch.object(deploy.time, "sleep"):
            with self.assertRaisesRegex(RuntimeError, "timed out"):
                deploy.wait_ready("2026-10-29 11:41:00 UTC", walking=True)

    def test_journal_failure_fails_closed(self):
        with patch.object(deploy, "command", side_effect=RuntimeError("journal unavailable")), \
             patch.object(deploy.time, "sleep"):
            with self.assertRaisesRegex(RuntimeError, "timed out"):
                deploy.wait_ready("2026-10-29 11:41:00 UTC", walking=False)
