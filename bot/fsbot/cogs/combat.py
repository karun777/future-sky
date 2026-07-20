# ============================================================
# FILE META — fsbot/cogs/combat.py
# Canonical name: CombatCog (initiative + turn loop + enemy persistence)
#
# Version: v2.9 — Authority Sweep #2B
# Last edited: 2026-07-17
#
# Purpose:
# - Manages per-room combat state machine (initiative order, rounds, turns)
# - Routes combat prompts/output to player run-channels (router)
# - Applies resolver-derived combat modifiers (damage_bonus v0)
# - Persists enemy HP to rooms.json enemy *instance* records (critical)
#
# Reads (authoritative JSON):
# - characters.json (player stats, flags, equipment, bag, current_room)
# - rooms.json (room enemies instances, room id/era via state)
# - enemies.json (indirectly via storage.resolve_room_enemies)
# - items.json (weapon/armor metadata via utils + storage.items_db)
# - modifiers/layers.json (indirectly via storage.resolve_for_combat -> resolver)
#
# Writes (persistence expectations):
# - characters.json:
#   - flags.in_combat
#   - hp changes on death/respawn
#   - intents are in-memory only (bot.state.combats), not persisted
# - rooms.json:
#   - enemy instance hp updates (per-hit)
#   - enemy instance removal on defeat
#
# Depends on:
# - fsbot.cogs.router.ensure_player_run_channel (delivery + channel creation)
# - fsbot.utils.weapon_damage / equipped_defense / add_to_bag
# - storage.resolve_room_enemies + storage.resolve_for_combat
# - presence.get_character + presence.get_room_members + presence.resolve_room_for_user
#
# Commands provided:
# - !combat / !draw / !engage
# - !attack <foe>
# - !disengage / !sheath / !flee
# - !combat_status / !status
#
# Operational notes / hazards:
# - If any other cog defines overlapping combat commands (e.g. combat/attack/disengage/status),
#   disable one to avoid command registration conflicts.
# - Combat loop runs as an asyncio.Task per active room (bot.state.combats[room_id]["task"]).
# ============================================================

from __future__ import annotations

import asyncio
import random
from typing import Optional, Set, Dict, Any, List, Tuple

from discord.ext import commands

from fsbot.cogs.router import ensure_player_run_channel
from fsbot.utils import weapon_damage, add_to_bag, equipped_defense

TURN_DELAY_SECONDS = 5
MAX_SKIP_ATTEMPTS_PER_TICK = 8  # prevents acted_this_round guard from spinning forever


def _mod(score: int) -> int:
    try:
        return (int(score) - 10) // 2
    except Exception:
        return 0


STAT_DEFAULTS: Dict[str, int] = {
    "strength": 10,
    "dexterity": 10,
    "constitution": 10,
    "intelligence": 10,
    "wisdom": 10,
    "charisma": 10,
    "max_hp": 20,
    "hp": 20,
}


def _to_int(x: Any, default: int = 0) -> int:
    try:
        return int(float(x))
    except Exception:
        return default


class CombatCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        if not hasattr(self.bot.state, "combats"):
            self.bot.state.combats = {}  # type: ignore[attr-defined]

    # ============================================================
    # Schema hardening helpers (legacy characters.json safe)
    # ============================================================
    def _ensure_character_schema(self, user_id: str) -> dict:
        s = self.bot.storage
        uid = str(user_id)

        # Presence is the canonical runtime character lookup boundary.
        # ``ensure=True`` delegates minimal record creation to GameState.
        ch = self.bot.presence.get_character(uid, ensure=True)
        if not isinstance(ch, dict):
            # Defensive schema repair remains a Combat mutation concern.
            ch = {}
            s.characters[uid] = ch

        ch.setdefault("name", f"wanderer-{user_id[-4:]}")
        ch.setdefault("birthdate", "2000-01-01")

        stats = ch.setdefault("stats", {})
        if not isinstance(stats, dict):
            stats = {}
            ch["stats"] = stats

        for k, v in STAT_DEFAULTS.items():
            if k not in stats:
                stats[k] = v

        try:
            stats["max_hp"] = max(1, int(stats.get("max_hp", 20)))
        except Exception:
            stats["max_hp"] = 20

        try:
            stats["hp"] = int(stats.get("hp", stats["max_hp"]))
        except Exception:
            stats["hp"] = stats["max_hp"]

        if stats["hp"] < 0:
            stats["hp"] = 0
        if stats["hp"] > stats["max_hp"]:
            stats["hp"] = stats["max_hp"]

        ch.setdefault("flags", {})
        if not isinstance(ch["flags"], dict):
            ch["flags"] = {}

        return ch

    # ============================================================
    # Resolver helpers (Phase 1 integration)
    # ============================================================
    def _effective_combat_view(self, user_id: str, *, room_id: str, event: str) -> Dict[str, Any]:
        s = self.bot.storage
        try:
            # ✅ include era in context so layers can gate via conditions
            era = self.bot.state.resolve_era_for_user(user_id)

            out = s.resolve_for_combat(
                user_id,
                context={"room_id": room_id, "event": event, "era": era},
            )
            view = out.get("view", {}) if isinstance(out, dict) else {}
            combat = view.get("combat", {}) if isinstance(view, dict) else {}
            return combat if isinstance(combat, dict) else {}
        except Exception:
            return {}

    def _effective_damage_bonus(self, user_id: str, *, room_id: str, event: str) -> int:
        combat = self._effective_combat_view(user_id, room_id=room_id, event=event)
        return _to_int(combat.get("damage_bonus", 0), 0)

    # ============================================================
    # Room / routing helpers
    # ============================================================
    def _room_members(self, room_key: str) -> List[Tuple[str, dict]]:
        """Return canonical non-Cube room membership through Presence."""
        members = self.bot.presence.get_room_members(room_key, resolve=True)
        return [
            (uid, ch)
            for uid, ch in members
            if isinstance(ch, dict) and not ch.get("in_cube")
        ]

    async def _broadcast_room(
        self,
        ctx: commands.Context,
        room_key: str,
        msg: str,
        *,
        exclude: Optional[Set[str]] = None,
    ):
        exclude = exclude or set()
        for uid, ch in self._room_members(room_key):
            if uid in exclude:
                continue
            name = (ch.get("name") if isinstance(ch, dict) else None) or "traveler"
            try:
                run_ch = await ensure_player_run_channel(self.bot, ctx, uid, name)
                if run_ch:
                    await run_ch.send(msg)
            except Exception:
                continue

    async def _send_to_player(
        self,
        ctx: commands.Context,
        user_id: str,
        player_name: str,
        msg: str,
        *,
        critical: bool = False,
    ):
        run_ch = None
        try:
            run_ch = await ensure_player_run_channel(self.bot, ctx, user_id, player_name)
        except Exception:
            run_ch = None

        sent_run = False
        if run_ch:
            try:
                await run_ch.send(msg)
                sent_run = True
            except Exception:
                sent_run = False

        if critical and not sent_run:
            try:
                await ctx.send(msg)
            except Exception:
                pass

    # ============================================================
    # Combat state helpers
    # ============================================================
    def _combat_state(self, room_id: str) -> Dict[str, Any]:
        combats = self.bot.state.combats  # type: ignore[attr-defined]
        st = combats.setdefault(
            room_id,
            {
                "active": False,
                "round": 1,
                "turn_index": 0,
                "order": [],              # list[("player", uid) | ("enemy", enemy_inst_id)]
                "engaged": set(),         # set[user_id] - committed fighters
                "pending_join": set(),    # set[user_id] - queued until next round
                "intents": {},            # user_id -> {"type":"attack","target":"enemy_inst_id"}
                "prompted": {},           # user_id -> last_round_prompted
                "acted_this_round": {},   # "player:uid" / "enemy:inst" -> round_num
                "lock": asyncio.Lock(),
                "task": None,             # asyncio.Task
                "tick_guard": 0,
            },
        )
        return st

    def _lock_for_room(self, room_id: str) -> asyncio.Lock:
        st = self._combat_state(room_id)
        lk = st.get("lock")
        if not isinstance(lk, asyncio.Lock):
            lk = asyncio.Lock()
            st["lock"] = lk
        return lk

    def _set_engaged_flag(self, user_id: str, engaged: bool) -> None:
        ch = self._ensure_character_schema(user_id)
        ch.setdefault("flags", {})
        ch["flags"]["in_combat"] = bool(engaged)

    # ============================================================
    # Room enemies (raw + effective)
    # ============================================================
    def _get_room(self, room_id: str) -> dict:
        return self.bot.storage.rooms.get(room_id, {}) or {}

    def _get_room_enemies_raw(self, room_id: str) -> Dict[str, dict]:
        room = self._get_room(room_id)
        ens = room.get("enemies", {})
        return ens if isinstance(ens, dict) else {}

    def _get_room_enemies_effective(self, room_id: str) -> Dict[str, dict]:
        """
        IMPORTANT: rooms.json holds instances; enemies.json holds templates.
        Storage resolves template+instance => effective dict for combat display/stats.
        """
        try:
            out = self.bot.storage.resolve_room_enemies(room_id)
            return out if isinstance(out, dict) else {}
        except Exception:
            return self._get_room_enemies_raw(room_id)

    def _enemy_label(self, inst_id: str, enemy: dict) -> str:
        etype = ""
        if isinstance(enemy, dict):
            etype = str(enemy.get("type") or "").strip()
        if etype:
            return f"{etype} ({inst_id})"
        return str(inst_id)

    def _persist_enemy_hp(self, room_id: str, enemy_inst_id: str, new_hp: int) -> None:
        """
        Persist enemy HP to rooms.json *instance* dict.
        This is the critical fix: without it, enemies reset HP every action.
        """
        s = self.bot.storage
        room = s.rooms.get(room_id, {}) or {}
        ens = room.get("enemies", {})
        if not isinstance(ens, dict):
            ens = {}
        inst = ens.get(enemy_inst_id)
        if not isinstance(inst, dict):
            inst = {}
        inst["hp"] = int(new_hp)
        ens[enemy_inst_id] = inst
        room["enemies"] = ens
        s.rooms[room_id] = room

    # ============================================================
    # Initiative / turn helpers
    # ============================================================
    def _roll_initiative_player(self, ch: dict) -> int:
        stats = (ch.get("stats") or {}) if isinstance(ch, dict) else {}
        dex = int(stats.get("dexterity", 10))
        return random.randint(1, 20) + _mod(dex)

    def _roll_initiative_enemy(self, enemy: dict) -> int:
        base = int(enemy.get("initiative", 0) or 0) if isinstance(enemy, dict) else 0
        return random.randint(1, 20) + base

    def _build_order_for_round(self, room_id: str) -> None:
        s = self.bot.storage
        st = self._combat_state(room_id)

        # Merge pending joiners at round boundary
        if isinstance(st.get("pending_join"), set) and st["pending_join"]:
            for uid in list(st["pending_join"]):
                st["engaged"].add(uid)
                st["pending_join"].discard(uid)

        engaged_in_room: List[str] = []
        for uid in list(st["engaged"]):
            try:
                if self.bot.presence.resolve_room_for_user(uid) == room_id:
                    engaged_in_room.append(uid)
                else:
                    st["engaged"].discard(uid)
                    self._set_engaged_flag(uid, False)
                    st["intents"].pop(uid, None)
            except Exception:
                st["engaged"].discard(uid)
                self._set_engaged_flag(uid, False)
                st["intents"].pop(uid, None)

        enemies = self._get_room_enemies_effective(room_id)

        rolls: List[Tuple[int, Tuple[str, str]]] = []
        for uid in engaged_in_room:
            ch = self.bot.presence.get_character(uid)
            if not isinstance(ch, dict):
                ch = self._ensure_character_schema(uid)
            ini = self._roll_initiative_player(ch)
            rolls.append((ini, ("player", uid)))

        for inst_id, enemy in enemies.items():
            ini = self._roll_initiative_enemy(enemy if isinstance(enemy, dict) else {})
            rolls.append((ini, ("enemy", str(inst_id))))

        rolls.sort(key=lambda x: x[0], reverse=True)
        st["order"] = [who for _, who in rolls]
        st["turn_index"] = 0
        st["active"] = bool(st["order"])
        st["acted_this_round"] = {}

    def _current_actor(self, room_id: str) -> Optional[Tuple[str, str]]:
        st = self._combat_state(room_id)
        if not st["active"] or not st["order"]:
            return None
        idx = int(st["turn_index"]) % len(st["order"])
        try:
            return st["order"][idx]
        except Exception:
            return None

    def _advance_turn_loop_only(self, room_id: str) -> None:
        st = self._combat_state(room_id)
        if not st["active"] or not st["order"]:
            return

        st["turn_index"] += 1

        if st["turn_index"] >= len(st["order"]):
            st["turn_index"] = 0
            st["round"] += 1
            self._build_order_for_round(room_id)

    def _cleanup_dead_from_order(self, room_id: str) -> None:
        st = self._combat_state(room_id)
        enemies = self._get_room_enemies_effective(room_id)

        new_order: List[Tuple[str, str]] = []
        for kind, ident in st["order"]:
            if kind == "enemy" and ident not in enemies:
                continue
            if kind == "player" and ident not in st["engaged"] and ident not in st.get("pending_join", set()):
                continue
            new_order.append((kind, ident))

        st["order"] = new_order
        if st["order"]:
            st["turn_index"] = int(st["turn_index"]) % len(st["order"])
        else:
            st["turn_index"] = 0

    def _end_combat(self, room_id: str) -> None:
        st = self._combat_state(room_id)
        st["active"] = False
        st["order"] = []
        st["turn_index"] = 0
        st["round"] = 1
        st["prompted"] = {}
        st["intents"] = {}
        st["pending_join"] = set()
        st["acted_this_round"] = {}
        st["tick_guard"] = 0

    # ============================================================
    # Enemy matching
    # ============================================================
    def _match_enemy_name(self, ens: dict, enemy_name: str) -> Tuple[Optional[str], Optional[str]]:
        if not ens:
            return None, "There’s nothing hostile here."

        raw = (enemy_name or "").strip()
        if not raw:
            return None, "Attack what?"

        key = raw.lower()

        # Exact match against instance ids
        exact_map = {str(en).strip().lower(): en for en in ens.keys()}
        if key in exact_map:
            return str(exact_map[key]), None

        # Substring match (instance ids contain template-ish bits)
        hits = []
        for en in ens.keys():
            s = str(en).strip().lower()
            if key in s:
                hits.append(str(en))

        if len(hits) == 1:
            return hits[0], None

        if len(hits) > 1:
            show = ", ".join(f"**{h}**" for h in hits[:8])
            if len(hits) > 8:
                show += ", …"
            return None, f"Too many matches for `{raw}`. Be specific: {show}"

        return None, "That foe isn’t here."

    # ============================================================
    # Intent helpers
    # ============================================================
    def _set_intent_attack(self, room_id: str, user_id: str, enemy_inst_id: str) -> None:
        st = self._combat_state(room_id)
        st["intents"][user_id] = {"type": "attack", "target": str(enemy_inst_id)}

    def _clear_intent(self, room_id: str, user_id: str) -> None:
        st = self._combat_state(room_id)
        st["intents"].pop(user_id, None)

    def _get_intent(self, room_id: str, user_id: str) -> Optional[dict]:
        st = self._combat_state(room_id)
        it = st["intents"].get(user_id)
        return it if isinstance(it, dict) else None

    def _auto_seed_intent_if_unset(self, room_id: str, user_id: str) -> Optional[str]:
        st = self._combat_state(room_id)
        intents = st.get("intents", {})
        if isinstance(intents, dict) and user_id in intents:
            return None

        enemies = self._get_room_enemies_effective(room_id)
        if not enemies or not isinstance(enemies, dict):
            return None

        if len(enemies) == 1:
            inst_id = next(iter(enemies.keys()))
            st.setdefault("intents", {})
            st["intents"][user_id] = {"type": "attack", "target": str(inst_id)}
            return str(inst_id)

        return None

    # ============================================================
    # Loop/task control
    # ============================================================
    def _start_loop_if_needed(self, ctx: commands.Context, room_id: str) -> None:
        st = self._combat_state(room_id)
        task = st.get("task")
        if task and isinstance(task, asyncio.Task) and not task.done():
            return

        new_task = asyncio.create_task(self._combat_loop(ctx, room_id))

        def _done(t: asyncio.Task):
            try:
                exc = t.exception()
                if exc:
                    print(f"[COMBAT] loop crashed room={room_id}: {type(exc).__name__}: {exc}")
            except asyncio.CancelledError:
                print(f"[COMBAT] loop cancelled room={room_id}")
            except Exception as e:
                print(f"[COMBAT] loop done-check failed room={room_id}: {type(e).__name__}: {e}")

        new_task.add_done_callback(_done)
        st["task"] = new_task

    async def _combat_loop(self, ctx: commands.Context, room_id: str) -> None:
        st = self._combat_state(room_id)
        lock = self._lock_for_room(room_id)

        async with lock:
            if not st["active"]:
                return

        while True:
            actor: Optional[Tuple[str, str]] = None
            end_msg: Optional[str] = None

            async with lock:
                if not st["active"] or not st["order"]:
                    return

                st["tick_guard"] = int(st.get("tick_guard", 0)) + 1
                if st["tick_guard"] > 600:
                    print(f"[COMBAT] tick_guard tripped room={room_id}; ending combat to prevent stall.")
                    self._end_combat(room_id)
                    end_msg = "🕊️ Combat collapses under its own contradictions."
                else:
                    # Clean order for removed actors
                    self._cleanup_dead_from_order(room_id)

                    if not st["order"]:
                        self._end_combat(room_id)
                        end_msg = "✅ Combat fades. The room exhales."
                    else:
                        enemies_now = self._get_room_enemies_effective(room_id)
                        if not enemies_now:
                            for uid in list(st["engaged"]):
                                self._set_engaged_flag(uid, False)
                            st["engaged"].clear()
                            self._end_combat(room_id)
                            end_msg = "✅ Combat fades. The room exhales."
                        else:
                            if not st["engaged"] and not st.get("pending_join"):
                                self._end_combat(room_id)
                                end_msg = "🕊️ No one commits to the fight. Violence loses momentum."
                            else:
                                # Find next actor who hasn't acted this round (bounded)
                                attempts = 0
                                while attempts < MAX_SKIP_ATTEMPTS_PER_TICK:
                                    candidate = self._current_actor(room_id)
                                    if not candidate:
                                        break
                                    k, ident = candidate
                                    akey = f"{k}:{ident}"
                                    acted_round = (st.get("acted_this_round") or {}).get(akey)
                                    if acted_round != st["round"]:
                                        actor = candidate
                                        break
                                    self._advance_turn_loop_only(room_id)
                                    attempts += 1

                                if actor is None and attempts >= MAX_SKIP_ATTEMPTS_PER_TICK:
                                    # Something's inconsistent; bump round safely
                                    print(f"[COMBAT] skip-guard tripped room={room_id}; forcing new round.")
                                    st["turn_index"] = 0
                                    st["round"] += 1
                                    self._build_order_for_round(room_id)

            if end_msg:
                await self._broadcast_room(ctx, room_id, end_msg)
                return

            if not actor:
                await asyncio.sleep(TURN_DELAY_SECONDS)
                continue

            kind, ident = actor
            try:
                if kind == "enemy":
                    await self._enemy_step(ctx, room_id, ident)
                else:
                    await self._player_step(ctx, room_id, ident)
            except Exception as e:
                print(f"[COMBAT] step error room={room_id} actor={actor}: {type(e).__name__}: {e}")

            async with lock:
                if st["active"]:
                    st.setdefault("acted_this_round", {})
                    st["acted_this_round"][f"{kind}:{ident}"] = st["round"]
                    self._advance_turn_loop_only(room_id)

            await asyncio.sleep(TURN_DELAY_SECONDS)

    # ============================================================
    # Steps
    # ============================================================
    async def _player_step(self, ctx: commands.Context, room_id: str, uid: str) -> None:
        s = self.bot.storage
        st = self._combat_state(room_id)
        lock = self._lock_for_room(room_id)

        run_target: Optional[Tuple[str, str, str]] = None
        pass_to_send: Optional[Tuple[str, str, List[str], List[str]]] = None

        async with lock:
            if not st["active"]:
                return
            if uid not in st["engaged"]:
                return

            ch = self._ensure_character_schema(uid)
            name = ch.get("name", "traveler")

            intent = self._get_intent(room_id, uid)
            enemies = self._get_room_enemies_effective(room_id)

            if not intent or intent.get("type") != "attack":
                last = (st.get("prompted") or {}).get(uid)
                if last != st["round"]:
                    st.setdefault("prompted", {})
                    st["prompted"][uid] = st["round"]
                    run_target = (uid, name, "⏳ Your turn. Use `!attack <foe>` to set intent, or `!hold` to pass.")
                s.save_characters()
                return

            target_inst = str(intent.get("target") or "").strip()
            if target_inst and target_inst in enemies:
                en_inst = target_inst
                err = None
            else:
                en_inst, err = self._match_enemy_name(enemies, target_inst)

            if err or not en_inst:
                st["intents"].pop(uid, None)
                run_target = (uid, name, f"⚠️ Intent lost: {err or 'target not found'}.")
                s.save_characters()
                return

            player_msgs, room_msgs, _ended = self._perform_player_attack(room_id, uid, en_inst)
            s.save_characters()
            s.save_rooms()
            pass_to_send = (uid, name, player_msgs, room_msgs)

        if pass_to_send:
            _uid, _name, pmsgs, rmsgs = pass_to_send
            try:
                run_ch = await ensure_player_run_channel(self.bot, ctx, _uid, _name)
                if run_ch:
                    for m in pmsgs:
                        await run_ch.send(m)
                else:
                    for m in pmsgs:
                        await ctx.send(m)
            except Exception:
                try:
                    for m in pmsgs:
                        await ctx.send(m)
                except Exception:
                    pass

            for rm in rmsgs:
                await self._broadcast_room(ctx, room_id, rm, exclude={_uid})
            return

        if run_target:
            tuid, tname, tmsg = run_target
            await self._send_to_player(ctx, tuid, tname, tmsg)

    async def _enemy_step(self, ctx: commands.Context, room_id: str, enemy_inst_id: str) -> None:
        s = self.bot.storage
        st = self._combat_state(room_id)
        lock = self._lock_for_room(room_id)

        target_uid: Optional[str] = None
        target_name: str = "traveler"
        msg_to_target: Optional[str] = None
        msg_death_room: Optional[str] = None
        msg_death_target: Optional[str] = None
        realm_feed: Optional[str] = None

        async with lock:
            if not st["active"]:
                return

            enemies = self._get_room_enemies_effective(room_id)
            if enemy_inst_id not in enemies:
                return

            enemy = enemies.get(enemy_inst_id, {})
            if not isinstance(enemy, dict):
                enemy = {}

            label = self._enemy_label(enemy_inst_id, enemy)

            room_players = self._room_members(room_id)
            engaged_players = [uid for uid, _ch in room_players if uid in st["engaged"]]
            non_engaged_players = [uid for uid, _ch in room_players if uid not in st["engaged"]]

            if not engaged_players:
                return

            # Prefer engaged targets; spill is rare
            if engaged_players:
                if non_engaged_players and random.random() >= 0.90:
                    target_uid = random.choice(non_engaged_players)
                else:
                    target_uid = random.choice(engaged_players)

            if not target_uid:
                return

            target = self._ensure_character_schema(target_uid)
            target_name = target.get("name", "traveler")

            enemy_atk = int(enemy.get("attack", 4))
            defense = equipped_defense(s.items_db, target.get("equipped", {}))
            taken = max(0, enemy_atk - defense)

            hp_before = int(target.get("stats", {}).get("hp", 20))
            target["stats"]["hp"] = max(0, hp_before - taken)

            msg_to_target = (
                f"👹 **{label}** strikes **{target_name}** for **{taken}** "
                f"(after armor {defense}). (HP: {hp_before}→{target['stats']['hp']})"
            )

            if int(target["stats"]["hp"]) <= 0:
                msg_death_room = f"☠️ **{target_name}** falls."

                safe = "neptune_lounge"
                target["current_room"] = safe
                target["stats"]["hp"] = int(target["stats"].get("max_hp", 20))
                target["pending_return_echo"] = True

                st["engaged"].discard(target_uid)
                self._set_engaged_flag(target_uid, False)
                st["intents"].pop(target_uid, None)

                whispers = [
                    "The Cube hums once — a low, intimate note — and stitches you back into continuity.",
                    "For a moment you are nowhere. Then the Lounge catches you like a net of warm light.",
                    "You feel a soft rewind behind your eyes. Reality re-aligns with a quiet click.",
                    "A thin static crawls over your skin… and then the smell of chips returns like a blessing.",
                    "Somewhere nearby, a presence notices — not alarmed, not amused. Simply *aware*.",
                ]
                whisper = random.choice(whispers)

                msg_death_target = (
                    f"☠️ **{target_name}** falls.\n"
                    f"🧊 *{whisper}*\n"
                    f"🛋️ **Respawned** in the Neptune Lounge."
                )
                realm_feed = f"☠️ **{target_name}** fractures — the Cube rethreads them in the Neptune Lounge."

            s.save_characters()

        if target_uid and msg_to_target:
            await self._send_to_player(ctx, target_uid, target_name, msg_to_target, critical=True)

        if target_uid and msg_death_target:
            await self._send_to_player(ctx, target_uid, target_name, msg_death_target, critical=True)

        if msg_death_room:
            await self._broadcast_room(ctx, room_id, msg_death_room, exclude={target_uid} if target_uid else set())

        if realm_feed and hasattr(self.bot, "send_to_realm_feed"):
            try:
                await self.bot.send_to_realm_feed(realm_feed)
            except Exception:
                pass

    # ============================================================
    # Core combat action (player attack tick)
    # ============================================================
    def _perform_player_attack(self, room_id: str, user_id: str, enemy_inst_id: str) -> Tuple[List[str], List[str], bool]:
        s = self.bot.storage
        st = self._combat_state(room_id)

        c = self._ensure_character_schema(user_id)
        attacker = c.get("name", "traveler")

        enemies = self._get_room_enemies_effective(room_id)
        enemy = enemies.get(enemy_inst_id, {})
        if not isinstance(enemy, dict):
            enemy = {}

        label = self._enemy_label(enemy_inst_id, enemy)

        # Weapon damage roll
        roll, dmin, dmax = weapon_damage(s.items_db, c)
        dmg = random.randint(int(dmin), max(int(dmin), int(dmax)))

        # Resolver-derived flat damage bonus
        dmg_bonus = self._effective_damage_bonus(user_id, room_id=room_id, event="attack")
        if dmg_bonus:
            dmg += int(dmg_bonus)

        crit_txt = ""
        if roll == 20:
            dmg += random.randint(2, 6)
            crit_txt = " (critical!)"

        # IMPORTANT: enemy_hp_before should be from the *instance* if present
        raw = self._get_room_enemies_raw(room_id)
        raw_inst = raw.get(enemy_inst_id, {}) if isinstance(raw, dict) else {}
        raw_hp = raw_inst.get("hp") if isinstance(raw_inst, dict) else None

        enemy_hp_before = int(raw_hp) if raw_hp is not None else int(enemy.get("hp", 10))
        new_hp = max(0, enemy_hp_before - dmg)

        # Persist to rooms.json instance
        self._persist_enemy_hp(room_id, enemy_inst_id, new_hp)

        bonus_txt = f" (+{dmg_bonus} mods)" if dmg_bonus else ""

        player_msgs = [
            f"🌀 ⚔️ **{attacker}** strikes **{label}** for **{dmg}** damage{crit_txt}{bonus_txt}. "
            f"(HP: {enemy_hp_before}→{new_hp})"
        ]
        room_msgs = [f"⚔️ **{attacker}** attacks **{label}**{crit_txt}."]

        defeated = new_hp <= 0
        if defeated:
            # Use effective enemy dict for loot/xp
            loot = enemy.get("loot", [])
            xp = int(enemy.get("xp", 1))
            c["xp"] = int(c.get("xp", 0)) + xp

            loot_msg = ""
            public_loot_hint = ""
            if isinstance(loot, list) and loot:
                drop = random.choice(loot)
                add_to_bag(c.setdefault("bag", {}), drop, 1)
                loot_msg = f" Loot: **{drop}**."
                public_loot_hint = " (something drops)"

            player_msgs.append(f"💀 **{attacker}** defeats **{label}**! +{xp} XP.{loot_msg}")
            room_msgs.append(f"💀 **{attacker}** defeats **{label}**!{public_loot_hint}")

            # Remove the instance from rooms.json
            room = s.rooms.get(room_id, {}) or {}
            room_ens = room.get("enemies", {})
            if not isinstance(room_ens, dict):
                room_ens = {}
            room_ens.pop(enemy_inst_id, None)
            room["enemies"] = room_ens
            s.rooms[room_id] = room

        # End conditions
        enemies_now = self._get_room_enemies_effective(room_id)
        if not enemies_now:
            for uid in list(st["engaged"]):
                self._set_engaged_flag(uid, False)
            st["engaged"].clear()
            self._end_combat(room_id)
            room_msgs.append("✅ Combat fades. The room exhales.")
            return player_msgs, room_msgs, True

        if not st["engaged"]:
            self._end_combat(room_id)
            room_msgs.append("🕊️ No one commits to the fight. Violence loses momentum.")
            return player_msgs, room_msgs, True

        return player_msgs, room_msgs, False

    # ============================================================
    # Commands
    # ============================================================
    @commands.command(name="combat", aliases=["draw", "engage"])
    async def combat_cmd(self, ctx: commands.Context):
        s = self.bot.storage
        user_id = str(ctx.author.id)

        c = self._ensure_character_schema(user_id)
        name = c.get("name", ctx.author.display_name)

        if c.get("in_cube"):
            await ctx.send("Inside the Cube, combat is… theoretical. For now.")
            return

        room_id = self.bot.presence.resolve_room_for_user(user_id)
        enemies = self._get_room_enemies_effective(room_id)
        if not enemies:
            await ctx.send("There’s nothing hostile here. (But you can still stay alert.)")
            return

        st = self._combat_state(room_id)
        lock = self._lock_for_room(room_id)

        auto_target: Optional[str] = None
        start_lines: List[str] = []

        async with lock:
            if not st["active"]:
                st["engaged"].add(user_id)
                self._set_engaged_flag(user_id, True)

                auto_target = self._auto_seed_intent_if_unset(room_id, user_id)

                st["round"] = 1
                self._build_order_for_round(room_id)
                st["active"] = True
                st["tick_guard"] = 0

                order_names: List[str] = []
                enemies_eff = self._get_room_enemies_effective(room_id)
                for kind, ident in st["order"]:
                    if kind == "enemy":
                        e = enemies_eff.get(ident, {})
                        order_names.append(self._enemy_label(ident, e if isinstance(e, dict) else {}))
                    else:
                        ch = self.bot.presence.get_character(ident) or {}
                        nm = ch.get("name", ident[-4:])
                        order_names.append(str(nm))
                ini_line = " → ".join(order_names) if order_names else "—"

                start_lines = [
                    "⚔️ You draw into combat. Initiative sparks.",
                    f"🎲 Initiative: {ini_line}",
                ]
            else:
                st.setdefault("pending_join", set())
                st["pending_join"].add(user_id)
                self._set_engaged_flag(user_id, True)

                auto_target = self._auto_seed_intent_if_unset(room_id, user_id)

                start_lines = [
                    "⚔️ You commit to the fight. You are now engaged.",
                    "🌀 You’ll slot into initiative at the start of the next round.",
                ]

            s.save_characters()
            self._start_loop_if_needed(ctx, room_id)

        dmg_bonus = self._effective_damage_bonus(user_id, room_id=room_id, event="combat_start")
        await ctx.send(start_lines[0])
        await ctx.send(start_lines[1])
        await ctx.send(f"🧬 Combat mods: damage_bonus=+{dmg_bonus}")

        if auto_target:
            enemies_eff = self._get_room_enemies_effective(room_id)
            e = enemies_eff.get(auto_target, {})
            label = self._enemy_label(auto_target, e if isinstance(e, dict) else {})
            await ctx.send(f"🎯 Default intent: attack → **{label}** (Auto-rounds ON)")

        await self._broadcast_room(ctx, room_id, f"⚔️ **{name}** draws into combat.", exclude={user_id})

    @commands.command(name="disengage", aliases=["sheath", "flee"])
    async def disengage_cmd(self, ctx: commands.Context):
        s = self.bot.storage
        user_id = str(ctx.author.id)
        c = self._ensure_character_schema(user_id)
        name = c.get("name", ctx.author.display_name)

        room_id = self.bot.presence.resolve_room_for_user(user_id)
        st = self._combat_state(room_id)
        lock = self._lock_for_room(room_id)

        async with lock:
            st["engaged"].discard(user_id)
            if isinstance(st.get("pending_join"), set):
                st["pending_join"].discard(user_id)

            self._set_engaged_flag(user_id, False)
            self._clear_intent(room_id, user_id)

            do_end = bool(st["active"] and not st["engaged"] and not st.get("pending_join"))
            if do_end:
                self._end_combat(room_id)

            s.save_characters()

        await ctx.send("🕊️ You disengage. You’re still nearby — and danger can still spill your way.")
        await self._broadcast_room(ctx, room_id, f"🕊️ **{name}** disengages.", exclude={user_id})
        if do_end:
            await self._broadcast_room(ctx, room_id, "🕊️ No one commits to the fight. Violence loses momentum.")

    @commands.command(name="combat_status", aliases=["status"])
    async def combat_status(self, ctx: commands.Context):
        s = self.bot.storage
        user_id = str(ctx.author.id)
        c = self._ensure_character_schema(user_id)

        if c.get("in_cube"):
            await ctx.send("The Cube does not provide a combat status readout. Yet.")
            return

        room_id = self.bot.presence.resolve_room_for_user(user_id)
        st = self._combat_state(room_id)
        enemies = self._get_room_enemies_effective(room_id)

        if not st["active"]:
            await ctx.send("🕊️ No active combat here.")
            return

        actor = self._current_actor(room_id)
        if actor:
            kind, ident = actor
            if kind == "player":
                ch = self.bot.presence.get_character(ident) or {}
                nm = ch.get("name", "someone")
                turn_txt = f"**Player turn:** {nm}"
            else:
                e = enemies.get(ident, {})
                turn_txt = f"**Enemy turn:** {self._enemy_label(ident, e if isinstance(e, dict) else {})}"
        else:
            turn_txt = "Turn: —"

        engaged_names = []
        for uid in list(st["engaged"]):
            ch = self.bot.presence.get_character(uid) or {}
            nm = ch.get("name", uid[-4:])
            engaged_names.append(nm)

        pending_names = []
        for uid in list(st.get("pending_join", set())):
            ch = self.bot.presence.get_character(uid) or {}
            nm = ch.get("name", uid[-4:])
            pending_names.append(nm)

        intent = st.get("intents", {}).get(user_id) if isinstance(st.get("intents"), dict) else None
        if isinstance(intent, dict) and intent.get("type") == "attack":
            tgt = str(intent.get("target", "—"))
            e = enemies.get(tgt, {})
            intent_txt = f"attack → **{self._enemy_label(tgt, e if isinstance(e, dict) else {})}**"
        else:
            intent_txt = "—"

        dmg_bonus = self._effective_damage_bonus(user_id, room_id=room_id, event="status")

        await ctx.send(
            "⚔️ **Combat Status**\n"
            f"Room: `{room_id}`\n"
            f"Round: **{st['round']}**\n"
            f"{turn_txt}\n"
            f"Engaged: {', '.join(engaged_names) if engaged_names else '—'}\n"
            f"Pending next round: {', '.join(pending_names) if pending_names else '—'}\n"
            f"Enemies: {', '.join([self._enemy_label(k, v if isinstance(v, dict) else {}) for k, v in enemies.items()]) if enemies else '—'}\n"
            f"Your intent: {intent_txt}\n"
            f"Mods: damage_bonus=+{dmg_bonus}\n"
            f"Turn delay: {TURN_DELAY_SECONDS}s"
        )

    @commands.command()
    async def attack(self, ctx: commands.Context, *, enemy_name: str):
        s = self.bot.storage
        user_id = str(ctx.author.id)
        c = self._ensure_character_schema(user_id)

        if c.get("in_cube"):
            await ctx.send("There’s nothing to fight in the atrium. (For now.)")
            return

        room_id = self.bot.presence.resolve_room_for_user(user_id)
        st = self._combat_state(room_id)
        lock = self._lock_for_room(room_id)

        if not st["active"]:
            await ctx.send("⚠️ No active combat here. Use `!combat` (or `!draw`) to engage first.")
            return

        if user_id not in st["engaged"] and user_id not in st.get("pending_join", set()):
            await ctx.send("⚠️ You’re not engaged. Use `!combat` to commit first.")
            return

        enemies = self._get_room_enemies_effective(room_id)
        en_inst, err = self._match_enemy_name(enemies, enemy_name)
        if err or not en_inst:
            await ctx.send(err or "That foe isn’t here.")
            return

        async with lock:
            self._set_intent_attack(room_id, user_id, str(en_inst))
            s.save_characters()
            self._start_loop_if_needed(ctx, room_id)

        e = enemies.get(en_inst, {})
        label = self._enemy_label(en_inst, e if isinstance(e, dict) else {})
        await ctx.send(f"🎯 Intent set: attack → **{label}** (Auto-rounds ON)")


async def setup(bot):
    await bot.add_cog(CombatCog(bot))
