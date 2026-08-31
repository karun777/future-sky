# BIKERACK.md
**Future Sky — Canonical Task Register & Handoff Primer**

_Version: 1.7_  
_Last updated: 2026-01-23_

---

## 0. What this file is

This file answers **one question only**:

> **“What do we work on next?”**

It is intentionally minimal.

This file exists to:
- Prevent scope drift
- Provide a single authoritative next step
- Enable clean handoff to future R3GPT / contributors

This file is **not a log**.  
Completed work does **not** remain here.

If a task is not written here:
- It is not active
- It should not be started

---

## 1. Authority & relationship to other docs

This file sits alongside:

- **DEV_STATE.md** — runtime truth, operational rules, reset ritual, feathering
- **JSON_CONTRACTS.md** — data authority

**Rule:**  
If this file conflicts with either of the above, **this file is wrong** and must be corrected.

---

## 2. How to use this file (MANDATORY)

- Only **active work** is listed
- Tasks are ordered top → bottom
- Work proceeds **one task at a time**
- Nothing new is added mid-task

When a task is completed:
- Remove it entirely
- Update the “Last updated” line

No checklists.  
No history.  
No commentary.

---

## 3. CURRENT WORK (ONLY)

### 3.1 Repository audit closure & contract alignment (v0)

**Goal:**  
Close the repo-wide audit by locking contracts, clarifying ownership, and removing ambiguity discovered during system mapping.

This task exists because **we just finished a deep scan** of:
- Runtime architecture
- State vs storage boundaries
- Combat + resolver integration
- Astrology ingestion
- Pools / modifiers / layers

**Boundaries:**
- NO new gameplay features
- NO balance tuning
- NO narrative expansion
- NO migrations

This is a **consolidation task only**.

**Includes (explicit):**
- Refactor `layers.json` into a clean, contract-aligned, non-ad-hoc set of modifier layers
  - Preserve dev/test layers
  - Remove ambiguity in selector / scope usage
  - Make layers *interesting but disciplined* (signals, not power creep)
- Finalise `JSON_CONTRACTS.md` to fully cover:
  - Astrology (`extra.astrology`, all planets)
  - Mana / spirit pools (`pools` contract)
  - Resolver expectations
- Validate that:
  - `fsbot/resolver.py`
  - `CombatCog`
  - `AstroCog`
  - `GameState.ensure_player_records`
  all conform to the written contracts (no code changes unless strictly required)
- Produce a stable mental model / handoff state for the repo

**Explicitly excludes:**
- Character creation rewrite
- Astrology → stat math
- Chakra regen logic
- Skill systems
- Thread node expansion

---

## 4. QUEUED (NOT ACTIVE)

### 4.1 Rewrite character creation & substrate binding (v0)

(Previously 3.1 — deliberately deferred until audit is closed)

---

### 4.2 Astrology → stat flavor pass
- Soft narrative modifiers only
- Educational, not optimization-driven

---

### 4.3 Chakra mana pool spend / regen rules (v0)
- Use existing chakra mapping
- No cross-chakra conversions

---

### 4.4 Skill Expression Layer continuation
- Capabilities → commands
- Expression, not progression

---

## 5. Explicit non-goals

- Feature expansion without architectural need
- Premature balance tuning
- UI design
- Performance optimisation
- Multiplayer scaling work
- Retroactive migration logic
- Deep astrology (houses, aspects, rising)

---

## 6. Handoff rule (READ FIRST)

If you are opening this file:

1. Open **DEV_STATE.md**
2. Open **JSON_CONTRACTS.md**
3. Return here
4. Work **only** on section **3.1**

Do not invent work.  
Do not skip ahead.

---

**End of BIKERACK.md**

