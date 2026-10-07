# Future Sky Narrative Context Model v0.1

**Status:** Working authoring model - research, not canon  
**Version:** 0.1  
**Date:** 2026-09-02  
**Scope:** Contextualizing authored content for causal, temporal, social, symbolic and narrative relationship  
**Runtime status:** Not implemented  

---

## 1. Purpose

Future Sky requires authored content rich enough to carry the particulars of its world while remaining available to multiple histories.

The project is not attempting an infinite simulation. The author establishes a bounded imaginative context: people, places, institutions, histories, forces, symbols, tensions and possible transformations. Within that context, the World Engine should help preserve sequence, consequence, recurrence and relationship so that different futures can develop without being reduced to prewritten branches.

The Narrative Context Model defines a lightweight contextual envelope for authored material. Its purpose is to let content retain its literary life while also becoming locatable and relational within Future Sky.

The model should help answer:

- What is this content?
- Where and when does it belong?
- Whose experience or account does it represent?
- What conditions produced it?
- What might it enable, obstruct or transform?
- What other content does it echo, contradict, remember or foreshadow?
- Which futures require it, and which futures does it make less likely?
- What must remain unresolved?

The model does not tell the story. It gives stories enough structure to encounter one another.

---

## 2. Foundational proposition

> **The author creates the field of possibility. The system preserves and relates what happens within it.**

Future Sky should not generate arbitrary possibility from nothing. Rich emergence requires authored constraint.

The author provides:

- the world and its historical bounds;
- people and institutions with partial knowledge;
- material and social conditions;
- durable tensions;
- possible transformations;
- questions that must not be answered cheaply.

The runtime may provide:

- temporal sequence;
- immutable events;
- situated observations;
- durable history;
- descriptive recurrence;
- eligibility under declared conditions;
- consequences that persist beyond a scene.

Later systems may explore relevance, resonance, relationship and social development. They must not invent meaning merely because content has been tagged.

---

## 3. Position within Future Sky

The current epistemic spine remains:

```text
Reality -> Event -> Observation -> History -> Pattern
```

The Narrative Context Model does not insert itself as another authority in this sequence. It sits beside the runtime as authored orientation.

```text
Authored context                       Runtime evidence
---------------                        ----------------
People, places, institutions           Reality authorities
Pressures and possible futures         Events
Perspectives and uncertainties         Observations
Typed narrative relationships          History
Scenario fields                        Patterns
                  \                    /
                   future relevance
```

Authored context says what kinds of relationships and transformations the world can support. Runtime evidence says what actually occurred.

Neither should silently overwrite the other.

---

## 4. Governing principles

### 4.1 Writing precedes classification

Content should first be allowed to live as writing. Contextualization follows as a second pass.

The model must not turn every act of imagination into form completion.

### 4.2 Context is inherited where possible

A line of dialogue may inherit context from its Thread Node. A Thread Node may inherit from its Scenario. A Scenario may inherit era, region and chapter context.

Explicit metadata is needed when content crosses, narrows or disputes inherited context.

### 4.3 Relationships matter more than tag accumulation

A tag such as `memory` groups content. A typed statement such as:

```text
fragment_017 contradicts earth_evacuation_account
```

describes a relationship the architecture may later traverse.

Tags remain useful for discovery. They must not substitute for meaningful connections.

### 4.4 Perspective must remain situated

A belief held by a character is not world truth. An institutional account is not automatically canonical. A narrator's framing should not be mistaken for a runtime fact.

Context should preserve who knows, believes, remembers, claims, disputes or cannot perceive something.

### 4.5 Contradiction is first-class

Conflicting accounts should be representable without immediate resolution.

The model must distinguish:

- conflicting observations;
- conflicting interpretations;
- temporal change;
- deliberate deception;
- incomplete evidence;
- genuinely coexisting realities.

### 4.6 Possibility is not actuality

Possible outcomes, backcast prerequisites and narrative affordances are authored possibility. They do not become world facts until the appropriate authorities record actual occurrences.

### 4.7 No hidden meaning scores

Trust, belonging, love, obligation, grief and meaning must not be collapsed into convenient universal numbers merely so the system can compare them.

If quantified mechanics are later introduced, their claims and limitations must be explicit.

### 4.8 Context must remain revisable

The contextual envelope is an authoring aid. It may evolve as the content reveals what the architecture actually needs.

---

## 5. Units of authored content

The model may accompany any significant authored object, including:

- character;
- role;
- institution;
- faction;
- place;
- object;
- memory fragment;
- historical account;
- scenario field;
- Thread Node;
- scene;
- custom;
- law;
- ritual;
- conflict;
- possible future state;
- recurring image or metaphor.

Not every object requires the full model.

### 5.1 Three levels of contextualization

#### Minimal

Suitable for ordinary rooms, items and small encounters.

- identity;
- content type;
- inherited situation;
- a small number of tags;
- any essential relationships.

#### Situated

Suitable for characters, institutions, important objects and Thread Nodes.

- identity;
- situation;
- perspective;
- causal position;
- narrative affordances;
- typed relationships.

#### Deep

Suitable for Scenario Fields, major conflicts, historical events, civilizational changes and recurrent symbols.

- all situated fields;
- Causal Layered Analysis;
- scenario uncertainties;
- possible futures;
- backcast prerequisites;
- indicators;
- explicit unresolved questions.

Authors should use the least depth that preserves what matters.

---

## 6. The contextual envelope

The following sections describe the complete model. They are conceptual fields, not yet a machine-readable contract.

### 6.1 Identity

Identity establishes what the content object is and how it should be treated.

Possible fields:

- `id`
- `title`
- `content_type`
- `version`
- `authorial_status`
- `canon_status`
- `provenance`
- `created_at`
- `updated_at`

Suggested authorial statuses:

- seed;
- exploratory;
- working;
- reviewed;
- sealed;
- superseded.

Suggested canon statuses:

- not_assessed;
- candidate;
- canonical;
- perspectival;
- disputed;
- apocryphal;
- non_canon.

These statuses must not be inferred from file location alone.

### 6.2 Situation

Situation locates the content within the world.

Possible fields:

- era;
- timeline or timeline family;
- chapter;
- region;
- location;
- world-time range;
- social setting;
- participating characters;
- participating institutions;
- material conditions;
- active world pressures;
- relevant runtime authorities.

Situation may contain uncertainty. A memory fragment may have an alleged era rather than a verified one.

### 6.3 Perspective

Perspective records the relationship between an account and its knower.

Possible fields:

- perspective holder;
- perspective type;
- access conditions;
- directly observed facts;
- remembered material;
- beliefs;
- assumptions;
- declared claims;
- uncertainties;
- blind spots;
- withheld knowledge;
- disputed-by relationships;

Suggested perspective types:

- first-hand witness;
- inherited memory;
- institutional account;
- scholarly reconstruction;
- rumour;
- prophecy;
- dream;
- machine observation;
- narrator framing;
- author-only knowledge.

Author-only knowledge must never leak automatically into character or institutional awareness.

### 6.4 Causal position

Causal position describes how the content participates in possible histories.

Possible fields:

- preceding conditions;
- enabling conditions;
- inhibiting conditions;
- pressures;
- drivers;
- triggers;
- possible actions;
- possible consequences;
- dependencies;
- thresholds;
- persistence effects;
- affected authorities;

Causal position should distinguish between:

- necessary conditions;
- contributing conditions;
- sufficient conditions;
- correlated conditions;
- believed causes;
- unknown causes.

The author should not label correlation as causation merely for narrative convenience.

### 6.5 Narrative affordances

Narrative affordances describe what this content makes available without requiring it to happen.

Possible fields:

- mysteries exposed;
- tensions intensified;
- invitations possible;
- relationships affected;
- choices made available;
- refusals made possible;
- Thread Nodes supported;
- Scenario Fields supported;
- possible transformations;
- costs of participation;
- consequences of non-participation;
- questions that must remain unresolved.

An affordance is not a command and not an activation.

### 6.6 Discovery tags

Tags support browsing and broad retrieval.

Useful tag families may include:

- theme: memory, inheritance, exile, continuity;
- domain: infrastructure, governance, ritual, trade;
- tone: intimate, uncanny, comic, elegiac;
- scale: personal, relational, institutional, civilizational;
- element or chakra association;
- class affinity;
- era or place;
- content warning where appropriate.

Tags should be controlled enough to remain useful but open enough for the vocabulary to develop.

Tags describe association. They must not claim causality or interpretation.

---

## 7. Typed relationships

Typed relationships form the connective tissue of the model.

A relationship should normally contain:

- source content ID;
- relationship type;
- target content ID;
- perspective or authority making the relationship;
- confidence or evidentiary status where relevant;
- optional note;
- validity range if the relationship changes over time.

### 7.1 Structural relationships

- `contains`
- `part_of`
- `located_in`
- `belongs_to`
- `holds_role_in`
- `participates_in`
- `governed_by`

### 7.2 Temporal relationships

- `precedes`
- `follows`
- `overlaps`
- `recurs_after`
- `persists_through`
- `originates_in`
- `returns_during`

### 7.3 Causal relationships

- `enables`
- `inhibits`
- `contributes_to`
- `triggers`
- `depends_on`
- `interrupts`
- `transforms`
- `stabilizes`
- `destabilizes`

### 7.4 Evidentiary relationships

- `observes`
- `records`
- `supports`
- `contradicts`
- `disputes`
- `corroborates`
- `misremembers_as`
- `conceals`
- `reveals`
- `is_evidence_for`

### 7.5 Narrative relationships

- `echoes`
- `foreshadows`
- `reframes`
- `inherits_from`
- `mirrors`
- `inverts`
- `resolves`
- `complicates`
- `remains_unresolved_with`

These are authored relationships unless supported by a declared runtime authority.

### 7.6 Social relationships

- `trusts`
- `depends_upon`
- `owes`
- `protects`
- `excludes`
- `represents`
- `claims_authority_over`
- `offers_custodianship_to`
- `inherits_obligation_from`

Social relationships are listed here as future requirements, not as a settled Social Cycle contract. Their durability, evidence and authority remain open research.

### 7.7 Symbolic relationships

- `symbolizes_for`
- `is_ritually_linked_to`
- `embodies_for`
- `is_named_after`
- `appears_in_myth_as`

Symbolic relationships must identify the perspective for whom the symbolism exists. The world must not universalize one culture's metaphor.

---

## 8. Causal Layered Analysis

Causal Layered Analysis, associated with Sohail Inayatullah, is used here as an authoring and inquiry method. It is not a runtime ontology.

### 8.1 Litany

The visible account of what is happening.

Questions:

- What events are being reported?
- What is treated as the immediate problem?
- What headlines, rumours or public anxieties circulate?
- What appears obvious to participants?

### 8.2 Systemic causes

The social, economic, institutional, technological, ecological and material structures shaping the situation.

Questions:

- Who controls resources, infrastructure and access?
- Which rules distribute risk and benefit?
- What historical systems produced the present conditions?
- Which feedback loops maintain the situation?

### 8.3 Worldview and discourse

The assumptions and interpretive frameworks through which participants understand the system.

Questions:

- What counts as knowledge?
- Who is recognized as a legitimate knower?
- What concepts appear natural or inevitable?
- Which alternatives are difficult to articulate?
- How do institutions name the situation differently?

### 8.4 Myth and metaphor

The deep stories, images and emotional structures beneath the worldview.

Questions:

- What kind of world do participants imagine they inhabit?
- Is the city a machine, refuge, inheritance, ancestor, prison or organism?
- What archetypal story makes current behaviour feel right?
- What new metaphor might make another future imaginable?

### 8.5 Multiple CLA accounts

A Scenario Field should be able to hold several layered accounts at once.

For example, the same aperture may be:

- a transport obstruction to the Dockworkers' Continuity Union;
- strategic technology to Earth;
- a civic memory organ to Sera;
- the continuation of a distributed person to Ilex;
- a wound in the city to the Dark Rat Queen.

The model should preserve these accounts rather than resolving them into one CLA analysis.

---

## 9. Scenario planning

Scenario planning explores multiple plausible futures produced by significant uncertainties and persistent forces.

### 9.1 Scenario Field rather than branch tree

A Scenario Field contains:

- stable authored truths;
- actors and institutions;
- material and social pressures;
- critical uncertainties;
- available capacities;
- possible interventions;
- thresholds and consequences;
- possible future states.

It does not need to prescribe a menu of endings.

### 9.2 Critical uncertainties

Critical uncertainties should materially change the kind of world that develops.

Examples:

- Is memory governed as a commons or strategic property?
- Is Triton Central regarded as an object or participant?
- Does Earth provide aid before demanding authority?
- Are contradictory testimonies preserved or reconciled into one account?

### 9.3 Persistent forces

Persistent forces operate across several futures:

- Comet Kirch's return;
- dependence on biodome infrastructure;
- unequal access to translation;
- the political isolation of Triton Central;
- the Cube's capacity to preserve cross-timeline memory.

### 9.4 Indicators

Indicators are observable developments suggesting movement toward a possible future.

They are not proof of destiny.

Examples:

- exclusive archive-access agreements;
- new public memory rituals;
- testimony excluded from official records;
- maintenance workers assuming custodial functions;
- infrastructure responding to particular voices.

### 9.5 Scenario status

Possible future states should be marked distinctly from actual world state.

Suggested statuses:

- imagined;
- plausible;
- enabled;
- emerging;
- dominant;
- dormant;
- foreclosed;
- realized;
- retrospectively_disputed.

The authority for changing these statuses is not defined in v0.1.

---

## 10. Backcasting

Backcasting begins with a possible future condition and asks what must have become true for it to exist.

### 10.1 Backcast structure

For each possible future:

1. Describe the future condition concretely.
2. Identify necessary institutional, relational and material preconditions.
3. Identify preceding events or transformations.
4. Identify capacities participants must possess.
5. Identify decisions, refusals or accidents that could open the path.
6. Identify early indicators.
7. Identify conditions that would close the path.
8. Return to the present and locate possible points of participation.

### 10.2 Backcasting is not predestination

A backcast prerequisite describes what a future would require. It does not cause the runtime to manufacture that prerequisite.

Several futures may share prerequisites. A condition that enables one future may also produce an unintended alternative.

### 10.3 Backcasting and narrative discovery

Backcasting can reveal scenes worth writing:

- the first time contradictory testimony is preserved publicly;
- the refusal of an exclusive-access agreement;
- an ordinary maintenance practice becoming a civic ritual;
- a character choosing not to use power they possess;
- a lost record returning through another timeline.

This moves the writer from abstract destination to causally meaningful encounters.

---

## 11. Inheritance and override

Context should be inherited to reduce authoring burden.

### 11.1 Example hierarchy

```text
World
  Chapter
    Era / Timeline
      Region
        Scenario Field
          Institution / Role
            Character
              Thread Node
                Action / Event
```

This is a contextual inheritance path, not necessarily a persistence hierarchy.

### 11.2 Inherited context

A Thread Node within a Manzo Scenario Field may inherit:

- era: Manzo;
- region: Triton Central;
- active world pressure: Comet Kirch return;
- participating institutions;
- relevant critical uncertainties.

### 11.3 Explicit override

An object should declare context when it:

- crosses timelines;
- occurs outside the parent location;
- represents a disputed account;
- belongs to another perspective;
- has a narrower time range;
- contradicts inherited assumptions;
- must remain isolated from parent knowledge.

### 11.4 No accidental knowledge inheritance

Structural inheritance must not become epistemic inheritance.

A character present within a Scenario Field does not automatically know all Scenario metadata. Knowledge and observation require their own declared relationships or runtime evidence.

---

## 12. Authoring workflow

### Pass 1 - Write

Write the character, place, scene, object, conflict or memory without interruption from the model.

### Pass 2 - Locate

Record only the essential identity and situation.

### Pass 3 - Situate perspective

Identify whose account this is, what they can know and what remains uncertain.

### Pass 4 - Connect

Add the few typed relationships that allow the content to participate in the wider world.

### Pass 5 - Deepen where warranted

For major Scenario Fields or civilizational material, apply CLA, scenario planning and backcasting.

### Pass 6 - Test expression

Ask which parts can already be expressed through:

- rooms;
- characters;
- institutions;
- items;
- Thread Nodes;
- World Opportunities;
- Scenarios;
- immutable events;
- observations and history.

Record architectural gaps. Do not silently force the content into an unsuitable runtime shape.

---

## 13. Illustrative representation

The following JSON is an authoring sketch, not a data contract.

```json
{
  "id": "scn_manzo_choir_beneath_glass",
  "content_type": "scenario_field",
  "authorial_status": "exploratory",
  "canon_status": "candidate",
  "situation": {
    "era": "manzo",
    "region": "triton_central",
    "locations": [
      "neptune_lounge",
      "promenade_freight_underpass",
      "outer_shell"
    ],
    "world_pressures": [
      "comet_kirch_return",
      "seven_tone_glass_hum"
    ]
  },
  "stable_truths": [
    "glass_hum_predates_human_settlement",
    "aperture_contact_can_produce_borrowed_memory",
    "no_participant_possesses_complete_evidence"
  ],
  "critical_uncertainties": [
    "memory_commons_or_strategic_property",
    "city_object_or_participant"
  ],
  "relationships": [
    {
      "source": "memory_fragment_017",
      "type": "contradicts",
      "target": "earth_evacuation_account",
      "perspective": "sera_venn",
      "status": "working_assessment"
    }
  ],
  "unresolved_questions": [
    "did_the_original_inhabitants_leave",
    "is_ilex_continuing_through_the_city"
  ]
}
```

The example deliberately separates stable truths from unresolved questions and perspectival relationships.

---

## 14. Runtime boundaries

Version 0.1 authorizes no runtime changes.

### 14.1 What current runtime components may honestly do

- match authored World Opportunities against declared era and comet-pressure requirements;
- start a Scenario deliberately;
- retain factual Scenario variables, flags, history and notes;
- publish immutable events;
- preserve observations and Event History;
- describe historical recurrence through Pattern queries.

### 14.2 What the runtime must not yet do

- infer a story's meaning;
- decide which worldview is correct;
- select a canonical future;
- convert CLA layers into universal truth;
- infer relationships merely because tags overlap;
- activate a Scenario because it appears narratively interesting;
- assign relevance without a declared relevance boundary;
- calculate resonance, love, belonging or moral value;
- treat possible futures as actual state;
- grant characters knowledge from author-only context.

### 14.3 Possible future technical forms

The model may eventually inform:

- authored context documents;
- a content identity registry;
- typed relationship records;
- controlled vocabularies;
- context-aware authoring tools;
- graph traversal for research and discovery;
- relevance queries that cite their evidence;
- Scenario and Thread Node authoring support.

No technical form is selected in v0.1.

---

## 15. Validation questions

A contextualized piece of content should be reviewable with the following questions.

### Literary integrity

- Does the content still work as writing?
- Has classification flattened ambiguity or voice?
- Is the content interesting without reading its metadata?

### Contextual integrity

- Can we locate it in era, place and situation?
- Is perspective distinguished from world truth?
- Are important uncertainties preserved?
- Are relationships typed rather than implied through tag accumulation?

### Causal integrity

- Are causes distinguished from correlations and beliefs?
- Can we identify what enables or inhibits possible developments?
- Do outcomes arise through sequences rather than arbitrary branches?

### Futures integrity

- Are possible futures genuinely different worlds rather than cosmetic endings?
- Can backcasting identify concrete preconditions and participation points?
- Does the model preserve futures that remain dormant or unresolved?

### Architectural integrity

- Is authored possibility kept separate from runtime actuality?
- Does each claimed fact have an appropriate authority?
- Are gaps recorded instead of hidden inside improvised fields?
- Has the model avoided assigning meaning prematurely?

---

## 16. Initial content trials

Version 0.1 should be tested against three scales of Manzo content.

### Trial A - Major Scenario Field

**The Choir Beneath the Glass**

Test:

- stable truths;
- critical uncertainties;
- multiple CLA accounts;
- scenario futures;
- backcast prerequisites;
- relationship graph;
- expression within current World Opportunity and Scenario architecture.

### Trial B - Person

**Sera Venn or Ilex-of-Many**

Test:

- personal knowledge boundaries;
- roles and institutional relationships;
- conflicting memories;
- capabilities;
- possible transformations;
- what should remain prose rather than metadata.

### Trial C - Ordinary object or encounter

**A glass trembling in the Neptune Lounge**

Test:

- minimal inherited context;
- one or two meaningful relationships;
- whether the model can remain light;
- how a small observation later participates in a large historical pattern.

The model succeeds only if Trial C remains easy.

---

## 17. Open questions

The following remain intentionally unresolved:

1. Which content types deserve durable identities?
2. Which relationships are authored, observed or inferred?
3. Who has authority to seal a relationship as canonical?
4. How should relationship validity change across timelines?
5. How should near-events, dormant alternatives and counterfactual histories be represented?
6. What is the minimum context required for honest relevance?
7. Does relevance relate a Pattern to a present Context, a participant, an institution, or all three?
8. How can social relationships become durable without reducing them to scores?
9. How should content cross timelines without making time travel erase consequence?
10. What authoring interface would make contextualization feel creative rather than administrative?

---

## 18. Relationship to the next architectural frontier

The Narrative Context Model prepares the inquiry beneath Pattern.

Pattern can currently describe recurrence in historical evidence. It cannot say whether that recurrence bears upon the present.

Before defining relevance, Future Sky needs sufficiently contextualized present material. Relevance cannot be honest if it compares patterns only against flat tags or globally assumed meaning.

The next research question becomes:

> **Given a remembered Pattern and a situated Narrative Context, what relationship may the system truthfully identify without interpreting meaning or activating a response?**

This model supplies the authored side of that relationship.

---

## Closing principle

> **Write the world richly. Contextualize it lightly. Connect it precisely. Let history determine which possibilities become real.**
