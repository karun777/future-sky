"""One-time, character-scoped pod discovery and item exchange.

No mutation of shared room inventories; each player can find their own token.
"""
from copy import deepcopy

TOKEN = "itm_pod_brass_token"


class ExchangeError(ValueError):
    pass


def discover_token(character: dict) -> dict:
    if character.get("current_room") != "pod_room":
        raise ExchangeError("You must be inside the transit pod.")
    updated = deepcopy(character)
    arrival = updated.setdefault("extra", {}).setdefault("arrival", {})
    if arrival.get("brass_token_found"):
        raise ExchangeError("The loose panel is empty. You already searched here.")
    arrival["brass_token_found"] = True
    bag = updated.setdefault("bag", {})
    bag[TOKEN] = int(bag.get(TOKEN, 0)) + 1
    return updated


def exchange_token(character: dict) -> dict:
    if character.get("current_room") != "neptune_lounge":
        raise ExchangeError("The counterkeeper is in Neptune Lounge.")
    updated = deepcopy(character)
    arrival = updated.setdefault("extra", {}).setdefault("arrival", {})
    if arrival.get("brass_token_exchanged"):
        raise ExchangeError("The counterkeeper already has your token.")
    bag = updated.setdefault("bag", {})
    if int(bag.get(TOKEN, 0)) < 1:
        raise ExchangeError("You have no brass token to offer.")
    bag[TOKEN] = int(bag[TOKEN]) - 1
    if bag[TOKEN] == 0:
        del bag[TOKEN]
    arrival["brass_token_exchanged"] = True
    updated.setdefault("flags", {})["counterkeeper_token_received"] = True
    return updated
