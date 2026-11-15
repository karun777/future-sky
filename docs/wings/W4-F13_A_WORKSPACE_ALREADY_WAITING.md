# W4-F13 — A Workspace Already Waiting

Status: **ACTIVE — isolated authoring and proof, open for review**
Home: **W4 — Play**. Linked: W2 Worlds, W3 Beings, W6 Expression, W7 Engine, W8 Stewardship.
Allocated: 15 November 2026, on Karun's request for a Future Sky echo handover “(for efiishent)”.
Source baseline: `4d33ce0367af9934e522886a757b978e097f2280`.
Dedicated branch: `play/w4-f13-a-workspace-already-waiting`.
Dedicated worktree: `/home/efiishent/future-sky-worktrees/w4-f13`.
Bridge key: `pod-workspace-mirror-2026-11`.
[Launch handover](../handover/W4-F13_EFIISHENT_WORKSPACE_HANDOVER.md) · [Wing Index](../WING_INDEX.md)

## Interaction treatment for review

Taken up on 15 November 2026 at clean handover `984d36f`. Both remote branch tips matched. W6-F11 keeps the active HUD work and Chapter 1 stays paused. This rehearsal follows an existing fictional stand-in for Efiishent who can already look around the pod.

| Typed action | What Efiishent experiences |
| --- | --- |
| `inspect pod` → `inspect berth` | Beside the woven cover, a strip of keys has worn smooth at the edge where a thumb would rest. A small console folds out here. |
| `inspect console` → `inspect note` | A slip catches against the hinge. On the folded face someone has written *password*. Inside, in smaller letters, *underblue*. No signature. |
| `console use note` | He keys in the word. A pencil line stops halfway across a sketch. Underneath it sits a slip about a borrowed probe. The workspace opens exactly where someone left it. *Mine, you suppose.* |
| `inspect probe slip` or `inspect sketch` | The slip says to return the probe before the bench is cleared. The sketch shows a stair with a fork at the foot. One arm of the fork has been rubbed through. Neither scrap names anyone. |
| `console mark sketch` or `console leave` | After inspecting the sketch, he may keep his place at the fork with a personal reading mark. He can also stand up at any point. Reading the slip leaves the undertaking where he found it. |
| Leave the room, return, use the note again | The workspace can be reopened. A deliberate mark brings him back to the rubbed-through fork. With no mark, the two scraps wait as before. |

The physical position, password, two scraps and reading mark are review copy. There is no confirmed owner, previous reader, note author, map exit, due date or real-world counterpart. Only the fictional stand-in selected by the rehearsal gets the private affordance. The documentary sample supplies themes and is never loaded into the game.

### Fit with existing source

- `pod_opening.py` already leads from pod to berth. The berth keeps its woven cover, panel seam and search guidance. `inspect panels`, `inspect display`, the booking and `CoreCog.feed7` retain the wall display, local listing when available and transmission link. `inspect hud` and `hud_view.py` retain the implant and its own discoveries.
- `pod_inspection.inspect_pod` and `InspectionCog.inspect` own shared pod attention. `web_portal.create_app` gets the reader from a verified session, checks current offers, room, movement and encounter gates, and consumes the offer before applying the action. `web_character_view.character_view` returns a curated projection. The room catalogue cannot hold personal workspace content.
- The full-page HUD takes typed commands in `tools/authoring/w6f8/live/game.js`. `issueCommand` also copies commands and inspection text to client history. The proof uses a fixed `console use note` action. Any later HUD binding must decide how to keep the note and private record text out of history and clear the private view when the reader or room changes. Public Discord `ctx.send` is unsuitable for the private scene.
- Keep source work under `tools/authoring/w4f13/`. Exercise the private proof with temporary fictional data and existing inspection, navigation and session boundaries. A later production command binding, enrolment and installation are separate review decisions.

## Purpose and source of authority

Give Efiishent a situated workspace through which to navigate his world: what he knows, what he can draw on, what he may do, what he has actually undertaken and what he could choose next. Echo useful navigation patterns from the author's private workspace; author fictional contents independently. This is Efiishent's gameplay handover, not instructions for commissioning a physical laptop or building another media server.

Karun's supplied premise is already recorded in [Pod console — an existing workspace](../seeds/POD_CONSOLE_WORKSPACE_20261115.md): Efiishent finds a data console in the pod, discovers a password in a note, logs in, finds an existing workspace and assumes ownership. The author asks whether it is actually his. Preserve that question rather than solve it through an invented owner, former incarnation or automatic title transfer.

This handover request gives the seed a bounded home. W4 owns the discovery, choices and consequences; the seed's earlier suggestion of W2 was provisional. W2 still owns physical placement, not a second copy of the task. The existing prose and seven-record fictional fixture remain drafts for review, not newly adopted canon.

## First bounded experience

**Notice console → investigate note → use the fictional clue → enter the existing workspace → inspect a record → choose a next move or leave → return.**

The scene should feel like discovering traces of a life, not filling in an administrative form or receiving a compulsory quest list. An existing Efiishent must be able to encounter it without another reset. Whether the final behaviour is specific to him or later reusable by other characters must be declared; do not silently seed this personal workspace for every player.

Use the existing [fictional fixture](../seeds/fixtures/pod_console_workspace.v0.1.json) as a starting test sample, not as runtime state. The console, old invitation, tool-return note, route sketch, archived credit claim, freely offered manual and possible provenance inquiry exercise resources, authority, undertakings, knowledge, exchange and agency. All may be revised deliberately before adoption. A useful first slice needs only enough of them to demonstrate a meaningful choice, not seven mandatory screens or a general economic engine.

The owner of the console, account holder, note author and previous workspace user stay unknown unless separately authored. A displayed claim is something Efiishent has found, not necessarily reliable knowledge about the world.

## Read before taking up the work

Read the [Knowledge Atlas](../KNOWLEDGE_ATLAS.md), [Wing Index](../WING_INDEX.md), this feather, the seed and fixture. Recheck [W6-F11](W6-F11_WHEN_THE_WAY_IS_CLOSED.md) before touching its client work. Follow the [Eight Wings charter](../current/EIGHT_WINGS_CHARTER.md), [ontology](../current/ARCHITECTURE_v1.1.md), [runtime authority register](../current/RUNTIME_AUTHORITY_REGISTER_v0.3.md) and [event model](../current/EVENT_MODEL_v4.1.md); dated architectural coverage is not proof of current implementation.

Reconcile the existing [pod features](W2-F3_POD_INSPECTION_AND_RECOGNITION.md), [shared inspection](W7-F6_ATTEND_TO_THE_WORLD.md) and [command-window contract](W7-F7_FROM_ATTENTION_TO_AGENCY.md) against source before choosing an interaction surface. Do not silently replace FEED7 or the behind-the-eyes HUD. Preserve text-command input and the accepted full-page window; do not add a whole new administrative interface by default.

## First session / execution boundary

Start with current source/connectivity checks and a compact interaction treatment using fictional records. Identify the existing inspection, action, persistence and authenticated projection routes that can carry it. Record unresolved design choices and implementation boundaries rather than ask Karun to reconstruct the premise.

The handover is READY, not a second active runtime job. A separate Efiishent conversation can take up this bounded authoring/isolated-development work, recording activation there. W6-F11 remains the current active source task; the wider Chapter 1 / W4 pause is not lifted by allocating this handover. Do not claim that console source is installed or that Efiishent has already played the scene. Production changes require their own reviewed installation/rollback step.

Do not start with a database migration, role-transfer engine, market/currency system, agent platform, private-repository import or operating-system setup. Share concepts and tested patterns, not live data or credentials.

## Invariants for the playable slice

- Finding the console and opening the workspace do not grant ownership, portability, resale rights or an inventory item.
- Viewing an invitation does not appoint a role. Reading a task or debt does not assign it to Efiishent. Viewing an archived balance does not credit spendable currency.
- A freely offered gift does not create a reciprocal obligation or an automatic karma reward.
- Reading, choosing, accepting and acting are distinct. The player can leave without silently accepting the workspace's undertakings or triggering a penalty.
- The note contains an in-world clue, never a real server password. Existing account authentication and actor checks remain authoritative; the fictional login must not replace OAuth or grant administrator access.
- Character-specific workspace data must not be exposed through a shared `pod_room` record, guessable character IDs, another player's view, history response or log. Private pod instancing is not assumed.
- The real and fictional records remain separate. No private identities, balances, source documents, hardware identifiers or credentials are copied into fixtures, narration or player responses.
- Domain authorities own state; presentation exposes permitted facts. Event history is not automatically replay or recovery authority.

## Acceptance evidence to build and review

| Proof | Expected outcome |
|---|---|
| Discovery and clue | A fictional existing character can notice/investigate the console and note; unsupported or premature actions give appropriate feedback, not a fabricated successful login. |
| Read and choose | The recovered view distinguishes observed access, ownership belief and unverified records. One optional next move is meaningful; leaving is a valid choice. |
| Persistence | Deliberate discovery/choice transitions save and survive ordinary return/reload. Repeated inspection does not duplicate grants; failed saving does not announce a success that was not recorded. |
| Actor isolation | A second fictional actor, a mismatched workspace ID and an unauthenticated request cannot read or act on the first actor's private workspace. Verify actual paths, not just fixture labels. |
| No inherited grants | Inspection alone creates no money, appointment, quest obligation, debt, inventory acquisition or ownership transfer. |
| Existing experience | FEED7, HUD, command input, encounter gates, normal navigation and protected accounts remain intact. No reset or raw live-character edits. |
| Independence | Tests use isolated fictional state; no private repository is needed for playback, tests or operation. |

A source-tested slice, an isolated visual review, deployment and an actual player walkthrough are different checkpoints. Report which occurred. Do not seal from a promising prose treatment or a passing fixture validator alone.

## Cross-wing return points

W2: console/note placement and relation to existing pod surfaces. W3: identity, memory and belief without imposing a past. W4: voluntary discovery and next action, home. W6: readable in-world expression within the accepted window. W7: bounded state, persistence and actor isolation. W8: independent handover, provenance and return. One feather and one eventual count, not six allocations.

## Parallel work and return contract

Use the dedicated worktree, not the active HUD checkout or installed `/opt/futuresky`. Verify branch, HEAD, uncommitted changes and upstream movement at the start and before integrating. Do not reset, stash or overwrite another session's work; a moved base needs reconciliation. The seed's original `design/pod-console-workspace` branch is lineage, not the active target for this feather.

Keep Future Sky facts here. Return a scoped commit and a short record of the scene adopted, patterns tested, known limits, open choices and source/deployment/playtest status. A later `docs/handover/W4-F13_EFIISHENT_WORKSPACE_RETURN.md` can hold that evidence when it exists. The private resource-mapping conversation can then choose which general lessons to adopt; this does not authorise editing its register or the separate physical-laptop setup branch.

The private bridge keeps counterpart mapping. The shared bridge key expresses a design relationship, not cross-repository atomicity, data synchronisation, identical entities or guaranteed shared conversational memory.

## Preparation evidence / return card — 15 November 2026

Read current Atlas, Wing Index, charter, active HUD feather, seed and fixture. Verified W4-F13 unallocated at the stated baseline. Reran the existing fixture validator: valid seven-record sample plus ten invalid variants rejected. This is documentary-fixture consistency, not gameplay/security verification. No fixture, runtime-source, asset, live state or existing test file changed by this handover.

Reached: echo task allocated and READY, with dedicated branch/worktree and copyable handover. W4 next unallocated is W4-F14. Sealed totals remain 38 overall, W4 nine, W6 nine, W7 ten. W6-F11 and existing seals remain untouched. No character reset, credential change, deployment, player action, private record import or automatic assistant launch.

Next: in the Efiishent conversation, verify state and take up the compact scene/interaction treatment and isolated proof. Keep real resource mapping and physical laptop commissioning in their own conversations. Review before sealing; allocation is not completion.
