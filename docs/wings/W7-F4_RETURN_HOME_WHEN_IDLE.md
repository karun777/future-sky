# W7-F4 — Return Home When Idle

Status: ALLOCATED / next feather, 29 October 2026. No implementation or deployment.

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
