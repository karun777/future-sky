"""Stopped-service character reset adapter. Never stops/starts the bot itself.

Private archives and journals contain personal data. CLI targets the canonical
server only; tests instantiate Adapter against temporary fictional stores.
"""
import argparse
import base64
from copy import deepcopy
import fcntl
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import tempfile

from tools.character_reset_rehearsal import Refused, digest, encoded, atomic

FILES = {
    "characters": "characters/characters.json",
    "lockers": "storage/lockers.json",
    "vault": "storage/efiishent_vault.json",
    "cubes": "storage/cubes.json",
    "receipt": "storage/reset_run_bindings.json",
}
LIVE = Path("/opt/futuresky/data")
STATE = Path("/home/efiishent/.local/state/future-sky/character-reset")


def account(value):
    if not isinstance(value, str) or not value.isascii() or not value.isdecimal() or str(int(value)) != value or int(value) <= 0:
        raise Refused("Expected canonical numeric account ID")
    return value


def envelope(payload):
    return {"payload": payload, "sha256": digest(payload)}


def verified(value):
    if not isinstance(value, dict) or set(value) != {"payload", "sha256"} or digest(value["payload"]) != value["sha256"]:
        raise Refused("Integrity check failed")
    return value["payload"]


def sync_dir(path):
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def snapshot(path):
    if path.is_symlink():
        raise Refused("Symlink refused")
    if not path.exists():
        return None
    info = path.stat()
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise Refused("Expected regular, unlinked file")
    return {"bytes": base64.b64encode(path.read_bytes()).decode(),
            "mode": stat.S_IMODE(info.st_mode), "uid": info.st_uid, "gid": info.st_gid}


def unpack(snap):
    return base64.b64decode(snap["bytes"], validate=True)


def document(snap):
    if snap is None:
        return None
    result = json.loads(unpack(snap))
    if not isinstance(result, dict):
        raise Refused("Expected dictionary store")
    return result


def updated(old, value, parent):
    raw = encoded(value)
    if old and document(old) == value:
        return old
    info = parent.stat()
    return {"bytes": base64.b64encode(raw).decode(),
            "mode": old["mode"] if old else 0o600,
            "uid": old["uid"] if old else info.st_uid,
            "gid": old["gid"] if old else info.st_gid}


def replace(path, snap):
    if snap is None:
        path.unlink(missing_ok=True)
        sync_dir(path.parent)
        return
    fd, name = tempfile.mkstemp(dir=path.parent, prefix=".character-reset-")
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(unpack(snap))
            os.fchown(stream.fileno(), snap["uid"], snap["gid"])
            os.fchmod(stream.fileno(), snap["mode"])
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
        sync_dir(path.parent)
    finally:
        if os.path.exists(name):
            os.unlink(name)


class Adapter:
    def __init__(self, root, state, guard, contract=None):
        self.root, self.state, self.guard = Path(root), Path(state), guard
        self.lock = None
        self.contract = contract or (lambda: {})

    def __enter__(self):
        if self.root.resolve() != self.root or self.state.resolve() != self.state:
            raise Refused("Use canonical paths, without symlinks")
        if self.state == self.root or self.root in self.state.parents:
            raise Refused("Private state must be outside data root")
        self.guard()
        self.state.mkdir(parents=True, mode=0o700, exist_ok=True)
        info = self.state.stat()
        if info.st_uid != os.geteuid() or stat.S_IMODE(info.st_mode) != 0o700:
            raise Refused("Private state must be owned by operator, mode 0700")
        fd = os.open(self.state / "lock", os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
        self.lock = os.fdopen(fd, "r+")
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BaseException:
            self.lock.close()
            raise Refused("Another reset adapter holds the lock")
        return self

    def __exit__(self, *args):
        self.lock.close()

    def check(self, idle=True):
        if self.lock is None or self.lock.closed:
            raise Refused("Adapter lock required")
        self.guard()
        if idle and (self.state / "journal.json").exists():
            raise Refused("Unresolved journal; recover before further work")
        for relative in FILES.values():
            path = self.root / relative
            if path.resolve() != path or not path.parent.is_dir():
                raise Refused("Store path redirected or parent missing")

    def read(self):
        return {name: snapshot(self.root / relative) for name, relative in FILES.items()}

    def protected(self):
        result = {}
        for path in sorted(self.root.rglob("*")):
            if path.is_symlink():
                raise Refused("Unexpected symlink inside canonical data")
            if path.is_file() and str(path.relative_to(self.root)) not in FILES.values():
                with path.open("rb") as stream:
                    checksum = hashlib.file_digest(stream, "sha256").hexdigest()
                result[str(path.relative_to(self.root))] = checksum
        return result

    def selected(self, snaps, uid):
        result = {}
        keys = {"characters": uid, "lockers": uid, "vault": uid, "cubes": "cube_personal_" + uid}
        for name, key in keys.items():
            store = document(snaps[name])
            if store is None:
                raise Refused("Required store missing")
            result[name] = {"present": key in store, "value": deepcopy(store.get(key))}
        char = result["characters"]
        if char["present"] and (not isinstance(char["value"], dict) or str(char["value"].get("id")) != uid):
            raise Refused("Character/account mismatch")
        cube = result["cubes"]
        if cube["present"]:
            value = cube["value"]
            if (not isinstance(value, dict) or value.get("id") != keys["cubes"]
                    or value.get("cube_type") != "personal_cube_v0"
                    or value.get("owner") != {"type": "player", "user_id": uid}):
                raise Refused("Personal cube identity/schema mismatch")
        for name in ("lockers", "vault"):
            if result[name]["present"] and not isinstance(result[name]["value"], dict):
                raise Refused("Unsupported holdings")
        for key, value in document(snaps["cubes"]).items():
            if key == keys["cubes"] or not isinstance(value, dict):
                continue
            if key == uid or (value.get("cube_type") == "personal_cube_v0"
                             and str(value.get("owner", {}).get("user_id")) == uid):
                raise Refused("Additional personal cube record needs review")
        receipt = document(snaps["receipt"])
        if receipt is not None and snaps["receipt"]["mode"] != 0o600:
            raise Refused("Existing reset receipt must be private, mode 0600")
        if receipt is not None:
            # Same strict schema checker as guided creation, without filesystem I/O.
            validate_receipt(receipt, uid, document(snaps["characters"]))
        bindings = receipt["bindings"] if receipt else {}
        result["receipt"] = {"present": uid in bindings, "value": deepcopy(bindings.get(uid)),
                             "file_present": snaps["receipt"] is not None}
        return result

    def archive(self, uid, snaps):
        payload = {"version": 1, "uid": uid, "selected": self.selected(snaps, uid)}
        value = envelope(payload)
        key = value["sha256"]
        self.save_private(key + ".archive.json", value)
        return key

    def save_private(self, name, value):
        path = self.state / name
        if path.is_symlink():
            raise Refused("Private artifact symlink")
        if path.exists():
            if json.loads(path.read_text()) != value:
                raise Refused("Existing private artifact differs")
        else:
            atomic(path, value)

    def load_archive(self, key, uid):
        if len(key) != 64 or any(c not in "0123456789abcdef" for c in key):
            raise Refused("Invalid archive ID")
        payload = verified(json.loads((self.state / (key + ".archive.json")).read_text()))
        if digest(payload) != key or payload["version"] != 1 or payload["uid"] != uid:
            raise Refused("Archive identity mismatch")
        return payload["selected"]

    def plan(self, uid, expected_name, restore=None):
        self.check()
        account(uid)
        before = self.read()
        selected = self.selected(before, uid)
        char = selected["characters"]["value"]
        if not restore and not selected["characters"]["present"]:
            raise Refused("No character to reset")
        if char is not None and char.get("name") != expected_name:
            raise Refused("Expected character name differs; account ID remains selector")
        desired = self.load_archive(restore, uid) if restore else {
            name: {"present": False, "value": None} for name in FILES}
        if not restore:
            channel = char.get("run_channel_id")
            channel = account(str(channel))
            binding = {"run_channel_id": channel, "run_seeded_channel_id": char.get("run_seeded_channel_id")}
            if selected["receipt"]["present"] and selected["receipt"]["value"] != binding:
                raise Refused("Existing receipt conflicts with saved channel")
            desired["receipt"] = {"present": True, "value": binding}
        after = deepcopy(before)
        for name, key in (("characters", uid), ("lockers", uid), ("vault", uid), ("cubes", "cube_personal_" + uid)):
            store = document(before[name])
            if desired[name]["present"]:
                store[key] = deepcopy(desired[name]["value"])
            else:
                store.pop(key, None)
            after[name] = updated(before[name], store, (self.root / FILES[name]).parent)
        receipt = document(before["receipt"]) or {"version": 1, "bindings": {}}
        if desired["receipt"]["present"]:
            receipt["bindings"][uid] = deepcopy(desired["receipt"]["value"])
        else:
            receipt["bindings"].pop(uid, None)
        after["receipt"] = (None if not receipt["bindings"] and not desired["receipt"]["present"] and not desired["receipt"].get("file_present")
                            else updated(before["receipt"], receipt, (self.root / FILES["receipt"]).parent))
        self.selected(after, uid)
        if desired["receipt"]["present"]:
            validate_receipt(receipt, uid, document(after["characters"]))
        payload = {"version": 1, "root": str(self.root), "uid": uid, "expected_name": expected_name,
                   "restore": restore, "before": before, "after": after, "protected": self.protected(),
                   "runtime_contract": self.contract()}
        # Re-read after hashing to reject an observed moving snapshot.
        if self.read() != before:
            raise Refused("Stores changed during planning")
        return envelope(payload)

    def apply(self, plan, after_write=None):
        self.check()
        payload = verified(plan)
        expected = self.plan(payload["uid"], payload["expected_name"], payload["restore"])
        if expected != plan:
            raise Refused("Stale or altered plan")
        key = self.archive(payload["uid"], payload["before"])
        journal = envelope({"version": 1, "plan": plan, "archive": key})
        atomic(self.state / "journal.json", journal)
        for index, name in enumerate(FILES):
            self.check(idle=False)
            if snapshot(self.root / FILES[name]) != payload["before"][name]:
                raise Refused("Concurrent store change; recovery required")
            if self.protected() != payload["protected"]:
                raise Refused("Protected data changed; recovery required")
            if payload["before"][name] != payload["after"][name]:
                replace(self.root / FILES[name], payload["after"][name])
            if after_write:
                after_write(index)
        self.check(idle=False)
        if self.read() != payload["after"] or self.protected() != payload["protected"]:
            raise Refused("Post-write validation failed; recovery required")
        self.finish(journal, "applied")
        return key

    def finish(self, journal, status):
        self.save_private(journal["sha256"] + "." + status + ".json",
                          envelope({"status": status, "journal": journal}))
        (self.state / "journal.json").unlink()
        sync_dir(self.state)

    def recover(self, after_write=None):
        self.check(idle=False)
        journal = json.loads((self.state / "journal.json").read_text())
        body = verified(journal)
        payload = verified(body["plan"])
        if body["version"] != 1 or payload["root"] != str(self.root):
            raise Refused("Journal version/root mismatch")
        self.load_archive(body["archive"], payload["uid"])
        current = self.read()
        if self.protected() != payload["protected"]:
            raise Refused("Protected files changed; manual recovery required")
        for name in FILES:
            if current[name] not in (payload["before"][name], payload["after"][name]):
                raise Refused("Unexpected writer; no rollback performed")
        for index, name in enumerate(FILES):
            self.check(idle=False)
            if snapshot(self.root / FILES[name]) not in (payload["before"][name], payload["after"][name]):
                raise Refused("Concurrent change during recovery")
            if snapshot(self.root / FILES[name]) != payload["before"][name]:
                replace(self.root / FILES[name], payload["before"][name])
            if after_write:
                after_write(index)
        if self.read() != payload["before"] or self.protected() != payload["protected"]:
            raise Refused("Rollback verification failed")
        self.finish(journal, "recovered")


def validate_receipt(receipt, uid, characters):
    # Keep the runtime and adapter schema logic identical.
    from fsbot.reset_binding import validate_reset_binding
    validate_reset_binding(receipt, {"id": uid}, characters)


def offline_guard():
    result = subprocess.run(["systemctl", "show", "futuresky-bot.service",
                             "-p", "ActiveState", "-p", "SubState", "-p", "MainPID"],
                            check=True, capture_output=True, text=True)
    values = dict(line.split("=", 1) for line in result.stdout.splitlines())
    if values != {"MainPID": "0", "ActiveState": "inactive", "SubState": "dead"}:
        raise Refused("Service must be explicitly stopped and inactive/dead")
    # Detect detached bot processes and open writable descriptors under live data.
    # Maintenance must also exclude external writers; this is not a global lock.
    for proc in Path("/proc").iterdir():
        if not proc.name.isdecimal() or int(proc.name) == os.getpid():
            continue
        try:
            cmd = (proc / "cmdline").read_bytes().replace(b"\0", b" ")
            if (b"/opt/futuresky/bot/run_bot.py" in cmd
                    or (b"run_bot.py" in cmd and (proc / "cwd").resolve() == Path("/opt/futuresky/bot"))):
                raise Refused("Detached bot process exists")
            for fd in (proc / "fd").iterdir():
                target = os.readlink(fd)
                if target.startswith(str(LIVE) + "/"):
                    info = (proc / "fdinfo" / fd.name).read_text()
                    flags = next(line.split()[1] for line in info.splitlines() if line.startswith("flags:"))
                    if int(flags, 8) & os.O_ACCMODE:
                        raise Refused("Writable live-data descriptor exists")
        except (FileNotFoundError, ProcessLookupError):
            continue
        except PermissionError:
            # Root invocation is required below so this is unexpected and blocking.
            raise Refused("Cannot inspect processes for writers")


def runtime_check():
    from dotenv import dotenv_values
    import shlex
    for path in (Path("/opt/futuresky/bot/.env"), Path("/opt/futuresky/web-portal.env")):
        if path.exists() and dotenv_values(path).get("FS_RESET_ROOMS_ON_BOOT") == "1":
            raise Refused("World reset on restart is enabled")
    settings = subprocess.run(["systemctl", "show", "futuresky-bot.service",
                               "-p", "Environment", "--value"],
                              check=True, capture_output=True, text=True).stdout
    if "FS_RESET_ROOMS_ON_BOOT=1" in shlex.split(settings):
        raise Refused("World reset on restart is enabled in service environment")
    source = Path(__file__).resolve().parents[1] / "bot"
    hashes = {}
    for relative in ("fsbot/cogs/arrival.py", "fsbot/cogs/core.py", "fsbot/storage.py",
                     "fsbot/config.py", "fsbot/reset_binding.py", "fsbot/cogs/router.py"):
        live = Path("/opt/futuresky/bot") / relative
        if not live.is_file() or live.read_bytes() != (source / relative).read_bytes():
            raise Refused("Reviewed runtime not installed: " + relative)
        hashes[relative] = hashlib.sha256(live.read_bytes()).hexdigest()
    hashes["adapter"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    return hashes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=["plan", "apply", "recover"])
    parser.add_argument("--account")
    parser.add_argument("--expect-name")
    parser.add_argument("--restore")
    parser.add_argument("--plan-id")
    args = parser.parse_args()
    if os.geteuid() != 0:
        raise Refused("Operator root terminal required for process visibility and metadata preservation")
    with Adapter(LIVE, STATE, offline_guard, contract=runtime_check) as adapter:
        if args.operation == "recover":
            adapter.recover()
            print("Rollback verified. Service remains stopped; review before resuming.")
            return
        runtime_check()
        if args.operation == "plan":
            if not args.account or not args.expect_name:
                raise Refused("--account and --expect-name required")
            plan = adapter.plan(args.account, args.expect_name, args.restore)
            adapter.save_private(plan["sha256"] + ".plan.json", plan)
            print("Private plan ID:", plan["sha256"])
            print("No data changed. Review archive scope, channel proof and maintenance impact before apply.")
        else:
            key = args.plan_id or ""
            if len(key) != 64 or any(c not in "0123456789abcdef" for c in key):
                raise Refused("Exact reviewed --plan-id required")
            plan = json.loads((STATE / (key + ".plan.json")).read_text())
            if plan.get("sha256") != key:
                raise Refused("Plan ID mismatch")
            archived = adapter.apply(plan)
            print("Transaction verified. Private before-archive:", archived)
            print("Service remains stopped. Review time-sensitive restored state and verify safe restart configuration.")
        print("Other players' persistent records and protected files verified unchanged.")


if __name__ == "__main__":
    main()

