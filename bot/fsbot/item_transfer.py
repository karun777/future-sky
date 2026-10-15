"""Pure transfers between room ground items and character bags."""
from copy import deepcopy


class TransferError(ValueError):
    pass


def resolve_item(query, items):
    query = (query or "").strip().casefold()
    matches = [(key, item["name"]) for key, item in items.items()
               if isinstance(item, dict) and isinstance(item.get("name"), str)
               and query in (key.casefold(), item["name"].casefold())]
    if len(matches) != 1:
        raise TransferError("Unknown or ambiguous item.")
    return matches[0]


def transfer(character, room, items, query, direction):
    if direction not in ("take", "drop"):
        raise TransferError("Invalid transfer.")
    item_id, name = resolve_item(query, items)
    person, place = deepcopy(character), deepcopy(room)
    bag = person.setdefault("bag", {})
    ground = place.setdefault("items", [])
    if not isinstance(bag, dict) or not isinstance(ground, list):
        raise TransferError("Invalid item storage.")
    if direction == "take":
        index = next((i for i, value in enumerate(ground)
                      if isinstance(value, str) and value.casefold() == name.casefold()), None)
        if index is None:
            raise TransferError(name + " is not here.")
        ground.pop(index)
        bag[item_id] = int(bag.get(item_id, 0)) + 1
    else:
        if int(bag.get(item_id, 0)) <= 0:
            raise TransferError("You are not carrying " + name + ".")
        bag[item_id] = int(bag[item_id]) - 1
        if bag[item_id] == 0:
            del bag[item_id]
        ground.append(name)
    return person, place, name
