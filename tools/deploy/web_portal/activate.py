"""Reviewed pilot activation. --check is read-only; activation requires sudo."""
import hashlib
import json
import os
from pathlib import Path
import pwd
import shutil
import subprocess
import sys
import time
import urllib.request
import urllib.error

SOURCE = Path("/home/efiishent/future-sky-worktrees/w6-f6")
LIVE = Path("/opt/futuresky")
HERE = SOURCE / "tools/deploy/web_portal"
NGINX = Path("/etc/nginx/sites-available/default")
DROPIN = Path("/etc/systemd/system/futuresky-bot.service.d/40-web-portal.conf")
ENV = LIVE / "web-portal.env"
STAGED_ENV = Path("/home/efiishent/.config/future-sky/web-portal.env")
PYTHON = LIVE / ".venv-web-pilot-20261029/bin/python"
MARKER = "    server_name www.future-sky.net future-sky.net; # managed by Certbot"
SERVICE = "futuresky-bot.service"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def command(*args):
    return subprocess.run(args, check=True, text=True, capture_output=True).stdout


def preflight():
    manifest = json.loads((HERE / "deployment-manifest.json").read_text())
    for relative, expected in manifest["source_files"].items():
        if sha(SOURCE / relative) != expected:
            raise RuntimeError("Source changed since staging: " + relative)
    for relative, expected in manifest["live_files"].items():
        target = LIVE / relative
        if expected is None:
            if target.exists():
                raise RuntimeError("New target already exists: " + relative)
        elif sha(target) != expected:
            raise RuntimeError("Runtime baseline changed: " + relative)
    if sha(NGINX) != manifest["nginx_sha256"] or NGINX.read_text().count(MARKER) != 1:
        raise RuntimeError("Nginx baseline changed")
    if DROPIN.exists() or ENV.exists():
        raise RuntimeError("Portal config already exists; inspect before repeating")
    cfg = dict(line.split("=", 1) for line in STAGED_ENV.read_text().splitlines() if "=" in line)
    required = ("FS_WEB_DISCORD_CLIENT_ID", "FS_WEB_DISCORD_CLIENT_SECRET",
                "FS_WEB_ALLOWED_DISCORD_IDS")
    if not all(cfg.get(key) for key in required) or cfg.get("FS_WEB_ENABLED") != "0":
        raise RuntimeError("Private staging configuration is incomplete")
    if cfg["FS_WEB_DISCORD_CLIENT_ID"] != "1348670557314482267":
        raise RuntimeError("Unexpected Discord application")
    if STAGED_ENV.stat().st_mode & 0o077:
        raise RuntimeError("Private staging file must be mode 0600")
    # Existing .env remains untouched; a destructive boot reset must not be enabled.
    probe = "from dotenv import dotenv_values; import sys; c=dotenv_values('/opt/futuresky/bot/.env'); sys.exit(1 if c.get('FS_RESET_ROOMS_ON_BOOT') == '1' else 0)"
    command(str(PYTHON), "-c", probe)
    command(str(PYTHON), "-m", "pip", "check")
    command(str(PYTHON), "-c", "from authlib.integrations.httpx_client import AsyncOAuth2Client; import discord, aiohttp")
    return manifest, cfg


def data_hashes():
    result = {}
    for root in (LIVE / "data", LIVE / "bot/data"):
        for path in root.rglob("*"):
            if path.is_file():
                result[str(path.relative_to(LIVE))] = sha(path)
    return result


def status(url):
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            return response.status
    except urllib.error.HTTPError as error:
        return error.code


def main():
    manifest, cfg = preflight()
    if sys.argv[1:] == ["--check"]:
        print("Preflight PASS: source, runtime baseline, private config and staged dependencies.")
        return
    if sys.argv[1:] or os.geteuid() != 0:
        raise SystemExit("Activate with sudo python3 activate.py, or inspect using --check.")
    if command("systemctl", "is-active", SERVICE).strip() != "active":
        raise RuntimeError("Bot is not currently active; inspect before deployment")
    command("nginx", "-t")
    stamp = time.strftime("%Y%m%d-%H%M%S")
    backup = LIVE / "backups" / ("web-portal-" + stamp)
    backup.mkdir(mode=0o700)
    targets = [LIVE / relative for relative in manifest["live_files"]] + [NGINX, DROPIN, ENV]
    originals = {}
    for index, target in enumerate(targets):
        if target.exists():
            original = target.stat()
            copy = backup / str(index)
            shutil.copyfile(target, copy)
            copy.chmod(0o600)
            originals[str(target)] = {"backup": str(copy), "mode": original.st_mode & 0o777,
                                      "uid": original.st_uid, "gid": original.st_gid}
        else:
            originals[str(target)] = None
    (backup / "restore.json").write_text(json.dumps(originals, indent=2))
    print("Backup prepared:", backup, flush=True)
    changed = False
    try:
        command("systemctl", "stop", SERVICE)
        changed = True
        before = data_hashes()
        owner = pwd.getpwnam("efiishent")
        for relative in manifest["live_files"]:
            target = LIVE / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(SOURCE / relative, target)
            target.chmod(0o644)
            os.chown(target, owner.pw_uid, owner.pw_gid)
        cfg["FS_WEB_ENABLED"] = "1"
        fd = os.open(ENV, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        with os.fdopen(fd, "w") as stream:
            stream.write("".join(key + "=" + value + "\n" for key, value in cfg.items()))
        DROPIN.parent.mkdir(parents=True, exist_ok=True)
        DROPIN.write_text("[Service]\nExecStart=\nExecStart=" + str(PYTHON) +
                          " /opt/futuresky/bot/run_bot.py\nEnvironmentFile=" + str(ENV) + "\n")
        DROPIN.chmod(0o644)
        fragment = (HERE / "nginx-location.conf").read_text()
        NGINX.write_text(NGINX.read_text().replace(MARKER, MARKER + "\n" + fragment, 1))
        command("nginx", "-t")
        if data_hashes() != before:
            raise RuntimeError("Data changed while stopped; inspect before restarting")
        (backup / "data-before.json").write_text(json.dumps(before, indent=2))
        command("systemctl", "daemon-reload")
        started = str(int(time.time()))
        command("systemctl", "start", SERVICE)
        print("Waiting for Discord reconnection and local portal...", flush=True)
        ready = False
        for attempt in range(45):
            try:
                pid = command("systemctl", "show", SERVICE, "-p", "MainPID", "--value").strip()
                logs = command("journalctl", "-u", SERVICE, "_PID=" + pid,
                               "--since", "@" + started, "--no-pager", "-o", "cat")
                if ("logged in as" in logs and status("http://127.0.0.1:8787/play/") == 200
                        and status("http://127.0.0.1:8787/play/api/me") == 401):
                    ready = True
                    break
            except Exception:
                pass
            time.sleep(1)
        if not ready:
            raise RuntimeError("Discord or local portal did not become ready")
        command("systemctl", "reload", "nginx")
        if status("https://future-sky.net/play/") != 200 or status("https://future-sky.net/play/api/me") != 401:
            raise RuntimeError("Public portal health check failed")
        (backup / "result.json").write_text(json.dumps({
            "source_commit": manifest["source_commit"], "status": "activated",
            "data_files_unchanged_during_install": len(before), "bot_pid": pid}, indent=2))
        print("Portal activated: https://future-sky.net/play/", flush=True)
        print("Discord reconnected. Anonymous character access denied. Existing player data preserved.")
    except Exception:
        print("Activation did not complete; restoring previous service and website configuration.", flush=True)
        if changed:
            subprocess.run(["systemctl", "stop", SERVICE], capture_output=True)
            for target_name, original in originals.items():
                target = Path(target_name)
                if original is None:
                    target.unlink(missing_ok=True)
                else:
                    shutil.copyfile(original["backup"], target)
                    target.chmod(original["mode"])
                    os.chown(target, original["uid"], original["gid"])
            command("systemctl", "daemon-reload")
            command("nginx", "-t")
            command("systemctl", "reload", "nginx")
            command("systemctl", "start", SERVICE)
        print("Rollback completed. Backup:", backup, flush=True)
        raise


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        # No subprocess output or environment content is printed.
        print("Stopped:", type(error).__name__, str(error) if isinstance(error, RuntimeError)
              else "A system check failed; inspect the deployment record.")
        sys.exit(1)
