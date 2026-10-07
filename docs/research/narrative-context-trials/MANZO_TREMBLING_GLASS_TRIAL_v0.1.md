# Narrative Context Trial 1 — A Glass Trembling

**Status:** Exploratory authoring trial  
**Version:** 0.1  
**Era:** Manzo  
**Primary location:** Neptune Lounge, Triton Central  
**Model under test:** `NARRATIVE_CONTEXT_MODEL_v0.1.md`  
**Runtime status:** Not implemented  
**Canon status:** Candidate material; not canonical

---

## 1. The writing

The glass began trembling before anyone touched it.

Not rattling. Not sliding. The thin stem remained exactly where Sera had left it, inside the pale ring dried into the bar from someone else's drink. Only the bowl moved: a small, lucid shiver that made the reflected lights of Neptune Lounge divide and recombine.

Around it, the room continued.

Bass travelled through the floor in long animal waves. Someone laughed near the old security arch. Beyond the curved windows, Triton Central held its nightless posture beneath the broken congregation of the sky.

Sera put two fingers against the bar.

Nothing.

She lifted them and the glass trembled again.

“Don't,” said the barmaid.

Sera looked up. “Don't what?”

The barmaid was already reaching past her for a bottle. “Make it lonely.”

She poured three measures although only two people were waiting. The third she set beside the trembling glass.

For seven breaths, both glasses were still.

Then the new one answered.

Not with the same movement. The first glass trembled inward, toward a centre it could not contain. The second gave a single clear note. It was too low for so little crystal, and too clean to belong to the music.

Conversation did not stop. Nobody turned. Yet Sera felt the room make space around the sound.

A memory arrived without images: hands she had never possessed, setting cups along a surface that curved away beneath a different gravity. A custom without explanation. One vessel for the traveller. One for what had travelled through them.

Sera withdrew her hand from the bar, although she had not touched either glass.

“Who is the second drink for?” she asked.

The barmaid glanced toward the window.

Outside, something crossed between the city and the stars. It might have been a service craft. It might have been a fault in the glass.

“It hasn't decided yet,” she said.

The first glass stopped trembling.

The second continued to sing after Sera could no longer hear it.

---

## 2. What remains deliberately unresolved

The scene does not establish:

- whether the vibration has a physical, technological, psychological or ritual cause;
- whether Sera experienced a memory, an interpretation or an intrusion;
- whether the barmaid knew the phenomenon would occur;
- whether the custom predates human settlement;
- whether the moving object outside caused, answered or merely coincided with the event;
- whether the second glass was offered to a person, a memory, the city or something arriving;
- whether anyone else perceived the low note.

These uncertainties are part of the content. They are not missing implementation.

---

## 3. Minimal contextual envelope

### Identity

```yaml
id: encounter_manzo_neptune_lounge_trembling_glass_001
title: A Glass Trembling
content_type: encounter
authorial_status: exploratory
canon_status: candidate
provenance: narrative_context_trial_1
```

### Situation

```yaml
era: manzo
region: triton_central
location: neptune_lounge
scene_scale: intimate
social_setting:
  - public_bar
  - ordinary_service_continuing
participating_characters:
  - sera_venn
  - neptune_lounge_barmaid
material_elements:
  - two_drinking_glasses
  - bar_surface
  - curved_windows
active_pressures:
  - broken_sky
  - uncertain_memory_provenance
```

The scene inherits Manzo-era and Neptune Lounge context. It does not declare a precise world time or timeline family because neither is presently required by the writing.

### Perspective

The prose remains close to Sera's experience.

Sera may honestly claim:

- she saw the first glass tremble;
- she felt no matching vibration through the bar;
- she heard or experienced a low note;
- an unowned memory-like impression occurred;
- the barmaid placed a second drink;
- something appeared to cross beyond the window.

Sera may not honestly claim:

- what caused any of these things;
- that the memory belonged to Triton's original inhabitants;
- that the city communicated;
- that the external object was a comet, vessel or fault;
- that the barmaid understood the phenomenon.

The barmaid's words are recorded as speech, not proof of knowledge.

### Discovery tags

```yaml
themes:
  - memory
  - hospitality
  - arrival
  - continuity
tone:
  - intimate
  - uncanny
scale:
  - personal
  - relational
domains:
  - ritual
  - ordinary_life
  - perception
```

These tags support discovery only. They establish no causal relationship.

---

## 4. Typed relationships

Only relationships supported by the authored scene are proposed.

```yaml
relationships:
  - source: encounter_manzo_neptune_lounge_trembling_glass_001
    type: located_in
    target: neptune_lounge
    authority: author
    status: proposed

  - source: encounter_manzo_neptune_lounge_trembling_glass_001
    type: participates_in
    target: sera_venn
    authority: author
    status: proposed

  - source: second_glass_offering
    type: echoes
    target: traveller_companion_vessel_custom
    authority: narrator_framing
    status: uncertain

  - source: sera_memory_impression_001
    type: contradicts
    target: sera_known_personal_memory
    authority: sera_venn
    status: experienced_not_explained
```

The final two relationships require later identity work if the custom or memory becomes durable content. They should not yet be promoted into a canonical relationship registry.

---

## 5. Narrative affordances

The encounter makes the following available without requiring any of them:

- Sera may investigate whether the Lounge has recorded similar incidents.
- The barmaid may refuse explanation while repeating the practice.
- Another participant may recognise the two-vessel custom differently.
- A later observation may echo the low note or inward trembling.
- Conflicting accounts may emerge about whether two glasses were present.
- The scene may remain an isolated moment with no larger consequence.
- A future Scenario Field may inherit this encounter as evidence, rumour or misremembered origin.

The encounter does not automatically awaken a Scenario.

---

## 6. Expression through current architecture

### Already expressible

**Room**

The Neptune Lounge can hold the physical setting, ambient sound, window view and ordinary bar activity.

**Character**

Sera and the barmaid can participate without either becoming the authority for world truth.

**Thread Node**

A Thread Node could increase resolution around Sera's response:

- ask the barmaid;
- touch neither glass;
- take the second drink;
- invite another witness;
- leave the event unresolved.

This would represent local agency, not explain the phenomenon.

**World Opportunity**

An authored opportunity could become eligible under declared Manzo-era and location conditions. Current architecture could match, gate and instantiate it, but doing so now would require inventing a runtime catalogue entry and is outside this trial.

**Event and observation**

If implemented later, the runtime could publish a narrow fact such as a declared encounter occurrence and preserve participant observations. It must not publish “the city remembered” unless a legitimate authority owns that truth.

**History and Pattern**

Repeated observations of glass vibration or the low tone could later be queried as neutral recurrence. Pattern could cite evidence. It could not declare ritual significance.

### Not yet honestly expressible

Current architecture does not provide a settled authority for:

- attaching authored contextual envelopes to content;
- durable identities for small encounters and memory impressions;
- typed authored relationships with perspective and evidentiary status;
- distinguishing narrative affordance from runtime eligibility in a common representation;
- determining whether a remembered pattern is relevant to Sera's present encounter.

These are findings, not requests for immediate implementation.

---

## 7. What the trial teaches

### The model remains light enough at this scale

The prose was written first. The context was added afterward. Most fields from the full model were unnecessary.

### Perspective is more valuable than dense tagging

The crucial distinction is not that the scene is tagged `memory`. It is that Sera experiences something memory-like without gaining authority over its origin.

### Relationships need provisional status

Small content can imply relationships whose endpoints do not yet deserve canonical identities. The model must allow provisional connection without forcing premature registry work.

### Ordinary objects can carry large futures

The glasses do not need to be magical items or new ontology primitives. Their significance can emerge through recurrence, testimony and later relationship.

### Architecture should stop here for now

The trial produces no justification for a relevance engine, resonance score, meaning authority or automatic Scenario activation.

---

## 8. Trial verdict

**Literary integrity:** Preserved.  
**Contextual integrity:** Sufficient at minimal/situated depth.  
**Causal integrity:** Uncertainty preserved; correlation not promoted to cause.  
**Futures integrity:** Several paths are available without becoming branch prescriptions.  
**Architectural integrity:** Authored possibility remains separate from runtime actuality.

The Narrative Context Model passes its first small-scale test provisionally.

The next useful test should concern a person—Sera Venn or Ilex-of-Many—where knowledge boundaries, conflicting memories, roles and institutional relationships place greater pressure on the model.

---

## Closing note

The scene does not become important because metadata says it is important.

It becomes available to history.

History may or may not return to it.
