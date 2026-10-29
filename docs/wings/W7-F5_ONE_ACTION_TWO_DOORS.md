# W7-F5 — One Action, Two Doors

Status: ACTIVE — implementation verified and deployment staged 29 October 2026; privileged activation and live author playcheck pending.
Home: W7 Engine. Shared checkpoints: W4 Play, W5 Time, W6 Expression, W8 Stewardship.
Source baseline: d58d3da; branch engine/w7-f5-one-action-two-doors.
W7 remains four sealed; total remains 28. W7-F6 is next unallocated.

## Outcome and acceptance

Existing Efiishent can take one ordinary walking step from the authenticated website or Discord, through shared movement authority and the same saved character. Walk an exit on the website, observe the location in Discord, walk back in Discord, refresh the website and observe the return.

The website is https://future-sky.net/play/ on the existing Neptune Lounge server. Discord remains a supported conversational way to play. Chapter 1 / W4 authoring stays paused. A tangible game window and interesting conversation should develop together.

## Boundary

Include current exit buttons, basic room description, approved existing artwork and useful action feedback. Reuse existing OAuth identity, owner allowlist, aiohttp, discord.py and bot-owned storage. No new framework or hosting service is required. Website requests an action; it never writes player JSON directly or fabricates a Discord message/context.

Preserve movement persistence and room-entry event consequences. Coordinate ordinary walking with explicit sequences and idle-home. Refuse stale views, repeated submissions and conflicting input safely. Deliberate website movement is conscious activity and interrupts/rearms idle-home; passive views remain observational.

Exclude combat controls, portals, teleport, purchases, wardrobe, arbitrary command execution, generic scripting/autonomy, full map/journal/avatar/telemetry, registration, wider access and unrelated narrative repairs. Only layout changes needed for room text, exits and feedback belong here.

## Dependencies and inspected seams

W6-F6 supplies live authenticated read-only access. W7-F3 owns explicit sequences and W7-F4 owns idle-home. Read reset ritual, Knowledge Atlas, Wing Index, charter and these checkpoints before returning.

Initial source inspection at d58d3da:

- NavigationCog.go owns walking, persistence, room-entry publication and Discord presentation. It awaits departure broadcasts before saving. Only automatic walking currently revalidates after that await. Concurrent ordinary actions can therefore act on a stale source room or record.
- SequenceCog has per-character task ownership; web requests must respect it without pretending to be sequence children.
- IdleHomeCog.observe replaces a character with a copied record when saving activity. Shared movement must reread the authoritative record after awaited work, preserving fresh input and generation checks.
- RecoveryCog is a Discord global check, not an HTTP check. Cube protection is inside navigation; sequence/idle choice and combat guards are separate. Moving the callback behind HTTP alone would bypass these boundaries.
- Navigation calls look after moving. Look can grant observations and change state; passive web scene projection must not invoke it.
- Existing movement announces the durable room-entry fact before rendering arrival. Event subscribers can open an encounter; web must preserve that consequence and hand unsupported choices back to Discord.

## Verification plan

Use fictional isolated characters and temporary persistence. Cover shared success/save rollback, blocked and missing exits, stale view and duplicate submission, competing clients, sequence ownership, interruption during departure, recovery/Cube/choice/combat, session identity and CSRF. Run existing suite for Discord/sequence/idle-home regression. Prepare a selective reversible overlay with source baseline checks and no player-data replacement. Live two-way author playcheck is required before sealing.

## Shared checkpoints

- W4: ordinary walking integration only; Chapter 1 authoring remains paused.
- W5: conscious web action rearms real idle time; observation does not; no world-clock change.
- W6: basic room text, exits and feedback; richer scene composition remains follow-up.
- W8: keep source, deployment and author playcheck separate; one home and one count.

## Return checkpoint

Allocated on an isolated worktree from the sealed W6-F6 baseline. Inspection has identified the action/concurrency seams above. No W7-F5 runtime changes deployed and no player moved by this work. The implementation and deployment preparation below supersede the initial next-step note. Do not rerun W6-F6's first-install activation script for an incremental deployment.


## Implementation and verification — 29 October 2026

NavigationCog.walk now owns ordinary walking for Discord go/move (including sequence and idle-home callers) and the authenticated web adapter. A per-character busy set refuses overlapping walks. Source room, exit destination, movement revision and current guards are rechecked after awaited departure delivery; the latest authoritative character object is used. No await separates final validation and save. Save failure restores the prior room. A successful save precedes the existing room-entry event. Sequence startup refuses while a walk is in flight; a walk refuses another task's active sequence.

The website's POST /play/api/walk uses the server-owned OAuth session, allowlist, exact Origin and session CSRF. Its only request fields are direction and a short-lived, single-use offer token. The offer contains server-side source room, walking revision and available direction names, expires after 120 seconds, and is consumed before the action await. A fresh view replaces the prior offer. Replays, stale rooms and walking away/back since the view cannot execute another step. Session restart invalidates offers. No browser-selected player or destination, fake Discord context or direct HTTP-side JSON write is introduced.

The web adapter counts a valid offered action attempt as conscious input, including an attempt refused as stale/busy; passive GETs remain observational. Activity-save failure prevents walking. Website movement refuses Cube/recovery and hands active combat/choices back to Discord. Discord's existing walkable-thread behaviour is deliberately retained: this pilot is not a rewrite of encounter escape rules. Arbitrary non-walking actions and teleport are not converted into a new universal transaction system.

Room title/art/basic description, pod bearings where applicable, exit buttons and inline feedback are shown. Image height is reduced to leave space for controls. Existing room text is rendered as plain text, never injected HTML. Room-entry subscribers still run and can open encounters. No web look command is invoked, so merely rendering does not grant inspection discoveries. The owner receives a best-effort movement notice in an existing Discord run channel; no channel is created. Full discovery/quest/encounter rendering remains outside scope.

Verification: 295 tests pass with /opt/futuresky/.venv-web-pilot-20261029/bin/python, against isolated source and fictional temporary state. This comprises the previous 270 tests, 21 new shared-walking/HTTP tests and four installer tests. Coverage includes persistence-before-event, save rollback, stale and repeated requests, cross-session movement, overlap, latest-record preservation, changed exit/room/recovery during departure, cancellation, idle rearm/save failure, identity/CSRF/origin checks, passive non-mutation, deployment success and automatic rollback. The browser JavaScript passes node --check. No automated rendered-browser or real authenticated walking playcheck is claimed.

## Deployment handoff

The staged installer is tools/deploy/w7f5/activate.py with a SHA-256 manifest for six existing files: navigation, sequence, web_portal and the three static UI files. Each live baseline was compared byte-for-byte with d58d3da. Read-only preflight passed on Neptune Lounge, including current service interpreter and pip check. No new dependency, nginx edit, OAuth secret change or persistent schema change is required.

Activation requires the existing administrator SSH/sudo step. The remote command tool rejected sudo -n true (Command not allowed); no privilege workaround was attempted. User already authorised deployment. This is an access handoff, not a new scope approval.

Run from Karun's terminal:

```sh
ssh -t -p 777 efiishent@future-sky.net 'sudo python3 /home/efiishent/future-sky-worktrees/w7-f5/tools/deploy/w7f5/activate.py'
```

The installer backs up affected code, stops the bot, verifies both data trees remain unchanged during the selective overlay, restarts and requires Discord reconnection, public portal 200, and anonymous read/move 401. Failure restores prior code and checks reconnection; player data is never rolled back. Backup/result evidence is written under /opt/futuresky/backups/w7f5-walking-<timestamp>. Do not rerun blindly after success: the baseline guard deliberately rejects it.

After activation, sign in again (restart clears memory-only sessions), walk one exit on the website, inspect the location in Discord, then walk back in Discord and refresh the website. Feather remains ACTIVE until deployment evidence and that live playcheck are recorded; not sealed. Chapter 1 stays paused. No player was moved by development tests.


## Activation attempt and corrected readiness check — 29 October, 19:43 AWST

The author ran activation at 19:41 AWST. Backup: /opt/futuresky/backups/w7f5-walking-20261029-114117 (backup timestamp is UTC). The candidate loaded navigation, sequence and portal and logged into Discord, but the installer falsely timed out. It then restored the old six files and restarted successfully, but falsely timed out again. Root cause: readiness searched case-sensitively for "Logged in as" while the actual application logs "logged in as". The initial installer tests mocked wait_ready and missed this real log-format mismatch.

Read-only recovery verification: service active/running at PID 917782; Discord logged in at 19:41:54 AWST; heartbeat subscribers succeeded. Every affected live file SHA-256 matches the old baseline. Local and public /play/ return 200, /play/api/me returns anonymous 401, and /play/api/walk returns 404 as expected for the restored read-only version. The installer had passed its stopped-data comparison before the original startup attempt; rollback copies only code, never data. No game-state reset was performed.

Fix: case-insensitive login matching and explicitly UTC-qualified journal timestamps. Four new readiness tests exercise the real lowercase log format, require current-PID filtering and endpoint checks, and reject gateway-only connection, absent walking endpoint and unavailable journal. Full suite now 299 passed. The corrected wait_ready was also called read-only against the actual restored service/logs and immediately returned PID 917782. Deployment preflight passed again. The six-file gameplay candidate/manifest is unchanged. Privileged retry is ready; not yet deployed or sealed.
