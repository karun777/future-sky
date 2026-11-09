# W7-F9 — Waking Into the Window

Status: PARKED / UNSEALED — 9 November 2026, at Karun's request.
Home: W7 Engine. Branch: engine/w7-f9-waking-into-the-window.
Baseline: W7-F8 seal 524411c. Working checkout remains physically at
/home/efiishent/future-sky-worktrees/w7-f8; its branch is W7-F9.
35 sealed feathers; W7 eight. W7-F10 is now allocated; next unallocated W7-F11 and W6-F10.
Chapter 1 / W4 stays paused.

## Current return checkpoint — adjacent creation/reset feather

Source checkpoint: `96ac40f`; reviewed 9 November 2026.
Karun has explicitly requested [W7-F10 — Beginning Again](W7-F10_BEGINNING_AGAIN.md)
to review creation and establish a reversible reset using Efiishent. W7-F9 is
parked until that separately reviewed work is ready. Prior prohibitions below
against resetting merely to manufacture acceptance retain their intent: no reset
has occurred, and live reset requires the concrete W7-F10 plan. A reset character
on an existing account does not verify new-account onboarding.
Existing-player handoff and activation are verified; fresh-character live
acceptance remains pending. Historical ACTIVE/deployment-pending statements below
describe their dated checkpoints, not the current status.

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
