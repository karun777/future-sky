"""W6-F10 two-asset release: check/verify are read-only; install/rollback are static-only.

No service control, OAuth, player-store access or reset/restore operations.
The CLI uses fixed production paths. Tests use temporary roots explicitly.
"""
import argparse
import base64
from contextlib import contextmanager
import fcntl
import hashlib
import json
import os
from pathlib import Path

from tools.character_reset_adapter import (
    Refused, snapshot, replace, envelope, verified, runtime_code_check,
)
from tools.character_reset_rehearsal import atomic

ROOT = Path(__file__).resolve().parents[3]
LIVE = Path("/opt/futuresky")
STATE = LIVE / "backups/w6f10-static"
PREFIX = "assets/experiments/w6-f8/live/"
SOURCES = {
    PREFIX + "game.js": "tools/authoring/w6f8/live/game.js",
    PREFIX + "index.html": "tools/authoring/w6f8/live/index.html",
}
ORDER = tuple(SOURCES)  # Publish script first, cache-versioned HTML second.
RUNTIME = "tools/deploy/w7f10/runtime-manifest.json"
PREVIOUS = "tools/deploy/w7f9_return/deployment-manifest.json"
MANIFEST = "tools/deploy/w6f10/deployment-manifest.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class StaticRelease:
    def __init__(self, repo=ROOT, live=LIVE, state=STATE):
        self.repo, self.live, self.state = Path(repo), Path(live), Path(state)
        self.manifest = json.loads((self.repo / MANIFEST).read_text())

    def guard(self):
        m = self.manifest
        if set(m["files"]) != set(ORDER):
            raise Refused("Only the two reviewed HUD assets may change")
        for path, key in ((RUNTIME, "runtime_sha256"), (PREVIOUS, "previous_sha256")):
            if sha(self.repo / path) != m["basis"][key]:
                raise Refused("Reviewed contract changed: " + path)
        previous = json.loads((self.repo / PREVIOUS).read_text())
        baseline = {r: entry["source"] for r, entry in previous["files"].items()}
        baseline.update(previous["pins"])
        if m["pins"] != {r: h for r, h in baseline.items() if r not in ORDER}:
            raise Refused("Preserved dependency set changed")
        for relative, source in SOURCES.items():
            entry = m["files"][relative]
            if (entry["source_path"] != source or entry["live"] != baseline[relative]
                    or sha(self.repo / source) != entry["source"]):
                raise Refused("Reviewed asset source/baseline changed: " + relative)
            path = self.live / relative
            for part in (path, *path.parents):
                if part.is_symlink():
                    raise Refused("Symlink in asset path")
                if part == self.live:
                    break
            if snapshot(path) is None:
                raise Refused("Existing regular asset required")
        tag = "game.js?v=w6f10-" + m["files"][ORDER[0]]["source"][:12]
        if tag not in (self.repo / SOURCES[ORDER[1]]).read_text():
            raise Refused("HTML cache version does not match the reviewed script")
        for relative, expected in m["pins"].items():
            if sha(self.live / relative) != expected:
                raise Refused("Preserved dependency changed: " + relative)
        # Existing bot-only lifecycle contract stays byte-for-byte unchanged.
        return runtime_code_check(repo=self.repo, live_root=self.live / "bot",
                                  manifest_path=self.repo / RUNTIME)

    def check(self, installed=False):
        hashes = self.guard()
        key = "source" if installed else "live"
        for relative, entry in self.manifest["files"].items():
            if sha(self.live / relative) != entry[key]:
                raise Refused("Asset differs from expected " + key + ": " + relative)
        return hashes

    @contextmanager
    def locked(self):
        self.guard()
        if self.state.is_symlink():
            raise Refused("Unsafe transaction path")
        self.state.mkdir(mode=0o700, parents=True, exist_ok=True)
        st = self.state.stat()
        if st.st_uid != os.geteuid() or st.st_mode & 0o077:
            raise Refused("Private owned transaction directory required")
        fd = os.open(self.state / "lock", os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
        with os.fdopen(fd, "w") as lock:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            yield

    def current(self):
        return {r: snapshot(self.live / r) for r in ORDER}

    def known(self, record):
        for r, current in self.current().items():
            if current not in (record["before"][r], record["after"][r]):
                raise Refused("Unexpected asset change; operator review required: " + r)

    def install(self, after_write=None):
        with self.locked():
            journal = self.state / "transaction.json"
            if journal.exists():
                raise Refused("Existing transaction: review or rollback; do not reinstall")
            self.check()
            before = self.current()
            after = {
                r: dict(before[r], bytes=base64.b64encode(
                    (self.repo / SOURCES[r]).read_bytes()).decode()) for r in ORDER
            }
            # Bind the captured bytes, not just an earlier path check.
            for r in ORDER:
                for captured, key in ((before[r], "live"), (after[r], "source")):
                    digest = hashlib.sha256(base64.b64decode(captured["bytes"], validate=True)).hexdigest()
                    if digest != self.manifest["files"][r][key]:
                        raise Refused("Asset changed during capture: " + r)
            record = {"manifest": self.manifest, "root": str(self.live.resolve()),
                      "before": before, "after": after}
            atomic(journal, envelope(record))  # Durable bytes/metadata before any asset write.
            for i, r in enumerate(ORDER):
                self.guard()
                self.known(record)
                if snapshot(self.live / r) != before[r]:
                    raise Refused("Asset changed before installation: " + r)
                replace(self.live / r, after[r])
                if after_write:
                    after_write(i)
            self.check(installed=True)
            atomic(self.state / "installed.json", {"transaction": envelope(record)["sha256"]})

    def rollback(self, after_write=None):
        with self.locked():
            record = verified(json.loads((self.state / "transaction.json").read_text()))
            if record["manifest"] != self.manifest or record["root"] != str(self.live.resolve()):
                raise Refused("Transaction contract or target changed")
            self.known(record)  # Check both before restoring either.
            for i, r in enumerate(reversed(ORDER)):
                self.guard()
                self.known(record)
                replace(self.live / r, record["before"][r])
                if after_write:
                    after_write(i)
            self.check()
            if self.current() != record["before"]:
                raise Refused("Rollback metadata verification failed")
            atomic(self.state / "rolled-back.json", {"transaction": envelope(record)["sha256"]})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=["check", "verify", "install", "rollback"])
    args = parser.parse_args()
    release = StaticRelease()
    if args.operation in {"check", "verify"}:
        hashes = release.check(installed=args.operation == "verify")
        print(f"Two HUD assets and {len(release.manifest['pins'])} preserved pins verified; "
              f"bot runtime contract unchanged ({len(hashes)} entries). Read-only.")
        return
    if os.geteuid() != 0:
        raise Refused("Privileged operator terminal required for static installation/rollback")
    getattr(release, args.operation)()
    print("Two-asset static transaction verified. No service control or player-data access.")
    print("Retained transaction: " + str(STATE))


if __name__ == "__main__":
    main()
