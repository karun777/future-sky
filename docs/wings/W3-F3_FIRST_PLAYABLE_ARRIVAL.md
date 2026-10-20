# W3-F3 — First Playable Arrival

Status: REVIEW — deployed and existing-player DM preview verified 20 October 2026.
20 October 2026. Branch: beings/w3-f3-first-playable-arrival.
Part of the authorised W3-F3 continuation; not another allocated feather. Counts remain twenty-two.

## What this pass makes playable
A bounded guided setup, explicit review, awakening and first inspectable action.
Start in a direct message to the bot. A guild invocation gives DM instructions without accepting draft fields.
Existing characters cannot be replaced, including through the legacy create command. They can rehearse with !begin preview.
No existing character, body, inventory, history or relationship detail is migrated by this branch.

## Commands — existing-player disposable preview
```text
!begin preview
!begin class Dreamer-Technician
!begin name Fictional Traveller
!begin date 2000-01-01
!begin body familiar
!begin embodiment unfamiliar
!begin background A musician whose travels mostly happened in dreams.
!begin review
!begin awaken
!begin inspect hands
!begin inspect body
!begin cancel
```
All preview state and discoveries are disposable and held in memory, never saved to the character store.
Use a fictional name/date/background for a review fixture. These examples are not a rename, biography or birthdate assignment for Efiishent.

## New-character path
Use !begin instead of !begin preview, then the same field/review/awaken sequence.
Awaken durably creates a new record and opening discovery state before presenting the scene. It is only permitted when no character already exists.
After creation, ordinary !inspect hands, !inspect body, !look, !wardrobe and !wear/!remove continue the existing game. Server !look uses the existing run-channel route. Actual DM/server transition and Discord delivery still need live verification.

## Actual authored opening
> A low thump beyond the wall.
>
> Something supports your weight. You draw a breath.
> Your fingers move against woven fabric.
>
> Light begins to resolve.

On inspecting hands when body recognition is familiar and embodiment unfamiliar:
> You turn them over, open them, close them. Yours. The weight of your arms and the touch of air on skin hold your attention. It has been a while.

The existing once-only HUD-presence notice can follow, according to existing display state.
Body recognition and familiarity with embodiment are separate saved choices; legacy records without those choices retain their existing authored responses.

## Mechanics and persistence
- Shared build_arrival_character in CoreCog module uses existing class tendencies, HP, astrology/mana and starter-item definitions; no parallel stat algorithm.
- The guided flow stores its choices under existing extra.profile and extra.arrival namespaces; durable character state is committed only at final awakening.
- Temporary draft is per user, with bounded field text, explicit review and cancellation. Edits invalidate review. Drafts disappear on restart; the instructions say so.
- Failed character save removes the uncommitted in-memory record and retains the draft for retry. This assumes the existing writer's atomic-save behaviour; no new multi-store transaction guarantee.
- Preview inspection uses only a copied rehearsal character and never forwards game callbacks against the account's live record.
- Legacy create command now refuses replacement of an existing character.
- The guided flow does not initialise optional locker/vault/cube bridge stores at creation. Character/core fields and starter inventory are present; later subsystem initialisation remains existing behaviour and needs verification before those paths are promised.

## Specific story versus generic arrival
New guided arrivals explicitly have no performance booking. Booking inspection, HUD notice and unread-display artwork do not invent Efiishent's particular gig. Existing performance-arrival records retain their booking. Generic panels/display are text-only to avoid performance-notice artwork.
Room and other existing pod features remain shared. This is not personal pod instancing or full arrival-story selection. Existing neck-object prose and broader room fixtures were not redesigned here.

## UI and scope limits
This is a command-based first pass, not a finished short visual wizard. The initial help lists fields; whether that feels too dense remains a live usability question.
Minimum fields in this pass: class, working name, character date (existing astrology requirement), body-recognition choice and embodiment familiarity. This is an implementation trial, not a final canonical mandatory creation policy.
Eight current starting classes are offered; Unwritten is excluded only from this new guided path pending its unlock-policy decision. Legacy creation eligibility remains unchanged.
No ancestry catalogue or bonuses, full physical appearance editor, gender/orientation fields, romance system, skill-tree unlocks or memory-timer rules were implemented. Optional background is plain authored text, not verified world history.
No new sense-progression gates or timing simulation. The opening illustrates hearing/touch/vision, not a completed five-sense-return system.
No player biography/relationship details from the conversation were inserted into live records or test fixtures.

## Verification — 20 October 2026
**150 isolated tests pass**, including ten new tests in tests/test_arrival.py:
- new-character setup, review, durable creation and saved hands inspection;
- both creation entry points protect existing characters;
- preview can inspect while saved character and file bytes remain unchanged;
- edits invalidate review;
- failed save/retry and repeated confirm do not duplicate a character;
- guild use does not capture drafts;
- invalid input and cancellation;
- generic booking/HUD/art suppression;
- shared builder baseline;
- real discord.py multiword argument parsing.
Existing 140 checks pass after shared builder extraction. An initial regression (stale local mana reference) was found and fixed before this passing run.
No new live bot instance, restart, production write, DM delivery or player playthrough in this verification.

## Return
W3-F3 remains REVIEW. Next: review the actual command-based passage, then choose deployment and a safe existing-player preview playcheck if accepted.
Deployment would touch CoreCog, ArrivalCog, opening/HUD/media selection, Help and extension registration; preserve existing live overlays and verify new extension count/readiness. No deployment authorised merely by this document.

## Deployment checkpoint — 20 October 2026, approximately 19:21 AWST

Karun explicitly authorised deployment. Source 108bac2. Seven compiled source files installed selectively after all six existing targets matched pre-change source 25fbf35. Private backup: /opt/futuresky/backups/w3f3-arrival-20261020-192103. All seven installed hashes match; all 61 data files unchanged immediately before/after installation. Character-file hash unchanged after restart: True.

Old PID 829575 was paused during install and exited by SIGKILL to trigger systemd Restart=on-failure (10 seconds). This is a supervised forced restart, not graceful shutdown. New service PID 830880 active/running; 45 extensions loaded including arrival, Discord login and Recovery heartbeat confirmed. No error/traceback matches in inspected startup output. Existing live overlays outside targets retained.

Actual Discord DM preview remains pending. Use !begin preview for existing accounts; never reset/recreate Efiishent for this playcheck. W3-F3 REVIEW, counts unchanged. Roll back code selectively from backup if needed; do not restore old gameplay data wholesale. Earlier not-deployed statements describe their dated checkpoint.


## Actual Discord preview check — 20 October 2026, 19:41–20:02 AWST
Karun supplied actual output confirming:
- Server invocation directs the player to DM without starting setup there.
- DM !begin preview displays PREVIEW and explicitly states nothing is saved.
- Class, fictional name/date, familiar-body and unfamiliar-embodiment selections and background are accepted; review card matches those inputs.
- !begin awaken presents the guided sensory opening and preview-only notice.
- !begin inspect hands recognises the hands and expresses unfamiliar embodiment, with a separate existing HUD-presence notice.
- !begin inspect body presents the contextual response.
- !begin cancel returns “Draft discarded. Your saved character is unchanged.”

This verifies the preview path and its presented cancellation result in Discord. No new after-playcheck live-record hash comparison was performed; actual no-write behaviour has isolated byte-comparison tests. Fresh creation, its first durable save and the DM-to-server run-channel handoff remain isolated/source coverage, not live player-tested.
Usability seams: initial instructions are dense, confirmations generic, class ID in review is technical, and body response explains the state more than evoking sensation. Retain these for later presentation work. No wording change or deployment for this checkpoint.
W3-F3 remains REVIEW; no seal or completed-count increment inferred from this playcheck alone.
