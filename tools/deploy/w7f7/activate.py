"""W7-F7 selective deployment. --check is read-only; activation requires root."""
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
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None

def command(*args):
    return subprocess.run(args, check=True, text=True, capture_output=True).stdout

def validate(manifest):
    for relative, entry in manifest["files"].items():
        if sha(SOURCE / relative) != entry["source"]:
            raise RuntimeError("Source changed: " + relative)
        if sha(LIVE / entry["target"]) != entry["live"]:
            raise RuntimeError("Live baseline changed: " + entry["target"])

def preflight():
    manifest = json.loads((HERE / "deployment-manifest.json").read_text())
    validate(manifest)
    if command("systemctl", "is-active", SERVICE).strip() != "active":
        raise RuntimeError("Bot is not active; inspect before deployment")
    if str(PYTHON) not in command("systemctl","show",SERVICE,"--property=ExecStart","--value"):
        raise RuntimeError("Unexpected service interpreter")
    probe = ("from dotenv import dotenv_values; import sys; "
             "c=dotenv_values('/opt/futuresky/bot/.env'); "
             "sys.exit(1 if c.get('FS_RESET_ROOMS_ON_BOOT') == '1' else 0)")
    command(str(PYTHON), "-c", probe)
    command(str(PYTHON), "-m", "pip", "check")
    return manifest

def data_hashes():
    return {str(p.relative_to(LIVE)):sha(p)
            for root in (LIVE/"data",LIVE/"bot/data")
            for p in root.rglob("*") if p.is_file()}

def status(url, post=False):
    req=urllib.request.Request(url,data=b"{}" if post else None,method="POST" if post else "GET")
    try:
        with urllib.request.urlopen(req,timeout=5) as r:return r.status
    except urllib.error.HTTPError as e:return e.code

def wait_ready(since, inspection):
    for _ in range(60):
        try:
            pid=command("systemctl","show",SERVICE,"--property=MainPID","--value").strip()
            logs=command("journalctl","-u",SERVICE,"--since",since,"--no-pager","-o","cat","_PID="+pid)
            if (pid!="0" and "logged in as" in logs.casefold()
                    and status("http://127.0.0.1:8787/play/")==200
                    and status("http://127.0.0.1:8787/play/api/me")==401
                    and status("http://127.0.0.1:8787/play/api/walk",True)==401
                    and (not inspection or (status("http://127.0.0.1:8787/play/api/inspect",True)==401 and status("http://127.0.0.1:8787/play/api/wardrobe",True)==401))):
                return pid
        except Exception:
            pass
        time.sleep(1)
    raise RuntimeError("Discord and portal health check timed out")

def start_and_wait(inspection):
    since=time.strftime("%Y-%m-%d %H:%M:%S UTC",time.gmtime())
    command("systemctl","start",SERVICE)
    return wait_ready(since,inspection)

def restore(backup,manifest):
    command("systemctl","stop",SERVICE)
    before=data_hashes()
    for entry in manifest["files"].values():
        target=LIVE/entry["target"]
        if entry["live"] is None:
            target.unlink(missing_ok=True)
        else:
            shutil.copy2(backup/entry["target"],target)
    if data_hashes()!=before:
        raise RuntimeError("Player data changed during code rollback")
    return start_and_wait(False)

def activate(manifest):
    backup=LIVE/"backups"/("w7f7-wardrobe-"+time.strftime("%Y%m%d-%H%M%S",time.gmtime()))
    backup.mkdir(parents=True,mode=0o700)
    installed=False
    try:
        command("systemctl","stop",SERVICE)
        validate(manifest)
        before=data_hashes()
        for entry in manifest["files"].values():
            target=LIVE/entry["target"]
            if entry["live"] is not None:
                dest=backup/entry["target"];dest.parent.mkdir(parents=True,exist_ok=True)
                shutil.copy2(target,dest)
        (backup/"deployment.json").write_text(json.dumps(manifest,indent=2))
        print("Backup prepared: "+str(backup),flush=True)
        installed=True
        for relative,entry in manifest["files"].items():
            target=LIVE/entry["target"]
            reference=target if target.exists() else target.parent
            previous=reference.stat()
            temporary=target.with_name(target.name+".w7f7-new")
            temporary.write_bytes((SOURCE/relative).read_bytes())
            os.chmod(temporary, (previous.st_mode & 0o777) if target.exists() else 0o644)
            os.chown(temporary,previous.st_uid,previous.st_gid)
            os.replace(temporary,target)
        if data_hashes()!=before:
            raise RuntimeError("Player data changed while service was stopped")
        print("Waiting for Discord and wardrobe portal...",flush=True)
        pid=start_and_wait(True)
        if status("https://future-sky.net/play/api/wardrobe",True)!=401:
            raise RuntimeError("Public wardrobe gate failed")
        for relative,entry in manifest["files"].items():
            if entry["target"].startswith("assets/"):
                with urllib.request.urlopen("https://future-sky.net/"+entry["target"],timeout=10) as response:
                    if hashlib.sha256(response.read()).hexdigest()!=entry["source"]:
                        raise RuntimeError("Public file mismatch: "+entry["target"])
        (backup/"result.json").write_text(json.dumps({"status":"activated","pid":pid,
            "data_preserved_during_overlay":True,"authenticated_playcheck":"pending"},indent=2))
        print("W7-F7 activated: https://future-sky.net/assets/experiments/w6-f8/live/index.html")
        print("Discord reconnected. Anonymous wardrobe changes denied. Player data preserved.")
        print("Sign in again at /play/. Type help in COMMANDS; use inspect wardrobe, wardrobe and wear <carried garment>. Compare !fit in Discord.")
    except BaseException:
        print("Activation failed; restoring code only, never player data.",flush=True)
        try:
            pid=restore(backup,manifest) if installed else start_and_wait(False)
            (backup/"result.json").write_text(json.dumps({"status":"rolled_back","pid":pid}))
            print("Prior code restored and Discord reconnected.")
        except BaseException:
            print("Rollback needs operator attention. Backup: "+str(backup),flush=True)
            raise
        raise

def main():
    manifest=preflight()
    if "--check" in sys.argv:
        print("W7-F7 preflight passed. Five backend files and four pilot assets; no data/config overlay.")
        return
    if os.geteuid()!=0:
        raise SystemExit("Activation requires sudo; --check is read-only.")
    activate(manifest)

if __name__=="__main__":
    main()
