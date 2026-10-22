"""Same-person bodily recovery. All possession transfers stay in characters.json."""
from copy import deepcopy
import json
from math import isfinite
from uuid import uuid4

DAY = 86400
DURATION = 7 * DAY


class RecoveryError(ValueError):
    pass


def record(character):
    value = (character.get("extra") or {}).get("recovery")
    return value if isinstance(value, dict) else None


def recovering(character):
    state = record(character)
    return bool(state and state.get("stage") in ("reanimating", "brain_review"))


def death_pile(character, items):
    """Equipping removes one bag unit. Two-handed mirrors count only once."""
    pile = {}
    for item, qty in character.get("bag", {}).items():
        if not isinstance(item, str) or not isinstance(qty, int) or isinstance(qty, bool) or qty < 0:
            raise RecoveryError("Inventory needs repair before recovery can begin.")
        if qty:
            pile[item] = qty
    equipped = character.get("equipped", {})
    for slot, item in equipped.items():
        if not item:
            continue
        if not isinstance(item, str):
            raise RecoveryError("Equipment needs repair before recovery can begin.")
        if slot == "off_hand" and equipped.get("main_hand") == item:
            definition = items.get(item, {})
            # CoreCog's canonical two-handed convention.
            if int((definition.get("equip") or {}).get("hands_required", 1)) >= 2:
                continue
        pile[item] = pile.get(item, 0) + 1
    return pile


def begin(character, now, items, *, cause, brain_intact=True):
    if recovering(character):
        return deepcopy(character)
    updated = deepcopy(character)
    extra = updated.setdefault("extra", {})
    pod = extra.setdefault("pod_delivery", {"items": {}, "receipts": []})
    pile = death_pile(character, items)
    for item, qty in pile.items():
        pod["items"][item] = pod["items"].get(item, 0) + qty
    receipt = uuid4().hex
    pod["receipts"].append({"id": receipt, "at": now, "items": pile})
    extra["recovery"] = {
        "version": 1, "id": receipt, "stage": "reanimating" if brain_intact else "brain_review",
        "cause": cause, "started_at": now, "ready_at": now + DURATION if brain_intact else None,
        "clock": "persisted_world_seconds", "brain": "recoverable" if brain_intact else "unresolved",
        "possessions_delivered_at": now, "from_room": character.get("current_room"),
    }
    updated["bag"] = {}
    updated["equipped"] = {}
    updated["current_room"] = "pod_room"
    updated.setdefault("stats", {})["hp"] = 0
    updated.setdefault("flags", {})["in_combat"] = False
    status = extra.setdefault("status", {})
    status["sneaking"] = False
    status["pending_return_echo"] = False
    updated.pop("pending_return_echo", None)
    from fsbot.terrace_delivery import secure_delivery
    return secure_delivery(updated)


def complete(character, now):
    state = record(character)
    if not state or state.get("stage") != "reanimating" or now < state["ready_at"]:
        return deepcopy(character)
    updated = deepcopy(character)
    updated["extra"]["recovery"].update(stage="ready", completed_at=now)
    updated["stats"]["hp"] = max(1, int(updated["stats"].get("max_hp", 20)))
    updated["current_room"] = "pod_room"
    return updated


class RecoveryService:
    def __init__(self, bot):
        self.bot = bot

    def now(self):
        # Do not use the soft in-memory clock: a failed heartbeat save can advance it.
        with open(self.bot.state.WORLD_CLOCK_FILE, encoding="utf-8") as stream:
            value = json.load(stream)["world_time_seconds"]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value) or value < 0:
            raise RecoveryError("The persisted world clock is unavailable.")
        return int(value)

    def commit(self, uid, updated):
        storage = self.bot.storage
        original = storage.characters[uid]
        if updated == original:
            return False
        storage.characters[uid] = updated
        try:
            storage.save_characters()
        except Exception:
            storage.characters[uid] = original
            raise
        return True

    def start(self, uid, *, cause="renewal", brain_intact=True, name=None, birthdate=None):
        original = self.bot.storage.characters[uid]
        if recovering(original):
            return False
        updated = begin(original, self.now(), self.bot.storage.items_db,
                        cause=cause, brain_intact=brain_intact)
        if name is not None:
            updated["name"] = name
        if birthdate is not None:
            updated["birthdate"] = birthdate
        return self.commit(uid, updated)

    def refresh(self, uid):
        character = self.bot.storage.characters[uid]
        if not recovering(character):
            return False
        return self.commit(uid, complete(character, self.now()))

    def collect(self, uid):
        self.refresh(uid)
        character = self.bot.storage.characters[uid]
        if recovering(character) or character.get("current_room") != "pod_room":
            raise RecoveryError("Collect your delivery in the pod after reanimation.")
        updated = deepcopy(character)
        pod = updated.get("extra", {}).get("pod_delivery", {})
        for item, qty in pod.get("items", {}).items():
            updated.setdefault("bag", {})[item] = updated.get("bag", {}).get(item, 0) + qty
        pod["items"] = {}
        from fsbot.terrace_delivery import release_delivery
        updated = release_delivery(updated)
        return self.commit(uid, updated)
