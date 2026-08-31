# Future Sky — Runtime Authority Register

**Version:** 0.3.0-working  
**Date:** 2026-08-31  
**Status:** Evidence-based working reconciliation; not yet canonical  
**Evidence base:** Live Python source supplied from `/opt/futuresky` on 2026-08-31, current through sealed Feather 20.

## 1. Purpose

This register records what the current runtime demonstrably owns.

It distinguishes:

- **authority** — owns and may change one category of canonical truth;
- **persistence boundary** — stores truth without owning its semantic meaning;
- **query boundary** — exposes existing truth without maintaining a second copy;
- **policy evaluator** — decides permission or resolution without owning source truth;
- **observer** — publishes a new fact about an observed fact;
- **historical substrate** — preserves evidence without becoming gameplay state;
- **expression/interface** — presents or delivers experience without determining gameplay truth.

Runtime code wins for statements about what is implemented. Constitutional and ontology documents retain authority over what Future Sky means and what concepts may become canonical.

## 2. Runtime entrypoint

`bot/run_bot.py` is authoritative only for runtime composition:

- instantiated shared services;
- loaded extensions;
- extension load order;
- bot startup;
- heartbeat activation.

It does not own the truths stewarded by the components it wires.

## 3. Core authorities

| Runtime component | Classification | Demonstrated ownership | Persistence | Publishes / exposes |
|---|---|---|---|---|
| `GameState` | Authority with legacy support duties | Canonical world time, heartbeat lifecycle, era resolution | `data/time/world_clock.json`; limited character shape/void repair | `heartbeat.advanced` |
| Navigation | Authority | Character location and movement transition | `characters.json` through Storage | `character.entered_room` after persistence |
| `ScenarioService` | Authority, currently memory-only | Active/completed scenario instances, variables, flags, steps and factual scenario history | In memory only | Scenario lifecycle records through its API; the service itself is not wired directly to EventBus |
| Thread Nodes | Authority within character namespace | Entanglement, active node, completed node events, pending answers and node effects | `characters.extra.thread_nodes` through Storage | Reacts to `character.entered_room`; presentation and state outcomes |
| Combat | Authority | Per-room combat lifecycle, turns, intents, character combat flags, combat HP consequences and enemy-instance HP | Combat loop in memory; character and room-instance changes through Storage | Primarily command/runtime outcomes; not yet integrated as a broad event publisher |
| Router | Authority for delivery infrastructure | Run-channel lifecycle and routing decisions | Character routing fields through Storage | Routed delivery helpers |
| Astrological Clock | Authority | Current observed real-sky Sun/Moon snapshot | Dedicated astrology snapshot JSON | `astrology.snapshot_changed` |
| Comet Cycle | Authority | Comet cycle position, phase, pressure and temporal modifier | `data/comet/current_state.json` | `comet.state_changed` |
| Temporal Resolver | Policy authority | Effective temporal multiplier derived from era and comet contributions | `data/time/temporal_resolver.json` | `temporal.resolved` |
| Comet Pressure Field | Field authority | Distribution of comet pressure across current world scopes | `data/fields/comet_pressure/current_state.json` | `comet_pressure_field.changed` |
| World Opportunity Runtime | Provisional runtime authority | Opportunity instance identity, status, lifecycle timestamps and active/expired history | `data/world_opportunities/runtime_state.json` | `world_opportunity.instantiated`, `world_opportunity.expired` |

### Qualification: GameState

`GameState` is architecturally the Clock authority but still performs limited character-shape and void-rescue repair. Combat and Activity also attach ephemeral dictionaries to `bot.state`. This makes `GameState` a practical shared runtime container in addition to its clean clock responsibility.

That is current implementation truth, not an ideal ownership model.

## 4. Persistence, query and calculation boundaries

| Component | Classification | Responsibility | Must not become |
|---|---|---|---|
| `Storage` | Central persistence boundary | Atomic JSON loading/saving; in-memory access to characters, rooms, enemies, items, lockers, vault, cubes and modifier layers | Semantic owner of every stored namespace |
| `Presence` | Canonical query boundary | Answers which characters exist and which occupy a room using Storage and GameState truth | A second mutable presence store |
| Modifier Resolver | Pure calculation authority | Computes an effective in-memory character view from spine, context and modifier layers | Persistence or source-character authority |
| Config | Configuration/path authority | Canonical legacy paths and safe environment parsing | Gameplay authority |

Storage owns persistence mechanics. Domain systems own the meaning of the fields they are permitted to mutate.

The present architecture is therefore largely **namespace-authoritative over centrally persisted JSON**, not file-authoritative in every case.

## 5. Event, observation, history and pattern stack

| Component | Classification | Owns | Explicitly does not own |
|---|---|---|---|
| `EventBus` | Infrastructure | In-memory subscription, isolated dispatch, subscriber tracing and bounded recent traces | Gameplay state, narrative or durable history meaning |
| `EventHistory` | Historical substrate | Append-only evidence of completed dispatches and subscriber outcomes | Gameplay state, replay, reconstruction, subscriber invocation or interpretation |
| Comet Observation | Observer | Canonical observation fact derived from `comet.state_changed` | Comet truth or comet meaning |
| Pattern utilities | Descriptive evaluator | Derived descriptions of historical observation sequences | Meaning, response, authority or narrative consequence |

Current canonical event envelope implemented by `create_event()`:

- `event_id`
- `event_type`
- `occurred_at_world_time`
- `occurred_at_utc`
- `source`
- `scope`
- `payload`
- `causation_id`
- `correlation_id`
- `schema_version`

The runtime boundary is:

```text
AUTHORITY TRUTH
    ↓
EVENT FACT
    ↓
OBSERVATION FACT
    ↓
HISTORICAL EVIDENCE
    ↓
DESCRIPTIVE PATTERN
```

No reviewed code crosses from pattern into relevance, interpretation, resonance, meaning or response.

## 6. Provisional World Moment / Opportunity pipeline

| Component | Classification | Actual current responsibility |
|---|---|---|
| World Moments | Temporal boundary publisher | Converts heartbeat progression into periodic `world_moment.eligible` facts; owns no gameplay or narrative meaning |
| World Moment Context | Context assembler | Reads authoritative conditions and publishes `world_moment.context`; owns no source truth or interpretation |
| World Opportunity Matcher | Authored-condition evaluator | Determines whether authored conditions match a context; owns no world or scenario truth |
| World Opportunity Gate | Policy evaluator | Owns the eligibility-to-awakening permission decision; owns no runtime instance state |
| World Opportunity Runtime | Runtime authority | Creates, ages and expires durable bounded instances |

Pipeline:

```text
heartbeat.advanced
    ↓
world_moment.eligible
    ↓
world_moment.context
    ↓
world_opportunity.eligible
    ↓
world_opportunity.awakened
    ↓
world_opportunity.instantiated
    ↓
world_opportunity.expired
```

Architectural status:

- `world_moment.eligible` is implementation vocabulary for a temporal observation boundary.
- It is not yet the emergent **Moment** described by `TRAJECTORY`.
- It is not the expressive **World Moment** described by `ARCHITECTURE` and `DATA_CONTRACTS`.
- World Opportunity remains provisional implementation language.
- Its durable runtime instances resemble Scenario substrate, but that equivalence is not yet canonical.

## 7. Gameplay and character-domain systems

These systems own behaviour or bounded namespaces but are not separate universe-level authorities merely because they are cogs.

| System | Current responsibility |
|---|---|
| Core | Character onboarding, inspection, inventory/storage commands and assorted legacy command surfaces |
| Rebirth | Character lifecycle reset/reincarnation operation while preserving cube/storage boundaries |
| Ambient | Ephemeral pacing and player ambient state; routes through Router |
| Narrator | Subjective, non-blocking impressions and per-character seen-state |
| Activity | In-memory activity timestamps and run-channel discipline |
| Cube cog | Cube inspection/command surface; delegates persistence to Storage |
| HUD | Telemetry presentation and per-character HUD preferences |
| Astro cog | Player-facing astrology interface and character astrology metadata |
| Skill cogs | Player actions and bounded character-state effects: Absorb, Attune, Catalyse, Descalate, Hold, Perceive and Sneak |
| Speech / Emotes | Player expression surfaces |
| Help | Documentation/command interface |
| Console UI | Deterministic formatting and presentation |

Their exact semantic field ownership belongs in Data Contracts, not in a list that promotes every implementation module into a fundamental authority.

## 8. Confirmed alignment with constitutional architecture

The reviewed runtime materially preserves:

- one steward per category of truth;
- persistence before fact publication;
- facts before reactions;
- independent subscribers;
- observation before intervention;
- memory before meaning;
- world continuity without player presence;
- presentation outside gameplay authority;
- descriptive signals and patterns without undeclared mechanics;
- narrow, testable architectural additions.

The code and constitution are strongly resonant. Current drift is mainly vocabulary, document completeness and a few proof-slice couplings.

## 9. Known coupling and integrity risks

### 9.1 Direct reads of another authority's persistence

Current proof-slice couplings include:

- World Clock reads Temporal Resolver state JSON.
- Temporal Resolver reads Comet Cycle state JSON.
- Comet Pressure Field reads Comet Cycle state JSON.
- World Opportunity Gate reads World Opportunity Runtime state JSON.

These preserve read-only ownership in practice but couple consumers to another authority's storage representation. Stable fact/query contracts are the likely long-term boundary. No immediate refactor is required solely for documentary purity.

### 9.2 Shared mutable `characters.json`

Navigation, Combat, Thread Nodes, Router, Narrator, HUD, Rebirth, skill cogs and other systems mutate different portions of the same character records through Storage.

This is valid only if field/namespace ownership is explicit. `DATA_CONTRACTS_v0.4.md` does not yet describe all current writers with sufficient precision.

### 9.3 `GameState` as shared container

Combat stores `bot.state.combats`; Activity stores `bot.state.last_activity_at`.

These are ephemeral and do not currently corrupt clock truth, but they blur the claim that GameState owns only temporal state and minimal player guarantees.

### 9.4 Scenario persistence gap

`ScenarioService` calls itself the active scenario authority but is memory-only. World Opportunity Runtime has durable bounded-instance persistence. Their future relationship must be resolved before either becomes the definitive Scenario runtime.

### 9.5 Version metadata drift

Several file headers and version comments predate the code now loaded around them. Entrypoint composition is more current than embedded version labels.

## 10. Required document updates

### Event Model v4

- Add `schema_version` to the envelope.
- Separate bounded in-memory flight recording from durable Event History.
- Remove any implication that history reconstructs authoritative state.
- Recognise derived event publication by observers/subscribers without allowing fabricated source facts.

### World Engine Architecture

- Replace “authorities publish observations” with “authorities publish facts; observers may publish observation facts.”
- Add the implemented temporal, comet, field, observation and history layers.
- Preserve “world-driven, event-mediated” as the reconciliation between world and event architecture.

### Data Contracts

- Inventory every current persistent store.
- Define namespace-level writers for shared character records.
- Add event history, astrology, comet, temporal, field and World Opportunity stores.
- Resolve the World Moment terminology collision.

### Architectural ontology

- Reconcile `ARCHITECTURE.md` with `SYSTEM_MAP_v0.3.md`.
- Distinguish emergent Moment, expressive World Moment and temporal observation boundary.
- Decide whether World Opportunity is merely provisional Scenario machinery.

## 11. Current authority hierarchy

When evidence conflicts:

1. Runtime state and logs establish what actually happened.
2. Runtime code establishes what is actually implemented.
3. Contracts establish intended ownership boundaries, unless shown stale.
4. Ontology establishes what concepts may become canonical.
5. Constitution establishes why the system exists and what direction must be preserved.

This is not a hierarchy in which code overrules meaning. Each layer has final weight only within its own question.

## 12. Status and next step

This working register supersedes `RUNTIME_AUTHORITY_REGISTER_v0.2.md` only as a description of the runtime observed on 2026-08-31.

It does not yet supersede v0.2 canonically.

Before sealing v0.3:

1. verify the loaded extension list against a live successful boot log;
2. verify current persistent paths on Neptune Lounge;
3. decide the canonical relationship between ScenarioService and World Opportunity Runtime;
4. decide whether query boundaries and policy evaluators belong in the formal register alongside authorities;
5. resolve terminology without silently changing ontology.

Until then, use this document as the evidence-based working map for the Knowledge Atlas and subsequent document reconciliation.
