# Neptune Lounge — First Night Player Journey

**Feather:** 32  
**Date:** 2026-10-15  
**Status:** Evidence-backed experience audit; implementation and live playtest pending  
**Boundary:** Documentation only. No live-state writes, deployment, canon rewrite or invented encounter outcomes.

## Experience goal

A new player should move from disorienting pod awakening to an inviting, navigable, socially alive Neptune Lounge, then discover an optional first venture into Triton Central. Design each beat as a complete player experience: **visible scene, interaction, response, audiovisual treatment, persistence and onward possibility**.

The player's freedom matters. A journey map is not a forced quest chain.

## Existing journey spine

| Beat | Authored evidence | Player-facing presentation | Verification / opportunity |
|---|---|---|---|
| Awakening in pod | `docs/archive/process-history/arrival.md`; `data/narratives/internal_narratives.json` | Unfamiliar hands, embodied sensations, HUD, disorientation; private narrator impressions | Archived arrival template is design intent, not proof of implementation. Trace actual spawn, `!feed7`, coherence test and `!code love` in commands |
| First agency | Arrival template: inspect pod, change, eat, sleep, stand, return to FEED7 | Choices and discovery without front-loading a manual | Determine which commands/choices are functional and what a player sees when trying them |
| Transition / Cube | Arrival template: code `love`, pod becomes small wooden cube | Memorable threshold from private chamber into the Lounge | Verify command, inventory effects, first-room transition and actual artwork |
| Domefront arrival | `data/rooms/rooms.json` `neptune_lounge`; `arrival_first_lounge` private narrative | Neptune visible through dome; neon, chips, music, ambient life; a private moment of uncertainty | Check room embed, image, audio link, navigation, once-per-character impression and return-echo triggers |
| Social foothold | `data/thread_nodes/thread_nodes.json`: `nl_barmaid_chips_name`, `nl_chips_delivered_anywhere` | Counterkeeper asks for a name; service-runner drone delivers chips | Confirm chip-counter reachability, gating, input handling, delivery timing and effects |
| Personal mystery | `drq_sneak_lesson` at `dark_rat_queen_den`; `efiishents_office` references the Queen | Queen teaches quiet as an action; character can learn `sneak` | Confirm route to den, choice presentation, movement entanglement and whether this is appropriate for new players |
| First outward possibility | `pressure_in_the_veins_v1` at `main_square`; Lounge exit north | A crowd moment invites response; potential `absorb`, `descalate` or `catalyse` capability | Confirm reachable exit, event gating and how returning to Lounge feels |

## Verified code-level boundaries

- `bot/fsbot/config.py` defines `START_ROOM` as `pod_room` by default and `ROOMS_FILE` as `data/rooms/rooms.json`.
- `bot/fsbot/storage.py` loads that rooms file through the JSON Storage layer. A separate `bot/import_rooms.py` is a destructive PostgreSQL import utility with old default paths; **do not run it** as a player-experience step.
- `bot/fsbot/cogs/navigation.py` publishes `character.entered_room` after persisted movement.
- `bot/fsbot/cogs/narrator.py` subscribes to that event, selects a matching `on_enter_room` narrative, and sends a private internal embed to the player's run channel. It has an eight-second send throttle and a per-character seen list for one-time narratives.
- `bot/fsbot/cogs/threadnodes.py` also subscribes to room-entry events, manages active/completed nodes and player-facing prompts.
- Both narrative and Thread Node catalogues are authored. Presence in JSON does **not** prove that every trigger is exercised in the live service.
- The repository contains duplicate/legacy room JSON paths; the configured runtime path above is the code-level authority, subject to live deployment verification.

## Visual and sonic design checklist for each beat

1. **What is seen:** hero artwork or small visual detail, framing, readable location identity.
2. **What is heard:** available music/audio link, spatial proximity, silence and transition.
3. **What is felt:** concise scene prose, sensory texture, private internal narrative.
4. **What can be done:** legible immediate actions without exhaustive menus.
5. **What changes:** persistent choices, relationships, unlocked capability or discovered information.
6. **What calls onward:** another space, person, question, sound or optional mystery.

Keep Discord message density, mobile readability, accessibility and repeat visits in view. Avoid treating image/audio references as functioning playback until verified.

## First cohort: players as participants and co-creators

Invite a small group to experience the current journey **before** authoring a wholesale rewrite. Ask each player to report:
- where they felt curious or immersed;
- where they did not know what to do;
- what they expected to see, hear or be able to interact with;
- which inhabitant, space or unresolved question they would like to help develop.

Contributions should carry attribution and a clear status: proposal, playtest improvisation, approved world content or established canon. No participant is required to become a writer or developer.

## One-card next action

**Trace the pod-to-Lounge path in source, read-only.** Identify the concrete command handlers for spawn, FEED7, coherence, `!code love`, first room rendering, image/audio output and the first reachable chip-counter interaction. Produce a concise **works / authored-but-unverified / missing** matrix, then choose exactly one player-facing gap to implement and test in an isolated checkout.

Do not invite the waiting cohort into a supposedly complete onboarding flow until the first real-player walkthrough is verified.
