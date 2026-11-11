# W7-F10 — Beginning Again: Character Creation & Reset

Status: REVIEW — isolated transaction rehearsal tested 11 November 2026; live adapter and execution pending.
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

## Creation and state audit — 11 November 2026

Status: AUDIT COMPLETE FOR REVIEW; reset implementation and live execution pending.
Audit baseline: f5811ab. Read-only live inspection plus isolated fictional tests.
Eight reviewed source files match their installed counterparts: arrival/core cogs,
storage, pod_opening, web_portal, router, rebirth and idle_home cog.
This is not a whole-runtime hash audit or an atomic snapshot of live data.

### Creation contract observed

| Stage | Current behaviour |
| --- | --- |
| Entry | !begin is DM-only. Existing characters are refused unless using preview. |
| Choices | Listed starting inclination (unwritten excluded), name, fictional date, body recognition and embodiment familiarity; optional background. |
| Validation | Listed class; parseable date; familiar/unfamiliar choices; field-length limits. Name uniqueness is not checked by guided creation. |
| Review | Required before awakening; editing any choice invalidates review. |
| Preview/cancel | Drafts are in memory. Preview has its own fictional character; cancellation discards the draft. Restart discards drafts. |
| Commit | Existence rechecked immediately before insertion/save, with no await between them. On save exception, insertion is removed and draft retained. |
| Beginning | Builder derives class stats, HP, astrology and mana; pod_room; empty equipment; one starter knife and jacket each if their IDs exist in the item catalogue. |
| Discovery | Guided arrival explicitly has performance_booking=false and an empty opening-discovery list. Awakening prose itself grants no inspection discoveries. |
| Clothing | No selected pod outfit is inherited. Existing wardrobe discovery and first-selection rules apply. |
| Handoff | Saved and allowlisted characters get the game-window link; preview/failed-save states do not. |
| Routing | Builder starts with no run-channel pointers. Server gameplay routing later finds/creates a channel. |

Starting values must be generated by the existing builder, not copied from
Efiishent or hardcoded from screenshots. The default is not an entirely empty
inventory: the current starter knife/jacket entitlement remains.

### Two creation paths need reconciliation

Guided !begin and legacy !create_character / !create / !cc share the builder but
are not equivalent. Legacy creation also attempts locker/vault/cube setup and run
channel routing, suppresses persistence exceptions, and does not set the guided
arrival's explicit no-booking marker. Missing performance_booking currently
defaults to eligible in pod_opening.

For this reset test, use !begin. Before calling the overall lifecycle coherent,
address or explicitly restrict the legacy entry point so it cannot bypass the
reviewed persistence and arrival contract. Preserve historical eligible characters;
do not globally reinterpret missing flags without migration review.

Run-channel reuse currently accepts a channel-name match without an ownership
check in that branch. Guided creation permits duplicate names, and a changed name
can produce a new run channel. The reset must not rely on matching a display name
to recover private-channel access. Reattach only a verified account/channel mapping,
or fix and test routing ownership first.

### Efiishent ownership findings

A unique current character named Efiishent was found; its embedded id matches
the storage account key. Raw IDs, private records and archive contents are omitted
from Git. This establishes stored identity; it does not separately verify current
Discord role membership or channel permission overwrites.

The record contains equipment/inventory, discoveries, social/work state,
HUD/idle/narrator state, recovery, pod delivery, performance/Queen/messenger/
terrace progression and thread-node history. Saved location was pod_room,
in_combat was false, recovery stage was ready, and a run channel was assigned.
These are dated disk observations, not evidence that no in-memory task exists.

Separate target-owned locker, vault and personal-cube records exist. The locker
has holdings; the vault entry is empty. The prime cube references the account
in meta.dpc_user_id and is a separate special/shared record: preserve it.

A second character JSON exists at data/characters/data/characters/characters.json
and contains a matching account record. The canonical Storage path is
data/characters/characters.json. No reset should edit the nested copy by guesswork;
identify any maintenance scripts or external readers before execution.

The bounded scan inspected readable JSON files under /opt/futuresky/data, excluding
files over 5 MB and corrupt-named files. Account-ID references were found in the
canonical and nested character records, lockers, vault and cubes. No matching
account-ID reference was found in layers, cube_sessions, combat_state or HUD
definition files. This scan does not prove absence of name-based, external,
event-ledger or in-memory references.

### Proposed concrete preserve / archive / clear / rebuild plan

| State | Treatment |
| --- | --- |
| Canonical characters[verified account ID] | Privately archive the complete record, then remove the selected entry only. Let !begin build the replacement. |
| lockers[account ID] | Archive and remove selected entry/holdings. Rebuild only through an agreed creation contract; do not leave old holdings accessible. |
| efi_vault[account ID] | Archive even if empty, then remove selected entry. |
| cubes[verified personal cube key] | Archive and remove only after validating owner.user_id against the target. Define normal recreation before execution; current Storage has no ensure_personal_cube implementation despite optional callers. |
| cube_efiishent_prime | Preserve byte-for-byte; account reference is not proof of personal-character ownership. |
| Run channel and historical messages | Preserve channel/messages/permissions. Retain verified mapping privately for controlled reattachment; do not copy narrative progress. |
| Account roles, portal allowlist, credentials | Preserve. Do not carry old character flags wholesale as a substitute for account authority. |
| Nested legacy character copy | Preserve pending reader/provenance check; treat as a preflight blocker, not a second reset target. |
| Other characters, world/room state, time and event history | Preserve; do not reset or roll back with this character. |
| Drafts, pending renewal, sequences, walking, combat, idle/ambient/narrator/scenario state | Invalidate old runtime work through a controlled maintenance boundary, then rebuild normally. |
| Web sessions and action offers | Invalidate before new character becomes playable; reload and sign in again. Browser presentation/history must not masquerade as new-character state. |

The initial implementation candidate is a short operator-managed stopped-service
transaction, not hot edits to running JSON. Web sessions and pending actions live
in process memory; a restart invalidates them but also signs out other portal users
and interrupts their transient activity. This operational impact must be disclosed
and scheduled; preserving other players' persistent data does not mean zero
interruption. Do not rewind the world clock or change its elapsed-time policy.

Capture exact before-images and presence/absence for each selected entry, schema
and source versions, and file integrity data in a private archive. Preflight must
refuse ownership mismatch, stale expected records, unsupported schemas or changed
source assumptions. Use a recoverable multi-file transaction journal; individual
atomic JSON replacements do not make the four-store operation atomic.

Before resuming the service, validate all selected changes and unchanged unrelated
entries. After a failure/interruption, keep play blocked until either the complete
reset or the complete rollback is verified. Never partially resume.

Restore must first archive any replacement character and its holdings. Reject
conflicting ownership, and restore only the selected entries. Do not resurrect
old pending tasks or authentication tokens. Shared-world consequences since reset
are outside character restoration; time-based records require explicit validation
against the current world clock.

### DPC test limitation

Efiishent's record has an is_dpc marker. Runtime gated-command bypass uses Discord
administrator permission or the DPC role, not that marker. Actual role membership
was not queried in this audit. Keep account authority unchanged and verify it
before the walkthrough. If the account has that bypass, a successful Efiishent run
proves fresh-character state but cannot prove ordinary-user command restrictions.
Use fictional non-DPC tests (or a separately authorised participant) for that claim.

### Verification performed

Existing isolated tests rerun:
PYTHONPATH=bot:tests /opt/futuresky/.venv-web-pilot-20261029/bin/python
-m unittest test_arrival test_web_arrival -q

14 tests passed. Coverage includes preview isolation, review invalidation,
existing-character protection, failed-save retry, validation/cancellation,
authorised handoff, no unearned booking, and a fictional fresh HTTP journey through
discovery, first clothing, walking and a new session.

These tests do not exercise a reset or restoration implementation; none exists
from this audit. No live commands, reset, service restart or character writes were
performed. No private archive has yet been created.

### Review decisions and next executable step

Recommended: retain the existing guided creation choices; use a full fresh
character rather than a partial progress wipe; preserve account access, the private
run channel and the prime cube; quarantine old personal holdings in the archive.

Before live execution, resolve legacy creation save/booking behaviour, personal-cube
recreation, private-channel ownership/reattachment, and the nested record's readers.
The next bounded step is implementing and testing archive/reset/restore in isolated
fixtures against this manifest, including those preflight blockers. Present the
tested operator plan and target for live approval only after it is concrete.
W7-F10 stays unsealed; W7-F9 stays parked; 35 sealed unchanged.

## Isolated transaction rehearsal — 11 November 2026

Implemented in [tools/character_reset_rehearsal.py](../../tools/character_reset_rehearsal.py),
with [fictional tests](../../tests/test_character_reset_rehearsal.py).
This is the first implementation checkpoint, not a production reset command.

The harness creates its own private temporary directory from four supplied
fictional dictionaries. It accepts no existing data-root path, has no live CLI,
imports no bot runtime, and cannot attach to the service through its public API.
Closing the harness removes its disposable archives. No real personal records
were used as fixtures or committed to Git.

### Implemented and tested

- Account-key and embedded character-ID agreement; selected personal-cube owner
  and type validation. Name is never the reset selector.
- Selected-record archives preserve absent versus empty entries and include a
  format version and SHA-256 integrity check. Archives are mode 0600 inside a
  mode-0700 directory. Checksums detect damage; they are not signatures.
- Plans are checked against the complete current four-store snapshot before
  mutation. Recomputed plans reject altered unrelated entries, even with a
  recomputed checksum. These are single-writer rehearsal guarantees.
- Reset removes only the selected character, locker, vault and personal cube.
  The prime cube and unrelated entries remain structurally identical.
- Restore first archives the current replacement records, including presence/
  absence, then reinstates the selected archived records. A subsequent restore
  of that replacement is tested.
- A durable journal is written before store changes. Each file uses temporary
  write, file fsync, replacement and directory fsync. Journal removal follows
  post-write verification.
- Any unresolved journal blocks further planning/apply/archive operations.
  Rollback validates every store against its before/after image before writing;
  unexpected contents block recovery rather than overwriting another writer.
- Rollback can resume from disk without the original in-memory plan and can
  itself be interrupted and retried.

### Evidence

Command from the repository root:

```sh
PYTHONPATH=.:bot:tests /opt/futuresky/.venv-web-pilot-20261029/bin/python   -m unittest test_character_reset_rehearsal test_arrival test_web_arrival -q
```

**29 tests passed:** 15 reset-rehearsal tests plus the existing 14 arrival/web
arrival tests. Failure cases include interruption after each of the four writes,
archive failure, store-write failure, interrupted rollback, stale plans,
tampered archives/journals, ownership mismatch, unexpected external changes,
replacement preservation, and refusal of filesystem-path inputs.

These are simulated exceptions and file-level recovery checks, not physical
power-loss testing. They do not establish live-service exclusion, stale-session
invalidation, source-version compatibility, or a fresh Efiishent walkthrough.
No bot source was modified, no service restarted, and no live data or private
live archive was created.

### Remaining production boundary

Do not turn this harness into a live tool merely by adding a path argument.
A production adapter still needs exclusive maintenance/service-stop verification,
persistent private archive placement and retention, source/schema/file metadata,
reviewed target identity and channel mapping, and the concrete blocker resolutions
from the audit. Rehearsal journals hold full fictional store before/after images;
production journals would contain other players' private data and require explicit
bounded retention and handling. Recovery must never replay a whole-store journal
after normal play has resumed.

The nested legacy file, channel ownership/reattachment, legacy creation contract,
personal-cube recreation, time-sensitive restored records and actual DPC role
remain unresolved live preflight items. The bounded repository search found the
canonical path in config, recovery capsule and portal deployment helper; it did
not establish provenance or external readers for the nested file.

Next: resolve those lifecycle boundaries, then build the stopped-service adapter
and its preflight checks. Present the exact Efiishent execution plan before a live
reset. W7-F10 remains unsealed; W7-F9 parked; 35 sealed unchanged.
