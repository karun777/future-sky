"""First impression: a provisional, one-time NPC observation, never an identity verdict."""

REACTIONS = {
    "pod_utility": ("The Service Runner", "A service runner glances at your workwear. “Shift change? You're early.” Then it looks at your face, hesitates, and checks its schedule again."),
    "pod_formal": ("The Door Attendant", "The attendant's posture straightens at the sight of your immaculate uniform. “My apologies. I thought you were—” The sentence disappears behind a careful smile."),
    "pod_technical": ("The Maintenance Hand", "A maintenance hand catches the light running along your seams. “You know what those loops are for?” Their eyes narrow. “No? Interesting.”"),
    "pod_freeform": ("The Counterkeeper", "The counterkeeper notices the embroidered motif at your shoulder. Their hand stops halfway to a glass. “Where did you get that?” They look away before you can answer."),
}


def first_impression(character: dict, room_id: str) -> tuple[str, str] | None:
    """React to current worn pod attire, not remembered identity or past choice."""
    if room_id != "neptune_lounge":
        return None
    extra = character.get("extra") or {}
    if (extra.get("arrival") or {}).get("first_impression_seen"):
        return None
    selected = (extra.get("arrival") or {}).get("pod_uniform_selected")
    if not selected:
        return None
    expected_item = "itm_" + selected.replace("pod_", "pod_uniform_", 1)
    if (character.get("equipped") or {}).get("chest") != expected_item:
        return None
    return REACTIONS.get(selected)
