"""Versioned pod stills. No world mutation; unread artwork follows discovery state."""
from fsbot.pod_opening import opening_state

ASSET_ROOT = "assets/images/world/manzo/triton_central/neptune_lounge/pod/v1/"
BASE_URL = "https://future-sky.net/" + ASSET_ROOT
BINDINGS = {
    "room": "p01.png", "pod": "p01.png",
    "panels": "p02.png",
    "display": "p03.png",
    "light": "p05.png", "button": "p05.png", "brochure": "p05.png", "brochure_art": "p05.png",
    "viewport": "p06.png", "reflection": "p06.png",
}


def pod_image(character, target):
    if character.get("current_room") != "pod_room" or character.get("in_cube"):
        return None
    discoveries = (opening_state(character) or {}).get("discoveries") or []
    if target == "display" and "booking" in discoveries:
        return None  # UNREAD is baked into this still; retain truthful text after reading.
    name = BINDINGS.get(target)
    return BASE_URL + name if name else None
