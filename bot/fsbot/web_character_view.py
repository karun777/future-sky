"""Internal read-only projection for the future authenticated game window.

Not an HTTP endpoint or an authentication implementation. The caller must supply
the Discord ID obtained from a verified server-side session, never request input.
No Storage construction, saves, discovery grants, or game commands happen here.
"""
from copy import deepcopy
from urllib.parse import urlsplit

from fsbot.lounge_media import lounge_image
from fsbot.pod_media import pod_image


class CharacterAccessDenied(Exception):
    pass


def _object(value):
    return value if isinstance(value, dict) else {}


def _text(value):
    return value if isinstance(value, str) else None


def _image(url):
    # First release uses our existing same-origin art only.
    if not isinstance(url, str):
        return None
    parsed = urlsplit(url)
    if (parsed.scheme == "https" and parsed.netloc == "future-sky.net"
            and parsed.path.startswith("/assets/") and not parsed.query
            and not parsed.fragment):
        return url
    return None


def character_view(storage, verified_discord_id, *, allowed_discord_ids):
    """Project only the existing owner's character; fail closed for pilot access.

    Invoke synchronously on the bot's event loop. Returned objects are detached.
    allowed_discord_ids is server configuration, not a browser-supplied parameter.
    This function does not establish identity; the OAuth/session layer must do that.
    """
    uid = verified_discord_id
    if not isinstance(uid, str) or not uid.isascii() or not uid.isdecimal():
        raise CharacterAccessDenied()
    if uid not in allowed_discord_ids:
        raise CharacterAccessDenied()
    character = storage.characters.get(uid)
    if not isinstance(character, dict):
        raise CharacterAccessDenied()
    c = deepcopy(character)
    items = _object(getattr(storage, "items_db", {}))

    def item(key):
        definition = _object(items.get(key))
        return {"id": key, "name": _text(definition.get("name")) or key}

    bag = [
        dict(item(key), quantity=qty)
        for key, qty in _object(c.get("bag")).items()
        if isinstance(key, str) and type(qty) is int and qty > 0
    ]
    equipped = {
        slot: item(key) if isinstance(key, str) else None
        for slot, key in _object(c.get("equipped")).items()
        if isinstance(slot, str)
    }
    room_id = _text(c.get("current_room"))
    room = _object(storage.rooms.get(room_id))
    image = None
    if not c.get("in_cube"):
        image = _image(pod_image(c, "room") or lounge_image(c)
                       or room.get("image"))
    # Neither the full room record nor extra/flags contain only player knowledge.
    # Narrative, map, quest notes and telemetry need their existing renderers
    # adapted separately; do not return raw internal state as a shortcut.
    return {
        "schema_version": 1,
        "character": {"name": _text(c.get("name")),
                      "credits": c.get("credits") if type(c.get("credits")) is int else None},
        "location": {"id": None if c.get("in_cube") else room_id,
                     "title": None if c.get("in_cube") else _text(room.get("title")),
                     "image": image},
        "inventory": {"bag": bag, "equipped": equipped},
        "capabilities": {"read_only": True, "actions": []},
    }
