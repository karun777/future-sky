# EVENT_MODEL_v4.md

> **Status:** Stable
>
> This document defines the canonical architecture for all Future Sky event-driven systems. Any new gameplay subsystem should conform to this model unless there is a documented architectural exception.

**Future Sky Event Framework**  
**Version:** 4.0  
**Status:** Production Foundation  
**Date:** July 2026

---

# Philosophy

Future Sky is not a collection of commands.

It is a world.

The world advances through **facts**.

When a fact occurs, the world announces it.

Systems listen.

Systems react.

No system should know who else is listening.

---

# The Golden Rule

> **Publish facts. Never invoke behaviour.**

Good:

```python
Character entered room.
```

Bad:

```python
Navigation calls Narrator.
Navigation calls ThreadNodes.
Navigation calls Ambient.
```

Navigation owns movement.

Navigation does **not** own storytelling.

---

# Architecture

```text
                 Navigation
                      │
                      │ publishes
                      ▼
              character.entered_room
                      │
          ┌───────────┼────────────┐
          │           │            │
          ▼           ▼            ▼
     ThreadNodes   Narrator    Ambient
          │           │            │
          └───────────┼────────────┘
                      ▼
                Event Results
                      │
                      ▼
               Event Flight Recorder
```

Subscribers never communicate with one another.

Every subscriber reacts independently to the same event.

---

# Event Envelope

Every published event is immutable.

It represents a historical fact.

```text
Event

event_id
event_type

occurred_at_utc
occurred_at_world_time

source

scope

payload

causation_id
correlation_id
```

---

## Source

Describes who created the event.

Example:

```text
source

system = navigation

actor = character_id
```

---

## Scope

Describes where the event occurred.

Example:

```text
world

era

room

chapter

scenario
```

---

## Payload

Contains event-specific information.

Example:

```text
from_room

to_room

movement_type

direction

sneaking
```

Payload should contain only information required to understand the fact.

---

# EventBus

The EventBus owns only four responsibilities.

```python
publish()

subscribe()

trace()

remember()
```

It owns no gameplay.

It owns no persistence.

It owns no narrative.

It simply distributes facts.

---

# Subscribers

Subscribers are independent world systems.

Example publisher:

```text
Navigation
```

publishes:

```text
character.entered_room
```

Subscribers:

```text
Thread Nodes

Narrator

Ambient

HUD

Music

Combat

Astrology

Achievements

Analytics

Future AI Director
```

No subscriber should ever require another subscriber.

---

# EventResult

Subscribers communicate their outcome using `EventResult`.

Examples:

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

The EventBus owns tracing.

Subscribers simply describe what happened.

Example:

```python
return EventResult.delivered(
    "pod_disorientation_02"
)
```

---

# Flight Recorder

Every published event is traced.

Example:

```text
EVENT_TRACE

evt_a0ee221e

character.entered_room

source=navigation

actor=karunicorn

from=dark_rat_queen_den

to=main_square
```

Subscriber execution:

```text
✓ Probe
    ok

✓ ThreadNodes
    suppressed(active_thread_node)

✓ Narrator
    delivered(pod_disorientation_02)
```

Completion:

```text
complete

subscribers=3

ok=3

errors=0

elapsed=0.377ms
```

The Flight Recorder is the authoritative execution history.

---

# Subscriber Contract

Subscribers should:

- React only to events.
- Return `EventResult`.
- Own their own gameplay.
- Never invoke other subscribers.

Subscribers should **not**:

- Publish fake events.
- Directly manipulate unrelated systems.
- Duplicate EventBus tracing.

---

# Current Production Subscribers

Event:

```text
character.entered_room
```

Subscribers:

```text
Probe

Thread Nodes

Narrator
```

Planned subscribers:

```text
Ambient

Music

Weather

NPC AI

Combat

HUD

Achievements

Analytics

Astrology

World Moments

Timeline Engine

Director AI
```

---

# Design Principles

## Facts Before Reactions

Movement is persisted before the event is published.

Subscribers react only after reality has changed.

---

## Loose Coupling

Adding a subscriber should require only:

```python
subscribe()
```

Nothing else.

Navigation should never need modification because Music now exists.

---

## Deterministic History

Events represent history.

Subscribers represent interpretation.

History never changes.

Interpretation may evolve.

---

## Observability

Every significant event should be observable.

A developer should understand why something happened without adding print statements.

---

## Composability

The same event may drive:

- Gameplay
- Audio
- Visuals
- Achievements
- Analytics
- AI
- Debugging

without modification to the publisher.

---

# Future Direction

The next primitives are expected to be:

### EventContext

Provides execution context to subscribers.

### EventReplay

Allows replaying historical events.

### EventPersistence

Persistent world event log.

### EventAnalytics

Timing, frequency, subscriber statistics.

### EventDirector

High-level orchestration driven entirely through events.

---

# The Future Sky Law

> **Reality publishes facts. Systems observe. Behaviour emerges.**

---

# Version History

## v1

Initial event publication.

## v2

Subscriber architecture.

## v3

Runtime tracing.

## v4

- Event package (`fsbot.events`)
- `EventResult` extracted into its own primitive
- Flight Recorder
- Structured subscriber outcomes
- Production-ready Event Framework

---

# Closing Note

The Event Framework is not merely infrastructure.

It is the nervous system of Future Sky.

Commands create facts.

Facts become events.

Events become shared reality.

From that shared reality, independent systems create the living world.
