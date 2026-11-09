# W7-F10 — Beginning Again: Character Creation & Reset

Status: DRAFT FOR REVIEW — 9 November 2026.
Home: W7 Engine. Adjacent to W7-F9 — Waking Into the Window.
Allocated on Karun's instruction; scope remains a review draft.
Branch: engine/w7-f10-beginning-again. Baseline: 96ac40f.
Checkout: /home/efiishent/future-sky-worktrees/w7-f8 (folder name retained).
Authority: [Wing Index](../WING_INDEX.md),
[eight-wing charter](../current/EIGHT_WINGS_CHARTER.md) and
[feathering protocol](../archive/process-history/R3GPT_FEATHERING.md).
W7-F9 is parked and unsealed while this proposal is reviewed.
No reset or deployment is authorised by this document alone.
Chapter 1 / W4 remains paused. No sealed-count change.

## Intention

Make beginning a life in Future Sky coherent, deliberate and repeatable.
A player should understand whether they are creating someone new, continuing
an existing character, recovering the same person, or choosing a fresh start.

Use Efiishent to establish a trustworthy, reversible fresh-start procedure.
Then return to W7-F9 and verify the creation-to-HUD journey with genuinely fresh
character state. A reset existing account is evidence of fresh-character behaviour,
not evidence of first-time Discord/OAuth account onboarding.

## Existing foundation

- Guided Discord !begin provides creation, review and awakening. Existing saved
  characters are protected against replacement.
- !awaken restores bearings; it does not create a fresh character.
- !scenario_reset clears in-memory scenario runtime only.
- Bodily recovery preserves continuity and secures possessions.
- Recovery capsules provide private bounded backups and disposable restore checks.
  They are not yet a targeted character archive/reset/restore transaction.

These mechanisms remain distinct. No full character reset was found in the
reviewed paths; the ownership audit must establish the complete affected state.

## Bounded outcome

One reviewed creation contract and one operator-controlled, reversible reset
procedure, exercised with Efiishent. Retain the existing creation interface and
rules, correcting inconsistencies only where necessary for this lifecycle.

### 1. Review the creation contract

Trace preview, choices, review, cancellation, save and awakening. Document which
choices are player supplied, which values are defaults and which facts are earned.
Check identity, inclination, embodiment/background, starting location, stats,
possessions, wardrobe entitlement, discoveries and booking eligibility against
existing authority. Do not invent defaults or grant narrative knowledge.

A cancelled preview leaves the saved character untouched. Awakening creates one
durable character. Repeating the request must not duplicate characters or rewards.

### 2. Map ownership and prepare a reset plan

Identify Efiishent by verified account ID, not display name alone. Inspect the
character record, separately stored personal holdings, pending actions, scenario
state, idle/recovery state and web sessions/caches.

Produce an exact preserve / archive / clear / rebuild list with evidence.
Unknown ownership blocks mutation of that state until resolved.

Preserve account identity, authorised access and other players' data. Keep the
shared world and clock running according to their existing rules; do not rewind
world history or remove past Discord messages. Name/date may be chosen again
through creation; they must not silently carry progression into the new character.

### 3. Archive and prove restoration

Create a private, versioned archive of the selected character-owned state with
integrity checks and a clear restoration manifest. Keep personal records out of Git.

Rehearse restoration in an isolated copy before touching live state. Establish
how conflicting new progress is handled: preserve the replacement character first,
then restore deliberately. Restoration must not roll back the shared world or
another player. Document any irreversible shared-world effects outside its scope.

### 4. Execute a deliberate fresh start

Present the concrete target and state-change plan for operator approval.
Apply changes with writes safely controlled, not by editing live JSON underneath
the running bot. Invalidate stale sessions, action tokens and cached state as needed.

The account should then enter the genuine creation flow. A failed or interrupted
operation must have a tested recovery path and must not leave a playable mixture
of old and new character state.

### 5. Verify with Efiishent

Archive the existing character, perform the approved reset, complete creation,
awaken and open the HUD. Verify that old inventory, knowledge, deliveries, recovery
state and rewards do not leak into the new life.

Verify intended starting values, one first-outfit entitlement, consistent Discord
and HUD views, and persistence after a new session. Keep restoration available.

## Acceptance evidence

- Reviewed creation contract and complete targeted ownership map.
- Cancellation, duplicate submission and failed-save checks.
- Verified private archive and isolated restore rehearsal.
- Reset failure/interruption and stale-session checks.
- Efiishent walkthrough with expected versus observed starting state.
- Evidence that unrelated player records and shared state were not reset.
- Clear separation of automated, directly observed and operator-reported results.

Document limitations honestly; no seal based only on a successful visual walkthrough.

## Outside this feather

New classes, lore, Chapter 1 progression, rebirth cosmology, creation artwork,
a new web creation interface, public access expansion, general account deletion,
and unrestricted player-facing reset commands.

Bodily recovery remains same-person recovery. This test/reset capability does not
establish new in-world canon about death, memory or reincarnation.

## Cross-wing return

W3: identity and creation choices.
W4: earned story knowledge and booking eligibility; chapter stays paused.
W5: world continuity and ownership boundaries.
W6: existing creation presentation and accepted HUD layout.
W8: private archives, access boundaries and honest evidence.
W7 owns implementation and the single feather count.

## Return to W7-F9

Resume Waking Into the Window after review of this feather's acceptance evidence.
Use the fresh-character run to assess the saved-character handoff, discovery,
first clothing selection, departure and return. Track new-account authentication
separately where it has not been observed. W7-F9 is not automatically sealed by
completion of W7-F10.

## Decisions for review

Recommended baseline: operator-controlled reset; full fresh progression; same
Discord identity and existing access; old character privately restorable; existing
creation journey retained. Resolve any creation-rule changes during review before
implementation. No live character data has been changed for this draft.

## Documentation review — 9 November 2026

The charter requires outcome, boundary, dependencies, status, evidence and return
checkpoint, with complete files and commits rather than chat memory alone.
Recent W7-F7, W6-F9, W7-F8 and W7-F9 records exist in Git; several first appear
alongside implementation. Their existence must not be confused with a separate
pre-implementation review checkpoint. This draft initially existed only as an
untracked working file; this documentation change corrects that omission.

For this feather: commit and push the complete proposal and register checkpoint,
provide the Git review link, incorporate Karun's review, then implement the agreed
scope. Later record verification and deployment separately, and update the register
in the same change as an authorised seal. Draft publication is not scope approval.
