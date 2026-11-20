# Astrology and the living world

Design checkpoint · 20 November 2026 · FS-W3-F4 · proposed architecture, not deployment

## Source and authority

Verified in the Future Sky checkout at ed41e17 on neptunelounge:

- `bot/fsbot/astrology.py`: Swiss Ephemeris tropical geocentric planetary signs. Missing time defaults to noon and missing timezone to UTC, with assumptions recorded. No houses, aspects or ascendant. This is a partial calculator, not a complete natal/interpretation engine.
- `bot/fsbot/cogs/astro_cog.py`: player command computes placements and persists character astrology metadata. Existing account-keyed access needs the future shared character resolver.
- `bot/fsbot/cogs/astrological_clock.py`: observes real-UTC Sun/Moon positions on heartbeat advancement, persists a snapshot, then emits a change fact. This is distinct from natal identity and accelerated fictional world time.
- `players-handbook/02_character_creation/08_astrology_birth_and_fate.md`: tendencies and pressures with agency, growth and experience. Its resonance/mechanical descriptions are design intent, not proof of implemented modifiers.
- `docs/RedBook_V7.2.md`: real-life player birth-chart/chakra premise. Its application to fictional transferable characters is unresolved; do not silently use the future controller’s chart.
- `docs/current/WORLD_ENGINE_ARCHITECTURE_v0.2.md` and `RUNTIME_AUTHORITY_REGISTER_v0.3.md`: one clock, bounded authorities, persistence before publication, events as facts, implemented observation/history/pattern boundary.

The separate Neptune Lounge repository at `/home/efiishent/projects/neptune-lounge` (5198e8d) and its local branch/remote refs were searched for astrology, ephemeris and birth-chart references in Markdown/Python. No matching framework document was located there. The expression worktree search likewise found none. This does not prove that the intended framework is absent from the server or other materials. The verified FS sources above are the starting point; the intended wider NL framework remains an explicit source-resolution task. No private source data was imported.

## Three things to keep distinct

1. Birth record: what event is charted, where and when, precision, calendar/era and source.
2. Calculated chart: reproducible positions and supported relationships under a named reference frame and version.
3. Interpretation: Future Sky rules translating chart features into conditional response tendencies. Version separately from astronomy. Keep reasons inspectable.

Do not pretend an Earth tropical geocentric calculation automatically describes a Triton birth or every era. Select the frame and the meaning of birth before computing the six drafts. Reanimation need not erase a natal record. Unknown inputs must not become falsely precise facts. A noon/UTC fallback is an assumption, not a known birth time.

## Author clarification: Earth context and the unconscious — 20 November 2026

Karun places the interpretive starting point with players here on Earth in 2026. They bring Earth-based astrological language and data into play while assuming a character situated in a future, potentially non-Earth environment. Their reasonable assumption of Earth origin supplies a bridge into the fiction; it does not establish every character’s birthplace or require us to invent an alien zodiac before proceeding.

The proposed working premise is to imagine a natal chart as a map of the unconscious: a structured vocabulary for underlying drives, conditions, dispositions, tensions and habitual responses. Future Sky can explore the complexity articulated by that body of knowledge without requiring participants to accept its claims as gospel. This is an interpretive design premise, not a scientific validation claim or a diagnosis of a player.

Under this premise, an Earth-referenced chart can supply a psychological foundation whose expression is shaped by future embodiment, culture, relationships, experience and immediate circumstances. Literal local-sky calculation is a separate question. The earlier frame warning concerns labelling calculations honestly; it must not become a requirement to solve extraterrestrial astrology before exploring character psychology. Whether a given chart represents an Earth-origin birth, an authored symbolic foundation or another agreed basis remains a recorded design choice. Do not manufacture historical birth facts to justify a symbolic chart.

Keep three layers distinct: the human player’s present context, the character’s enduring natal/psychological foundation, and the character’s current fictional environment. Their relationship needs explicit authoring. This clarification does not automatically substitute an account holder’s personal chart into an existing character, nor make player birth-data collection a prerequisite. A transferable character retains continuity across drivers.

The interpretive framework must preserve complexity: interacting tendencies, inner conflicts, different expressions under pressure, and growth through awareness and experience. Avoid one-sign personality labels, fixed moral judgements or predetermined responses. NPC response logic should make room for the interplay of chart, memory, circumstance and choice; human players retain agency.

Karun regards the astrological tradition as a rich, openly accessible knowledge resource while recognising competing branches, inconsistencies and what he considers distortions or corruptions. We therefore need to agree a coherent shared framework rather than blending incompatible schools opportunistically. Public availability is not a blanket licence for modern texts, datasets or software; retain source and reuse provenance as materials are selected.

Near-term design work: locate/recover the intended framework; agree its vocabulary, chart basis, selected interpretive relationships and exclusions; distinguish calculation conventions from interpretation; version that agreement; then examine one character in a few concrete situations. This remains a carry-forward within the existing FS-W3-F4 checkpoint and its cross-wing engine follow-up. It is future work close enough to guide the cast now, not an invitation to expand this pass into a complete astrology engine.

## What exists and what comes next

The source already has structured files, authored world definitions, character storage, a canonical clock, event dispatch, opportunities, observation, durable event history and neutral pattern queries. Current runtime persistence includes JSON; this checkpoint does not claim SQL migration or live-service verification.

Markdown documents explain meaning and authority. JSON holds machine-readable definitions and state. Media supplies sensory material. Stable IDs connect them. SQL can later enforce transactions, references and efficient queries for mutable state. It complements the authored repository; it does not replace prose, media or interpretation.

A knowledge repository is not automatically a knowledge engine. Retrieval must select current, permitted evidence with provenance; author-only outcomes and another character’s private knowledge must not enter an NPC context. An AI model can compose a response from that packet. It cannot grant itself authority to change the world.

Proposed NPC flow: situation → authorised known context + natal interpretation + remembered experience → candidate response/action → ordinary engine validation → durable accepted outcome → event → HUD/Discord presentation. Player control bypasses NPC decision generation, while retaining the same character and ordinary game rules. Recheck the current driver before applying queued work.

No model call is needed to advance every tick. Deterministic code can detect meaningful transitions, eligibility and nearby needs cheaply. Only selected jobs need generated prose or dialogue. Generated content remains a candidate until validated. Existing narrative/scripted portrayal remains a usable fallback.

## Scheduling and preparation

Cron is useful for wall-clock maintenance, backups and batch preparation. Fictional world advancement remains under its existing canonical clock. A due-time queue and event subscribers can respond to changed world facts and prepare likely encounters before players arrive. Do not add a second world clock.

Proposed generation jobs need event/character/version identifiers, deduplication, retry limits, budgets, cancellation and freshness checks. Cache reusable scene material; bind player-specific content only to permitted knowledge. Discard or regenerate stale candidates if the world or controller changes. Prepared possibilities do not become completed events until their ordinary activation conditions hold.

For example: an eligible briefing can prepare descriptions and possible greetings for known participants. It cannot claim attendance, assign a berth, accept work, or predetermine an outcome. Real players may leave the invitation waiting.

## Bounded follow-up, not yet allocated

Within FS-W3-F4: reconcile the intended framework, establish six fictional birth records, produce reproducible natal charts, and review a single shared situation portrayed through each character’s history and natal tendencies. Keep cast and charts in review until accepted.

Cross-wing engine follow-up: implement one versioned, explainable natal-to-response contract in an isolated fixture first. W1 reviews meaning; W3 reviews portrayal and continuity; W5 resolves time/frame semantics; W7 builds and tests computation and action authority; W4 receives permitted undertaking effects. Allocate its implementation feather after checking the current index for overlap. Do not allocate a broad autonomous-agent programme as a prerequisite.

Tests when implementation begins: repeatable calculations, explicitly unknown inputs, different charts in the same situation, same chart with changed experience, no player compulsion, no author-only knowledge leakage, stale queued work after handover, idempotent retry and persistence-before-event. No production changes, real account assignments or character resets are authorised by this note.
