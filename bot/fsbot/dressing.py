"""Name resolution for worn clothing; CoreCog remains equipment steward."""
def normal(value):
    return " ".join(str(value).casefold().split())

def clothing_slots(item):
    return [s for s in (item.get("equip") or {}).get("allowed_slots", [])
            if s not in {"main_hand", "off_hand"}]

def resolve_clothing(character, items, query, worn=False):
    needle = normal(query)
    if not needle:
        raise ValueError("Use !remove <clothing name>." if worn else "Use !wear <clothing name>.")
    equipped = character.get("equipped") or {}
    owned = set(equipped.values()) if worn else {k for k,v in (character.get("bag") or {}).items() if int(v)>0}
    matches = [key for key in owned if isinstance(items.get(key),dict)
               and clothing_slots(items[key])
               and needle in {normal(key),normal(items[key].get("name",""))}]
    if len(matches)>1:
        raise ValueError("More than one garment has that name. Use its item ID from !inventory.")
    if not matches:
        raise ValueError("You are not wearing that garment." if worn else
                         "You are not carrying that garment. Check !inventory; !wardrobe offers your first outfit in the pod.")
    key=matches[0]
    if worn:
        slots=[s for s,v in equipped.items() if v==key and s not in {"main_hand","off_hand"}]
        if len(slots)!=1:
            raise ValueError("That garment occupies multiple slots; use !unequip <slot>.")
        return key,slots[0]
    return key,clothing_slots(items[key])[0]
