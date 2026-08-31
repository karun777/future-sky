# Future Sky — Architectural Ontology

**Version:** 1.1  
**Status:** Current canonical ontology  
**Reconciled:** 2026-08-31  
**Supersedes:** `ARCHITECTURE.md` v1.0

## Purpose

Future Sky is constructed from a small vocabulary of enduring concepts.

Every system, mechanic, story, institution and civilisation should be expressible through relationships among these concepts. When a feature appears to require a new primitive, the first question remains:

> Is this genuinely new, or an existing concept wearing a different costume?

This document defines conceptual kinds and their relationships. It does not define Python classes, JSON shapes, event names or current implementation coverage.

## Design principle

Future Sky should possess as few fundamental concepts as possible.

Complexity belongs in composition, history and relationship—not in an ever-growing list of primitives.

## Architectural regions

The ontology is not a single descending hierarchy. It is a grammar organised into four related regions:

```text
CONTEXT
World · Chapter

PARTICIPATION
Institution · Role · Character · Driver · Action

EMERGENCE AND AGENCY
Moment · Scenario · Thread Node

EXPRESSION
World Moment · Renderer
```

These regions overlap through relationships. They do not form a ladder of ownership.

## World

The World is the persistent shared reality within which all other concepts participate.

It includes geography, timelines, eras, civilisations and the accumulated consequences of existence.

The World exists regardless of whether a participant is observing it.

It does not own every local choice or responsibility. Those remain with the beings and structures that enact them.

**Lifetime:** enduring.

## Chapter

A Chapter is a long-lived developmental context.

It answers:

> What field of becoming currently frames this part of the journey?

Examples include Arrival, Orientation, Belonging and Stewardship.

A Chapter may shape which Moments, Scenarios and interpretations become possible. It does not script immediate events or dialogue.

**Lifetime:** long.

## Institution

An Institution is a persistent social structure composed through Roles, memory, culture and responsibility.

Examples include Triton Central, Feed7, Neptune Lounge, a government, an archive or the Golden Dragon.

Institutions may remember, inherit and survive individual occupants. They do not own individual consciousness.

An Institution may be experienced as a composite living entity without requiring a separate ontological primitive.

**Lifetime:** persistent.

## Role

A Role is a situated responsibility within a world, Institution, Scenario or relationship.

Examples include Mayor, Archivist, Rat, Dragon Heart, Security Agent and DJ.

A Role may carry permissions, obligations, authority and expected capabilities. It exists independently of its current Driver or Character occupant.

A Role does not own personal identity or memory.

**Lifetime:** variable.

## Character

A Character is the persistent world-expression of a consciousness or being.

Characters develop, remember, relate and participate.

A Character may possess identity, memory, relationships, inventory and progression. It may inhabit many Roles across its history.

A Character does not become identical to any Role it occupies.

**Lifetime:** persistent unless the world explicitly establishes otherwise.

## Driver

A Driver is the current source of decisions for a Role or participating Character.

Possible Drivers include:

- Human
- AI
- Script
- Narrative process
- Dormant continuity

Changing the Driver does not erase the Role, Character or their accumulated history.

Drivers are replaceable. Continuity is not.

## Action

An Action is an intentional attempt by a participant to influence the world.

Examples include moving, speaking, hiding, investigating, attacking, repairing and voting.

Actions may succeed, fail or create unintended consequences.

An Action does not own the narrative account of itself. Reality determines consequences; expression communicates them.

## Moment

A Moment is an emergent condition in which otherwise independent truths become coherently present together.

Moments are not authored directly and are not reducible to a clock boundary.

They arise from the world’s state, history, participants and relationships.

A Moment may become noticeable, relevant or consequential without being forced into a Scenario.

The implemented event named `world_moment.eligible` is a neutral temporal opportunity boundary. It is not, by itself, this ontological Moment.

## Scenario

A Scenario is a bounded living situation that coordinates participants, Roles, pressures and transitions.

Examples include an escape, election, festival, investigation or dragon flight.

A Scenario answers:

> What situation currently surrounds these participants?

It may contain objectives, cycles and knowledge state, but it must not presume the choices participants will make.

A Scenario may arise within a Moment, respond to one, or be authored as a possible structure awaiting suitable conditions.

**Lifetime:** temporary.

## Thread Node

A Thread Node is a local structure of explicit agency.

It temporarily increases simulation resolution around a decision, discovery, conversation, dilemma, ritual or interrogation.

A Thread Node answers:

> What choice or response matters here?

It may own branching, prompts and immediate consequences. It does not orchestrate the whole World or silently become an Item, Scenario or authority.

## World Moment

A World Moment is an expression through which the living world becomes perceptible.

Examples include footsteps, weather, rumours, music changes, feathers, broadcasts, artwork, NPC behaviour and silence.

World Moments may occur with or without player interaction. They communicate life rather than exposition.

A World Moment is not identical to an emergent Moment. It may express one, hint at one or simply reveal ongoing reality.

It is also distinct from the runtime event `world_moment.eligible`, whose name is retained as implementation history until terminology is deliberately revised.

## Renderer

A Renderer presents selected reality through an interface.

Discord, websites, Feed7, a companion application and future interfaces may all render Future Sky differently.

A Renderer may choose form, emphasis and sensory language. It does not own the underlying truth and must never manufacture canonical meaning merely through presentation.

## Core relationships

```text
Worlds contain histories, places and conditions.

Chapters frame development within Worlds.

Characters inhabit Roles.

Drivers provide decisions for participating Characters or Roles.

Roles compose Institutions and Scenarios.

Actions produce consequences within the World.

Moments emerge from coherent conditions.

Scenarios coordinate bounded situations.

Thread Nodes focus explicit agency.

World Moments express living reality.

Renderers present selected expressions.
```

No one of these relationships implies total ownership of the concepts on either side.

## Human participation

Future Sky prefers genuine human participation but never depends upon constant human presence.

When a human is unavailable, another Driver may maintain continuity. This substitution must preserve lineage and should not counterfeit human choice.

## Authorities are stewardship, not ontology

An authority is an implementation pattern: the identifiable steward of one category of runtime truth.

Authorities implement parts of the ontology but are not additional fundamental beings merely because code exists for them.

Likewise, events, observations, history and patterns are epistemic and runtime infrastructure. They describe how truths travel and become knowable; they do not enlarge the fundamental ontology by default.

## Fields are distributed conditions

A field describes a condition distributed across addressable scopes.

A field is not automatically an authority and does not decide outcomes.

The implemented Comet Pressure Field is a concrete example. Proposed fields such as resonance, institutional legitimacy or timeline stability remain proposals until their truth, stewardship and boundaries are established.

Pramá and Love must not be reduced to fields merely because a field is computationally convenient.

## Opportunity is implementation scaffolding

A World Opportunity is an authored and runtime structure used to detect that conditions may permit something to awaken.

It is presently useful implementation vocabulary, not a new fundamental ontological primitive.

Eligibility, awakening and durable instantiation do not automatically create a Moment or activate a Scenario.

## Ownership and integrity rules

- Every implemented category of truth has one identifiable steward.
- Concepts may relate without duplicating stewardship.
- Presentation does not own reality.
- Persistence does not create legitimacy by accident.
- Runtime vocabulary does not silently become ontology.
- Constitutional language does not prove implementation.
- Observation precedes interpretation.
- Pattern does not equal meaning.
- Human choice must not be counterfeited by continuity machinery.

## Architectural test

Every proposed feature should answer:

1. Which existing concept or relationship expresses it?
2. Is it ontology, authored content, runtime authority, infrastructure or presentation?
3. Does it duplicate an existing responsibility?
4. Is a new primitive truly necessary?
5. Does it preserve emergence and future possibility?

New primitives should remain extraordinarily rare.

## Current terminology tension

“Moment” presently appears in three distinct senses:

1. **Moment** — an emergent coherence of conditions;
2. **World Moment** — an expression of living world reality;
3. **`world_moment.eligible`** — an implemented temporal boundary fact.

This document makes the distinction canonical. A later bounded refactor may rename the runtime event, but documentation must not pretend these three meanings are interchangeable.

## Closing principle

Future Sky is built from relationships among enduring concepts.

As the simulation grows richer, the ontology should become clearer and smaller.

The world may accumulate limitless complexity. Its fundamental grammar should not.
