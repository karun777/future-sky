# W6-F3 — The Display Behind Your Eyes

Home wing: **W6 Expression**. Allocated by Karun on 18 October 2026, 18:46 AWST.
Status: **REVIEW — bounded implementation tested in isolation**, 18 October 2026. Internal voice and ambient boundaries discussed. Not deployed; live Discord verification remains open. No completed-count increment.

## Purpose and scope

Make the HUD intelligible as technology experienced by the character, within Discord's presentation. Establish its presence during awakening, its initial capabilities and the meaning or uncertainty of its readings. Fix display-state handling after the boundaries with internal voice and ambient events are agreed.

The implant can develop through character proficiency and gameplay upgrades. Hacking, corruption, faults and misuse are desired future possibilities, not implemented mechanics. Separate physical world conditions, the device's assessment and the character's interpretation. Inaccurate readings need traceable causes; changing a display must not change world reality.

The three coordinated channels:
- HUD: technological observation and interpretation.
- Internal voice: developing intuition/sixth sense, ordinary sensory enhancement and subtle perception beyond technological access; independent of HUD enablement. Source review and development mechanics remain deferred.
- Ambient events: distinguish continuing atmosphere, particular occurrences and character-specific reception. Larger event simulation remains deferred.

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

Internal-voice and ambient discussions are recorded in the coordinated review below. Next: review/deploy this bounded implementation and verify the display in Discord.

W6 completed count remains **2**; total sealed remains **18**. W6-F3 allocated/open; next unallocated **W6-F4**. W4-F6 remains unallocated.

## Coordinated perception checkpoint — 18 October, 19:29 AWST

[Ambient and internal-voice review](../handover/W6_F3_AMBIENT_AND_PERCEPTION_REVIEW_20261018.md) preserves Dragonfly Goggles direction, independent subtle-perception development, the authored sensory-return sequence, recovered ambient preferences and verified implementation gaps. Detailed Sarkar source review remains deferred. This checkpoint informs W6-F3; it does not authorise a general world-engine expansion or mark implementation complete.

## First implementation pass — 18 October 2026

Base source: `49d69c6ebfbd65fcfe646aee90dee3e39408ce89`. Built in isolated archive `/tmp/futuresky-w6f3-5w5irv30` on Neptune Lounge; live service and characters untouched.

Implemented:
- HudCog owns one renderer used by both navigation and explicit HUD commands. Off hides the automatic panel; explicit `!hud` confirms offline. Dark mode conceals telemetry; degraded state reports readings unavailable. Normal shows UNCALIBRATED for coherence, parallelism and commotion. No measurement producer is invented.
- Existing authored 97/78/LOW values remain in storage, but are not rendered as measured reality. HUD reads do not seed or save character state. Preference changes persist copied records with rollback on save failure.
- HUD commands added to private run-channel routing eligibility.
- First hands inspection notices the display once when visible. `!inspect hud` explains the display and working commands, respecting off/dimmed/degraded settings. This does not grant or disable intuition, narrator records or sensory capabilities.
- Brochure crash occurs only on its first recorded inspection per character. Previously recorded brochure discoveries count as already experienced; no replay on return/reload. Observation is persisted before presentation; this guarantees no duplicate on retry after a failed write, not exactly-once delivery across network failure.
- ActivityCog typing/messages in the owner's run channel now feed AmbientCog's monotonic activity path, cancelling pending rest/sleep. Recognized commands still update Ambient directly. No conversion/mixing of epoch and monotonic timestamps.
- Existing 120-second idle breathing space remains; after an idle Thread Node opens, Ambient rechecks current character state and suppresses atmosphere in that iteration.

Verification: **112 tests passed**, including **18 new tests** in `tests/test_display.py`, via `PYTHONPATH=bot /opt/futuresky/.venv/bin/python -m unittest discover -s tests`. Actual HUD/inspection/navigation callbacks, Activity listeners, Ambient loop body, production JSON writer and failure injection use synthetic temporary records. Fresh/legacy preferences, all display modes, repeat reads, save/reload, isolation, typing elsewhere/bots, failed discovery and HUD saves, and new-choice suppression are covered. No live command delivery claimed.

Scope limits:
- No calibration gameplay or numeric formula, upgrade tree, actual hacking/corruption, full sense-return sequence, chakra simulation, or new intuitive messages.
- Legacy `!hud_state` remains a display-state control; it does not prove physical damage or implement hacking.
- No global ambient loader/fallback overhaul, shared crash event, global NPC/object effects or general scheduling system. Those audit findings remain open.
- No change to returning-player wardrobe policy, shared pod presence or office secrecy prose.
- Console's older generic HUD helpers remain for compatibility, but Navigation and HudCog no longer use their default-percent path.
- The first display notice and crash are per-character authored experiences, not shared-world event instances. Richer event/perception integration remains future work.
- A successful state save followed by failed network delivery can consume a once-only presentation. No distributed exactly-once claim is made.

W6-F3 remains REVIEW pending live delivery/playtest. W6 completed count **2**, total sealed **18**, next unallocated **W6-F4**. W4-F6 unallocated.
