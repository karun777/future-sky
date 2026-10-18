# W2-F3 — The Opening We Can Inhabit

**Home:** W2 Worlds  
**Linked wings:** W1 Mythos, W3 Beings, W4 Play, W5 Time, W6 Expression, W7 Engine, W8 Stewardship  
**Status:** REVIEW — source walkthrough and one staged passage ready; author review pending  
**Date:** 18 October 2026, Australia/Perth  
**Source revision:** `48ff5b822ca81c8551e4e84b83eeb8a2922d2f90` on main  
**Return:** [Wing Index](../WING_INDEX.md)

**Connected return:** [Awakening reconstruction](../handover/AWAKENING_RECONSTRUCTION_20261018.md) now reads the pod, reintegration, wardrobe, FEED7 and tomorrow's gig together. [Source review](../handover/AWAKENING_SOURCE_REVIEW_20261018.md) records the live checks and revisions.

## The experience we are building

An immersive MUD 7.0: a world worth inhabiting, an opening that invites attention, and actions that let the player find their bearings. Karun has put larger World Engine expansion on hold while world-building and player experience provide its context.

This feather traces existing arrival material from first awareness to the first meaningful choice, then selects and stages one small passage for review. It is a source-based walkthrough, not a Discord playthrough. The draft below is new candidate writing; the existing scene remains intact.

## The opening already present

The most developed current arrival is [Transit Pod 3417](../../data/thread_nodes/thread_nodes.json), node `arrival_awakening_v1`. Its roots include the [archived arrival template](../archive/process-history/arrival.md), but that template's coherence test, `!code love` exit and collapsing pod must not be presented as the current sequence.

The present pod has a body, a temperature, a soundscape, evidence of other people and objects within reach. It offers tension between sensory experience and supplied information without deciding which account is right. [W1-F2](W1-F2_FINDING_OUR_WAY_THE_BROCHURE.md) already establishes this reading.

The first meaningful choice is **how to seek bearings**, not which combat power to use: listen, intervene, accept supplied guidance, examine something personal, wait, or question the situation.

## A source-based walk through the opening

| Player beat | Existing material or behaviour | Experience and seam |
| --- | --- | --- |
| Enter the game | [CoreCog.create_character](../../bot/fsbot/cogs/core.py) takes a name, birthdate and class; stores `current_room = pod_room`; creates a run channel where possible. | The player supplies identity before a character who supposedly does not remember it awakens. This can be player/Character knowledge separation, but needs deliberate presentation. Do not run creation again as a reset: it assigns a replacement character record. |
| First welcome | The same callback says the character stumbles through a blue-edged portal into the Lounge. | The welcome describes a different immediate location from the stored pod. It does not call Navigation or start the awakening node in that callback. Successful creation alone does not establish delivery of the opening. |
| Become aware | Pod room description: transit pod, condensation, construction beyond the walls, no memory of boarding/arriving. The Thread Node adds cold blue light, chain at chest, red light, overheard disagreement and brochure. | Two authored layers can reinforce each other, but the room card should not feel like the character awakens afresh on every look. Narrator disorientation fragments are another layer, not a guaranteed scripted montage. |
| Encounter the scene | [ThreadNodesCog](../../bot/fsbot/cogs/threadnodes.py) subscribes to `character.entered_room`, selects an eligible node and needs an existing run channel before starting it. [Navigation](../../bot/fsbot/cogs/navigation.py) publishes that event after saving a move. | An on-enter trigger is not equivalent to initial record creation. `!look` presents an already-active node but does not itself start the arrival node. The initial bootstrap is a concrete seam, not proof the text is absent. |
| Choose an approach | The six numbered options use `!choose <key>`. | Each option offers a different relation to uncertainty. Listening need not be the correct answer; waiting need not be punished. |
| Receive a consequence | The chosen result is sent; option effects set the corresponding flags. Then `choose_cmd` marks the whole node complete, clears it and saves. | This is **one choice per awakening node**, not six repeatable inspections. Listening does not automatically lead to brochure inspection, green light or key discovery. Result text precedes the save, so source order alone is not a durability guarantee. |
| Orient and leave | [Room graph](../../data/rooms/rooms.json): pod **west** → hostel hallway **down** → stairwell **down** → Lounge arrival hub. A subsequent **inside** reaches the Main Floor. | Concrete geography gives us a small, buildable opening. Current movement does not require `waited_for_green` or the key flag. Red/green light currently carries narrative implication rather than an implemented hatch lock. |
| Be met by the world | Existing wardrobe, brass token and attire reactions offer continuities into the Lounge. The counterkeeper motif follow-up is explicitly invoked; chips/name scenes exist elsewhere. | These are available strands, not mandatory tutorial steps or a proven joined-up opening. [W4-F2](W4-F2_ONE_LOOP_THAT_HOLDS.md) verifies token callbacks/persistence in isolation, not actual navigation or Discord delivery. |

Repository inspection confirms these definitions and control paths. No account was created, character moved or live game action invoked.

## What holds together

- **An intimate beginning:** body, breath, cold surface, a nearby object.
- **A world already occupied:** voices and work continue outside; the player is not the sole reason the place exists.
- **A comic institutional voice:** the brochure offers reassurance without solving the mystery.
- **A small outward journey:** pod → corridor → stairs → social hub, with the wider Lounge beyond.
- **Ways to be recognised:** clothes, a found token and conversations can carry a small choice into a later encounter.

We can deepen this existing place before inventing another region, a new mystery system or a larger engine.

## Selected passage — Listen at Transit Pod 3417

**Candidate prose for review. Not installed, canonised or represented as captured game output.**

This stages the approach to the first choice. It condenses the existing imagery and rhythm while preserving the six existing approaches. It adds no new Character, institution, cosmic fact or reward.

---

### Transit Pod 3417

Cold blue light. A breath.

Your breath.

Condensation beads on the viewport. You lift your hands. Turn them over. Open them. Close them.

They move when you mean them to.

You do not recognise them.

You cannot remember boarding.

You cannot remember arriving.

Something cold rests against your chest. A thin chain disappears beneath your transit garment.

Beyond the wall:

**THUMP. THUMP. THUMP.**

Machinery. Probably.

Someone is arguing.

“…not ready…”

“…the Lounge wasn’t supposed to open this cycle…”

“…just get them settled…”

Beside the hatch, a red light burns steadily. Below it is a red button.

A folded brochure waits in a dispenser.

**WELCOME TO TRITON CENTRAL**  
**Safest Biodome in the Neptune Sector.**  
**Six consecutive cycles.**

The banging continues.

**What do you attend to?**

1. Listen.
2. Press the red button.
3. Inspect the brochure.
4. Investigate the object around your neck.
5. Wait.
6. Question the situation.

*Choose with `!choose <number>`.*

---

### If the player listens

Retain the existing authored outcome as the starting point:

> You hold still.
>
> A voice crackles through a wall speaker.
>
> “Drone 12, consciousness check complete.”
>
> “Drone 7, memory integrity?”
>
> “Stable enough.”
>
> A pause.
>
> “Good. Open them when the light changes.”
>
> **THUMP. THUMP. THUMP.**
>
> The voice waits for the rhythm to pass before continuing.
>
> “Or whatever they’re calling maintenance this cycle.”

This lets attention reveal a little more of the world's activity without explaining the machinery, identifying the speakers or settling the character's predicament.

**The handoff still needs an authored decision:** the current callback closes the node here. The draft does not quietly add a new hatch transition, unlock a perception skill or promise a second inspection. That is where we should stop this first small passage and review its tone.

## Coordination across the wings

| Wing | Contribution to this opening |
| --- | --- |
| W2 Worlds — home | Keep the pod and outward route spatially coherent. |
| W1 Mythos | Protect uncertainty and knowledge boundaries; Feather 57 remains parked. |
| W3 Beings | Distinguish player-supplied identity from what the awakening Character remembers. |
| W4 Play | Make the first choice and its aftermath understandable; review the one-choice lifecycle before changing it. |
| W5 Time | Give the opening breathing room; no clock/cycle expansion needed here. |
| W6 Expression | Review the prose, information density and subsequent room presentation. |
| W7 Engine | Support demonstrated delivery needs; the first observed seam is creation-to-awakening, not a new World Engine layer. |
| W8 Stewardship | Preserve source evidence, draft status and return point. |

## Verification, boundary and return

Read against main at the revision above: CoreCog creation/welcome; Navigation look/go and room-entry publication; ThreadNodesCog selection/presentation/choice completion; Router allowlist; WardrobeCog; NarratorCog; authored rooms and Thread Nodes; W1-F2 and W4-F2 evidence.

The router's broad welcome says responses route from anywhere, but its allowlist excludes several newer commands such as wardrobe/search/offer/feed7. Keep any later rehearsal in the existing run channel until routing is verified. No universal routing fix is included here.

The connected MacBook is offline as checked 18 October. The earlier live runtime inspection remains dated evidence; current host state and initial Discord delivery were not refreshed. W1-F3's host sync is still pending, and no host sync is claimed for this record.

**Completed now:** source walkthrough, concrete opening route, identified seams and one full staged passage.

**Awaiting review:** whether the passage feels like Future Sky and whether listening is the right first passage to develop. W2-F3 remains in REVIEW; W2's completed count stays at 2 and total completed wing feathers at 16.

**One candidate after review:** make fresh character creation hand off coherently to the existing awakening scene, with matching welcome text and an isolated delivery check. Do not implement until this is chosen; preserve existing characters and all six source options.

No production code, world data, Red Book, service or World Engine architecture changed. The passage remains a review draft even if this documentary checkpoint is merged.

## Shared checkpoint — W2 ↔ W6: Cinematic storytelling

**Adopted:** Karun, 18 October 2026. **Home feather:** W2-F3; linked wing W6 Expression. This section owns the shared decision; both wing checkpoints link here.

Cinematic stills and occasional short videos have a substantial storytelling role. Concrete visual footholds should help players inhabit the world while leaving room for imagination. Compose prose, imagery and choices together. Stills can establish presence; motion is useful where the movement itself carries the story. Prose carries sensation, uncertainty and attention. These are creative guides, not mandatory media quotas.

Render the pod's physical setting concretely while leaving its purpose, the Character's identity and the world beyond the glass unresolved. Begin with one first-person cinematic still inside Transit Pod 3417: cold blue light, condensation/frosted viewport, red status light and red button, a brochure partly protruding from its dispenser. No visible face or defined body; no clear outside vista, revealed mystery, HUD statistics or new lore.

**Review state:** Karun approved the walkthrough's direction and requested stronger cinematic support. W2-F3 remains in REVIEW while prose and the first still are assessed together. Generating a concept image does not install an asset, approve a final visual canon or complete another wing's feather. Completed counts remain 16.

**Carry forward:** Worlds maintains spatial coherence and what is discoverable. Expression maintains visual treatment, framing, prose/media balance and continuity across later images. The first image is a review concept generated in conversation; a selected production asset will need its own versioned repository placement and delivery check. Live-host documentation sync remains pending.

**Generation brief:** cinematic photorealistic science-fiction still, landscape, seated/reclining first-person eye height inside a compact habitable transit pod; tactile, slightly worn materials, cold blue practical lighting and soft red indicator; condensation obscures the viewport; integrated hatch controls and partly dispensed paper brochure; restrained, intimate, mysterious and humane rather than horror. No visible person, no exterior reveal, no added objects or signage beyond pod number and brochure heading. Review-only, no media installation.

## Shared checkpoint — W2 / W3 / W4 / W6: Attention and recognition

Karun's 18 October direction: every discernible thing shown should support closer investigation, with text and/or close-up media and authored contextual differences. Prioritise depth in a small inhabited Triton Central. Keep early unfamiliar hands and recover FEED7 after bodily awareness; looking for one's reflection is a natural player intention.

The [pod inspection and recognition pass](W2-F3_POD_INSPECTION_AND_RECOGNITION.md) owns the complete visual inventory, source recovery, hands-first revision, FEED7 boundary and proposed wardrobe mirror. W3 joins the crossing for embodied identity, W4 for investigation and W6 for visual promises; W2 remains home. Generated props and mirror placement are proposals, not adopted lore or implemented affordances. No extra feather allocated; W2-F3 remains in REVIEW.

The next candidate in this follow-up refines the earlier creation-handoff candidate: review the pod inspection slice first so any implementation carries the recovered experience rather than simply wiring an incomplete scene.

## Switch checkpoint — W4-F3, 18 October 2026

W2-F3 stays in REVIEW while [W4-F3 — Two Days at Neptune Lounge](W4-F3_TWO_DAYS_AT_NEPTUNE_LOUNGE.md) maps the concrete mission the pod prepares a participant to enter. [Preparation and work garments](W2-F3_POD_PREPARATION_AND_WORK_GARMENTS.md) records Karun's subsequent existential-spy framing, basic creation before ordinary departure, possible unprepared exit, five explicit work outfits, casual gear and jobs separate from factions. Earlier mirror/prop responses remain proposals. No production changes or W2 completion increment.
