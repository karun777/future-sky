"""Legacy intoxication namespace now presents psychedelic microvita effects.
Intensity still accumulates and fades in real elapsed time.

No combat or movement penalties in this feather; descriptive effects only.
"""
from copy import deepcopy
from datetime import datetime, timezone

DECAY_SECONDS = 900
MAX_LEVEL = 6
KEY = "intoxication"


def level_at(character, now=None):
    now = int(datetime.now(timezone.utc).timestamp()) if now is None else int(now)
    state = character.get(KEY, {})
    if not isinstance(state, dict):
        return 0
    level, timestamp = state.get("level", 0), state.get("updated_at", now)
    if type(level) is not int or type(timestamp) is not int:
        return 0
    return max(0, min(MAX_LEVEL, level) - max(0, now - timestamp) // DECAY_SECONDS)


def description(level):
    if level <= 0:
        return "Clear-headed. Neptune's horizon is steady."
    if level == 1:
        return "A pleasant warmth settles behind your eyes."
    if level == 2:
        return "The neon acquires intricate depth; the music feels unusually vivid."
    if level == 3:
        return "The floor has acquired a gentle, suspicious sway."
    if level <= 5:
        return "Patterns gather in the light. The music seems to have texture."
    return "The stars are dancing in elaborate patterns. Sensation is intensely layered."


def drink(character, now=None):
    now = int(datetime.now(timezone.utc).timestamp()) if now is None else int(now)
    updated = deepcopy(character)
    level = min(MAX_LEVEL, level_at(updated, now) + 1)
    updated[KEY] = {"level": level, "updated_at": now}
    return updated, description(level)


def status(character, now=None):
    level = level_at(character, now)
    return level, description(level)
