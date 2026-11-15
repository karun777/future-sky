# Pod console — an existing workspace

Seed ID: `POD-CONSOLE-WORKSPACE-20261115` · 15 November 2026
Status: **AUTHOR DIRECTION RECORDED; FICTIONAL DATA DRAFT. NOT LIVE.**
Current handover home: [W4-F13 — A Workspace Already Waiting](../wings/W4-F13_A_WORKSPACE_ALREADY_WAITING.md), activated for isolated rehearsal on its dedicated branch after allocation on 15 November 2026 for Efiishent. The initial W2 suggestion is superseded for task ownership: W4 owns interaction and agency; W2 remains linked for placement. This seed and its fictional fixture remain drafts, not runtime state or adopted extra canon. No seal or count change.
Source baseline: `f2da15f93a750b98bea1b8267d1e16de1c813e19`.
Authoring branch: `design/pod-console-workspace`.
Bridge key: `pod-workspace-mirror-2026-11`.

## The author's scene premise

Efiishent finds a data console in the pod. A note contains a password. He logs in and finds an existing user workspace. He assumes the console is his.

That sequence is author-supplied direction, not a report of a completed command, deployed scene or changed player record. Keep the uncertainty the author explicitly introduced: **is it his?**

The physical console, the account, the recovered workspace and each record inside it are different things. Access to one does not resolve ownership of all of them. The note's author, account holder, previous workspace user, actual console owner and origin of the records remain open. Do not silently make the workspace a verified earlier Efiishent incarnation or another known character.

## A workspace with a past, not an empty tutorial

The player discovers existing material and decides what to do with it. The scene can make familiar navigation functions useful without becoming an administrative lesson.

Possible short treatment, **assistant-authored prose for review**:

> The note gives you a password.
>
> The console accepts it.
>
> Not a blank screen. A workspace: unfinished notes, resources, messages. Things someone meant to return to.
>
> Yours, you suppose.
>
> The console has not said so.

This does not force a new choice or promise a working command. It preserves the author's assumption without turning it into omniscient narration.

## The mirrored structure

The design echoes a private working environment's navigation, **not its records**. Independent fictional data populate orientation, resources, roles/authority, undertakings, knowledge, exchange and next moves. No production shared renderer, data bridge or database has been built.

The [machine-readable sample](fixtures/pod_console_workspace.v0.1.json) is a documentary fixture under `docs/`, never a runtime save. Its `FS-DEMO-*` identifiers are deliberately not production character, item, permission or account IDs. Existing `pod_room` is a reference to inspect during later integration, not a new location or a claim that all pods are already private instances.

| Panel | Sample recovered material | What it does not establish |
|---|---|---|
| Resources | Pod data console; session opens | Ownership, portability, inventory acquisition or resale rights |
| Roles | Invitation to help the Concourse Repair Circle catalogue tools | Accepted membership, appointment or authority |
| Undertakings | “Return a borrowed diagnostic probe” | That Efiishent borrowed it or inherits the task |
| Knowledge | Old workshop route sketch | Current accuracy, a canon location or an unlocked map |
| Exchange | Archived claim of 12 station credits | A current balance, currency definition or spendable player funds |
| Giving | A repair manual freely offered | An automatic reciprocal debt or karma reward |
| Next moves | Investigate provenance, follow a clue, or leave it | A mandatory quest, accepted duty or timed penalty |

The Repair Circle, probe, sketch, balance and manual are **new synthetic examples for review**, not recovered lore or existing gameplay facts. Their dates, authors and relationship to the character remain unknown on purpose. The open owner/account questions are not answered by filling the sample.

## Important separations

**World state:** a later implementation must define each authoritative fact and its owner. This seed does not supply unknown owners.

**Observed access:** the authored login works. In the sample that opens a read-only recovered view; the precise final interaction permissions remain to author and implement. A successful login does not imply unrestricted use or transfer rights.

**Belief:** Efiishent assumes ownership. Record that as his perspective, not a title transfer.

**Inherited records:** a workspace can hold stale claims, mistaken notes or obligations belonging to someone else. Showing a task or debt must not automatically assign it to the current reader.

**Player agency:** examining, adopting, editing, accepting and acting are distinct. No automatic quest acceptance or obligation inheritance.

**Authentication:** the note is a fictional clue. It is not an actual server credential, web login or OAuth replacement. Do not put a real password in the fixture or allow a player's request parameter to select another player's workspace. The normal authenticated actor and domain checks must remain authoritative if the feature is later built.

**Player privacy:** per-character projection and actor checks need explicit tests before live use. Pod instancing is not established by this seed. Do not attach one shared readable workspace to the common `pod_room` and expose it to every occupant.

## Reconcile before implementation

The pod already has display/FEED7 and HUD strands; inspect [pod inspection and recognition](../wings/W2-F3_POD_INSPECTION_AND_RECOGNITION.md), [W7-F6 shared inspection](../wings/W7-F6_ATTEND_TO_THE_WORLD.md), and the selected live source before choosing whether this is another surface or an extension of a present one. Do not silently replace FEED7 or the behind-the-eyes display.

The archived [Console Language](../archive/deferred-subsystems/FUTURE_SKY_CONSOLE_LANGUAGE_v0.1.md) describes presentation vocabulary, not evidence that this physical console or workspace is implemented. It remains deferred and is not reactivated by this seed.

Preserve the [ontology](../current/ARCHITECTURE_v1.1.md), [authority register](../current/RUNTIME_AUTHORITY_REGISTER_v0.3.md), [event model](../current/EVENT_MODEL_v4.1.md) and [knowledge routing](../KNOWLEDGE_ATLAS.md). A view does not own the facts it presents; an event history is not automatically a replay engine.

## Later bounded proof

First review the scene and fictional records. Only after a separate implementation choice, author and test discovery, note, successful/failed login, character-scoped projection and ordinary return. Repeated inspection must not duplicate resources or grants; reload must preserve only explicitly completed actions. A second fictional user must not read the first user's workspace. A carried task or archived credit must not become a quest or balance through display alone. No real records may enter a fixture, player response or game log.

A console can be useful without first building a general economic engine. Do not expand this seed into a database migration or resume Chapter 1 without a deliberate selection of the next work.

## Cross-project continuity

This is the Future Sky-owned record of the fictional premise and sample. The private companion workspace keeps its own asset register and coordination mapping. It is not a runtime dependency, and no private asset identifiers, local paths, financial records or personal documents are copied into this fixture.

The shared key above identifies a design relationship, **not entity equivalence or automatic synchronisation**. Each repository owns its facts. A fresh session should read its own Atlas, Wing Index and current feather before following this seed. Tool access and an authorised task are required to inspect another repository; conversational project memory is not a source-control mechanism.

## Reproducible fixture checks

Run `python3 docs/seeds/validate_pod_console_workspace.py` from this repository. It checks the seven-record sample and rejects ten deliberately invalid variants covering mixed realms, invented ownership, stored credentials, spendable archived balances, reciprocal gift debt, assumed role authority, inherited obligations, production loading, acceptance by display and duplicate IDs. These checks validate the sample's declarations; they are **not** a deployed security policy or live gameplay test.

## Historical return card — before W4-F13 allocation

Reached: author direction recorded and a seven-record fictional workspace sample prepared for review. No runtime implementation, player login, reset, inventory grant, money credit, new account, role transfer, world-clock change, deployment or permissions change.

Current gameplay-source work remains W6-F11, ACTIVE / source prepared on `engine/w7-f10-beginning-again`; Chapter 1 / W4 remains paused. No implementation priority, next feather ID or completed count changes. This seed is not a second active gameplay feather.

The companion design branch preserves the source baseline. Documentation may be fast-forwarded to the current source branch after verifying it has not moved, so a future session can discover this seed without losing W6-F11. Neither branch is the installed runtime or main.

Next for this seed: review the fictional scene and example workspace; then scope a separately selected playable slice. Continue the current HUD review separately unless Karun changes direction.
