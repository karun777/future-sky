# W7-F6 — Attend to the World

Status: ACTIVE — deployed 4 November 2026; authenticated player walkthrough pending.
Allocated 4 November 2026 on Karun's instruction “let's attend to the world”.
Home: W7 Engine. Baseline W6-F8 seal 4c7383f. Branch engine/w7-f6-attend-to-the-world.
31 sealed feathers remain; W7 five sealed. Next unallocated W7-F7, W6-F9. Chapter 1 / W4 stays paused.

## Outcome and scope

Inspect the pod's storage panels, display and booking notice inside the live fixed-screen window using the same durable observation service as Discord. Present saved authored prose, guidance and existing close-up art; preserve first/repeat behavior, arrival settings, recovery constraints and discovery prerequisites. No new canon, player reset, combat mode, wardrobe actions, map/journal rollout or expanded account access.

## Implementation

bot/fsbot/pod_inspection.py extracts the existing prepare_observation → save → presentation path, including equipped garment text and rollback on failed persistence. InspectionCog._pod_view calls it; the new POST /play/api/inspect calls the same service. Existing !awaken behavior is retained; the web does not silently start an opening.

GET /play/api/me adds a curated inspection offer. Initially panels are visible; display and booking become available according to saved discoveries. Arrivals explicitly without a booking do not receive one. Reads do not mutate knowledge or activity. Server checks session ownership/allowlist, Origin/CSRF, token expiry/single use, offered targets, current private state fingerprint and navigation revision. Current room, recovery/cube and existing web movement/sequence restrictions are rechecked. Explicit attention touches IdleHome; failures block discovery. No await separates final validation from mutation/save. Each client reads the same persisted knowledge; inspection does not send unsolicited Discord messages.

The live-pilot game.js extends the established transport with serialized inspection and movement, no command retries, stale/offline blocking and safe text rendering. Saved observations open in a native dialog, close when location changes, and clear on session expiry. Reading retains existing activity semantics: only the inspection is an action. Existing /play remains the original walking interface.

## Verification — 4 November 2026

- Full Python suite: 332 tests passed, including 13 new inspection tests.
- Three additional deployment tests passed: successful selective overlay, rollback of existing/new code without data changes, and refusal to overwrite a changed baseline.
- Live-pilot JavaScript behavior suite: 14 tests passed (11 transport regressions, three inspection behaviors); syntax passed.
- Existing frame privacy tests are retained. No authenticated live test or new browser visual pass is claimed.
- Read-only activation preflight passed against current server baseline. Only three backend files and four pilot static assets are in the manifest; no dependency/config/data overlay.
- Deployment tests use temporary directories and fake service commands; their printed “activated” text is not a live activation.
- W6-F8 authenticated movement/Discord walkthrough remains pending. Implementation proceeded independently using fictional cross-adapter tests; acceptance remains open.

## Deployment and return

Worktree: /home/efiishent/future-sky-worktrees/w7-f6.
Read-only check: python3 tools/deploy/w7f6/activate.py --check.
Operator activation:
ssh -t -p 777 efiishent@future-sky.net 'sudo python3 /home/efiishent/future-sky-worktrees/w7-f6/tools/deploy/w7f6/activate.py'

Activation stops the bot briefly, revalidates exact baseline hashes, backs up only selected code/assets, overlays them, confirms data hashes unchanged while stopped, starts the bot and verifies Discord reconnection and anonymous API denial. Health failure restores code only. Newly introduced module is removed on rollback; no player-data snapshot is restored. Sessions expire on restart: sign in again. Sign-in still lands at /play; reopen https://future-sky.net/assets/experiments/w6-f8/live/index.html.

After activation: check original movement/Discord synchronization, return to pod through actual routes, inspect panels → display → booking; then use !inspect booking and !inspect display in Discord, checking shared knowledge and truthful artwork. Test repeat observation, modal return, tab switch, and denied/stale action. Respect current recovery/opening state; do not reset character or invent a booking to force a test. Record terminal result and user evidence before sealing.

## Shared checkpoints

W6 retains the accepted frame; new observations use authored text and art. W2/W4 knowledge and first/repeat consequences remain authoritative. W5 passive refresh is quiet, explicit inspection records attention. W8 counts unchanged; live acceptance outstanding. Interface evolution remains a future expression of server-owned discoveries, not browser-local progression.

## Deployment confirmed — 4 November 2026, 17:54 AWST

Karun ran activation directly on neptunelounge. Backup: /opt/futuresky/backups/w7f6-inspection-20261104-095424. Operator output reports Discord reconnected, anonymous inspection denied and player data preserved. Independent post-activation verification: all seven runtime/assets match the deployment manifest, service active/running PID967373, original /play/ and live pilot HTTP200, anonymous /play/api/me and POST /play/api/inspect HTTP401. Source implementation 5ba3d1ecd6336ed62465ccfcb746456b97978e0c.

This supersedes earlier pending-activation statements. No authenticated character action was performed by the assistant. Player acceptance and cross-client inspection walkthrough remain pending; W7-F6 is not sealed, total remains31. Chapter1 stays paused.

## Inspection refinements — 4 November 2026

Karun's 18:00–18:01 screenshots show panels, display and booking observations in the live window, followed by matching booking/display responses in Discord. This is repeat-observation evidence; it does not establish a fresh discovery transition. W7-F6 remains active and Chapter 1 paused.

The room passage now has a larger share of the fixed viewport, with inspection and movement sharing a wrapping control shelf. Observation overlays offer Inspect display after panels and Read booking after display, intersected with the current server offer. Actions use the existing serialized, single-use-token transport. Offline/error status is visible inside the modal; revoked offers disappear. Wardrobe and FEED7 are still Discord guidance, not misleading web buttons.

Validation: all 16 JavaScript behavior tests passed, including new chained-action/fresh-token and offline/revoked-offer tests. No backend, dependency, player data or discovery rule changes. Fresh-character live acceptance remains outstanding.

Frontend refinement deployment: 4 November 2026, 18:14 AWST, source 6010f83834c4c4877148568fcd08e5be613fbfd5. Three static assets updated after exact baseline validation; public asset hashes match source. Backup /home/efiishent/future-sky-static-backups/w7f6-refinements-20261104-101416. No service restart or player-data changes. Browser visual verification remains pending: local Chromium download failed. The operator should refresh the pilot and check room prose plus panels → display → booking at their normal viewport. The original activation manifest describes the earlier deployment and must not be rerun for these frontend changes.
