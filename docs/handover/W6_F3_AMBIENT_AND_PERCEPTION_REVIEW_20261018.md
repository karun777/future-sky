# W6-F3 — Ambient, internal voice and perception review

18 October 2026. Discussion/source review only. No runtime changes, deployment or new feather allocation. Home: [W6-F3](../wings/W6-F3_THE_DISPLAY_BEHIND_YOUR_EYES.md). World-engine expansion remains on hold.

## Author direction recovered and clarified

Earlier conversation retrieval records: private local ambience first, global fallback; atmosphere must not overshadow player action; typing in one's run channel should count as activity; timing should vary; leaving the keyboard should not be punished; long-idle characters can rest at their current anchor. July discussion explicitly sought eventual images, NPC movement and dropped inventory. These preferences are distinct from prior assistant proposals about world-moment roles and larger engine architecture.

New author direction on 18 October:
- HUD technology develops towards Dragonfly Goggles: sensing, data, analysis and advanced AI communication, with proficiency/upgrades and possible faults/interference.
- Internal voice develops intuitive/sixth-sense capacity, enhances ordinary senses and can reach others' inner worlds and the subtle world beyond technological access. It is independent of HUD enablement. Earlier assistant suggestions that HUD progression unlocks the narrator are superseded.
- Awakening unfolds hearing (Vishuddha), touch (Anahata), vision (Manipura), taste (Svadhistana), smell (Muladhara), in that order. Nature of preceding death can disrupt/delay return. Chakra parallelism has wider consequences not yet specified.
- This records Karun's fictional framework and stated inspiration. Detailed Sarkar source review is deferred; no verified quotation, numeric thresholds, timings or injury penalties are inferred.
- Seven-day bodily reanimation, sensory return, memory access and fuller reintegration are distinct; precise relationships remain open.

## Current sources and behaviour

Inspected current Git/live AmbientCog, ActivityCog, NarratorCog, ThreadNodesCog, Storage, WorldMomentsCog, room ambience and data/ambient/global_ambient.json. Bot active at PID 811335 during review. Deployment source 9707200bd5874a440b6ee2c80bccc8020b6d896b; later commits are documentation. Historical attachments are not runtime authority.

AmbientCog v2.5:
- A 30-real-second loop; default 120-real-second minimum idle, 90-second spacing, max two attempts per five minutes, six recent lines remembered.
- Commands update its own activity map. Active Thread Nodes, recovery and sleeping suppress output.
- Room ambient_events first; global/Cube fallback only if no local line is available.
- Private run-channel delivery through Router; no channel creation.
- After 2700 real seconds idle, two-stage rest returns to configured anchor (default pod), with a 30-second stage gap; sleeps until another command. This is ordinary rest, not seven-world-day reanimation.
- Selection/history/pacing/rest-in-progress are memory-only; rest movement and last_reset are saved on the character. The header's broad ephemeral claim does not cover that persisted relocation.
- Rendering currently text embeds only: no asset, inventory, NPC movement or room-state effect.

NarratorCog: room-entry event subscriber, conditional authored impressions, eight-second throttle and persistent once-seen IDs. Idle selection exists but is not called by AmbientCog or another discovered runtime caller. No faculty-development model or discovery-event subscription is implemented.

WorldMomentsCog: separate heartbeat consumer publishing eligibility facts at six-world-hour boundaries. It does not itself narrate or move NPCs. It is not the AmbientCog random prose selector despite similar names.

## Verified gaps

1. ActivityCog notices typing/messages but keeps its own timestamps; AmbientCog does not consume them. Its own listener tracks recognized commands. Real user activity can therefore be misclassified as idle.
2. A character absent from Ambient's activity map is assigned now as its last-action default on every iteration, producing zero idle indefinitely until a command seeds the map.
3. Storage has no load_global_ambient method. Ambient therefore uses hardcoded DEFAULT_GLOBAL_AMBIENT. The live data/ambient/global_ambient.json also uses global_ambient/player_feelings keys, whereas Ambient expects fallback_events/cube_whispers and cooldown/rest settings. Editing that file alone does not configure this cog.
4. _pick_line falls back to the full local pool once recent choices exhaust it. Local lines never become exhausted for fallback purposes. Synthetic helper probe: 100 draws with a three-line room pool yielded 100 room lines.
5. No active-loop call reaches NarratorCog.maybe_trigger_on_idle. ThreadNodes idle is wired, but no immediate entanglement recheck follows it before ambient prose, so a newly opened choice can receive an ambient line in the same iteration.
6. Pacing slots and anti-repeat choices are recorded before successful delivery. Failed attempts can consume the budget; rest moves the character before delivering/saving and has no rollback on failed persistence.
7. No sense, knowledge, implant capability, private context or world-event identity filters these room strings. A pod line currently supplies smell regardless of sensory development; office ambience can explicitly name a secret association.
8. Generic fallback text can assert hunger or an urge without reading bodily state. Cube text can resemble subtle perception without distinguishing source/channel.
9. The brochure crash in the playtest is not AmbientCog at all: it is embedded in W4-F4's inspection text. Fixing ambient scheduling alone cannot make it a once-only event.

Evidence: read-only source/config inspection plus synthetic calls on an uninitialised AmbientCog object with fictional in-memory state. Confirmed missing Storage loader and zero-idle default. No live event was triggered, no character record copied/modified and no production bot instantiated for the probe.

## Relevance and bounded proposal

Ambient scarcity during rapid command-driven play is expected under the idle policy. Raising frequency alone would crowd attention and still fail to make events contextual.

Distinguish:
- Recurring atmosphere: continuing hum, air circulation, distant sound. Repetition can be valid with pacing.
- Particular occurrences: a crash, person passing or dropped object. If consequential/inspectable/shared, record the occurrence and its actual effects; a random line must not fabricate an inspectable entity absent from state.
- Personal reception: which senses/faculties/device channels can receive or interpret that occurrence, and what the character notices.

One occurrence may support several presentations, not necessarily several messages. A corridor crash can be heard when hearing is available; a HUD may analyse accessible acoustic data if equipped; an inward impression can have a distinct authored intuitive basis. Do not always broadcast all three or equate bodily intuition with an implant unlock. Other players can witness different aspects of the same event without creating multiple incompatible crashes.

For W6-F3: agree channel boundaries and truthful HUD states; document sensory/proficiency contracts; choose a few pod events as a bounded proof. Preserve quiet during important discoveries. Reconcile activity signals and verify pacing/config before relying on idle delivery. Keep a room's continuing atmosphere available during active play through appropriate scene/action descriptions, rather than requiring silence to experience the world.

Do not build a general NPC/event/courier system or complete chakra simulation in this feather. Retain future capability hooks and stage implementation in the agreed HUD scope. Sensory progression timings await source/authoring; no rewrite deployed.

## Return

W6-F3 remains SCOPED/OPEN, W6 completed count 2, total sealed 18. W4-F6 unallocated. Next: review this three-channel model with Karun, then settle the smallest opening/HUD implementation. Live W4-F4/F5 remain unchanged.
