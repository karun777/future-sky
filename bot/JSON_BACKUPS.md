# Future Sky — JSON Backups (Operational Contract)

_Last updated: 2026-01-17_

This is a **ship-stabiliser**: it protects Future Sky’s JSON-authoritative runtime from accidental corruption,
partial writes, or bad edits.

This is **not** a new gameplay system. It is crash protection.

---

## What gets backed up

Everything under:

- `bot/data/**.json`

Backups are stored under:

- `bot/data/_backups/<timestamp>_<reason>/`

Each backup includes a `manifest.txt` with sha256 hashes of every JSON file inside the snapshot.

---

## Retention

Default: keep last **10** backups.

Override with env var (server shell):

- `FS_BACKUP_KEEP=25`

---

## When to take backups

### Required (minimum)
- Before any manual edit of JSON on server
- Before deploying new bot code that changes persistence behaviour
- After you confirm the bot boots cleanly and `!time` works

### Recommended (best practice)
- On every successful bot boot (reason: `boot`)
- On every “write batch” (if/when we hook into `storage.py`)

---

## Commands

Run from bot root:

- `/home/karun777/futuresky/bot`

### Create a backup
```bash
chmod +x json_backup.sh
./json_backup.sh --reason manual
```

### Restore a backup (with safety backup + JSON validation)
```bash
chmod +x json_restore.sh
./json_restore.sh data/_backups/<timestamp_reason>
```

---

## Minimal integration (next optional step)

We can make backups automatic by calling `./json_backup.sh --reason boot` from the bot startup path,
or (better) by adding a small hook inside `fsbot/storage.py` so that “pre-write” snapshots happen before
a save batch.

If/when enabled, we will:
- Document it in DEV_STATE.md and OPS_STATE.md
- Keep it read-only and low-risk (no extra dependencies)
