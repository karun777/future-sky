"""Small, persistent bar labour exchange. Real-time cooldown."""
from copy import deepcopy
from datetime import datetime, timezone
from fsbot.intoxication import level_at

PAY = 5
COOLDOWN_SECONDS = 300


class WorkError(ValueError):
    pass


def work_bar(character, now=None):
    now = int(datetime.now(timezone.utc).timestamp()) if now is None else int(now)
    if character.get("current_room") != "neptune_lounge":
        raise WorkError("The bartender is back at Neptune Lounge.")
    if level_at(character, now) >= 3:
        raise WorkError("The bartender eyes your unsteady hands. 'Come back when you're a bit steadier, mate.'")
    ledger = character.get("work", {})
    if not isinstance(ledger, dict):
        raise WorkError("Your work record is unavailable.")
    last = ledger.get("bar_last_paid_at")
    if last is not None:
        if type(last) is not int:
            raise WorkError("Your work record is invalid.")
        remaining = COOLDOWN_SECONDS - (now - last)
        if remaining > 0:
            raise WorkError(f"The glasses are still clean. Another shift in {remaining} seconds.")
    credits = character.get("credits", 20)
    if type(credits) is not int or credits < 0:
        raise WorkError("Your credit balance is invalid.")
    updated = deepcopy(character)
    updated["credits"] = credits + PAY
    updated.setdefault("work", {})["bar_last_paid_at"] = now
    updated["work"]["bar_shifts_completed"] = int(ledger.get("bar_shifts_completed", 0)) + 1
    return updated, (
        "You collect glasses, wipe tables, and help the bartender clear the bar. "
        f"'Good on you, mate.' You earn {PAY} credits. Balance: {updated['credits']} credits."
    )
