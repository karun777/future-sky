"""Shared durable pod observation; adapters provide identity and presentation."""
import re
from fsbot.pod_opening import prepare_observation, opening_state, scene_target, TARGETS
from fsbot.pod_media import pod_image
from fsbot.recovery import recovering

def inspect_pod(storage, uid, target=None):
    original = storage.characters.get(str(uid))
    if not isinstance(original, dict):
        raise ValueError("Create a character first.")
    if recovering(original):
        raise ValueError("Your body is in recovery. Bodily actions must wait.")
    if original.get("in_cube") or original.get("current_room") != "pod_room":
        raise ValueError("This awakening begins in the pod.")
    if target is not None:
        target = scene_target(target)
        if not target:
            raise ValueError("That pod detail is unavailable.")
        if not opening_state(original):
            raise ValueError("Begin finding your bearings with !awaken in Discord.")
    updated, view = prepare_observation(original, target)
    if updated != original:
        storage.characters[str(uid)] = updated
        try:
            storage.save_characters()
        except Exception as exc:
            storage.characters[str(uid)] = original
            raise RuntimeError("The pod could not remember that discovery. Please try again.") from exc
    title, text, guidance = view
    if target == "garment":
        item_id = (original.get("equipped") or {}).get("chest")
        definition = storage.items_db.get(item_id, {})
        if definition:
            title = definition.get("name", "Your clothing")
            text = ("You are wearing **" + title + "**. A thin chain rests beneath the collar. "
                    "Clothes alone do not establish a job, a faction or a remembered identity.")
    return {"title": title, "text": text, "guidance": guidance,
            "image": pod_image(updated, target), "target": target,
            "room": "pod_room"}

def web_targets(character):
    """Only this pilot's visible targets; never grant knowledge during a read."""
    if (not isinstance(character, dict) or recovering(character)
            or character.get("in_cube") or character.get("current_room") != "pod_room"):
        return []
    state = opening_state(character)
    if not state:
        return []
    discoveries = state.get("discoveries")
    if not isinstance(discoveries, list):
        return []
    targets = ["hands", "garment", "pod", "panels"]
    # Reuse authored follow-on guidance and each character's recognition choices.
    # prepare_observation works on a copy: rendering offers never discovers anything.
    for discovered in discoveries:
        if discovered not in TARGETS:
            continue
        _, (_, _, guidance) = prepare_observation(character, discovered)
        for query in re.findall(r"`!inspect ([^`]+)`", guidance):
            target = scene_target(query)
            if target and target not in {"display", "wardrobe", "booking"} and target not in targets:
                targets.append(target)
    if "hud_presence" in discoveries and "hud" not in targets:
        targets.append("hud")
    if "panels" in discoveries or "display" in discoveries:
        targets.extend(["display", "wardrobe"])
        if character.get("extra", {}).get("arrival", {}).get("performance_booking", True) is not False:
            targets.append("booking")
    return targets
