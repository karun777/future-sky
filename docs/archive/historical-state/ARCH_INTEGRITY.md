# ARCH_INTEGRITY.md
**Future Sky — Architecture Integrity Audit Notes (Canonical Snapshot)**

_Version: 0.1_  
_Last updated: 2026-01-23 (Australia/Perth)_

---

## 0. What this file is

This document is a **human-readable integrity snapshot** of the Future Sky repo’s architecture.

It is:
- **Non-speculative**
- **Boundary-focused**
- **Audit-style** (observations + risks + invariants)

It is **not**:
- A task list (see **BIKERACK.md**)
- A migration plan
- A changelog

If something in this file conflicts with:
- **DEV_STATE.md** → this file is wrong
- **JSON_CONTRACTS.md** → this file is wrong

---

## 1. Overall system health

**Current state:** coherent, tightening required (not a rewrite).

- Authority boundaries exist and are mostly respected.
- Main risk is **future drift**, not present collapse.
- Complexity is being successfully contained via `extra.*` and pure helper modules.

---

## 2. Boundary map (who owns what)

### 2.1 `fsbot/storage.py` — Persistence boundary (CRITICAL)
**Owns:**
- JSON load into memory
- JSON atomic write (tmp + replace)
- “Dumb adapter” responsibility: **no schema migration on load**

**Integrity rule:**
- Storage must remain **logic-light**. Any “helpful normalization” on load is a hidden migration and a risk.

---

### 2.2 `fsbot/state.py` — Temporal & minimal player guarantees (AUTHORITATIVE)
**Owns:**
- `data/time/world_clock.json` persistence
- World clock in-memory progression (`world_time_seconds`)
- Heartbeat lifecycle
- Era time profiles cache + lookup
- `ensure_player_records()` — **shape guarantees only**, not migration

**Integrity observation:**
- `ensure_player_records()` has become the de facto **schema stabilizer** for `characters.json`.
- This is acceptable, but **JSON_CONTRACTS.md and ensure_player_records must never drift**.

---

### 2.3 `fsbot/cogs/*` — Gameplay behaviors (SUPPORTING, stateful at runtime)
**Owns:**
- Command behaviors
- In-memory runtime state for loops (e.g. combat per-room tasks)
- Narrow, explicit persistence writes (only where specified)

**Integrity rule:**
- Cogs must not silently introduce new canonical JSON fields without updating JSON_CONTRACTS.md (or confining them to `extra.*`).

---

### 2.4 `fsbot/utils.py` — Pure helpers (SUPPORTING)
**Status:** stable and appropriately pure.

**Integrity rule:**
- No storage calls, no Discord imports, no state access.
- All mutations must be explicit (caller-provided dicts only).

---

## 3. Data model integrity notes

### 3.1 `characters.json` — Canonical spine + `extra.*` containment
**Healthy pattern:**
- Core runtime-critical fields are present.
- Rich/experimental systems are correctly contained in `extra.*`.

**Risk:**
- Characters schema density will grow; keep “core” minimal and stable, and prefer `extra.*` for expansion.

---

### 3.2 Astrology (`extra.astrology`) — Data-first, assumption-logged
**Status:** excellent foundation.

**What’s good:**
- Deterministic and reproducible
- Assumptions recorded (time/tz)
- JSON-safe output
- Planetary placements include full major planet set (Sun..Pluto) in v0

**Integrity rule:**
- Astrology should remain **data**, not authority:
  - stored under `extra.astrology`
  - sampled by mechanics only via explicit systems (layers/resolver/UI)
  - never silently affects core stats without a declared, versioned mechanic

---

### 3.3 Chakra / Mana pools — not yet canonical
**Current reality:**
- Chakra concept is present in lore and intended mechanics.
- No canonical JSON contract for mana pools exists yet.

**Integrity recommendation:**
- Treat chakra pools as **resources**, not base stats:
  - prefer `extra.status` or `extra.resources`
  - render them as “signals” (visible values) before allowing spend/regeneration rules
  - avoid contaminating `stats` with non-d20 resources

---

## 4. Modifier system integrity (`layers.json` + `resolver.py`)

### 4.1 `layers.json`
**What it is becoming (healthy):**
- A meta-system for controlled interpretation:
  - tuning layers
  - visibility labels
  - hooks declarations

**Integrity rule:**
- layers.json must never become a dumping ground for executable logic.
- It should declare intent and parameters; the resolver applies constrained ops.

---

### 4.2 `fsbot/resolver.py`
**Healthy properties:**
- Pure, no I/O
- Fail-closed selector/condition handling
- Safe dotted-path writes (won’t crash on non-dicts)
- Pool clamping after each layer and at end

**Integrity rule:**
- Resolver must remain dependency-light and deterministic.
- Unknown selector/comparator keys must remain fail-closed.

---

## 5. Enemy system integrity (templates vs instances)

**Status:** structurally sound.

- `enemies.json` = templates (reusable)
- `rooms.json` = instances (per-room, per-spawn overrides)
- “effective view” merge is non-persisted and used only for runtime display/stats

**Critical persistence rule (already aligned):**
- Combat may persist only:
  - instance `hp` updates
  - instance removal on defeat
- Combat must not persist template-only fields (e.g. `type`) into `rooms.json`.

---

## 6. Router/run-channel integrity

**Pattern observed:**
- Run channels are ephemeral at runtime but `run_channel_id` is persisted for continuity.

**Integrity rule:**
- Router should remain the sole owner/writer of routing fields:
  - `run_channel_id`
  - `run_seeded_channel_id` (if used)

---

## 7. System-level integrity insight (keep this triangle)

Future Sky is evolving into a stable model:

- **Core = physics** (minimal canonical data + invariants)
- **Extra = perception** (rich, evolving player/world facets)
- **Layers = interpretation** (controlled modifiers and tuning)

Protect this triangle and the system scales without myth-bloat.

---

## 8. Immediate integrity risks (observations only)

- **Drift risk:** JSON_CONTRACTS.md vs `ensure_player_records()` / live usage.
- **Scope creep risk:** pushing chakra/mana into `stats` instead of `extra.*`.
- **Logic creep risk:** layers.json accumulating mechanics rather than declarative modifiers.
- **Ownership creep risk:** cogs adding persisted fields outside `extra.*` without contract updates.

---

**End of ARCH_INTEGRITY.md**
