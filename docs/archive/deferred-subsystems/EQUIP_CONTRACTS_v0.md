# EQUIP_CONTRACTS_v0.md
**Future Sky — Equipment & Equipping Contracts (v0)**

_Version: 0.0_
_Last updated: 2026-02-03 (Australia/Perth)_

---

## 0. What this document is

This document defines **how equipping works** in Future Sky.

It specifies:
- Equip slot model
- Slot ownership rules
- Handedness rules
- Eligibility and restriction contracts
- Canonical equipped state shape

This document is:
- **Canonical**
- **Contract-first**
- **MajorMUD-inspired**
- **System-level**

This document is **not**:
- A combat balance guide
- A stat modifier list
- A UI or command spec
- A crafting or upgrade system

If equip behavior contradicts this document, **the runtime is wrong**.

---

## 1. Core equip principle

> **Equipping is the act of binding an item to a character slot.**

Only **equipment-capable items** may be equipped.

Equipping:
- is reversible (unless explicitly restricted)
- does not consume the item
- does not change item identity
- only changes **where the item is bound**

---

## 2. What can be equipped

An item may be equipped if and only if:

1. `item.type == "equipment"`
   *(or `artifact` with an explicit equip block)*

2. The item declares an `equip` capability block.

3. The character satisfies all equip requirements.

All other item types are **never equip-capable** in v0.

---

## 3. Equip slots (v0 canonical)

### Body slots
- `head`
- `neck`
- `chest`
- `back`
- `hands`
- `waist`
- `legs`
- `feet`

### Accessory slots
- `ring_1`
- `ring_2`
- `trinket`

### Hand slots
- `main_hand`
- `off_hand`

These slots are **fixed identifiers**.
No dynamic or ad-hoc slots are permitted in v0.

---

## 4. Slot occupancy rules

1. **One item per slot.**
2. A slot may be empty (`null`) or occupied by one item id.
3. An item may occupy:
   - one slot, or
   - multiple slots (e.g. two-handed weapons).
4. If any required slot is unavailable, equip fails unless explicitly overridden by a swap operation.

---

## 5. Handedness & weapon rules (MajorMUD core)

### Hand usage
- Weapons declare `hands_required: 1 | 2`
- `hands_required = 2` occupies both `main_hand` and `off_hand`
- `hands_required = 1` occupies one hand only

### Off-hand eligibility
- Shields may occupy `off_hand` only
- One-handed weapons may occupy either hand
- Dual-wielding is allowed if both items are one-handed and no restrictions block it

### Conflicts
- If an item occupies `off_hand`, equipping a two-handed weapon must unequip it first (explicitly or via swap).

---

## 6. Equip capability block (item definition)

Items that can be equipped must define:

```json
"equip": {
  "allowed_slots": ["main_hand", "off_hand"],
  "hands_required": 1,
  "unique_equipped": false,
  "requirements": {},
  "restrictions": {}
}
