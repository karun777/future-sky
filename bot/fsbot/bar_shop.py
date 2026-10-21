"""Neptune Lounge purchases; restricted performance credit is spent first."""
from copy import deepcopy
from fsbot.performance_tab import balance as tab_balance, KEY as TAB_KEY
from fsbot.triton_lager import SERVING

BAR_ROOM = "neptune_lounge"
STARTING_CREDITS = 20
BAR_STOCK = {"Triton Lager": 5}

class BarError(ValueError):
    pass

def balances(character):
    credits = character.get("credits", STARTING_CREDITS)
    if type(credits) is not int or credits < 0:
        raise BarError("Invalid credit balance.")
    try:
        restricted = tab_balance(character)
    except ValueError as exc:
        raise BarError(str(exc)) from exc
    return credits, restricted

def buy_from_bar(character, items, query):
    if character.get("in_cube") or character.get("current_room") != BAR_ROOM:
        raise BarError("You must be in Neptune Lounge to buy a drink.")
    needle = (query or "").strip().casefold()
    if not needle:
        raise BarError("Usage: !buy <item>. Try !bar.")
    matches = [(key, price) for key, price in BAR_STOCK.items() if needle in key.casefold() and key in items]
    if len(matches) != 1:
        raise BarError("The bartender doesn't sell that." if not matches else "Which drink?")
    key, price = matches[0]
    credits, restricted = balances(character)
    if credits + restricted < price:
        raise BarError(f"{key} costs {price} credits; you have {credits} credits and {restricted} bar credits.")
    updated = deepcopy(character)
    bag = updated.setdefault("bag", {})
    if not isinstance(bag, dict):
        raise BarError("Inventory unavailable.")
    count = bag.get(key, 0)
    if type(count) is not int or count < 0:
        raise BarError("Inventory unavailable.")
    from_tab = min(restricted, price)
    if from_tab:
        updated["extra"][TAB_KEY]["balance"] -= from_tab
    updated["credits"] = credits - (price - from_tab)
    bag[key] = count + 1
    payment = f"{from_tab} bar credits and {price - from_tab} credits" if from_tab else f"{price} credits"
    message = (f"The bartender slides you a chilled {key}. You pay {payment}. "
               f"Balance: {updated['credits']} credits; performance tab: {restricted - from_tab} bar credits. "
               + SERVING)
    return updated, message

def bar_menu(character, items):
    if character.get("in_cube") or character.get("current_room") != BAR_ROOM:
        raise BarError("The Neptune Lounge bar isn't here.")
    credits, restricted = balances(character)
    offers = [f"{key} — {price} credits" for key, price in BAR_STOCK.items() if key in items]
    message = ("Neptune Lounge Bar\n" + "\n".join(offers)
               + f"\nBalance: {credits} credits.\nPerformance tab: {restricted} bar credits."
               + "\nBlue, chilled, non-alcoholic; infused with psychedelic Neptunian microvita."
               + "\nNot everyone comes for the chips.")
    if credits + restricted >= BAR_STOCK["Triton Lager"] and "Triton Lager" in items:
        message += "\nUse !buy Triton Lager."
    else:
        message += "\nYou do not currently have enough credit for a lager."
    return message
