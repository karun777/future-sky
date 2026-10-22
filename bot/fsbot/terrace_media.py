"""Transient arrival art; explicit memory view never replays the occurrence."""
from fsbot.terrace_delivery import state_of, rank

ASSET_ROOT = "assets/images/world/manzo/triton_central/neptune_lounge/terrace_delivery/v1"
ARRIVAL_URL = "https://future-sky.net/" + ASSET_ROOT + "/arrival.webp"

def arrival_image(previous, current, request):
    if current.get("in_cube"):
        return None
    before, after = state_of(previous), state_of(current)
    if rank(after) < 1:
        return None
    action = " ".join(request.casefold().split())
    if action == "arrival":
        return ARRIVAL_URL
    if action in {"sky", "notice sky"} and rank(before) == 0 and rank(after) == 1:
        return ARRIVAL_URL
    return None
