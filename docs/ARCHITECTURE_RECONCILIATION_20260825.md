# Future Sky — Architecture Reconciliation
**Date:** 2026-08-25  
**Status:** Working Architecture Checkpoint — Non-Canonical  
**Purpose:** Reconcile the current runtime through Feather 16 against the existing Future Sky architecture, trajectory, event model, synchronicity model, and related design documents.

---

## 1. Why This Document Exists

Future Sky development has reached a useful architectural plateau.

Feathers 10–16 established a working autonomous world pipeline, but several existing documents use overlapping language at different abstraction levels. This checkpoint records what appears stable, what is provisional, and what should be reconciled before the next development trunk is extended.

This document does **not** replace canonical architecture.

It exists to prevent temporary implementation vocabulary from silently becoming ontology.

---

## 2. Stable Architectural Centre

Across the strongest current documents, the following structure remains coherent:

```text
CONSTITUTION
Natural Laws / LAWS / Pramá / Trajectory
        ↓
ONTOLOGY
World / Chapter / Scenario / Institution / Role /
Character / Driver / Action / Thread Node / World Moment
        ↓
AUTHORITIES
Each owns one category of truth
        ↓
EVENT FRAMEWORK
Completed facts are published
        ↓
OBSERVATION / MEMORY / INTERPRETATION
        ↓
EMERGENT WORLD BEHAVIOUR
        ↓
PERCEPTION / EXPRESSION / RENDERER
```

The strongest shared principles are:

- coherence before complexity
- emergence before prescription
- observation before intervention
- memory before meaning
- one authority per category of truth
- facts before reactions
- human participation preferred but never required
- continuity without dependence on player presence
- presentation must not determine meaning

---

## 3. Event Framework Reconciliation

The Event Framework remains foundational infrastructure rather than ontology.

Its architectural law remains:

> Reality publishes facts. Systems observe. Behaviour emerges.

The runtime work through Feather 16 is strongly aligned with this principle.

The current causal chain is event-driven:

```text
heartbeat.advanced
    ↓
world_moment.eligible
    ↓
world_moment.context
    ↓
world_opportunity.eligible
    ↓
world_opportunity.awakened
    ↓
world_opportunity.instantiated
    ↓
world_opportunity.expired
```

Each stage publishes a new fact rather than directly invoking downstream gameplay.

This is healthy.

---

## 4. Feather 10–16 Reconciliation

Feathers 10–16 should currently be understood as a **vertical proof slice**, not as new ontology.

### Feather 10 — Temporal Observation Boundary

Current event:

```text
world_moment.eligible
```

Actual architectural meaning:

> A deterministic world-time boundary has been crossed and systems may observe the world.

This is **not yet a canonical World Moment**.

---

### Feather 11 — World Context Snapshot

Current event:

```text
world_moment.context
```

Actual architectural meaning:

> Authoritative world conditions were captured at the temporal observation boundary.

Current context includes:

- era
- comet state
- temporal state
- astrology

It does not interpret those facts.

---

### Feather 12 — Authored Condition Matching

Current event:

```text
world_opportunity.eligible
```

Actual architectural meaning:

> An authored possibility matches the current world conditions.

The matcher owns relevance only.

It does not awaken or instantiate anything.

---

### Feather 13 — Awakening Policy

Current event:

```text
world_opportunity.awakened
```

Actual architectural meaning:

> A matching possibility is permitted to proceed.

The gate owns the eligibility → awakening decision.

---

### Feather 14 — Persistent Runtime Instance

Current event:

```text
world_opportunity.instantiated
```

Actual architectural meaning:

> A temporary bounded world situation has gained durable runtime existence.

This is increasingly similar to **Scenario substrate** rather than evidence for a new fundamental concept named Opportunity.

---

### Feather 15 — Lifecycle

Current event:

```text
world_opportunity.expired
```

The runtime authority now owns:

- instance identity
- active/expired status
- awakening time
- expiry time
- lifecycle history

This successfully proved that an autonomous world situation can continue and resolve without human presence.

---

### Feather 16 — Single Active Suppression

Current gate policy:

```text
single_active
```

The matcher may continue to report that conditions match.

The gate suppresses awakening while an active instance of the same authored possibility already exists.

This preserves the authority split:

```text
Matcher  → relevance
Gate     → permission
Runtime  → existence
Lifecycle→ transition
```

---

## 5. The Main Terminology Collision: Moment

The document set currently carries at least three meanings of the word **Moment**.

### A. World Moment as Expression

In ARCHITECTURE and related runtime/design documents, a World Moment communicates living simulation.

Examples include:

- weather
- footsteps
- rumours
- broadcasts
- music
- silence
- environmental changes

It answers:

> What is the world expressing?

---

### B. Moment as Emergent Condition

In TRAJECTORY and SYNCHRONICITY_ENGINE, a Moment is a meaningful world condition produced by the convergence of independent observations.

Examples include:

- Gathering Storm
- Festival Spirit
- Quiet Mourning
- Great Curiosity
- Civic Renewal

It sits conceptually upstream of Scenario:

```text
Signals
    ↓
Convergence
    ↓
Moment
    ↓
Scenario
    ↓
Thread Node
```

---

### C. `world_moment.eligible`

The live engine currently uses `world_moment.eligible` for a six-world-hour temporal observation boundary.

This is neither of the above.

### Reconciliation Position

For now:

- treat `world_moment.eligible` as implementation vocabulary only
- do not promote it into canonical ontology
- preserve the distinction between temporal observation boundaries and semantic/emergent Moments
- explicitly reconcile **Moment** versus **World Moment** in the future documentation pass

A likely eventual distinction is:

```text
Moment
    = emergent world condition

World Moment
    = perceptible expression of living simulation
```

This remains provisional until the canonical documents are reconciled.

---

## 6. World Opportunity Is Not Yet Ontology

The term **World Opportunity** currently describes useful implementation machinery.

It should not yet be added to the fundamental ontology.

The current opportunity pipeline may eventually become part of Scenario infrastructure:

```text
matching conditions
    ↓
permission to awaken
    ↓
bounded persistent situation
    ↓
lifecycle
```

This resembles the canonical Scenario definition:

> A bounded living situation.

Therefore:

> Do not build a permanent `World → Opportunity → Scenario` hierarchy unless a genuinely unique architectural responsibility for Opportunity emerges.

---

## 7. Synchronicity and Event Architecture

The Synchronicity Engine and Event Framework are complementary rather than competing systems.

The likely relationship is:

```text
WORLD AUTHORITIES
Clock / Comet / Astrology / Characters / NPCs /
Institutions / Factions / Environment / Cube
        ↓
completed FACTS
        ↓
EVENT FRAMEWORK
        ↓
independent OBSERVERS
        ↓
OBSERVATIONS / SIGNALS
        ↓
MEMORY
        ↓
CONVERGENCE
        ↓
emergent MOMENT
        ↓
SCENARIO
        ↓
THREAD NODE
        ↓
CONSEQUENCE / EXPRESSION
```

The Event Framework answers:

> How does reality announce completed facts?

The Synchronicity Engine answers:

> How can independent observations become coherent enough for meaning to emerge?

The ontology answers:

> What kinds of enduring concepts may exist?

The constitutional documents answer:

> Why should the system behave this way?

---

## 8. Memory Is Probably the Missing Trunk

TRAJECTORY provides two important spines:

```text
Presence
    ↓
Memory
    ↓
Meaning
    ↓
Relationship
    ↓
Coordination
    ↓
Civilization
```

and:

```text
Observe
    ↓
Remember
    ↓
Interpret
    ↓
Relate
    ↓
Coordinate
    ↓
Build
    ↓
Steward
```

This suggests that a future Synchronicity implementation should not jump directly from instantaneous signals to convergence.

A stronger model is:

```text
Facts
    ↓
Persistent Event History
    ↓
Observations / Signals
    ↓
Temporal Memory
    ↓
Convergence
    ↓
Meaning / Moment
```

This also aligns with the Event Model's future primitives:

- EventContext
- EventReplay
- EventPersistence
- EventAnalytics
- EventDirector

---

## 9. Drift Findings

### 9.1 Terminology Drift

`world_moment.eligible` currently sounds more ontologically significant than it is.

It is a temporal observation boundary.

### 9.2 Document Drift

Moment and World Moment carry different meanings across otherwise authoritative documents.

This must be reconciled in the next documentation run.

### 9.3 Authority Coupling Risk

Feather 16's gate currently reads:

```text
data/world_opportunities/runtime_state.json
```

directly.

This was acceptable for the proof.

However, it creates a possible future coupling pattern in which one authority depends on another authority's persistence representation.

Longer-term, shared world truth should be exposed through a stable fact/query contract rather than knowledge of another authority's file format.

No immediate refactor is required.

### 9.4 State Documentation Staleness

At least the following documents cannot currently be treated as live runtime truth without reconciliation:

```text
DEV_STATE_v6.0.md
WORLD_ENGINE_ARCHITECTURE.md
```

WORLD_ENGINE_ARCHITECTURE explicitly identifies itself as pre-Feather 8.

The live engine is now through Feather 16.

---

## 10. What Feathers 10–16 Proved

The experiment demonstrated that Future Sky can autonomously:

```text
continue
    ↓
notice time
    ↓
inspect its own state
    ↓
recognise authored possibility
    ↓
decide whether awakening is permitted
    ↓
create persistent bounded world state
    ↓
age that state
    ↓
expire it
    ↓
prevent duplicate concurrent instances
```

No player needs to be online.

That directly supports the constitutional principle:

> Human participation is preferred but never required.

The world is becoming capable of continuing while nobody is watching.

---

## 11. Current Architectural Position

The current engine is not yet a Synchronicity Engine.

It now possesses several prerequisites for one:

- persistent world time
- era-specific temporal grammar
- independent world authorities
- immutable event facts
- causation/correlation lineage
- astrology observer
- comet cycle authority
- temporal resolver
- pressure fields
- periodic observation boundaries
- context capture
- authored condition matching
- persistent bounded situations
- lifecycle processing

What is still missing is the deeper sequence:

```text
independent observations
    ↓
remembered observations
    ↓
convergence
    ↓
emergent meaning
```

---

## 12. Candidate Next Development Trunk

Do **not** automatically continue the World Opportunity pipeline.

Before defining Feather 17, investigate the architectural substrate for:

> Observation → Memory → Convergence

The strongest candidate is some form of remembered event/observation layer.

Possible future primitives to investigate include:

```text
EventPersistence
Observation Fact
Signal
Signal Memory
Convergence
```

No name is yet approved.

The next feather should be chosen only after determining which of these responsibilities already belongs to an existing concept.

---

## 13. Documentation Work Still Required

A future document-reconciliation run should:

1. identify authoritative versus historical documents
2. reconcile Moment / World Moment terminology
3. update runtime-state documentation beyond Feather 16
4. reconcile SYSTEM_MAP, WORLD_ENGINE_ARCHITECTURE and RUNTIME_AUTHORITY_REGISTER
5. determine whether Synchronicity Engine remains a separate architecture document or becomes part of the canonical ontology
6. preserve the distinction between constitution, ontology, implementation, operations and historical state
7. build a Knowledge Atlas only after those authority relationships are understood

Do not repeat the earlier mistake of reorganising, rewriting, classifying and reconciling simultaneously.

---

## 14. Working Guardrails

Until the canonical documentation pass is complete:

- Feathers 10–16 are considered valid experimental architecture.
- `world_opportunity` remains provisional implementation language.
- `world_moment.eligible` is treated as a temporal boundary fact.
- no new ontology primitive should be introduced casually.
- no new downstream opportunity-system feather should be assumed.
- EventBus remains infrastructure only.
- authorities continue to own one category of truth.
- observation should precede intervention.
- memory should precede meaning.
- autonomous world continuity remains a core requirement.

---

## Closing

The current development trajectory remains coherent.

The risk is not that Feathers 10–16 were misguided.

The risk is allowing the vocabulary of a successful proof to become permanent architecture before it has been reconciled with the deeper system.

Future Sky now has enough autonomous machinery to begin asking a more important question:

> Not merely what can happen while nobody is watching —

> but what can the world remember well enough to discover meaning?
