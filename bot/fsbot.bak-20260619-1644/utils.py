# fsbot/utils.py — Utilities (contract-clean) v3.6.2
#
# Scope:
# - Pure helpers only (no storage writes, no discord imports)
# - Case-insensitive matching helpers
# - Bag/inventory formatting and arithmetic
# - Equip/weapon helpers used by combat or future systems
# - Room item list helpers (rooms.json contract expects list[str])
#
# Notes:
# - Keep this module dependency-light.
# - Avoid side effects. Callers own persistence.

from __future__ import annotations

from typing import Any, Dict, Iterable, Optional, Tuple
import random

# Canonical long-form d20 stat keys in character["stats"]
STAT_KEYS = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]

# Canonical equip slots
EQUIP_SLOTS = [
    "main_hand",
    "off_hand",
    "head",
    "body",
    "hands",
    "legs",
    "feet",
    "accessory1",
    "accessory2",
]


# -------------------------
# String matching
# -------------------------

def ci_match(target: str, options: Iterable[str]) -> Optional[str]:
    """Return the original option that matches target case-insensitively."""
    t = (target or "").strip().lower()
    if not t:
        return None
    for opt in options:
        if isinstance(opt, str) and opt.strip().lower() == t:
            return opt
    return None


# -------------------------
# Bag helpers (dict[item_name] = qty)
# -------------------------

def add_to_bag(bag: Dict[str, int], item: str, qty: int = 1) -> None:
    """Add qty to bag. Removes the key if qty would be <= 0."""
    if not item:
        return
    q = int(qty)
    if q == 0:
        return
    bag[item] = int(bag.get(item, 0)) + q
    if bag[item] <= 0:
        bag.pop(item, None)


def remove_from_bag(bag: Dict[str, int], item: str, qty: int = 1) -> bool:
    """Remove qty from bag if available. Returns True if removed."""
    if not item:
        return False
    q = int(qty)
    if q <= 0:
        return True
    have = int(bag.get(item, 0))
    if have < q:
        return False
    new = have - q
    if new > 0:
        bag[item] = new
    else:
        bag.pop(item, None)
    return True


def bag_count(bag: Dict[str, int]) -> int:
    """Total count of all items (sum of quantities)."""
    return sum(int(v) for v in bag.values())


def fmt_bag(bag: Dict[str, int]) -> str:
    if not bag:
        return "— (empty)"
    parts = [f"{name} x{int(qty)}" for name, qty in sorted(bag.items(), key=lambda kv: kv[0].lower())]
    return ", ".join(parts)


def fmt_equipped(equipped: Dict[str, str]) -> str:
    if not equipped:
        return "— (nothing equipped)"
    lines = []
    for slot in EQUIP_SLOTS:
        item = equipped.get(slot)
        if item:
            lines.append(f"{slot}: {item}")
    return "\n".join(lines) if lines else "— (nothing equipped)"


# -------------------------
# Equip / combat helpers
# -------------------------

def calc_scaling_bonus(stats: Dict[str, Any], scaling: str) -> int:
    """Return modifier from stats for scaling key (STR/DEX/INT)."""
    s = (scaling or "").strip().upper()
    if s == "STR":
        return (int(stats.get("strength", 10)) - 10) // 2
    if s == "DEX":
        return (int(stats.get("dexterity", 10)) - 10) // 2
    if s == "INT":
        return (int(stats.get("intelligence", 10)) - 10) // 2
    return 0


def equipped_defense(items_db: Dict[str, Any], equipped: Dict[str, str]) -> int:
    """Sum defense across equipped armor."""
    total = 0
    for item in equipped.values():
        meta = items_db.get(item, {})
        if isinstance(meta, dict) and meta.get("type") == "armor":
            total += int(meta.get("defense", 0))
    return total


def weapon_damage(items_db: Dict[str, Any], char: Dict[str, Any]) -> Tuple[int, int, int]:
    """Return (roll_d20, damage_min, damage_max) for main_hand weapon or fallback."""
    equipped = char.get("equipped") if isinstance(char.get("equipped"), dict) else {}
    main = equipped.get("main_hand")
    if main and main in items_db:
        meta = items_db.get(main, {})
        if isinstance(meta, dict) and meta.get("type") == "weapon":
            dmg = meta.get("damage", [1, 3])
            try:
                dmin = int(dmg[0])
                dmax = int(dmg[1])
            except Exception:
                dmin, dmax = 1, 3
            scale = calc_scaling_bonus(char.get("stats", {}) if isinstance(char.get("stats"), dict) else {}, meta.get("scaling", ""))
            # v0: scaling only increases the max, never reduces
            return (random.randint(1, 20), dmin, dmax + max(0, int(scale)))

    # fallback unarmed-ish
    return (random.randint(1, 20), 1, 2)


# -------------------------
# Room item helpers (rooms.json contract: items is list[str])
# -------------------------

def ensure_room_items_as_list(room: Dict[str, Any]) -> None:
    if "items" not in room or not isinstance(room.get("items"), list):
        room["items"] = []


def find_room_item_ci(room: Dict[str, Any], name: str) -> Optional[str]:
    ensure_room_items_as_list(room)
    return ci_match(name, [x for x in room["items"] if isinstance(x, str)])


def add_item_to_room(room: Dict[str, Any], item: str) -> None:
    if not item:
        return
    ensure_room_items_as_list(room)
    room["items"].append(item)


def remove_item_from_room(room: Dict[str, Any], item: str) -> bool:
    ensure_room_items_as_list(room)
    m = find_room_item_ci(room, item)
    if m:
        room["items"].remove(m)
        return True
    return False
