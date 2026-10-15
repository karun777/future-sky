"""Social resolution of Neptune Lounge's bouncer encounter."""
from copy import deepcopy

CHOICES = ("apologise", "buy", "charm", "bluff")


class BouncerError(ValueError):
    pass


def resolve_bouncer(character, choice):
    if character.get("current_room") != "neptune_lounge":
        raise BouncerError("The bouncer is back at Neptune Lounge.")
    if not character.get("social_flags", {}).get("neptune_bouncer_pending"):
        raise BouncerError("The bouncer isn't waiting for you.")
    choice = (choice or "").strip().casefold()
    if choice not in CHOICES:
        raise BouncerError("Try !bouncer apologise, buy, charm, or bluff.")
    updated = deepcopy(character)
    flags = updated["social_flags"]
    if choice == "buy":
        credits = updated.get("credits", 20)
        if type(credits) is not int or credits < 5:
            raise BouncerError("The bouncer points to the bar. You need 5 credits to buy a round.")
        updated["credits"] = credits - 5
        message = ("You buy the house a round for 5 credits. The bouncer nods. "
                   f"Fair enough. Balance: {updated['credits']} credits.")
    elif choice == "apologise":
        message = "Sorry, mate, you say. The bouncer studies you, then steps aside. Just ask next time."
    elif choice == "charm":
        message = ("You compliment the Lounge's hospitality. The bouncer almost smiles. "
                   "Flattery won't get you another free one, mate.")
    else:
        message = ("You insist the bottles were yours all along. The bouncer raises one eyebrow. "
                   "Sure they were. Don't push your luck.")
    flags["neptune_bouncer_pending"] = False
    flags["neptune_bouncer_resolved"] = True
    return updated, message
