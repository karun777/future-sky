"""Authored pod-opening content. Pure selection; no file or world mutation."""
from copy import deepcopy

OPENING = "performance_arrival_v1"
INTRO = (
    "Cold blue light.\n\nYou lift your hands.\n"
    "They move when you mean them to.\n"
    "You turn them over. Open them. Close them.\n\n"
    "**You do not recognise them.**\n\n"
    "A breath comes. Something cold rests against your chest. "
    "A thin chain disappears beneath your garment.\n\n"
    "Beyond the wall: **THUMP. THUMP. THUMP.**\n\nMachinery. Probably."
)
GUIDANCE = (
    "Follow what catches your attention: `!inspect hands`, "
    "`!inspect garment` or `!inspect pod`."
)
# All targets below are fixtures/body observations, not portable item definitions.
TARGETS = {
    "hud": ("The display behind your eyes", "The markings stay with your field of vision when you turn away from the pod screen. "
            "An interface waits quietly for your attention. Signals and notices you discover can be revisited here. "
            "Your inward impressions are not messages from this display.",
            "Use `!hud` to review what you have found. `!hud off` hides the display; `!hud on` restores it."),
    "hands": ("Your hands", "They answer each movement. You turn them over slowly. "
              "Familiar control; unfamiliar hands. Looking closer does not give you a name.",
              "Try `!inspect body`, `!inspect garment` or `!inspect pod`."),
    "body": ("Breath and body", "You notice your breathing and the support beneath you. "
             "A faint vibration runs through you; you cannot tell whether it begins in the pod.",
             "Something cold touches your chest. Try `!inspect garment` or `!inspect chain`."),
    "garment": ("The transit garment", "The garment rests against your skin. A thin chain "
                "disappears beneath its collar. It tells you little about who you are.",
                "Follow the chain with `!inspect chain`, or survey the cubicle with `!inspect pod`."),
    "chain": ("The object at your chest", "A small metal key hangs from the chain. "
              "A worn loop of cord binds a little wooden cube to it. Circle, heart, crossed mark; "
              "the other symbols feel directional. You do not remember acquiring either object.",
              "Observation alone adds no item to your bag. Try `!inspect pod`."),
    "pod": ("The cubicle", "A berth, a frosted viewport and a hatch within reach. "
            "A red light burns beside a button. A welcome brochure protrudes from a dispenser. "
            "Storage panels occupy the side wall; their recessed grips invite a closer look.",
            "Try `!inspect panels`, `!inspect viewport`, `!inspect brochure` or `!inspect berth`."),
    "hatch": ("The hatch", "A solid panel separates the cubicle from the corridor. The light and button sit beside its frame.",
              "Use `!look` to see the existing route out, or examine `!inspect button`."),
    "viewport": ("The viewport", "Droplets merge and run down the glass. Blue light comes through, "
                 "but the outside does not resolve. Your movement returns as an incomplete reflection.",
                 "You can examine the fittings with `!inspect light` or turn to `!inspect panels`."),
    "reflection": ("Looking for your face", "You lean towards the viewport. Moisture and blue light "
                   "break up your reflection. It follows your movements, but gives you no clear face.",
                   "You have not found a clear mirror here. Try `!inspect panels` to look around."),
    "light": ("The status light", "A small steady red light. It is separate from the button below it. "
              "You cannot infer a hatch lock merely from its colour.",
              "Try `!inspect button` or `!inspect pod`."),
    "button": ("The red button", "A physical button beside the hatch. You examine its edge "
               "without pressing it. Its purpose is not labelled here.",
               "This inspection does not operate it. Try `!inspect brochure` or `!inspect panels`."),
    "brochure": ("Welcome to Triton Central", "The brochure unfolds.\n\n"
                 "**WELCOME TO TRITON CENTRAL**\nPlease enjoy your stay.\nPlease remain calm.\n"
                 "Please disregard any contradictory onboarding information.\n\n"
                 "A metallic crash sounds outside. The brochure does not acknowledge it.",
                 "Try `!inspect panels` or return to `!inspect pod`."),
    "panels": ("The side wall", "One recessed compartment is a wardrobe. Beside it, a small display "
               "flickers. A signal tile reads **FEED7**. Below it is a separate notification: "
               "**Performance booking**.",
               "Try `!inspect display`, `!inspect wardrobe` or open the compartment with `!wardrobe`."),
    "display": ("Signal and notification", "FEED7 flickers in one part of the display. "
                "A separate local booking notice waits beneath it. The notification is addressed to you.",
                "View the signal with `!feed7`. Read the notice with `!inspect booking`."),
    "wardrobe": ("The clothing compartment", "A recessed grip opens the clothing compartment. "
                 "There are outfits to examine before you enter the Lounge. "
                 "What you wear is not proof of a job, a faction or a remembered identity.",
                 "Use `!wardrobe` for the existing outfit choices. Review what you wear with `!fit`."),
    "berth": ("The berth", "The surface has supported your weight. Below its edge is a panel seam "
              "you can follow with your fingertips.",
              "Try the existing `!search panel` action, or turn to `!inspect panels`."),
    "booking": ("Tomorrow night", "**PERFORMANCE BOOKING — TOMORROW NIGHT**\n\n"
                "You have a gig.\n\nA DJ set? An instrument? Someone to play alongside? "
                "The notice gives you no set format, instrument or collaborator. "
                "You do not yet know what to prepare.",
                "The booking is remembered. `!look` returns to your bearings; "
                "`!wardrobe` offers somewhere practical to begin."),
}
ALIASES = {
    "telemetry": "hud", "goggles": "hud", "implant": "hud", "internal display": "hud",
    "hand": "hands", "my hands": "hands", "fingers": "hands", "palms": "hands",
    "breath": "body", "breathing": "body", "my body": "body",
    "clothes": "garment", "clothing": "garment", "transit garment": "garment",
    "neck": "chain", "chest": "chain", "key": "chain", "cube": "chain",
    "room": "pod", "cubicle": "pod", "walls": "pod", "door": "hatch",
    "grips": "panels", "dispenser": "brochure",
    "window": "viewport", "glass": "viewport", "condensation": "viewport",
    "mirror": "reflection", "face": "reflection", "my face": "reflection",
    "red light": "light", "status light": "light", "red button": "button",
    "leaflet": "brochure", "welcome brochure": "brochure",
    "storage": "panels", "compartment": "panels", "side wall": "panels",
    "screen": "display", "feed7": "display", "feed": "display",
    "bed": "berth", "panel": "berth", "loose panel": "berth",
    "notice": "booking", "notification": "booking", "gig": "booking",
    "performance booking": "booking",
}


def opening_state(character):
    extra = character.get("extra")
    arrival = extra.get("arrival") if isinstance(extra, dict) else None
    state = arrival.get("opening") if isinstance(arrival, dict) else None
    return state if isinstance(state, dict) and state.get("id") == OPENING else None


def scene_target(query):
    key = " ".join((query or "").casefold().split()).strip(".!?")
    key = ALIASES.get(key, key)
    return key if key in TARGETS else None


def prepare_observation(character, target=None):
    """Return copied character plus authored view. Caller persists before presenting."""
    updated = deepcopy(character)
    extra = updated.setdefault("extra", {})
    arrival = extra.setdefault("arrival", {})
    state = arrival.setdefault("opening", {"id": OPENING, "discoveries": []})
    if state.get("id") != OPENING:
        raise ValueError("Another opening is already recorded.")
    discoveries = state.setdefault("discoveries", [])
    if not isinstance(discoveries, list):
        raise ValueError("The pod cannot read your discovery record.")
    if target is None:
        return updated, ("POD // WHOSE HANDS ARE THESE?", INTRO, GUIDANCE)
    if target == "booking" and not any(k in discoveries for k in ("panels", "display")):
        return character, ("A notice?", "You have not located a booking notice yet.",
                           "Look around with `!inspect pod` and `!inspect panels`.")
    first = target not in discoveries
    if first:
        discoveries.append(target)
    title, text, guidance = TARGETS[target]
    hud = extra.get("hud") or {}
    hud_visible = hud.get("enabled", True) and hud.get("state") != "dark_mode"
    if target == "hands" and "hud_presence" not in discoveries and hud_visible:
        discoveries.append("hud_presence")
        text += ("\n\nAt the edge of your vision, small markings remain when you turn your head. "
                 "They are not on the wall. Something is displaying information within your sight.")
        guidance = "Examine the markings with `!inspect hud`, or follow `!inspect body`."
    if target == "hud":
        if not hud.get("enabled", True):
            text = "Your display is switched off. Your inward impressions remain your own."
        elif hud.get("state") == "dark_mode":
            text = "Your display is dimmed. Its information is concealed."
        elif hud.get("state") == "signal_degraded":
            text = "The display remains in your field of vision, but the signal is degraded. Information is unavailable."
    if target == "brochure" and not first:
        text = text.replace("A metallic crash sounds outside. The brochure does not acknowledge it.",
                            "The brochure offers the same reassurance as before.")
    return updated, (title, text, guidance)


def pod_bearings(character):
    state = opening_state(character)
    if not state or character.get("current_room") != "pod_room" or character.get("in_cube"):
        return None
    text = "You are in the pod. The world beyond the hatch continues without waiting for you."
    if "booking" in (state.get("discoveries") or []):
        text += "\n\nYou remember the notice: **a gig tomorrow night**. The format is still unclear."
    return text
