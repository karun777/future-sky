# Future Sky – DEV_STATE v6.0

## Last Updated

2026-07-20

---

# Purpose

DEV_STATE records the current operational reality of Future Sky.

It answers one question:

> What is true right now?

This document is intentionally present-tense and is expected to become outdated.

Related documents:

- `DEV_ENVIRONMENT_SETUP.md` — how the environment is built and operated
- `OPERATIONS.md` — routine administration and recovery
- `TRAJECTORY.md` — where Future Sky is heading
- `CHANGELOG.md` — how the system arrived here
- `EVENT_MODEL.md` — event architecture and runtime contracts
- `SCENARIO_RUNTIME.md` — scenario execution model
- `SCENARIO_AUTHORING.md` — scenario authoring conventions
- `SCENARIO_STATE_CONVENTIONS.md` — scenario state rules
- `EVENT_CATALOGUE.md` — canonical event vocabulary

---

# Executive Summary

Future Sky is operational.

The Discord world is live.

The public website is live at `https://future-sky.net`.

The current Neptune Lounge server remains stable and usable, but a major infrastructure limitation has now been confirmed:

> Debian 12 is installed as a 32-bit `i386` userspace on 64-bit-capable hardware.

This does not presently prevent Future Sky from operating, but it blocks modern .NET deployment and constrains future services.

The discovery occurred while preparing to run MajorMUD through MBBSEmu.

The correct response is not an in-place architecture conversion.

The current strategic priority is now:

> Inventory, back up, verify, simplify, and commission Neptune Lounge v2 on 64-bit Debian.

The existing server remains the fallback position until the rebuilt system has passed a formal service-by-service validation.

---

# Current Era

## The Coherence and Runtime Era

Future Sky has moved beyond proving that individual systems can exist.

The present work is to make those systems operate as a coherent world.

Current development focuses on:

- event-driven runtime architecture
- presence as a dedicated service
- scenario execution
- thread node integration
- living-world behaviour
- authoring conventions
- operational reproducibility
- removal of accidental infrastructure complexity

The onboarding rite remains important, but is no longer the only active centre of development.

The larger question is now:

> Can Future Sky move as one world rather than as a collection of features?

---

# Operational Reality

## Infrastructure

### Current Server

**Host:** Neptune Lounge  
**Operating system:** Debian GNU/Linux 12 (bookworm)  
**Installed architecture:** `i386` / `i686`  
**CPU capability:** 32-bit and 64-bit  
**Status:** Operational, stable, pending planned replacement

Confirmed:

```text
uname -m                 → i686
dpkg --print-architecture → i386
CPU op-mode(s)           → 32-bit, 64-bit
```

The hardware can run a 64-bit operating system.

The current installation cannot provide the clean modern .NET environment required by MBBSEmu.

### Current Network and Access

- NBN FTTP operational
- Neptune Lounge connected through the household network
- Reserved LAN address previously recorded as `192.168.0.148`
- `future-sky.net` resolves to Neptune Lounge
- HTTPS served through nginx and Let's Encrypt
- SSH administration uses port **777**
- SSH key authentication enabled
- SSH password authentication disabled
- UFW operational
- Fail2Ban operational
- console-only boot enabled

The previously recorded public IPv4 address must not be treated as permanent. Confirm it during the infrastructure audit.

### Current Service State

Known operational services include:

- Future Sky Discord bot
- nginx
- Let's Encrypt certificate handling
- PostgreSQL
- Redis
- JSON persistence
- systemd service management
- Lavalink

Not every operational service is necessarily required in Neptune Lounge v2.

The migration audit must distinguish between:

```text
required
useful
experimental
legacy
redundant
unknown
```

---

# Neptune Lounge v2

## Status

**Commissioning planned. Not yet begun.**

## Reason

The rebuild is required because the current operating system is 32-bit.

It is also an opportunity to remove infrastructure that no longer earns its place.

## Migration Principle

The current server is not to be altered destructively until:

1. the system has been inventoried
2. all important data and configuration have been backed up
3. the backups have been verified as readable
4. the intended Neptune Lounge v2 architecture has been documented
5. the restoration sequence has been written
6. rollback expectations are understood

## Preferred Strategy

A clean 64-bit installation is preferred over an in-place `i386` to `amd64` conversion.

Likely target:

- Debian 13 amd64, subject to final compatibility review

## Commissioning Sequence

```text
Inventory
↓
Backup
↓
Backup verification
↓
Redundancy audit
↓
Rebuild plan
↓
Fresh 64-bit Debian
↓
Secure remote access
↓
Core services
↓
Future Sky restore
↓
Service validation
↓
MBBSEmu and MajorMUD
↓
Retire old installation
```

---

# Backup Position

## Objective

Create a fallback position strong enough that the current Neptune Lounge can be restored or reconstructed without relying on memory.

## Backup Scope

The inventory must locate and preserve at least:

- Future Sky source code
- JSON game state
- room, character, enemy, item and thread node data
- scenario files and authoring documents
- website files
- world assets
- environment files and secret locations
- PostgreSQL databases, roles and schema
- Redis configuration if retained
- nginx configuration
- Let's Encrypt material or a documented certificate reissue path
- SSH server configuration
- authorised keys
- UFW rules
- Fail2Ban configuration
- systemd unit files
- Lavalink configuration if retained
- custom scripts
- cron jobs and timers
- package inventory
- ownership and permissions
- symlinks
- operational documentation

Secrets should not be copied into ordinary documentation.

Documentation should record where secrets live and how they are restored.

## Verification Standard

A backup is not considered complete merely because an archive exists.

It must be:

- listable
- readable
- stored outside the server being rebuilt
- accompanied by checksums
- sufficient to restore critical state
- tested through selective extraction or restoration

---

# Runtime Architecture

## Discord Bot

**Status:** Operational

The bot is now organised around an increasingly explicit event-driven architecture.

Recent work includes:

- event publication and subscriber tracing
- world heartbeat and accelerated world time
- extraction of presence concerns from ambient behaviour
- navigation publishing `character.entered_room`
- thread nodes subscribing to room-entry events
- clearer separation between runtime services and cogs

The bot currently loads a broad collection of cogs, including navigation, ambient systems, thread nodes, HUD, narration, activity, combat, cubes, attunement and related abilities.

## Presence Service

**Status:** Extracted and operational

Presence is no longer intended to be an accidental responsibility of ambient systems or direct iteration over character storage.

The emerging rule is:

> Systems ask the presence service who is present. They do not independently reconstruct presence from persistence.

This separation is foundational for:

- room population
- ambient behaviour
- event targeting
- scenario participation
- social cycles
- future multi-interface presence

## Event Framework

**Status:** Phase II active

The event framework is now a central runtime spine.

Observed runtime events include:

- `character.entered_room`
- event probes and trace logging
- heartbeat-driven world time progression

The direction is toward explicit contracts between:

```text
emitters
events
subscribers
state transitions
presentation
```

## Thread Nodes

**Status:** Operational and actively integrated

Thread nodes currently support:

- room-entry triggers
- once-per-character behaviour
- command unlock conditions
- active node guards
- pending answers
- event completion tracking
- presentation suppression while another node is active

Thread nodes sit alongside scenarios as focused, authored encounter structures.

They are not being replaced by the scenario framework.

The intended relationship is:

```text
Thread node
    focused encounter, lesson, choice or narrative knot

Scenario
    wider orchestration across roles, events, state and time
```

## Scenario Framework

**Status:** Design and authoring framework established; implementation remains in progress

Current canonical documents include:

- `SCENARIO_AUTHORING.md`
- `EVENT_CATALOGUE.md`
- `SCENARIO_STATE_CONVENTIONS.md`
- `SCENARIO_RUNTIME.md`

The framework is intended to support:

- chapters
- scenes
- role assignment
- player and NPC substitution
- timed transitions
- world-state conditions
- event-driven progression
- thread node participation
- local and global consequences

The system should orchestrate existing world mechanisms rather than becoming a parallel game engine.

---

# World Time

**Status:** Operational

The heartbeat advances Future Sky world time.

Current observations confirm:

- active era: Manzo
- configurable time multiplier
- persisted clock state
- regular heartbeat logging
- event framework participation

World time is expected to become a shared authority used by scenarios, ambient systems, social cycles, astrology and world moments.

---

# Persistence

## Current Gameplay Authority

**Primary gameplay authority:** JSON

JSON currently remains the clearest and most active source of gameplay state.

## PostgreSQL

**Status:** Operational, role under review

Substantial database work was completed previously.

The migration audit must determine:

- what databases exist
- what schemas and tables contain meaningful data
- what code currently reads or writes PostgreSQL
- whether any data is authoritative
- whether PostgreSQL should be restored immediately, deferred, or simplified

PostgreSQL must not be discarded merely because its present role is unclear.

It must first be dumped, inspected and documented.

## Redis

**Status:** Operational, role under review

Redis is not presently established as a core gameplay authority.

Its active use must be verified before it is included in Neptune Lounge v2.

## Persistence Doctrine

Clarity over complexity.

A persistence system stays only when its responsibility is explicit.

---

# Audio and Lavalink

## Lavalink

**Status:** Operational, retention undecided

Lavalink has successfully connected and supported room audio work.

However, its place in the rebuilt environment should be reconsidered.

Questions for the audit:

- Is Lavalink used by the current player experience?
- Is it required for SoundCloud or room audio?
- Does the bot depend on it at startup?
- Would a simpler audio path be sufficient?
- Is Java being retained only for Lavalink?

Lavalink should be restored only after its current value and dependency chain are understood.

---

# Website and Public World Surface

## Website

**Status:** Operational

Canonical URL:

- `https://future-sky.net`

Known public surfaces include:

- `index.html`
- `signal.html`
- `chamber.html`
- `love.html`
- `feed7.html`
- shared assets

The website remains part of the gameworld rather than a separate marketing layer.

## Feed7

**Status:** Experimental and active as a concept

Feed7 is intended as a porous broadcast surface connecting Future Sky, music, video, performance and external observation.

Its infrastructure should be inventoried, but experimental media tooling does not need to block the core server rebuild.

---

# Onboarding

## Canonical Path

```text
Pod
↓
Signal
↓
Chamber
↓
LOVE
↓
Neptune Lounge
```

## Current Status

- Pod arrival exists
- arrival thread nodes exist
- character creation and persistence operate
- Signal operates as a public discovery surface
- Chamber remains partial
- LOVE remains partial
- full unassisted public onboarding has not yet been conclusively validated

The Arrival Rite remains an important milestone, but current infrastructure and runtime work temporarily take precedence.

---

# MajorMUD and MBBSEmu

## Status

**MajorMUD source files located and extracted.**  
**MBBSEmu deployment blocked by current 32-bit operating system.**

The located MajorMUD distribution contains the original module files, including:

- `WCCMMUD.DLL`
- `WCCMMUD.MSG`
- `WCCMMUD.MDF`
- `WCCMMUD.NOT`
- `WCCMMUD.RLN`
- related help, text, update and module archives

The main DLL has been identified as:

```text
MS-DOS executable
NE for MS Windows 3.x
```

This is consistent with the class of original MajorBBS/Worldgroup module MBBSEmu is designed to execute.

The intended initial deployment mode is DEMO until the original activation information is recovered.

Preferred future architecture:

```text
Debian amd64
└── MBBSEmu
    └── Original MajorMUD modules
        └── Telnet clients / MegaMMUD
```

MajorMUD is not the reason for the server rebuild.

It exposed the architectural limitation at a useful moment.

---

# Operating Workstations

## MacBook Pro

**Status:** Operational again

The MacBook Pro was previously treated as dead, but has since been repaired and returned to service.

Confirmed uses include:

- SSH access
- SCP deployment
- local editing
- development workflow

Operating documents must no longer describe the MacBook Pro as unavailable.

## Windows Workstation

**Status:** Operational

The Windows workstation remains useful for:

- server administration
- OBS
- browser-based operations
- possible MajorMUD client access
- local media and production work

Neither workstation should be the sole repository of critical server state.

---

# Current Risks

## 32-bit Operating System

The current server is constrained by its `i386` installation.

Mitigation:

- planned clean amd64 rebuild
- preserve current installation until validation is complete

## Backup Confidence

A formal, verified full-server recovery position has not yet been established.

Mitigation:

- inventory
- external backup
- checksums
- restoration testing

## Infrastructure Redundancy

PostgreSQL, Redis, Lavalink, Java and other services may contain useful work, accidental complexity, or both.

Mitigation:

- audit before removal
- preserve before simplifying
- restore only with explicit purpose

## Single-Operator Dependency

Operational knowledge remains concentrated in one person and across multiple evolving documents.

Mitigation:

- authoritative operations manual
- commissioning record
- repeatable installation process
- documented secret locations
- tested recovery procedure

## Documentation Drift

Several documents still describe the July 1 environment and earlier assumptions.

Mitigation:

- update documentation as part of Neptune Lounge v2
- define precedence between operational documents

## Household Network Instability

Recent reports indicate intermittent Wi-Fi problems affecting multiple household devices.

This may be unrelated to the server itself but could affect administration and public availability.

Mitigation:

- simplify extender topology during diagnosis
- distinguish LAN/Wi-Fi failure from server failure
- retain wired networking for Neptune Lounge where possible

---

# Immediate Mission

## Establish the Fallback Position

Before further expansion:

1. inventory the current server
2. capture all meaningful state
3. back up outside Neptune Lounge
4. verify the backup
5. document what is retained
6. identify redundancy
7. design Neptune Lounge v2
8. rebuild only after sign-off on the recovery position

---

# Next Milestones

## Milestone 1 — Current-State Inventory

Produce a machine-readable and human-readable record of:

- disks and filesystems
- architecture and operating system
- packages
- systemd services
- listening ports
- firewall rules
- users and groups
- cron jobs and timers
- application directories
- databases
- web configuration
- SSL configuration
- environment files
- custom symlinks
- ownership and permissions

## Milestone 2 — Verified Backup

Create and validate a backup stored away from the server.

## Milestone 3 — Redundancy Decision Record

For every major service, decide:

```text
retain now
retain later
archive only
replace
remove
```

## Milestone 4 — Neptune Lounge v2 Build Specification

Write the exact installation and restoration sequence.

## Milestone 5 — 64-bit Commissioning

Install, secure, restore and validate the new server.

## Milestone 6 — MajorMUD

Deploy MBBSEmu and prove an original MajorMUD module can be reached through Telnet.

---

# Success Condition

Neptune Lounge v2 is commissioned only when:

```text
SSH works securely
HTTPS works
Future Sky website loads
Discord bot runs
character state persists
navigation works
thread nodes trigger
event framework operates
world time advances
assets resolve
backups run
a restore test succeeds
MajorMUD can be reached
```

The old installation remains the fallback until this condition is met.

---

# Closing Observation

The discovery of the 32-bit installation is not merely a technical inconvenience.

It has revealed the right moment to establish a recoverable foundation.

Future Sky now has enough living machinery that infrastructure decisions matter.

The objective is not to preserve every service merely because it exists.

The objective is to preserve everything meaningful, understand every dependency, remove accidental complexity, and rebuild with confidence.

The current server is alive.

The next task is to make it reproducible.

---

**End of Document**
