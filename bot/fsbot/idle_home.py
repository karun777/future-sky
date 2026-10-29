"""Durable opt-in idle-home policy; no movement or Discord I/O here."""
from collections import deque
from copy import deepcopy
from math import isfinite
from fsbot.recovery import recovering
from fsbot.sequence import requires_choice

KEY = "idle_home_v1"
PUBLIC_ROOMS = {
    "pod_room","hostel_hallway","hostel_stairwell","neptune_lounge",
    "lounge_main_floor","lounge_rest_nook","lounge_games_corner",
    "lounge_stardock_overlook","lounge_smoking_terrace","lounge_balcony_overlook",
    "main_square","sector_42","elemental_sound","lounge_conference_wing",
    "lounge_conference_room_a","lounge_gym","lounge_dance_floor","lounge_stage_edge",
}

def record(ch):
    s=(ch.get("extra") or {}).get(KEY)
    if s is None:return None
    if (not isinstance(s,dict) or s.get("version")!=1
            or type(s.get("enabled")) is not bool or not isinstance(s.get("home"),str)
            or type(s.get("idle_seconds")) is not int or not 60<=s["idle_seconds"]<=86400
            or type(s.get("generation")) is not int
            or not isinstance(s.get("last_input_at"),(int,float))
            or not isfinite(s["last_input_at"]) or s["last_input_at"]<0
            or not isinstance(s.get("history"),list)):
        raise ValueError("Your idle-home record is unavailable.")
    return s

def default_home(ch):
    extra=ch.get("extra") or {}
    for home in [ch.get("reset_location"),extra.get("reset_location"),
                 (extra.get("reset_anchor") or {}).get("room"),"pod_room"]:
        if isinstance(home,str) and home.strip():return home.strip()

def configure(ch, now, *, enabled=True, idle_seconds=1800, message=None, home=None):
    if type(idle_seconds) is not int or not 60<=idle_seconds<=86400:
        raise ValueError("Idle duration must be 60–86400 real seconds.")
    current=record(ch)
    updated=deepcopy(ch)
    state=deepcopy(current) if current else {
        "version":1,"home":default_home(ch),"history":[],"generation":0,
    }
    state.update(enabled=enabled,idle_seconds=idle_seconds,last_input_at=now,
                 generation=state["generation"]+1,status="armed" if enabled else "disabled")
    if home is not None:state["home"]=home
    if message is not None:
        state["channel_id"]=str(message.channel.id)
        state["message_id"]=str(message.id)
    updated.setdefault("extra",{})[KEY]=state
    return updated

def touch(ch, now, message=None):
    state=record(ch)
    if not state or not state["enabled"]:return ch
    updated=deepcopy(ch);s=updated["extra"][KEY]
    s.update(last_input_at=now,generation=s["generation"]+1,status="armed")
    if message is not None:
        s["channel_id"]=str(message.channel.id);s["message_id"]=str(message.id)
    return updated

def due(ch, now):
    s=record(ch)
    return bool(s and s["enabled"] and now>=s["last_input_at"]+s["idle_seconds"])

def blocked(ch):
    return bool(ch.get("in_cube") or recovering(ch) or requires_choice(ch))

def next_step(rooms, start, home):
    if start==home:return None
    if start not in PUBLIC_ROOMS or home not in PUBLIC_ROOMS:
        raise ValueError("No supported walking route home is known.")
    queue=deque([(start,[])])
    seen={start}
    while queue:
        node,path=queue.popleft()
        exits=rooms.get(node,{}).get("exits",{})
        if not isinstance(exits,dict):continue
        for direction,destination in exits.items():
            if not isinstance(direction,str) or not direction.replace("_","").isalpha():continue
            if destination not in PUBLIC_ROOMS or destination not in rooms or destination in seen:continue
            new=path+[direction]
            if destination==home:return new[0]
            seen.add(destination);queue.append((destination,new))
    raise ValueError("No supported walking route home is available.")

def note(ch, status, text=None):
    updated=deepcopy(ch);s=updated["extra"][KEY]
    if s.get("status")==status and (text is None or s.get("pending_notice")==text):return ch
    s["status"]=status
    if text is not None:s["pending_notice"]=text
    s["history"]=(s["history"]+[{"kind":status,"room":ch.get("current_room")}])[-20:]
    return updated
