"""Web wardrobe projection and durable first selection; existing rules remain authoritative."""
from fsbot.pod_wardrobe import select_uniform, current_fit
from fsbot.dressing import clothing_slots, resolve_clothing
from fsbot.pod_opening import opening_state
from fsbot.recovery import recovering

def select_outfit(storage, uid, choice, catalogue):
    uid = str(uid)
    original = storage.characters.get(uid)
    if not isinstance(original, dict) or original.get("current_room") != "pod_room":
        raise ValueError("The wardrobe is back in your pod.")
    if recovering(original) or original.get("in_cube"):
        raise ValueError("Your body cannot change clothes now.")
    updated = select_uniform(original, choice, catalogue, storage.items_db)
    storage.characters[uid] = updated
    try:
        storage.save_characters()
    except Exception as exc:
        storage.characters[uid] = original
        raise ValueError("The wardrobe could not save your selection. Please try again.") from exc
    return current_fit(updated, storage.items_db)

def wardrobe_view(character, items, catalogue):
    state = opening_state(character) or {}
    if "wardrobe" not in state.get("discoveries", []):
        return {"available": False, "options": [], "actions": []}
    selected = (character.get("extra") or {}).get("arrival", {}).get("pod_uniform_selected")
    options, actions = [], []
    for outfit in catalogue.get("uniforms", []):
        action = None if selected else "select:" + outfit["id"]
        options.append({"id": "catalogue:" + outfit["id"], "name": outfit["name"],
                        "description": outfit["description"], "action": action,
                        "label": "Choose and wear" if action else "First-selection catalogue"})
        if action:
            actions.append(action)
    for key, quantity in (character.get("bag") or {}).items():
        item = items.get(key)
        if not isinstance(item, dict) or not clothing_slots(item) or int(quantity) <= 0:
            continue
        # Use the same resolution and first compatible clothing slot as !wear.
        resolve_clothing(character, items, key)
        action = "wear:" + key
        options.append({"id": "carried:" + key, "name": item.get("name", key),
                        "description": item.get("description") or "A garment you carry.",
                        "action": action, "label": "Wear", "quantity": int(quantity)})
        actions.append(action)
    return {"available": True, "first_selection": not bool(selected),
            "fit": current_fit(character, items)["label"],
            "options": options, "actions": actions}
