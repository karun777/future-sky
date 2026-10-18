# W6-F3 — The Display Behind Your Eyes

Home wing: **W6 Expression**. Allocated by Karun on 18 October 2026, 18:46 AWST.
Status: **SCOPED / OPEN**. Discuss internal voice and ambient events before implementation. No completed-count increment, runtime change or deployment.

## Purpose and scope

Make the HUD intelligible as technology experienced by the character, within Discord's presentation. Establish its presence during awakening, its initial capabilities and the meaning or uncertainty of its readings. Fix display-state handling after the boundaries with internal voice and ambient events are agreed.

The implant can develop through character proficiency and gameplay upgrades. Hacking, corruption, faults and misuse are desired future possibilities, not implemented mechanics. Separate physical world conditions, the device's assessment and the character's interpretation. Inaccurate readings need traceable causes; changing a display must not change world reality.

The three coordinated channels:
- HUD: technological observation and interpretation.
- Internal voice: inward response; exact boundaries still to discuss.
- Ambient events: situated occurrences around the character; timing and persistence still to discuss.

The transport/display problem and in-world technology are distinct. Automatic presentation remains an author preference; the character should not repeatedly request a status command merely to experience the HUD.

## Source findings — inspected 18 October

Live source at deployed bot revision 9707200bd5874a440b6ee2c80bccc8020b6d896b:
- `bot/fsbot/cogs/hud.py`: preferences/default telemetry at `extra.hud`; normal, signal_degraded and dark_mode; on/off/state commands. Default coherence 97, parallelism 78, commotion LOW. No demonstrated measurement, proficiency, upgrade or hacking loop.
- `bot/fsbot/cogs/navigation.py`: constructs display-state-aware text, but then sends a separate `hud_embed` using raw/default values. The calculated offline/degraded text is unused by that send path. Fix this inconsistency rather than inventing metric fluctuations.
- `bot/fsbot/ui/console.py`: telemetry embed helper carries the same defaults.
- `data/hud/hud_metrics.json` and `hud_states.json`: declarative defaults/states exist; the inspected HUD renderer does not load them.
- [Archived arrival](../archive/process-history/arrival.md): display embedded in vision, initially unfamiliar, recedes as attention shifts; HUD mediates the FEED7 prompt. The 97/78 pair originates in authored arrival material. Archived fullscreen/code-door details are lineage, not current behaviour.
- [System map](../current/SYSTEM_MAP_v0.4.md), [data contracts](../current/DATA_CONTRACTS_v0.5.1.md) and [W6-F1](W6-F1_HOW_THE_WORLD_REACHES_US.md): presentation is subordinate to domain authority; HUD numbers are not proof of measured psychological states.

Conversation retrieval recovered a September 2025 user preference for automatic HUD information and July 2026 discussions of progressive capability and Discord rendering constraints. Retrieved prior assistant proposals are not automatically adopted canon. The current author explicitly restated the implant/proficiency/upgrades/interference direction on 18 October.

## Proposed acceptance boundary

Before sealing:
1. Agree the first available readings and what they mean; distinguish baseline/demo values from supported assessments.
2. Introduce the implant in the opening without prescribing the player's emotional response.
3. Render on/off/degraded/dark states consistently across HUD and navigation, preserving player-specific visibility.
4. Identify what belongs to HUD versus internal voice and ambient events.
5. Test fresh and returning characters, repeated attention, saved preferences and failures. Verify actual Discord delivery before claiming it.
6. Record future capability/proficiency/fault hooks without building a general upgrade or hacking subsystem.

Do not broaden this into a full Discord redesign, universal sensory filter, new resource simulation or general world engine expansion. Do not silently treat internal voice as implant output. No exact metric formula, implant origin, installation method or reliability rules are established by this allocation.

## Coordinated return

W3: embodiment, proficiency and character interpretation.
W4: awakening, discoverable actions and returning-player behaviour.
W5: reading age, timing and event pacing.
W7: authoritative inputs and persistence.
W6 owns the feather; connected wings receive no duplicate count.

W4-F4/F5 remain deployed. Karun's first live walkthrough demonstrated hands/body/garment inspection, FEED7, wardrobe and booking discovery. It exposed a returning-player wardrobe invitation that cannot be fulfilled, shared pod presence, repeat awakening framing, repeated brochure crash and implementation-language hints. These remain connected playtest findings; allocating this HUD feather does not claim to fix them all. No live character reset occurred.

Next conversation: internal voice, then ambient events. Return here to settle the small HUD implementation after those boundaries are clear.

W6 completed count remains **2**; total sealed remains **18**. W6-F3 allocated/open; next unallocated **W6-F4**. W4-F6 remains unallocated.

## Coordinated perception checkpoint — 18 October, 19:29 AWST

[Ambient and internal-voice review](../handover/W6_F3_AMBIENT_AND_PERCEPTION_REVIEW_20261018.md) preserves Dragonfly Goggles direction, independent subtle-perception development, the authored sensory-return sequence, recovered ambient preferences and verified implementation gaps. Detailed Sarkar source review remains deferred. This checkpoint informs W6-F3; it does not authorise a general world-engine expansion or mark implementation complete.
