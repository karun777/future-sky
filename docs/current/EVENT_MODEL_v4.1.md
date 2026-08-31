# Future Sky — Event Model

**Version:** 4.1  
**Date:** 2026-08-31  
**Status:** Sealed production foundation  
**Supersedes:** `EVENT_MODEL_v4.md`  
**Runtime evidence:** Verified against the live Event Framework and sealed Feathers 17–20.

## 1. Purpose

This document defines the canonical architecture for event-driven cooperation inside Future Sky.

Future Sky is world-driven and event-mediated.

The world and its authorities determine what becomes true. The Event Framework communicates completed facts so independent systems may observe and respond without being directly invoked by the authority that changed reality.

The Event Framework is infrastructure. It is not ontology, gameplay state, narrative authority or an omniscient director.

## 2. Core law

> **Reality changes through its authorities. Authorities publish completed facts. Systems observe. Behaviour emerges.**

The implementation rule remains:

> **Publish facts. Never invoke unrelated behaviour.**

Good:

```text
Navigation persists the character's new location.
Navigation publishes character.entered_room.
Thread Nodes, Narrator and other subscribers react independently.
```

Bad:

```text
Navigation calls Thread Nodes.
Navigation calls Narrator.
Navigation calls Ambient.
```

Navigation owns movement. It does not own storytelling, ambience or entanglement.

## 3. Authority, fact and observation

### Authority

An authority owns one category of canonical truth.

An authority may:

1. observe relevant input;
2. evaluate its own responsibility;
3. persist its resulting truth;
4. publish a fact describing what became true.

### Event fact

An event is an immutable announcement of a completed fact.

It does not make the fact authoritative. The publishing authority and its persisted state do that.

### Observation fact

An observation is a new fact about something observed.

An observer may publish a derived observation event when:

- the source fact is identified;
- causation and correlation are preserved;
- source truth is not overwritten;
- the observation does not claim undeclared meaning.

Example:

```text
comet.state_changed
    ↓
observation.comet_state
```

The first event announces comet truth. The second records what the observer noticed about that truth.

## 4. Event envelope

Every canonical runtime event contains:

```text
event_id
event_type
occurred_at_world_time
occurred_at_utc
source
scope
payload
causation_id
correlation_id
schema_version
```

### `event_id`

Unique event identity.

### `event_type`

Stable dotted vocabulary describing the completed fact, such as:

```text
heartbeat.advanced
character.entered_room
comet.state_changed
observation.comet_state
world_opportunity.instantiated
```

Event names describe facts in the past tense or an explicitly defined factual state.

### Time

`occurred_at_world_time` records canonical world time.

`occurred_at_utc` records when the event envelope was created in real-world UTC.

Neither field alone defines narrative time or participant experience.

### Source

`source` identifies the publishing system and optional actor.

```json
{
  "system": "navigation",
  "actor_id": "character_id"
}
```

### Scope

`scope` identifies relevant world context without claiming ownership of it.

Potential fields include:

```text
world
era
room
chapter
scenario
```

### Payload

`payload` contains only information required to understand the fact.

It must not become an undeclared copy of another authority's entire state.

### Causation

`causation_id` identifies the event that directly caused this event to be published.

### Correlation

`correlation_id` groups facts belonging to a wider causal or operational chain.

Derived observations should preserve the source correlation when available.

### Schema version

`schema_version` identifies the event-envelope contract version.

It does not replace versioning inside event-specific payloads.

## 5. EventBus

The EventBus owns:

- subscription;
- unsubscription;
- isolated asynchronous dispatch;
- subscriber outcome normalisation;
- runtime tracing;
- bounded in-memory recent traces;
- best-effort handoff of completed dispatches to Event History.

The EventBus owns no:

- gameplay state;
- authority state;
- narrative meaning;
- subscriber behaviour;
- replay semantics;
- state reconstruction.

The EventBus validates the envelope before dispatch.

Each subscriber receives an isolated copy of the event. One subscriber must not mutate the event seen by another.

## 6. Dispatch sequence

```text
Authority persists truth
        ↓
Authority creates event
        ↓
EventBus validates envelope
        ↓
EventBus invokes subscribers independently
        ↓
Subscribers return EventResult outcomes
        ↓
EventBus records bounded runtime trace
        ↓
EventHistory appends completed dispatch evidence
```

Truth must normally be persisted before its fact is published.

If authority persistence fails, publication should be suppressed unless a documented exception exists.

## 7. Subscriber contract

Subscribers:

- react only within their declared responsibility;
- receive an isolated event copy;
- return `EventResult`, a compatible result, or no result;
- may publish a legitimate new fact produced by their own responsibility;
- must preserve causation and correlation for derived facts;
- must not mutate unrelated authority state;
- must not depend upon another subscriber having run;
- must not duplicate EventBus tracing.

Subscribers do not publish “fake events.”

This means they must not announce a source fact that did not become true. It does **not** prohibit an observer or policy system from publishing a new derived fact it legitimately owns.

Subscriber execution order may be operationally deterministic, but architectural correctness must not depend upon subscriber-to-subscriber ordering.

## 8. EventResult

`EventResult` describes the observable outcome of one subscriber reaction.

Typical statuses include:

```text
ok
delivered
matched
suppressed
skipped
no_match
queued
applied
changed
unchanged
failed
```

An EventResult is diagnostic evidence about dispatch behaviour.

It is not automatically a gameplay event, authority mutation or narrative consequence.

## 9. Runtime flight recorder

The EventBus retains a bounded in-memory record of recent completed dispatches.

This runtime flight recorder exists for:

- diagnostics;
- inspection;
- developer observability;
- short-lived runtime queries.

It is:

- memory-only;
- bounded;
- non-authoritative;
- lost on restart.

The runtime flight recorder is not durable history.

## 10. Durable Event History

`EventHistory` preserves completed EventBus dispatches in append-only JSONL.

Canonical production ledger:

```text
data/events/event_history.jsonl
```

Each history record preserves:

- the canonical event envelope;
- subscriber outcomes;
- historical recording time.

Event History owns historical evidence only.

It does not:

- own gameplay state;
- make events authoritative;
- replay events;
- reconstruct runtime state;
- invoke subscribers;
- reinterpret facts;
- assign narrative meaning.

History can be queried without being replayed.

Absence from the ledger is truthful absence unless evidence shows persistence failure.

## 11. Failure semantics

Subscriber failure does not retroactively invalidate a fact already persisted and published.

The EventBus:

- isolates subscriber exceptions;
- records failure in the subscriber trace;
- continues dispatch to remaining subscribers;
- attempts to preserve completed dispatch evidence.

Event History persistence is best-effort relative to live event dispatch. A history write failure must be logged, but it must not cause already completed subscriber behaviour to run again automatically.

## 12. Observation, history and pattern boundaries

The current sealed architectural stack is:

```text
REALITY
    ↓
EVENT
    ↓
OBSERVATION
    ↓
HISTORY
    ↓
PATTERN
```

### Observation

Records what was observed about a source fact.

### History

Preserves completed evidence.

### Pattern

Describes relationships across historical observations, including sequence, direction, recurrence, clustering or change over time.

A pattern must not automatically become:

- relevance;
- interpretation;
- resonance;
- meaning;
- narrative;
- command;
- response.

Those layers remain open architecture beyond Feather 20.

## 13. Current demonstrated topology

### Character movement

```text
Navigation persists current_room
    ↓
character.entered_room
    ├── Probe
    ├── Scenario Engine
    ├── Thread Nodes
    └── Narrator
```

### World Engine

```text
heartbeat.advanced
    ├── Astrology
    ├── Comet Cycle
    └── World Moment boundary

comet.state_changed
    ├── Comet Observation
    ├── Temporal Resolver
    └── Comet Pressure Field

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

These names record current implementation. They do not automatically create new ontology.

## 14. Architectural invariants

- Authorities own truth; events announce facts.
- Event publication follows persistence wherever practical.
- Events are immutable after publication.
- Publishers do not invoke unrelated behaviour.
- Subscribers remain independent.
- Derived events preserve provenance.
- Observers do not overwrite source reality.
- History is evidence, not authority.
- Query is not replay.
- Pattern is not meaning.
- Renderer and presentation systems do not determine gameplay truth.
- Event infrastructure does not become an omniscient orchestrator.

## 15. Deferred capabilities

The following are not established by this version:

- event replay;
- event-sourced state reconstruction;
- automatic recovery from history;
- persistent patterns;
- generic relevance evaluation;
- interpretation engines;
- resonance scoring;
- narrative direction from the EventBus.

Any future replay capability requires a separate contract defining idempotency, authority restoration, subscriber safety and the relationship between historical evidence and current truth.

## 16. Relationship to other documents

| Document | Relationship |
|---|---|
| `TRAJECTORY_v2.1.md` | Constitutional direction: observation and memory precede meaning |
| `ARCHITECTURE.md` | Defines enduring concepts; Event Model does not add ontology |
| `SYSTEM_MAP_v0.3.md` | Defines layers and stewardship; currently awaiting ontology reconciliation |
| `WORLD_ENGINE_ARCHITECTURE.md` | Defines how reality evolves; Event Model mediates cooperation |
| `RUNTIME_AUTHORITY_REGISTER_v0.3.md` | Records which live components own truth or supporting boundaries |
| `DATA_CONTRACTS_v0.4.md` | Defines persistent shape; requires later update for event history and current World Engine stores |

## 17. Version history

### v4

- Event package
- subscriber architecture
- `EventResult`
- structured runtime tracing
- production Event Framework foundation

### v4.1

- reconciled the document against the live runtime through Feather 20;
- added `schema_version` to the canonical envelope;
- distinguished event facts from observation facts;
- distinguished bounded runtime traces from durable Event History;
- established query-without-replay semantics;
- documented failure isolation and history persistence behaviour;
- recognised legitimate derived event publication;
- preserved the boundary from pattern to meaning;
- reconciled “world-driven” with “event-mediated.”

## Closing principle

> **The world owns its truth. Events announce what became true. Observers notice. History remembers. Patterns describe. Meaning remains elsewhere.**
