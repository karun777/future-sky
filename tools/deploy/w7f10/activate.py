"""W7-F10 five-file lifecycle overlay. Never stops or starts services.
--check reads source/live hashes. install/rollback require an already stopped bot.
Rollback is code-only and must precede any character reset, or follow data recovery.
"""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
from tools.character_reset_adapter import Refused, snapshot, replace, envelope, verified, offline_guard
from tools.character_reset_rehearsal import atomic

ROOT = Path(__file__).resolve().parents[3]
LIVE = Path("/opt/futuresky/bot")
STATE = Path("/opt/futuresky/backups/w7f10-lifecycle")
MANIFEST = Path(__file__).with_name("deployment-manifest.json")

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None

def check(source, live, manifest, installed=False):
    for relative, entry in manifest["files"].items():
        if sha(source / relative) != entry["source"]:
            raise Refused("Source changed: " + relative)
        if sha(live / relative) != entry["source" if installed else "live"]:
            raise Refused("Live code changed: " + relative)
    for relative, expected in manifest["pins"].items():
        if sha(live / relative) != expected:
            raise Refused("Preserved dependency changed: " + relative)

def data_hashes(root):
    result = {}
    for p in sorted(root.rglob("*")):
        if p.is_symlink():
            raise Refused("Unexpected data symlink")
        if p.is_file():
            result[str(p.relative_to(root))] = sha(p)
    return result

class Deployment:
    def __init__(self, source, live, data, state, manifest, guard):
        self.source, self.live, self.data, self.state = source, live, data, state
        self.manifest, self.guard = manifest, guard

    def __enter__(self):
        self.guard()
        if self.state.is_symlink():
            raise Refused("Unsafe backup path")
        self.state.mkdir(mode=0o700, parents=True, exist_ok=True)
        st = self.state.stat()
        if st.st_uid != os.geteuid() or st.st_mode & 0o077:
            raise Refused("Private owned backup directory required")
        fd = os.open(self.state / "lock", os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
        self.lock = os.fdopen(fd, "w")
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BaseException:
            self.lock.close()
            raise
        return self

    def __exit__(self, *args):
        self.lock.close()

    def current(self):
        return {r: snapshot(self.live / r) for r in self.manifest["files"]}

    def install(self, after_write=None):
        self.guard()
        if (self.state / "transaction.json").exists():
            raise Refused("Existing deployment: review or rollback first")
        check(self.source, self.live, self.manifest)
        before = self.current()
        after = {}
        # Code is bytes, not a JSON document.
        import base64
        for r in before:
            p = self.live / r
            metadata = before[r] or {"mode": 0o644, "uid": p.parent.stat().st_uid,
                                    "gid": p.parent.stat().st_gid}
            after[r] = dict(metadata, bytes=base64.b64encode((self.source / r).read_bytes()).decode())
        record = {"manifest": self.manifest, "before": before, "after": after,
                  "data": data_hashes(self.data), "root": str(self.live.resolve())}
        atomic(self.state / "transaction.json", envelope(record))
        for i, r in enumerate(before):
            self.guard()
            if snapshot(self.live / r) != before[r] or data_hashes(self.data) != record["data"]:
                raise Refused("Concurrent code/data change; service remains stopped")
            replace(self.live / r, after[r])
            if after_write:
                after_write(i)
        check(self.source, self.live, self.manifest, installed=True)
        if data_hashes(self.data) != record["data"]:
            raise Refused("Data changed; inspect before any restart")
        atomic(self.state / "installed.json", {"transaction": envelope(record)["sha256"]})

    def rollback(self, after_write=None):
        self.guard()
        record = verified(json.loads((self.state / "transaction.json").read_text()))
        if record["manifest"] != self.manifest or record["root"] != str(self.live.resolve()):
            raise Refused("Deployment contract changed")
        # Never roll code back over reset data or another writer's work.
        if data_hashes(self.data) != record["data"]:
            raise Refused("Data differs from deployment: recover/review data before code rollback")
        for r, expected in self.manifest["pins"].items():
            if sha(self.live / r) != expected:
                raise Refused("Preserved dependency changed")
        for r in record["before"]:
            if snapshot(self.live / r) not in (record["before"][r], record["after"][r]):
                raise Refused("Unexpected code; manual review required")
        for i, r in enumerate(record["before"]):
            self.guard()
            if data_hashes(self.data) != record["data"]:
                raise Refused("Data changed during rollback")
            if snapshot(self.live / r) not in (record["before"][r], record["after"][r]):
                raise Refused("Code changed during rollback")
            replace(self.live / r, record["before"][r])
            if after_write:
                after_write(i)
        if self.current() != record["before"] or data_hashes(self.data) != record["data"]:
            raise Refused("Rollback verification failed")
        atomic(self.state / "rolled-back.json", {"transaction": envelope(record)["sha256"]})
        # Retain original transaction and backups for operator review.

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=["check", "install", "rollback"])
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text())
    if args.operation == "check":
        check(ROOT / "bot", LIVE, manifest)
        print("Five-file source/baseline check passed. Router/dependencies pinned. No live changes.")
        return
    if os.geteuid() != 0:
        raise Refused("Privileged operator terminal required")
    with Deployment(ROOT / "bot", LIVE, Path("/opt/futuresky/data"), STATE,
                    manifest, offline_guard) as deployment:
        getattr(deployment, args.operation)()
    print("Code transaction verified. Service remains stopped; no data/configuration changed.")

if __name__ == "__main__":
    main()
