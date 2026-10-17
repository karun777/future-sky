# W7-F1 — What Is Actually Running?

Home: W7 Engine. Status: COMPLETE — bounded live operational checkpoint.
Date: 17 October 2026, approximately 16:18 AWST.
Return: [Wing Index](../WING_INDEX.md).
Repository reference: d9f33b6579b0f7abf4d2bfe9b695c84850f19777.
No deployment, service restart, permissions change, world-state repair or asset move performed.

## The running node

Host: neptunelounge.
Verified access: Desktop Commander on Karun's MacBook → existing SSH alias neptunelounge, account efiishent.
This documents the working access route without recording keys, credentials or account secrets.

| Component | Direct observation | Practical boundary |
| --- | --- | --- |
| Future Sky bot | futuresky-bot.service active/running, PID 799778; started 12:50:26 AWST. | Service liveness is not a complete Discord gameplay test. |
| Runtime interpreter | /opt/futuresky/.venv/bin/python; Python 3.13.5. | Rebuilding the entire dependency environment was not tested. |
| Entrypoint / cwd | /opt/futuresky/bot/run_bot.py; cwd /opt/futuresky/bot; service user efiishent. | This is the live path, not the uploaded historical bot.py files. |
| nginx | active/running; listeners on 80/443. | Multiple sites share the daemon; only Future Sky routing was scoped here. |
| SSH | ssh.service active/running; TCP listener 777 observed; authenticated connection worked. | External reachability, firewall/key policy and every network path were not audited. |
| fail2ban | active/running. | Does not establish complete security posture. |
| Docker | docker.service active/running. | Docker API query denied for this account; running/stopped containers and their services remain unknown. |
| PostgreSQL / Redis / Lavalink named systemd units | postgresql.service, redis-server.service and lavalink.service returned not-found/inactive. | This does not establish global absence: container inventory is unknown and other unit names/hosts were not exhaustively searched. |

No failed systemd units appeared in the scoped command output. The active bot is using the inspected JSON Storage path; the archived operations document's database/audio service list is not proof those are active dependencies now.

## Code, data and documentation are at different checkpoints

Runtime checkout HEAD: **937c007a2981d10b8e1230f293c85b6c72750425**, main, global Feather 54.

At inspection its cached origin/main was d9f33b6579b0f7abf4d2bfe9b695c84850f19777, 22 commits ahead of runtime HEAD. A git diff of HEAD against that reference under bot/ returned no paths. The worktree status also showed no bot-source modifications. Thus the inspected tracked bot source tree matches that main reference despite different commit identities. This is file/source evidence, not direct introspection of every object in process memory.

Visible differences:

- Live modified data: characters, items, rooms, room baseline and clock.
- Documentation/test overlays from this eight-wing pass; known added files are expected to appear modified/untracked relative to older HEAD.
- Existing Compass and Tiny Book image directories and pre-compass data copies are untracked relative to runtime HEAD.
- HEAD-to-main tracked differences are item/room data, docs and the new tests; there is no bot/ source delta at this checkpoint.

Do not run a blanket pull/reset/restore/stash to tidy this checkout. Each state category must be reconciled deliberately before future deployment.

[W8-F2](W8-F2_BRING_THE_DRAGONS_MEMORY_HOME.md) records the intentional documentation overlay and [Wing Index](../WING_INDEX.md) provides the current return route. Source availability in Git, documentation sync and runtime deployment are separate facts.

## Persistent truth and delivery paths

| Path | Role established by current evidence |
| --- | --- |
| /opt/futuresky/bot/data → /opt/futuresky/data | Symlink resolves the bot's relative data paths. |
| data/characters/characters.json | Shared account-character state. |
| data/rooms/rooms.json | Configured persistent room store; baseline and duplicates remain separate. |
| data/items/items.json | Current item definitions; live modifications must be preserved. |
| data/time/, data/comet/, data/astrology/, data/fields/ | Temporal and derived world stores traced in W5. |
| data/events/event_history.jsonl | Durable event-history ledger; 231,214,222 bytes at inspection, modified recently. |
| /var/www/html | nginx root for future-sky.net/www.future-sky.net in the readable enabled site config. |
| /var/www/html/index.html and feed7.html | Actual website files present outside the inspected project source paths. |
| /var/www/html/assets → /opt/futuresky/assets | Public asset route is a symlink into project assets. |

The direct asset relationship matters: changing an asset under /opt/futuresky/assets can affect public delivery without a bot restart or separate build step. Conversely, committing a file elsewhere does not automatically deploy it.

Read-only HTTP requests returned 200 text/html for https://future-sky.net/ (6,298 bytes) and /feed7.html (12,658 bytes). W6-F1 supplies the separate image-byte delivery checks. This is not a browser/UI or audio test.

The metadata inventory contained duplicate room/profile files and archived/import utilities. Their presence does not supersede current configured authority or authorise a migration.

## Backup and recovery evidence

/opt/futuresky/backups contained 15 directories at this checkpoint: feather36 plus the recent documentation/test-overlay backup directories. The newer directories retain previous documents and source manifests from this session. They are useful change-local rollback evidence, not a verified disaster-recovery system.

The archived [operations runbook](../archive/operational-reference/FUTURE_SKY_OPERATIONS_v1.0.md) labels broad backup coverage as target state. It is not evidence that source, changing JSON, event history, website files, assets and service configuration are all captured and restorable.

No Future Sky-specific job was identified in the inspected system timer list or readable system cron file references. The user-crontab query returned no usable schedule evidence. Root-only schedules, external/off-host backups and restore capability remain unverified.

Free space under the project filesystem was approximately 119.3 GB at inspection. This does not establish backup sufficiency. Event-history retention/rotation remains an open issue recorded by the Atlas.

## Verification boundary

Read service metadata, process entry/cwd, selected TCP listeners, runtime/interpreter/repository identity, diff/status, readable nginx root/symlink configuration, relevant file metadata, backup directory names, accessible schedules and HTTP responses. Docker inventory was denied; no elevation or workaround attempted.

No secrets, complete environment, credential-bearing unit configuration or character content is copied into this record. No whole-database/container audit, restore, firewall change, deployment or service restart.

## Parked return and next candidate

Reached: working operational topology, real paths, code/data/doc divergence, public asset coupling and recovery evidence recorded.
Open: dependency/container visibility, reproducible environment, full backup coverage, recovery procedure and intentional future deployment reconciliation.
W7 completed count: 1. All other wings remain parked at 2 each.
Candidate W7-F2, not activated: Recovery Capsule — capture a narrowly scoped recovery set with provenance, restore it into a disposable directory and compare bytes; distinguish that rehearsal from a coherent full-world snapshot or disaster recovery. No live restore.
