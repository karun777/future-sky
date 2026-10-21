"""One performance allowance per established, discovered booking.
The counterkeeper/bar caller persists the returned copy before presenting success.
"""
from copy import deepcopy
from fsbot.pod_opening import opening_state

ALLOWANCE = 25
KEY = "performance_bar_tab_v1"
REVEAL = ('The counterkeeper checks something below the counter. '
          '“Twenty-five on the tab. For the set. Apparently.” '
          'A pause. “Try to leave something for afterwards.”')

def tab_state(character):
    extra = character.get("extra") or {}
    value = extra.get(KEY) if isinstance(extra, dict) else None
    if value is None:
        return None
    if (not isinstance(value, dict) or value.get("granted") is not True
            or type(value.get("balance")) is not int
            or not 0 <= value["balance"] <= ALLOWANCE):
        raise ValueError("Your performance tab is unavailable. No credits were changed.")
    return value

def balance(character):
    state = tab_state(character)
    return state["balance"] if state else 0

def reveal_tab(character):
    existing = tab_state(character)
    if existing is not None:
        return character, None
    if character.get("in_cube") or character.get("current_room") != "neptune_lounge":
        return character, None
    extra = character.get("extra") or {}
    arrival = extra.get("arrival") or {}
    opening = opening_state(character)
    if (not opening or arrival.get("performance_booking", True) is False
            or "booking" not in (opening.get("discoveries") or [])):
        return character, None
    updated = deepcopy(character)
    updated.setdefault("extra", {})[KEY] = {"granted": True, "balance": ALLOWANCE}
    return updated, REVEAL


def claim_tab(storage, uid):
    """Synchronous save/rollback prevents duplicate grants between local callbacks."""
    original = storage.characters[uid]
    updated, message = reveal_tab(original)
    if updated != original:
        storage.characters[uid] = updated
        try:
            storage.save_characters()
        except Exception as exc:
            storage.characters[uid] = original
            raise ValueError("The performance tab could not be saved. Please try again.") from exc
    return updated, message
