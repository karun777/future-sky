"""Pure, side-effect-free pod wardrobe selection (Feather 34).

Caller owns persistence and presentation. No Discord dependency.
Selection does not change identity or grant authority.
"""
from __future__ import annotations

from copy import deepcopy


class WardrobeError(ValueError):
    pass


def select_uniform(character: dict, choice: str, catalogue: dict, items: dict) -> dict:
    """Return a *new* character with selected pod uniform equipped.

    Raises WardrobeError without mutating input on invalid selection.
    Existing chest equipment returns to bag; other slots are untouched.
    This is the initial pod selection only, not a replacement for !equip.
    """
    if not isinstance(character, dict):
        raise WardrobeError("Invalid character.")
    uniforms = catalogue.get("uniforms", [])
    selection = next((u for u in uniforms if u.get("id") == choice), None)
    if selection is None:
        raise WardrobeError("Unknown uniform.")
    result = deepcopy(character)
    extra = result.setdefault("extra", {})
    arrival = extra.setdefault("arrival", {})
    if arrival.get("pod_uniform_selected"):
        raise WardrobeError("Pod uniform already selected; use equipment commands to change clothes.")
    item_id = selection["item_id"]
    item = items.get(item_id)
    if not isinstance(item, dict) or item.get("type") != "equipment":
        raise WardrobeError("Uniform item definition missing or not equipment.")
    if "chest" not in item.get("equip", {}).get("allowed_slots", []):
        raise WardrobeError("Uniform does not fit the chest slot.")
    bag = result.setdefault("bag", {})
    equipped = result.setdefault("equipped", {})
    previous = equipped.get("chest")
    if previous:
        bag[previous] = int(bag.get(previous, 0)) + 1
    if int(bag.get(item_id, 0)) > 0:
        bag[item_id] -= 1
        if bag[item_id] == 0:
            del bag[item_id]
    equipped["chest"] = item_id
    arrival["pod_uniform_selected"] = choice
    # Current visual fit derives from equipped; social impression is only a hint.
    return result


def current_fit(character: dict, items: dict) -> dict:
    """Read-only visual/social presentation derived from equipped chest item."""
    item_id = (character.get("equipped") or {}).get("chest")
    item = items.get(item_id, {}) if item_id else {}
    return {
        "chest_item_id": item_id,
        "label": item.get("name", "Unspecified attire"),
        "appearance_key": item.get("appearance_key"),
        "social_cue": item.get("social_cue"),
    }
