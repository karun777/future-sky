"""W4-F8: local arrival cues selected from existing character knowledge.
No movement, encounter, inventory, clock or persistence authority.
"""
from fsbot.pod_opening import opening_state
from fsbot.token_exchange import TOKEN

ROUTE = {
    "hostel_hallway": ("The sound below", "Beyond the pod doors, the corridor continues. Lounge noise carries up from below.", "down", "hostel_stairwell"),
    "hostel_stairwell": ("Down to the Lounge", "Warm metal, detergent, distant chips. The sound is closer now.", "down", "neptune_lounge"),
}

def arrival_attention(character, room):
    if character.get("in_cube") or not opening_state(character):
        return None
    room_id = character.get("current_room")
    exits = room.get("exits") or {}
    if room_id in ROUTE:
        title, text, direction, destination = ROUTE[room_id]
        if exits.get(direction) == destination:
            return title, text + f"\n\nFollow it with `!go {direction}`, or take another route."
        return None
    if room_id != "neptune_lounge":
        return None
    text = "A counterkeeper works behind the counter. You can pause here before going farther."
    state = opening_state(character)
    arrival = (character.get("extra") or {}).get("arrival") or {}
    if arrival.get("performance_booking", True) is not False and "booking" in (state.get("discoveries") or []):
        text += "\n\nThe notice comes back to you: a gig tomorrow night. You still do not know the format."
    text += "\n\nTry `!inspect counterkeeper` or `!bar`."
    if exits.get("inside") == "lounge_main_floor":
        text += " `!go inside` takes you farther into the Lounge."
    return "At the counter", text

def counterkeeper_view(character, query):
    key = " ".join((query or "").casefold().split()).strip(".!?")
    if key not in ("counterkeeper", "counter", "bar counter"):
        return None
    if character.get("in_cube") or character.get("current_room") != "neptune_lounge":
        return None
    arrival = (character.get("extra") or {}).get("arrival") or {}
    if arrival.get("brass_token_exchanged"):
        text = "The counterkeeper has your brass token. Their warning stays with you: don't answer that here."
        guidance = "The exchange is remembered. You can browse with `!bar` or continue exploring."
    elif (character.get("bag") or {}).get(TOKEN, 0) > 0:
        text = "The counterkeeper polishes behind the counter. You still have the notched brass token from the pod."
        guidance = "You can offer it with `!offer token`, browse with `!bar`, or leave it for now."
    else:
        text = "The counterkeeper polishes behind the counter. You have nothing you need to offer."
        guidance = "Browse with `!bar`, or continue exploring. No exchange is required to enter the Lounge."
    return "The counterkeeper", text, guidance
