# HUD encounter warning — next-feather proposal

Status: PROPOSED ONLY — 12 November 2026. No feather allocated.
Recommended home: W6 Expression; candidate W6-F10 — One Clear Warning.
W7 supplies the unchanged encounter-gating authority. One home/count if accepted.
W7-F11 and W6-F10 remain unallocated; 37 sealed feathers, W7 ten.

## Verified starting point

Read in order: [Wing Index](../WING_INDEX.md),
[W7-F9 current summary, carry-forwards and seal](../wings/W7-F9_WAKING_INTO_THE_WINDOW.md),
then [W7-F10 current summary and seal](../wings/W7-F10_BEGINNING_AGAIN.md).
W7-F10's dated W7-F9 PARKED statements are superseded by the 12 November W7-F9 seal.

Server checkout: /home/efiishent/future-sky-worktrees/w7-f8.
Verified branch: engine/w7-f10-beginning-again.
Clean HEAD, tracking ref and independently queried origin branch all matched
f2346b11c7ce92b51337edc39c3ff448cc257eca before this documentation checkpoint.
The checkout folder name is historical. No branch switch occurred.

The W7 register row still reported nine seals and W7-F9 return blocked, contradicting
the current index summary and W7-F9 seal. This checkpoint reconciles that row to ten
and W7-F9 sealed; it adds no seal.

## Cause confirmed

The same authoritative refusal reaches two presentation slots:

| Source at the inspected revision | Role |
| --- | --- |
| bot/fsbot/cogs/navigation.py:480–497 | walking_refusal(web_pilot=True) returns the encounter/choice refusal when requires_choice is true. |
| bot/fsbot/web_portal.py:194–220 | add_walking projects that refusal into walking.notice and withholds exits. |
| bot/fsbot/web_portal.py:252–281 | inspection_refusal reuses the walking refusal; add_inspection projects it into inspection.notice and withholds targets. |
| tools/authoring/w6f8/live/game.js:171–173 | Renders inspection.notice in inspect-notice and opens inspection-options. |
| tools/authoring/w6f8/live/game.js:223 | Independently renders walking.notice in walk-notice. |
| tools/authoring/w6f8/live/index.html:13 | Both notice elements occupy the current room's reading area. |

The identical text is “A choice or encounter needs your attention in Discord.”
This is duplicate rendering of one shared refusal, not evidence of a second encounter
or a reason to weaken the server checks. The earlier
[W7-F9 blocker screenshot](../wings/W7-F9_RETURN_BLOCKER_20261112.jpg) records the live
symptom historically; this inspection does not recreate it on Efiishent.

The active client source is tools/authoring/w6f8/live, served from the existing
/assets/experiments/w6-f8/live path. bot/fsbot/web_static/game.js is not the client
to change for this follow-up.

## Evidence — 12 November 2026

Four read-only source/live SHA-256 comparisons passed against /opt/futuresky:

| Installed relative path | SHA-256 |
| --- | --- |
| assets/experiments/w6-f8/live/game.js | 4bb1d86f20371d1021596d610a8d6671384fb3c07a52a64aa13cf74e288407ce |
| assets/experiments/w6-f8/live/index.html | c5aa48b5c6feea26aab93a19fed5d9c83e9858cc9c992a7f7ce2993df0ee5356 |
| bot/fsbot/cogs/navigation.py | ec52b66d5143749d4cc5147ce07da3dc3307184c42257737ff78790db0ee1147 |
| bot/fsbot/web_portal.py | 3519c4a8f15af1bd93dc81a1095d7e1406e51db3d592a535170440a03e0521d8 |

A one-off HTTP diagnosis reused WebWardrobeTests and WebWalkingTests.move with
fictional account 123, fake OAuth, the real HTTP adapters and captured fixture saves.
After obtaining valid offers, each separate fixture received either a fictional
active_thread_node or active_encounter_id. In both cases:

- Previously offered walking, inspection and wardrobe requests returned HTTP 409,
  each carrying the same encounter refusal.
- A fresh view supplied identical walking/inspection notices, no exits, no
  inspection targets and wardrobe.available false.
- Exact all-character fixture comparison and save count remained unchanged after
  the blocked requests and read.

A one-off Node diagnosis reused the setup/data/command helpers from
tests/test_web_inspection_window.cjs against copied, unchanged Git HTML/game.js.
Node was unavailable in the server shell, so this ran in the isolated local runtime.
It confirmed two unhidden notice elements containing the same refusal and a visible
inspection-options container. Blocked go/inspect commands produced zero POSTs.
Replacing the fictional response with the ordinary offer cleared both notices and
restored the exit. One diagnostic assertion group passed.

These are fictional HTTP and minimal-DOM diagnostics, not a new browser visual
playcheck or a live player encounter. No production character records, archive,
receipt or permissions were read or written. The prior 470-test Python result
belongs to W7-F9's reviewed code; this proposal does not claim a fresh full-suite run.

## Proposed bounded outcome

Show an identical nonempty walking/inspection refusal once in the existing room
reading area. Retain the existing walk-notice as the shared display and suppress
only the matching inspection copy. Hide an inspection-options wrapper that has
neither targets nor its own distinct notice. Keep unequal or inspection-only
notices visible and preserve existing command-result feedback.

Refresh must restore or clear the notice from the current authoritative response.
Do not retain a stale block after the encounter ends, and do not expose actions
while it remains active. This is a presentation change in the accepted game window:
no new encounter controls, prose redesign, layout redesign or API/gating change.

Acceptance for the proposed feather:
- Equal nonempty notices appear once; distinct and inspection-only notices survive.
- Repeated polling does not multiply messages; blocked-to-clear and clear-to-block
  transitions update correctly.
- Fictional encounter requests remain refused without character changes; ordinary
  controls recover only when the authoritative offers return.
- Review the existing game window with a clearly fictional blocked fixture and an
  ordinary fixture. Preserve image-left/reading-right layout, persistent typed
  commands, reference panels and obvious-exit bearings.
- Any later static delivery needs a bounded package, cache-version update and
  source/installed verification under the current runtime contract. Do not reuse an
  old broad deployment package without reconciling its pins.

## Return checkpoint and retained boundaries

Diagnosis and proposal only. No implementation, allocation, seal, deployment,
service restart, gameplay command, reset, restore or main merge in this checkpoint.
If Karun accepts the proposal, allocate W6-F10 and make the isolated presentation
correction plus focused regression checks as the next concrete step.

Efiishent's last verified state remains the sealed W7-F9 pod-room return with
Freeform Attire, belongings and discoveries intact; it was not freshly re-audited
here. Do not reset again. Preserve the private archive and reset receipt.
The Dark Rat Queen remains another person's protected player character: account,
permissions and routing preserved; her access issue parked. Chapter 1 / W4 paused.
First-time account/OAuth onboarding still needs a separate eligible participant;
no reset or access expansion substitutes for that evidence.
