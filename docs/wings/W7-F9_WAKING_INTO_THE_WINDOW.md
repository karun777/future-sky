# W7-F9 — Waking Into the Window

Status: ACTIVE / UNSEALED — 12 November 2026; correction deployed and owner release verified, awaiting HUD sign-in and return retest.
Home: W7 Engine. Working branch: engine/w7-f10-beginning-again.
Original implementation branch: engine/w7-f9-waking-into-the-window.
Baseline: W7-F8 seal 524411c. Working checkout remains physically at
/home/efiishent/future-sky-worktrees/w7-f8; the checkout is now on adjacent
engine/w7-f10-beginning-again. The original W7-F9 branch records this feather's implementation lineage.
36 sealed feathers; W7 nine. Adjacent W7-F10 is sealed; next unallocated W7-F11 and W6-F10.
Chapter 1 / W4 stays paused.

## Current return checkpoint — resumed 12 November 2026

Karun explicitly requested resumption of W7-F9 after the W7-F10 seal at
`26a6270f0a27f525f0879d998911056ec6208ad6`. Continue in the existing checkout on
`engine/w7-f10-beginning-again`; do not switch back to the older W7-F9 branch.
The completed reset, guided creation, awakening, saved-channel reuse and opening
inspection evidence are inherited from W7-F10. **Do not reset again.**

First clothing selection, live Discord/HUD outfit and inventory parity, HUD
departure, and reverse location synchronization are directly verified. However,
the first return to the pod triggered legacy arrival_awakening_v1 and blocked the HUD.
The correction is now installed; at 17:21 AWST the existing owner's !awaken released
only the two obsolete scene fields. Efiishent remains in the pod with the correct
outfit, bag, discoveries and routing. No story choice was submitted or completed.
Next: finish existing-account Discord sign-in in the HUD tab, then compare clients
and retest departure, return and persistence. Do not reset or clear unrelated
encounters. New-account / first OAuth onboarding remains separate and unverified.

Initial read-only connection evidence on 12 November: Neptune Lounge Desktop Commander
responded; Mac is listed online and Windows offline. Checkout was clean at the seal
and the remote branch had the same full SHA. Bot is active/running, PID 1029171;
public /play/ returned HTTP 200. Chrome connected and a newly opened HUD displayed
Signed out / Sign in with Discord. A fresh Discord tab opened the existing private
fs-efiishent channel while signed in as karunicorn; its 11 November fresh-pod !look
response is visible. The older tab did not respond to control. No Discord command
was sent. Player HUD sign-in is required before live acceptance.
At that initial resumption checkpoint, no clothing choice, movement, reset,
deployment or service restart had occurred. Later live evidence follows below.

Retain the private original archive and reset receipt. The Dark Rat Queen remains
another person's protected player character; preserve her account, permissions and
existing routing, with her access issue parked. Chapter 1 / W4 remains paused.
W7-F10 remains sealed; W7-F9 is active but unsealed. **36 seals; W7 nine.**

## Deployment and owner release verified — 12 November 2026, 17:17–17:23 AWST

Karun reported completing the reviewed installer. Direct installed-code verification
passed: three replacement files, preserved dependencies/assets and the current
140-entry runtime contract. Service restarted at 17:17:40 AWST with PID 1037793;
Discord login/readiness was logged at 17:17:45, and public /play/ returned HTTP 200.
Checkout remained clean/synced at 900c746 on engine/w7-f10-beginning-again.

At 17:21, !awaken was sent once in the existing private fs-efiishent channel.
The bot returned POD // FINDING YOUR BEARINGS and the existing-account HUD handoff.
Private canonical before/after comparison found exactly two owner record changes:
extra.thread_nodes.active_thread_node became null and active_presented became false.
Completed history remained empty and pending_answer remained null. All other owner
fields, including outfit, bag, first-choice record, discoveries and routing, matched.
Every other character record matched. Lockers, vault, cubes and the reset receipt
were byte-for-byte unchanged. No reset, direct player-data edit or choice completion.

[Direct release screenshot](W7-F9_RELEASE_20261112.jpg), SHA-256
c06b4587b1a1fd6ecd74ab2300ae0c48380d421a4ed902e14fe182e1c34c2a87.

The private original archive was not opened or altered; its permissions prevent this
remote account from inspecting it, so no new archive hash verification is claimed.
Private comparison material remains outside Git. Queen account/routing records and
the pinned router were preserved; Discord permissions were not changed or re-audited.

HUD reload after restart showed Signed out. Its existing Discord sign-in route now
shows karunicorn / Please log in again. The player must complete this sign-in in the
retained HUD tab; the separate Discord private-channel tab remains usable. Both tabs
are retained for continuation. No post-correction movement has yet been attempted,
and no cross-client return/persistence acceptance is claimed at this checkpoint.
The legacy scene is safely released; the remaining hold is authentication.

W7-F9 ACTIVE/unsealed; 36 seals, W7 nine. First-time account/OAuth remains unverified.
Chapter 1 and the Queen's separate access issue remain parked.

## Correction prepared — 12 November 2026

Karun authorised the bounded fix after the live blocker was identified. Three
Python files now prevent arrival_awakening_v1 from triggering on room entry when
the character already has a valid guided_creation_v1 / performance_arrival_v1
opening. Ordinary legacy arrivals and unrelated thread nodes retain their behavior.
The existing owner's !awaken can release only that exact obsolete active node:
active_thread_node becomes null and active_presented false, after a successful
save. It does not record completion or select an option. Missing/invalid guided
state, a pending answer, another encounter, cube, other location, combat and bodily
recovery are refused. Failed save restores the in-memory original.

470 Python tests pass. The added journey includes real HTTP inspection and first
outfit, departure, shared Navigation return, actual EventBus/ThreadNodes subscriber,
saved-record reload and a new fictional signed-in session. Disabling the new guard
reproduces legacy delivery in this test. Separate temporary-file recovery tests
verify exact changes only, other-player preservation, durable reload, idempotence,
failure/retry and refusal boundaries. Existing deployment and old-archive restore
regressions remain green. These are fictional tests, not live acceptance.

[Reviewed package and operator steps](../../tools/deploy/w7f9_return/README.md):
three replacement files, 138 preserved code/assets, private transactional code
backup and data-drift checks. The package preserves the W7-F10 router and the
documented ba884a9 HTML cache correction. Exact install and rollback were rehearsed
in temporary copies of current code, with fictional player records, receipt and
archive unchanged. Both old/new 140-entry runtime contracts passed that rehearsal.
Read-only production code/asset baseline check passes; the bot remains running
with the original code.

Historical deployment manifests and archive schema remain unchanged. The current
runtime contract advances to version 3 for the reviewed correction; until installed,
the default contract intentionally refuses old live code. The package retains the
previous contract as baseline-runtime.json. No reset or restore is requested.

**Pending privileged step:** remote command access blocks sudo, and restart
configuration includes a root-readable file. The operator script checks restart
flags before stopping the service, then installs/verifies code and restarts.
No production installation, restart, owner !awaken release or return retest has
occurred at this preparation checkpoint. The live character remains blocked by
the old node with correct belongings. After readiness, compare private before/after
state, use !awaken once, then verify HUD/Discord departure, return and persistence.

Duplicate refusal text remains a secondary presentation finding. First-time
account/OAuth onboarding is unverified. W7-F10 sealed; W7-F9 ACTIVE/unsealed;
36 seals, W7 nine. Private archive/receipt and Queen account/permissions/routing
remain protected; Chapter 1 remains paused.

## Live comparison and return blocker — 12 November 2026, 16:46–16:53 AWST

After the player restored Discord login, fresh commands in the existing private
fs-efiishent channel supplied direct evidence:

| Check | Result |
| --- | --- |
| Discord !fit and !inventory | Freeform Attire equipped; Leather Jacket x1 and Rusty Knife x1 carried. Matches HUD and saved state. |
| HUD go west | Arrived at Hostel Hallway — Pod Doors & Quiet Lives; Discord received the web-movement notification. |
| Hallway reload and Discord !look | HUD retained the hallway after reload. Discord showed the same room description and south/east/down exits. Disk current_room was hostel_hallway; outfit and bag unchanged. |
| Discord !go east | Location returned to pod_room and HUD synchronized without a manual refresh. The legacy Transit Pod 3417 awakening node started instead of an ordinary return. |
| Returned belongings | HUD and canonical disk still show Freeform Attire, the original knife/jacket and pod_freeform first-choice record. Opening discoveries remain intact. |
| Returned interaction | FAIL: active arrival_awakening_v1 leaves no visible HUD exits and displays the Discord-choice refusal twice. No story choice was submitted. |

[Return-blocker screenshot](W7-F9_RETURN_BLOCKER_20261112.jpg), SHA-256
45eddd92e5b7b3207900690ade88e0654ef9b98da7c7d010350d5153831496c9.
This is functional location/equipment persistence, not successful return acceptance.
The live server was not restarted and no fresh live web session was forced.

### Root cause and isolated reproduction

Source/live bytes match for navigation.py, threadnodes.py, arrival.py and
pod_opening.py. The tracked and live arrival_awakening_v1 trigger both specify
on_enter_room pod_room and once_per_character true, with no opening-ownership
requirement. Guided creation records origin guided_creation_v1 and the new opening,
but does not complete the legacy node. ThreadNodesCog's room-entry selector checks
legacy completion and trigger requirements without checking the existing opening.
Consequently the first return starts the older awakening; once-per-character does
not prevent its first activation. The HUD correctly refuses active encounters.

A one-off isolated reproduction used WebArrivalTests.asyncSetUp, its fictional
account 123, fake OAuth and real HTTP adapters. It connected Navigation's event
publication to the real ThreadNodesCog._on_character_entered_room subscriber,
loaded the tracked node definitions, and substituted captured-message delivery.
The fixture's return exit was set to pod_room. Discovery, first Freeform selection,
HTTP departure and shared-navigation return reproduced the active legacy node.
A new fictional signed-in session still had no walking exits. Captured saved state
retained the active node and outfit; the other fictional character was unchanged.
All characters and writes were fixture-only; no live messages or data writes came
from this reproduction. This is a successful bug reproduction, not a passing return.
The earlier fresh-arrival HTTP test omitted the thread-node subscriber and return
leg; its passing result therefore did not cover this interaction.

### Next bounded correction

Prevent this legacy awakening from starting for an already-established guided
opening, while preserving legacy arrivals and unrelated thread nodes. Add the real
room-entry subscriber and the return leg to regression coverage. Handle the exact
erroneously active node separately, preserving discoveries, first-outfit entitlement,
belongings, completed history and all other players; do not pretend any of its
choices was played. The duplicate refusal text is a secondary HUD presentation
finding. Do not bypass encounter gating globally.

At this diagnosis checkpoint, no implementation or live node repair/deployment had
been performed. The later Correction prepared section supersedes source status;
the active legacy node remains the live blocker until installation and explicit release.
Any code delivery must preserve the live router and reconcile the W7-F10 runtime
pins before future restore plans. Private archive and reset receipt remain retained;
Queen account/permissions/routing and Chapter 1 stay outside this work.
W7-F9 remains ACTIVE/unsealed; 36 seals, W7 nine.

## Live first clothing selection — 12 November 2026, 16:35–16:41 AWST

The existing-account OAuth flow returned to the signed-in HUD during the player
handoff. Direct HUD inspection confirmed efiishent, Dreamer Technician, in the pod,
with one Rusty Knife, one Leather Jacket and nothing equipped. This verifies a
returning account, not first-time account/OAuth onboarding.

Commands were typed through the ordinary HUD field, following visible guidance:
inspect garment → inspect pod → inspect panels → inspect display → inspect wardrobe
→ wardrobe → inspect Freeform Attire → uniform freeform. The first-choice prompt
was present before selection. The action reported the choice recorded; wardrobe
then showed Freeform Attire worn and the first outfit already issued. No repeat
selection was submitted, so duplicate-request refusal remains automated evidence.

Read-only canonical-store observations before and after the action confirmed:
- before: chest empty and pod_uniform_selected absent/null;
- after: chest itm_pod_uniform_freeform and pod_uniform_selected pod_freeform;
- bag unchanged: one itm_rusty_knife and one itm_leather_jacket.

HUD Inventory matched those holdings. Quest Log showed the discovered FEED7 signal
without a performance booking. A full browser page reload retained the discovered
inspection options and equipped Freeform Attire. This is disk-save and same-session
page-reload evidence, not a service-restart or fresh-session persistence test.

[Post-reload inventory screenshot](W7-F9_FIRST_OUTFIT_20261112.jpg) is the direct
browser evidence; SHA-256 ffd7ecbf3cb3fe654baeaa64e122ed561c09e700c8bdd3009a3bb57d1d19f26b.

A fresh tab for fs-efiishent instead reached Discord's account chooser, showing
karunicorn / Please log in again. Its login form is open for the player. No Discord
command was sent and no current Discord outfit comparison is claimed. Resume with
!fit and !inventory in that private channel, then departure, return and persistence.
Character remains in the pod; no movement, reset, restart or deployment occurred.
Private archive/receipt, Queen account/grants/routing and the Chapter 1 pause remain
unchanged. W7-F9 ACTIVE/unsealed; 36 seals, W7 nine.

## Location-change connection check — 12 November 2026, 16:33 AWST

Karun moved location and requested a state check. Both Mac and Neptune Lounge
Desktop Commander executed read-only commands successfully; Windows remains offline.
The public HUD returned HTTP 200 from the Mac with successful TLS verification
(curl total 0.063 seconds for this request, not a gameplay latency benchmark).
Server checkout was clean on engine/w7-f10-beginning-again at d96b6b1, matching the
queried remote branch. Bot remains active/running with unchanged PID 1029171.
Chrome responds and the existing HUD still displays Signed out. The older private
Discord tab is listed, but its control attempt timed out; its current content was
not reverified after the move. Earlier fresh-tab Discord evidence remains historical.

No gameplay, reset, deployment, restart or permission change was made. Next remains
HUD sign-in, first clothing selection, Discord/HUD comparison, departure, return and
persistence. W7-F9 ACTIVE/unsealed; W7-F10 sealed; 36 seals, W7 nine; Chapter 1 paused.

## Historical return checkpoint — adjacent creation/reset feather

Original source checkpoint: `96ac40f`. Return note refreshed 11 November 2026
through adjacent W7-F10 evidence at `1028790`.

[W7-F10 — Beginning Again](W7-F10_BEGINNING_AGAIN.md#current-review-summary--11-november-2026)
has completed the separately authorised reset, guided recreation, fresh HUD state
and saved-channel verification. Opening guidance is deployed and browser-verified;
restoration is rehearsed under the reconciled runtime contract. W7-F10 is now
SEALED following Karun's final review on 11 November 2026. This feather remains
PARKED/unsealed and is the next return; its work has not been automatically resumed.

On return, use that existing fresh-character evidence; do not reset again merely
to manufacture acceptance. Complete first clothing selection, departure and return,
and compare Discord/HUD behaviour. A reset character on an existing account does
not verify new-account onboarding. Historical ACTIVE, deployment-pending and
no-reset statements below describe their dated checkpoints, not current state.

## Bounded outcome

Connect existing guided Discord awakening to the accepted live HUD. Verify first
arrival, discovery, first clothing selection, departure and return using existing
game authority. No creation redesign, new story, artwork expansion or public-access
expansion. Generic new arrivals deliberately have no performance booking; the
suggested booking walkthrough applies only to already-eligible performance arrivals.

## Implementation and evidence

- Saved, authorised characters receive Open your game window after !begin awaken.
  Existing eligible characters can recover that handoff with !awaken in the pod.
- Handoff checks the running WebPortalCog's configured allowlist and saved character.
  Preview, failed saves, disabled portal and non-admitted users receive no live-HUD
  promise. OAuth access policy is unchanged; no allowlist values are exposed.
- Help's available commands reflect current inspection targets, exits and discovered
  wardrobe. No fixed booking/garment examples imply that everyone has those options.
- Existing room hints already respect discovery. They are reused, not replaced with
  a new tutorial state machine or knowledge grants.

362 Python tests and 24 frontend behaviour tests pass. These include a fictional
fresh guided creation through real HTTP adapters: panels -> display -> wardrobe ->
first Freeform selection -> west -> new signed-in session. Saved holdings and
location persist; early booking is rejected, generic arrivals never receive it,
first-outfit token reuse fails, and reads do not mutate character state. Separate
callback checks cover handoff after save, resumability, preview isolation, failed
save and non-admitted users. OAuth and all fixtures are fictional; this is not a
live new-account walkthrough. Activation messages printed by deployment unit tests
refer to temporary test environments, not production.

## Deployment

Prepared six-file selective deployment: four backend files and HTML/game.js.
Exact live baselines checked. Reuses the W7-F8 deployment procedure, scoped to
W7-F9: stopped-service backup, data preservation checks, code-only rollback and
Discord/portal readiness. No config, player data or access-policy overlay.

```sh
sudo python3 /home/efiishent/future-sky-worktrees/w7-f8/tools/deploy/w7f9/activate.py
```

Not yet activated. Administrator restart requires the operator. After activation,
sign in again and check Help plus the existing-character !awaken handoff. An actual
fresh-player run requires a separate eligible Discord identity without a saved
character; never reset Efiishent to manufacture acceptance. Do not widen the pilot
allowlist without explicit authorisation identifying the new participant.

## Acceptance and return

- Verify active Discord handoff, correct link/account instruction and current Help.
- Observe an eligible fresh player's creation-to-HUD path and first clothing choice.
- Confirm discovery hints, no unearned booking, departure and return with saved state.
- Keep automated, operator-reported and directly observed evidence separate.
- W7-F9 stays ACTIVE until bounded acceptance/review; no sealed-count increment.

Shared-wing return: W3 retains existing creation/identity rules, W4 keeps booking
eligibility and chapter pause, W5 retains world continuity, W6 supplies the sealed
layout, W8 records access and live-evidence limits. One W7 home/count.

## Activation and existing-player live check — 9 November 2026, 16:03 Perth

Operator activation verified: all six installed source hashes match the manifest,
public HTML/game.js match, service active and anonymous /play/api/me returns 401.
The already signed-in browser returned to Up to date after page reload. Help lists
Efiishent's currently offered inspections, west exit and discovered wardrobe.

In the private fs-efiishent channel, !awaken returned existing pod bearings followed
by Open your game window linking to https://future-sky.net/play/, the same-account
sign-in instruction and command guidance. This directly verifies the running
existing-character handoff. No movement, equipment selection or reset was used.
The HUD was left at its room view.

Fresh-player live creation, first discovery and first clothing choice remain pending:
the current character already completed those steps. The passing fictional HTTP
rehearsal is separate evidence. Next requires a separate eligible Discord participant
without a saved character, or an explicitly agreed deferment of that live walkthrough.
Do not reset Efiishent or expand access merely to manufacture a passing check.
W7-F9 remains ACTIVE/unsealed; Chapter 1 paused; total 35 sealed unchanged.
