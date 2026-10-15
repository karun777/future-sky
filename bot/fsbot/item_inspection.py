"""Pure, visibility-aware item inspection."""
def inspect_item(query, character, room, items):
    needle = (query or "").strip().casefold()
    if not needle:
        raise ValueError("Usage: !inspect <item>")
    bag = character.get("bag") or {}
    equipped = character.get("equipped") or {}
    ground = room.get("items") or []
    candidates = []
    for item_id, item in items.items():
        if not isinstance(item, dict):
            continue
        name = item.get("name", item_id)
        if needle not in (str(item_id).casefold(), str(name).casefold()):
            continue
        in_bag = isinstance(bag, dict) and int(bag.get(item_id, 0)) > 0
        worn = isinstance(equipped, dict) and item_id in equipped.values()
        nearby = isinstance(ground, list) and any(
            isinstance(entry, str) and entry.casefold() in (str(name).casefold(), str(item_id).casefold())
            for entry in ground)
        if in_bag or worn or nearby:
            candidates.append((item_id, item))
    if len(candidates) != 1:
        raise ValueError("You cannot see that item here." if not candidates else "That item name is ambiguous.")
    item_id, item = candidates[0]
    known = dict(item.get("attributes", {})) if isinstance(item.get("attributes"), dict) else {}
    discoveries = character.get("item_discoveries") or {}
    unlocked = discoveries.get(item_id, []) if isinstance(discoveries, dict) else []
    if not isinstance(unlocked, list):
        unlocked = []
    for key, entry in (item.get("discoveries") or {}).items():
        if key in unlocked and isinstance(entry, dict):
            known.update(entry.get("attributes", {}))
    return item_id, item, known, unlocked
