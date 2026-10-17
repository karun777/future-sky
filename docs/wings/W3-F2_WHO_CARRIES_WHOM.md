# W3-F2 — Who Carries Whom

Home: W3 Beings. Status: COMPLETE — documentary identity, role and driver map of the existing cast.
Date: 17 October 2026. Previous: [W3-F1](W3-F1_WHO_IS_ALREADY_HERE.md).
Return: [Wing Index](../WING_INDEX.md).
Source revision: 8bf1853bbbf64f4973f6e3143db3cf7fecd280c8. Live source inspected at runtime checkout 937c007a2981d10b8e1230f293c85b6c72750425.
No new Characters, Roles, Drivers, agents, canon or runtime registry created.

## Existing distinctions

The [current ontology](../current/ARCHITECTURE_v1.1.md) already defines:

- **Character:** the persistent world-expression of a being; identity, history and relationships are not identical to a job.
- **Role:** a situated responsibility that can outlast its occupant.
- **Driver:** the current source of decisions; possible forms include Human, AI, Script, Narrative process and Dormant continuity.

These are conceptual distinctions, not proof that an explicit driver registry or handover service exists in code. The human author of a script is not automatically a live Human Driver whenever that script runs.

## Existing representation map

| Existing being or participant | Character / identity evidence | Role or function expressed | Decision source actually supported by inspection | Continuity currently evidenced |
| --- | --- | --- | --- | --- |
| Account-keyed participant | Persistent character entry keyed by command author's account ID. | Chosen actions, exploration and participation; a role is not inferred solely from the name. | Commands select the invoking account's record. Human versus automation behind the account was not verified. | Saved character data. No separate persistent driver assignment established. |
| Efiishent | Named lore; live stored record shares the name. | Wizard, Cube guardian and Key bearer in lore. | Account command route exists; present controller and relationship to all lore selves are unknown. | Character persistence and authored cross-era lineage, not proven single-instance equivalence. |
| Dark Rat Queen | Named lore, matching stored name, room references and lesson. | Alchemist, navigator, smuggler and teacher. | Authored lesson responses are script-expressed. Current driver of the account character is unknown. | Lesson state is recorded on the participating character; this is not proof of a separate Queen memory ledger. |
| The Puzzler | Named lore identity. | Riddling architect/curator. | No specific runtime decision source verified. | Authored lineage; persistent agent not established. |
| Portal Sluts | Composite meta-being in lore. | Musical/cosmic expression of three named participants. | No collective runtime driver or aggregation service verified. | Lore relationship; no duplication or identity merge performed. |
| Vitriol / comet entity | Working narrative material, not agent deployment. | Antagonist / cosmic force within the working outline. | No runtime driver verified. | Research provenance; author knowledge is not character knowledge. |
| Counterkeeper, priest and service drone | Encounter participants, not separately verified persistent Characters. | Food service, origin inquiry and delivery. | Authored node text and effects, selected by Thread Node code; player chooses or answers where offered. | Flags, answers and completion state on the participating player's record. No independent staff memory inferred. |
| Security droid / pod voices / rat | Authored identifiers or appearances. | Gatekeeping, onboarding, lesson cue. | Scripted expression in inspected content; autonomous decisions unverified. | Participant-side scene state where declared; independent identity continuity unknown. |
| Bartender / bouncer / silver-eyed patron | Source-expressed roles; distinct stable character IDs not established. | Exchange, social boundary and rumour witness. | Conditional Python handlers and fixed response text. This does not establish AI reasoning or independent NPC action. | Character-scoped purchase/work/social/rumour state, as inspected in W3-F1. |
| Crowd and decorative inhabitants | Descriptive presence in rooms or scenes. | Ambient social life. | Authored description; independent decisions unverified. | No individual persistent identity established by prose alone. |
| Room enemy entries | Room-scoped instance keys and overrides; separate template catalogue. | Encounter opposition. | No autonomous controller inspected by this feather. | Persistent room entries; not a verified social identity or total living-creature census. |
| Sera / candidate research people | Explicitly exploratory prose identity. | Possible perspective holder. | Authored narrative, not verified runtime control. | Research document history; not adopted casting. |

Do not silently equate bartender, barmaid and counterkeeper, or equate a named account character with every scripted/lore appearance of that name. Equivalence remains a deliberate authorial question.

## The control path we can trace

In inspected CoreCog commands and ThreadNodesCog.choose_cmd / answer_cmd:

1. ctx.author.id selects the account-scoped character.
2. The active node and authored options/prompt constrain the available response.
3. The authored result and effects are applied by code.
4. Character flags and extra.thread_nodes bookkeeping are saved.

Relevant source: [CoreCog](https://github.com/karun777/future-sky/blob/8bf1853bbbf64f4973f6e3143db3cf7fecd280c8/bot/fsbot/cogs/core.py), [ThreadNodesCog](https://github.com/karun777/future-sky/blob/8bf1853bbbf64f4973f6e3143db3cf7fecd280c8/bot/fsbot/cogs/threadnodes.py), [GameState](https://github.com/karun777/future-sky/blob/8bf1853bbbf64f4973f6e3143db3cf7fecd280c8/bot/fsbot/state.py).
Script-expressed social responses: [bouncer](https://github.com/karun777/future-sky/blob/8bf1853bbbf64f4973f6e3143db3cf7fecd280c8/bot/fsbot/bouncer.py), [rumours](https://github.com/karun777/future-sky/blob/8bf1853bbbf64f4973f6e3143db3cf7fecd280c8/bot/fsbot/rumours.py), [bar work](https://github.com/karun777/future-sky/blob/8bf1853bbbf64f4973f6e3143db3cf7fecd280c8/bot/fsbot/bar_work.py).

This supports a distinction between participant input and scripted world response. It does not establish an explicit runtime Driver object, an autonomous NPC mind or a tested controller substitution. DPC node tools can start authored material for the invoking participant; that alone does not implement a general “possess any NPC” capability.

## What must survive a future driver change

The ontology requires continuity without counterfeiting human choice. For later work, preserve the distinctions already identified: which being, which role, who/what made a decision, what that participant knew, what happened and whose record remembers it.

The current inspection does not certify a driver-transfer mechanism, shared NPC memory, role occupancy registry or offline-human substitution. Do not introduce fields or build those systems merely because this map names the gaps.

## Verification and parked return

Read the current ontology, W3-F1 and pinned ThreadNodesCog; inspected live CoreCog, ThreadNodesCog and GameState account-routing references. Checked choose/answer execution and participant-side persistence in source. No commands invoked, controller switched or character record modified.

Reached: existing identity, situated function, input/response source and persistence scope mapped without creating a new subsystem.
Open: durable NPC identities, role equivalences, driver assignment/transfer and shared social memory.
W3 completed count: 2. W3-F3 unallocated. Beings first pass parked alongside Mythos, Worlds and Stewardship.
Next proposed wing: W4 Play. No Play feather activated by this document.
