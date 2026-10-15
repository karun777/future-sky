"""Neptune Lounge's finite complimentary bottles and scavenging memory."""
from copy import deepcopy

LOUNGE = "neptune_lounge"
FREE_BOTTLES = 3
MARKER = "triton_lager_freebies_v1"


def seed_freebies(room):
    """Seed once, preserving existing ground items and room metadata."""
    updated = deepcopy(room)
    markers = updated.setdefault("world_flags", {})
    if not isinstance(markers, dict):
        raise ValueError("Invalid room flags")
    if markers.get(MARKER):
        return updated, False
    ground = updated.setdefault("items", [])
    if not isinstance(ground, list):
        raise ValueError("Invalid room items")
    existing = sum(1 for name in ground if isinstance(name, str) and name.casefold() == "triton lager")
    ground.extend(["Triton Lager"] * max(0, FREE_BOTTLES - existing))
    markers[MARKER] = True
    return updated, True


def record_free_take(character, room_id, item_name):
    """Only record a successful ground pickup, not a purchase or gift."""
    updated = deepcopy(character)
    if room_id != LOUNGE or item_name.casefold() != "triton lager":
        return updated, None
    counters = updated.setdefault("social_counters", {})
    if not isinstance(counters, dict):
        raise ValueError("Invalid social counters")
    previous = counters.get("neptune_free_lagers_taken", 0)
    if type(previous) is not int or previous < 0:
        raise ValueError("Invalid scavenging count")
    counters["neptune_free_lagers_taken"] = previous + 1
    if previous == 0:
        return updated, "A complimentary lager. Someone must be feeling generous."
    if previous == 1:
        return updated, "Another free lager? The bartender glances in your direction."
    return updated, "You pocket the lager. Someone behind the bar seems to be keeping count."
