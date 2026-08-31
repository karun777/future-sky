# WORLD_ENGINE_ARCHITECTURE.md

# Future Sky — World Engine Architecture

**Version:** 0.1 (Pre-Feather 8)

**Status:** Living Architecture

**Purpose:**

Describe the architecture of the living simulation that powers Future Sky.

This document is not concerned with gameplay.

It is concerned with reality.

---

# Relationship to ARCHITECTURE.md

The Architectural Ontology defines **what exists**.

This document defines **how reality evolves.**

Ontology answers:

> What kinds of things exist?

World Engine answers:

> How does the universe change?

The two documents should never duplicate one another.

---

# Core Philosophy

Future Sky is not event-driven.

It is world-driven.

Players do not create the universe.

They participate within it.

The world exists before players.

The world continues after players.

The simulation is the primary reality.

Everything else is an interpretation of that reality.

---

# First Principles

The World Engine is governed by several permanent laws.

These should be considered architectural invariants.

## One Heartbeat

There exists exactly one canonical heartbeat.

Every subsystem observes this heartbeat.

No subsystem owns its own clock.

No subsystem advances time independently.

```text
Heartbeat
    ↓
Everything else
```

## One World Time

Only one authority advances canonical world time.

No other authority may directly modify it.

All temporal behaviour ultimately derives from this single progression.

## Immutable Facts

Authorities never publish commands.

Authorities publish observations.

Examples:

- heartbeat.advanced
- astrology.snapshot_changed
- comet.state_changed

These are historical facts.

They describe what became true.

They do not instruct another authority what to do.

## Independent Authorities

Every authority follows the same lifecycle.

```text
Observe
    ↓
Evaluate
    ↓
Persist
    ↓
Publish
```

---

# Authority Ownership

## Heartbeat

Owns:
- heartbeat cadence

Publishes:
- heartbeat.tick

Consumes:
- none

Purpose:
Provide the universal rhythm of the simulation.

## World Clock

Owns:
- canonical world time

Publishes:
- heartbeat.advanced

Consumes:
- heartbeat.tick
- temporal multiplier

Purpose:
Advance world time and nothing more.

## Astrological Authority

Owns:
- astronomical snapshot

Publishes:
- astrology.snapshot_changed

Consumes:
- heartbeat.advanced

Purpose:
Describe the state of the sky.

## Comet Authority

Owns:
- comet cycle
- phase
- pressure
- temporal influence

Publishes:
- comet.state_changed

Consumes:
- heartbeat.advanced

Purpose:
Describe the authored celestial cycle.

## Temporal Policy Authority

Owns:
- effective temporal multiplier

Publishes:
- temporal.policy_changed

Consumes:
- era policy
- comet state
- future temporal influences

Purpose:
Resolve all temporal influences into one canonical multiplier.

The World Clock consumes the result.

---

# Layers of Reality

## Layer One — Reality

Determines what is objectively true.

Examples:

- Heartbeat
- World Clock
- Astrology
- Comet
- Era

## Layer Two — Policy

Interprets reality without replacing it.

Examples:

- Temporal Policy
- Portal Policy
- Mana Policy
- Climate Policy
- Reality Stability

## Layer Three — Expression

Communicates reality.

Examples:

- World Moments
- Ambient systems
- Broadcasts
- Music transitions
- NPC observations

---

# Event Topology

```text
Heartbeat
    ↓
Reality Authorities
    ↓
Policy Authorities
    ↓
Expression Systems
    ↓
Scenarios
    ↓
Players
    ↓
Renderers
```

Information should almost always flow in this direction.

---

# Persistence

Every authority owns its own canonical state.

No authority should persist another authority's responsibility.

Persistence remains decentralised.

---

# Future Direction

```text
Heartbeat
    ↓
Reality Authorities
    ↓
Policy Authorities
    ↓
Expression Systems
    ↓
Resonance
    ↓
Temporal Cohorts
    ↓
Scenario Engine
    ↓
Players
    ↓
Renderer
```

---

# Architectural Test

Before introducing a new authority, ask:

1. What single truth does it own?
2. Could an existing authority own this instead?
3. Does it publish facts rather than commands?
4. Can it function independently?
5. Would the universe continue if it temporarily disappeared?

---

# Closing Principle

Future Sky is not built from gameplay systems.

Gameplay emerges from cosmological systems.

The purpose of the World Engine is to maintain a living universe whose behaviour remains coherent regardless of observation.

> *"The universe does not tell stories. Stories are what consciousness experiences while travelling through the universe."*
