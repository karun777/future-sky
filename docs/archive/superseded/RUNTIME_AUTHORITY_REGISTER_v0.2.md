# Future Sky

# RUNTIME_AUTHORITY_REGISTER.md

**Version:** 0.2.0\
**Status:** Canonical Draft\
**Purpose:** Define the runtime authorities that steward the Future Sky
universe and describe how they cooperate through the Arrival Scenario as
the first living vertical slice.

------------------------------------------------------------------------

# Architectural Principle

The runtime does not exist to execute features.

It exists to steward a living universe.

Each authority protects one category of truth.

No authority owns another authority's truth.

Events allow independent authorities to cooperate.

Arrival is the first proof that the architecture is alive.

------------------------------------------------------------------------

# Runtime Activation Principle

When an Arrival Scenario begins every registered authority must be in
one of four states:

-   **Active** --- performing authoritative work.
-   **Listening** --- observing events and evaluating relevance.
-   **Available** --- initialised and ready to participate.
-   **Dormant by Design** --- intentionally inactive, with a reserved
    architectural boundary.

Every cog therefore turns, listens, stands ready, or is consciously
still.

------------------------------------------------------------------------

# Runtime Authorities

  -----------------------------------------------------------------------
  Authority                           Owns
  ----------------------------------- -----------------------------------
  Character                           Identity, lifecycle, profile

  Navigation                          Location and movement

  Scenario                            Scenario lifecycle, phases,
                                      objectives

  Thread Nodes                        Entanglements, node progression

  Portal                              Transit, portal lifecycle

  Activity                            Participation and idle state

  Ambient / Rest                      Environmental pacing

  Capabilities                        Character development

  Inventory                           Objects and custody

  Relationships                       Persistent interpersonal state

  Memory                              Durable remembered truth

  Narrator                            Subjective interpretation

  Perception                          Audience and knowledge visibility

  World Moments                       Selection of observable events

  HUD                                 Character telemetry presentation

  Renderer                            Presentation formatting

  Router                              Delivery to interfaces

  Clock                               World time and heartbeat

  Storage                             Durable persistence

  Reset / Rebirth                     Continuity and recovery

  **Civilisation**                    Institutions, factions, social
                                      power, legitimacy, civilisational
                                      transition

  Telemetry                           Operational diagnostics
  -----------------------------------------------------------------------

------------------------------------------------------------------------

# Civilisation Authority (New)

## Purpose

Civilisation Authority stewards collective social reality.

It exists between World Simulation and individual lives.

It answers:

> How is power organised, exercised, resisted and transformed?

## Owns

-   institutions
-   factions
-   governance
-   social power
-   legitimacy
-   exploitation
-   ownership patterns
-   cultural influence
-   civilisational cycle state
-   transition between historical social formations

## Publishes

-   civilisation.phase_changed
-   civilisation.transitioned
-   institution.created
-   institution.collapsed
-   institution.changed
-   faction.influence_changed
-   legitimacy.changed
-   social_pressure.changed

## Subscribes

-   scenario.resolved
-   heartbeat.advanced
-   leadership changes
-   economic events
-   relationship changes
-   major world events

## Does NOT own

-   individual morality
-   character identity
-   character location
-   narrative prose
-   renderer behaviour

------------------------------------------------------------------------

# Institutions

Institutions are persistent civilisational entities.

Examples include:

-   Neptune Lounge
-   Transit Authority
-   Universities
-   Archives
-   Merchant Houses
-   Temples
-   Councils
-   Media Networks

Institutions outlive individuals.

They may survive changes of faction.

They become participants in Scenarios.

------------------------------------------------------------------------

# Factions

Factions are organised collections of beings and institutions pursuing
shared interests.

A faction belongs to Civilisation.

It does not define Civilisation.

------------------------------------------------------------------------

# Arrival Reference Flow

``` text
Character recognised
        ↓
Character Authority
        ↓
Scenario starts
        ↓
Portal transit
        ↓
Navigation places character
        ↓
character.entered_room
        ↓
Thread Node eligibility
        ↓
Narrator
HUD
Ambient
World Moments
Scenario
Activity
Civilisation (listens)
        ↓
Awakening completes
        ↓
Scenario transitions
        ↓
Character joins a living civilisation already in motion
```

Arrival is therefore not simply an introduction to a room.

It is entry into an evolving society.

------------------------------------------------------------------------

# Civilisation Snapshot

Arrival may request a read-only civilisation snapshot.

This snapshot never changes gameplay truth.

It provides context for expression.

Examples:

-   dominant institutions
-   current social tensions
-   public mood
-   notable conflicts
-   major historical developments

Different interfaces may express the same snapshot differently.

------------------------------------------------------------------------

# Reserved Evolution

The runtime now has clear expansion paths for:

-   Social Cycle
-   Institutions
-   Economy
-   Collective memory
-   Cultural transmission
-   Governance
-   AI civic actors
-   Historical simulation

These systems extend Civilisation Authority rather than fragmenting it.

------------------------------------------------------------------------

# Closing Principle

The runtime is no longer only an engine for characters.

It is an engine for worlds.

Worlds become civilisations.

Civilisations shape institutions.

Institutions shape lives.

Lives create moments.

Moments become history.

The runtime preserves the truth at every layer while allowing each
authority to turn in harmony with the others.
