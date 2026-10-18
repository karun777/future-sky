# Transit Pod 3417 — Attention, Inspection and Recognition

**Home:** [W2-F3 — The Opening We Can Inhabit](W2-F3_THE_OPENING_WE_CAN_INHABIT.md)  
**Shared wings:** W2 Worlds ↔ W3 Beings ↔ W4 Play ↔ W6 Expression  
**Date:** 18 October 2026, Australia/Perth  
**Status:** Authoring review; inspection responses and mirror placement below are proposals, not implemented commands  
**Repository checkpoint:** `786956430013286ffae034759384f30c63213002`

## The decision carried into this pass

Karun wants every discernible feature in scene imagery to support closer investigation: text, close-up media, interaction or contextual detail. Depth in approximately ten inhabited rooms is preferred to enormous lifeless geography. Ten is a depth preference, not an instruction to delete existing rooms or a final map cap.

Meaning does not require every object to be a puzzle or reward. Ordinary wear, use, material and relationship can make a place inhabited. Equally, an unexplained visual flourish cannot be an excuse for a dead end. An unreachable thing can still be observed and described; an explicit physical limit differs from “you cannot see that” when it is plainly in the picture.

The earlier still introduced plants, books, textiles and storage without authored inspection support. These are suggestions from image generation, not established possessions or lore. This pass accounts for them rather than quietly canonising them.

## Recovered trail: what was being lost

| Evidence | Recovered detail | How to use it |
| --- | --- | --- |
| [Archived arrival, Visible Narrative](../archive/process-history/arrival.md) | Hands are the first thing noticed and are unfamiliar. Chest sensation, breathing, earthy air, body hum/scan, HUD, then sitting up and surveying follow. The pod is square/cube-shaped: spartan, comfortable, wizardy and high-tech. | Keep the early embodied recognition. Do not reduce the entire source to obsolete exit mechanics. Its viewpoint sequence remains useful authoring evidence. |
| Same arrival source | A display port carries a Lounge feed. Attention to it reveals the HUD instruction `!feed7`; opening the feed is described as fullscreen and closing it returns to the pod. | Restore FEED7 as an early discoverable strand, after initial bodily awareness. Fullscreen return is authored intent, not verified current client behaviour. |
| [Internal narratives](../../data/narratives/internal_narratives.json) | `pod_disorientation_03`: breathing and uncertainty that these are one's hands; `pod_feed7_recognition`: a nearby flickering display and FEED7. Other entries retain familiarity, earthy smell, lost purpose and vibration. | These details still exist beyond the archive. They are separate entries, not a guaranteed ordered awakening montage. |
| [NarratorCog](../../bot/fsbot/cogs/narrator.py), `_pick_on_enter` and delivery | Selects the first eligible matching narrative in catalogue order; returns one; delivery has an eight-second throttle. | For a fresh unseen catalogue the first pod impression precedes the hands entry. File presence does not guarantee hands first or FEED7 next. Mandatory opening perception should not rely on a chance impression or repeated room entry. |
| [CoreCog.feed7](../../bot/fsbot/cogs/core.py) | Sends a transmission message and `https://future-sky.net/feed7.html`. | There is an actual command. It does not implement an in-world turn of the head, fullscreen/close flow or room relocation. The website's current content was not inspected here. |
| [First Night Player Journey / Feather 32](../current/NEPTUNE_LOUNGE_FIRST_NIGHT_v0.1.md) | Already lists unfamiliar hands, HUD, FEED7, sensory presentation, agency and onward possibility. | W2-F3 extends an existing experience audit; these are not new discoveries invented today. |
| [Current awakening node](../../data/thread_nodes/thread_nodes.json) | Red/green light, button, brochure, chest chain/key/cube, listening and questioning. | Retain its tone and choices. It does not mention hands or FEED7 in its main opening text. Current options close the whole node after one selection; deeper inspection needs an explicit delivery decision. |
| [WardrobeCog](../../bot/fsbot/cogs/wardrobe.py) | Concealed wardrobe and four uniform choices; pod panel search yields brass token; selected attire is later inspectable as equipment. | These are existing candidate discoveries to make visible through attention; the wardrobe and token should not silently disappear during a cinematic redesign. |
| [Configured room catalogue](../../data/rooms/rooms.json) | Doubled reflections at Domefront Catwalk and Stardock Overlook; pool surface called a trembling mirror. | Reflection motifs exist. No explicit pod mirror/vanity or pod face-recognition interaction was found in this checked catalogue. These distant motifs do not answer an immediate search for one's face. |
| Conversation retrieval, 1 July and 15 October 2026 | Earlier material discusses Pod → Signal → Chamber → LOVE → Lounge; player/Character distinction; FEED7 as signal/art/music; embodied disorientation. | Conversation search returned summaries, many labelled prior assistant output. They are retrieval leads, not transcripts or proof of adoption/runtime. The directly read arrival source corroborates hands-first and later FEED7; old Chamber/LOVE delivery remains historical intent. |
| Karun, 18 October 2026 | Hands should be noticed quickly and not recognised; looking for a mirror is a natural desire. | Current authorial direction. A specific mirror location, appearance of the Character or identity revelation is not yet adopted. |

Repository code searches covered **feed7, mirror, hands, chamber**, then relevant source files were read. Item and room catalogues were checked without reading private character backups. The older `data/rooms.json` was checked as lineage, not substituted for the configured `data/rooms/rooms.json`.

## Revised opening: body before the room

**Candidate prose, replacing the softer “something unfamiliar about the hand” in the previous draft:**

Cold blue light.

You lift your hands.

They move when you mean them to.

You turn them over. Open them. Close them.

You do not recognise them.

For a moment, you forget to breathe.

Then a breath comes, and you feel something cold against your chest. A thin chain disappears beneath your garment.

**Whose hands are these?**

Beyond the wall:

**THUMP. THUMP. THUMP.**

Machinery. Probably.

---

The wording anchors unfamiliarity without prescribing skin, age, gender, scars, species or a biography. It is immediate perception, not an author-level claim that the body belongs to a stranger. Preserve the Player / Character / future-self distinction until deliberately revealed.

The current still has no visible hands. It can serve as the **next room-facing view**, after this bodily beat, rather than pretending it depicts the literal first instant. A hands close-up would require an agreed approach to Character appearance; no universal hand image is selected in this pass.

## View and attention sequence — proposal

1. **Hands and body:** early, reliable prose. Chest sensation, breath and hum can be investigated.
2. **Face-seeking:** looking for a reflection becomes an available player intention immediately; it is not forced.
3. **Survey the cubicle:** current room-facing still, hatch, brochure, red controls and the audible life beyond.
4. **Turn attention:** reveal the side of the pod containing a display/FEED7 port, and the concealed wardrobe if examined. They need not be visible in the first crop.
5. **Follow a curiosity:** inspect, listen, read, wait, dress, follow the signal or seek the threshold.

This is an authoring arrangement, not a required sequence of player actions or an implemented state machine. Listening and the six existing approaches remain available; no forced lesson or mirror quest is added.

## Inspection inventory of the actual concept still

Image: `exec-c3e9e45d-2755-406a-b93a-84b9b493f683.png`, generated in this conversation. SHA-256: `0304345f652469da01efc0b6b35b4f6026561d945677bd4206c1939aec671ef8`.

The image is a review concept, not a production repository asset. The table is a complete authored response proposal for discernible features at the supplied resolution, with small construction details grouped into sensible targets. If enlargement exposes another readable or distinctive feature, it also needs a response. Target names below are **proposed vocabulary, not currently supported command promises**.

| Visible target / natural aliases | Proposed closer attention | State, media and boundary |
| --- | --- | --- |
| Viewport / window / glass | Beads join into thin tracks. Your movement gives the dark glass a shifting, incomplete reflection; the outside remains obscured. | Text first; optional close-up of water and glass. No full face or outside vista guaranteed. |
| Condensation / frost / droplets | Moisture clouds the surface. A trail runs down through older trails; shapes beyond it do not resolve. | Wiping or clearing is an action to author, not an automatic inspection effect. |
| Hatch / door | A heavy framed hatch with a sealed edge, controls beside it and a recessed fitting beneath the glass. | Describe before promising how it opens. Narrative red/green and current free navigation are a recorded seam. |
| Handle / vertical recessed grip | The grip is broad enough for a hand. Its recess is darker and more polished where fingers might rest. | Examining is not opening. No forced exit. |
| Hinges / hatch frame / seals | Hinges, fasteners and the seal show ordinary wear; the frame holds steady under the distant impacts. | Grouped text detail; no invented hidden switch. |
| Slot / recess beneath viewport | A narrow recessed fitting sits below the window. From here its function is not obvious. | Source does not define it; either author a physical purpose before shipping or simplify the fitting in revised art. “Mystery” is not permanent non-response. |
| Number / 3417 / identification plate | **3417.** A number assigned to the pod. It does not tell you who you are. | Close-up optional. No assumed passenger name or history. |
| Arrow below number | A small downward triangle marks the control area. | Plain signage; do not automatically identify it with the neck cube's symbols. |
| Red light / indicator | A steady red point against the cold blue interior. No explanatory label is visible. | Later green presentation must match any authored light change; not random flavour. |
| Red button / control | A physical button, separate from the light; its surface is worn around the edge. | Inspect differs from press. Existing button option supplies the override/brief viewport result. |
| Screws / control plate / access covers | Small fasteners hold the controls and covers into the wall. Their edges catch the light. | Text; do not conflate every cover with the existing token panel. |
| Brochure / welcome leaflet | The heading welcomes you to Triton Central. The printed reassurance contrasts with the interrupted activity outside. | Existing brochure outcome is source footing. A readable close-up needs exact approved text. |
| Brochure illustration / skyline | A stylised skyline is printed beneath the heading. It is promotional artwork, not a reliable map. | Image-generated suggestion; retain only with an authored response. No invented landmark identity. |
| Dispenser / leaflet holder | A metal pocket holds the partially exposed brochure within reach. Its rim has been rubbed smooth. | Inspection can explain the holder; taking or returning a leaflet needs separate authored behaviour. |
| Trailing plant / vine / leaves | Leaves trail from the shelf, turning toward the warm light. You cannot identify the plant merely by looking. | Species/meaning not established. Text suffices initially; use position/closer view if identification is authored later. |
| Plant container / upper shelf containers | Several containers are partly obscured by foliage and shadow; their contents cannot all be identified from this angle. | Looking closer must resolve what is physically visible; no unsupported claim of alien botany or ownership. |
| Books / spines / volumes | A few volumes stand together. At this distance their spines are not legible. | Reading must lead to a real title/response once approached. Select and author actual volumes before production, or remove indistinct book-like detail. |
| Canister / flask / metal cylinder | A cylindrical metal vessel catches the shelf light. Its contents are not visible. | Do not call it drinkable or usable without defining opening and contents. Resolve the prop or remove it before production. |
| Folded cloth / towels | Folded textiles occupy the shelf. Their weave and edges are more definite than their purpose. | Proposed retained ordinary detail; touching may clarify texture. No free towel item is silently granted. |
| Shelves / cubbies | Storage is built into the walls, rather than furniture standing loose in the pod. | Looking under/behind can return an authored ordinary result; not every recess must hide loot. |
| Warm shelf lights / strips | Warm light picks out leaves and cloth against the blue light at the hatch. | Descriptive support; switch/dimming behaviour not assumed. |
| Berth / bedding / blanket | Rumpled woven fabric lies over the berth, close enough to feel its texture when you move. | Text; no inference of whose blanket it is or proof someone slept here before you. |
| Upholstery / padded edge / berth rim | A padded edge runs beside you; the hard rim supports the bedding. | Text and movement-relative detail. No equipment bonus. |
| Vent / grille | Narrow slats break the wall panel. A faint flow of air gives the pod a lived-in temperature. | Candidate sensory detail; remove “airflow” if final prop is authored differently. No established speaker identity. |
| Right-wall mesh / padded inset | A dark, woven-looking inset sits in the side wall. Its construction is unclear from the first view. | Must resolve as pocket, upholstery or grille before final art; do not pretend all are simultaneously true. |
| Upper-right partial framed panel | Only part of a framed inset appears in this crop; there is not enough visible content to identify it as a screen. | Could be integrated with a later FEED7 display view, but that is a proposed revision, not a recovered fact. |
| Wall seams / surface wear / marks | Scuffs collect at edges and around fittings. They suggest use without identifying a prior occupant. | Distinct readable scratches/marks need their own closer response if introduced; generic wear can share a description. |
| Small striped marking / warning tab at hatch base | A short black-and-yellow marking sits near the lower frame. No wording is legible. | Close-up text can describe caution marking; no invented warning message or hazard. |
| Blue light / shadow / obscured shapes beyond glass | Light gives depth to the moisture but does not resolve a scene outside. | Camera/lighting cannot secretly reveal a definite person that the inspection denies. If players read a silhouette, respond to that ambiguity. |

The first concept is more rounded and weathered than the archived **square, functional, comfortable** cubicle. That is an art-direction seam to review, not a new fact about the pod. Keep its useful intimacy; do not let generated geometry silently overwrite authored space.

## Things absent from this crop that still belong in the opening

| Target | Source or status | Proposed discoverability / response |
| --- | --- | --- |
| Hands / fingers / palms | Explicit older arrival; existing hands narrative; current author instruction. | Notice early. Looking closer describes what the Character can perceive without granting an identity answer. |
| Breath / chest / garment / chain | Existing arrival and Thread Node. | Chest attention finds the chain; following it reveals the key/cube through existing authored material. Not visible in this outward-facing crop. |
| Key / wooden cube / symbols | Existing neck-object choice. | Discovery is not automatically inventory acquisition. Symbol close-ups must preserve the source's uncertainty and approved object appearance. |
| Body hum / apparent scan / speaker / sound | Earlier embodied arrival and current overheard voices. | Listen and feel are valid investigation, not just mouse-like visual hotspots. Do not identify the source of every sound prematurely. |
| FEED7 display / signal / screen | Recovered arrival, narrator entry and actual `!feed7` handler. | Proposed early turn of attention: a side display flickers; focusing offers FEED7. It need not intrude into the initial hands view. |
| Wardrobe / clothes compartment | Actual wardrobe command. | Inspecting the cubicle/wardrobe area should expose it; do not require guessing a command absent any cue. |
| Loose panel / underside of berth | Actual pod search command. | A closer examination can expose a seam worth searching. Its physical position should agree with the final view. |
| Mirror / reflection / face | Current player intention from Karun; specific mirror fixture is a new proposal. | Give a real authored route to a reflection, below. Do not answer a plainly reasonable action with a generic invisible-item rejection. |

## Looking for a mirror — one concrete proposal

A mirror is an ordinary response to unfamiliar embodiment, not necessarily a cosmic puzzle.

**Proposed location for review:** a small reflective panel on the inside of the concealed wardrobe door. Opening the wardrobe exposes it. This reuses an existing local discovery instead of adding another room. No source presently establishes this fixture.

**Candidate response to searching for a mirror:**

> The viewport gives back blue light, water and the suggestion of your own movement. Not enough.
>
> You turn toward the storage panels. In the edge of one, a narrow grip catches the light.
>
> There may be a better place to look.

**Candidate response after opening the wardrobe:**

> Clothes wait in the compartment.
>
> On the inside of the door, a small mirror.
>
> You lean closer.
>
> The face moves with you.
>
> That does not make it familiar.

The face's particular appearance must come from an agreed Character appearance choice or authored identity, not an arbitrary generated protagonist. The inspection must eventually describe visible features or use an approved Character-specific image; perpetually obscuring the face after promising a mirror would repeat the original problem.

**Review boundary:** this is a concrete candidate, not permission to add a mirror retroactively to every existing pod picture or to treat any reflection as an identity reveal. No `!mirror` or `!inspect hands` command is claimed to exist.

## Context changes that can reveal different detail

Author a base description first, then add only changes supported by a declared condition. There is no new context engine in this document.

| Context | Grounded possible difference | Constraint |
| --- | --- | --- |
| Position / attention | First crop omits the side display; turning reveals FEED7. Closer attention makes an actual book title legible. | Offscreen is a viewing boundary, not a permanently uninspectable object. |
| Time / light state | Red indicator becomes green after a defined event; the same glass may reflect more clearly when lighting changes. | No claim that waiting currently updates the image or locks the hatch. |
| Person | Character-specific hands/face differ; a symbol may be recognisable to someone with relevant knowledge. | Player familiarity does not automatically become Character memory. |
| Recorded discovery | A previously examined cube can now be described by its known details rather than repeating total unfamiliarity. | Existing flags are evidence candidates; do not invent unlocked knowledge or claim persistence is wired. |
| Return / changed world | An object moved or altered by an actual event should appear and inspect differently on return. | Prefer a truthful ordinary repeat description over random changes or fake personal memory. |

## Current implementation gap, kept small

[InspectionCog](../../bot/fsbot/cogs/inspection.py) calls [inspect_item](../../bot/fsbot/item_inspection.py). It matches exact item IDs/names in the item catalogue and requires bag, equipment or room-item visibility. The pod's room-item list is empty. It does not provide general scene-fixture or body inspection, and it does not analyse the image.

Therefore this inventory is **authored content for review**, not a shipped inspection system. There is already specific wardrobe/search behaviour and existing numbered scene choices; neither provides universal inspection of the cinematic still.

Before calling the pod playable, a bounded implementation must resolve its actual targets, natural aliases, responses, discovery boundaries and presentation. Keep the new work at the scene boundary; the authoring need does not justify restarting larger World Engine expansion.

## Shared checkpoint and return

**W2:** spatial truth and discoverable objects, including things outside the first crop.  
**W3:** unfamiliar embodiment, appearance ownership, recognition and knowledge.  
**W4:** closer attention receives a meaningful response; inspect differs from manipulate.  
**W6:** every discernible visual feature is an authored promise; text and media must agree.

This document owns the inventory and the mirror proposal. The W2-F3 parent owns the opening, status and earlier cinematic decision; each affected wing links here rather than copying competing inventories.

Completed: conversation retrieval, repository/source search, actual-image visual audit, concrete draft responses and revised hands-first opening. Awaiting review: retained generated props, wardrobe mirror location, face representation and the authored inspection content. W2-F3 remains in REVIEW; counts unchanged.

**One next candidate after review:** implement a small pod inspection slice around hands, reflection-seeking and FEED7 discovery, preserving the source-backed opening and testing the actual player-facing callbacks in isolation. No implementation, new image, media deployment, live-state write or service restart performed by this pass.
