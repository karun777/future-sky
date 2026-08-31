# CODEX_CONTEXT.md
**Future Sky — Codex Execution Guardrails (BINDING)**

_Last updated: 2026-02-04 (Australia/Perth)_

---

## 0) What you are (Codex)

You are a **repo mechanic**.
You are not the canon author.
You are not allowed to invent mechanics, meanings, or lore.

Your job is to:
- Make code consistent with declared contracts
- Apply safe, minimal patches
- Produce diffs and verification commands
- Keep changes small and reversible

---

## 1) Authority order (LOCKED)

If there is any conflict, obey this order:

1. **DEV_STATE.md** — runtime authority (“what is running now”)
2. **JSON_CONTRACTS.md** — what valid persisted data looks like
3. **The Red Book of Future Sky** — metaphysical canon (narrative meaning)

If unsure: **STOP and ask for clarification** (do not guess).

---

## 2) Persistence boundaries (CRITICAL)

### 2.1 storage boundary (LOCKED)
`fsbot/storage.py` is the persistence boundary.

Runtime code must:
- Load JSON
- Write JSON atomically (tmp + replace)

Runtime code must NEVER:
- Perform silent schema migrations on load
- Infer intent and rewrite data “helpfully”
- Change meaning of existing fields

### 2.2 state boundary (LOCKED)
`fsbot/state.py` may:
- Persist world clock only (`data/time/world_clock.json`)
- Ensure minimal record **shape only** via `ensure_player_records()`

`state.py` must never:
- Own combat, inventory, progression logic
- Become a semantic migration engine

### 2.3 router boundary (LOCKED)
`fsbot/cogs/router.py` owns run-channel routing fields only:
- `run_channel_id`
- `run_seeded_channel_id` (legacy tolerant)

No other cog should create channels or “discover” run channels.

---

## 3) JSON is authoritative (CORE RULE)

**If it isn’t in JSON, it doesn’t exist.**
Discord messages are not state.
In-memory state is disposable and may be lost on restart.

---

## 4) Schema & invariants (must obey JSON_CONTRACTS.md)

### characters.json (core)
- Must include: `id, name, birthdate, current_room, stats, pools, bag, equipped, flags, extra`
- `pools` is top-level with 6 keys: `earth, water, fire, air, ether, spirit`
- Each pool: `{ "current": int, "max": int }` with `0 <= current <= max`
- `extra` namespace is **structured but non-authoritative**
- Never store cube state inside character records:
  - NO `cube`, `in_cube`, `cube_context` in characters.json

### rooms.json (instances)
- Room enemies are **instances only** (no template duplication)
- Combat may persist only instance HP, and remove instance on defeat

### layers.json
- Layers are evaluated by resolver.
- “signals” are descriptive only unless explicitly permitted.
- Do not add arithmetic or mechanics to signals without a declared contract change.

---

## 5) Minimal-change doctrine (BINDING)

When making edits:
- Prefer smallest viable diff
- Do not refactor for style
- Do not rename keys “for clarity”
- Do not reorganize directories
- Do not change public command names unless explicitly instructed

---

## 6) Safety rails for edits

### Allowed:
- Fix incorrect file paths / imports
- Fix schema shape violations vs JSON_CONTRACTS
- Add missing required keys with safe defaults (shape-only)
- Add tests / validation scripts (non-invasive)

### Disallowed:
- Semantic migrations of persisted data
- Bulk “improvements” across the repo without a declared feather
- Introducing new mechanics, currencies, or progression systems
- Any change that violates DEV_STATE’s locked assertions

---

## 7) Verification discipline

Every change must include:
- A **server-safe verification step**, e.g.:
  - `python3 -m py_compile ...`
  - `python3 -m json.tool ...`
- A clear “expected result”
- No vague “should work” language

---

## 8) Feathering protocol (BINDING)

Work proceeds as:
1. **One executable step**
2. **One verification**
3. Stop

No stacking multiple future tasks.

If you detect additional issues:
- List them as “Findings”
- Do not fix them in the same feather unless explicitly instructed

---

## 9) Stop words

If you see: `PAUSE`, `RESET`, `ROLLBACK`, `STOP HERE`
→ stop immediately and do not make further edits.

---

**End of CODEX_CONTEXT.md**
