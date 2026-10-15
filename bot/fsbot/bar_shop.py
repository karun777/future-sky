"""Neptune Lounge bar purchases."""
from copy import deepcopy

BAR_ROOM = "neptune_lounge"
STARTING_CREDITS = 20
BAR_STOCK = {"Triton Lager": 5}

class BarError(ValueError):
    pass

def buy_from_bar(character, items, query):
    if character.get("current_room") != BAR_ROOM:
        raise BarError("You must be in Neptune Lounge to buy a drink.")
    needle = (query or "").strip().casefold()
    if not needle:
        raise BarError("Usage: !buy <item>. Try !bar.")
    matches = [(key, price) for key, price in BAR_STOCK.items() if needle in key.casefold() and key in items]
    if len(matches) != 1:
        raise BarError("The bartender doesn't sell that." if not matches else "Which drink?")
    key, price = matches[0]
    credits = character.get("credits", STARTING_CREDITS)
    if type(credits) is not int or credits < 0:
        raise BarError("Invalid credit balance.")
    if credits < price:
        raise BarError(f"{key} costs {price} credits; you have {credits}.")
    updated = deepcopy(character)
    bag = updated.setdefault("bag", {})
    if not isinstance(bag, dict):
        raise BarError("Inventory unavailable.")
    updated["credits"] = credits - price
    bag[key] = int(bag.get(key, 0)) + 1
    return updated, f"The bartender slides you a chilled {key}. You pay {price} credits. Balance: {updated['credits']} credits."

def bar_menu(character, items):
    if character.get("current_room") != BAR_ROOM:
        raise BarError("The Neptune Lounge bar isn't here.")
    credits = character.get("credits", STARTING_CREDITS)
    if type(credits) is not int or credits < 0:
        raise BarError("Invalid credit balance.")
    offers = [f"{key} — {price} credits" for key, price in BAR_STOCK.items() if key in items]
    return "Neptune Lounge Bar\n" + "\n".join(offers) + f"\nBalance: {credits} credits. Use !buy Triton Lager."
