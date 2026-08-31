# Future Sky

# SCENARIO_AUTHORING.md

## Version 0.1

### "Authoring Living Journeys"

------------------------------------------------------------------------

# Purpose

A Future Sky scenario is **not** a quest.

It is a structured sequence of experiences that gently transforms a
character.

The Scenario Engine listens to the living world, remembers what has
happened, and advances when meaningful transformation has occurred.

Scenarios should therefore be authored in terms of:

-   experiences
-   discoveries
-   relationships
-   choices
-   consequences

rather than linear room sequences.

------------------------------------------------------------------------

# Design Philosophy

## Traditional RPG

-   Go here.
-   Kill this.
-   Collect that.
-   Return.

## Future Sky

-   Become curious.
-   Develop trust.
-   Notice a pattern.
-   Feel uncertain.
-   Make a meaningful choice.

Movement is only one catalyst. The player should feel free. The world
quietly remembers.

------------------------------------------------------------------------

# Hierarchy

``` text
Story Arc
    ↓
Chapter
    ↓
Scenario
    ↓
Encounter
    ↓
World Events
```

------------------------------------------------------------------------

# Authoring Principle

Never ask:

> What should the player do?

Instead ask:

> **Who should the player become?**

------------------------------------------------------------------------

# Scenario Template

## Purpose

Describe why this scenario exists.

## Player Transformation

Describe who the player should become.

## Free Play

-   Unlimited
-   Limited
-   None

## World Events Listened For

-   character.entered_room
-   combat.started
-   combat.ended
-   npc.conversation.completed
-   rest.completed
-   item.picked_up
-   player.scanned
-   dream.completed

## Variables

Examples:

-   orientation
-   fear
-   trust
-   curiosity
-   clues_found
-   times_eaten
-   times_slept
-   agent_attention

## Flags

Examples:

-   met_rat_queen
-   accepted_key
-   noticed_agent
-   received_uniform
-   joined_faction

## History

Objective facts only.

## Notes

Narrative interpretation only.

History provides evidence.

Notes provide memory.

## Progress Conditions

Prefer transformation-based progression over room-based progression.

## Failure

Failure should create stories, not simply end them.

## Completion

Describe what the player has become.

------------------------------------------------------------------------

# Authoring Principles

1.  Experiences before objectives.
2.  Transformation before completion.
3.  Choices before rewards.
4.  Consequences before punishment.
5.  Discovery before exposition.
6.  Freedom before scripting.
7.  The world should remember.
8.  Players become people through experience.

------------------------------------------------------------------------

# Scotland Yard Example

Instead of:

-   Go to Room A
-   Fight NPC
-   Receive Key

Author:

-   Become known.
-   Attract surveillance.
-   Notice pursuit.
-   Seek safety.
-   Accept help.
-   Choose whom to trust.

------------------------------------------------------------------------

# Final Principle

**Future Sky is not attempting to simulate events.**

**It is attempting to simulate meaningful change.**

> **Who is the player after this experience that they were not before?**
