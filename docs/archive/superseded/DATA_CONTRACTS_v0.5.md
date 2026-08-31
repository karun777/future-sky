# Future Sky — Data Contracts

**Version:** 0.5.0  
**Date:** 2026-08-31  
**Status:** Sealed current contract  
**Supersedes:** `DATA_CONTRACTS_v0.4.md`  
**Evidence:** Reconciled against live Python source, active persistent-store inventory, structural inspection of current JSON/JSONL stores, Runtime Authority Register v0.3 and Event Model v4.1.

## 1. Purpose

This document defines the canonical shape, location, ownership and mutation boundaries of persistent data used by the current Future Sky runtime.

It defines:

- which stores are current;
- what broad structures systems may rely upon;
- which authority owns each semantic namespace;
- which component performs persistence;
- what constitutes contract drift;
- how contracts may evolve without silently changing meaning.

It does not define metaphysical canon, narrative meaning, gameplay balance, presentation style or future ontology.

## 2. Authority rule

Persistence and semantic authority are different.

`Storage` owns the mechanics of loading and saving the central JSON stores. It does not automatically own the meaning of every field inside them.

Domain systems own the namespaces they are permitted to mutate.

```text
Domain authority decides what becomes true
        ↓
Persistence boundary stores the resulting shape
        ↓
Readers consume truth through declared contracts
```

No system may treat access to a JSON file as permission to reinterpret or mutate every field in that file.

## 3. Global invariants

- Text encoding is UTF-8.
- Canonical JSON stores contain valid JSON.
- Event History contains one valid JSON object per non-empty JSONL line.
- IDs are strings unless explicitly contracted otherwise.
- Unknown keys may be tolerated for forward compatibility.
- Unknown keys are non-authoritative until declared by a contract.
- Missing optional keys must degrade safely.
- Systems must not silently change an existing field's semantic meaning.
- Persistence should be atomic where implemented as replaceable JSON.
- A failed persistence operation must not be presented as completed canonical truth.
- Historical data must not be rewritten merely to match a newer interpretation.

## 4. Current canonical path registry

### Central stores

| Domain | Canonical path |
|---|---|
| Characters | `data/characters/characters.json` |
| Rooms | `data/rooms/rooms.json` |
| Room baseline | `data/rooms/rooms_base.json` |
| Enemies | `data/enemies/enemies.json` |
| Items | `data/items/items.json` |
| Thread Node definitions | `data/thread_nodes/thread_nodes.json` |
| Modifier layers | `data/modifiers/layers.json` |
| Era time profiles | `data/modifiers/era_time_profiles.json` |
| Lockers | `data/storage/lockers.json` |
| Efiishent vault | `data/storage/efiishent_vault.json` |
| Cubes | `data/storage/cubes.json` |

### World Engine stores

| Domain | Canonical path |
|---|---|
| World Clock | `data/time/world_clock.json` |
| Astrology snapshot | `data/astrology/current_snapshot.json` |
| Comet Cycle | `data/comet/current_state.json` |
| Temporal Resolver | `data/time/temporal_resolver.json` |
| Comet Pressure Field | `data/fields/comet_pressure/current_state.json` |
| World Opportunity catalogue | `data/world_opportunities/catalogue.json` |
| World Opportunity runtime | `data/world_opportunities/runtime_state.json` |
| Event History | `data/events/event_history.jsonl` |

### Supporting authoring/configuration stores

| Domain | Canonical path |
|---|---|
| Ambient configuration | `data/ambient/global_ambient.json` |
| Internal narratives | `data/narratives/internal_narratives.json` |

Paths not listed here are not automatically current merely because a file exists.

## 5. Known legacy or uncertain paths

The 2026-08-31 inventory found additional paths including:

- `data/characters/data/...`
- root `data/rooms.json`
- root `data/era_time_profiles.json`
- `data/combat/combat_state.json`
- `data/respawn_timers.json`
- `data/cubes/cube_sessions.json`
- `data/hud/hud_metrics.json`
- `data/hud/hud_states.json`
- `data/irl/irl_nodes.json`

These are historical, legacy or uncertain until a separate path-usage audit proves otherwise.

They must not be:

- deleted;
- promoted into the canonical registry;
- merged into current stores;
- treated as additional authorities;

without explicit evidence and migration planning.

## 6. Runtime ownership matrix

| Data / namespace | Semantic authority | Persistence mechanism | Readers |
|---|---|---|---|
| Character identity and profile spine | Character/Core lifecycle systems | Storage | All authorised systems |
| `characters.current_room` | Navigation | Storage | Presence, Combat, Ambient, Scenario and expression systems |
| `characters.stats` and combat HP | Combat/character systems | Storage | Gameplay and presentation systems |
| `characters.pools` | Declared gameplay systems | Storage | Gameplay and presentation systems |
| `characters.bag`, `equipped` | Inventory/gameplay systems | Storage | Combat, character and presentation systems |
| `characters.flags` | Declared gameplay/lifecycle systems | Storage | Relevant systems |
| `characters.extra.thread_nodes` | Thread Nodes | Storage | Thread Nodes and presentation |
| `characters.extra.narrator` | Narrator | Storage | Narrator |
| `characters.extra.hud` | HUD preferences/presentation | Storage | HUD |
| `characters.extra.astrology` | Astrology interface metadata | Storage | Astrology and presentation |
| Character routing fields | Router | Storage | Router and Activity |
| Rooms and exits | World authoring / Navigation contract | Storage | Navigation and world systems |
| Room enemy instance state | Combat | Storage | Combat and presentation |
| Enemy templates | Enemy authoring contract | Storage | Combat |
| Item definitions | Item authoring contract | Storage | Inventory, Combat and utilities |
| Cubes | Cube/storage domain | Storage | Cube and lifecycle systems |
| Lockers and vault | Storage/inventory domain | Storage | Core and lifecycle systems |
| World Clock | GameState/Clock | GameState atomic write | All temporal consumers |
| Astrology snapshot | Astrological Clock | Authority-local JSON | Observers and context systems |
| Comet state | Comet Cycle | Authority-local JSON | Temporal, field, observation and context systems |
| Temporal resolved state | Temporal Resolver | Authority-local JSON | World Clock and context systems |
| Comet pressure field | Comet Pressure Field | Authority-local JSON | Context and future field consumers |
| World Opportunity instances | World Opportunity Runtime | Authority-local JSON | Gate, runtime and diagnostics |
| Event History | EventHistory | Append-only JSONL | Historical queries and pattern evaluators |

Shared readability does not imply shared writability.

## 7. Character contract

`data/characters/characters.json` is a dictionary keyed by runtime user/character key.

A current character record may contain:

```text
id
name
birthdate
birth_time
tz_offset_minutes
current_room
stats
pools
bag
equipped
flags
extra
last_action
locker_tier
run_channel_id
run_seeded_channel_id
```

Minimum runtime safety is narrower than the full observed shape. GameState may ensure only the shape required to prevent a character from falling out of the world.

### Namespace rules

- `stats`, `pools`, `bag`, `equipped` and `flags` require declared system ownership.
- `extra` contains bounded system namespaces, not an unstructured permission to write anything.
- A system must not overwrite another system's `extra.*` namespace.
- Routing fields are infrastructure metadata, not character identity.
- Character records must never contain Cube session/persistence truth that belongs in the Cube store.

## 8. Room contract

`data/rooms/rooms.json` is a dictionary keyed by room ID.

Observed room fields include:

```text
title
description
image
soundcloud
exits
items
enemies
tags
ambient_events
return_echoes
era
```

Rooms define authored possibility and local world structure. They do not execute behaviour.

Enemy entries inside rooms are runtime instances. Combat may mutate instance HP and remove defeated instances without rewriting enemy templates.

`rooms_base.json` is a baseline/reset source. It is not the live room store while `rooms.json` is active.

## 9. Enemy contract

`data/enemies/enemies.json` is a dictionary keyed by enemy template ID.

Observed template fields include:

```text
hp
attack
xp
loot
```

Room enemy instances may override template values. Instance values win during resolution.

Template resolution must not erase valid room-instance overrides.

## 10. Item contract and verified violation

The Item contract expects item definitions capable of describing inventory and equipment, including fields such as:

```text
type
slot
rarity
stackable
weight
damage
defense
effects
```

Additional type-specific fields are permitted when their meaning is declared.

### Verified live-store violation

On 2026-08-31, `data/items/items.json` contained six records shaped as Thread Node definitions:

```text
triggers
title
text
prompt / reprompt
after_text
effects
```

Their IDs duplicate records in `data/thread_nodes/thread_nodes.json`.

Therefore:

- the active Item store does not conform to the Item contract;
- Thread Node shape must not be redefined as Item shape;
- the store must not be silently corrected during documentation work;
- recovery of intended Item data requires a separate runtime/data feather with backup, provenance and validation.

Until repaired, consumers must fail safely when expected item metadata is absent.

## 11. Thread Node definition contract

`data/thread_nodes/thread_nodes.json` is a dictionary containing optional `_meta` plus node definitions keyed by node ID.

`_meta` may contain:

```text
canonical
last_updated
notes
version
```

Node definitions may contain:

```text
triggers
title
text
prompt
reprompt
options
effects
after_text
```

Definitions are authored possibility. Per-character Thread Node runtime state belongs in `characters.extra.thread_nodes`.

Legacy shapes may be normalised in memory for reading. Read-time normalisation must not silently write a migration.

## 12. Cube and storage contracts

### Cubes

`data/storage/cubes.json` is a dictionary keyed by Cube ID.

Observed Cube fields include:

```text
id
cube_type
owner
integrity
flags
meta
```

Cube persistence belongs in the Cube store, not character records.

### Lockers

`data/storage/lockers.json` is a dictionary keyed by locker/owner identity.

Observed fields include:

```text
capacity
items
```

### Vault

The Efiishent vault remains a distinct persistent store. Its internal shape must not be inferred from locker shape without inspection.

## 13. World Clock contract

`data/time/world_clock.json` contains:

```text
world_time_seconds: int
version: str
```

Only the Clock/GameState authority advances `world_time_seconds`.

The persisted clock must be updated before `heartbeat.advanced` is published.

## 14. Astrology snapshot contract

`data/astrology/current_snapshot.json` contains:

```text
version: str
observed_at_utc: str
ephemeris_mode: str
zodiac: str
placements: dict
```

The snapshot records astronomical/astrological observation truth owned by the Astrological Clock. Character astrology metadata is a separate namespace.

## 15. Comet Cycle contract

`data/comet/current_state.json` contains:

```text
version: str
world_time_seconds: int
cycle_number: int
cycle_position: float
cycle_duration_world_days: int
world_seconds_until_cycle_reset: int
phase: str
pressure: float
pressure_band: str
temporal_modifier: float
temporal_band: str
```

The Comet Cycle owns this truth. Consumers may read or observe it but must not mutate it.

## 16. Temporal Resolver contract

`data/time/temporal_resolver.json` contains:

```text
version: str
era: str
effective_temporal_multiplier: float
resolved_at_world_time_seconds: int
contributors: dict
context: dict
source_versions: dict
```

`contributors` preserves the declared sources contributing to resolution.

The World Clock consumes `effective_temporal_multiplier`. It does not recompute temporal policy.

## 17. Comet Pressure Field contract

`data/fields/comet_pressure/current_state.json` contains:

```text
version: str
field: str
era: str
band: str
distribution_model: str
resolved_at_world_time_seconds: int
source: dict
samples: dict
```

Fields describe distributed conditions. They do not decide gameplay outcomes.

The current distribution may remain uniform until genuine regional physics exists.

## 18. World Opportunity contracts

### Catalogue

`data/world_opportunities/catalogue.json` contains:

```text
version: str
opportunities: list
```

The catalogue contains authored possibilities and matching conditions.

### Runtime state

`data/world_opportunities/runtime_state.json` contains:

```text
version: str
instances: list
```

The World Opportunity Runtime owns instance identity, status and lifecycle timestamps.

The catalogue does not make an opportunity active. The Runtime does not redefine catalogue authorship.

World Opportunity remains provisional implementation language pending Scenario reconciliation.

## 19. Event History contract

`data/events/event_history.jsonl` is append-only historical evidence.

Each record contains:

```text
history_version
recorded_at_utc
event
subscribers
```

`event` conforms to Event Model v4.1:

```text
event_id
event_type
occurred_at_world_time
occurred_at_utc
source
scope
payload
causation_id
correlation_id
schema_version
```

Each subscriber outcome may contain:

```text
subscriber
ok
status
detail
data
elapsed_ms
```

Event History is evidence, not gameplay state. Contract validity does not grant replay or reconstruction semantics.

## 20. Ambient, narrative and presentation data

Ambient configuration, internal narratives, HUD preferences and other presentation-oriented records remain subordinate to their domain systems.

- Configuration defines authored possibility.
- Runtime systems own selection and pacing.
- Renderers own presentation.
- Presentation data never becomes gameplay authority merely because it is persisted.

## 21. Validation

Validation may confirm:

- container type;
- required keys;
- primitive types;
- allowed enum values where declared;
- identifier presence;
- namespace ownership;
- cross-reference existence where safe.

Validation does not confirm:

- narrative quality;
- metaphysical truth;
- gameplay balance;
- constitutional coherence;
- whether an event has meaning.

A store can be valid JSON and still violate its semantic contract, as demonstrated by the current Item store.

## 22. Contract evolution

Contracts may:

- add optional fields;
- add optional namespaces;
- introduce explicit schema versions;
- define migrations;
- replace persistence technology while preserving meaning.

Contracts must not:

- silently reinterpret existing fields;
- change semantic ownership without an architectural decision;
- copy one authority's truth into another namespace without provenance;
- invalidate historical data without a declared migration;
- treat accidental current data as canonical merely because it exists.

## 23. Relationship to current documents

| Document | Responsibility |
|---|---|
| Red Book | Metaphysical/world canon |
| `TRAJECTORY_v2.1.md` | Constitutional direction |
| `ARCHITECTURE.md` | Fundamental concepts, pending ontology reconciliation |
| `RUNTIME_AUTHORITY_REGISTER_v0.3.md` | Implemented ownership and runtime boundaries |
| `EVENT_MODEL_v4.1.md` | Event, observation and historical-evidence contracts |
| `DATA_CONTRACTS_v0.5.md` | Persistent shape, paths and namespace ownership |

## 24. Required follow-up

The following are recorded follow-up feathers, not hidden work inside this contract:

1. recover and validate the intended Item store;
2. audit legacy and accidentally nested data paths before archival;
3. define retention/rotation policy for the growing Event History ledger;
4. reconcile durable World Opportunity instances with memory-only ScenarioService;
5. progressively add machine-readable validation without allowing validators to invent meaning.

## Closing principle

> **Data records truth in declared shapes. Persistence stores it. Authorities give it meaning. Accidents do not become canon merely because they are written to disk.**
