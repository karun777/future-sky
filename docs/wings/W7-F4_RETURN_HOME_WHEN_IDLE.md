# W7-F4 — Return Home When Idle

Status: ACTIVE — first playable implementation, 29 October 2026. W4 chapter feathering remains paused at the author’s request. Implementation/testing complete; deployment recorded below.

## Author direction

An automatic script triggers after a certain amount of player idle time and transitions the character home. %home is the author’s illustrative reference: in Chapter 1 it returns the character to the pod; later it resolves whatever location is that character’s home. It must not permanently hardcode the pod as everyone’s home.

This follows W7-F3’s explicit runner and is a first bounded example of unconscious character behaviour. Player-created custom scripts and a larger library of conditional generic scripts remain broader direction, not first-pass requirements.

## Proposed first-pass behaviour for design

- A persisted home destination; Chapter 1 defaults to pod_room.
- A configurable inactivity threshold, with its real/world/chapter time basis stated explicitly.
- Conscious player input interrupts unattended return; automatic actions do not refresh conscious activity.
- Return uses normal movement rules and stops for obstacles, combat or an unresolved choice.
- A concise narrative update explains what happened.
- Resolve home at execution time, respecting changed residence/chapter.

These details were assistant proposals in the review, accepted as the direction to move towards; they are not implemented guarantees.

## Open implementation questions

Define which input counts as conscious activity, how the initial idle anchor is established for existing characters, durable progress/restart semantics, permitted route discovery, offline delivery and scheduling. Verify the runner can be reused without impersonating a new conscious command or bypassing its normal checks. The current runner only accepts explicit supplied commands and is not a background scheduler.

Choose a bounded threshold and test idle activation, new-input interruption, blocked routes, changed home and safe retries before live automatic movement. No idle automation is enabled by allocating this feather.

## Scope and return

Prioritise this one home routine; defer custom script authoring, learned moral/factional habits and generic condition language. After this bounded Engine work return to Chapter 1, W4-F13 — Vitriol’s interference. W7-F3 sealed; 26 sealed total.


## First playable implementation

Opt-in !idlehome on defaults to 1800 REAL seconds (30 minutes); !idlehome on 60 enables a short live test. Accepted range 60–86400 real seconds. !idlehome off disables return; !idlehome status reports settings; !idlehome home <room_id> changes this character’s home. %home remains symbolic author notation, not a Discord command or general script variable system.

Persistent extra.idle_home_v1 stores enabled state, home, real UTC last-input timestamp, inactivity duration, generation, status, source channel/message reference, a bounded history and pending notice. Initial home respects existing reset_location/extra reset_location/reset_anchor before defaulting to pod_room. No NPC or existing player is automatically enrolled. Commands count as conscious activity; messages/typing in the player’s own run channel also count. Sequence child and automatic actions do not refresh conscious timestamps. New input re-arms the timer and invalidates the current generation. Failed activity saves suspend automatic movement in that process until activity saves successfully; this ephemeral fail-closed suspension is not a new durable clock.

Heartbeat drives at most one checked ordinary walking action per opted-in character per tick. It consumes real idle time, not the era/comet multiplier. Wall-clock downtime can make a character overdue on restart; no offline journeys are fast-forwarded. Resume from the current saved room/home after reconstructing and validating an original player context. If the source message cannot be retrieved, no automatic move occurs. Use commands in the player’s run channel for restart-supported context. Cached contexts are not a claim of an offline identity/permission service.

Routes use current actual exits over a bounded curated public walking network (Lounge, hostel, market, Sector 42, Elemental Sound). Portals, sewers, service/security routes and unknown areas are excluded. Future homes work where supported routes exist; other homes block rather than teleport. Resolve destination and route anew each tick. Normal Command.invoke/checks/hooks/persistence/events apply. Recovery, Cube, combat, active choices and an explicit sequence defer walking. A navigation guard revalidates activity generation after departure awaits and before the movement save. Already committed movement is not undone by later input. A concise notice follows arrival; intermediate go embeds are suppressed, but meaningful room-entry narrative events retain their normal behaviour.

The prior Ambient rest_v0 teleport routine is bypassed whenever IdleHomeCog is loaded, including for players who have not opted in. Ambient flavour remains active; there is now one idle-return movement owner. Old configuration remains on disk but no longer triggers the legacy teleport while the new cog is loaded.

Pending arrival notices persist before sending; failed delivery retains them. A delivered notice is cleared after acknowledgement. This is retryable at-least-once delivery; a crash between sending and clearing can duplicate a notice. No channel is created from idle activity. No global time advance, rehearsal credit, Queen approval, learning or chapter progression is granted.

## Verification

240 full-suite tests passed. Fourteen new tests cover threshold boundary, real checked multi-step walking, no automatic timestamp refresh, persisted completion, fresh typing/commands, interruption during awaited departure, recovery/Cube/combat/choice guards, unsupported routes, changed home, restart context retrieval and wrong-author rejection, movement-save retry, activity-save suspension, old-rest suppression, sequence-busy deferral, disabling/settings validation, retained/delivered notices and automatic/sequence activity exclusions. Fictional temporary records only; no author character moved by test.

Live playcheck: from a supported non-home location issue !idlehome on 60 in the player’s run channel. Stop typing/issuing commands; after the threshold, one walking step occurs per roughly one-minute heartbeat until home or interruption. A short journey can take several real minutes. Check arrival with !look after the notice, then !idlehome off if desired. Settings/status queries themselves are conscious input and restart the idle wait.

This is opt-in authored home automation, not custom script authoring, learned routines or a full autonomous character system. Human-to-script transitions are first-pass behaviour here. Feather remains ACTIVE, not sealed, pending author playcheck/review. W4 remains paused; no commitment to return after only this Engine feather overrides the author’s current focus.
