"""Selective W7-F5 overlay. --check reads only; activation requires root."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import urllib.request
import urllib.error

SOURCE = Path(__file__).resolve().parents[3]
LIVE = Path("/opt/futuresky")
HERE = Path(__file__).resolve().parent
PYTHON = LIVE / ".venv-web-pilot-20261029/bin/python"
SERVICE = "futuresky-bot.service"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def command(*args):
    return subprocess.run(args, check=True, text=True, capture_output=True).stdout


def preflight():
    manifest = json.loads((HERE / "deployment-manifest.json").read_text())
    for relative, hashes in manifest["files"].items():
        if sha(SOURCE / relative) != hashes["source"]:
            raise RuntimeError("Source changed: " + relative)
        if sha(LIVE / relative) != hashes["live"]:
            raise RuntimeError("Live baseline changed: " + relative)
    active = command("systemctl", "is-active", SERVICE).strip()
    if active != "active":
        raise RuntimeError("Bot is not active; inspect before deployment")
    start = command("systemctl", "show", SERVICE, "--property=ExecStart", "--value")
    if str(PYTHON) not in start:
        raise RuntimeError("Unexpected service interpreter")
    probe = ("from dotenv import dotenv_values; import sys; "
             "c=dotenv_values('/opt/futuresky/bot/.env'); "
             "sys.exit(1 if c.get('FS_RESET_ROOMS_ON_BOOT') == '1' else 0)")
    command(str(PYTHON), "-c", probe)
    command(str(PYTHON), "-m", "pip", "check")
    return manifest


def data_hashes():
    return {str(p.relative_to(LIVE)): sha(p)
            for root in (LIVE / "data", LIVE / "bot/data")
            for p in root.rglob("*") if p.is_file()}


def status(url, *, post=False):
    req = urllib.request.Request(url, data=b"{}" if post else None,
                                 method="POST" if post else "GET")
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            return response.status
    except urllib.error.HTTPError as exc:
        return exc.code


def wait_ready(since, *, walking):
    for _ in range(30):
        try:
            pid = command("systemctl", "show", SERVICE, "--property=MainPID", "--value").strip()
            logs = command("journalctl", "-u", SERVICE, "--since", since,
                           "--no-pager", "-o", "cat", "_PID=" + pid)
            if (pid != "0" and "Logged in as" in logs
                    and status("http://127.0.0.1:8787/play/") == 200
                    and status("http://127.0.0.1:8787/play/api/me") == 401
                    and (not walking or status("http://127.0.0.1:8787/play/api/walk", post=True) == 401)):
                return pid
        except Exception:
            pass
        time.sleep(1)
    raise RuntimeError("Discord and portal health check timed out")


def restore(backup, manifest):
    command("systemctl", "stop", SERVICE)
    for relative in manifest["files"]:
        shutil.copy2(backup / relative, LIVE / relative)
    since = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    command("systemctl", "start", SERVICE)
    return wait_ready(since, walking=False)


def activate(manifest):
    stamp = time.strftime("%Y%m%d-%H%M%S", time.gmtime())
    backup = LIVE / "backups" / ("w7f5-walking-" + stamp)
    backup.mkdir(parents=True, mode=0o700)
    for relative in manifest["files"]:
        dest = backup / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(LIVE / relative, dest)
    (backup / "deployment.json").write_text(json.dumps(manifest, indent=2))
    print("Backup prepared: " + str(backup), flush=True)
    before = None
    installed = False
    try:
        command("systemctl", "stop", SERVICE)
        before = data_hashes()
        # Revalidate stopped files: never overwrite a changed runtime baseline.
        for relative, hashes in manifest["files"].items():
            if sha(LIVE / relative) != hashes["live"]:
                raise RuntimeError("Live file changed during staging: " + relative)
            if sha(SOURCE / relative) != hashes["source"]:
                raise RuntimeError("Source changed during staging: " + relative)
        installed = True
        for relative in manifest["files"]:
            target = LIVE / relative
            previous = target.stat()
            temporary = target.with_name(target.name + ".w7f5-new")
            temporary.write_bytes((SOURCE / relative).read_bytes())
            os.chmod(temporary, previous.st_mode & 0o777)
            os.chown(temporary, previous.st_uid, previous.st_gid)
            os.replace(temporary, target)
        if before != data_hashes():
            raise RuntimeError("Player data changed while service was stopped")
        since = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        command("systemctl", "start", SERVICE)
        print("Waiting for Discord reconnection and walking portal...", flush=True)
        pid = wait_ready(since, walking=True)
        if (status("https://future-sky.net/play/") != 200
                or status("https://future-sky.net/play/api/me") != 401
                or status("https://future-sky.net/play/api/walk", post=True) != 401):
            raise RuntimeError("Public portal health check failed")
        (backup / "result.json").write_text(json.dumps({
            "status": "activated", "pid": pid, "data_preserved_during_overlay": True,
            "authenticated_playcheck": "pending"}, indent=2))
        print("W7-F5 activated: https://future-sky.net/play/", flush=True)
        print("Discord reconnected. Anonymous movement denied. Player data preserved.")
        print("Sign in again, walk one exit, then check the same location in Discord.")
    except BaseException:
        print("Activation failed; restoring the prior code (never player data).", flush=True)
        try:
            if installed:
                pid = restore(backup, manifest)
            else:
                since = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
                command("systemctl", "start", SERVICE)
                pid = wait_ready(since, walking=False)
            (backup / "result.json").write_text(json.dumps({"status": "rolled_back", "pid": pid}))
            print("Previous portal restored and Discord reconnected.", flush=True)
        except BaseException:
            print("Rollback needs operator attention. Backup: " + str(backup), flush=True)
            raise
        raise


def main():
    manifest = preflight()
    if "--check" in sys.argv:
        print("W7-F5 preflight passed. Six-file overlay; no new dependencies or configuration.")
        return
    if os.geteuid() != 0:
        raise SystemExit("Activation requires sudo; --check is read-only.")
    activate(manifest)


if __name__ == "__main__":
    main()
