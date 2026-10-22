"""W4-F10: private messenger contact, not an enemy or the Queen."""
from copy import deepcopy
from fsbot.terrace_delivery import state_of as delivery_state, APPROACH
from fsbot.recovery import recovering

KEY = "rat_messenger_v1"
TIP = ('“For tomorrow’s music? The Dark Rat Queen might know what your audience likes.” '
       'The counterkeeper glances towards the dock windows. '
       '“Someone who knows her sometimes waits there. Low down.”')
RAT = ("At the quiet end of the windowline, an actual rat sits on a warm conduit, "
       "grooming itself while ships manoeuvre beyond the glass. "
       "It notices you noticing it, and waits.")

def state_of(ch):
    value = (ch.get("extra") or {}).get(KEY)
    if value is None:
        return None
    if (not isinstance(value, dict) or value.get("version") != 1
            or value.get("stage") not in {"tip", "arranged"}):
        raise ValueError("Your messenger record is unavailable. Nothing was changed.")
    if value["stage"] == "arranged" and value.get("meeting") != {
            "contact": "dark_rat_queen", "room": APPROACH, "status": "arranged"}:
        raise ValueError("Your meeting record is unavailable. Nothing was changed.")
    return value

def eligible(ch):
    state = delivery_state(ch)
    return bool(state and state["stage"] == "usb_collected")

def available(ch):
    return not ch.get("in_cube") and not recovering(ch)

def tip(ch):
    """Return a copy for the counterkeeper presenter to persist before revealing."""
    if not available(ch) or ch.get("current_room") != "neptune_lounge" or not eligible(ch):
        return ch, None
    current = state_of(ch)
    if current:
        return ch, TIP if current["stage"] == "tip" else None
    updated = deepcopy(ch)
    updated.setdefault("extra", {})[KEY] = {"version": 1, "stage": "tip"}
    return updated, TIP

def guidance(ch):
    if not available(ch):
        return None
    state = state_of(ch)
    if not state:
        if ch.get("current_room") == "neptune_lounge" and eligible(ch):
            return "Tomorrow’s music", "Ask the counterkeeper: `!inspect counterkeeper`."
        return None
    room = ch.get("current_room")
    if state["stage"] == "arranged":
        if room == APPROACH:
            return "The arrangement", "The Dark Rat Queen has agreed to meet you here. Her arrival is the next part of this story."
        return None
    if room == "neptune_lounge":
        return "The dock windows", "Head onto the main floor with `!go inside`, then `!go south` to the Stardock Overlook."
    if room == "lounge_main_floor":
        return "The dock windows", "Find the messenger at the Stardock Overlook: `!go south`."
    if room == APPROACH:
        return "Low down", RAT + "\n\nAsk it to carry a request to meet the Dark Rat Queen: `!rat message`."
    return None

def prepare(ch, request=""):
    if not available(ch):
        raise ValueError("Return from the Cube or finish recovery before meeting the messenger.")
    if ch.get("current_room") != APPROACH:
        raise ValueError("Look for the messenger at the Stardock Overlook.")
    state = state_of(ch)
    if not state:
        raise ValueError("You have no lead on a messenger. Ask the counterkeeper.")
    action = " ".join(request.casefold().split())
    if action not in {"", "look", "inspect", "message"}:
        raise ValueError("Use `!rat message` to request a meeting.")
    if state["stage"] == "arranged":
        return ch, ("A meeting arranged",
                    "The rat has carried your message. The Dark Rat Queen has agreed to meet you here.",
                    "Her arrival is the next part of this story.")
    if action != "message":
        return ch, ("By the dock windows", RAT, "Send your request with `!rat message`.")
    updated = deepcopy(ch)
    updated["extra"][KEY] = {"version": 1, "stage": "arranged",
                            "meeting": {"contact": "dark_rat_queen", "room": APPROACH, "status": "arranged"}}
    return updated, ("A rat with connections",
        "You crouch beside the conduit and ask whether it can take a message to the Dark Rat Queen. "
        "You would like to meet her about tomorrow’s music.\n\n"
        "The rat studies you, then slips behind a pipe. When it returns, it pushes a folded scrap towards you.\n\n"
        "In a small, firm hand: **I’ll meet you here.**",
        "The meeting is arranged. Her arrival is the next part of this story.")
