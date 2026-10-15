# Feather 33 — Neptune Lounge Gameplay Integration

**Date:** 2026-10-15  
**Status:** Initial source audit and coordinated implementation plan  
**Scope:** Inventory, item use, equipment, visual fit/avatar, combat and first-night player experience. **No deployment or live-state mutation.**

## Objective

Make the first playable journey coherent across the same character: awaken, examine possessions, equip and use items, see the current fit, navigate the Lounge, encounter danger, recover and choose a first venture beyond. Develop the subsystems in parallel **with shared contracts and integration tests**, not as isolated demonstrations.

## Source-verified baseline

| Track | Evidence | Assessment / gap |
|---|---|---|
| Inventory | `bot/fsbot/cogs/core.py` provides `!inventory` / `!inv`; character bag and equipped slot maps persist in `data/characters/characters.json` | Existing command and persistence. Audit display, item lookup, acquisition and removal in isolated tests |
| Equipment | CoreCog provides `!equip`, `!unequip`; `data/items/items.json` has equip metadata | Existing commands. Verify slot constraints, swaps, two-handed equipment, equipped/bag arithmetic and effects in combat |
| Item use | `data/items/items.json` includes consumables such as Med Patch and Tin Rations, with empty `effects` arrays | No `!use` command identified in the inspected CoreCog command decorators; inspect all command registration before declaring this missing |
| Character sheet and HUD | CoreCog provides `!character_sheet` / `!sheet`; `bot/fsbot/cogs/hud.py` provides `!hud`, `!hud_on`, `!hud_off`, `!hud_state` | Existing text/embeds. Need a verified avatar presentation and equipment-to-appearance mapping |
| Combat | `bot/fsbot/cogs/combat.py` provides `!combat`/`!draw`/`!engage`, `!attack`, `!disengage`/`!flee`, `!combat_status`/`!status`; uses room enemy instances and resolver-derived modifiers | Existing turn-based loop with persisted enemy HP/defeat. Test encounter safety, pacing, retreat, rewards, death/respawn and multiplayer effects offline |
| World traversal | `bot/fsbot/cogs/navigation.py` handles movement, room rendering and entry events; `data/rooms/rooms.json` defines Lounge and adjoining rooms | Trace first-night transitions, return path, encounters and media delivery |
| Items and equipment contracts | `docs/archive/deferred-subsystems/ITEMS_CONTRACTS_v0.md`, `EQUIP_CONTRACTS_v0.md` | Archived documents are design evidence, **not automatically current authority**. Reconcile against current runtime and canonical documents before any migration |

## Contract hazards requiring early tests

1. **Equip slot divergence.** Archived contract and character state use `chest`, `back`, `waist`, `ring_1`, `ring_2`, `trinket`; `bot/fsbot/utils.py` declares `body`, `accessory1`, `accessory2`. Determine which functions actually consume each list before altering slots.
2. **Item taxonomy divergence.** Archived item contract expects `equipment` with an equip block; recovered current definitions include `weapon`, `armor`, `accessory` and `trinket`. Do not bulk-convert existing player possessions.
3. **Consumable effects.** Recovered consumables may have empty effects. Do not present healing or nourishment as implemented without tests.
4. **Stateful combat.** Enemy HP and character health are persisted. Never run encounter trials against live rooms or players.
5. **Visual identity.** The repository has place art, but no verified wearable-layer renderer or generated avatar pipeline has yet been identified. Choose a representation only after checking the available UI and asset paths.

## Parallel tracks with integration contracts

### A — Inventory and item use

Audit commands and item IDs, inspect/use/drop/pickup flows, bag arithmetic, ownership, persistence and player feedback. Deliver a reproducible offline command test for one starter item and one consumable.

### B — Equipment and current fit

Audit slot maps, allowed slots, one-/two-handed rules and combat modifiers. Define a character appearance view derived **read-only** from equipped state. Begin with a readable fit summary and visual asset mapping; avatar image work must not silently alter item authority.

### C — First combat encounter

Select an **existing** suitable enemy and location from room/enemy data. In a sandbox, verify enter → engage → act → damage → disengage or victory → aftermath, including character death/recovery and enemy persistence. Decide narrative placement only after safety and pacing are demonstrated.

### D — Player journey and presentation

Integrate pod, HUD, inventory, fit, Lounge exploration, first social exchange and combat into a short first-night walkthrough. For each step specify exactly what a player sees, hears, can do and remembers. Invite a small cohort to report friction and offer content contributions after a verified walkthrough.

## Shared acceptance criteria

- A fresh test character can complete the journey without administrative intervention.
- Items cannot duplicate or disappear unexpectedly when equipped, used, dropped or rewarded.
- Equipping visibly updates the character sheet/fit and affects combat only where defined.
- The encounter can be resolved or exited without corrupting persistent state.
- Every important step provides clear, legible Discord feedback and a discoverable next action.
- Returning to the Lounge preserves earned changes and does not replay one-time scenes unintentionally.
- All tests use a disposable isolated checkout and fixtures; no live character, room, event history or world-clock files are changed.

## Execution order

**Concurrent audit first:** A, B and C inspect current behaviour in parallel while D maps presentation. **Integration checkpoint:** agree on the item/slot/state contracts and test fixtures. **Concurrent implementation next:** address verified gaps with separate bounded changes. **First cohort:** only after a full sandbox walkthrough passes.

## Next one-card action

**Build a read-only command and state-contract matrix** from `core.py`, `utils.py`, `combat.py`, `storage.py`, `data/items/items.json` and character fixtures. Specifically resolve the equip-slot mismatch and locate all item-use commands before writing or modifying gameplay code.
