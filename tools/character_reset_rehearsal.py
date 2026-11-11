"""W7-F10 transaction rehearsal. No live adapter or production CLI.

The harness owns a new temporary directory; callers supply fictional dictionaries,
never a data-root path. This deliberately cannot attach to the running game.
Archives contain private selected records; checksums detect damage, not forgery.
"""
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import tempfile

STORES = ("characters", "lockers", "vault", "cubes")


class Refused(ValueError):
    pass


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(encoded(value)).hexdigest()


def atomic(path, value):
    fd, name = tempfile.mkstemp(dir=path.parent, prefix=".write-")
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(encoded(value))
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if os.path.exists(name):
            os.unlink(name)


class Rehearsal:
    """Single-writer fictional-store harness; close() destroys its private files."""

    def __init__(self, stores):
        if type(stores) is not dict or set(stores) != set(STORES) or any(type(v) is not dict for v in stores.values()):
            raise Refused("Expected four dictionary stores")
        self._tmp = tempfile.TemporaryDirectory(prefix="future-sky-reset-rehearsal-")
        self.root = Path(self._tmp.name)
        self.archive_dir = self.root / "archives"
        self.archive_dir.mkdir(mode=0o700)
        for name in STORES:
            atomic(self.root / (name + ".json"), stores[name])

    def close(self):
        self._tmp.cleanup()

    def read(self):
        return {name: json.loads((self.root / (name + ".json")).read_text()) for name in STORES}

    def _idle(self):
        if (self.root / "journal.json").exists():
            raise Refused("Unresolved transaction: recover before further operations")

    def _keys(self, uid):
        if not isinstance(uid, str) or not uid.isdecimal():
            raise Refused("Account ID must be a decimal string")
        return dict(zip(STORES, (uid, uid, uid, "cube_personal_" + uid)))

    def _selected(self, stores, uid):
        result = {}
        for name, key in self._keys(uid).items():
            result[name] = {"present": key in stores[name], "value": stores[name].get(key)}
        char = result["characters"]
        if char["present"] and (type(char["value"]) is not dict or str(char["value"].get("id")) != uid):
            raise Refused("Character identity mismatch")
        cube = result["cubes"]
        if cube["present"]:
            value = cube["value"]
            if (type(value) is not dict or type(value.get("owner")) is not dict
                    or str(value["owner"].get("user_id")) != uid
                    or value.get("cube_type") != "personal_cube_v0"):
                raise Refused("Personal cube ownership/schema mismatch")
        for name in ("lockers", "vault"):
            if result[name]["present"] and type(result[name]["value"]) is not dict:
                raise Refused("Unsupported personal store schema")
        return deepcopy(result)

    def _archive(self, uid, selected):
        payload = {"version": 1, "uid": uid, "selected": selected}
        checksum = digest(payload)
        path = self.archive_dir / (checksum + ".json")
        if path.exists():
            if json.loads(path.read_text()) != {"payload": payload, "sha256": checksum}:
                raise Refused("Existing archive is damaged")
        else:
            atomic(path, {"payload": payload, "sha256": checksum})
        return checksum

    def archive(self, uid):
        self._idle()
        return self._archive(uid, self._selected(self.read(), uid))

    def load_archive(self, archive_id, uid):
        if not isinstance(archive_id, str) or len(archive_id) != 64 or any(c not in "0123456789abcdef" for c in archive_id):
            raise Refused("Invalid archive identifier")
        envelope = json.loads((self.archive_dir / (archive_id + ".json")).read_text())
        payload = envelope.get("payload")
        if digest(payload) != archive_id or envelope.get("sha256") != archive_id:
            raise Refused("Archive integrity mismatch")
        if payload.get("version") != 1 or payload.get("uid") != uid:
            raise Refused("Archive version/identity mismatch")
        return deepcopy(payload["selected"])

    def plan(self, uid, restore=None):
        self._idle()
        before = self.read()
        selected = self._selected(before, uid)
        if restore is None and not selected["characters"]["present"]:
            raise Refused("No character to reset")
        desired = (self.load_archive(restore, uid) if restore else
                   {name: {"present": False, "value": None} for name in STORES})
        after = deepcopy(before)
        for name, key in self._keys(uid).items():
            if desired[name]["present"]:
                after[name][key] = deepcopy(desired[name]["value"])
            else:
                after[name].pop(key, None)
        self._selected(after, uid)
        payload = {"version": 1, "uid": uid, "before": before, "after": after,
                   "restore": restore}
        return {"payload": payload, "sha256": digest(payload)}

    def apply(self, plan, after_write=None):
        self._idle()
        payload = plan["payload"]
        if plan["sha256"] != digest(payload) or payload.get("version") != 1:
            raise Refused("Changed or unsupported plan")
        # Recompute to prevent a crafted plan from altering unrelated entries.
        expected = self.plan(payload["uid"], payload["restore"])
        if expected != plan:
            raise Refused("Stale or altered plan")
        before_archive = self._archive(payload["uid"], self._selected(payload["before"], payload["uid"]))
        journal = {"version": 1, "before": payload["before"], "after": payload["after"],
                   "before_archive": before_archive}
        atomic(self.root / "journal.json", {"payload": journal, "sha256": digest(journal)})
        for index, name in enumerate(STORES):
            atomic(self.root / (name + ".json"), payload["after"][name])
            if after_write:
                after_write(index)
        if self.read() != payload["after"]:
            raise Refused("Post-write verification failed; recovery required")
        self._clear_journal()
        return before_archive

    def _clear_journal(self):
        (self.root / "journal.json").unlink()
        directory = os.open(self.root, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)

    def recover(self):
        path = self.root / "journal.json"
        envelope = json.loads(path.read_text())
        journal = envelope["payload"]
        if envelope["sha256"] != digest(journal) or journal.get("version") != 1:
            raise Refused("Journal integrity/version mismatch")
        current = self.read()
        # Validate every store before any rollback write. Unexpected writers block.
        for name in STORES:
            if current[name] not in (journal["before"][name], journal["after"][name]):
                raise Refused("Unexpected store content; manual recovery required")
        for name in STORES:
            atomic(self.root / (name + ".json"), journal["before"][name])
        if self.read() != journal["before"]:
            raise Refused("Rollback verification failed")
        self._clear_journal()
