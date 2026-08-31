# Future Sky — World Engine Architecture

**Version:** 0.2  
**Status:** Current implemented architecture through Feather 20  
**Reconciled:** 2026-08-31  
**Supersedes:** `WORLD_ENGINE_ARCHITECTURE.md` v0.1 (Pre-Feather 8)

## Purpose

Describe the implemented architecture of the living simulation that powers Future Sky.

This document is not primarily concerned with gameplay. It is concerned with reality: how canonical world facts arise, persist, become observable, enter history and support neutral pattern recognition.

Runtime code is authoritative for implemented behaviour. Constitutional and ontological documents remain authoritative for declared meaning and permitted concepts.

## Relationship to the architectural corpus

`ARCHITECTURE.md` describes what kinds of things exist, pending ontology reconciliation.

This document describes how implemented world reality evolves.

`RUNTIME_AUTHORITY_REGISTER_v0.3.md` records who owns each implemented truth.

`EVENT_MODEL_v4.1.md` defines fact publication, observation, dispatch history and historical query.

`DATA_CONTRACTS_v0.5.1.md` defines canonical persistent paths and shapes.

These documents overlap only where a boundary must be made explicit.

## Core philosophy

Future Sky is world-driven.

Players do not create the universe. They participate within it.

The world exists before players, continues after players and evolves through authorities whose responsibilities remain narrow. Gameplay, narration and rendering may respond to reality, but they do not retroactively become its source.

## Architectural invariants

### One heartbeat

There is one canonical heartbeat cadence. Subsystems may observe it, but they do not create competing clocks.

### One world time

Only the World Clock advances canonical world time.

The effective temporal multiplier is resolved separately. A newly resolved multiplier influences later advancement; it does not rewrite the heartbeat from which it was derived.

### One steward per category of truth

Each authority owns one bounded category of canonical state. Consumers may react to its facts but must not silently assume its stewardship.

### Persist before publish

When an authority changes durable truth, it persists that truth before publishing the corresponding fact. Publication announces what became true; it is not a request for another system to make it true.

### Facts, not commands

Canonical events describe occurrences or state transitions. Subscribers decide independently whether and how to respond.

### Failure isolation

One subscriber failure must not prevent other subscribers from receiving a fact. Completed dispatch outcomes are recorded for diagnosis and history.

### Meaning is not smuggled into mechanism

Context, eligibility, awakening, observation and pattern are distinct from interpretation, relevance, resonance and meaning. The latter remain open research beneath the current implemented boundary.

## Implemented reality spine

```text
Heartbeat
  → World Clock
  → Reality authorities
  → Derived fields and temporal resolution
  → Moment boundary and context
  → Opportunity matching, gating and lifecycle
  → Observation
  → Event History
  → Historical query
  → Neutral pattern recognition
```

This is a dependency spine, not a claim that every fact passes through every stage.

## Authority layers

### Layer 1 — Cadence and canonical time

#### Heartbeat

Owns the runtime cadence and initiates world advancement.

#### World Clock

Owns canonical world time and publishes `heartbeat.advanced`.

It consumes the previously resolved temporal multiplier. No other subsystem advances world time.

### Layer 2 — Independent world truths

#### Astrological Clock

Observes real-sky Sun and Moon positions at the event UTC instant, persists `data/astrology/current_snapshot.json`, then publishes `astrology.snapshot_changed` when its stable fingerprint changes.

#### Comet Cycle

Derives authored comet state deterministically from world time, persists `data/comet/current_state.json`, then publishes `comet.state_changed` when a meaningful state band changes.

It owns comet cycle position, phase, pressure and temporal modifier. Its current cycle length is implementation scaffolding, not constitutional canon.

#### Era policy

Era time profiles provide the existing baseline temporal contribution. Their use is implemented; broader era ontology remains governed by constitutional documents.

### Layer 3 — Resolution and spatial projection

#### Temporal Resolver — Feather 8

Resolves era baseline and comet temporal influence into one `effective_temporal_multiplier`.

It persists `data/time/temporal_resolver.json` and publishes `temporal.resolved` when the resolved fingerprint changes.

It does not advance time, mutate comet state or alter era policy.

#### Comet Pressure Field — Feather 9

Projects canonical comet pressure into an addressable spatial field.

It persists `data/fields/comet_pressure/current_state.json` and publishes `comet_pressure_field.changed` when its fingerprint changes.

Distribution model `uniform_global_v0` is deliberately minimal. It does not invent regional attenuation, emotion, significance or narrative consequence.

### Layer 4 — Temporal opportunity boundary

#### World Moment Boundary — Feather 10

Detects six-world-hour boundaries crossed by canonical world time and publishes one `world_moment.eligible` fact per crossed boundary.

This implemented use of “world moment” means a neutral temporal eligibility boundary. It is not automatically an emergent Moment or an expressive authored World Moment.

#### World Moment Context — Feather 11

Consumes `world_moment.eligible`, reads current durable world facts and publishes `world_moment.context`.

Context binds facts together without classifying their danger, mood, importance or meaning.

### Layer 5 — World opportunities

#### Opportunity Matcher — Feather 12

Matches `world_moment.context` deterministically against authored definitions in `data/world_opportunities/catalogue.json` and publishes `world_opportunity.eligible` for each match.

Eligibility is not selection, awakening or scenario activation.

#### Opportunity Gate — Feathers 13 and 16

Owns the eligibility-to-awakening decision. It applies authored gate policy and, where required, checks durable runtime state before publishing `world_opportunity.awakened`.

It owns no opportunity instance and starts no scenario.

#### Opportunity Runtime — Feathers 14 and 15

Owns durable world-scoped opportunity instances in `data/world_opportunities/runtime_state.json`.

It creates instances from awakened facts, advances their authored lifecycle from heartbeat facts and publishes `world_opportunity.instantiated` and `world_opportunity.expired`.

It does not assign players, interpret narrative meaning or start memory-only scenarios.

### Layer 6 — Events, observation and memory

#### Event Bus — Feather 17

Publishes immutable event envelopes to independently invoked subscribers. It records subscriber outcomes and isolates failures.

The Event Bus is transport and dispatch, not world authority.

#### Comet Observation — Feather 18

Observes `comet.state_changed` and publishes `observation.comet_state`.

The observation asserts only that a canonical transition was observed. It does not replace comet truth or interpret significance.

#### Event History — Feathers 17 and 19

Appends completed dispatch records to `data/events/event_history.jsonl`, including the event and subscriber outcomes.

History is durable evidence of publication and reaction. It is not replay authority and does not recreate world state.

Read-only historical queries may filter remembered events without mutating them.

#### Pattern Recognition — Feather 20

Inspects remembered observation facts and identifies neutral structural relationships such as comet-pressure sequences.

A pattern records what recurred or changed and cites its source observation event IDs. It does not determine relevance, resonance, causality, intent, narrative significance or meaning.

## The implemented epistemic boundary

```text
Reality → Event → Observation → History → Pattern
```

Each transition changes what may honestly be claimed:

- Reality: an authority owns what is true.
- Event: a state transition or occurrence is announced.
- Observation: an observer records that it witnessed a fact.
- History: completed publication and subscriber outcomes are remembered.
- Pattern: structural relationships across remembered observations are described.

No implemented layer currently owns relevance, resonance, interpretation or meaning.

## Persistence model

Persistence is decentralised by stewardship. Each authority writes only its declared canonical store.

Important World Engine stores are:

- `data/time/world_clock.json`
- `data/astrology/current_snapshot.json`
- `data/comet/current_state.json`
- `data/time/temporal_resolver.json`
- `data/fields/comet_pressure/current_state.json`
- `data/world_opportunities/catalogue.json`
- `data/world_opportunities/runtime_state.json`
- `data/events/event_history.jsonl`

The exact contracts belong to `DATA_CONTRACTS_v0.5.1.md`.

## Known implementation tensions

These are recorded, not silently resolved:

1. Some authorities read another authority’s durable JSON directly rather than consuming a complete event projection or narrow query interface.
2. World Opportunity instances are durable, while `ScenarioService` remains memory-only. Their relationship is not yet reconciled.
3. “Moment” remains overloaded across emergent Moments, expressive World Moments and the implemented `world_moment.eligible` boundary fact.
4. Event History is growing and has no sealed retention or rotation policy.
5. Era profiles are operational inputs, but their broader canonical and policy ownership still requires ontology-level reconciliation.

These tensions are architectural work items, not permission for an implementation to invent meaning.

## What is not yet implemented architecture

The following remain deliberately open:

- relevance authority;
- resonance model;
- convergence or “knot” detection;
- interpretation authority;
- meaning assignment;
- Love as a computable score or causal arithmetic;
- temporal cohorts;
- automatic conversion of patterns into scenarios.

They may guide research and constitutional thought. They must not be described as runtime truth until explicitly designed, implemented and sealed.

## Test for a new World Engine authority

Before introducing one, ask:

1. What single category of truth does it own?
2. Is that truth already owned elsewhere?
3. What immutable facts does it consume?
4. What state does it persist before publication?
5. Does it publish facts rather than commands?
6. Can subscriber failure remain isolated?
7. Does it preserve the boundary between pattern and meaning?
8. Would the world remain coherent if it temporarily disappeared?

## Closing principle

Future Sky is not built from gameplay systems. Gameplay emerges within cosmological systems.

The World Engine maintains a living universe whose truths have identifiable stewards, whose changes leave evidence and whose patterns may be recognised without prematurely declaring what they mean.

> *The universe does not tell stories. Stories are what consciousness experiences while travelling through the universe.*
