"""Offer the existing HUD only to saved characters admitted by the running pilot."""
URL = "https://future-sky.net/play/"


def window_handoff(bot, uid):
    uid = str(uid)
    portal = getattr(bot, "get_cog", lambda name: None)("WebPortalCog")
    if (portal is None or uid not in getattr(portal, "allowed_ids", frozenset())
            or not isinstance(bot.storage.characters.get(uid), dict)):
        return ""
    return (f"[Open your game window]({URL}) — sign in with this Discord account. "
            "Your character is shared between Discord and the window. "
            "Read the room, then type a suggested command beneath the text.")
