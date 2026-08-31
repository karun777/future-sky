# DATA_CONTRACTS.md
**Future Sky — Canonical Data Contracts**

**Version:** 0.4.0  
**Status:** Canonical  
**Last Updated:** 2026-07-03

---

# 1. Purpose

This document defines the canonical shape, ownership and authority of all persistent data used by Future Sky.

It defines:

- what data may exist
- who owns it
- who may modify it
- what guarantees runtime systems may rely upon

It does **not** define gameplay mechanics, narrative meaning, renderer behaviour or implementation details.

Those belong respectively to:

- Red Book
- LAWS.md
- Runtime Systems (Cogs)
- Console

---

# 2. Architectural Philosophy

Future Sky is contract-first.

The architecture is layered:

```text
Red Book
    ↓
LAWS
    ↓
Data Contracts
    ↓
Storage
    ↓
State
    ↓
Systems
    ↓
Console
    ↓
Discord
```

Each layer depends only on the layer above it.

---

# 3. Core Principles

## Shape before Meaning

Storage guarantees shape.

State guarantees minimum runtime validity.

Systems provide meaning.

Console provides experience.

---

## Storage Agnostic

These contracts describe the data.

JSON is the current persistence implementation.

Future PostgreSQL or other storage backends must satisfy the same contracts.

---

## No Silent Meaning Changes

Systems may:

- extend
- add fields
- add namespaces

Systems must never silently reinterpret existing canonical data.

---

# 4. Ownership Boundaries

## Storage

Owns persistence only.

Responsibilities:

- load
- save
- atomic writes
- shape validation

Must never:

- invent meaning
- migrate semantics
- trigger gameplay

---

## State

Owns runtime continuity.

May guarantee:

- player existence
- world clock
- minimum runtime shape

Must never:

- reinterpret persistence
- author gameplay

---

## Systems

Systems own behaviour.

Examples:

- Combat
- Navigation
- Thread Nodes
- Ambient
- Narrator
- HUD
- Astro
- Cube
- Renderer

---

## Console

Owns presentation only.

It renders:

- PLACE
- SELF
- OTHER
- WORLD
- SIGNAL
- CHOICE
- SYSTEM
- THRESHOLD

Console never decides gameplay.

---

# 5. Runtime Ownership Matrix

| Namespace | Authority | Writable By | Readable By |
|-----------|------------|-------------|-------------|
| characters.stats | Combat | Combat | Everyone |
| characters.pools | Gameplay Systems | Explicit systems | Everyone |
| characters.flags | Gameplay | Gameplay | Everyone |
| extra.status | Runtime | Runtime systems | Everyone |
| extra.thread_nodes | Thread Nodes | Thread Nodes | Everyone |
| extra.astrology | Astro | Astro | Everyone |
| extra.metaphysics | Narrative Metadata | Narrative systems | Everyone |
| rooms | World | World Editors | Everyone |
| world_clock | GameState | GameState | Everyone |
| ambient config | Ambient | Ambient | Everyone |
| renderer metadata | Renderer | Renderer | Console |

---

# 6. Global Invariants

- UTF-8
- Two-space indentation
- IDs are strings unless explicitly stated
- Unknown keys are tolerated
- Unknown keys are non-authoritative
- Runtime may ignore unknown keys
- No subsystem may silently migrate semantic meaning

---

# 7. Canonical Namespaces

## Authoritative

- characters
- rooms
- enemies
- items
- cubes
- lockers
- layers
- world_clock

## Runtime Metadata

- extra.status
- extra.thread_nodes
- extra.astrology
- extra.metaphysics
- extra.samskara

---

# 8. Character Contract

Every character must contain:

- id
- name
- current_room
- stats
- pools
- bag
- equipped
- flags
- extra

The character record represents persistent identity only.

Narrative state belongs inside structured namespaces beneath `extra`.

---

# 9. Rooms Contract

Rooms are runtime instances.

A room may define:

- title
- description
- image
- soundcloud
- exits
- items
- enemies
- tags
- ambient_events
- return_echoes
- era

Rooms define possibility.

They do not execute behaviour.

---

# 10. Enemy Contract

Enemy templates live in enemies.json.

Room instances reference templates and contain mutable state such as HP.

Only mutable encounter state may change during play.

---

# 11. Items Contract

Items define capability.

They do not define behaviour.

Recommended fields include:

- type
- slot
- rarity
- stackable
- damage
- defence

---

# 12. Cube Contract

Cube records define ownership and persistent state.

Cube mechanics remain external.

---

# 13. World Moment Contract

A World Moment is the smallest observable unit of world activity.

Sources may include:

- Ambient
- NPC
- Thread Node
- Signal
- Feed7
- Cube
- Narrator

Renderer selects presentation.

Source selects meaning.

---

# 14. Ambient Contract

Ambient owns:

- pacing
- scheduling
- selection

Ambient does not own:

- rendering
- routing
- channel creation

Configuration belongs to a canonical schema.

Runtime defaults must not diverge from persisted schema.

---

# 15. Renderer Contract

Renderer accepts structured inputs.

Renderer never decides gameplay.

Renderer may present:

- room
- world moment
- HUD
- signal
- threshold
- choice

Presentation remains deterministic.

---

# 16. HUD Contract

HUD represents telemetry only.

Telemetry is presentation.

It is never gameplay authority.

---

# 17. Validation

Canonical stores must validate as well-formed data.

Validation confirms:

- shape
- required keys
- primitive types

Validation does not confirm gameplay correctness.

---

# 18. Contract Evolution

Contracts may:

- expand
- add optional namespaces
- add optional fields

Contracts must not:

- silently reinterpret canonical meaning
- change authority ownership
- invalidate historical saves without explicit migration

---

# 19. Relationship to Other Canonical Documents

| Document | Responsibility |
|-----------|----------------|
| Red Book | Metaphysical canon |
| LAWS.md | Behavioural laws |
| DATA_CONTRACTS.md | Data truth |
| DEV_STATE | Runtime truth |
| DEV_ENVIRONMENT_SETUP | Platform |
| OPERATIONS | Operational procedures |
| TRAJECTORY | Strategic direction |

---

# 20. Closing Principle

Data Contracts define **what may exist**.

LAWS define **why it behaves**.

Systems define **how it behaves**.

The Console defines **how it is experienced**.

The Red Book defines **what it ultimately means**.
