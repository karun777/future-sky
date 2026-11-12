# W6-F10 — two-asset static delivery

Status: INSTALLED AND VERIFIED, 12 November 2026, 22:05–22:09 AWST. Feather unsealed.
Operator installation was followed by independent installed/public hash checks
and passive authorised HUD review. Do not rerun installation. Use verify below.
Read [the feather checkpoint](../../../docs/wings/W6-F10_ONE_CLEAR_WARNING.md).

Only the installed assets below change:
- assets/experiments/w6-f8/live/game.js
- assets/experiments/w6-f8/live/index.html

The manifest binds the reviewed sources, exact installed baselines and 139 preserved
code/asset pins, including the live router, frame.js and frame.css. Only these two
paths can enter the transaction. Script installs first, cache-versioned HTML second;
rollback restores HTML first and script second. The source cache tag is
game.js?v=w6f10-b41f6e1f1619.

This is a static release with no service stop/start, configuration change or player
store access. Normal gameplay may continue. Old and new scripts use the same API and
server gates. Asset replacement is atomic per file, not a simultaneous two-file
swap. Existing tabs need a reload to acquire the corrected client.

## Runtime reconciliation

The W7-F10 current bot-only runtime remains contract version 3 with SHA-256
74a2c678be786b41ed03fc194c833e233161604e565de3e275d0833ded78327e.
It intentionally excludes static HUD assets. Its 140-entry verification still
passes and is required by this package. No lifecycle schema, reset/restore plan,
private archive, reset receipt or historical deployment manifest is modified.

The earlier W7-F9 return package's static pins remain historical. After this
release, its all-assets verification will correctly see changed static files.
Use this package for the current static contract and the unchanged W7-F10 runtime
for bot-only verification; do not rerun old packages.

## Current read-only verification

From /home/efiishent/future-sky-worktrees/w7-f8:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. /opt/futuresky/.venv-web-pilot-20261029/bin/python -m tools.deploy.w6f10.activate verify
```

Both new assets, 139 preserved pins and the 140-entry runtime passed after install.
Public HTML/script hashes and the cache tag matched. The ordinary HUD loaded the
new client without page scrolling or browser errors; bot PID 1037793 stayed active.
See the feather checkpoint for the screenshot and evidence limits.

## Historical read-only preflight

From /home/efiishent/future-sky-worktrees/w7-f8:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. /opt/futuresky/.venv-web-pilot-20261029/bin/python -m tools.deploy.w6f10.activate check
```

This makes no backup or live changes. It checks source/cache version, both installed
baselines, every preserved pin and the bot runtime. Missing files, symlinks, changed
sources or contract drift block installation.

## Completed operator activation — retained procedure

The accepted installation used the following command. It is recorded for audit;
do not rerun it against the retained transaction:

```sh
sudo bash /home/efiishent/future-sky-worktrees/w7-f8/tools/deploy/w6f10/install.sh
```

The wrapper runs check, install and verify. It does not restart the bot or nginx.
A private owned transaction directory at /opt/futuresky/backups/w6f10-static retains
the original asset bytes, modes and ownership, their reviewed replacements and an
integrity-checked journal. It contains no character records. A lock prevents a
second transaction using this directory. Existing transactions are never overwritten.

After successful install, independently check public HTML/cache tag and script
bytes, then reload the existing authorised HUD and verify the ordinary window.
Do not manufacture a live encounter, reset a character, choose a story option,
send Discord messages or expand access for this presentation check.

## Interruption and rollback

On error the wrapper stops. Retain the transaction and inspect the failure; do not
rerun install or delete its journal. Exact interrupted and completed transactions
can be rolled back with:

```sh
cd /home/efiishent/future-sky-worktrees/w7-f8
sudo env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. /opt/futuresky/.venv-web-pilot-20261029/bin/python -m tools.deploy.w6f10.activate rollback
```

Then run read-only check. Rollback verifies both files are recognised before
restoring either, restores exact bytes/metadata and preserves any subsequent player
progress because it never reads or writes those stores. Unexpected asset or pinned
code changes block rollback for operator review. An interrupted rollback can retry.
The transaction remains retained; a subsequent release needs a fresh reviewed
transaction and cache version, rather than reusing this installation blindly.

## Rehearsal and checks

483 Python tests passed, including 12 new static-package/transaction tests.
This includes changed-source/baseline/pin refusal, changes during byte capture,
private journal failure, corruption, lock/duplicate-install refusal, exact
metadata, interruptions and preservation of fictional later player progress.
Old cache-version test assumptions now bind to the static release rather than
requiring immutable historical static pins to equal future source.

[Exact-package rehearsal result](rehearsal-20261112.json) used temporary copies of
141 installed code/asset files, plus newly created fictional state sentinels.
No production character store, archive or reset receipt was copied or read.
Installation, rollback, interruption after either install write and rollback retry
passed. The existing 140-entry runtime contract passed before and after. Temporary
copies were removed and production code/asset hashes remained unchanged.

The pre-install rehearsal was run from the checkout with the command below.
It expects the original live baseline, so do not rerun it after installation:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. /opt/futuresky/.venv-web-pilot-20261029/bin/python -m tools.deploy.w6f10.rehearse
```

At rehearsal, production remained unmodified and bot PID 1037793 stayed active.
The later installation and independent checks are recorded above. Neither step
establishes new-account onboarding, reset/restore acceptance or a feather seal.
