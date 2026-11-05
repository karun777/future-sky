# W7-F8 — Bringing the HUD to Life

Status: ACTIVE — 5 November 2026. Allocated on Karun's instruction.
Home: W7 Engine. Branch: engine/w7-f8-bringing-the-hud-to-life.
Baseline: W6-F9 seal 5b18f2f; live W7-F7 file hashes independently matched before changes.
34 sealed feathers; W7 seven. This feather is not sealed. Next unallocated W7-F9 and W6-F10. Chapter 1 / W4 remains paused.

## Bounded outcome

Bring the accepted W6-F9 image-left, narrative-right presentation into the authenticated game window. Preserve shared walking, inspection and wardrobe operations. Character, Inventory and Quest Log show saved player information. No fictional rehearsal capabilities, upgrade stages, telemetry, new quest engine, new lore or chapter progression.

## Implementation

- Live art uses contain/left positioning, without narrative overlay. Desktop reading column is 28% (300–420px); on narrow screens art sits above the reading panel. References replace only that panel and restore attention on close. Commands stay available.
- Existing authenticated transport, CSRF checks, one-use action offers, stale/offline safeguards and no automatic mutation retry remain in use.
- Character adds an explicit whitelist of saved birthdate, class, six existing stats, HP and elemental pools already exposed by Discord sheet. Missing values are not fabricated. Inventory retains shared bag/equipment projection.
- hud_view.discovered_entries supplies the same known FEED7/notice/booking facts to Discord and the web. Quest Log uses saved discoveries and never grants them. No author-only room records or raw extra/flags enter the API.
- Quest Log is a memory/reference panel. Implant off/dimmed/degraded is displayed separately on Character and does not erase memory. Existing Discord !hud continues to conceal its own instrument panel when off/unavailable. Web implant-setting mutation and FEED7 playback remain outside this scope.
- Equipment confirmations display plain text without leftover Markdown delimiters.
- Delivery collection stays Discord-only. Activity is still per-tab, not a durable shared event log.

## Verification

353 Python tests passed, including six new discovery/projection/HTTP tests. Existing security, walking, inspection, wardrobe and persistence suites pass. Frontend regression tests cover commands, duplicate Enter, lost responses, passive browsing, expiry, external room changes, refresh recovery and private data clearing. Final frontend count and deployment record follow below.

Authenticated browser preview uses the existing live /play API. Confirmed real room, Freeform Attire equipped, carried inventory, passive wardrobe browsing and reference return. Desktop 1512×784, short laptop 1366×600 and phone 390×844 layouts inspected. No outfit or movement mutation performed during preview. The preview against the old backend cannot yet display the new sheet/journal projection.

## Deployment and rollback

Selective manifest: three backend files (new hud_view plus existing cogs/hud and web_character_view) and four live static assets. No player-data/config/catalogue/dependency overlay. Exact source and baseline hashes checked; read-only preflight passed.

Activation:
```bash
sudo python3 /home/efiishent/future-sky-worktrees/w7-f8/tools/deploy/w7f8/activate.py
```
Briefly stops the bot, revalidates hashes, backs up only affected code, verifies data hashes while stopped, installs files, reconnects Discord and checks anonymous denial plus public asset hashes. Failure restores code only; never restore old player state. Sessions expire on restart: sign in again at /play/.

## Acceptance before seal

- Check live Character, Inventory and Quest Log against current Discord sheet/fit/hud knowledge.
- Inspect an available detail; open and close a reference; confirm image/focus continuity.
- Refresh/reconnect and confirm the saved location, equipment and discovered notices return.
- Existing mutation regression tests are not a new live web/Discord action comparison. Fresh-character first discovery and first outfit live checks remain explicitly unverified.
- Artwork standardisation remains W6 follow-up; existing room art is the wardrobe fallback.
- Chapter 1 stays paused. No sealed-count increment.

## Shared-wing return

W1/W2: existing authored facts/art only. W3: attire and class remain distinct; existing sheet fields only.
W4: established consequences retained, chapter paused. W5: reading remains passive; no fabricated time/progress.
W6: accepted layout integrated; art standards deferred. W8: one home/count, deployment and acceptance limits explicit.

## Review checkpoint — 5 November 2026

356 Python tests passed (including three new code-only deployment/rollback safety cases); 22 frontend tests passed under Node in the local test runtime because Neptune Lounge has no Node executable. Python runs are on Neptune Lounge using the configured web-pilot interpreter. Printed activation lines in the test log are from temporary-directory tests, not production deployment.

Browser checks used the authenticated static preview at /assets/experiments/w7-f8-review/index.html, against the unchanged live backend. Real inventory/wardrobe rendered; reference return preserved the scene. At 1366×600 and 390×844 there was no document overflow, long Help content scrolled in its own column, and commands remained accessible. No browser console errors. Temporary viewport overrides reset.

Read-only deployment preflight passed. Production activation is NOT complete: sudo requires a password, and Desktop Commander returned "Command not allowed" for the noninteractive activation attempt. No service stop or production overlay occurred. The existing /play/ remains the sealed W7-F7 frame. The review preview uses the old API and explicitly reports new records unavailable until the backend upgrade; it is not proof of the new live projection.

Operator next step: run the activation command above on Neptune Lounge, then sign in again. Complete the live Character/Inventory/Quest Log comparison and refresh/reconnection acceptance before asking to seal. No player record was modified to manufacture acceptance. W7-F8 remains active; 34 sealed unchanged.

## Operator activation verified — 5 November 2026

Karun ran the prepared activation command. Independent verification subsequently found all seven live files equal to the manifest source hashes, all four public assets equal to source, futuresky-bot.service active, /play/ returning 200 and anonymous /play/api/me returning 401. This supersedes the earlier pending-activation checkpoint.

The browser loads the new live frame and correctly requests sign-in after the service restart. Authenticated Character/Inventory/Quest Log comparison and post-restart continuity remain pending the user's sign-in. No seal, count increment or Chapter 1 activation.

### Live presentation refinement — 5 November 2026, 20:02 UTC

User screenshots confirm live room walking, side-wall inspection, wardrobe examination,
Character, Inventory and Quest Log in the accepted image-left/text-right layout.
This frontend-only pass groups saved Character values into Profile, Attributes and
Elemental pools, moves the checked timestamp beside connection status, and suppresses
the development-only out-of-pod inspection pilot notice. Genuine restriction notices
remain visible.

Artwork audit: P03 contains an unread booking state and is deliberately withheld after
booking discovery. No dedicated wardrobe still is bound. Existing truthful room
fallbacks remain; no new artwork or lore was introduced.

Validation: all 22 Node browser-behaviour tests pass. Signed-in production browser
verified grouped Character values, unobstructed scene, polling and explicit Refresh
while retaining the open panel; no browser console errors. Public HTML/CSS/JS match
source hashes. Reconnection/no-replay remains covered by isolated tests; a deliberately
interrupted live connection and fresh rendered Discord comparison remain outstanding.

Static deployment backed up the three previous files to
`/opt/futuresky/backups/w7f8-polish-20261105T200144` after exact HEAD/live comparison.
No service restart or player-data changes. The original activation manifest records
the earlier deployment and is not a manifest for this follow-up static pass.
W7-F8 remains ACTIVE and unsealed. Chapter 1 remains paused.

### Commands beneath the reading column

At the user's request, the command box and exits now sit immediately after the active
text in the right-hand column. Reference navigation stays along the bottom. Long
narrative/reference panels scroll above the reachable command box. The image remains
unobstructed and gains vertical space from the smaller bottom bar.
HTML/CSS only; transport and action semantics unchanged.

Verified signed-in preview at desktop and 390 × 844: long Help content scrolls,
command input remains within the viewport, no horizontal overflow on the narrow
layout, Return and typed look work. Public HTML/CSS bytes verified after backup and
static deployment. W7-F8 remains active; prior outstanding acceptance checks remain.
