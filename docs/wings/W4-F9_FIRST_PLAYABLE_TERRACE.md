# W4-F9 — First playable terrace passage

Status: **REVIEW — deployed 22 October 2026; actual Discord walkthrough pending.**
Prepared 22 October 2026, Australia/Perth.
Home: [W4-F9](W4-F9_WHAT_AM_I_PLAYING_TOMORROW.md).
Source baseline: 70ef9bf. One active feather, twenty-three sealed.

## Result

The reviewed terrace/package-to-tunes passage now has a Discord command bridge and persistent character state. Existing Navigation, Inspection, Inventory and Recovery cooperate with the new TerraceCog. The authoring prototype remains separate; production does not import it.

[Actual callback rehearsal transcript](W4-F9_DISCORD_CALLBACK_REHEARSAL.md) shows fictional outputs. This is not a Discord client playcheck.

## Player route and actions

From the main floor:

```text
!go south
!go out
```

The first step reaches the existing Stardock Overlook. Its room card points towards the outdoor terrace. The new terrace returns through !go inside. It is text-only pending reviewed artwork; no atmosphere technology or scenic-viewer fee has been invented.

The terrace offers the next relevant action after each step:

```text
!terrace attend
!terrace sky
!inspect package
!terrace take package
!terrace open package
!inspect box
!terrace unlock box
!terrace open box
!inspect tunes
!terrace take usb
!inventory
```

The explicit attend/sky pair is this first implementation's pacing mechanism, not a real-time delay or a smoking prerequisite. Available actions remain editable with experience. Reading the address is optional for pickup. The printed name is shown without asserting autobiographical recognition. Opening wrapper, unlocking/opening box, and taking the USB are separate; no premature contents/sender disclosure.

After collecting the package, the player can leave and open it elsewhere. Before pickup it remains in that participant's terrace encounter. Re-entry and repeated actions cannot duplicate it.

## Conditions

Initial attention/delivery requires the character's existing performance opening, discovered booking, no explicit performance_booking=False, terrace presence, being outside a Cube and not recovering. Sky observation follows the saved attention step.

Generic arrivals can visit the terrace without inheriting this particular delivery. No token, tab purchase, outfit, smoking or current class-field requirement is added.

The neck key is established by the existing performance opening's authored neck-key continuity. No Key of Commotion item is substituted or generated. Opening a box does not grant sender, Queen, princess or sabotage knowledge.

## State and custody

terrace_delivery.py selects pure copied character transitions. TerraceCog persists the changed character through existing storage before reporting success, rolling back in-memory state on save failure.

extra.terrace_delivery_v1 owns the stage, stable per-character instance IDs, package/box/USB holders, discoveries and ordered local occurrence records. Owner/record validation fails closed. This is content-specific state, following the pod-opening precedent; it does not extend memory-only ScenarioService or claim to implement a general scenario persistence layer.

Objects remain scene-owned rather than entering the count-based generic bag. !inventory displays a Personal delivery field. General drop/give/locker/Cube storage/copy/use is not enabled for these objects in this first pass. Ordinary possessions and their existing actions are unchanged. This explicit boundary avoids losing provenance before the temporal rules are defined.

The USB retains internal lineage, provisional temporal validity, unexamined content integrity and unresolved future condition. Player prose does not expose these metadata. No future send, disappearance, sabotage, repair, music playback or performance action is implemented.

## Recovery compatibility

The existing recovery transaction also secures held delivery objects in the pod, preserving instance IDs, stage and unrelated possessions. They are unavailable during reanimation and remain secured after bodily recovery until !pod_delivery collect succeeds. Failed collection rolls back; retry and repeated collection cannot duplicate them.

The existing pod-delivery count includes held scene objects. The inventory field only shows them while actually back in the character's possession. A package not yet picked up remains at its prior encounter rather than being conjured into the pod.

## Room registration

TerraceCog registers one content-owned room, lounge_smoking_terrace, and the Stardock Overlook's out exit at cog load. The new room's inside exit returns to the overlook.

Registration validates collisions before changing the in-memory room map, is idempotent, and preserves all existing descriptions, exits, items and enemies. Existing room IDs/routes are retained. No whole-room JSON replacement or baseline reset is part of deployment. Registration itself performs no file write; if an existing gameplay subsystem later persists rooms, its normal writer can include registered content. On every restart the same definitions are registered again.

The loader adds fsbot.cogs.terrace; the private run-channel routing allowlist includes terrace. There is no automatic encounter merely for startup, movement or !look, and no generic world-time timer.

## Executed verification

**190 runtime tests pass**, including sixteen new integration tests:
- Actual registered NavigationCog walks main floor → overlook → terrace, then real terrace/inspection/inventory callbacks save/reload through the full passage.
- Every mutating action has failed-save rollback and safe retry checks.
- Repeated actions/re-entry do not duplicate objects or occurrences.
- Generic/missing-booking, location, Cube and body-recovery gates.
- Separate container visibility and optional address reading; neck-key continuity.
- Character isolation, unchanged shared rooms during actions, and generic transfer rejection.
- Recovery/pod collection preserves instance identity; failed and repeated collection are safe.
- Room registration idempotence/collision protection; loader/routing/command registration.
- No hidden sender or temporal metadata in address/inventory output.

The earlier eighteen authoring tests remain separate evidence; no claim that the new passage has been played live. Tests use temporary fictional character JSON and production atomic saves, with no bot login or live storage. This is serial callback verification, not a concurrency or multi-store crash-recovery proof.

Before preparation, all seven pre-existing deployment target files on Neptune Lounge matched baseline 70ef9bf exactly. This is dated preflight evidence, to refresh immediately before installation.

## Deployment and review return

The source is ready for selective installation with backup and fresh hash checks: new terrace_delivery.py and cogs/terrace.py plus seven existing files (run_bot.py, cogs/core.py, cogs/inspection.py, cogs/navigation.py, cogs/recovery.py, cogs/router.py, recovery.py). No bulk character migration, catalogue replacement or live reset.

The new extension will make 46 loaded cogs if all existing 45 continue to load. Verify new cog registration, Discord login and heartbeat after restart. Then playcheck from the actual character location; no teleport/reset needed to force it.

W4-F9 remains ACTIVE/REVIEW. Later Cube-send/material disappearance, Queen/rat messenger, fee/practice/sabotage, artwork/scenic viewers, precise pacing and causal rules remain the linked authoring work.

## Deployment — 22 October 2026, 12:38 AWST

Karun explicitly requested deployment. Source f11ec66 installed selectively: seven modified source files and two new terrace modules. All existing target files matched reviewed baseline 70ef9bf; nine installed hashes verified again after startup. 190 runtime tests rerun and passed immediately before install.

Private rollback backup: /opt/futuresky/backups/w4f9-terrace-20261022-123759. Paused installation left all 61 data-file hashes unchanged. Character-file hash remains unchanged after startup. No character migration, relocation, reset or inventory grant; no whole-room JSON replacement. The new cog registers room content in memory when it loads, as described above.

Forced exit of paused PID 844485 triggered systemd on-failure restart. New PID 856490 active/running. All 46 extensions loaded, including fsbot.cogs.terrace (whose cog_load validates/registers the route); Discord login confirmed and initial heartbeat passed all seven subscribers including Recovery with errors=0. Temporary guided-creation drafts expire on restart as previously documented.

Actual Discord movement/terrace delivery remains for the player's check. Start with !look in the server run channel and follow from actual location. No live scene action was executed on the player's behalf. Later Cube send/vanishing, rat/Queen meeting and sabotage remain open. Counts unchanged; W4-F9 remains active in review. Earlier undeployed notes above are dated history.
