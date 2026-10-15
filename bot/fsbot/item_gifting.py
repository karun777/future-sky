"""Pure character-to-character item gifting."""
from copy import deepcopy


class GiftError(ValueError):
    pass


def give_item(giver, recipient, items, query):
    if giver.get("current_room") != recipient.get("current_room"):
        raise GiftError("The recipient isn't here.")
    needle = (query or "").strip().casefold()
    bag = giver.get("bag") or {}
    matches = [(key, value) for key, value in items.items()
               if isinstance(value, dict) and needle
               and needle in (str(key).casefold(), str(value.get("name", "")).casefold())
               and isinstance(bag, dict) and int(bag.get(key, 0)) > 0]
    if len(matches) != 1:
        raise GiftError("You aren't carrying that item." if not matches else "Ambiguous item.")
    key, item = matches[0]
    if item.get("transfer_policy") in ("restricted", "not_transferable"):
        raise GiftError("That item cannot be given.")
    a, b = deepcopy(giver), deepcopy(recipient)
    a["bag"][key] -= 1
    if a["bag"][key] == 0:
        del a["bag"][key]
    b.setdefault("bag", {})[key] = int(b.get("bag", {}).get(key, 0)) + 1
    if key == "itm_tiny_book" and recipient.get("name", "").casefold() == "the dark rat queen":
        known = a.setdefault("item_discoveries", {}).setdefault(key, [])
        if "queen_interest" not in known:
            known.append("queen_interest")
    return a, b, item.get("name", key)
