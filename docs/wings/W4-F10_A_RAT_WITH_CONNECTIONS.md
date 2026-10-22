# W4-F10 — A Rat with Connections

Status: ACTIVE / first playable draft, 22 October 2026. Follows W4-F9, parked for prose/pacing refinement after the author confirmed collecting tunes at 13:38 AWST. Neither feather is newly sealed; sealed total remains 23.

## Agreed scope

Counterkeeper supplies the tip. An actual rat waits on a warm conduit beneath the Stardock Overlook windows. It carries a message to the Dark Rat Queen and arranges a meeting. It is not the Queen in rat form and is not either hostile sewer rat. Keep interactions brief. Fee, rapport, tunes, practice, sabotage, Cube send and performance remain later work.

## First playable choice

After collecting the terrace USB, inspect the counterkeeper at Domefront Arrival. The tip suggests the Queen may know the audience’s taste, and points low down by the dock windows. Go inside to the main floor, then south to the Overlook. One `!rat message` asks for the meeting and covers the rat’s departure/return with a folded acceptance: “I’ll meet you here.” The exact staging, note and agreement to meet at these windows are implementation proposals for play review, not additional established lore. No real-world or world-clock wait. The Queen encounter is not implemented in this feather.

Optional `!inspect rat` or `!rat` describes the messenger; neither is required. Existing room art remains. No additional rat artwork was requested for this pass.

## State and checks

`extra.rat_messenger_v1` owns version 1 and stages tip/arranged. The meeting record names contact dark_rat_queen, room lounge_stardock_overlook and status arranged. This is a saved arrangement, not an NPC spawn, inventory item, shared enemy or active encounter. No music data, princess identity, fee or success at performance is disclosed or granted. Tip eligibility requires USB collected; afterwards knowledge persists separately from custody. Cube/recovery/location guards apply. All success follows a save; failed saves restore memory; repeated requests remain idempotent. No character-specific reset or migration.

`bot/fsbot/rat_messenger.py`, `bot/fsbot/cogs/rat_messenger.py`; bridges in inspection/navigation, loader and run router. Full suite: 206 tests pass, including real navigation/callbacks, reload, tip/message rollback, gates, optional inspection, command registration and unchanged music/other-character/room state.

## Deployment

22 October 2026, 13:53 AWST: source b3490c6 installed selectively (six code files); backup `/opt/futuresky/backups/w4f10-rat-20261022-135340/deployment.json`. Preflight matched all four replaced files against preceding source 95616f4. Both data roots unchanged during installation (122 file paths). No character resets, room edits or enemy spawns. Bot PID 857909 reconnected to Discord. Runtime checks and 206 tests passed; author live playcheck remains open.
