"""Exercise installer transaction with temporary files and simulated system commands."""
import contextlib
import importlib.util
import io
import os
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "tools/deploy/web_portal/activate.py"
spec = importlib.util.spec_from_file_location("web_activation", SCRIPT)
deploy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(deploy)


class DeploymentTests(unittest.TestCase):
    def run_fixture(self, failure=None):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source, live = root / "source", root / "live"
            here = source / "tools/deploy/web_portal"
            here.mkdir(parents=True)
            (source / "bot").mkdir()
            (source / "bot/run_bot.py").write_text("new entrypoint")
            (source / "bot/portal.py").write_text("new portal")
            (here / "nginx-location.conf").write_text("location /play/ { proxy_pass http://127.0.0.1:8787; }")
            (live / "bot/data").mkdir(parents=True)
            (live / "backups").mkdir()
            (live / "data").mkdir()
            (live / "bot/run_bot.py").write_text("original entrypoint")
            player = live / "bot/data/characters.json"
            player.write_text("fictional unchanged character")
            nginx = root / "nginx"
            nginx.write_text(deploy.MARKER)
            dropin, env = root / "service.d/portal.conf", live / "web-portal.env"
            manifest = {"source_commit": "fixture", "live_files":
                        {"bot/run_bot.py": "old", "bot/portal.py": None}}
            calls, validations = [], [0]

            def command(*args):
                calls.append(args)
                if args == ("nginx", "-t"):
                    validations[0] += 1
                    if failure == "nginx" and validations[0] == 2:
                        raise RuntimeError("fictional nginx failure")
                if args[:2] == ("systemctl", "is-active"):
                    return "active"
                if args[:2] == ("systemctl", "show"):
                    return "12345"
                if args[0] == "journalctl":
                    return "Future Sky logged in as fictional-bot"
                return ""

            def status(url):
                if failure == "public" and url.startswith("https"):
                    return 502
                return 401 if url.endswith("/api/me") else 200

            output = io.StringIO()
            changes = dict(SOURCE=source, LIVE=live, HERE=here, NGINX=nginx,
                           DROPIN=dropin, ENV=env, PYTHON=root / "python")
            with contextlib.ExitStack() as stack:
                for name, value in changes.items():
                    stack.enter_context(patch.object(deploy, name, value))
                stack.enter_context(patch.object(deploy, "preflight", return_value=(manifest,
                    {"FS_WEB_ENABLED": "0", "FS_WEB_DISCORD_CLIENT_SECRET": "fictional-secret"})))
                stack.enter_context(patch.object(deploy, "command", side_effect=command))
                stack.enter_context(patch.object(deploy, "status", side_effect=status))
                stack.enter_context(patch.object(deploy.os, "geteuid", return_value=0))
                stack.enter_context(patch.object(deploy.pwd, "getpwnam",
                    return_value=SimpleNamespace(pw_uid=os.getuid(), pw_gid=os.getgid())))
                stack.enter_context(patch.object(deploy.sys, "argv", ["activate.py"]))
                stack.enter_context(contextlib.redirect_stdout(output))
                if failure:
                    with self.assertRaises(RuntimeError):
                        deploy.main()
                else:
                    deploy.main()
            self.assertNotIn("fictional-secret", output.getvalue())
            self.assertEqual(player.read_text(), "fictional unchanged character")
            self.assertEqual(len(list((live / "backups").iterdir())), 1)
            if failure:
                self.assertEqual((live / "bot/run_bot.py").read_text(), "original entrypoint")
                self.assertFalse((live / "bot/portal.py").exists())
                self.assertEqual(nginx.read_text(), deploy.MARKER)
                self.assertFalse(env.exists())
                self.assertFalse(dropin.exists())
                self.assertIn(("systemctl", "start", deploy.SERVICE), calls)
                self.assertIn("Rollback completed", output.getvalue())
            else:
                self.assertEqual((live / "bot/run_bot.py").read_text(), "new entrypoint")
                self.assertIn("FS_WEB_ENABLED=1", env.read_text())
                self.assertEqual(env.stat().st_mode & 0o777, 0o600)
                self.assertIn("location /play/", nginx.read_text())
                self.assertIn("Portal activated", output.getvalue())

    def test_success_preserves_data_and_keeps_secret_private(self):
        self.run_fixture()

    def test_nginx_failure_restores_previous_runtime_and_config(self):
        self.run_fixture("nginx")

    def test_public_failure_rolls_back_after_bot_restart(self):
        self.run_fixture("public")
