"""Read-only player knowledge shared by Discord and the authenticated HUD."""
from fsbot.pod_opening import opening_state

DEFAULT_HUD = {"enabled": True, "state": "normal"}
STATES = {"normal", "signal_degraded", "dark_mode"}

def hud_preferences(character):
    extra = character.get("extra")
    value = extra.get("hud") if isinstance(extra, dict) else None
    return value if isinstance(value, dict) else DEFAULT_HUD

def display_view(character):
    value = hud_preferences(character)
    state = value.get("state", "normal")
    return {"enabled": bool(value.get("enabled", True)),
            "state": state if state in STATES else "normal"}

def discovered_entries(character):
    """Known notices persist independently of the implant's display setting."""
    discovered = (opening_state(character) or {}).get("discoveries", [])
    extra = character.get("extra") or {}
    arrival = extra.get("arrival") or {}
    has_booking = arrival.get("performance_booking", True) is not False
    entries = []
    if "display" in discovered:
        entries.append({"id": "feed7", "title": "FEED7",
                        "text": "A signal you found in the pod."})
    if has_booking and "booking" in discovered:
        entries.append({"id": "booking", "title": "Remembered booking",
                        "text": "A gig tomorrow night. Format still unclear."})
    elif has_booking and any(t in discovered for t in ("panels", "display")):
        entries.append({"id": "notice", "title": "Unread notice",
                        "text": "You found a performance notification in the pod."})
    return entries
