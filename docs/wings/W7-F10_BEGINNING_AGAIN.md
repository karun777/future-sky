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

## Private play spaces and permeable world — 11 November 2026

Karun reaffirmed the original intention: each player has an isolated play area,
with a permeable boundary through which the multiplayer experience is delivered.
The private run channel belongs to the account's play space. A character reset
must preserve that space and its history while replacing character progression.
This is operational continuity, not new narrative canon.

### Existing permeability retained

Speech delivers to the run channels of players in the same resolved room;
characters inside cubes are excluded by that audience selection. Emotes use
presence to find other room occupants and deliver to their individual channels.
Whispers require shared room presence; tells address an explicit player.
Selected creation, movement and combat events use the realm feed. These audience
rules and shared-world state have not been rewritten in this change.

Channel access is distinct from world interaction. Seeing another player's
speech or entrance does not require access to their private command history,
inventory or inward narration. Explicit visitor grants are not automatically
treated as proof of channel ownership.

### Ownership implementation

[Router](../../bot/fsbot/cogs/router.py) now:

- Resolves the recipient guild member from the target account ID. Previously,
  creation used ctx.author even when speech/emotes were creating a recipient's
  channel. That could grant the speaker access instead of the recipient.
- Checks saved mappings before delivery: same guild; configured category when
  present; explicit target visibility; everyone denied; no extra human grant,
  non-admin role visibility grant, or conflicting saved character claim.
  Bots and Discord administrator access remain platform exceptions.
- Recovers an unmapped channel only from a unique verified recipient permission
  pattern in the configured category. A changed/duplicate character name is
  irrelevant. Ambiguity blocks adoption; permissions/history are not rewritten.
- Serializes creation per guild/account, rolls back an in-memory mapping when
  its save fails, and can recover the newly created channel on retry.
- Uses the same verification for canonical non-creating/background lookup.
- Sends routed private command output to the caller's DM if no verified run
  destination can be resolved; failed DM delivery does not expose that payload
  in the public or another player's command channel.

This is a bounded legacy permission-based ownership check, not a new account
registry or a general visitor/party permission system. If deliberate visitor
access is needed later, it requires an explicit owner binding separate from
permission grants. No existing channel grants were removed.

### Read-only Efiishent Discord evidence

Discord GET requests, canonical stored identity and service configuration were
checked directly. No messages, edits, invitations or permission changes were
sent. Credentials and raw account/channel IDs are omitted from Git.

Observed: stored account ID matches the character; account is a guild member;
saved destination is a text channel in a category of the same guild; exactly one
saved character claims it; target has explicit view access; everyone is denied;
no additional human view grant or non-admin role view grant; seeded-channel
pointer matches. Existing channel ownership is therefore supported by both the
stored mapping and its permissions. Preserve its ID, history and seeded marker
in the private reset manifest; verify again immediately before any execution.

**Configuration gap:** FS_PLAYERS_CATEGORY_ID is absent from the running process
environment and the bot's dotenv file. The earlier audit's category comparison
returned false because this setting was absent, not because a different configured
category was found. Existing saved-channel routing historically did not need it.
The revised router preserves verified saved mappings with that setting absent,
but refuses new creation/discovery without a configured category. Before reset,
the operator must configure the verified existing Players category and review all
mapped destinations against it. No service configuration was changed here.

**DPC clarification:** the account has neither a DPC role nor an administrator
role, but it is the guild owner. Discord owner permissions therefore still give
administrator authority; ordinary-user gating remains a separate test claim.
This supersedes the earlier audit's unverified role limitation.

### Validation and activation boundary

17 fictional router tests cover cross-player creation, duplicate names, renamed
character recovery, wrong owner/guild/category, conflicting and ambiguous claims,
public/role/visitor grants, missing member/category, failed persistence, concurrent
creation, shared speech audiences, background refusal and private DM fallback.
The full Python suite passes: **394 tests**. Deployment-script output during that
suite belongs to temporary fixtures; it is not a production deployment.

Only repository source/tests/docs changed. The live service remains active on its
existing code; Efiishent is untouched. The router change is ready for the reviewed
deployment procedure, not yet activated. Live ownership is verified as a dated
observation; post-deployment Discord delivery and reset reattachment remain to be
observed. This does not certify every historical helper outside the canonical
router as a complete privacy audit.

Next: supply the missing category in the eventual operator configuration step,
resolve legacy creation and personal-store/nested-file boundaries, and finish the
stopped-service reset adapter. W7-F10 stays unsealed; W7-F9 parked.

## Players category staging and wider mapping audit — 11 November 2026

On Karun's instruction to reconnect the Players category, read-only Discord
inspection identified the existing category named **🌀 Player Runs**, using
Efiishent's verified channel parent. Its numeric ID is staged outside Git at
/home/efiishent/.config/future-sky/players-category.env (mode 0600).
The active bot dotenv, systemd configuration, service and Discord permissions
remain unchanged. Category staging is not activation.

The wider audit examined all five saved run-channel mappings:

| Character | Observation |
| --- | --- |
| Efiishent | Existing channel in Player Runs; explicit access belongs to the recorded account. |
| The Dark Rat Queen | Existing channel in Player Runs; explicit human access belongs to Efiishent's account, not the account stored for this character. |
| wanderer-9551 | Saved channel returns Discord 404. |
| wanderer-3616 | Saved channel returns Discord 404. |
| wanderer-0466 | Saved channel returns Discord 404. |

No alternative explicit-owner channels were found for the Queen or the three
wanderers. Efiishent has explicit grants on two category channels: its own and the
Queen's. The current router's conflicting-saved-claim check prevents silently
adopting the Queen's channel as Efiishent's reset destination.

These observations do not establish whether the Queen's access is an old
broadcast-creation bug or an intentional operator arrangement. Ask Karun whether
the Queen is another person's player character or an operator-controlled persona,
and establish intended ownership before changing any grants/mappings. Do not infer
ownership from character name or grant another account the existing history.

The three 404 results mean the bot cannot currently retrieve those saved channels;
they do not alone prove deletion rather than loss of visibility. Preserve records
until ownership/lifecycle is reviewed. No cleanup or recreation occurred.

Activation of the ownership-aware router would refuse the Queen's present mapping
and unresolved wanderer mappings. Therefore do not activate it as an apparently
transparent category-only change without addressing or explicitly accepting those
delivery effects. Next return: resolve the Queen's ownership intent, then prepare
the reviewed router/category activation. Production activation needs the operator's
privileged terminal; remote sudo execution is unavailable. No reset, seal or
sealed-count change.


## Ownership clarification and reset preview — 11 November 2026

This checkpoint supersedes the earlier request to establish whether the Queen is
an operator persona. Karun confirmed **The Dark Rat Queen is another person's
player character**. Preserve that account, its character, channel, history and
existing grants. Its access issue is parked separately from Efiishent's reset;
no permission repair or reassignment is authorised here.

A subsequent read-only Discord check matched the stored character/account ID and
queried the member, guild roles, guild ownership and saved channel overwrites.
The Queen has @everyone and DPC; neither grants Administrator. The account is not
the guild owner and has no individual channel overwrite. Applying role and member
overwrites yields View Channel=false. Send/history bits do not overcome missing
visibility. The DPC role therefore confirms developer status, but does not supply
access to the saved channel. This establishes current access, not the historical
intent or cause. No messages or Discord mutations were made.

### Router revision, source only

Saved association and access are separate. A saved, uniquely claimed channel can
retain an explicit guild-owner/Administrator operator grant. A saved recipient
who is a guild owner/Administrator can use effective access without an individual
allow. Actual platform permissions are used, never the DPC label. Discovery still
requires explicit recipient access and conservative private-channel checks;
administrator visibility alone cannot adopt a channel. Conflicting saved claims,
public/non-admin-role visibility and unapproved non-admin visitor grants remain
refused. The router never edits existing grants to make a check pass.

This does not resolve the Queen's absent visibility or change live routing.
A fleet deployment still requires review of delivery effects for her and the
three unavailable wanderer channels; parking these issues is not acceptance of
silently breaking their delivery. Category configuration stays staged only.

24 fictional routing tests pass, including seven new administrator/owner/DPC,
visitor and conflicting-claim cases. Full suite: **401 tests passed**. Activation
messages in test output are from disposable deployment fixtures, not production.

### Efiishent reset preview for review

This is a concrete state-treatment preview based on the dated ownership audit,
not an executable live plan or a request to approve execution now. Exact account
and channel IDs, before-images and hashes belong in a private manifest produced
by the future stopped-service adapter; none are embedded in this document.

| Component | Proposed effect |
| --- | --- |
| Efiishent canonical character entry | Archive complete entry; remove only verified account key. Old stats, inventory/equipment, discoveries, booking/performance progression, recovery, delivery and character flags do not transfer. |
| Selected locker and vault | Archive presence and values, including empty vault; remove selected entries so old holdings cannot be reclaimed. |
| Selected personal cube | Archive/remove only after owner and personal-cube type validation; normal recreation contract remains a blocker. |
| Efiishent prime cube | Preserve; special/shared cube is outside reset. |
| Discord identity, roles, allowlist and credentials | Preserve account access. Guild-owner status remains; this is not an ordinary-user permissions test. |
| Verified own run channel and seeded marker | Preserve channel, grants and history; retain mapping separately for controlled reattachment to the replacement without importing old progression. |
| Queen and all other players | No persistent record, account, grant or channel changes. |
| Shared world, clock and event history | Preserve; no rewind or deletion of historic messages. |
| Nested legacy character copy | Preserve; resolve its readers/provenance before reset. |
| Runtime actions, drafts and portal sessions | Controlled stop/restart clears stale process state; all portal users must sign in again and transient activity is interrupted. |
| Replacement character | Create through reviewed !begin, with fresh chosen identity and builder-derived starting state; retain existing starter knife/jacket entitlement, no inherited outfit or earned booking knowledge. |

Execution order once blockers are resolved: stop service and verify no other
writers; capture private archive and exact manifest; rehearse restoration from
that snapshot in isolation; apply the validated journalled selected-entry reset;
verify unrelated records and shared state unchanged; resume only after complete
success or complete rollback. Reauthenticate, create/review/awaken, reattach the
verified own channel, compare Discord/HUD and check fresh rewards/discoveries.

Restoration first archives any replacement character and personal holdings, then
restores only the selected old entries. It must validate time-dependent state
against the current world clock and never restore old sessions/tasks or rewind
other players. An unresolved journal keeps play blocked until recovery completes.

**Remaining execution blockers:** legacy creation persistence/booking consistency;
personal-cube recreation; nested-file reader/provenance check; persistent channel
reattachment across the no-character interval; production single-writer adapter
and archive/restore validation; reviewed router deployment effects and maintenance
window. The isolated harness is tested but is not a production reset tool.

Next bounded implementation step: resolve those lifecycle boundaries and build
the stopped-service preflight/adapter. Present its exact private target manifest
and maintenance impact before requesting live-reset approval. W7-F10 remains
REVIEW/unsealed, W7-F9 parked, 35 seals unchanged. No live reset, archive, restart,
configuration activation or code deployment occurred in this checkpoint.


## Lifecycle checks resolved in source — 11 November 2026

Repository changes only; not deployed. This checkpoint narrows the remaining
work to the production reset adapter and its operational acceptance.

### One reviewed creation path

Legacy !create_character / !create / !cc now redirect to DM !begin, including
when called without arguments. Existing-character protection remains. They no
longer create partial bridge stores, suppress failed saves, announce success or
bypass the guided review/no-booking contract. Missing-character prompts in core
now point to !begin. Existing historical characters are not migrated.

Historical opening tests now construct explicit pre-guided fixtures rather than
calling the disabled legacy command. They retain their earned/discoverable booking
assertions; guided-arrival tests separately prove no unearned booking. This is an
intentional entry-point restriction, not a change to historical story eligibility.

### Personal-cube lifecycle

Storage now provides get_cube, get_personal_cube and ensure_personal_cube.
Personal lookup validates key/id, personal_cube_v0 type, player owner type and
account ID. Ensuring requires a matching character, refuses conflicting ownership
or another personal record claiming the account, preserves existing holdings,
and durably creates a missing cube before returning its ID. Failed persistence
removes the tentative in-memory insertion and permits retry.

Recreation is lazy through the existing cube/rebirth callers. It uses the existing
v0 marker shape: integrity 100/100, empty flags, fresh timestamps and no old stash.
The new helper does not create a prime cube, change shared state or add character
session fields. The established cube command may perform an additional save;
that is idempotent after initial durable creation. Guided creation remains a
single-character save, not a new multi-store transaction. Old locker/vault entries
will be archived/removed by reset; no old holdings or bridge-store defaults are
silently copied into guided creation.

### Durable channel reattachment across reset

A new read-only bridge accepts an operator-owned receipt at the canonical
relative path data/storage/reset_run_bindings.json. No such live file was created.
The future stopped-service adapter must write it privately and include it in its
transaction/rollback manifest. Format: version=1 and bindings keyed by verified
account ID; each binding contains only run_channel_id and run_seeded_channel_id.
Unknown fields, malformed IDs/seed markers, duplicate receipt channel claims and
another saved character claiming that channel block creation without losing the
guided draft. Character names are irrelevant to this binding.

Guided creation copies only these two routing fields immediately before its
existing durable character save. Preview does not read/apply the receipt. A failed
save removes the tentative character and retains the draft; the receipt remains
available for retry/restart. Receipt retention is intentional until the operator
verifies the replacement and retires it through the adapter. It contains no old
inventory, story state, roles or class values. Router checks still validate actual
Discord access/category and competing claims before delivering output.

This is not user-supplied input or permission to attach arbitrary history. The
adapter must validate account/channel ownership immediately before writing the
receipt, prohibit new conflicting bindings and preserve/restore any prior receipt
on rollback. Its file permissions and writer exclusion remain implementation
requirements for the adapter, not claims already proven by the read-only bridge.

### Nested character file: bounded provenance result

The service WorkingDirectory is /opt/futuresky/bot; canonical config resolves
characters to /opt/futuresky/data/characters/characters.json through bot/data.
The nested file data/characters/data/characters/characters.json was last modified
22 June 2026 at 15:21:53 UTC. No direct nested-path reader was found in checked
runtime bot/tools, checkout tools, readable systemd units or cron.d scripts.
The service account has no crontab; listed system timers showed no Future Sky
maintenance job. These checks support treating it as a noncanonical historical
copy. They do not prove who created it or exclude every external/dynamic reader.

Resolution: preserve the nested file byte-for-byte and never use it as a reset
source or target. Pin canonical resolved paths and hashes in preflight; record and
verify the nested file remains unchanged. If an active external reader/writer is
found during final maintenance checks, stop rather than expand reset scope.
No deletion, migration or speculative synchronisation is required.

### Evidence and remaining boundary

**417 Python tests passed**, including new legacy redirect, cube durability,
ownership, failed-save retry, reset receipt validation, binding failure and guided
save/retry tests. Existing historical opening, fresh arrival, web, routing and
reset-rehearsal coverage passes. Test activation messages refer to temporary
fixtures, not the running service.

Next: build the stopped-service adapter that captures current private records,
creates/restores the routing receipt, journals selected state changes and enforces
single-writer/path/schema/hash checks; exercise it on isolated captured-state
copies before a concrete live approval. Resolve router deployment delivery effects
separately; the Queen and other players' persistent records/grants remain protected.
No production restart, deployment, reset, receipt or archive was made. W7-F10
remains REVIEW/unsealed; W7-F9 parked; 35 seals unchanged.


## Stopped-service adapter built and rehearsed — 11 November 2026

Implemented [tools/character_reset_adapter.py](../../tools/character_reset_adapter.py)
and [22 adapter tests](../../tests/test_character_reset_adapter.py). The original
fictional transaction harness remains available. Runtime receipt validation is now
a shared pure function used by both guided creation and the adapter.

### Transaction contract

The production CLI has fixed canonical paths: /opt/futuresky/data and the private
operator directory /home/efiishent/.local/state/future-sky/character-reset. It
requires a root operator terminal for process inspection and preservation of file
ownership. It never stops, starts or restarts the service. Plan/apply/recover all
require the bot to be inactive/dead with MainPID=0; writable data descriptors and
detached bot processes are additional refusal checks. A nonblocking exclusive
adapter lock prevents concurrent adapter instances. This is not a global lock on
arbitrary external programs: the operator must maintain a single-writer window.

Preflight rejects symlink/redirection, nonregular or hardlinked store files,
missing stores, malformed identity/schema, additional personal cube claims,
conflicting channel bindings and unsupported private receipt permissions. Current
live lifecycle/router source must match the reviewed checkout before plan/apply.
Plans pin that runtime contract; changed code or data invalidates the plan. Known
service/dotenv world-reset-on-boot flags are checked. Restart configuration still
requires operator review before resuming; no automatic restart is attempted.

Plans capture exact bytes and metadata for characters, lockers, vault, cubes and
the reset receipt. Reset changes only the selected account entries and inserts
its verified saved-channel receipt. All other data files are hashed, including
the nested character copy and world-clock files. Other entries inside shared
stores are preserved structurally; JSON formatting may change for a modified
store. Existing file owner/group/mode are retained; a new receipt is mode 0600.

Before mutation, the selected records are archived and a durable journal is
written. Each file replacement is atomic and fsynced, followed by directory fsync.
The journal remains until complete after-state/protected-file verification and a
private completion record succeed. Interrupted recovery restores exact before
bytes/metadata, including absence of a newly created receipt, and can itself be
interrupted and retried. Unexpected concurrent contents block recovery without
blindly overwriting them. Never resume play with an unresolved journal.

Restore archives the current replacement first, then reinstates only the chosen
archive's selected entries/receipt. Current progress of other players is retained.
Restore does not resurrect sessions/tasks or roll back time. Time-dependent old
character fields must be reviewed against the current world before service resume.
Archive checksum identifies content and detects damage; it is not authentication.
These root-owned mode-0700 directories/mode-0600 files are the access boundary.

The private journal/completion records contain full before/after shared-store
snapshots to enable exact rollback, including other players' records. Keep them
outside Git and retain only for the reviewed recovery period; never publish their
contents. Selected-record archives alone are insufficient for interrupted-write
rollback. No automatic retention deletion is implemented.

### Rehearsal evidence

Full command: PYTHONPATH=.:bot:tests /opt/futuresky/.venv-web-pilot-20261029/bin/python
-m unittest discover -s tests -q. **439 tests passed**, including 22 adapter tests.
New tests cover reset/restore, replacement archiving, unrelated new progress,
interruptions after every one of five writes, reopened recovery, interrupted
rollback, stale/crafted plans, changed runtime contracts, protected-file changes,
external writers, archive/store-write failures, damaged archives/journals,
ownership/cube/channel conflicts, existing receipts, path/ID/mode checks, exclusive
locking and active-service refusal. These are injected failures, not physical
power-loss or adversarial external-writer race proofs.

A separate private-copy rehearsal used the current server data: 61 files, about
347 MB. Source/copy hashes were compared before rehearsal. In a mode-0700 temporary
directory, Efiishent was selected uniquely and its embedded account ID checked;
reset, receipt creation, selected restoration and interruption after the fifth
write followed by exact rollback all passed. Other player entries and prime-cube
values were unchanged; protected files including nested characters and world clock
were byte-identical. Temporary copied data and all rehearsal archives were deleted.
Live hashes were unchanged afterward and the bot retained the same nonzero PID.
This was a stable disk-copy observation, not an atomic running-process snapshot.
It proves compatibility with captured disk state, not live cache invalidation.

The actual read-only offline guard was also run against the active service and
correctly refused it. No production CLI apply or recovery was invoked, no service
was stopped, and no production archive or receipt exists from this work.

### Operator sequence for the later approved execution

1. Review lifecycle/router deployment and its effects on every saved mapping.
   Queen access and the unavailable wanderer channels remain separate issues;
   do not silently deploy changed delivery semantics as part of a reset.
2. Reverify Efiishent's account/channel in Discord, approve the exact scope and
   maintenance impact, and install the reviewed source through controlled deployment.
3. In the privileged operator terminal, stop the service and exclude other writers.
   Confirm no world reset will run on restart. Use the adapter module with the
   repository root and bot on PYTHONPATH; do not run it from a different checkout.
4. Run plan with the verified numeric --account and exact --expect-name. Inspect
   its private manifest; the printed plan ID is its exact integrity fingerprint.
5. Apply only that reviewed --plan-id. The adapter rechecks code/data and archives
   before changing state. It leaves the service stopped. On interruption, run
   recover before any other action; inspect unexpected-content refusals manually.
6. Verify results, resume under the reviewed configuration, reauthenticate and
   complete guided !begin. The receipt restores routing fields in the same save
   as the replacement character. Compare Discord/HUD and verify fresh progression.
7. Keep the receipt until the new binding and seeded marker are durably verified;
   retire it deliberately during maintenance. Retain the original selected archive
   for the agreed restore window. Receipt retirement is not part of this adapter.

For a later restore: stop/exclude writers again, plan with --restore ARCHIVE_ID,
--account and the replacement's exact --expect-name (or the known target label if
no current character exists), inspect, then apply the new plan ID. The replacement
is archived first. Review restored time-dependent state before resuming.

**Next checkpoint:** review deployment compatibility and the concrete maintenance
plan before live execution approval. Adapter built/rehearsed does not authorise a
live reset. W7-F10 remains REVIEW/unsealed; W7-F9 parked; 35 seals unchanged.

## Pinned-router deployment prepared — 11 November 2026

Review found that the adapter's earlier runtime check required the stricter branch
router. That would alter behaviour for Queen's saved mapping, contrary to the
agreed parked grant issue. This checkpoint supersedes that deployment dependency.

The new [operator runbook](../../tools/deploy/w7f10/README.md) and manifest deploy
only five lifecycle files. The current live router v3.6.4 and remaining Python
dependencies are hash-pinned and excluded from the overlay. Category configuration
stays unset. The reset adapter accepts this reviewed installed package, includes
its manifest and adapter/rehearsal code in the plan contract, and rejects drift.

The installer never stops/starts services. It requires the offline guard, retains
a private recoverable code transaction before the first write, preserves data,
and provides code-only rollback. Rollback refuses changed data, including a
completed reset; interrupted reset recovery must precede any code rollback.
Completed selected-data restore remains a separately reviewed adapter transaction.

**456 tests passed**, including 17 new deployment, positive stopped-service fixture
and pinned-router compatibility tests. Five-write interruption/rollback, retry,
drift, changed data/code, corrupt journal, failed backup and active-service refusal
passed. A hash-matched live-router fixture routes fictional receipt-bound output
to its saved channel with category unset, without creating channels, changing
other mappings or reseeding. This is scoped compatibility, not broader router
repair. The real read-only deployment hash check passed. Service remained active
with PID 1016603; no live deployment, reset, grant/config change or messages.

Next: review the concrete maintenance sequence, reverify Efiishent account/channel,
then operator-approved stop/install/archive/reset/restart and DM !begin acceptance.
The brief shared-service interruption and reauthentication are explicit. Queen's
persistent account, grants and current routing behaviour stay unchanged.
W7-F10 REVIEW/unsealed; W7-F9 PARKED; 35 seals unchanged.

## Live reset and restart verified — 11 November 2026

Karun explicitly approved maintenance and ran the privileged commands in the
Neptune Lounge SSH terminal. The installer reported its code transaction verified;
the reset adapter reported its transaction verified, a private before-archive
created, and other players' persistent records/protected files unchanged.
The private plan and archive remain on the server; their contents are not in Git.
No character creation or receipt retirement has occurred at this checkpoint.

After operator restart, direct read-only checks confirmed:
- service active/running with new PID 1028397;
- Discord login recorded for that process, with no traceback in its current logs;
- five lifecycle files and pinned router/dependencies match the deployment manifest;
- local and public /play/ return 200; anonymous local /play/api/me returns 401;
- the selected character, locker, vault and personal cube records are absent;
- the receipt is readable by the service account and passes the runtime validator,
  preserving the independently verified channel ID and seeded marker.

The other-player/protected-file preservation statement above is supported by the
operator's successful transaction output; post-restart checks did not reopen the
root-private before-archive. No Discord permissions or category configuration were
changed. The broader strict-router change remains excluded.

Next is player acceptance: Karun sends !begin in a DM to Future Sky, completes the
guided draft and review, then awakens. Verify fresh progression, the same private
channel without duplicate welcome/creation, and Discord/HUD agreement after login.
Keep the reset receipt until the replacement binding is durably verified; retain
the original archive. W7-F10 remains REVIEW/unsealed, W7-F9 PARKED, 35 seals.

## Saved channel verified after awakening — 11 November 2026

Read-only canonical-store verification confirms the saved replacement character's
account ID and name match the private pre-reset proof. Its run_channel_id and
run_seeded_channel_id exactly match both that proof and the retained reset receipt.
No other saved character claims the channel. Receipt validation passes against the
current character store. This verifies durable binding reuse, not a channel-history
audit or proof that no duplicate channel exists elsewhere in Discord. No game data,
Discord permissions or receipt were changed by this check.

Karun's supplied playcheck shows guided creation through awakening, the web handoff,
correct character profile, empty quest log, and one Rusty Knife plus one Leather
Jacket with nothing equipped. Discord !look returns the fresh pod opening. Retained
issues: the post-awakening embed still shows the temporary-draft footer, and the web
opening suggests panels instead of Discord's hands/garment/pod guidance. These remain
unresolved; W7-F10 REVIEW/unsealed, W7-F9 PARKED. Receipt retained pending deliberate
maintenance retirement; original archive retained.

## Playcheck corrections prepared — 11 November 2026

Saved awakening now confirms persistence; preview keeps its temporary-draft footer. Web opening guidance is restored. Hands, garment and pod are offered alongside panels; follow-on inspections reuse shared authored guidance and saved discoveries. Reads remain passive, with wardrobe/booking gates and stale-token checks intact.

459 Python tests and 25 Node browser-script tests passed. Node tests exercise DOM behavior, not visual browser rendering. Exact three-file installation and rollback passed in temporary code with fictional data. Live baseline verification passed. Service remains active at PID 1028397; no live code/data/channel/receipt/service changes occurred.

Deployment awaits privileged terminal installation; see tools/deploy/w7f10_playcheck/README.md. The historical reset contract remains unchanged and will intentionally refuse another reset/restore after this hotfix until a new runtime contract is reviewed. Do not repeat character reset to test the footer. W7-F10 REVIEW/unsealed, W7-F9 PARKED, 35 seals. Receipt and original archive retained.

## Playcheck corrections live — 11 November 2026

Karun reports completing the privileged installation/restart. Direct read-only
verification confirms all three delivered files and preserved code/HUD asset pins
match the reviewed package. Public game.js also matches the delivery bytes.
Service is active/running with new PID 1029171; its logs record Discord login and
contain no traceback. Local/public /play/ return 200; anonymous API access returns
401. The saved character name matches the selected account; run_channel_id and
run_seeded_channel_id match the retained receipt. No other stored character claims
that channel. No player records or permissions were changed by these checks.

Player acceptance remains: refresh/sign in to the HUD, confirm hands/garment/pod
guidance, and inspect hands to compare the familiar-body wording and next choices.
Do not recreate/reset the character for footer validation. Existing Discord embeds
retain their old text. Receipt/archive retained; W7-F10 REVIEW, W7-F9 PARKED.

## Browser cache correction verified — 11 November 2026

The player's screenshot showed successful hands observation but missing follow-on
suggestions. Live DOM inspection found an empty navigation element, not clipping.
A normal page reload still stripped opening guidance despite current server script
bytes. index.html retained game.js?v=w7f9. Updating only that script reference to
game.js?v=w7f10-4bb1d86f2037 forced the reviewed script to load. Browser verification
then showed opening guidance and visible follow-on suggestions after inspect hands.
Repeat hands inspection offers body/garment/pod, since hud_presence was already
discovered; the first-time implant cue correctly does not repeat. No reset occurred.

Source/live HTML matched before the edit; script hash matched the reviewed package.
Only HTML was atomically published, with prior HTML retained privately on the server.
No service restart or direct player-data edit was needed. The authorized repeat
inspection can record normal activity, but does not add a new hands discovery.
The previous package manifest remains historical and its HTML pin predates this
cache correction; do not rerun its installer/rollback without review. Future static
releases must version changed browser assets. W7-F10 remains REVIEW, pending seal.


## Step 1: restore runtime reconciled — 11 November 2026

The adapter now binds new lifecycle plans to a reviewed current runtime manifest:
the installed lifecycle package plus the two Python playcheck corrections. Every
other Python pin, including the existing router, is preserved. Historical deployment
manifests remain immutable; the historical playcheck installer explicitly uses its
original pre-install contract. Static HUD assets are outside this bot contract.

464 Python tests pass. Five new contract tests rehearse old-archive restoration
under a new runtime, preservation of another fictional player's later progress,
replacement-life archival and restoration, stale-plan refusal, source/live/pinned
code-drift refusal, and continued blocking of unsafe restart flags. The portal test
expectation was also corrected to the already-published cache-versioned script URL.

Read-only installed-code verification passed: 140 hash entries. The live bot stayed
active/running with unchanged PID 1029171. No live reset/restore, private-archive
access, receipt retirement, service restart or player-record edit was performed.
Actual future restoration still requires fresh privileged maintenance preflight and
a reviewed new plan; the isolated rehearsal does not claim a live restore occurred.

See [current restore runtime](../../tools/deploy/w7f10/RESTORE_RUNTIME.md).
Step 1 is complete. The earlier status summary/register still need reconciliation
and final review before sealing. W7-F10 remains REVIEW; W7-F9 remains PARKED.
