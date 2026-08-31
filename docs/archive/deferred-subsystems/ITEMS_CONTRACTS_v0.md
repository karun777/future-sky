# ITEMS_CONTRACTS_v0.md
**Future Sky — Item System Contracts (v0)**

_Version: 0.0_
_Last updated: 2026-02-03 (Australia/Perth)_

---

## 0. What this document is

This document defines **what an item is** in Future Sky.

It specifies:
- Item ontology
- Item types and capabilities
- Equip rules (structure only)
- Container rules
- Binding and portability rules

This document is:
- **Canonical**
- **Contract-first**
- **Definition-level**

This document is **not**:
- A gameplay balance guide
- A crafting system
- A combat spec
- An inventory UX spec
- A code implementation

If runtime behavior contradicts this file, **the runtime is wrong**.

---

## 1. Core definition

> **An item is a persistent, ownable entity that can exist independently of a character, room, or system.**

If something:
- can be owned,
- can be transferred or stored,
- can persist while a player is offline,

…it is an item.

---

## 2. Explicit non-items

The following are **not items** and must never be represented as such:

- Cubes (contexts / constructs)
- Cube sessions (ephemeral overlays)
- States (buffs, debuffs, flags)
- Skills / commands
- Permissions (unless externalised as access items)
- Knowledge (unless externalised as data objects)
- Rooms
- World Anchors (structures)

These systems may **interact with items**, but are not items themselves.

---

## 3. Item type taxonomy (v0)

Every item **must** declare a `type`.

Canonical item types:

- `equipment`
- `consumable`
- `tool`
- `access`
- `container`
- `data`
- `valuable`
- `artifact`
- `vehicle`
- `structure_kit`

### Type notes
- `container` is a capability-bearing item (storage interface).
- `vehicle` items are ownable but not inventory-carriable.
- `structure_kit` represents a deed / kit that creates or upgrades a World Anchor.
- World Anchors themselves are **never items**.

---

## 4. Portability contract

Each item must declare a `portability` value:

- `portable` — carriable in inventory
- `fixed` — exists in world or anchor, not carriable
- `vehicle_scale` — mobile, but not inventory-carriable

Portability governs **where an item may exist**, not who owns it.

---

## 5. Binding contract

Each item must declare a `bind_policy`:

- `unbound`
- `bind_on_acquire`
- `bind_on_use`
- `bound_to_anchor`
- `bound_to_cohort`
- `bound_to_timeline`

Binding affects **transfer**, not existence.

---

## 6. Transfer policy

Each item must declare a `transfer_policy`:

- `tradeable`
- `restricted`
- `not_transferable`

Transfer policy is enforced at interaction time, not at definition load.

---

## 7. Equipment & equipping (structure only)

Only items with `type = equipment` (and optionally `artifact`) may be equipped.

### Equip slots (v0 canonical)
- `head`
- `neck`
- `chest`
- `back`
- `hands`
- `waist`
- `legs`
- `feet`
- `ring_1`
- `ring_2`
- `trinket`
- `main_hand`
- `off_hand`

### Equip rules
- Equipment declares which slots it may occupy.
- Weapons declare `hands_required` (1 or 2).
- Two-handed items occupy both `main_hand` and `off_hand`.
- Only one item may occupy a slot at a time.

No equip logic is permitted outside these rules.

---

## 8. Containers (storage capability)

Items with `type = container` may expose a `container` capability block.

### Container invariants
- Containers are items.
- Containers do **not** store contents directly.
- Container contents live in a separate storage ledger.
- Containers may be portable or fixed.

### Container capability fields
- `capacity_units`
- `max_item_stacks`
- `allowed_types`
- `disallowed_tags`
- `is_world_container`
- `anchor_id` (required if `is_world_container = true`)

World Anchors may **expose** containers, but never contain items themselves.

---

## 9. Cube relationship (descriptive only)

Items may declare cube affinity:

- `cube_agnostic`
- `cube_aware`
- `cube_bound`
- `cube_forged`

These flags are **descriptive**, not authoritative logic.

> **Cubes are contexts, never items.**

---

## 10. World Anchor relationship

Items may declare world-anchor affinity:

- `placeable` — can place/create an anchor (typically `structure_kit`)
- `installable` — can be installed into an anchor (locker, bench, module)

Items do not own anchors; anchors reference items.

---

## 11. Required fields per item definition

Every item definition must include:

- `id`
- `name`
- `type`
- `rarity`
- `stackable`
- `portability`
- `bind_policy`
- `transfer_policy`

Optional blocks:
- `equip`
- `use`
- `container`
- `access`
- `value`
- `cube_affinity`
- `world_anchor_affinity`
- `presentation`
- `tags`
- `notes`

---

## 12. Validation rules (v0)

- Malformed item definitions are ignored.
- No silent migration is permitted.
- Unknown enum values invalidate the item.
- Definitions must never auto-correct.

---

## 13. Design axioms (non-negotiable)

1. **Items are things, not contexts.**
2. **Containers are items, contents are separate.**
3. **World Anchors are not items.**
4. **Equipping is slot-based, not free-form.**
5. **No silent migration. Ever.**

---

## 14. Authority & scope

**Authority rank:** Canonical (definitions)
**Applies to:** `items.json`, inventory systems, equip logic, container exposure
**Does not own:** balance, combat math, crafting, UI

If this document changes:
- version bump
- date bump
- explicit rationale

Otherwise: leave it alone.

---
