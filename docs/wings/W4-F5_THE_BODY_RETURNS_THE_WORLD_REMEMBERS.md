# W4-F5 — The Body Returns, the World Remembers

Home: W4 Play. Allocated and sealed 18 October 2026.
Status: isolated implementation and verification complete; **not deployed**. Efiishent remains unchanged.

## Player experience

Voluntary renewal uses the existing `!reincarnate` command. With no argument it offers renewal of the current person, preserving the existing name/date. `!reincarnate confirm` begins; `!reincarnate cancel` cancels. Explicit existing name/date arguments remain supported, with name uniqueness rechecked at confirmation. No run-channel archive or default birthdate replacement occurs. Leave combat and any legacy-marked Cube state before voluntary renewal.

Lethal combat now enters the same recovery path instead of instantly restoring HP in the Lounge.

Carried and worn possessions are secured immediately in the owner's private pod parcel. This implements timely delivery at intake; no courier delay or public loot pile. Remote Cube/locker/vault holdings and account credits remain where they were. Reanimation lasts **604800 persisted world seconds** (seven 86400-second in-world days). Shared-world time continues; no real-time substitution, time jump, scenario rewind or mission restart.

During recovery, `!recovery` reports the remaining world days. `!pod_delivery` reports the private parcel count. Help, time and FEED7 remain available; other commands are blocked by a global Cog check, including admin bypass attempts and character recreation. Completion restores max HP in the pod. `!pod_delivery collect` moves the parcel to the bag, once; `!awaken` can enter/resume W4-F4. Existing active Thread Nodes and opening discoveries are preserved, so this does not forcibly replay a fresh opening.

## State and failure behaviour

`extra.recovery` stores recovery ID, stage, cause, source room, start/deadline and delivery time. `extra.pod_delivery` stores owner-only items and receipts. They live in the same character record as bag/equipment. Intake, completion and collection each replace that record with a copied version and use the existing atomic JSON replacement writer. Failed writes restore the prior in-memory record and do not announce success.

Bag quantities are combined with equipped units. Core's two-handed main/off-hand mirror counts once, while separately equipped one-handed items count separately. Definition metadata comes from the existing item catalogue. Retained delivery manifests survive repeat recovery without duplication.

All unrelated character fields are preserved, including identity, birth details, profile, XP, knowledge, credits, routing, quest flags, completed and active nodes, and opening discoveries. Combat and sneaking state clear; bodily HP stays zero until completion. Brain preservation does not declare immediate memory access.

Recovery reads the persisted clock file, never the soft in-memory clock that may advance after a failed save. A durable heartbeat subscriber completes due recoveries; the command gate/status path also checks deadlines after restart. No world time progresses merely because the server was offline. Variable acceleration changes wall-clock waiting time, not the deadline's world duration.

Ambient rest and idle narration skip recovering bodies. Combat skips them as targets/actors. Recovery extension startup is required: failure aborts startup rather than leaving reanimating characters without an action gate.

## Brain continuity

Ordinary HP depletion means recoverable bodily trauma in this implementation; it does not diagnose brain death. The service can hold a brain-continuity case in `brain_review`, with possessions secured, no completion deadline and no progress erasure. No player command or HP rule automatically assigns that case.

The legacy destructive severance command is explicitly unavailable pending authored brain-death rules. No claim that its old wipe models samskaras, consent, memory or irreversible brain loss is made. Historical old-brainer status is never automatically granted after repair.

## Verification

Base source: `023f77b6d831f8a49472db2b691d79d47efe0075`.
Isolated archive: `/tmp/futuresky-w4f5-btnx8ndl` on Neptune Lounge, with no external symlinks. Synthetic records and temporary files only.

`PYTHONPATH=bot /opt/futuresky/.venv/bin/python -m unittest discover -s tests`: **94 passed**, including **21 new recovery tests**. Actual renewal/status/delivery/inspection callbacks, lethal CombatCog step, global Discord Bot check registration, EventBus subscription/dispatch, AmbientCog rest guard and production JSON writer are exercised.

Evidence covers possession conservation, two-hand mirrors, remote-store and participant isolation, identity/progress continuity, repeat intake/collection, restart before the exact boundary, soft-clock divergence, failed intake/completion/collection/combat writes and retry, unresolved brain hold, disabled severance and handoff to the W4-F4 hands opening. Discord network delivery and a full live bot startup are not tested. No live bot entrypoint was imported in tests.

## Deployment and return

Deploy W4-F4 and W4-F5 together, preserving all live data, local overlays and service configuration. Before acting on Efiishent, inspect his current recovery eligibility privately and take a backup; show a field-level reset plan. Do not run character creation or silently fast-forward the shared clock. Recovery preserves existing narrative state; any selective opening rehearsal requires an explicit separate plan.

Limits: existing atomic replacement is not a power-loss durability guarantee; no multi-process coordination or multi-file transaction is added. No medical injury taxonomy, known instruction manual, memory unlock schedule, brain-death wipe, UI cinematic, pod-storage capacity or delivery theft mechanic is introduced. Parcel receipts are retained and may later need archival policy. Direct non-command/admin integrations that mutate others' records require their own future recovery checks.

[Reset audit](../handover/RESET_AND_RECOVERY_REVIEW_20261018.md) · [Canon](../current/MANZO_PRESERVED_BRAINS_AND_AWAKENING.md) · [W4-F4](W4-F4_WHOSE_HANDS_ARE_THESE.md)

Shared nodes: W1/W3 continuity and brain/soul questions; W2 owned pod; W5 clock domain; W7 persistent transitions. W4 owns this feather. Completed W4 count **4** (F1, F2, F4, F5); W4-F3 remains REVIEW. Total sealed **18**. Next unallocated **W4-F6**.
