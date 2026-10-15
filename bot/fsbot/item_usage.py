"""Pure, inventory-owned item use with explicit catalogue mechanics."""
from copy import deepcopy


class ItemUseError(ValueError):
    pass


def use_item(character, items, query):
    needle = (query or "").strip().casefold()
    if not needle:
        raise ItemUseError("Usage: !use <item>")
    bag = character.get("bag") or {}
    matches = [(key, value) for key, value in items.items()
               if isinstance(value, dict)
               and needle in (str(key).casefold(), str(value.get("name", "")).casefold())
               and isinstance(bag, dict) and int(bag.get(key, 0)) > 0]
    if len(matches) != 1:
        raise ItemUseError("You aren't carrying that item." if not matches else "Ambiguous item.")
    key, item = matches[0]
    name = item.get("name", key)
    action = item.get("use_action")
    if not isinstance(action, dict):
        raise ItemUseError(f"{name} has no usable action yet.")
    kind = action.get("kind")
    updated = deepcopy(character)
    if kind == "read":
        return updated, str(action.get("text") or f"You read {name}."), False
    if kind != "heal":
        raise ItemUseError(f"{name} has no supported use action.")
    amount = action.get("amount")
    if type(amount) is not int or amount <= 0:
        raise ItemUseError(f"{name} has invalid healing data.")
    pools = updated.get("pools")
    hp_pool = pools.get("hp") if isinstance(pools, dict) else None
    if not isinstance(hp_pool, dict):
        raise ItemUseError("Your health pool is unavailable.")
    current, maximum = hp_pool.get("current"), hp_pool.get("max")
    if type(current) is not int or type(maximum) is not int or maximum <= 0:
        raise ItemUseError("Your health pool is invalid.")
    if current >= maximum:
        raise ItemUseError("You're already at full health.")
    recovered = min(amount, maximum - current)
    hp_pool["current"] = current + recovered
    if action.get("consume", True):
        updated["bag"][key] -= 1
        if updated["bag"][key] == 0:
            del updated["bag"][key]
    return updated, f"You use {name} and recover {recovered} HP.", bool(action.get("consume", True))
