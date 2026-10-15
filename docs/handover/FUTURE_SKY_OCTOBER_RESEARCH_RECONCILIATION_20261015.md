# Future Sky — October Research Reconciliation Handover

**Date:** 2026-10-15  
**Status:** Documentary handover; no canon or runtime promotion  
**Base:** `main` at `ad9f851`  
**Research branch:** `research/narrative-context-trial-1`  
**Research checkpoint:** `6bf99eec63e160a5047bbf17d4d7f33b7e718fc5`  
**Runtime boundary:** Feather 20 remains the last documented sealed runtime feather.

## Why this exists

The 2026-08-31 Knowledge Atlas was accurate at its own checkpoint but did not point to subsequent September–October research isolated on another Git branch. A cold-start session therefore recovered the August relevance frontier but missed the newer Anchor and narrative-context work. This document restores discoverability without changing its authority.

## Source-of-truth boundaries

- **Implemented:** live code and persistent state on Neptune Lounge, then current runtime architecture. The research branch changes neither.
- **World canon:** Red Book and explicitly adopted authored canon. Research labels do not silently grant canonical status.
- **Current architecture:** seven reconciled `docs/current/` documents on `main`.
- **Working research:** the documents below on `research/narrative-context-trial-1`. These are proposals and authored working outlines, not new runtime entities, data contracts or a licence to implement Feather 21.
- **Author-level givens within working research:** distinguish deliberately specified outcomes from still-unsettled mechanism and from what Characters know. The files themselves continue to say *working research — not canon*.

## Recovered research documents

1. `docs/research/NARRATIVE_CONTEXT_MODEL_v0.1.md` (2026-09-02): authored contextual envelopes; situated perspective, typed relationships, possibility versus actuality, lightweight classification, Causal Layered Analysis.
2. `docs/research/ANCHOR_MODEL_v0.1.md` (2026-10-07): **Anchors bound possibility; they do not prescribe outcome.** An Anchor is provisionally an authoring relationship, not a new ontology primitive. Scope, provenance, fixed/variable conditions, five affected layers, attack vectors, bounded causal cascades and continuity breaches are explored.
3. `docs/research/THREE_ERAS_COMET_MACRO_CONSTELLATION_v0.1.md`: retained earlier research version, superseded *within research* by v0.2.
4. `docs/research/THREE_ERAS_COMET_MACRO_CONSTELLATION_v0.2.md` (2026-10-08): one long-period comet, three names/encounters, Jyotzon and Manzo fixed timeline histories, Omincron A–G, Cube and Broken Sky loops, efiishent/Vitriol continuity, Manzo opening and authored outcome.
5. `docs/research/TIMELINE_G_CUBE_LOOP_v0.1.md` (2026-10-08): detailed Timeline G chronology, Cube Loop, 2019 intervention and proposed retrocausal closure from Manzo success.
6. `docs/research/narrative-context-trials/MANZO_TREMBLING_GLASS_TRIAL_v0.1.md`: prose/contextualisation trial; not a canonical Manzo scene.
7. `docs/research/RETREAT_PORTAL_NARRATIVE_CONTEXT_TRIAL_1.md`: branch safety boundary, return path and outstanding trial-review questions.

## Recovered authored story structure — working, not promoted

- **One comet:** Jyotzon c. 98,000 BCE; Omincron encounter 2019 CE; Manzo c. 102,019 CE. Nominal cadence roughly 100,000 years; exact orbital dynamics unsettled.
- **Asymmetric timelines:** one fixed Jyotzon history, seven Omincron lines A–G, one fixed Manzo history. Their precise cross-line relationships remain open.
- **Cube Loop:** an ordinary CMYK Cube passes from Omincron into Jyotzon, is encoded and launched, returns to Omincron, and is carried back into Jyotzon. Its informational role is recursive; its matter need not be created from nothing.
- **Broken Sky / retrocausal loop:** the successful 2019 intervention makes possible the protagonists' journey to Manzo; their later Manzo success closes the causal conditions for the earlier intervention. Do not confuse causal completion with rewriting a persisted event.
- **Manzo opening:** protagonists arrive without knowing how or remembering who they are; must find one another and consciously recover faculties used unconsciously during 2019. Manzo's technologically mediated population has let some direct faculties atrophy.
- **Vitriol:** overtly directs an Earth-impact threat through a comet-possessing entity and a virus affecting people on Earth. The physical coupling of the proposed attraction is speculative, not established science.
- **Outcome given:** Vitriol is overcome, the comet is captured, Earth gains a small new moon rather than suffering catastrophe. Exact capture engineering and retrocausal transfer remain open. The dark entity's ultimately benign cosmic role is author-level revelation, not general Character knowledge.
- **Anchor attacks:** destroying records, corrupting belief, severing relationships and breaching reality are different operations. A cascade must follow declared dependencies; it cannot be invented from thematic similarity.

## What was checked on 2026-10-15

- `/opt/futuresky` live checkout on `main`; `futuresky-bot` active.
- `main` at `ad9f851`, research branch 10 commits ahead, 0 behind, seven research documents added.
- Live working tree had modifications in `data/characters/characters.json` and `data/time/world_clock.json`; these were not changed or staged.
- Research branch existed on GitHub but had not been fetched into the live Debian checkout.
- No runtime code, services, persistent state or Red Book content was changed by this reconciliation.

## Open questions — do not silently decide

1. Does the trembling-glass scene work as prose, and is Sera the right perspective holder?
2. Which candidate Anchor declarations should be retained, and which remain authorial possibilities?
3. How do the seven Omincron lines relate to one another and to fixed Jyotzon/Manzo histories?
4. What actually enables comet capture and sends/relates the necessary influence backward to 2019?
5. What is the virus–comet coupling, and which faculties do the protagonists recover?
6. How much of the macro constellation is to be formally adopted as canon, and by whom?
7. Is the next trial a deep Character study or a wider Scenario Field?

## Next bounded action

Review the October research **as writing first**, then its contextual envelope and Anchor claims. Confirm the working authored givens and identify remaining contradictions. Only then decide whether any research document merits a pull request into `main` as **research**, not canon. A future Feather 21 requires its own explicit architectural question and authorisation.

## Cold-start route

1. Read `docs/KNOWLEDGE_ATLAS.md` and `docs/current/TRAJECTORY_v2.2.md`.
2. Read this handover.
3. Consult `research/narrative-context-trial-1`, starting with the retreat portal, Anchor Model and macro constellation v0.2.
4. Inspect current runtime code before any implementation claim.
5. Preserve open questions; do not promote working research by implication.
