"""W4-F11 bounded rehearsal clock. Explicit actions, no automatic idle timer."""
from copy import deepcopy
from fsbot.recovery import recovering
from fsbot.rat_messenger import state_of as messenger_state
from fsbot.terrace_delivery import APPROACH

KEY = "rehearsal_v1"
ROOM = "elemental_sound"
ROOT = "sector_42"
ROUTE = [(APPROACH, "north", "lounge_main_floor"),
         ("lounge_main_floor", "outside", "neptune_lounge"),
         ("neptune_lounge", "north", "main_square"),
         ("main_square", "up", ROOT), (ROOT, "east", ROOM)]
LISTING = ("**ELEMENTAL SOUND — REHEARSAL SPACE**\n"
           "A room, decks, monitors. Bring something you want to work on.\n\n"
           "Above the market, Sector 42. Locals rehearse, produce and record here. "
           "A slot starts thirty minutes after booking and lasts one hour. "
           "The direct walk takes twenty minutes; the next booking starts when yours ends.\n\n"
           "Book with `!rehearsal book`.")
DEFINITION = {
    "title": "Elemental Sound — Creative Common",
    "description": ("A bass phrase stops, starts again, then resolves differently. "
        "Flight cases pass between open doors. Musicians and DJs compare mixes in a busy common area. "
        "Beyond the desk, room lights mark rehearsal, production and recording sessions already underway."),
    "exits": {"west": ROOT}, "items": [], "enemies": {}, "image": "",
    "era": "manzo", "content_owner": "w4f11_elemental_v1",
}

def register_room(rooms):
    source = rooms.get(ROOT)
    if not isinstance(source, dict) or not isinstance(source.get("exits"), dict):
        raise ValueError("The Elemental Sound approach is unavailable.")
    if source["exits"].get("east") not in (None, ROOM):
        raise ValueError("The Elemental Sound exit is already in use.")
    existing = rooms.get(ROOM)
    if existing is not None and (not isinstance(existing, dict)
            or existing.get("content_owner") != DEFINITION["content_owner"]
            or existing.get("exits", {}).get("west") != ROOT):
        raise ValueError("The Elemental Sound room ID is already in use.")
    if existing is None:
        rooms[ROOM] = deepcopy(DEFINITION)
    source["exits"]["east"] = ROOM

def state_of(ch):
    state = (ch.get("extra") or {}).get(KEY)
    if state is None:
        return None
    if (not isinstance(state, dict) or state.get("version") != 1
            or state.get("stage") not in {"booked", "arrived", "complete", "missed", "returned"}
            or type(state.get("elapsed_minutes")) is not int or state["elapsed_minutes"] < 0
            or state.get("clock") != "rehearsal_elapsed_minutes"
            or not isinstance(state.get("history"), list)):
        raise ValueError("Your rehearsal record is unavailable. Nothing was changed.")
    return state

def available(ch):
    return not ch.get("in_cube") and not recovering(ch)

def listing(ch):
    if not available(ch):
        return None
    if messenger_state(ch) is None:
        return None
    state = state_of(ch)
    return status(state) if state else LISTING

def status(state):
    if state["stage"] == "booked":
        return (f"Elemental Sound: session starts at minute 30 and ends at minute 90. "
                f"Your booking clock: **{state['elapsed_minutes']} minutes**. "
                "Walk there with `!rehearsal go` (20 minutes).")
    if state["stage"] == "arrived":
        return (f"Booking clock: **{state['elapsed_minutes']} minutes**. "
                "Begin with `!rehearsal start`. Early arrival waits until the slot starts.")
    if state["stage"] == "missed":
        return "The rehearsal slot has ended. You can request another slot with `!rehearsal rebook`."
    if state["stage"] == "returned":
        return "You are back at the dock windows. Your rehearsal is recorded."
    return "Your rehearsal is complete. Return to the dock windows with `!rehearsal return` (20 minutes)."

def guidance(ch):
    if not available(ch):
        return None
    state = state_of(ch)
    if state:
        return "Elemental Sound", status(state)
    if ch.get("current_room") == APPROACH and messenger_state(ch):
        return "Time to prepare", "Find rehearsal space on `!feed7`."
    return None

def _require(ok, message):
    if not ok:
        raise ValueError(message)

def _route(rooms, path):
    for source, direction, destination in path:
        _require(rooms.get(source, {}).get("exits", {}).get(direction) == destination,
                 "The rehearsal route is unavailable. Nothing was changed.")

def prepare(ch, request, rooms):
    _require(available(ch), "Return from the Cube or finish recovery before rehearsing.")
    words = request.casefold().split()
    action = words[0] if words else "status"
    state = state_of(ch)
    _require(action in {"status","book","rebook","go","start","return","wait","routine"},
             "Use `!rehearsal` to see your next action.")
    if action == "status":
        _require(state is not None, "Find rehearsal space on `!feed7`.")
        return ch, ("Your rehearsal", status(state))
    if action in {"book", "rebook"}:
        _require(messenger_state(ch) is not None, "The rehearsal strand begins after contacting the rat.")
        if state and action == "book":
            return ch, ("Your rehearsal", status(state))
        _require(action != "rebook" or (state and state["stage"] == "missed"),
                 "A replacement slot is available only after a missed session.")
        updated = deepcopy(ch)
        updated.setdefault("extra", {})[KEY] = {
            "version":1, "stage":"booked", "elapsed_minutes":0,
            "clock":"rehearsal_elapsed_minutes", "history":[],
            "previous_attempts": (state.get("previous_attempts", []) + [deepcopy(state)]
                                  if state else []),
        }
        return updated, ("Elemental Sound — booked",
            "Your slot starts in thirty minutes and lasts one hour. The direct walk takes twenty minutes.\n\n"
            "Route: dock windows → main floor → Domefront → market → Sector 42 → Elemental Sound.\n\n"
            "Go with `!rehearsal go`.")
    _require(state is not None, "Book a room first with `!rehearsal book`.")
    updated = deepcopy(ch)
    s = updated["extra"][KEY]
    title = "Elemental Sound"
    if action == "wait":
        _require(len(words) == 2 and words[1].isdigit() and 0 < int(words[1]) <= 1440,
                 "Use `!rehearsal wait <minutes>` (1–1440).")
        s["elapsed_minutes"] += int(words[1])
        text = f"You let {int(words[1])} minutes pass.\n\n" + status(s)
    elif action == "go":
        _require(ch.get("current_room") in {APPROACH, ROOM},
                 "Start the rehearsal walk at the Stardock Overlook.")
        if ch.get("current_room") == ROOM:
            return ch, (title, status(state))
        _require(s["stage"] == "booked", "That rehearsal journey is already recorded.")
        _route(rooms, ROUTE)
        s["elapsed_minutes"] += 20
        s["stage"] = "arrived"
        updated["current_room"] = ROOM
        text = ("You cross the Lounge, pass through the market and climb to Sector 42. "
                "A sign beside the next doorway reads **Elemental Sound**.\n\n"
                + DEFINITION["description"] + "\n\n" + status(s))
    elif action in {"start","routine"}:
        _require(ch.get("current_room") == ROOM, "Reach Elemental Sound first with `!rehearsal go`.")
        if s["stage"] in {"complete","returned","missed"}:
            return ch, (title, status(state))
        _require(s["stage"] == "arrived", "Check in after the rehearsal walk first.")
        now = max(30, s["elapsed_minutes"])
        if now >= 90:
            s["stage"] = "missed"
            text = "The next booking is already setting up. Your slot has passed.\n\n" + status(s)
        else:
            s["practice_minutes"] = 90 - now
            s["elapsed_minutes"] = 90
            s["stage"] = "complete"
            s["mode"] = "habitual" if action == "routine" else "conscious"
            text = (("You fall back on familiar material and a familiar way of practising."
                     if action == "routine" else
                     "You work on timing, transitions and listening to what you are actually doing.")
                    + f" You spend **{s['practice_minutes']} minutes** rehearsing. "
                    "The next booking arrives as your slot ends.\n\n"
                    "You have rehearsed, without opening the terrace USB or using music from the Queen. "
                    "Her approval remains unresolved.\n\n" + status(s))
    else:
        _require(action == "return", "Use `!rehearsal` for your next action.")
        if s["stage"] == "returned":
            return ch, (title, status(state))
        _require(s["stage"] == "complete" and ch.get("current_room") == ROOM,
                 "Complete rehearsal at Elemental Sound before the return walk.")
        for a,direction,b in ROUTE:
            _require(a in rooms.get(b,{}).get("exits",{}).values(),
                     "The return route is unavailable. Nothing was changed.")
        s["elapsed_minutes"] += 20
        s["stage"] = "returned"
        updated["current_room"] = APPROACH
        text = ("You make your way back through the market to the dock windows.\n\n"
                f"**{s['elapsed_minutes']} minutes** have passed on your rehearsal booking clock. "
                "You have time to look out over the stardock again.")
    s["history"].append({"action":action,"at_minute":s["elapsed_minutes"]})
    return updated, (title,text)
