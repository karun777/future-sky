# Future Sky Anchor Model v0.1

**Status:** Working research model — not canon  
**Version:** 0.1  
**Date:** 2026-10-07  
**Scope:** Authored givens, continuity constraints, anchor attack and cascading consequence  
**Runtime status:** Not implemented  
**Related research:** `NARRATIVE_CONTEXT_MODEL_v0.1.md`

---

## 1. Purpose

Future Sky needs to support many possible histories without pretending that every imaginable history belongs to the same world.

An **Anchor** is an authored given that holds a field of possible histories in relationship with itself.

An Anchor establishes what remains sufficiently fixed for variation to be meaningful. Characters, institutions and timelines may respond differently to it. Their knowledge of it may be incomplete or false. Its consequences may vary. But the Anchor defines part of the common ground against which those differences can be understood.

Examples may include:

- a comet is coming;
- Triton Central exists within a defined timeline family;
- a past occurrence cannot be undone without breaking continuity;
- an actor is genuinely committed to a particular purpose;
- two distinct characters operate from mirrored potentiality;
- no participant possesses complete evidence.

This model also explores a more dangerous possibility: an actor may attempt to obscure, corrupt, sever, erase or counterfeit an Anchor. The World Engine may eventually need to preserve and process the resulting cascade without inventing arbitrary consequences or declaring what the damage means.

Version 0.1 is an authoring and architectural research document. It authorizes no runtime change.

---

## 2. Foundational proposition

> **Anchors bound possibility. They do not prescribe outcome.**

Future Sky is not an infinite simulation. The author establishes a bounded imaginative field containing people, places, forces, histories, obligations, contradictions and givens.

Within that field:

```text
Anchor
  → establishes what remains given

Pressure
  → describes what the given exerts upon the world

Uncertainty
  → identifies what may develop differently

Participation
  → allows characters and institutions to respond

Event
  → records what actually occurs

History
  → preserves which possibility became real
```

Without Anchors, alternate futures become unrelated arbitrary stories.

With too many Anchors, the future becomes a disguised script.

The model therefore seeks the smallest set of givens capable of sustaining a coherent field of meaningful variation.

---

## 3. Anchor is not a new ontology primitive

Version 0.1 does not declare Anchor to be a new runtime entity or universal ontological kind.

Initially, Anchor should be understood as an authoring relationship between:

- a declared proposition;
- a scope of possible histories;
- an authority or provenance;
- permitted variability;
- and the consequences of contradiction or violation.

An Anchor may refer to existing Future Sky concepts such as a World, Character, Institution, object, historical occurrence, relationship or temporal condition.

The first task is to test whether Anchor is a useful contextual property and relationship. Runtime implementation must not precede that evidence.

---

## 4. Anchors and stable truths

A stable truth says:

> This remains factually true within the situation.

An Anchor says:

> This must remain present for these permutations to belong to the same field of possibility.

Some Anchors are stable truths. Some stable truths are too local or incidental to function as Anchors.

An Anchor has a compositional role: it allows histories to vary while remaining comparable.

For example:

```text
Anchor: A comet is coming.
```

This need not fix:

- its exact arrival time;
- who observes it first;
- whether it is welcomed or feared;
- which institutions claim authority over it;
- what it carries;
- how participants respond;
- what its coming means.

The Anchor holds the field together. The uncertainties make the field alive.

---

## 5. Scope

An Anchor must declare the field within which it is given.

Possible scopes include:

### 5.1 Cosmological

Applies across the Future Sky world or a declared cosmological order.

### 5.2 Timeline-family

Applies to every history treated as a member of a particular family.

### 5.3 Era

Applies throughout Jyotzon, Manzo, Ominicron or another declared temporal grammar.

### 5.4 Regional or institutional

Applies within a place, polity, Institution, culture or durable social structure.

### 5.5 Scenario Field

Applies to the set of possible histories explored by one Scenario Field.

### 5.6 Character or relationship

Applies to a being, Role, commitment, relationship or mirrored potentiality.

### 5.7 Epistemic

Constrains what may be known, proven or completely observed.

### 5.8 Continuity

Establishes a condition whose removal would fracture, sever or reclassify the history itself.

Scope prevents a local authored given from silently becoming a universal law.

---

## 6. Proposed Anchor declaration

The following is an authoring sketch, not a data contract.

```yaml
id: anchor_comet_kirch_returns
statement: Comet Kirch is coming.
anchor_class: temporal
scope:
  type: scenario_family
  id: manzo_kirch_return
authorial_status: working
canon_status: candidate
authority: author
provenance:
  source: Future Sky authored context
invariance:
  fixed:
    - the_return_occurs
  variable:
    - exact_arrival_time
    - first_observer
    - institutional_response
    - experienced_meaning
observability:
  may_be_known_by: []
  may_be_inferred_from:
    - sky_observation
    - inherited_record
violation_semantics:
  type: continuity_question
  unresolved: true
```

A useful declaration may include:

- identity;
- proposition;
- class;
- scope;
- authority and provenance;
- authorial and canon status;
- fixed content;
- permitted variability;
- temporal validity;
- observability;
- dependent Anchors or systems;
- violation semantics;
- restoration conditions;
- unresolved questions.

No field should be required merely because it exists in the model.

---

## 7. Anchor constellations

A major narrative force may carry multiple related Anchors.

A comet need not be represented by one overloaded statement. Its authored givens may form an **Anchor constellation**.

Illustrative only:

```text
Comet Kirch will return
  ├─ its motion belongs to a larger cycle
  ├─ its passage changes the available temporal field
  ├─ it carries or distributes life
  ├─ some prior cultures recorded an earlier passage
  └─ no current participant possesses the complete record
```

Each proposition may have a different scope, authority and vulnerability.

A constellation is a relationship graph, not automatically a hierarchy. Breaking one member does not necessarily invalidate every other member.

This permits precise questions:

- Was the comet itself diverted?
- Was its arrival record erased?
- Was its life-bearing function corrupted?
- Was knowledge of its earlier passage suppressed?
- Was the relationship between the comet and a cycle severed?
- Did nothing change except the story people tell about it?

These are different events and must produce different cascades.

---

## 8. Layers of an Anchor

Before claiming that an Anchor has been broken, Future Sky must distinguish what has actually been affected.

### 8.1 Ontic layer

What is true in world reality.

Example: the comet is physically approaching.

### 8.2 Evidentiary layer

What observations, records and material traces support the truth.

Example: orbital observations, archive fragments and prior passage records.

### 8.3 Epistemic layer

What a Character, Institution or culture knows, believes or can infer.

Example: Triton Central knows the comet exists but misunderstands its cycle.

### 8.4 Relational layer

Which other Anchors, systems, obligations or possibilities depend upon it.

Example: a migration ritual depends on the expected passage.

### 8.5 Authorial layer

What the author has declared fixed for a particular field of possible histories.

Example: every history in this Scenario Field includes the comet's return.

An attacker may destroy evidence without changing reality. They may corrupt public knowledge while the evidence remains intact. They may sever a dependency without erasing either endpoint.

Only a genuine attack upon continuity or world reality should be described as breaking the Anchor itself.

---

## 9. Anchor conditions

Suggested descriptive conditions include:

- **intact** — the Anchor remains operative within its declared scope;
- **stressed** — pressures threaten dependencies or expression without altering the Anchor;
- **obscured** — access to the Anchor or its evidence is restricted;
- **contested** — participants or Institutions dispute the proposition;
- **misrepresented** — a false account of the Anchor circulates;
- **corrupted** — the Anchor, its expression or a declared dependency has been altered in a way that produces inconsistent consequences;
- **severed** — a declared relationship between the Anchor and a dependent structure has been broken;
- **counterfeited** — another proposition is made to function socially or mechanically as though it were the Anchor;
- **erased-from-memory** — knowledge and records have been removed while world reality may remain;
- **breached** — the Anchor's declared invariant no longer holds within its former scope;
- **restored** — a previous relationship or invariant has been re-established;
- **transformed** — the original field no longer applies and a new Anchor declaration is required.

These conditions must not be treated as a universal state machine in v0.1.

Some may coexist. An Anchor may be ontically intact, evidentially obscured, epistemically counterfeited and relationally severed at the same time.

---

## 10. Attack vectors

Vitriol or aligned agents may attempt to attack Anchors through different means.

### 10.1 Obscuration

Prevent participants from perceiving evidence or accessing records.

### 10.2 Corruption

Alter evidence, transmission, expression or dependent processes so the Anchor produces inconsistent appearances.

### 10.3 Erasure

Remove records, witnesses, inherited memory or access paths.

Erasure of memory is not automatically erasure of reality.

### 10.4 Counterfeiting

Install a substitute proposition that Institutions or systems treat as given.

### 10.5 Inversion

Cause a dependent structure to respond to the Anchor in a reversed or hostile manner.

Inversion does not prove the underlying Anchor changed.

### 10.6 Severance

Break a declared dependency, relationship or continuity path.

### 10.7 Displacement

Move the apparent time, place, subject or scope of the Anchor.

### 10.8 Breach

Alter the world condition or continuity invariant itself.

This is the strongest claim and demands a legitimate world authority, explicit evidence and declared consequences.

---

## 11. Cascading consequence

An Anchor cascade is the propagation of a verified change through declared dependencies.

```text
Anchor disturbance
  → verified affected layer
  → declared dependency edge
  → local consequence
  → persisted world change
  → immutable event
  → independent downstream responses
  → historical evidence
```

The cascade must proceed through explicit relationships. It must not jump from a dramatic event to every thematically similar object.

### 11.1 Cascade rules

A future implementation should preserve the following constraints:

1. **No dependency, no automatic cascade.**  
   Tags and narrative similarity do not establish causal connection.

2. **Every step cites its source.**  
   A consequence should identify the disturbed Anchor, the dependency used and the prior event.

3. **Authorities remain narrow.**  
   The Anchor model must not mutate clocks, Institutions, Characters or histories directly.

4. **Persist before publish.**  
   A steward records its own changed truth before announcing it.

5. **Subscribers choose their own response.**  
   An Anchor event is a fact, not a command to manufacture drama.

6. **Failure remains local.**  
   One failed response does not invalidate unrelated consequences.

7. **Possibility remains distinct from actuality.**  
   A possible cascade is not a completed cascade.

8. **Meaning is not a consequence type.**  
   The system may record fracture, loss, contradiction and response. It may not declare what they ultimately mean.

### 11.2 Cascade horizon

Cascades should have bounded reach.

Possible stopping conditions include:

- no further declared dependencies;
- dependency conditions are unmet;
- an isolating boundary contains the effect;
- a steward absorbs or transforms the disturbance;
- evidence becomes insufficient;
- the consequence leaves the current Scenario Field;
- further propagation would require interpretation rather than fact.

A cascade that reaches everything is usually evidence of an undeclared god-system rather than good architecture.

---

## 12. Continuity breach

Some Anchors may be declared continuity Anchors.

If one is genuinely breached, the result need not be a conventional failure. It may indicate:

- timeline fracture;
- branching into a new timeline family;
- incompatible histories coexisting;
- loss of causal reachability;
- discontinuity between memory and world state;
- an entity becoming ungrounded from its own history;
- a Scenario Field no longer describing the world;
- a new World or Chapter boundary.

The system must not decide among these outcomes automatically. Violation semantics belong to the Anchor declaration or to a legitimate authority established later.

Breaking time should therefore be representable without being trivial.

It is not:

```text
anchor.health -= damage
```

It is a change to the conditions under which histories can remain coherent with one another.

---

## 13. Vitriol and Efiishent

The following material is preserved as working narrative context, not resolved canon.

Candidate givens:

- Lord Vitriol possesses a genuine vision of nurturing human destructive potentiality.
- Vitriol intends to break time.
- Vitriol is also bound to the structure he seeks to break.
- Efiishent believes he perceives Vitriol's plan.
- Efiishent's reply is associated with Saturn in Aries.
- Autonomy and automation form a live opposition.
- Freedom and order form a live opposition.
- Vitriol and Efiishent are distinct Characters operating from mirrored potentiality.
- Both are playing Roles within a larger drama.

Explicitly unresolved:

- whether either understands the mirroring;
- whether their opposition is necessary, contingent or cultivated;
- whether Efiishent's resistance reproduces part of Vitriol's method;
- whether Vitriol's destructive role ultimately serves a larger light;
- whether either Character could exchange, refuse or transform their Role;
- what Saturn in Aries ultimately expresses;
- whether the author should ever resolve these questions.

The mirrored potentiality may itself become an Anchor while its meaning remains unresolved.

> **A relationship may be given without its interpretation becoming fixed.**

---

## 14. Knowledge and deception

A Character does not gain knowledge of an Anchor merely because the author declared it.

For each Anchor, the model should preserve:

- who may observe it directly;
- who inherits an account;
- who believes a counterfeit;
- who knows evidence has been altered;
- who suspects an Anchor exists;
- who cannot safely articulate their suspicion;
- who benefits from public misunderstanding;
- which knowledge has been erased or displaced.

Efiishent's suspicion is therefore not equivalent to proof.

Vitriol's ignorance, if retained, is not evidence that the mirrored relationship is false.

Authorial truth, world truth, evidence, belief and speech remain distinct.

---

## 15. Repair and restoration

Repair should not mean resetting the world to a prior save.

Possible forms include:

- recovering suppressed evidence;
- reconnecting a severed dependency;
- preserving contradictory histories without collapsing them;
- establishing a new continuity relation;
- allowing an Institution to remember what individuals forgot;
- accepting irreversible loss while restoring coherence;
- transforming the Anchor's scope;
- founding a new ritual, Role or stewardship around the wound.

Restoration may leave scars, obligations and changed possibilities.

A repaired Anchor need not recreate the history that existed before its disturbance.

---

## 16. Relationship to the current epistemic spine

The current implemented boundary remains:

```text
Reality → Event → Observation → History → Pattern
```

The Anchor Model sits initially within authored context.

It may declare:

- givens;
- scope;
- permitted variability;
- dependency relationships;
- possible violation semantics.

The runtime may currently preserve:

- actual world changes;
- immutable events;
- situated observations;
- completed history;
- neutral patterns.

It does not currently own:

- Anchor authority;
- Anchor breach detection;
- cascade execution;
- relevance;
- resonance;
- interpretation;
- narrative meaning.

An Anchor document cannot override verified runtime reality merely because it was authored first. A runtime accident cannot become constitutional truth merely because it occurred.

Conflict must remain visible.

---

## 17. Possible future technical boundary

If authoring trials justify implementation, the smallest honest technical boundary may involve:

1. a registry of authored Anchor declarations;
2. explicit dependency relationships;
3. narrow status observations rather than one universal health score;
4. events describing verified disturbances;
5. authority-specific consumers applying local consequences;
6. provenance across every cascade step;
7. historical queries capable of reconstructing a cascade;
8. no automatic interpretation or Scenario activation.

This is a research direction only.

Version 0.1 does not select a schema, service, event catalogue or runtime steward.

---

## 18. Validation questions

### Authorial integrity

- Is the Anchor truly necessary to hold the field together?
- Is its fixed statement as narrow as possible?
- Does sufficient uncertainty remain?
- Has authorial convenience been mistaken for inevitability?

### Scope integrity

- Where does the Anchor apply?
- Which histories fall outside its scope?
- Would violation create a new history, or merely change this one?

### Epistemic integrity

- Who knows the Anchor?
- What evidence exists?
- Could evidence be erased while reality remains?
- Is a counterfeit being mistaken for an actual breach?

### Causal integrity

- Are dependent consequences explicitly declared?
- Does each cascade step have a legitimate steward?
- Are correlation, symbolism and thematic similarity being mistaken for causation?

### Temporal integrity

- Does the Anchor persist through time, recur or apply only at one boundary?
- What does breach mean for history?
- Can restoration preserve consequence rather than erase it?

### Architectural integrity

- Is authored context separate from runtime actuality?
- Does the model preserve the current boundary beneath Pattern?
- Can the cascade stop?
- Has meaning remained outside mechanism?

---

## 19. Initial trials

### Trial A — Comet Anchor Constellation

Describe the narrow constellation surrounding one coming comet:

- what is fixed;
- what remains uncertain;
- which evidence exists;
- who knows what;
- which systems or rituals depend upon it;
- what Vitriol could attack without moving the comet itself;
- what would constitute a genuine continuity breach.

### Trial B — Mirrored Potentiality

Test the relationship between Vitriol and Efiishent:

- which propositions are given;
- which remain authorially unresolved;
- how distinct Characters can share mirrored potentiality;
- what each believes;
- what must never become automatic knowledge;
- whether the relationship should remain an Anchor or a candidate interpretation.

### Trial C — Small Cascade

Take one local disturbance:

> The record of the trembling glass is erased.

Trace only declared consequences:

- the glass still trembled;
- the Event may remain in History;
- a character's memory may remain;
- an Institutional record may disappear;
- later corroboration becomes harder;
- the scene's meaning remains undecided.

The trial succeeds if the model distinguishes loss of evidence from alteration of reality.

---

## 20. Open questions

1. Who may author an Anchor?
2. Who may seal one as canonical?
3. Can an Anchor be perspectival, or is that a belief with Anchor-like force?
4. How many Anchors can a Scenario Field sustain before becoming predetermined?
5. Can contradictory Anchors coexist across timeline families?
6. What constitutes sufficient evidence of breach?
7. Can a counterfeit Anchor acquire real institutional consequences?
8. When does accumulated consequence transform the scope rather than break the Anchor?
9. How should restoration preserve scars?
10. Can an Anchor be discovered rather than authored?
11. Are some Anchors only visible retrospectively?
12. What distinguishes a continuity Anchor from a Natural Law?
13. Is mirrored potentiality an authored relationship, an Anchor, or an interpretation?
14. Can Vitriol erase an Anchor, or only force the world into a history where it no longer applies?
15. How much of a cascade should remain explicitly authored?

---

## Closing principle

> **Anchors hold possible histories together. Their disturbance should propagate through declared relationships, not authorial convenience. Their breach may change what history can be—but the system must never pretend that damage explains itself.**
