# Awakening reconstruction — source and verification record

**Date:** 18 October 2026, Australia/Perth  
**Scope:** Reconstruct the day's creative work after restored Neptune Lounge access  
**Repository baseline:** `1df7bb31f78977df51b457948ba7d83c27c8892e`  
**Research baseline:** `dfe9e4a803bc75c852697af298c6d3f29c346c65` on `research/narrative-context-trial-1`  
**Main result:** [Awakening — a connected reconstruction](AWAKENING_RECONSTRUCTION_20261018.md)  
**Author's words:** [primary-source capture](AUTHORIAL_NOTES_20261018.md)

## What was actually read

### Foundational sources

- [Red Book v7.2](../RedBook_V7.2.md), read in full: eras, selves, arrival, Cube, uncertain-use artefacts, gifts, DPCs, music, real-world anchoring and recognition.
- [Knowledge Atlas](../KNOWLEDGE_ATLAS.md), [reset ritual](../R3GPT_RESET_RITUAL_v2.0.md), [Architecture v1.1](../current/ARCHITECTURE_v1.1.md), [Trajectory v2.2](../current/TRAJECTORY_v2.2.md), [feathering protocol](../archive/process-history/R3GPT_FEATHERING.md), and [phase closure](../current/PHASE_CLOSURE_EPISTEMIC_FOUNDATIONS_2026-10-15.md), reread from the host during reconnection.
- [The Eternal Struggle](../current/THE_ETERNAL_STRUGGLE.md), read in full; its proposed/review status retained.
- [Wakefulness](../archive/deep-research/WAKEFULNESS.md), read in full. Its archive classification is preserved even though its own header calls it canonical bootstrap.
- [Developer Codex v2.1 reference edition](../archive/reference-canon/developer_codex_v2.1_with_NRE.md), specifically §§2–3, 11, 17–18: developer role, cosmology, temporal layering and memory proposals. These sections were read; this pass does not claim a full Codex reread.

### Research read in full at the pinned research revision

- [Retreat portal](https://github.com/karun777/future-sky/blob/dfe9e4a803bc75c852697af298c6d3f29c346c65/docs/research/RETREAT_PORTAL_NARRATIVE_CONTEXT_TRIAL_1.md).
- [Narrative Context Model v0.1](https://github.com/karun777/future-sky/blob/dfe9e4a803bc75c852697af298c6d3f29c346c65/docs/research/NARRATIVE_CONTEXT_MODEL_v0.1.md).
- [Anchor Model v0.1](https://github.com/karun777/future-sky/blob/dfe9e4a803bc75c852697af298c6d3f29c346c65/docs/research/ANCHOR_MODEL_v0.1.md).
- [Three Eras / One Comet v0.2](https://github.com/karun777/future-sky/blob/dfe9e4a803bc75c852697af298c6d3f29c346c65/docs/research/THREE_ERAS_COMET_MACRO_CONSTELLATION_v0.2.md).
- [Timeline G / Cube Loop v0.1](https://github.com/karun777/future-sky/blob/dfe9e4a803bc75c852697af298c6d3f29c346c65/docs/research/TIMELINE_G_CUBE_LOOP_v0.1.md).

The Narrative Context Model explicitly puts writing before classification, uses the lightest context needed, and distinguishes necessary, contributing and sufficient conditions. The Anchor Model preserves reality/evidence/knowledge distinctions. Those are useful methods here, not permission to promote research or instantiate an Anchor subsystem.

The trembling-glass trial was not freshly reread in this reconstruction; earlier handover references remain only pointers.

### Attachments inspected as historical sources

| Attachment | Work performed | Authority boundary |
| --- | --- | --- |
| 250702 Future Sky Lore.pdf | Text extracted and read in full | July-era dates and seven timelines retained as lineage |
| 250702 Red Book Future Sky.pdf | Text extracted and read in full | Historical edition, not automatically identical to repository PDF or v7.2 |
| 250702 Future_Sky_Character_Classes.pdf | Text extracted and read in full | Seven older class names differ from current Red Book; not imported as current class requirements |
| rooms (1).json | All nine room identities, descriptions and exits read | Compact historical geography, not live map |
| rooms.json | Room count and identity range inspected | 93-entry legacy attachment, not current configured 43-room map |
| discord_game_bot.py / bot.py | AST function inventory inspected | Older monolithic prototypes; not executed or mistaken for running source |
| application.yml, characters.json, enemies.json | Not freshly read | Not needed for these authoring questions; no claim of exhaustive attachment audit |

PDF SHA-256 identities:

- Lore: `6af46d72d80578ad6e5e493ab6fc1b81e0b4d15eea7bdbce3b9054355cf26b59`
- Red Book: `d5ea16a924e3f37fdacf75f657590489b0246a21f17af5eae4031839d22bb2c1`
- Classes: `412d82929bc9a6d9f8278ce8ce4a9b2f74da41ac9c5d70e16ab4f9a50c02fe4e`

### Authored opening and current work

Read the [archived arrival](../archive/process-history/arrival.md), current awakening node, narrator entries and selected live room content. Recovered [First Night / Feather 32](../current/NEPTUNE_LOUNGE_FIRST_NIGHT_v0.1.md), W2-F3 and its inspection/preparation addenda, W4-F3, the brain/reintegration canon note, gift record, development direction and current wing register.

The actual generated pod still had already been visually inspected feature by feature during the inspection pass. Its inventory and image identity remain linked rather than generating another unreviewed scene.

Conversation retrieval recovered a specific prior user instruction to give the Queen a rat-sized Tiny Book from the office/quarters. Current item and gifting code corroborate that concrete strand. Conversation search summaries are not treated as literal transcripts; the primary-source capture for today is transcribed from the visible messages.

## Live connection and state

MacBook Desktop Commander → SSH alias `neptunelounge` is restored. The service reports active, PID **799778**, started **17 October 2026 12:50:26 AWST**. Runtime checkout HEAD remains `937c007a2981d10b8e1230f293c85b6c72750425`.

The checkout contains live data modifications and intentional documentation/test/tool overlays. None was reset, stashed, broadly staged or replaced with a whole-tree pull.

During reconnection, ten documentation files were selectively synced from main `1df7bb3`; 126 relative links were checked. That was a documentation update, not movement of runtime HEAD or a service restart.

### Source checks performed on the host

| Source | Observed boundary |
| --- | --- |
| CoreCog | Current on-disk source matches inspected Git; creation stores pod but welcome describes Lounge and does not start awakening directly |
| ThreadNodesCog | Current source matches Git; selected option completes awakening node; shared multi-step exploration not implemented there |
| Narrator catalogue / archived arrival | Initial byte comparison differed; decoded unified diffs were empty, identifying line-ending differences rather than changed text |
| InspectionCog / item_inspection | Current item inspection is catalogue/visibility based, not room-fixture/body inspection |
| WardrobeCog / catalogue | Four provisional choices; explicit pod search/token and motif follow-up already exist |
| ScenarioService | In-memory, per-player active/completed instances; factual history inside instances, no durable shared two-day mission |
| ScenarioEngineCog | EventBus bridge and a hard-coded Portal Run proof; not this quest |
| GiftingCog | Gives between co-located stored characters; shared save with rollback on save failure; Tiny Book acknowledgement exists |
| Local room/item content | Pod-to-Lounge route and performance surroundings exist. Tiny Book/Compass definitions exist; office's live item list differs from original placement, which is legitimate world-state evidence to preserve |

The service's active status and on-disk matches do not inspect every object in process memory. No Discord gameplay, real-player movement, real gift transfer or live event replay was invoked.

### Critical implementation findings

1. **There is existing grammar to build on.** We do not need to invent the World, Scenario, Role, Character or Driver anew.
2. **The full experience is not joined up.** Creation, scene triggering, inspection, media and onward orientation need a deliberate local integration.
3. **Durable shared quest memory is not supplied by ScenarioService.** Existing durable event history is separate; it cannot be equated with a complete multiplayer quest state.
4. **Gift code can expose presentation concerns.** The Tiny Book acknowledgement names the Queen. A disguised royal encounter must not reuse an output that leaks the secret identity merely because it uses the same item.
5. **A den description is not encounter entitlement.** The world already names the Queen publicly in lore/rooms; the secret is the princess's identity connection within Efiishent's special encounter. The general text and restricted encounter presentation need deliberate alignment before live play.
6. **Role transfer is still a future capability.** Human participation in existing NPC roles is a stated horizon, not something verified by a Script-driven Thread Node.

## Corrections made to today's earlier work

| Earlier weakness | Correction |
| --- | --- |
| Classifying nearly every sentence before letting the account live | Narrative-first reconstruction, with the author's words preserved separately |
| Reducing old arrival material mainly to obsolete mechanics | Restore hands, sensory embodiment, HUD, FEED7 and comfortable cubicle as useful authoring lineage |
| Calling Tiny Book only an ungrounded possible match | Recover the prior specific gift/office instruction and inspect actual item/gifting source |
| Leaving memory retention versus amnesia unresolved after clarification | Link the adopted gradual reintegration canon into W4-F3 |
| Creating decorative objects in an image without support | Keep the complete visible-feature inventory and require retained details to support attention |
| Treating uncertain gift relevance too narrowly as validation | Preserve ordinary, relational and personal significance while separating reported physical receipt from fictional transfer |
| Sounding as though reconnection itself restored creativity | Distinguish live verification from the assistant's responsibility to read, synthesise and reason carefully |
| Accumulating next-step proposals | Keep one current home, review status and connected return entry point |

## Offline logic rehearsal

Files: [rehearsal](../../tools/authoring/chapter_one_rehearsal.py), [test cases](../../tools/authoring/test_chapter_one_rehearsal.py).

Executed with standard-library unittest in an isolated scratch directory: **19 tests passed**.

```bash
python -m unittest discover -s tools/authoring -p 'test_chapter_one_rehearsal.py' -v
```

What was tested: closed/unknown/open opportunity answers under supplied facts; synthetic exact boundary ticks; privacy/recognition/willingness; separate participant perspectives; retained actual occurrence under disputed credit; idempotent event delivery; immutable returned fact payload; non-duplicating item-instance custody; sample cycle retention plus JSON reload; and the non-equivalence of other gifts or in-game transfers to the particular IRL relevance condition.

What was **not** tested: actual musical quality adjudication, real NPC decisions, Discord routing, missing chapter content, live persistence, concurrency, transaction recovery after crash, production access control, actual scenario timing or physical-world verification.

Synthetic half-open intervals and sample retention are explicitly experimental policies. The code is an authoring exhibit with no imports into `bot/`, no environment or credentials, and no live data paths.

## Completion and return

This reconstruction is complete as a bounded source review, synthesis and isolated logic demonstration. It does **not** seal W2-F3 or W4-F3 as approved playable content. Counts remain 16.

The original research branches, Red Book and live gameplay remain unchanged. The reconstructed entry point, primary notes, revisions and rehearsal are saved together so the next session can resume without Karun re-explaining the world.

## Author clarification — 18 October 2026, 17:05

Karun clarified that Efiishent's preservation was near the end of his ordinary earthly human life in Omincron; the earlier portal passage was at Earthdance 2024. In his encounter, the sadvipran alien embassy representative, ambassador, princess and Dark Rat Queen are one person.

The common mission is available to any player: meet an allied-faction representative and trade, with romance optional. Puzzler and Queen particular instances are for later authoring. The reconstruction and W4-F3 now distinguish that common quest from Efiishent's performance/private encounter. Every quest leaves a footprint with privacy paramount; discoverability does not confer unrestricted access to private history.

Four common-quest boundary cases were added to the offline rehearsal. **Current total: 23 passing tests** (the 19-test results above describe the original reconstruction run). They exercise a common trade opportunity without musical or romantic facts, missing exchange information, refusal and an expired window. Production access control/privacy enforcement remains outside this rehearsal; no such guarantee is claimed.
