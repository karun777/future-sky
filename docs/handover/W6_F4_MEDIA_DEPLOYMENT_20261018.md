# W6-F4 illustrated pod deployment — 18 October 2026

Authorisation: Karun accepted the five-still binding plan and requested moving the other pod occupant to Neptune Lounge temporarily, deferring unique player pods. Text-only open wardrobe and undefined conditional contents are preserved.

Source: `cd4d28e8988d207c2b718553acede87093640e35`.
Installed at approximately **21:06 AWST**. **130 isolated tests pass**, including 11 media tests.
Private backup: `/opt/futuresky/backups/w6f4-media-20261018-210559`. Restricted directory, snapshot of live data/assets/docs/bot/tests, pre-change data hashes, staged files and manifest. Do not publish snapshot contents.

Four code files installed selectively: pod_media.py, pod_opening.py, NavigationCog and InspectionCog. Five versioned PNG stills plus checksum manifest installed under `assets/images/world/manzo/triton_central/neptune_lounge/pod/v1/`. Live data, other artwork and service configuration preserved. Historical checkout HEAD left unchanged; deployed source is the manifest target.

## Verified

- Source code and asset bytes match Git target and tested candidate.
- All five HTTPS image URLs returned **200**, with downloaded bytes matching SHA-256 manifest.
- Service active/running; PID **813169**, replacing 812667.
- All **44 cogs loaded**, no extension-load failures, Discord readiness and Recovery heartbeat verified.
- All 61 data files checked during installation. Only characters.json changed intentionally.
- Exactly one record, `wanderer-0466`, changed only current_room from pod_room to neptune_lounge. Every other field and every other record, including Efiishent, compared equal after restart.
- No character reset, item grant, Thread Node replay, narrative event or room-instance creation.
- Full Discord image rendering remains a player check.

The process was paused for snapshot/install/data update, then resumed and terminated as its owning user to trigger existing systemd Restart=on-failure after ten seconds. This is a supervised forced restart, not a graceful stop. Updating the saved record and restarting avoids an in-memory stale record overwriting the move.

## Binding contract

`!look` in pod and `!inspect pod`: P01. `!inspect panels`: P02. `!inspect display`: P03 only before booking-read; after reading, text only. `!inspect light/button/brochure` and brochure picture: P05. `!inspect viewport/reflection`: P06. Wardrobe/body/HUD/material inspections remain text-led. No image is added to the explicit awakening introduction.

Inspection coverage includes grouped walls/floor/ceiling/seams, handles/drawer, bedding, warm lighting and printed brochure art. An image grants no inventory or control operation. The existing four wardrobe choices are not promoted to a final exhaustive catalogue.

## Deferred

Each player needs a unique pod in a future design; moving an occupant is a workaround only. Existing shared-room presence/broadcast semantics are unchanged. No occupancy hiding or general instancing is claimed. Other players can still enter the shared pod room until that work is done.

Sense return, full bodily appearance, mirror, conditional wardrobe population and media event scheduling remain unimplemented. The unread still is never shown after saved booking discovery. Placeholder in live rooms.json remains on disk; pod renderer overrides it without rewriting room data.

## Return / rollback

Player check: `!look`, `!inspect panels`, `!inspect light`, `!inspect viewport`, `!inspect wardrobe`. Efiishent already read the booking, so `!inspect display` should be text-only.

Rollback code/assets individually from private snapshot; remove newly added media module/assets if reverting fully, then restart and verify. Preserve current gameplay data. Do not restore the full old characters.json to undo one authorised location change. Any reverse move requires a targeted edit and reload.

W6-F4 REVIEW pending player image verification. No seal increment; W6 completed 3, total 19.
