# Future Sky

# SCENARIO_STATE_CONVENTIONS.md

## Version 0.1

### "Consistent Memory for Living Journeys"

------------------------------------------------------------------------

# Purpose

This document defines the canonical structure of scenario state within
Future Sky.

Scenario state is the memory of a journey.

It is separate from game state, storage, combat state, inventory state
and room state.

------------------------------------------------------------------------

# Design Principles

-   State should describe transformation, not implementation.
-   State names should remain stable over time.
-   Prefer explicit names over abbreviations.
-   The same concept should never have multiple names.

------------------------------------------------------------------------

# Canonical Scenario Instance

``` yaml
scenario:
chapter:
status:
step:

started_at_world:
updated_at_world:
completed_at_world:

variables:
flags:
history:
notes:
```

------------------------------------------------------------------------

# Variables

Variables represent quantities.

Examples:

-   orientation
-   fear
-   trust
-   curiosity
-   clues_found
-   meals_eaten
-   rest_cycles
-   agent_attention

Rules:

-   snake_case
-   numeric where practical
-   accumulate gradually
-   avoid booleans

------------------------------------------------------------------------

# Flags

Flags answer yes/no questions.

Examples:

-   met_rat_queen
-   accepted_key
-   customs_scanned
-   faction_joined
-   dream_completed

Rules:

-   positive names
-   no double negatives
-   set once where possible

------------------------------------------------------------------------

# History

History records objective facts.

Examples:

-   scenario.started
-   room.entered
-   combat.won
-   player.scanned
-   item.received

Rules:

-   factual
-   chronological
-   never rewritten

------------------------------------------------------------------------

# Notes

Notes are authored interpretations.

Examples:

-   "Someone expected your arrival."
-   "The market felt strangely familiar."
-   "The encounter left you unsettled."

Rules:

-   narrative tone
-   may differ between scenarios
-   do not duplicate history

------------------------------------------------------------------------

# Chapters

Chapters group scenarios into meaningful phases.

Example:

``` text
Arrival
 ├─ Orientation
 ├─ Suspicion
 ├─ Flight
 └─ Allegiance
```

------------------------------------------------------------------------

# Status Values

Canonical values:

-   inactive
-   active
-   suspended
-   completed
-   failed
-   abandoned

------------------------------------------------------------------------

# Naming Conventions

Use:

-   meals_eaten
-   clues_found
-   trust
-   fear

Avoid:

-   meals
-   mealCount
-   clueCounter
-   playerFear

------------------------------------------------------------------------

# Ownership

  State             Owner
  ----------------- ---------------------
  World time        GameState
  Room occupancy    Presence
  Inventory         Inventory subsystem
  Combat            Combat subsystem
  Scenario memory   ScenarioService

------------------------------------------------------------------------

# Persistence

Scenario state should eventually survive:

-   logout
-   reconnect
-   server restart

The runtime model should not change when persistence is introduced.

------------------------------------------------------------------------

# Final Principle

Scenario state should answer one question:

> "What has this character genuinely become because of what they have
> experienced?"
