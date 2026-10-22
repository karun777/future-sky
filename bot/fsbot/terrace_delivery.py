"""W4-F9 private delivery state; character storage persists returned copies.
No clock, shared ground stock, generic trading, causal send or invalidation.
"""
from copy import deepcopy
from fsbot.pod_opening import opening_state
from fsbot.recovery import recovering

KEY = "terrace_delivery_v1"
ROOM = "lounge_smoking_terrace"
APPROACH = "lounge_stardock_overlook"
STAGES = ("attended", "landed", "collected", "unwrapped", "unlocked", "open", "usb_collected")
ROOM_DEFINITION = {
    "title": "Neptune Lounge — The Open Terrace",
    "description": ("An outdoor terrace opens over Triton Central. The city lights spread below; "
                    "docked ships hang against the vast blue of Neptune. The Lounge's music "
                    "reaches you softened by distance. A rail offers somewhere to linger."),
    "image": "", "era": "manzo", "tags": ["overlook", "social", "quiet"],
    "items": [], "enemies": {}, "exits": {"inside": APPROACH},
    "ambient_events": [], "content_owner": "w4f9_terrace_v1",
}
TARGETS = {
    "package": "inspect package", "parcel": "inspect package",
    "box": "inspect box", "antique box": "inspect box",
    "usb": "inspect usb", "tunes": "inspect usb",
}
ACTIONS = {
    "": "view", "help": "view", "look": "view", "linger": "attend",
    "attend": "attend", "sky": "sky", "notice sky": "sky",
    "inspect package": "inspect package", "take package": "take package",
    "open package": "open package", "inspect box": "inspect box",
    "unlock box": "unlock box", "open box": "open box",
    "inspect usb": "inspect usb", "take usb": "take usb", "inventory": "inventory",
}


class TerraceError(ValueError):
    pass


def state_of(character):
    extra = character.get("extra") or {}
    if not isinstance(extra, dict):
        raise TerraceError("Your delivery record is unavailable.")
    value = extra.get(KEY)
    if value is None:
        return None
    if (not isinstance(value, dict) or value.get("version") != 1
            or value.get("stage") not in STAGES
            or not isinstance(value.get("objects"), dict)
            or not isinstance(value.get("discoveries"), list)
            or not isinstance(value.get("history"), list)
            or not isinstance(value.get("owner"), str) or not value["owner"]):
        raise TerraceError("Your delivery record is unavailable. Nothing was changed.")
    n = STAGES.index(value["stage"])
    for kind, threshold in [("package", 1), ("box", 3), ("usb", 5)]:
        if n >= threshold:
            obj = value["objects"].get(kind)
            if (not isinstance(obj, dict)
                    or obj.get("instance_id") != f"{value['owner']}:terrace:{kind}:v1"
                    or not isinstance(obj.get("holder"), str)):
                raise TerraceError("Your delivery record is incomplete. Nothing was changed.")
    if n >= 1 and not isinstance(value["objects"]["package"].get("addressee"), str):
        raise TerraceError("Your package address is unavailable.")
    return value


def eligible(character):
    opening = opening_state(character)
    arrival = (character.get("extra") or {}).get("arrival") or {}
    return bool(opening and arrival.get("performance_booking", True) is not False
                and "booking" in (opening.get("discoveries") or []))


def rank(state):
    return STAGES.index(state["stage"]) if state else -1


def inventory_lines(character):
    """Scene-owned holdings, deliberately outside generic bag transfers."""
    state = state_of(character)
    if not state or state.get("secured_in_pod") or rank(state) < STAGES.index("collected"):
        return []
    lines = ["Warm addressed package" if rank(state) < STAGES.index("unwrapped")
             else "Opened package containing the antique box"]
    if state["stage"] == "usb_collected":
        lines.append("USB marked tunes")
    return lines


def guidance(character):
    if character.get("in_cube"):
        return None
    if character.get("current_room") == APPROACH:
        return "Beyond the glass", "An outdoor lookout is reached with `!go out`."
    if character.get("current_room") != ROOM:
        return None
    state = state_of(character)
    options = {
        -1: "Linger with the view: `!terrace attend`.",
        0: "Watch the sky: `!terrace sky`.",
        1: "Try `!inspect package` or `!terrace take package`.",
        2: "Open it with `!terrace open package`.",
        3: "Try `!inspect box` or `!terrace unlock box`.",
        4: "Open the box: `!terrace open box`.",
        5: "Try `!inspect usb` or `!terrace take usb`.",
        6: "Review what you carry with `!inventory` or `!inspect tunes`.",
    }
    if state is None and not eligible(character):
        return "At the rail", "You can enjoy the view or return with `!go inside`."
    return "Your attention", options[rank(state)] + " You can leave with `!go inside`."


def register_room(rooms):
    """Idempotent, in-memory content registration, with collision protection."""
    source = rooms.get(APPROACH)
    if not isinstance(source, dict) or not isinstance(source.get("exits"), dict):
        raise TerraceError("The terrace approach is unavailable.")
    destination = source["exits"].get("out")
    if destination is not None and destination != ROOM:
        raise TerraceError("The proposed terrace exit is already in use.")
    existing = rooms.get(ROOM)
    if existing is not None and (
        not isinstance(existing, dict)
        or existing.get("content_owner") != "w4f9_terrace_v1"
        or existing.get("exits", {}).get("inside") != APPROACH
    ):
        raise TerraceError("The terrace room ID is already in use.")
    if existing is None:
        rooms[ROOM] = deepcopy(ROOM_DEFINITION)
    source["exits"]["out"] = ROOM


def _require(condition, message):
    if not condition:
        raise TerraceError(message)


def _remember(state, kind):
    if kind not in state["discoveries"]:
        state["discoveries"].append(kind)
        state["history"].append({"sequence": len(state["history"]) + 1, "kind": kind})


def prepare(character, uid, request=""):
    """Return copied character and (title, prose, guidance); no I/O."""
    _require(not recovering(character), "Your body is in recovery. Use \x60!recovery\x60.")
    _require(not character.get("in_cube"), "Return from the Cube before attending to this delivery.")
    key = " ".join(request.casefold().split())
    action = ACTIONS.get(key)
    _require(action is not None, "Use `!terrace` for the available delivery actions.")
    current = state_of(character)
    _require(not current or current["owner"] == str(uid), "This delivery belongs to another traveller.")
    n = rank(current)
    _require(not current or not current.get("secured_in_pod"),
             "Your delivery is secured in the pod. Collect it with \x60!pod_delivery collect\x60 after recovery.")
    on_terrace = character.get("current_room") == ROOM
    carrying = n >= STAGES.index("collected")
    _require(on_terrace or carrying, "This delivery begins at the outdoor terrace.")
    text = ""
    title = "The terrace"

    if action == "view":
        if not current:
            text = ROOM_DEFINITION["description"]
        else:
            text = "The view and the Lounge continue around you." if on_terrace else "You still carry your delivery."
        hint = guidance(character)
        return character, (title, text, hint[1] if hint else "Use `!terrace inventory` to review this delivery.")
    if action == "inventory":
        lines = inventory_lines(character)
        return character, ("Your delivery", "\n".join(lines) or "You carry no terrace delivery.",
                           "Use `!terrace` to return to this passage.")
    if action in ("attend", "sky"):
        _require(on_terrace, "The terrace sky is not in view.")
        if n >= STAGES.index("landed"):
            return character, ("The delivery", "The package has already arrived.",
                               "Use `!terrace` to see your next action.")
        _require(eligible(character), "No performance delivery is established for this arrival.")
        if action == "sky":
            _require(n >= 0, "First linger with the view: `!terrace attend`.")
        elif n == 0:
            return character, (title, "You remain with Neptune and the question of tomorrow's music.",
                               "Watch the sky with `!terrace sky`.")
    else:
        _require(n >= STAGES.index("landed"), "No package has arrived.")
        _require(on_terrace or carrying, "The package is not within reach.")

    updated = deepcopy(character)
    state = updated.setdefault("extra", {}).setdefault(KEY, {
        "version": 1, "owner": str(uid), "stage": "attended", "objects": {},
        "discoveries": [], "history": [],
    })

    if action == "attend":
        state["stage"] = "attended"
        _remember(state, "terrace.attended")
        text = "You linger at the rail. Neptune holds your attention. Tomorrow night. What are you going to play?"
    elif action == "sky":
        state["stage"] = "landed"
        state["objects"]["package"] = {
            "instance_id": f"{uid}:terrace:package:v1", "holder": ROOM,
            "addressee": str(character.get("name") or "an unreadable name"),
        }
        _remember(state, "package.landed")
        title = "Something in the sky"
        text = ("A shooting star? It slips between docked ships, disappears against Neptune, "
                "then appears closer. Coming here. Before you can respond, it gently streaks down. "
                "A soft impact at your feet. The last bright tendrils of wrapping burn away.")
    elif action == "inspect package":
        _remember(state, "package.address_read")
        title = "The package"
        # Reading the address does not assign autobiographical recognition.
        import discord
        addressee = discord.utils.escape_markdown(state["objects"]["package"]["addressee"])
        text = f"The label reads **{addressee}**. The wrapping gives no explanation."
    elif action == "take package":
        if n < STAGES.index("collected"):
            state["stage"] = "collected"
            state["objects"]["package"]["holder"] = str(uid)
            _remember(state, "package.collected")
            text = "You lift the package. Warm, but comfortable to hold."
        else:
            text = "You already carry the package."
    else:
        _require(carrying, "Pick up the package first: `!terrace take package`.")
        if action == "open package":
            if n < STAGES.index("unwrapped"):
                state["stage"] = "unwrapped"
                state["objects"]["box"] = {
                    "instance_id": f"{uid}:terrace:box:v1",
                    "holder": state["objects"]["package"]["instance_id"],
                }
                _remember(state, "package.opened")
                text = "The wrapping gives easily. Inside is an antique locked box."
            else:
                text = "The wrapping is already open. The antique box remains inside."
        else:
            _require(n >= STAGES.index("unwrapped"), "Open the wrapping first.")
            if action == "inspect box":
                title = "The antique box"
                _remember(state, "box.inspected")
                text = "An old box with a small lock." if n < STAGES.index("unlocked") else "The old box is unlocked."
                if opening_state(character):
                    text += " The key at your neck touches your chest."
            elif action == "unlock box":
                if n < STAGES.index("unlocked"):
                    _require(opening_state(character) is not None,
                             "No matching neck key is established for this arrival.")
                    state["stage"] = "unlocked"
                    _remember(state, "box.unlocked")
                    text = "You remember the key at your neck. It fits. The key turns."
                else:
                    text = "The box is already unlocked."
            else:
                _require(n >= STAGES.index("unlocked"), "The antique box is locked.")
                if action == "open box":
                    if n < STAGES.index("open"):
                        state["stage"] = "open"
                        state["objects"]["usb"] = {
                            "instance_id": f"{uid}:terrace:usb:v1",
                            "holder": state["objects"]["box"]["instance_id"],
                            "lineage": f"{uid}:terrace:delivery:v1",
                            "temporal_validity": "provisional",
                            "content_integrity": "unexamined", "future_condition": "unresolved",
                        }
                        _remember(state, "box.opened")
                        text = "Inside the box is a USB. A small label reads: **tunes**."
                    else:
                        text = "The box is open." + (" The USB is inside." if n == STAGES.index("open") else " It is empty.")
                else:
                    _require(n >= STAGES.index("open"), "Open the box before reaching for its contents.")
                    if action == "inspect usb":
                        title = "tunes"
                        _remember(state, "usb.label_read")
                        text = "An ordinary-looking USB. Its label reads **tunes**. You have not examined the files."
                    elif action == "take usb":
                        if n < STAGES.index("usb_collected"):
                            state["stage"] = "usb_collected"
                            state["objects"]["usb"]["holder"] = str(uid)
                            _remember(state, "usb.collected")
                            text = "You lift out the USB marked **tunes**."
                        else:
                            text = "You already carry the USB marked **tunes**."
    hint = guidance(updated)
    return updated, (title, text, hint[1] if hint else "Use `!terrace` or `!inventory`.")


def secure_delivery(character):
    """Recovery adapter; preserve scene identity while moving held objects to pod."""
    state = state_of(character)
    if not state or rank(state) < STAGES.index("collected") or state.get("secured_in_pod"):
        return character
    updated = deepcopy(character)
    state = updated["extra"][KEY]
    state["secured_in_pod"] = True
    state["objects"]["package"]["holder"] = "pod_delivery"
    if state["stage"] == "usb_collected":
        state["objects"]["usb"]["holder"] = "pod_delivery"
    return updated


def release_delivery(character):
    """Called by successful pod collection, within its character transaction."""
    state = state_of(character)
    if not state or not state.get("secured_in_pod"):
        return character
    updated = deepcopy(character)
    state = updated["extra"][KEY]
    state["secured_in_pod"] = False
    state["objects"]["package"]["holder"] = state["owner"]
    if state["stage"] == "usb_collected":
        state["objects"]["usb"]["holder"] = state["owner"]
    return updated


def secured_inventory_lines(character):
    state = state_of(character)
    if not state or not state.get("secured_in_pod"):
        return []
    preview = deepcopy(character)
    preview["extra"][KEY]["secured_in_pod"] = False
    return inventory_lines(preview)
