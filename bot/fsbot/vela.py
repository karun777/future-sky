"""Dragonfly crew call in the pod, Vela's table in the wing, and the crew next door."""
import json
from pathlib import Path

from fsbot.encounter_memory import EncounterMemory, EncounterUnavailable
from fsbot.recovery import recovering

KEY = "vela_table_v1"
POD = "pod_room"
TABLE = "lounge_conference_wing"
BRIEFING = "lounge_conference_room_a"
SCRIPT = json.loads(Path(__file__).with_name("vela_table.json").read_text(encoding="utf-8"))
FACTS = SCRIPT["observations"]


def _ready(ch):
    return (isinstance(ch, dict) and isinstance(ch.get("extra", {}), dict)
            and not ch.get("in_cube") and not recovering(ch)
            and not (ch.get("flags") or {}).get("in_combat")
            and not (ch.get("extra", {}).get("thread_nodes") or {}).get("active_thread_node"))


def offer_crew_call(storage, uid):
    """Story entry point. Offering the call leaves it unread and the job open."""
    ch = storage.characters.get(uid)
    if not isinstance(ch, dict):
        raise EncounterUnavailable("Character unavailable.")
    EncounterMemory.read(ch, KEY).witness("invited").save(storage, uid, KEY)


def _orders(memory):
    return [row["order"] if row["id"] in memory.shared else row["draft"] for row in FACTS]


def _card(memory):
    return "Dragonfly · Approach card\n" + "\n".join(_orders(memory))


def journal(memory):
    notes = [row["note"] for row in FACTS if row["id"] in memory.seen]
    if "beacon" in memory.seen:
        notes.insert(0, "Vela’s double tap means the beacon is lit.")
    if "invited" in memory.seen:
        status = "read" if "read" in memory.seen else "unread"
        notes.insert(0, f"Dragonfly Rescue · Crew call open ({status}). Meet at Neptune Lounge.")
    if memory.shared:
        notes.append(_card(memory))
    return notes


def _scene(room, memory):
    if room == POD and "read" not in memory.seen:
        return "Behind your eyes, the words DRAGONFLY RESCUE glimmer. A crew call is waiting.", ["read crew call"]
    actions = ["read crew call"]
    if room == TABLE:
        actions.append("inspect chart")
        if "beacon" not in memory.seen:
            actions.append("tap back")
            return SCRIPT["table"], actions
        actions.extend(row["play"] for row in FACTS if row["id"] != "gap" or "returned" in memory.seen)
        if "gap" in memory.seen:
            return SCRIPT["after"], actions
        if "returned" in memory.seen:
            return SCRIPT["recalled"], actions
        return SCRIPT["shared"], actions
    if room == BRIEFING:
        actions.extend(row["report"] for row in FACTS if row["id"] in memory.seen and row["id"] not in memory.shared)
        actions.append("stay quiet")
        return SCRIPT["briefing"] + "\n\n" + _card(memory), actions
    return ("Vela has laid her chart out in the conference wing at Neptune Lounge. "
            "The crew is briefing in the room just north of her table."), actions


def view(ch):
    if not _ready(ch):
        return None
    try:
        memory = EncounterMemory.read(ch, KEY)
    except EncounterUnavailable:
        return None
    room = ch.get("current_room")
    if "invited" not in memory.seen:
        return None
    prose, actions = _scene(room, memory)
    return {"message": prose, "commands": actions, "journal": journal(memory),
            "marks": [row["id"] for row in FACTS if row["id"] in memory.seen],
            "at_table": room == TABLE, "at_briefing": room == BRIEFING}


def act(storage, uid, command):
    ch = storage.characters.get(uid)
    current = view(ch)
    if not current:
        raise EncounterUnavailable("There is no crew call available here.")
    command = " ".join(command.lower().split())
    if not command:
        return current["message"]
    if command not in current["commands"]:
        raise EncounterUnavailable("That action is unavailable here. Check Vela’s current commands.")
    memory = EncounterMemory.read(ch, KEY)
    if command == "read crew call":
        memory.witness("read").save(storage, uid, KEY)
        return SCRIPT["invitation"] + "\n\nVela has the chart in the conference wing."
    if command == "inspect chart":
        return "\n".join([SCRIPT["chart"]] + [row["mark"] for row in FACTS if row["id"] in memory.seen])
    if command == "tap back":
        memory.witness("beacon").save(storage, uid, KEY)
        return SCRIPT["shared"]
    if command == "stay quiet":
        return SCRIPT["quiet"] + "\n\n" + _card(memory)
    for row in FACTS:
        if command == row["play"]:
            memory.witness(row["id"]).save(storage, uid, KEY)
            return row["scene"]
        if command == row["report"]:
            updated = memory.report(row["id"])
            updated.save(storage, uid, KEY)
            return row["reply"] + "\n\n" + _card(updated)
    raise EncounterUnavailable("That action is unavailable.")


def returned_to_table(storage, uid, previous, destination):
    if destination != TABLE or previous == destination:
        return False
    ch = storage.characters.get(uid)
    if not _ready(ch) or ch.get("current_room") != TABLE:
        return False
    memory = EncounterMemory.read(ch, KEY)
    if "beacon" not in memory.seen or "returned" in memory.seen:
        return False
    memory.witness("returned").save(storage, uid, KEY)
    return True
