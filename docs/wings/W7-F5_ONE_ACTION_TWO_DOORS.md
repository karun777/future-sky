# W7-F5 — One Action, Two Doors

Status: ACTIVE — scope accepted and implementation authorised 29 October 2026.
Home: W7 Engine. Shared checkpoints: W4 Play, W5 Time, W6 Expression, W8 Stewardship.
Source baseline: d58d3da; branch engine/w7-f5-one-action-two-doors.
W7 remains four sealed; total remains 28. W7-F6 is next unallocated.

## Outcome and acceptance

Existing Efiishent can take one ordinary walking step from the authenticated website or Discord, through shared movement authority and the same saved character. Walk an exit on the website, observe the location in Discord, walk back in Discord, refresh the website and observe the return.

The website is https://future-sky.net/play/ on the existing Neptune Lounge server. Discord remains a supported conversational way to play. Chapter 1 / W4 authoring stays paused. A tangible game window and interesting conversation should develop together.

## Boundary

Include current exit buttons, basic room description, approved existing artwork and useful action feedback. Reuse existing OAuth identity, owner allowlist, aiohttp, discord.py and bot-owned storage. No new framework or hosting service is required. Website requests an action; it never writes player JSON directly or fabricates a Discord message/context.

Preserve movement persistence and room-entry event consequences. Coordinate ordinary walking with explicit sequences and idle-home. Refuse stale views, repeated submissions and conflicting input safely. Deliberate website movement is conscious activity and interrupts/rearms idle-home; passive views remain observational.

Exclude combat controls, portals, teleport, purchases, wardrobe, arbitrary command execution, generic scripting/autonomy, full map/journal/avatar/telemetry, registration, wider access and unrelated narrative repairs. Only layout changes needed for room text, exits and feedback belong here.

## Dependencies and inspected seams

W6-F6 supplies live authenticated read-only access. W7-F3 owns explicit sequences and W7-F4 owns idle-home. Read reset ritual, Knowledge Atlas, Wing Index, charter and these checkpoints before returning.

Initial source inspection at d58d3da:

- NavigationCog.go owns walking, persistence, room-entry publication and Discord presentation. It awaits departure broadcasts before saving. Only automatic walking currently revalidates after that await. Concurrent ordinary actions can therefore act on a stale source room or record.
- SequenceCog has per-character task ownership; web requests must respect it without pretending to be sequence children.
- IdleHomeCog.observe replaces a character with a copied record when saving activity. Shared movement must reread the authoritative record after awaited work, preserving fresh input and generation checks.
- RecoveryCog is a Discord global check, not an HTTP check. Cube protection is inside navigation; sequence/idle choice and combat guards are separate. Moving the callback behind HTTP alone would bypass these boundaries.
- Navigation calls look after moving. Look can grant observations and change state; passive web scene projection must not invoke it.
- Existing movement announces the durable room-entry fact before rendering arrival. Event subscribers can open an encounter; web must preserve that consequence and hand unsupported choices back to Discord.

## Verification plan

Use fictional isolated characters and temporary persistence. Cover shared success/save rollback, blocked and missing exits, stale view and duplicate submission, competing clients, sequence ownership, interruption during departure, recovery/Cube/choice/combat, session identity and CSRF. Run existing suite for Discord/sequence/idle-home regression. Prepare a selective reversible overlay with source baseline checks and no player-data replacement. Live two-way author playcheck is required before sealing.

## Shared checkpoints

- W4: ordinary walking integration only; Chapter 1 authoring remains paused.
- W5: conscious web action rearms real idle time; observation does not; no world-clock change.
- W6: basic room text, exits and feedback; richer scene composition remains follow-up.
- W8: keep source, deployment and author playcheck separate; one home and one count.

## Return checkpoint

Allocated on an isolated worktree from the sealed W6-F6 baseline. Inspection has identified the action/concurrency seams above. No W7-F5 runtime changes deployed and no player moved by this work. Next: implement shared walking authority and its adapters, prove it in isolation, then prepare the reversible live overlay. Do not rerun W6-F6's first-install activation script for an incremental deployment.
