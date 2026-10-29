"""W4-F12 provisional audience; performance approval remains unresolved."""
from copy import deepcopy
from fsbot.recovery import recovering
from fsbot.terrace_delivery import APPROACH, KEY as DELIVERY, state_of as delivery_state
from fsbot.rehearsal import state_of as rehearsal_state
from fsbot.rat_messenger import state_of as rat_state
KEY = "queen_audience_v1"
FEE = 1

def elapsed(ch):
    r = rehearsal_state(ch)
    if not r:
        return 0
    return r["elapsed_minutes"] + sum(a["elapsed_minutes"] for a in r.get("previous_attempts", []))

def gate(ch):
    r = rehearsal_state(ch)
    if not r or r["stage"] not in {"complete","returned"}:
        raise ValueError("Finish your rehearsal before seeking the Queen.")
    rat = rat_state(ch)
    if not rat or rat["stage"] == "tip":
        raise ValueError("Ask the rat to carry your message first.")
    remaining = 120 - (elapsed(ch) - rat.get("requested_at_minute",0))
    if remaining > 0:
        raise ValueError(f"The messenger has not returned. At least {remaining} more minutes must pass. You can wait with `!rehearsal wait {remaining}`.")
    return rat

def record(ch):
    value=(ch.get("extra") or {}).get(KEY)
    if value is None:
        return None
    if not isinstance(value,dict) or value.get("version") != 1 or value.get("stage") not in {"met","rapport","received"}:
        raise ValueError("Your audience record is unavailable.")
    return value

def prepare(ch, uid, action=""):
    if ch.get("in_cube") or recovering(ch):
        raise ValueError("Return from the Cube or finish recovery before the audience.")
    if ch.get("current_room") != APPROACH:
        raise ValueError("The Queen’s meeting is at the Stardock Overlook.")
    gate(ch)
    current=record(ch)
    action=" ".join(action.casefold().split())
    if action not in {"","meet","talk","pay","status"}:
        raise ValueError("Use `!queen` for your next action.")
    if current and current["stage"]=="received":
        return ch,("The Queen’s music","You have her music. Her approval of your performance is still yours to earn.")
    updated=deepcopy(ch)
    rat = updated["extra"]["rat_messenger_v1"]
    if rat["stage"] == "pending":
        rat.update(stage="arranged",meeting={"contact":"dark_rat_queen","room":APPROACH,"status":"arranged"})
    state=updated.setdefault("extra",{}).setdefault(KEY,{"version":1,"stage":"met","fee":FEE,"approval":"unresolved"})
    if not current:
        if action not in {"","meet","status"}:
            raise ValueError("Meet her first with `!queen`.")
        return updated,("The Dark Rat Queen",
            "The rat appears beside the conduit. Behind you, a voice says, “You wanted to talk about music?” "
            "The Dark Rat Queen joins you at the window.\n\n"
            "Speak with her: `!queen talk`.")
    if action in {"","meet","status"}:
        return ch,("The Dark Rat Queen",
            "She waits for your answer. Use `!queen talk`." if current["stage"]=="met"
            else "She has offered the music for **1 credit**. Accept with `!queen pay`.")
    if action=="talk":
        if current["stage"]=="rapport":
            return ch,("Her offer","The fee is **1 credit**. Accept with `!queen pay`.")
        state["stage"]="rapport"
        return updated,("A little preparation",
            "You tell her about the rehearsal: the transitions, the listening, the parts that needed work. "
            "She asks a few questions, and you find yourself answering plainly.\n\n"
            "“I can give you something to play. One credit. What you do with it is another matter.”\n\n"
            "Accept with `!queen pay`.")
    if current["stage"]!="rapport":
        raise ValueError("Speak with her first: `!queen talk`.")
    cash=ch.get("credits",0)
    if type(cash) is not int or cash<FEE:
        raise ValueError("You need 1 ordinary credit. Your Lounge bar tab cannot pay this fee. At the Lounge counter, use `!work bar` to earn credits, then return.")
    delivery=delivery_state(ch)
    if not delivery or delivery.get("secured_in_pod") or delivery["stage"]!="usb_collected":
        raise ValueError("Collect your terrace delivery before receiving the Queen’s music.")
    updated["credits"]=cash-FEE
    state.update(stage="received",fee_paid=FEE,approval="unresolved",
        music={"instance_id":f"{uid}:queen:music:v1","holder":str(uid),
               "source":"dark_rat_queen","integrity":"intact","sent_back":False,
               "related_delivery":delivery["objects"]["usb"]["instance_id"]})
    return updated,("The music",
        "You pay the credit. She transfers a collection of tracks to you.\n\n"
        "“Listen to the room,” she says. “You’ve already spent enough time listening to yourself.”\n\n"
        "You have the music. Keep it safe until the set.")
