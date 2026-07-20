# fsbot/cogs/threadnodes.py — Thread Nodes (Contract-Clean) v3.7.4
#
# Patch goals (2026-02-05):
# - Presentation guard: avoid duplicate node spam (modal moments feel viscous, not glitchy)
#     - Persistent guard: char["extra"]["thread_nodes"]["active_presented"]
#     - Ephemeral throttle: suppress SAME node re-send within ~2 seconds per user
# - Auto-close "cutscene" nodes:
#     - If a node has NO options and NO prompt, it resolves immediately after first presentation
#     - Prevents movement from being "entangled" by a delivery/cutscene moment
# - Add effects:
#     - set_status       (writes to char["extra"]["status"][key])
#     - adjust_status    (delta + clamp) for hunger/thirst/fatigue etc
# - Add trigger requirements:
#     - requirements.flag_set: "some_flag"   (must be truthy)
# - Keep free-text prompt resolution via: !answer <text...>
# - Keep optional idle trigger support via: maybe_trigger_on_idle()
# - Tolerate legacy JSON shapes (read-only normalization; no migrations written)
# - UX: explicit acknowledgement after !answer when no after_text/result is provided
#
# Canonical per-character thread node state lives ONLY at:
#   char["extra"]["thread_nodes"]["active_thread_node"]
#   char["extra"]["thread_nodes"]["events_completed"]
#   char["extra"]["thread_nodes"]["pending_answer"]
#   char["extra"]["thread_nodes"]["active_presented"]        (presentation guard)

from __future__ import annotations

import json
import os
import time
from typing import Any, Dict, Optional, Tuple

import discord
from discord.ext import commands

THREAD_NODES_FILE = "data/thread_nodes/thread_nodes.json"


# ============================================================
# Permissions
# ============================================================

def is_dpc(ctx: commands.Context) -> bool:
    # Admins are always DPC.
    if getattr(ctx.author, "guild_permissions", None) and ctx.author.guild_permissions.administrator:
        return True
    role = discord.utils.get(getattr(ctx.author, "roles", []), name="DPC")
    return role is not None


# ============================================================
# JSON loader + normalization (read-only)
# ============================================================

def _normalize_node_shape(node_id: str, node: Dict[str, Any]) -> Dict[str, Any]:
    """
    Best-effort normalization so the runtime can accept both:
      - canonical: {"triggers": {...}, "title": "...", "text": "...", "options": [...], "effects":[...]}
      - legacy-ish: {"trigger": {...}, "content": {"title": "...", "text": "..."}, ...}
    WITHOUT writing migrations back to disk.
    """
    n = dict(node or {})

    # ---- triggers / trigger ----
    if "triggers" not in n and isinstance(n.get("trigger"), dict):
        trig = n.get("trigger") or {}
        ttype = (trig.get("type") or "").strip().lower()

        triggers: Dict[str, Any] = {}
        if ttype == "on_enter_room":
            rid = (trig.get("room_id") or "").strip()
            triggers["on_enter_room"] = [rid] if rid else []
        elif ttype == "on_idle_room":
            rid = (trig.get("room_id") or "").strip()
            triggers["on_idle_room"] = [rid] if rid else []
            if "min_seconds" in trig:
                triggers["min_seconds"] = int(trig.get("min_seconds") or 0)

        if "once_per_character" in trig:
            triggers["once_per_character"] = bool(trig.get("once_per_character"))
        if isinstance(trig.get("requirements"), dict):
            triggers["requirements"] = trig.get("requirements") or {}
        if "era" in trig:
            triggers["era"] = trig.get("era")

        n["triggers"] = triggers

    # ---- content / title,text ----
    if isinstance(n.get("content"), dict):
        c = n.get("content") or {}
        if "title" not in n and isinstance(c.get("title"), str):
            n["title"] = c.get("title")
        if "text" not in n and isinstance(c.get("text"), str):
            n["text"] = c.get("text")
        if "options" not in n and isinstance(c.get("options"), list):
            n["options"] = c.get("options")

    # ---- effects list always present ----
    if not isinstance(n.get("effects"), list):
        n["effects"] = []

    # Debug identity
    n["_id"] = str(node_id)

    return n


def _load_nodes() -> Dict[str, Dict[str, Any]]:
    """
    Loader notes:
    - BOM-safe (utf-8-sig).
    - Canonical format: dict keyed by node_id.
    - Tolerates legacy wrapper: {"version": "...", "nodes": { ... }}.
    """
    if not os.path.exists(THREAD_NODES_FILE):
        return {}

    with open(THREAD_NODES_FILE, "r", encoding="utf-8-sig") as f:
        data = json.load(f)

    raw_nodes: Dict[str, Any]
    if isinstance(data, dict) and "nodes" not in data:
        raw_nodes = {str(k): v for k, v in data.items() if isinstance(v, dict)}
    elif isinstance(data, dict) and isinstance(data.get("nodes"), dict):
        nodes = data.get("nodes") or {}
        raw_nodes = {str(k): v for k, v in nodes.items() if isinstance(v, dict)}
    else:
        raw_nodes = {}

    out: Dict[str, Dict[str, Any]] = {}
    for nid, node in raw_nodes.items():
        out[str(nid)] = _normalize_node_shape(str(nid), node)

    return out


# ============================================================
# Cog
# ============================================================

class ThreadNodesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.nodes: Dict[str, Dict[str, Any]] = _load_nodes()

        # Ephemeral idle timing (safe to lose on restart)
        self._idle_seen: Dict[Tuple[str, str], float] = {}

        # Ephemeral presentation throttle (safe to lose on restart)
        # user_id -> (node_id, ts)
        self._last_presented_by_user: Dict[str, Tuple[str, float]] = {}
        self._present_throttle_seconds: float = 2.0

    # -------------------------
    # Data helpers
    # -------------------------

    def reload_nodes(self) -> None:
        self.nodes = _load_nodes()

    def _get_char(self, user_id: str) -> dict:
        s = self.bot.storage
        # Ensure storage has a record
        self.bot.state.ensure_player_records(user_id)
        ch = s.characters.get(user_id)
        return ch if isinstance(ch, dict) else {}

    def _save_chars(self) -> None:
        s = self.bot.storage
        if hasattr(s, "save_characters"):
            s.save_characters()

    def _get_unlocked(self, char: dict) -> set[str]:
        flags = char.get("flags") or {}
        unlocked = flags.get("unlocked_commands") or []
        return {str(x).strip().lower() for x in unlocked if str(x).strip()}

    # ---- canonical threadnode state lives under char["extra"]["thread_nodes"] ----

    def _tn_state(self, char: dict) -> dict:
        extra = char.get("extra")
        if not isinstance(extra, dict):
            extra = {}
            char["extra"] = extra

        tn = extra.get("thread_nodes")
        if not isinstance(tn, dict):
            tn = {}
            extra["thread_nodes"] = tn

        if not isinstance(tn.get("events_completed"), list):
            tn["events_completed"] = []

        if "active_thread_node" not in tn:
            tn["active_thread_node"] = None

        if "pending_answer" not in tn:
            tn["pending_answer"] = None

        # Presentation guard: prevents repeated embed spam
        if "active_presented" not in tn:
            tn["active_presented"] = False

        return tn

    def _get_active_node_id(self, char: dict) -> Optional[str]:
        tn = self._tn_state(char)
        active = tn.get("active_thread_node")
        return str(active) if active else None

    def _set_active_node_id(self, char: dict, node_id: Optional[str]) -> None:
        tn = self._tn_state(char)
        tn["active_thread_node"] = node_id
        # Whenever we set/clear active node, reset presentation guard
        tn["active_presented"] = False

    def _get_pending_answer(self, char: dict) -> Optional[dict]:
        tn = self._tn_state(char)
        pa = tn.get("pending_answer")
        return pa if isinstance(pa, dict) else None

    def _set_pending_answer(self, char: dict, payload: Optional[dict]) -> None:
        tn = self._tn_state(char)
        tn["pending_answer"] = payload

    def _get_presented(self, char: dict) -> bool:
        tn = self._tn_state(char)
        return bool(tn.get("active_presented", False))

    def _set_presented(self, char: dict, val: bool) -> None:
        tn = self._tn_state(char)
        tn["active_presented"] = bool(val)

    def _get_completed(self, char: dict) -> list[str]:
        tn = self._tn_state(char)
        done = tn.get("events_completed") or []
        out: list[str] = []
        for x in done:
            sx = str(x).strip()
            if sx and sx not in out:
                out.append(sx)
        tn["events_completed"] = out
        return out

    def _mark_complete(self, char: dict, node_id: str) -> None:
        nid = str(node_id).strip()
        if not nid:
            return
        done = self._get_completed(char)
        if nid not in done:
            done.append(nid)

    def _has_completed(self, char: dict, node_id: str) -> bool:
        return str(node_id).strip() in self._get_completed(char)

    # -------------------------
    # Presentation throttle (ephemeral)
    # -------------------------

    def _should_throttle_presentation(self, user_id: str, node_id: str, now_ts: float) -> bool:
        prev = self._last_presented_by_user.get(str(user_id))
        if not prev:
            return False
        prev_node_id, prev_ts = prev
        if prev_node_id == str(node_id) and (now_ts - prev_ts) < self._present_throttle_seconds:
            return True
        return False

    def _mark_presented_throttle(self, user_id: str, node_id: str, now_ts: float) -> None:
        self._last_presented_by_user[str(user_id)] = (str(node_id), float(now_ts))

    # -------------------------
    # Era helpers
    # -------------------------

    def _room_era(self, room_id: str) -> str:
        try:
            rid = (room_id or "").strip()
            if not rid:
                return "manzo"
            room = None
            if hasattr(self.bot, "storage") and getattr(self.bot.storage, "rooms", None):
                room = self.bot.storage.rooms.get(rid)
            if isinstance(room, dict):
                era = (room.get("era") or "").strip().lower()
                return era or "manzo"
        except Exception:
            pass
        return "manzo"

    def _era_matches(self, node: dict, room_era: str) -> bool:
        triggers = node.get("triggers") or {}
        era = triggers.get("era", "any")
        re_ = (room_era or "").strip().lower() or "manzo"

        if era is None:
            return True

        if isinstance(era, str):
            e = era.strip().lower()
            if not e or e in ("any", "*"):
                return True
            return e == re_

        if isinstance(era, list):
            allow = {str(x).strip().lower() for x in era if str(x).strip()}
            if not allow or "any" in allow or "*" in allow:
                return True
            return re_ in allow

        return True

    # -------------------------
    # Formatting
    # -------------------------

    def _fmt_node(self, node_id: str, node: Dict[str, Any]) -> discord.Embed:
        title = node.get("title") or "An encounter unfolds…"
        text = node.get("text") or ""
        embed = discord.Embed(title=title, description=text)

        options = node.get("options") or []
        if isinstance(options, list) and options:
            lines = []
            for opt in options:
                if not isinstance(opt, dict):
                    continue
                key = str(opt.get("key", "")).strip()
                label = opt.get("label") or opt.get("text") or "…"
                if key:
                    lines.append(f"**{key}.** {label}")
            if lines:
                embed.add_field(
                    name="Choices",
                    value="\n".join(lines) + "\n\nUse `!choose <key>`",
                    inline=False,
                )
        else:
            embed.add_field(name="Choices", value="—", inline=False)

        prompt = node.get("prompt")
        if isinstance(prompt, dict):
            ptext = (prompt.get("text") or "").strip()
            if ptext:
                embed.add_field(
                    name="Prompt",
                    value=f"{ptext}\n\nUse `!answer <your text>`",
                    inline=False,
                )
            else:
                embed.add_field(
                    name="Prompt",
                    value="Use `!answer <your text>`",
                    inline=False,
                )

        embed.set_footer(text=f"node: {node_id}")
        return embed

    def _reprompt_line(self, node: Dict[str, Any]) -> str:
        """
        One-line gentle tether back into the active moment.
        Optional JSON hook:
          node["reprompt"] = "..."
        """
        rep = node.get("reprompt")
        if isinstance(rep, str) and rep.strip():
            return rep.strip()

        prompt = node.get("prompt")
        if isinstance(prompt, dict):
            return "🧷 The moment is still open. The question is still waiting."
        opts = node.get("options") or []
        if isinstance(opts, list) and opts:
            return "🧷 The moment is still open. Your choice still matters."
        return "🧷 The moment is still open."

    # -------------------------
    # Start / Present
    # -------------------------

    async def _start_node(self, ctx: commands.Context, user_id: str, node_id: str) -> None:
        node_id = str(node_id).strip()
        if not node_id:
            return

        if node_id not in self.nodes:
            await ctx.send(f"⚠️ Unknown thread node id: `{node_id}`")
            return

        char = self._get_char(user_id)

        # Set active + reset presentation guard
        self._set_active_node_id(char, node_id)

        node = self.nodes[node_id]
        if isinstance(node.get("prompt"), dict):
            self._set_pending_answer(char, {"node_id": node_id, "expects": "text"})
        else:
            self._set_pending_answer(char, None)

        self._save_chars()

        # First present is always intended to be the full embed
        await self.present_active_node(ctx, user_id, force=True)

    async def present_active_node(self, ctx: commands.Context, user_id: str, *, force: bool = False) -> None:
        """
        Present the currently active node for this character.

        Guard:
        - Persistent: if already presented and not force, do NOT resend full embed; send reprompt line.
        - Ephemeral throttle: suppress same-node re-send within ~2 seconds (even if multiple callers).
        - Auto-close cutscenes: nodes with NO options and NO prompt resolve immediately after first show.
        """
        uid = str(user_id)
        char = self._get_char(uid)
        node_id = self._get_active_node_id(char)
        if not node_id:
            await ctx.send("There is nothing to answer right now.")
            return

        self.reload_nodes()
        node = self.nodes.get(node_id)
        if not node:
            self._set_active_node_id(char, None)
            self._set_pending_answer(char, None)
            self._save_chars()
            await ctx.send("That moment has passed.")
            return

        already = self._get_presented(char)

        # If it's already presented and we're not forcing, just tether.
        if already and not force:
            await ctx.send(self._reprompt_line(node))
            return

        # If force is being called repeatedly (multiple triggers), throttle SAME node spam.
        now_ts = time.time()
        if self._should_throttle_presentation(uid, node_id, now_ts):
            # If we've already presented at least once, tether; otherwise, silently suppress.
            if already:
                await ctx.send(self._reprompt_line(node))
            return

        # Present full embed once (or forced, but throttled)
        await ctx.send(embed=self._fmt_node(node_id, node))
        self._set_presented(char, True)
        self._mark_presented_throttle(uid, node_id, now_ts)

        # Auto-close cutscene nodes (no choices, no prompt)
        options = node.get("options") or []
        has_options = isinstance(options, list) and any(isinstance(o, dict) for o in options)
        has_prompt = isinstance(node.get("prompt"), dict)

        if not has_options and not has_prompt:
            self._mark_complete(char, node_id)
            self._set_active_node_id(char, None)
            self._set_pending_answer(char, None)

        self._save_chars()

    # -------------------------
    # Trigger evaluation
    # -------------------------

    def _requirements_met(self, char: dict, node: dict) -> bool:
        """
        Supported requirements:
          requirements.must_not_have_unlocked_commands: ["sneak", ...]
          requirements.flag_not_set: "some_flag"
          requirements.flag_set: "some_flag"
          requirements.character_name_is_null: true
        """
        req = (node.get("triggers") or {}).get("requirements") or {}
        if not isinstance(req, dict):
            req = {}

        must_not_have = req.get("must_not_have_unlocked_commands") or []
        unlocked = self._get_unlocked(char)
        for cmd in must_not_have:
            c = str(cmd).strip().lower()
            if c and c in unlocked:
                return False

        fns = req.get("flag_not_set")
        if isinstance(fns, str) and fns.strip():
            flags = char.get("flags")
            if not isinstance(flags, dict):
                flags = {}
                char["flags"] = flags
            if bool(flags.get(fns.strip(), False)):
                return False

        fs = req.get("flag_set")
        if isinstance(fs, str) and fs.strip():
            flags = char.get("flags")
            if not isinstance(flags, dict):
                flags = {}
                char["flags"] = flags
            if not bool(flags.get(fs.strip(), False)):
                return False

        if bool(req.get("character_name_is_null", False)):
            nm = (char.get("name") or "").strip()
            if nm:
                return False

        return True

    def _pick_on_enter_node_id(self, char: dict, room_id: str) -> Optional[str]:
        room_id = (room_id or "").strip().lower()
        if not room_id:
            return None

        # If there's an active moment, do not start a new one.
        if self._get_active_node_id(char):
            return None

        room_era = self._room_era(room_id)

        for node_id, node in self.nodes.items():
            triggers = node.get("triggers") or {}

            rooms = triggers.get("on_enter_room") or []
            rooms_norm = {str(r).strip().lower() for r in rooms if str(r).strip()}
            if room_id not in rooms_norm:
                continue

            if not self._era_matches(node, room_era):
                continue

            if bool(triggers.get("once_per_character", False)) and self._has_completed(char, node_id):
                continue

            if not self._requirements_met(char, node):
                continue

            return node_id

        return None

    def _pick_on_idle_node_id(self, char: dict, room_id: str, user_id: str) -> Optional[str]:
        room_id_norm = (room_id or "").strip().lower()
        if not room_id_norm:
            return None

        if self._get_active_node_id(char):
            return None

        room_era = self._room_era(room_id_norm)

        key = (str(user_id), room_id_norm)
        now = time.time()
        first_seen = self._idle_seen.get(key)
        if first_seen is None:
            self._idle_seen[key] = now
            return None

        for node_id, node in self.nodes.items():
            triggers = node.get("triggers") or {}
            rooms = triggers.get("on_idle_room") or []
            rooms_norm = {str(r).strip().lower() for r in rooms if str(r).strip()}
            if room_id_norm not in rooms_norm:
                continue

            if not self._era_matches(node, room_era):
                continue

            if bool(triggers.get("once_per_character", False)) and self._has_completed(char, node_id):
                continue

            if not self._requirements_met(char, node):
                continue

            min_seconds = int(triggers.get("min_seconds") or 0)
            if min_seconds > 0 and (now - first_seen) < min_seconds:
                continue

            return node_id

        return None

    async def maybe_trigger_on_enter(self, ctx: commands.Context, user_id: str, room_id: str) -> None:
        try:
            self.reload_nodes()
            char = self._get_char(user_id)

            # Reset idle timer on room enter
            rid = (room_id or "").strip().lower()
            if rid:
                self._idle_seen[(str(user_id), rid)] = time.time()

            node_id = self._pick_on_enter_node_id(char, room_id)
            if node_id:
                await self._start_node(ctx, user_id, node_id)
        except Exception:
            return

    async def maybe_trigger_on_idle(self, ctx: commands.Context, user_id: str, room_id: str) -> None:
        try:
            self.reload_nodes()
            char = self._get_char(user_id)
            node_id = self._pick_on_idle_node_id(char, room_id, user_id)
            if node_id:
                await self._start_node(ctx, user_id, node_id)
        except Exception:
            return

    # -------------------------
    # Effects engine
    # -------------------------

    def _ensure_flags(self, char: dict) -> dict:
        flags = char.get("flags")
        if not isinstance(flags, dict):
            flags = {}
            char["flags"] = flags
        return flags

    def _ensure_status(self, char: dict) -> dict:
        extra = char.get("extra")
        if not isinstance(extra, dict):
            extra = {}
            char["extra"] = extra
        st = extra.get("status")
        if not isinstance(st, dict):
            st = {}
            extra["status"] = st
        return st

    def _to_int(self, v: Any, default: int = 0) -> int:
        try:
            if v is None:
                return default
            if isinstance(v, bool):
                return int(v)
            if isinstance(v, (int, float)):
                return int(v)
            s = str(v).strip()
            if not s:
                return default
            return int(float(s))
        except Exception:
            return default

    def _clamp(self, x: int, mn: Optional[int], mx: Optional[int]) -> int:
        if mn is not None and x < mn:
            x = mn
        if mx is not None and x > mx:
            x = mx
        return x

    async def _apply_effects(
        self,
        ctx: commands.Context,
        user_id: str,
        effects: list[dict],
        *,
        player_input: Optional[str] = None,
        active_node_id: Optional[str] = None,
    ) -> None:
        char = self._get_char(user_id)
        s = self.bot.storage
        flags = self._ensure_flags(char)

        inp = (player_input or "").strip()

        for eff in effects or []:
            if not isinstance(eff, dict):
                continue
            et = (eff.get("type") or "").strip().lower()

            if et == "unlock_command":
                cmd = (eff.get("command") or "").strip().lower()
                if cmd and hasattr(ctx.bot, "unlock_command"):
                    changed = await ctx.bot.unlock_command(user_id, cmd)  # type: ignore[attr-defined]
                    if changed:
                        await ctx.send(f"🔓 **New verb unlocked:** `{cmd}`")

            elif et == "add_item":
                item = eff.get("item")
                qty = int(eff.get("qty", 1))
                if item:
                    bag = char.get("bag")
                    if not isinstance(bag, dict):
                        bag = {}
                        char["bag"] = bag
                    bag[item] = int(bag.get(item, 0)) + qty
                    await ctx.send(f"👜 You received: **{item}** x{qty}")

            elif et == "set_flag":
                if isinstance(eff.get("params"), dict):
                    fp = eff.get("params") or {}
                    f = str(fp.get("flag") or "").strip()
                    v = fp.get("value", True)
                else:
                    f = str(eff.get("flag") or "").strip()
                    v = eff.get("value", True)
                if f:
                    flags[f] = v

            elif et == "set_character_name":
                val = (eff.get("value") or "").strip()
                if not val:
                    val = inp
                if val:
                    char["name"] = val

            elif et == "confirm_or_update_name":
                if not inp:
                    continue
                if inp.strip().lower() == "yes":
                    pass
                else:
                    char["name"] = inp

            elif et == "set_birthdate_if_provided":
                if inp:
                    char["birthdate"] = inp

            elif et == "conditional_flag":
                p = eff.get("params") or {}
                if not isinstance(p, dict):
                    continue
                rule = (p.get("if_input_present") or p.get("if_birthdate_provided")) if inp else p.get("else")
                if isinstance(rule, dict):
                    f = str(rule.get("flag") or "").strip()
                    v = rule.get("value", True)
                    if f:
                        flags[f] = v

            elif et == "set_status":
                # params: { "key":"hunger", "value": 1, "min":0, "max":10 }
                p = eff.get("params") or {}
                if not isinstance(p, dict):
                    continue
                key = str(p.get("key") or "").strip()
                if not key:
                    continue
                st = self._ensure_status(char)
                mn = p.get("min")
                mx = p.get("max")
                mn_i = self._to_int(mn) if mn is not None else None
                mx_i = self._to_int(mx) if mx is not None else None
                val = self._to_int(p.get("value"), default=self._to_int(st.get(key), 0))
                st[key] = self._clamp(val, mn_i, mx_i)

            elif et == "adjust_status":
                # params: { "key":"hunger", "delta": +1, "min":0, "max":3 }
                p = eff.get("params") or {}
                if not isinstance(p, dict):
                    continue
                key = str(p.get("key") or "").strip()
                if not key:
                    continue
                st = self._ensure_status(char)
                cur = self._to_int(st.get(key), 0)
                delta = self._to_int(p.get("delta"), 0)
                mn = p.get("min")
                mx = p.get("max")
                mn_i = self._to_int(mn) if mn is not None else None
                mx_i = self._to_int(mx) if mx is not None else None
                st[key] = self._clamp(cur + delta, mn_i, mx_i)

            elif et == "mark_complete":
                nid = ""
                if isinstance(eff.get("params"), dict):
                    nid = str((eff.get("params") or {}).get("node") or "").strip()
                if not nid:
                    nid = str(eff.get("node") or "").strip()
                if not nid:
                    nid = str(active_node_id or "").strip()
                if nid:
                    self._mark_complete(char, nid)

        if hasattr(s, "save_characters"):
            s.save_characters()

    # -------------------------
    # Player: choose an option on the active node
    # -------------------------

    @commands.command(name="choose")
    async def choose_cmd(self, ctx: commands.Context, key: str):
        user_id = str(ctx.author.id)
        char = self._get_char(user_id)

        node_id = self._get_active_node_id(char)
        if not node_id:
            await ctx.send("There is nothing to choose right now.")
            return

        self.reload_nodes()
        node = self.nodes.get(node_id)
        if not node:
            self._set_active_node_id(char, None)
            self._set_pending_answer(char, None)
            self._save_chars()
            await ctx.send("That moment has passed.")
            return

        key = str(key).strip()
        options = node.get("options") or []
        chosen: Optional[dict] = None
        if isinstance(options, list):
            for opt in options:
                if isinstance(opt, dict) and str(opt.get("key", "")).strip() == key:
                    chosen = opt
                    break

        if not chosen:
            await ctx.send("That choice isn’t available. Try `!choose 1` (or the listed keys).")
            return

        result = chosen.get("result")
        if isinstance(result, str) and result.strip():
            await ctx.send(result.strip())

        effects = chosen.get("effects") or []
        await self._apply_effects(ctx, user_id, effects, active_node_id=node_id)

        # completion bookkeeping
        self._mark_complete(char, node_id)
        self._set_active_node_id(char, None)
        self._set_pending_answer(char, None)
        self._save_chars()

    # -------------------------
    # Player: answer a prompt on the active node
    # -------------------------

    @commands.command(name="answer")
    async def answer_cmd(self, ctx: commands.Context, *, text: str = ""):
        user_id = str(ctx.author.id)
        char = self._get_char(user_id)

        node_id = self._get_active_node_id(char)
        if not node_id:
            await ctx.send("There is nothing to answer right now.")
            return

        self.reload_nodes()
        node = self.nodes.get(node_id)
        if not node:
            self._set_active_node_id(char, None)
            self._set_pending_answer(char, None)
            self._save_chars()
            await ctx.send("That moment has passed.")
            return

        prompt = node.get("prompt")
        if not isinstance(prompt, dict):
            await ctx.send("This moment doesn’t accept a free-text answer. Use `!choose <key>` if choices are listed.")
            return

        # UX grace: empty !answer re-tethers (without spamming the full embed)
        if not text.strip():
            await self.present_active_node(ctx, user_id, force=False)
            return

        effects = node.get("effects") or []
        await self._apply_effects(ctx, user_id, effects, player_input=text, active_node_id=node_id)

        # Explicit acknowledgement / payoff line
        after = node.get("result") or node.get("after_text")
        if isinstance(after, str) and after.strip():
            await ctx.send(after.strip())
        else:
            await ctx.send("✅ Noted.")

        self._mark_complete(char, node_id)
        self._set_active_node_id(char, None)
        self._set_pending_answer(char, None)
        self._save_chars()

    # -------------------------
    # DPC tools
    # -------------------------

    @commands.command(name="node")
    async def node_cmd(self, ctx: commands.Context, node_id: str):
        if not is_dpc(ctx):
            await ctx.send("⛔ You don’t have permission to use `!node`.")
            return
        self.reload_nodes()
        await self._start_node(ctx, str(ctx.author.id), node_id.strip())

    @commands.command(name="nodes_reload")
    async def nodes_reload_cmd(self, ctx: commands.Context):
        if not is_dpc(ctx):
            await ctx.send("⛔ You don’t have permission to use `!nodes_reload`.")
            return
        self.reload_nodes()
        await ctx.send(f"✅ Reloaded thread nodes ({len(self.nodes)} loaded).")


async def setup(bot):
    await bot.add_cog(ThreadNodesCog(bot))
