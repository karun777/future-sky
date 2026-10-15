"""A first local rumour: claims are not facts.

The character record stores a witnessed claim for later exploration; this
does not yet model autonomous NPC communication or global propagation.
"""
from copy import deepcopy

RUMOUR_ID = "lounge_efiishent_drinking_v1"


def witness_drinking(character, level):
    if level < 3 or character.get("room") != "neptune_lounge":
        return character, None
    updated = deepcopy(character)
    rumours = updated.setdefault("rumours_heard_about_self", [])
    if not isinstance(rumours, list):
        return character, None
    if any(isinstance(r, dict) and r.get("id") == RUMOUR_ID for r in rumours):
        return character, None
    name = str(updated.get("name") or "that traveller")
    claim = f"{name} has a drinking problem and has been causing trouble at Neptune Lounge."
    rumours.append({
        "id": RUMOUR_ID,
        "room_id": "neptune_lounge",
        "witness": "silver-eyed patron",
        "claim": claim,
        "status": "unverified",
        "basis": "witnessed intoxication level 3",
    })
    return updated, (
        "A silver-eyed patron watches you over the rim of her glass. "
        "She leans towards her companion. 'That one has a problem, I reckon.' "
        "A whisper begins its journey."
    )


def local_rumours(character):
    rumours = character.get("rumours_heard_about_self", [])
    if not isinstance(rumours, list):
        return []
    return [r for r in rumours if isinstance(r, dict) and r.get("room_id") == character.get("room")]
