# Future Sky

# EVENT_CATALOGUE.md

## Version 0.1

### "The Language of the Living World"

------------------------------------------------------------------------

# Purpose

The Event Catalogue defines every significant occurrence that can be
emitted by the Future Sky runtime.

Events are immutable facts.

Subsystems publish events.

Other subsystems may listen, react, ignore, or remember.

The publisher never needs to know who is listening.

------------------------------------------------------------------------

# Design Principles

-   Events describe what happened, never what should happen.
-   Event names are written in the past tense.
-   Events are immutable.
-   Events should be deterministic and replayable.

------------------------------------------------------------------------

# Canonical Naming

    domain.action

Examples:

-   character.entered_room
-   combat.started
-   combat.ended
-   item.picked_up
-   rest.completed
-   npc.conversation.completed

------------------------------------------------------------------------

# Standard Event Envelope

``` yaml
event_type:
timestamp_world:
actor_id:
character_id:
scope:
payload:
```

`scope` may later include:

-   scenario_id
-   chapter_id
-   faction_id
-   region_id

------------------------------------------------------------------------

# Event Categories

## Navigation

-   character.entered_room
-   character.left_room
-   character.teleported
-   character.spawned

Payload example:

-   previous_room_id
-   room_id
-   movement_type

------------------------------------------------------------------------

## Combat

-   combat.started
-   combat.round_completed
-   combat.damage_applied
-   combat.ended
-   combat.fled
-   combat.death

------------------------------------------------------------------------

## Inventory

-   item.picked_up
-   item.dropped
-   item.used
-   item.equipped
-   item.given

------------------------------------------------------------------------

## NPC

-   npc.conversation.started
-   npc.conversation.completed
-   npc.relationship_changed

------------------------------------------------------------------------

## Rest

-   rest.started
-   rest.completed
-   dream.started
-   dream.completed

------------------------------------------------------------------------

## Character

-   player.created
-   player.rebirthed
-   player.scanned
-   player.levelled
-   player.died

------------------------------------------------------------------------

## Social

-   faction.joined
-   faction.left
-   trust.changed
-   reputation.changed

------------------------------------------------------------------------

## Scenario

-   scenario.started
-   scenario.advanced
-   scenario.completed
-   scenario.failed
-   scenario.abandoned

------------------------------------------------------------------------

# Authoring Guidance

Authors should think in events rather than rooms.

Instead of:

-   "Player reaches Room 5"

Prefer:

-   player.ate
-   rest.completed
-   npc.conversation.completed
-   player.scanned
-   combat.ended

Scenarios react to accumulated experience.

------------------------------------------------------------------------

# Event Ownership

  System            Publishes
  ----------------- ---------------------
  Navigation        movement events
  Combat            combat events
  Inventory         item events
  Dialogue          conversation events
  Ambient           world events
  Scenario Engine   scenario lifecycle
  ThreadNodes       narrative triggers

------------------------------------------------------------------------

# Future Vision

Eventually every meaningful action in Future Sky should emit an event.

Any subsystem may subscribe.

The Event Catalogue is therefore the shared language spoken by the
entire simulation.
