"""Approved Lounge room and arrival-route images; presentation only."""
ASSET_ROOT = "assets/images/world/manzo/triton_central/neptune_lounge/arrival_route/v1"
BASE_URL = "https://future-sky.net/" + ASSET_ROOT
STARDOCK_ASSET_ROOT = "assets/images/world/manzo/triton_central/neptune_lounge/stardock_overlook/v1"
STARDOCK_URL = "https://future-sky.net/" + STARDOCK_ASSET_ROOT + "/overlook.webp"
TERRACE_ASSET_ROOT = "assets/images/world/manzo/triton_central/neptune_lounge/open_terrace/v1"
TERRACE_URL = "https://future-sky.net/" + TERRACE_ASSET_ROOT + "/terrace.webp"
ROOM_IMAGES = {
    "hostel_hallway": "hallway.webp",
    "hostel_stairwell": "stairwell.webp",
    "neptune_lounge": "domefront.webp",
}

def lounge_image(character, target="room"):
    if character.get("in_cube"):
        return None
    room = character.get("current_room")
    if target == "room" and room == "lounge_conference_wing":
        return "https://future-sky.net/assets/images/world/manzo/triton_central/neptune_lounge/conference_wing/v1/conference.webp"
    if target == "room" and room == "lounge_smoking_terrace":
        return TERRACE_URL
    if target == "room" and room == "lounge_stardock_overlook":
        return STARDOCK_URL
    if target == "counterkeeper":
        filename = "counterkeeper.webp" if room == "neptune_lounge" else None
    elif target == "room":
        filename = ROOM_IMAGES.get(room)
    else:
        filename = None
    return BASE_URL + "/" + filename if filename else None
