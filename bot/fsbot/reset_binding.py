"""Read-only bridge from an operator reset receipt into guided creation.

The future stopped-service adapter owns this private receipt. It contains only
account/channel identity, not character progress. Routing still checks Discord
access and conflicting claims before delivery. Never discovers by name.
"""
import json
from pathlib import Path
from fsbot.config import RESET_RUN_BINDINGS_FILE


def apply_reset_binding(character, characters):
    path = Path(RESET_RUN_BINDINGS_FILE)
    try:
        raw = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return
    receipt = json.loads(raw)
    validate_reset_binding(receipt, character, characters)


def validate_reset_binding(receipt, character, characters):
    if (not isinstance(receipt, dict) or set(receipt) != {"version", "bindings"}
            or receipt["version"] != 1 or not isinstance(receipt["bindings"], dict)):
        raise ValueError("Invalid reset channel receipt")
    seen = set()
    for uid, binding in receipt["bindings"].items():
        if not (isinstance(uid, str) and uid.isascii() and uid.isdecimal() and str(int(uid)) == uid and int(uid)>0):
            raise ValueError("Invalid account ID")
        if not isinstance(binding, dict) or set(binding) != {"run_channel_id", "run_seeded_channel_id"}:
            raise ValueError("Invalid channel binding")
        channel = binding["run_channel_id"]
        if not (isinstance(channel, str) and channel.isascii() and channel.isdecimal() and int(channel)>0 and str(int(channel)) == channel):
            raise ValueError("Invalid channel ID")
        seeded = binding["run_seeded_channel_id"]
        if seeded is not None and (type(seeded) is not int or str(seeded) != channel):
            raise ValueError("Invalid seeded-channel marker")
        if int(channel) in seen:
            raise ValueError("Duplicate reset channel claim")
        seen.add(int(channel))
    uid = str(character["id"])
    binding = receipt["bindings"].get(uid)
    if binding is None:
        return
    for other_uid, other in characters.items():
        if str(other_uid) != uid and isinstance(other, dict):
            if str(other.get("run_channel_id")) == binding["run_channel_id"]:
                raise ValueError("Channel claimed by another character")
    character.update(binding)
