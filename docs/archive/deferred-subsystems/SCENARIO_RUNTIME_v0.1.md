# Future Sky

# SCENARIO_RUNTIME.md

## Version 0.1

### "How Living Journeys Execute"

------------------------------------------------------------------------

# Purpose

This document defines the runtime behaviour of the Scenario Engine.

It does not describe story design (SCENARIO_AUTHORING.md), event
definitions (EVENT_CATALOGUE.md), or memory conventions
(SCENARIO_STATE_CONVENTIONS.md).

It describes how scenarios live inside the running world.

------------------------------------------------------------------------

# Core Responsibilities

ScenarioService is responsible for:

-   starting scenarios
-   tracking active journeys
-   remembering scenario state
-   listening for world events
-   evaluating progress
-   advancing scenarios
-   completing or suspending scenarios

It is **not** responsible for movement, combat, inventory, dialogue,
persistence or rendering.

------------------------------------------------------------------------

# Runtime Flow

``` text
World Subsystem
      │
      ▼
Publishes Event
      │
      ▼
Event Bus
      │
      ▼
ScenarioService
      │
      ├─ Ignore
      ├─ Update State
      ├─ Add History
      ├─ Add Notes
      ├─ Advance
      └─ Complete
```

------------------------------------------------------------------------

# Runtime Loop

For each incoming event:

1.  Receive immutable event.
2.  Find active scenarios for the character.
3.  Determine whether the event is relevant.
4.  Update variables and flags.
5.  Append history.
6.  Add authored notes if appropriate.
7.  Evaluate progression rules.
8.  Emit scenario lifecycle events if state changed.

------------------------------------------------------------------------

# Scenario Lifecycle

``` text
Inactive
    │
    ▼
Started
    │
    ▼
Active
    │
 ┌──┴─────────────┐
 ▼                ▼
Suspended     Completed
 │                │
 ▼                ▼
Active        Archived
```

------------------------------------------------------------------------

# Event Evaluation

Scenario logic should react to **facts**, not commands.

Example:

Event:

``` text
player.scanned
```

Possible runtime effects:

-   agent_attention += 1
-   history += player.scanned
-   note added
-   progression re-evaluated

The publisher never knows these reactions exist.

------------------------------------------------------------------------

# State Mutation

ScenarioService may mutate only its own state:

-   variables
-   flags
-   history
-   notes
-   lifecycle status

It must never directly change:

-   combat
-   inventory
-   room occupancy
-   NPC state

Instead it requests changes through events or dedicated services.

------------------------------------------------------------------------

# Multiple Active Scenarios

Characters may eventually participate in multiple scenarios
simultaneously.

Example:

-   Main Story
-   Personal Quest
-   Ambient Festival
-   Faction Mission

Each scenario evaluates the same incoming event independently.

------------------------------------------------------------------------

# Progression Philosophy

Prefer:

-   accumulated experience
-   repeated behaviour
-   meaningful choices

Avoid:

-   exact room order
-   invisible trigger tiles
-   brittle scripting

------------------------------------------------------------------------

# Suspension

A scenario may pause because:

-   another chapter takes priority
-   player enters a different arc
-   world event interrupts
-   time-gated content

Suspension preserves state.

------------------------------------------------------------------------

# Completion

Completion should:

-   archive the scenario
-   preserve history
-   preserve notes
-   emit scenario.completed

Completion should not erase memory.

------------------------------------------------------------------------

# Runtime Authority

  Responsibility    Owner
  ----------------- -----------------
  World state       GameState
  Presence          Presence
  Events            EventBus
  Scenario memory   ScenarioService
  Persistence       Storage

------------------------------------------------------------------------

# Future Evolution

The runtime should eventually support:

-   branching scenarios
-   concurrent chapters
-   dynamic NPC participation
-   faction-aware progression
-   cooperative scenarios
-   AI-authored encounters
-   save/resume
-   simulation replay

None of these should require changing the core runtime model.

------------------------------------------------------------------------

# Final Principle

The Scenario Engine should never ask:

> "What room is the player standing in?"

Its primary question is:

> **"Given everything that has happened, who is this character
> becoming?"**
