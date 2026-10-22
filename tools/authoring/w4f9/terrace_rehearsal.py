"""Disposable W4-F9 authoring rehearsal; never imported by the bot.

Synthetic scene IDs, explicit attention actions and fixture-key availability
are demonstration choices, not adopted world rules. No clock or future-send
mechanic. All persistence is inside an internally-created temporary directory.
"""
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
import argparse
import json
import os

MARKER = "w4f9-fictional-rehearsal-v1"
TERRACE = "rehearsal_terrace"
LOUNGE = "rehearsal_lounge"
ACTIONS = ("look", "attend", "notice sky", "inspect package", "take package",
           "open package", "inspect box", "unlock box", "open box", "take usb",
           "inventory", "leave", "return")


class SceneError(ValueError):
    pass


def fictional_character(name, *, enrolled=True, booking_known=True,
                        neck_key=True, recognises_name=None):
    return {
        "name": name, "room": TERRACE, "scenario_enrolled": enrolled,
        "booking_known": booking_known, "neck_key_available": neck_key,
        "recognises_name": recognises_name, "attention": False,
        "inventory": [], "scene": {}, "knowledge": [],
    }


class FixtureStore:
    """Owns only temporary fictional JSON; no caller-supplied storage path."""
    def __init__(self, characters=None):
        self._temp = TemporaryDirectory(prefix="futuresky-w4f9-fictional-")
        self.path = Path(self._temp.name) / "fixture.json"
        self.fail_next_save = False
        self.save({
            "kind": MARKER,
            "characters": deepcopy(characters or {
                "fixture-a": fictional_character("Rehearsal Traveller"),
                "fixture-b": fictional_character("Other Fictional Traveller"),
            }),
            "objects": {}, "facts": [],
        })

    def close(self):
        self._temp.cleanup()

    def load(self):
        data = json.loads(self.path.read_text())
        if data.get("kind") != MARKER:
            raise ValueError("Not a fictional rehearsal store.")
        return data

    def save(self, data):
        if data.get("kind") != MARKER:
            raise ValueError("Only fictional rehearsal state is accepted.")
        if self.fail_next_save:
            self.fail_next_save = False
            raise OSError("Injected fixture write failure")
        temporary = self.path.with_suffix(".pending")
        try:
            with temporary.open("w") as stream:
                json.dump(data, stream, indent=2, sort_keys=True)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, self.path)
        finally:
            if temporary.exists():
                temporary.unlink()


def object_id(uid, kind):
    return f"{uid}:terrace-delivery:{kind}"


def _require(condition, message):
    if not condition:
        raise SceneError(message)


def _record(state, uid, kind, **details):
    state["facts"].append({"id": len(state["facts"]) + 1,
                           "actor": uid, "kind": kind, "details": details})


def transition(original, uid, action):
    """Pure serial transition; presenter saves before showing the returned text."""
    _require(uid in original["characters"], "Unknown fictional traveller.")
    state = deepcopy(original)
    ch = state["characters"][uid]
    scene = ch["scene"]
    action = " ".join(action.casefold().split())
    _require(action in ACTIONS, "Choose one of the listed rehearsal actions.")
    package = state["objects"].get(object_id(uid, "package"))
    box = state["objects"].get(object_id(uid, "box"))
    usb = state["objects"].get(object_id(uid, "usb"))

    if action == "look":
        if ch["room"] != TERRACE:
            return original, "You are back inside the fictional Lounge."
        text = ("From the terrace, Triton Central spreads beneath you in light. "
                "Docked ships hang against Neptune. The music is quieter here.")
        if ch["booking_known"]:
            text += " Tomorrow night. What are you going to play?"
        if package and package["holder"] == TERRACE:
            text += " A package lies where it landed."
        return original, text

    if action == "inventory":
        entries = [state["objects"][key]["label"] for key in ch["inventory"]]
        text = "Carrying: " + (", ".join(entries) if entries else "nothing from this rehearsal")
        return original, text

    if action in ("leave", "return"):
        destination = LOUNGE if action == "leave" else TERRACE
        if ch["room"] == destination:
            return original, "You are already there."
        ch["room"] = destination
        _record(state, uid, "fixture.moved", destination=destination)
        return state, ("You leave the terrace." if action == "leave"
                       else "You return to the terrace.")

    if action in ("attend", "notice sky"):
        _require(ch["room"] == TERRACE, "The terrace is not in view.")
        _require(ch["scenario_enrolled"] and ch["booking_known"],
                 "No performance-delivery encounter is established for this fixture.")
        if package:
            return original, "The delivery has already happened. You can attend to the package."
        if action == "attend":
            if ch["attention"]:
                return original, "You remain with the view and the question of tomorrow's music."
            ch["attention"] = True
            _record(state, uid, "terrace.attended")
            return state, ("You linger at the rail. Neptune holds your attention. "
                           "Tomorrow's music problem stays with you.")
        _require(ch["attention"], "First take a moment to attend to the view.")
        state["objects"][object_id(uid, "package")] = {
            "kind": "package", "label": "warm addressed package",
            "holder": TERRACE, "addressee": ch["name"],
            "lineage": f"{uid}:future-send-unresolved",
        }
        scene["delivery_received"] = True
        _record(state, uid, "package.landed", instance=object_id(uid, "package"))
        return state, ("A shooting star? It slips between docked ships, disappears against "
                       "Neptune, then appears closer. Coming here. Before you can respond, "
                       "it gently streaks down. A soft impact at your feet. "
                       "The last bright tendrils of wrapping burn away.")

    _require(package is not None, "There is no delivered package to examine.")
    accessible = package["holder"] == uid or (
        package["holder"] == TERRACE and ch["room"] == TERRACE)
    _require(accessible, "The package is not within reach.")

    if action == "inspect package":
        if "package_address" not in ch["knowledge"]:
            ch["knowledge"].append("package_address")
            _record(state, uid, "package.address_read")
        text = f"The label reads: {package['addressee']}."
        if ch["recognises_name"] is True:
            text += " Yours. The name is familiar, though much else remains beyond reach."
        elif ch["recognises_name"] is False:
            text += " You can read the name. It does not yet feel like yours."
        else:
            text += " A readable name; whether you recognise it as yours remains open."
        return state, text

    if action == "take package":
        if package["holder"] == uid:
            return original, "You already carry the package."
        package["holder"] = uid
        ch["inventory"].append(object_id(uid, "package"))
        _record(state, uid, "package.collected")
        return state, "You lift the package. Warm, but comfortable to hold."

    _require(package["holder"] == uid, "Pick up the package before opening it.")
    if action == "open package":
        if scene.get("wrapper_open"):
            return original, "The wrapping is already open. The antique box remains inside."
        scene["wrapper_open"] = True
        state["objects"][object_id(uid, "box")] = {
            "kind": "box", "label": "antique locked box",
            "holder": object_id(uid, "package"),
            "locked": True, "open": False,
        }
        _record(state, uid, "package.opened")
        return state, "The wrapping gives easily. Inside is an antique locked box."

    _require(box is not None, "Open the wrapping to see what is inside.")
    if action == "inspect box":
        if "box_seen" not in ch["knowledge"]:
            ch["knowledge"].append("box_seen")
            _record(state, uid, "box.inspected")
        text = "An old box with a small lock." if box["locked"] else "The old box is unlocked."
        if ch["neck_key_available"]:
            text += " The key at your neck touches your chest."
        return state, text

    if action == "unlock box":
        if not box["locked"]:
            return original, "The box is already unlocked."
        _require(ch["neck_key_available"], "The lock waits. No matching neck key is established.")
        box["locked"] = False
        _record(state, uid, "box.unlocked", key="fixture-neck-key")
        return state, "You remember the key at your neck. It fits. The key turns."

    if action == "open box":
        _require(not box["locked"], "The antique box is locked.")
        if box["open"]:
            return original, ("The box is open. The USB is inside."
                              if usb["holder"] == object_id(uid, "box")
                              else "The box is open and empty.")
        box["open"] = True
        state["objects"][object_id(uid, "usb")] = {
            "kind": "usb", "label": "USB marked tunes",
            "holder": object_id(uid, "box"),
            "lineage": package["lineage"], "temporal_validity": "provisional",
            "content_integrity": "unexamined", "future_condition": "unresolved",
        }
        ch["knowledge"].append("usb_label_tunes")
        _record(state, uid, "box.opened")
        return state, "Inside the box is a USB. A small label reads: tunes."

    _require(action == "take usb", "That action is not available.")
    _require(box["open"] and usb is not None, "Open the box before reaching for its contents.")
    if usb["holder"] == uid:
        return original, "You already carry the USB marked tunes."
    _require(usb["holder"] == object_id(uid, "box"), "The USB is not in the box.")
    usb["holder"] = uid
    ch["inventory"].append(object_id(uid, "usb"))
    _record(state, uid, "usb.collected", instance=object_id(uid, "usb"))
    return state, ("You lift out the USB marked tunes. You have not examined its files "
                   "or learned who sent it.")


class Rehearsal:
    def __init__(self, store):
        self.store = store

    def act(self, action, uid="fixture-a"):
        original = self.store.load()
        try:
            updated, text = transition(original, uid, action)
        except SceneError as exc:
            return str(exc)
        if updated != original:
            try:
                self.store.save(updated)
            except OSError:
                return "The rehearsal could not save that action. Nothing new is confirmed; try again."
        return text


DEMO = ("look", "attend", "notice sky", "inspect package", "take package",
        "open package", "inspect box", "unlock box", "open box", "take usb",
        "inventory", "leave", "return", "notice sky", "take usb")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--interactive", action="store_true",
                        help="Try actions against a disposable fictional save.")
    args = parser.parse_args()
    store = FixtureStore()
    rehearsal = Rehearsal(store)
    print("W4-F9 FICTIONAL REHEARSAL — no live character or world changes.")
    print("Attention actions, eligibility and fixture key are review assumptions.")
    try:
        if args.interactive:
            print("Actions: " + " | ".join(ACTIONS) + " | quit")
            while True:
                try:
                    action = input("> ")
                except EOFError:
                    break
                if action.strip().casefold() == "quit":
                    break
                print(rehearsal.act(action))
        else:
            for action in DEMO:
                print(f"\n> {action}\n{rehearsal.act(action)}")
    finally:
        store.close()


if __name__ == "__main__":
    main()
