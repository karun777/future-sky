# Future Sky — System Map

**Version:** 0.4  
**Status:** Current orientation map through Feather 20  
**Reconciled:** 2026-08-31  
**Supersedes:** `SYSTEM_MAP_v0.3.md`

## Purpose

This document shows how the major conceptual, runtime, persistence and expression regions of Future Sky relate.

It is an orientation map—not the sole ontology, a data contract or a second Runtime Authority Register.

- `ARCHITECTURE.md` describes fundamental concepts, pending ontology reconciliation.
- `TRAJECTORY_v2.1.md` records constitutional direction.
- `WORLD_ENGINE_ARCHITECTURE_v0.2.md` describes how implemented world reality evolves.
- `RUNTIME_AUTHORITY_REGISTER_v0.3.md` records implemented stewardship.
- `EVENT_MODEL_v4.1.md` defines facts, observation and historical evidence.
- `DATA_CONTRACTS_v0.5.1.md` defines persistent paths and shapes.

Where implementation and aspiration differ, this map labels the distinction.

## Constitutional horizon

Future Sky is guided by:

- The Code is Love.
- Reality exists independently of its presentation.
- Every implemented category of truth has one identifiable steward.
- Emergence is preferred over premature prescription.
- Diversity strengthens coherence.
- History accumulates.
- Participation matters.
- Architecture preserves future possibility.

Natural Laws, Pramá, the Social Cycle and Love remain constitutional frames. They are not automatically runtime authorities, fields or scores.

## Whole-system view

```text
CONSTITUTIONAL FRAME
Natural Laws · Pramá · Social Cycle · Love
                     ↓ constrains
ONTOLOGY AND AUTHORING
World · Chapter · Scenario · Institution · Role · Character
Thread Node · authored opportunity · expressive World Moment
                     ↓ implemented through
RUNTIME REALITY
Heartbeat · World Time · Astrology · Comet · Era contribution
Temporal Resolution · Comet Pressure Field
                     ↓ produces
TEMPORAL OPPORTUNITY PIPELINE
Moment Boundary · Context · Match · Gate · Durable Instance
                     ↓ becomes observable through
EPISTEMIC PIPELINE
Event · Observation · History · Pattern
                     ↓ may inform
PARTICIPATION AND EXPRESSION
Scenarios · actions · narration · Discord · website · Feed7
```

The arrows describe dependency and constraint. They do not collapse these regions into one authority.

## 1. Constitutional frame

### Natural Laws

Describe the deepest declared principles governing movement and relationship.

### Pramá

Describes coherent development across diverse systems. It is not currently a runtime authority, field or writable simulation score.

### Social Cycle

Describes a constitutional pattern through which collective power may move. It is not currently an implemented World Engine subsystem.

### Love

Remains a constitutional and invisible vector. It is not implemented as arithmetic, ranking or causal machinery.

## 2. Ontology and authored structure

The conceptual vocabulary presently includes:

- World
- Chapter
- Scenario
- Institution
- Role
- Character
- Driver
- Action
- Thread Node
- World Moment
- Renderer

`ARCHITECTURE.md` and `SYSTEM_MAP_v0.3.md` previously made overlapping ontology claims. This revision ends that duplication: SYSTEM_MAP now maps relationships and defers definition of fundamental concepts to the reconciled ontology work.

Authored structures may state possibilities and conditions. They do not become canonical runtime truth merely by existing in a document or catalogue.

## 3. Implemented World Engine

### Cadence and time

- Heartbeat provides one runtime cadence.
- World Clock alone advances canonical world time.
- Temporal Resolver owns the effective temporal multiplier used by later advancement.

### Independent world truths

- Astrological Clock owns the observed real-sky snapshot.
- Comet Cycle owns authored comet state.
- Era profiles contribute baseline temporal policy.

### Derived world conditions

- Temporal Resolver combines independent temporal contributions.
- Comet Pressure Field projects comet pressure spatially using `uniform_global_v0`.

These derived systems do not reinterpret their inputs as story or meaning.

## 4. Implemented temporal-opportunity pipeline

```text
heartbeat.advanced
  → world_moment.eligible
  → world_moment.context
  → world_opportunity.eligible
  → world_opportunity.awakened
  → world_opportunity.instantiated
  → world_opportunity.expired
```

### Moment Boundary

Publishes a neutral fact for each crossed six-world-hour boundary.

This is one technical meaning of “world moment.” It must not be confused with an emergent Moment or an authored expressive World Moment.

### Context

Binds current durable facts without evaluating importance or meaning.

### Matcher

Compares context with authored opportunity requirements. A match creates eligibility, not selection.

### Gate

Applies authored awakening policy. Awakening is not scenario activation.

### Opportunity Runtime

Creates and advances durable world-scoped instances. It does not assign players or start memory-only scenarios.

## 5. Event and knowledge infrastructure

### Event Bus

Carries immutable facts, invokes subscribers independently and records their outcomes. It is infrastructure, not a world authority.

### Observation

An observer may publish that it observed a canonical fact. Observation does not replace the underlying truth.

### Event History

Durably records completed event dispatches and subscriber outcomes. History is evidence, not replay authority.

### Historical query

Reads remembered events without mutating history or rebuilding world state.

### Pattern recognition

Describes neutral structural relationships across remembered observations and cites its evidence.

The implemented boundary is:

```text
Reality → Event → Observation → History → Pattern
```

Relevance, resonance, convergence, interpretation and meaning remain outside the sealed runtime.

## 6. Participation systems

Characters participate within world reality through navigation, combat, actions, Thread Nodes, scenarios, storage and other gameplay systems.

Important boundaries:

- character state does not own world truth;
- Thread Nodes are authored interaction structures, not Item definitions;
- memory-only `ScenarioService` is not the durable World Opportunity Runtime;
- gameplay effects must not silently rewrite another authority’s canonical state.

## 7. Expression systems

Discord cogs, embeds, narration, ambient output, HUD, websites and Feed7 express selected truths.

Expression may frame experience. It does not own the underlying reality it presents.

Renderers should consume resolved state or published facts and remain replaceable.

## 8. Persistence regions

### World truth

- `data/time/world_clock.json`
- `data/astrology/current_snapshot.json`
- `data/comet/current_state.json`
- `data/time/temporal_resolver.json`
- `data/fields/comet_pressure/current_state.json`

### Opportunities

- `data/world_opportunities/catalogue.json`
- `data/world_opportunities/runtime_state.json`

### Historical evidence

- `data/events/event_history.jsonl`

### Participation and authored content

- `data/characters/characters.json`
- `data/rooms/rooms.json`
- `data/enemies/enemies.json`
- `data/items/items.json`
- `data/thread_nodes/thread_nodes.json`
- `data/storage/`

Exact ownership and shape belong to the Runtime Authority Register and Data Contracts.

## 9. Known seams

1. Some runtime authorities read another authority’s durable JSON directly.
2. `characters.json` contains namespaces stewarded by several gameplay systems.
3. `GameState` contains both persistent-domain access and ephemeral runtime containers.
4. Durable World Opportunity instances and memory-only scenarios are not yet reconciled.
5. “Moment” has three active meanings that require eventual terminology repair.
6. Event History requires a retention and rotation policy.
7. The fundamental ontology documents still require consolidation.

These seams are recorded constraints, not invitations to perform an unbounded refactor.

## 10. Current documentary authority

For implemented reality, consult in this order:

1. running code and verified persistent state;
2. `RUNTIME_AUTHORITY_REGISTER_v0.3.md`;
3. `WORLD_ENGINE_ARCHITECTURE_v0.2.md`;
4. `EVENT_MODEL_v4.1.md`;
5. `DATA_CONTRACTS_v0.5.1.md`;
6. this orientation map.

For constitutional meaning, consult `TRAJECTORY_v2.1.md`, the Red Book and other explicitly constitutional documents.

A constitutional declaration does not prove implementation. An implementation accident does not become constitutional truth.

## Closing principle

Future Sky is a constitutional universe implemented as a living system.

The map must show both what guides the universe and what presently runs—without mistaking aspiration for machinery, machinery for meaning, or presentation for reality.
