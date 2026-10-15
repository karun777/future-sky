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
    stats = updated.get("stats")
    # Match the combat resolver's precedence: explicit HP pool first,
    # legacy stats.hp/max_hp second. Never replace elemental pools.
    if isinstance(hp_pool, dict):
        current, maximum = hp_pool.get("current"), hp_pool.get("max")
        hp_target, hp_field = hp_pool, "current"
    elif isinstance(stats, dict) and "hp" in stats and "max_hp" in stats:
        current, maximum = stats["hp"], stats["max_hp"]
        hp_target, hp_field = stats, "hp"
    else:
        raise ItemUseError("Your health values are unavailable.")
    if type(current) is not int or type(maximum) is not int or maximum <= 0 or current < 0 or current > maximum:
        raise ItemUseError("Your health values are invalid.")
    recovered = min(amount, maximum - current)
    if recovered:
        hp_target[hp_field] = current + recovered
    consumed = bool(action.get("consume", True))
    if consumed:
        updated["bag"][key] -= 1
        if updated["bag"][key] == 0:
            del updated["bag"][key]
    if recovered:
        message = f"You use {name} and recover {recovered} HP."
    else:
        message = str(action.get("full_health_text") or f"You enjoy {name}.")
    return updated, message, consumed
