# W4-F6 — Attending to the World

Home wing: **W4 Play**.
Status: **REVIEW — offline authoring prototype verified, 19 October 2026**. Allocated 10:57 AWST.
Completed counts unchanged: W4 four; total nineteen.

## Outcome
Design one reusable sensory interaction loop in the arrival pod: attend → perceive → interpret → act → encounter a consequence. Clarify how deliberate attention, available senses and an internal impression can support unfolding character creation.

## Bounded question
What can a player deliberately attend to in the pod, what information can they receive, and how does that inform their next action without revealing unavailable knowledge?

## Deliverable and verification
Produce a small interaction table for hearing, touch, vision, taste and smell, grounded in existing pod fixtures and existing commands. For each supported example record target, availability/conditions, observable response, optional internal impression, attempted action and resulting state change (including no change).
Trace one ordinary path and one out-of-order attempt against current source. Clearly distinguish implemented behaviour, proposed behaviour and author decisions still needed. Review this design before implementing new sensory rules. This allocation itself does not implement commands.

## Shared checkpoints
- W2 Worlds: inspectable pod fixtures and contextual affordances.
- W3 Beings: choosing identity, discovering retained faculties and developing abilities are distinct; sensing, memory and intuition must remain distinguishable.
- W5 Time: adopted awakening direction is hearing → touch → vision → taste → smell. Timing, gates and detailed mechanics remain unresolved.
- W6 Expression: communicate sensations and internal impressions intelligibly; internal voice/intuition remains distinct from goggles' technological sensing and analysis.
- W7 Engine: reuse existing interaction, persistence and routing stewards; only identify implementation needs demonstrated by this slice.

## Boundaries
No full character-creation system, skill tree, combat redesign, numerical sensory/chakra rules or wider World Engine expansion. No automatic recovery/reset, character edits or deployment. Clothing interaction remains a connected requirement, not a second active implementation feather.
The assistant's earlier sensory-loop wording is a design proposal accepted for investigation, not a blanket canon declaration or compulsory sequence for every interaction.

## Dependencies and source
Karun's 19 October conversation: paper pod logic alongside reusable interaction work; acceptance of attention/sensory interaction as the next bounded piece; explicit request to allocate the correct wing.
Read the Wing Index, eight-wing charter, current awakening sources, W4-F4, W6-F3 and W6-F4, then inspect current perception/inspection/body/wardrobe/item commands before making implementation claims.
Live source contains overlays on older checkout HEAD; preserve them.

## Return checkpoint
Current home moves from W6-F4 to W4-F6. W6-F4 remains REVIEW: five illustrated pod views deployed; close-up player checks remain open. No completion increment.
Next action: inspect current sensory/attention command paths and draft the bounded interaction table. Author sketches the pod's choice logic independently.


## Source review and interaction map — 19 October 2026, 11:03–11:10 AWST

Status: **REVIEW — bounded design and pure source traces complete; author review pending.**
The READY header above records allocation, not the current review state. No completed-count increment.

### Verified existing behaviour
AST inspection of all top-level cog Python files finds look, inspect/examine and perceive commands, but no registered listen, touch, smell or taste commands. Registration scan does not prove every command is reachable through routing/unlock/recovery gates.
The explicit awaken strand already presents vision, bodily movement, cold contact and a thumping sound together. Hearing-first staged availability is not implemented by this strand.
Inspection dispatches authored pod targets after awaken, records discoveries with copy-before-change, and persists before displaying. Most recognised targets have no prerequisite. Booking requires either panels or display discovery; pod/wardrobe discovery is not a universal gate.
Perceive selects random room exit/item/enemy cues and varies prose by awareness label. It does not establish sensory availability or a reliable internal-voice channel. Claims such as an item being a clue or important are supplied by templates, not verified contextual significance.
The brochure's first inspection produces an authored crash and repeat inspections suppress it. This is a once-per-character discovery response, not evidence of a shared external sound event.
Uniform selection grants/equips a first catalogue outfit and returns previous chest gear to the bag. It does not implement physically taking a garment from a persistent wardrobe. Existing equip/unequip use item IDs and slot names. Item use resolves carried bag items and supports read/heal actions; this does not provide arbitrary fixture interaction.

### Pod interaction table
Existing prose is evidence of current implementation, not a new decision that all sensations or objects are canonical in every context.

| Sense / target | Current conditions and response | Current consequence | Proposed reusable interaction / unresolved choice |
| --- | --- | --- | --- |
| Hearing / thump beyond wall | Explicit awaken introduction includes THUMP; no listen command or localisation check | Opening record created; no sound-source discovery | Listen to surroundings, then a named target. Report only authored audible detail; machinery remains a guess. Decide persistent ambience versus an event before replay rules. |
| Touch / body and berth | inspect body describes breathing, support and vibration; inspect berth suggests a seam; opening must exist in pod | Target discovery recorded; search panel separately grants token through existing path | Deliberate touch should require reach and distinguish tactile observation from searching/manipulating. No automatic item acquisition from touching. |
| Vision / hands, room, panels, display | inspect accepts target aliases; view may include a still. Hands may reveal HUD presence if display enabled/non-dark | Discovery persisted; panels/display allow booking | Visual observation should consult future availability, visibility and target state. Do not introduce those gates silently; current code has none for sensory return. |
| Taste / own mouth | No deliberate taste command or authored pod taste response verified | None established | Optional embodied observation requires author content. Unknown response is not proof of no taste. Do not invent food, metallic taste or a recovery stage. |
| Smell / pod surroundings | No deliberate smell command or authored pod smell response verified | None established | Optional environmental scent description requires author content and context. Do not invent antiseptic, perfume, danger or identity clues. |
| Internal impression / any supported encounter | Some current prose expresses uncertainty; perceive supplies generic interpretive templates | No distinct intuition mechanism established by this review | Keep optional impression separate from observed detail and technological analysis. Do not label all inner speech intuition or promise accuracy; triggers and player agency remain decisions. |

### Proposed interaction contract — design only
An authored response should identify: verb, target, relevant sense, location/reach, available evidence, conditions, observation text, optional impression, and explicit effects.
Resolve the target before revealing detail. Check only adopted conditions; return a specific, useful response for unknown/unreachable/unavailable targets without inventing a sensory disability.
Observation can be repeatable; an actual one-time effect must be recorded separately from merely seeing a target. Looking at a button is not pressing it; hearing an event is not causing it; knowing a target exists is not possessing it.
Use existing discovery and item stewards where suitable. No second inventory, universal sensory meter or new event engine is proposed.
Future sensory availability needs an explicit unknown/unmodelled state: absence of a field must not automatically mean blindness or full recovery.

### Character creation implications — proposals
Choosing identity/presentation, discovering retained faculties and developing new abilities remain separate.
An unfamiliar movement, fitting garment or attempted performance can provide evidence without selecting a class or granting proficiency. Clothes do not prove job/faction. Preserve this distinction when later designing skills/combat.
Sensory observation, autobiographical memory, inner speech, intuition and goggles analysis need distinct provenance; none automatically confirms the others.

### Source traces and verification limits
Used fictional in-memory character dictionaries with current installed pure functions; no live player records or Discord commands.
Ordinary path: awaken → hands → body → pod → panels → display → booking. Recorded discovery sequence as expected; repeated booking did not duplicate discovery.
Out-of-order: booking immediately after awaken returned “You have not located a booking notice yet” and left discovery state unchanged.
Repeated brochure inspection suppressed the authored crash. Input dictionaries remained unchanged by the pure selection calls.
These verify selection/discovery logic only, not Discord routing, persistence failure, timing, sensory gating or actual play experience. Existing full suite was not rerun for this documentation-only work.

Source SHA-256:
- pod_opening.py: 5aea973692fdbef1d023863e54713be05614366cbe3a818e9e3b6e026d53f594
- cogs/inspection.py: 6239468ce57e24378af56b6a0a09ab0d49bae8f360dff3a0a05f36c16e3b8d9b
- cogs/perceive.py: 4d5a5c09a4f5f552265c3a72d60cd7a596e592d5b98d3b83f3c0de58648f3aae
- cogs/router.py: 932a11fbef66f2c4d05f887740c251705d2abfcf63a2c9b589bed8345c2a7b42
- pod_wardrobe.py: da567b6ba60655a611196a9b0648b04a50b935ac23780c7a2069e66149b2b890
- item_usage.py: e586b21a52e8b1e1d5b4b2308b7d0d7f905ee2cb54ca9cb197780d6998c74523

### Updated return checkpoint
W4-F6 is REVIEW. Interaction map and ordinary/out-of-order traces are complete; no new interaction command has been built or deployed.
Next bounded candidate after review: deliberate listening in the pod, with authored repeatable ambient observation and explicit uncertainty about its source. No automatic sense-unlock progression or intuition mechanic.
W6-F4 remains REVIEW. Counts remain W4 four / total nineteen.


## Authoring prototype — 19 October 2026, afternoon
Karun clarified the thump is ordinary building maintenance and asked not to fixate on it. General warmth, taste, impact, watched-feeling and hip pain examples are broader brainstorming, not automatically pod content.
Karun approved sensory observation followed by occasional tentative authored inner thoughts. This does not settle broader intuition mechanics.

Authorised isolated implementation now exists at tools/authoring/w4f6:
- interactions.py: pure scene/verb/target resolver with explicit context facts, optional character wording, optional proposed discoveries, aliases and ambiguity rejection.
- examples.json: six editable interaction entries covering all five senses and several fictional contexts.
- test_interactions.py: seven checks passed.
- README.md: authoring instructions and integration boundaries.

Rehearsal executed successfully: listening, berth touch, hands inspection, ordinary/trained panel touch, taste and smell. Character-specific recognition changed thought without changing physical observation. Repeated observation leaves content and supplied context unchanged. Unsupported and unmet-condition responses reveal no authored observation. Explicit unavailable senses differ from unmodelled availability. Overlapping matching entries fail instead of selecting arbitrary meaning.
No bot integration, commands, restart, live character data or world-state edits. Proposed discoveries are returned only. Pain, watched-feeling, physical manipulation, inventory changes and event modelling remain unimplemented. Example content is review material, not adopted world canon.

Return: W4-F6 remains REVIEW; authoring usability is the next review, no completed-count increment. Next candidate is reviewing/editing one content entry together before deciding live integration.
