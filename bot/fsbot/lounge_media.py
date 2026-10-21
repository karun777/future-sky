"""Approved W4-F8 arrival-route images; presentation only."""
ASSET_ROOT = "assets/images/world/manzo/triton_central/neptune_lounge/arrival_route/v1"
BASE_URL = "https://future-sky.net/" + ASSET_ROOT
ROOM_IMAGES = {
    "hostel_hallway": "hallway.webp",
    "hostel_stairwell": "stairwell.webp",
    "neptune_lounge": "domefront.webp",
}

def lounge_image(character, target="room"):
    if character.get("in_cube"):
        return None
    room = character.get("current_room")
    if target == "counterkeeper":
        filename = "counterkeeper.webp" if room == "neptune_lounge" else None
    elif target == "room":
        filename = ROOM_IMAGES.get(room)
    else:
        filename = None
    return BASE_URL + "/" + filename if filename else None
