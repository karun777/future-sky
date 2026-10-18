# Reset and recovery review — 18 October 2026

Home: W4 Play; connects W1/W3 continuity, W2 pod ownership, W5 elapsed time, W7 durable state. Review only: no new completed feather and no character reset.

## Source inspected

Live /opt/futuresky: RebirthCog, CombatCog and AmbientCog. Main reference 0b113f48c85679e0c49cc0e5b327a2d67136a6e7; W4-F4 is saved but not deployed. Historical attachments are not treated as current runtime authority.

## Existing paths

| Path | Observed behaviour | Required change |
| --- | --- | --- |
| !reincarnate | Name/date selection, confirmation, selected progress carry, bag moved to Cube, run-channel archive, new pod body immediately | Preserve same-person continuity; account for equipped items; deliver to owned pod; persist recovery duration; fail safely |
| Combat death | Immediate full-HP return to Neptune Lounge, equipment/bag retained | Use the same durable recovery transition, not a separate instant respawn |
| Idle rest | Return to configured anchor after inactivity | Remain ordinary rest; do not treat as injury or seven-day reanimation |
| !scenario_reset | Clears scenario runtime | Not a bodily reset |
| Existing severance command | Two confirmations, progression wipe, personal Cube deletion, immediate new record | Not an established model of brain death; do not use for Efiishent or silently redefine it |

RebirthCog moves only bag entries; equipped entries are cleared by its record builder. Separate bag/equipment ownership semantics must be checked before calculating the death pile to avoid both loss and duplication. The builder retains selected XP/badges/knowledge, flags, profile and completed nodes, but rebuilds stats/pools and drops other fields including birth time/timezone, arbitrary extra state and arrival discoveries. Current combat flags can be carried forward. Missing Cube handling does not abort inventory clearing. Character/Cube saves suppress errors and are separate, with no transactional rollback; archival occurs before saves. These are reasons not to run the current command as a safe replay reset.

## Adopted requirements

- All carried and worn possessions go to the owner's pod automatically in a timely manner. Shared pod_room is not permission to create a publicly lootable room pile.
- Reanimation takes seven days. Recovery completion and memory reintegration are separate facts.
- Ordinary repair preserves personal continuity. Historical old-brainer restoration is a rare origin, not a new label granted after each repair.
- Brain death is a harder boundary; damage severity, recoverability, soul continuity and progression consequences remain unspecified. Do not invent automatic erasure or guaranteed resurrection.

## Recommended bounded implementation

One recovery record should own the character's recovery stage, time basis, deadline, possession manifest and delivery receipt. Both combat death and voluntary bodily renewal should call that path. Completion and delivery must be restart-safe and idempotent; partial saves must never duplicate or lose possessions. Preserve identity, world evidence and unrelated state, clear transient combat state, and expose recovery status without allowing normal bodily actions prematurely.

Recommended provisional delivery policy: immediately secure possessions in owner-only pod storage at recovery intake, so delivery is guaranteed by awakening. This is a proposal, not an authored exact transit duration. Existing remote Cube/locker/vault holdings should remain where they are; the death pile is carried/worn property, not every remote holding the character owns. Currency and unique item-instance handling require source checks.

Interpret seven days using the adopted world clock if approved; do not silently substitute seven real days. The current clock can accelerate and vary, so store the deadline in the chosen canonical domain and test across restarts and rate changes. Relationship to the two-day mission window must be explicit; do not automatically rewind the shared world.

Brain death should be recorded as unresolved/awaiting an authored disposition until rules are agreed, with no destructive wipe inferred from HP reaching zero. The existing severance command is not proof of medical or metaphysical equivalence.

## Efiishent test return

Karun prefers testing as Efiishent and permits a reset if necessary. First inspect whether repositioning/resuming the existing character suffices; preserve a private backup and produce a field-level change plan before executing any reset. Do not invoke create_character, reincarnate or severance to improvise a safe reset. Do not bypass seven days silently for testing; any controlled rehearsal-time override must be explicit and isolated from the shared world.

No live character contents were copied into this audit. No game command was executed; no runtime source, service or character state changed. Next proposed feather: **W4-F5 — The Body Returns, the World Remembers**, subject to author adoption; not allocated or counted by this review.
