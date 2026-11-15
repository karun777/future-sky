"""Berth console composition used only inside a fictional rehearsal process."""
from copy import deepcopy

from fsbot.pod_inspection import inspect_pod, web_targets
from fsbot.pod_opening import opening_state

READER = "123"  # Synthetic actor from the shared walking fixture.
MEMORY = "w4f13_rehearsal"
USE = "console use note"
MARK = "console mark sketch"
LEAVE = "console leave"
PRIVATE = {"console", "note", "sketch", "probe slip", USE, MARK, LEAVE}

CONSOLE = "You tip the little keyboard out. A folded slip catches in the hinge. A cursor wakes on the glass."
NOTE = "The folded face reads ‘password’. Inside, in smaller letters, ‘underblue’. You turn the slip over. The back is blank."
FIRST_OPEN = ("You key in the word. A pencil drawing fills the glass, open halfway down a flight of stairs. "
              "There’s an old slip pinned across one corner, headed PROBE.\n\nYours, you suppose.")
RETURN = "The sketch and the probe slip are still where you found them."
BOOKMARK = "The little crescent you left sits beside the rubbed-through fork."
SLIP = ("‘Bring the probe back before they clear the bench.’\n\n"
        "The last four words crowd into the margin. There’s space for a reply underneath.")
SKETCH = ("Below the second flight the stair divides. One pencil line shines where a thumb "
          "has rubbed it nearly away. The other stops at a little square with an open side.")
DESK_GUIDE = "Try inspect sketch, inspect probe slip or console leave."


class WorkspaceScene:
    """One enrolled fictional reader. A screen stays open only for this pod visit."""

    def __init__(self, bot, navigation):
        self.storage = bot.storage
        self.navigation = navigation
        self.open_revision = None

    def is_open(self):
        return self.open_revision == self.navigation.walk_revision(READER)

    def targets(self, character):
        targets = web_targets(character)
        if not targets or character is not self.storage.characters.get(READER):
            return targets
        known = opening_state(character)["discoveries"]
        if "berth" not in known:
            return targets
        memory = character["extra"].get(MEMORY, {})
        targets.append("console")
        if memory.get("console"):
            targets.extend(["note", LEAVE])
        if memory.get("note"):
            targets.append(USE)
        if self.is_open():
            targets.extend(["sketch", "probe slip"])
            if memory.get("sketch"):
                targets.append(MARK)
        return targets

    def remember(self, character, fact):
        if character["extra"].get(MEMORY, {}).get(fact):
            return
        updated = deepcopy(character)
        updated["extra"].setdefault(MEMORY, {})[fact] = True
        self.storage.characters[READER] = updated
        try:
            self.storage.save_characters()
        except Exception:
            self.storage.characters[READER] = character
            raise

    def inspect(self, storage, uid, target=None):
        if target not in PRIVATE:
            result = inspect_pod(storage, uid, target)
            if uid == READER and target == "berth":
                result["text"] += " Level with your elbow, a row of narrow keys lies flush with the berth frame. The space bar has a hollow the width of a thumb."
                result["guidance"] += " You can inspect console."
            return result

        character = storage.characters.get(uid)
        if uid != READER or target not in self.targets(character):
            raise ValueError("That detail is unavailable.")

        memory = character["extra"].get(MEMORY, {})
        title, guidance = "The berth console", DESK_GUIDE
        if target == "console":
            self.remember(character, "console")
            text, guidance = CONSOLE, "Try inspect note or console leave."
            if memory.get("note"):
                guidance += " Use the slip again with console use note."
        elif target == "note":
            self.remember(character, "note")
            title, text = "The folded slip", NOTE
            guidance = "Try console use note or console leave."
        elif target == USE:
            title = "An open workspace"
            text = FIRST_OPEN if not memory.get("visited") else RETURN
            if memory.get("marked"):
                title = "The fork in the stair"
                text = BOOKMARK + " " + SKETCH
            self.remember(character, "visited")
            self.open_revision = self.navigation.walk_revision(READER)
        elif target == "probe slip":
            title, text = "A slip headed PROBE", SLIP
        elif target == "sketch":
            self.remember(character, "sketch")
            title, text = "A stair drawn in pencil", SKETCH
            if memory.get("marked"):
                text += " " + BOOKMARK
            guidance = "Try console mark sketch, inspect probe slip or console leave."
        elif target == MARK:
            self.remember(character, "marked")
            title = "Your reading mark"
            text = BOOKMARK if memory.get("marked") else "You leave a little crescent beside the fork so you can find this spot again."
        else:  # LEAVE
            self.open_revision = None
            text = "You ease the keys back into their recess. The woven cover brushes your wrist."
            guidance = "You are beside the berth. Look around or take an ordinary exit."
        return {"title": title, "text": text, "guidance": guidance, "room": "pod_room",
                "target": target, "image": None}
