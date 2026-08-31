# SCENARIO_ENGINE.md

# Future Sky — Scenario Engine

**Version:** 0.1.0  
**Status:** Canonical Design Draft  
**Last Updated:** 2026-07-13

---

# 1. Purpose

The Scenario Engine defines how **bounded pieces of living simulation** are orchestrated within the wider Future Sky world.

A Scenario is **not**:

- a quest
- a mission
- a cutscene
- a script
- a Thread Node

A Scenario is a temporary state of heightened coherence where multiple actors, roles, objectives and pressures interact toward one or more possible resolutions.

The Scenario Engine coordinates those interactions.

---

# 2. Architectural Position

Future Sky now distinguishes between persistent world systems and bounded simulations.

```
Chapter
    ↓
Scenario
    ↓
Roles
    ↓
Thread Nodes
    ↓
Action Resolution Pipeline
    ↓
World Moments
    ↓
Renderer
```

Each layer owns a different concern.

---

# 3. Relationship to Existing Systems

## Chapter

A Chapter represents a broad stage of a character's journey.

Examples:

- Arrival
- Orientation
- Affiliation
- Stewardship
- Civilization

Chapters provide developmental context.

They are intentionally long-lived.

---

## Scenario

A Scenario is a bounded living situation.

Examples:

- Escape from the Pod
- Festival Preparation
- Missing Child
- Comet Evacuation
- Election
- Dragon Flight
- Scotland Yard-style Pursuit

Scenarios are temporary.

Multiple scenarios may occur during a Chapter.

---

## Thread Nodes

Thread Nodes remain the primary unit of explicit player interaction.

Thread Nodes are **not replaced** by Scenarios.

Instead:

Scenarios create the conditions under which Thread Nodes become available.

Example:

```
Scenario

↓

Security Agent enters room

↓

Thread Node

"Security Interrogation"

↓

Player choices

↓

Scenario updated
```

Thread Nodes remain responsible for:

- dialogue
- branching choices
- immediate consequences
- narrative entanglement

---

## World Moments

World Moments communicate Scenario state to the world.

Examples:

- distant footsteps
- security announcement
- flickering lights
- rumours
- feathers
- Feed7 broadcasts

Scenarios generate pressure.

World Moments express it.

---

# 4. Responsibilities

The Scenario Engine owns:

- active roles
- cycle progression
- objectives
- actor knowledge
- world pressure
- scenario state
- transition conditions

It does **not** own:

- renderer
- dialogue
- room descriptions
- combat mechanics
- Thread Node content
- persistence implementation

---

# 5. Core Principles

## Living Simulation

A Scenario continues to exist regardless of whether players are currently observing every part of it.

The world does not pause.

---

## Multiple Valid Outcomes

Scenarios do not have one correct ending.

Every meaningful outcome transitions into another living state.

Failure creates a different future.

It does not erase participation.

---

## Information Asymmetry

Different actors possess different knowledge.

No participant is guaranteed complete information.

Knowledge itself becomes part of gameplay.

---

## Human Preference

Whenever possible:

Roles should be inhabited by human players.

NPCs exist primarily to preserve continuity.

---

# 6. Roles

A Scenario consists of Roles.

A Role is a responsibility within a living system.

Examples:

- Target
- Security Agent
- Mayor
- Dispatcher
- Dragon Heart
- Rat
- Archivist
- DJ
- Observer

Roles persist independently of their current Driver.

---

# 7. Drivers

Every Role has a Driver.

Driver types include:

- Human
- AI
- Script
- Narrative
- Dormant

Changing Driver does not change the Role.

Only how decisions are produced.

---

# 8. Dynamic Casting

Roles prefer human participation.

When no suitable player is available:

```
Human unavailable

↓

NPC Driver assumes Role

↓

World continues

↓

Human returns

↓

Role transferred back
```

Future Sky therefore scales naturally between:

- solo play
- small communities
- large persistent worlds

without changing its architecture.

---

# 9. Composite Entities

Some entities are composed of many Roles.

Examples include:

- Golden Dragon
- Triton Central
- Feed7
- The Archive
- Government
- Expedition
- Spaceship

Example:

```
Golden Dragon

Root
Sacral
Solar Plexus
Heart
Throat
Third Eye
Crown
```

Each centre may have an independent Driver.

If one becomes vacant, an NPC Driver may temporarily maintain coherence.

---

# 10. Scenario Cycles

Scenarios advance through Cycles.

Cycles represent meaningful progression within the Scenario rather than real-world time.

Each Cycle may:

- advance objectives
- update actor knowledge
- move Roles
- emit World Moments
- trigger Thread Nodes

Cycle progression should respect Future Sky's real-life philosophy.

Urgency exists within the simulation.

Real life remains primary.

---

# 11. Knowledge Model

Every Role maintains its own understanding of the Scenario.

Knowledge may include:

- confirmed facts
- suspicions
- rumours
- misinformation
- forgotten information

The Scenario Engine never assumes perfect information.

---

# 12. Example

## Arrival Chapter

### Scenario

Escape from the Pod

Roles:

- Target
- Archive Agent
- Security Agent
- Queen's Observer
- Transit Operator
- Dispatcher

Objective:

Reach a Safe Room before the Scenario resolves.

Possible outcomes:

- Safe Arrival
- Captured
- Protected
- Misdirected
- Betrayed
- Lost

Each outcome transitions into a different Scenario.

None are considered "Game Over."

---

# 13. Design Philosophy

Future Sky does not primarily simulate combat.

It simulates **living situations**.

Scenarios provide the temporary structures through which:

- cooperation
- pursuit
- ritual
- governance
- investigation
- survival
- celebration
- civilization

can naturally emerge.

---

# 14. Closing Principle

Rooms define places.

Thread Nodes define moments.

Scenarios define situations.

Roles define responsibilities.

Drivers define participation.

Together they create living worlds capable of continuing with or without any individual consciousness while always preferring genuine human participation whenever possible.

---

**End of SCENARIO_ENGINE.md**