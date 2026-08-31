# ARCHITECTURE.md

# Future Sky — Architectural Ontology

**Version:** 1.0
**Status:** Canonical
**Purpose:** Define the fundamental architectural concepts of Future Sky.

---

# Purpose

Future Sky is constructed from a small number of fundamental concepts.

Every system.

Every mechanic.

Every story.

Every institution.

Every civilization.

Should be expressible through combinations of these concepts.

When a proposed feature appears to require a new architectural primitive, the first question should always be:

> Is this genuinely new?

Or

> Is this an existing concept wearing a different costume?

The goal of this document is not to describe implementation.

It is to minimise conceptual complexity.

---

# Design Principle

Future Sky should possess as few fundamental concepts as possible.

Everything else should emerge through composition.

The architecture should become simpler as the world becomes richer.

---

# The Fundamental Ontology

```
World
    ↓
Chapter
    ↓
Scenario
    ↓
Institution
    ↓
Role
    ↓
Character
    ↓
Driver
    ↓
Action
    ↓
Thread Node
    ↓
World Moment
    ↓
Renderer
```

Each layer exists for a different reason.

Each owns different responsibilities.

---

# World

The World is the persistent simulation.

It exists regardless of whether anyone is observing it.

Owns:

- civilizations
- geography
- timelines
- eras
- institutions

Does not own:

- individual choices

Lifetime:

Permanent.

---

# Chapter

A Chapter is a long-lived developmental context.

It answers:

> Who is this consciousness becoming?

Examples:

- Arrival
- Orientation
- Belonging
- Stewardship

Owns:

- developmental stage
- available Scenarios
- world interpretation

Does not own:

- dialogue
- immediate events

Lifetime:

Long.

---

# Scenario

A Scenario is a bounded living situation.

Examples:

- Escape
- Election
- Festival
- Investigation
- Dragon Flight

A Scenario answers:

> What situation currently surrounds this participant?

Owns:

- active Roles
- objectives
- pressure
- cycle
- transitions
- knowledge state

Does not own:

- dialogue
- room descriptions
- rendering

Lifetime:

Temporary.

---

# Institution

An Institution is a persistent collection of Roles.

Examples:

- Triton Central
- Feed7
- Neptune Lounge
- Government
- The Archive
- Golden Dragon

Institutions remember.

Institutions inherit.

Institutions survive individuals.

Owns:

- culture
- continuity
- succession
- responsibilities

Does not own:

- individual consciousness

Lifetime:

Persistent.

---

# Role

A Role is a responsibility.

Roles exist independently of their current occupant.

Examples:

- Mayor
- Archivist
- Rat
- Dragon Heart
- Security Agent
- DJ

Owns:

- permissions
- obligations
- authority
- responsibilities

Does not own:

- identity
- memory

Lifetime:

Variable.

---

# Character

A Character is the persistent expression of one consciousness.

Characters develop.

Characters remember.

Characters participate.

Owns:

- identity
- memories
- relationships
- inventory
- progression

Does not own:

- institutions
- responsibilities

A Character may inhabit many Roles.

---

# Driver

A Driver produces decisions.

Drivers inhabit Roles.

Possible Drivers:

- Human
- AI
- Script
- Narrative
- Dormant

Changing Driver never changes the Role itself.

Drivers are replaceable.

Roles are persistent.

---

# Action

An Action is an intentional attempt to influence the world.

Examples:

- Move
- Speak
- Hide
- Investigate
- Attack
- Repair
- Vote

Actions produce consequences.

Actions do not produce narrative.

---

# Thread Node

A Thread Node is a moment of explicit agency.

Thread Nodes temporarily increase simulation resolution.

Examples:

- conversations
- dilemmas
- discoveries
- rituals
- interrogations

Thread Nodes answer:

> What decision matters right now?

Owns:

- branching
- choices
- immediate consequences

Does not own:

- world orchestration

---

# World Moment

A World Moment communicates living simulation.

Examples:

- footsteps
- music changes
- weather
- rumours
- feathers
- broadcasts
- silence

World Moments answer:

> What is the world expressing?

They may occur with or without player interaction.

---

# Renderer

The Renderer presents experience.

The Renderer never determines meaning.

Meaning belongs to systems above.

Presentation belongs to the Renderer.

---

# Relationships

```
Characters inhabit Roles.

Roles belong to Institutions.

Institutions participate in Scenarios.

Scenarios occur within Chapters.

Chapters unfold inside the World.
```

This relationship should remain stable regardless of implementation.

---

# Human Participation

Future Sky always prefers genuine human participation.

When humans are unavailable:

Drivers may become:

- AI
- Script
- Dormant

Continuity is preserved.

The world never depends upon population.

---

# Composite Entities

Some entities consist of many coordinated Roles.

Examples:

- Golden Dragon
- Triton Central
- Feed7
- Expedition Teams

Composite Entities are Institutions viewed as living organisms.

---

# Ownership Rules

Every concept owns exactly one responsibility.

Responsibility should never be duplicated.

When two concepts appear to own the same thing:

The architecture should be reconsidered.

---

# Architectural Test

Every new feature should answer:

Which existing concept does this belong to?

If none apply:

Challenge the feature.

New architectural primitives should be extraordinarily rare.

---

# Closing Principle

Future Sky is not built from mechanics.

It is built from relationships between enduring concepts.

As the simulation grows larger, the ontology should become smaller.

Complexity belongs in composition.

Never in the number of fundamental ideas.

---

End of document.