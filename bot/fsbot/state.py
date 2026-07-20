# ============================================================
# FILE META — fsbot/state.py
# Canonical name: GameState (world clock + era resolution + heartbeat)
#
# Version: v0.4.0
# Last edited: 2026-07-17
#
# Authority:
# - AUTHORITATIVE for runtime temporal state:
#   (world clock, heartbeat lifecycle, era resolution)
# - AUTHORITATIVE for minimal player SHAPE guarantees and void-rescue repair
# - NOT authoritative for runtime presence queries (Presence owns that boundary)
#
# Purpose:
# - Maintains the single soft world clock (world_time_seconds)
# - Owns heartbeat lifecycle (periodic tick + time advancement)
# - Resolves player era and era-specific time profiles
# - Provides minimal safety guarantees for player character records
#   (ensure_player_records — shape, not migration, characters.json ONLY)
# - Provides limited "void rescue" room resolution (repair invalid room -> fallback)
#
# Owns (persistence / authority):
# - data/time/world_clock.json (world clock persistence)
# - In-memory world_time_seconds (advanced by heartbeat)
# - Era time profile loading + cache (era_time_profiles.json)
#
# Reads (authoritative JSON / config):
# - characters.json (read-only except for minimal guarantees)
# - era_time_profiles.json
# - config.START_ROOM (fallback placement)
#
# Writes (explicit, scoped):
# - world_clock.json (world_time_seconds persistence)
# - characters.json (ONLY via ensure_player_records shape guarantees + void-rescue repair)
#
# Must NOT own:
# - Any persistence for lockers/cubes/vault (Storage boundary owns those stores)
# - Cube session keys on character records (NO: ch["cube"], ch["in_cube"], ch["cube_context"])
# - Cube schema or cube persistence authority (cubes.json contract is separate)
# - Combat logic, initiative, or turn state
# - Narrative authority or story progression
# - Broad JSON mutation outside world_clock + minimal character safety
#
# Depends on:
# - fsbot.config (paths, START_ROOM, Lavalink)
# - Storage (reference passed at init; state.py must not become persistence authority)
#
# Used by:
# - run_bot.py (boot, heartbeat start, audio init)
# - Presence (delegated canonical room resolution)
# - Cogs (room/era resolution + ensure_player_records)
#
# Operational notes / hazards:
# - Heartbeat must be started exactly once (run_bot on_ready)
# - world_time_seconds is a soft clock (not real-time authoritative)
# - ensure_player_records must remain minimal and non-destructive
#   (no schema migration, no opinionated defaults beyond shape safety)
#
# Change notes (v0.4.0):
# - Removed get_players_in_room(); runtime presence queries now belong to Presence.
# - GameState is now a cleaner world/time, era, shape-safety, and void-rescue service.
#
# Earlier v0.3.4 change retained:
# - Removed cross-store seeding: ensure_player_records() now touches ONLY characters.json.
#   (Cube/lockers/vault guarantees belong to Storage + their cogs.)
# ============================================================

from __future__ import annotations

import os
import json
import asyncio
import time
import logging
from typing import Any, Dict, Optional

# Kept: other modules may rely on discord import side-effects or typing
import discord  # noqa: F401

from fsbot.config import START_ROOM, LAVALINK_URI, LAVALINK_PASSWORD


# Optional audio
try:
    import wavelink  # noqa: F401
    WAVES_OK = True
except Exception:
    WAVES_OK = False


class GameState:
    def __init__(self, storage):
        self.storage = storage
        self.waves_ok = WAVES_OK
        self._audio_ready = False

        # Era Time Profiles (v0)
        self._era_time_profiles: Optional[Dict[str, Any]] = None

        # Heartbeat (v0)
        self._heartbeat_task: Optional[asyncio.Task] = None

        # World clock (persisted)
        self.world_time_seconds: int = 0
        self.WORLD_CLOCK_FILE = "data/time/world_clock.json"
        self._heartbeat_ticks: int = 0
        self._persist_every_ticks: int = 5  # save every N heartbeats

        # Logger (use same namespace as run_bot.py)
        self.log = logging.getLogger("futuresky")

        # Load/seed world clock early so logs show on startup
        self.load_world_clock()

    # ---------------------------
    # Audio (optional)
    # ---------------------------

    async def init_audio(self, bot) -> None:
        if not self.waves_ok:
            return
        try:
            import wavelink

            node = wavelink.Node(uri=LAVALINK_URI, password=LAVALINK_PASSWORD)
            await wavelink.Pool.connect(client=bot, nodes=[node])
            self._audio_ready = True
            self.log.info("[AUDIO] Lavalink connected.")
        except Exception as e:
            self.log.warning(f"[AUDIO] Lavalink connection failed: {type(e).__name__}: {e}")

    async def play_music(self, ctx, soundcloud_url: str) -> None:
        """Best-effort. Non-authoritative."""
        if not self.waves_ok:
            return
        try:
            import wavelink

            if not getattr(ctx.author, "voice", None):
                return

            vc: Optional[wavelink.Player] = ctx.voice_client
            if not vc:
                vc = await ctx.author.voice.channel.connect(cls=wavelink.Player)

            tracks = await wavelink.Pool.fetch_tracks(soundcloud_url)
            if tracks:
                await vc.play(tracks[0])
        except Exception as e:
            # Keep user-facing error minimal
            try:
                await ctx.send(f"⚠️ Music error: {type(e).__name__}")
            except Exception:
                pass
            self.log.warning(f"[AUDIO] play_music error: {type(e).__name__}: {e}")

    # ---------------------------
    # World Clock Persistence (v0)
    # ---------------------------

    def _atomic_write_json(self, path: str, data: dict) -> None:
        """Atomic JSON write: write to tmp then replace. Ensures parent dir exists."""
        parent = os.path.dirname(path)
        if parent:
            os.makedirs(parent, exist_ok=True)

        tmp = f"{path}.tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, path)

    def load_world_clock(self) -> None:
        """Load world_time_seconds from JSON. Safe if missing/malformed."""
        try:
            if not os.path.exists(self.WORLD_CLOCK_FILE):
                os.makedirs(os.path.dirname(self.WORLD_CLOCK_FILE), exist_ok=True)
                self._atomic_write_json(
                    self.WORLD_CLOCK_FILE,
                    {"version": "v1", "world_time_seconds": int(self.world_time_seconds)},
                )
                self.log.info(f"[CLOCK] seeded {self.WORLD_CLOCK_FILE} world_time={self.world_time_seconds}s")
                return

            with open(self.WORLD_CLOCK_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

            w = data.get("world_time_seconds", 0)
            if isinstance(w, (int, float)) and int(w) >= 0:
                self.world_time_seconds = int(w)
                self.log.info(f"[CLOCK] loaded world_time={self.world_time_seconds}s from {self.WORLD_CLOCK_FILE}")
            else:
                self.log.warning(f"[CLOCK] invalid world_time_seconds in {self.WORLD_CLOCK_FILE}; using 0")
                self.world_time_seconds = 0

        except Exception as e:
            self.log.warning(f"[CLOCK] load failed: {type(e).__name__}: {e}")
            self.world_time_seconds = 0

    def save_world_clock(self) -> None:
        """Persist world_time_seconds atomically to avoid corruption on crash."""
        try:
            payload = {"version": "v1", "world_time_seconds": int(self.world_time_seconds)}
            self._atomic_write_json(self.WORLD_CLOCK_FILE, payload)
            self.log.info(f"[CLOCK] saved world_time={self.world_time_seconds}s")
        except Exception as e:
            self.log.warning(f"[CLOCK] save failed: {type(e).__name__}: {e}")

    # ---------------------------
    # Era Time Profiles (v0) — Loader + Lookup
    # ---------------------------

    def load_era_time_profiles(self) -> Dict[str, Any]:
        """Load era time metabolism profiles from JSON (cached). Safe fallback if missing/malformed."""
        if self._era_time_profiles is not None:
            return self._era_time_profiles

        from fsbot.config import ERA_TIME_PROFILES_FILE

        try:
            with open(ERA_TIME_PROFILES_FILE, "r", encoding="utf-8") as f:
                self._era_time_profiles = json.load(f)
        except Exception:
            # Safe fallback: manzo-like defaults
            self._era_time_profiles = {
                "version": "fallback",
                "default": "manzo",
                "profiles": {"manzo": {"label": "Fallback Manzo", "era_time_multiplier": 60}},
            }

        return self._era_time_profiles

    def get_era_time_profile(self, era: Optional[str] = None) -> Dict[str, Any]:
        """Return a single era profile; falls back to default."""
        data = self.load_era_time_profiles()
        default_era = str(data.get("default", "manzo")).lower()
        profiles = data.get("profiles", {})

        key = (era or default_era).lower()
        return profiles.get(key) or profiles.get(default_era) or {"label": "Manzo Default", "era_time_multiplier": 60}

    def resolve_default_era(self) -> str:
        """v0: single default era metabolism; later: per-room/per-player metabolism."""
        p = self.load_era_time_profiles()
        return str(p.get("default", "manzo")).lower()

    # ---------------------------
    # Era-by-room helpers (v0)
    # ---------------------------

    def resolve_era_for_room(self, room_id: str) -> str:
        """rooms.json may include room['era']. Fallback to profiles default if missing."""
        try:
            room = self.storage.rooms.get(room_id, {}) if hasattr(self.storage, "rooms") else {}
            if isinstance(room, dict):
                era = room.get("era")
                if isinstance(era, str) and era.strip():
                    return era.strip().lower()
        except Exception:
            pass
        return self.resolve_default_era()

    def resolve_era_for_user(self, user_id: str) -> str:
        """Resolve era based on the user's current room."""
        try:
            room_id = self.resolve_room_for_user(user_id)
            return self.resolve_era_for_room(room_id)
        except Exception:
            return self.resolve_default_era()

    # ---------------------------
    # Heartbeat (v0)
    # ---------------------------

    async def _heartbeat_loop(self, interval_seconds: int = 60) -> None:
        await asyncio.sleep(2)  # small jitter so restarts don't align perfectly

        last = time.time()
        while True:
            try:
                now = time.time()
                real_elapsed = max(1, int(now - last))
                last = now

                era = self.resolve_default_era()
                profile = self.get_era_time_profile(era)
                mult = int(profile.get("era_time_multiplier", 60))

                era_advanced = real_elapsed * mult
                self.world_time_seconds += era_advanced

                self._heartbeat_ticks += 1
                if self._persist_every_ticks > 0 and (self._heartbeat_ticks % self._persist_every_ticks == 0):
                    self.save_world_clock()

                self.log.info(
                    f"[HEARTBEAT] real={real_elapsed}s era={era} mult={mult} "
                    f"era_advanced={era_advanced}s world_time={self.world_time_seconds}s"
                )

            except Exception as e:
                self.log.exception(f"[HEARTBEAT] ERROR: {type(e).__name__}: {e}")

            await asyncio.sleep(interval_seconds)

    def start_heartbeat(self, interval_seconds: int = 60, persist_every_ticks: int = 5) -> None:
        """Start heartbeat if not already running. Safe to call multiple times."""
        try:
            self._persist_every_ticks = int(persist_every_ticks)
        except Exception:
            self._persist_every_ticks = 5

        if self._heartbeat_task and not self._heartbeat_task.done():
            return

        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop(interval_seconds=interval_seconds))
        self.log.info(f"[HEARTBEAT] started interval={interval_seconds}s persist_every_ticks={self._persist_every_ticks}")

    def stop_heartbeat(self) -> None:
        """Optional. Not used yet, but safe to have."""
        try:
            self.save_world_clock()
        except Exception:
            pass

        if self._heartbeat_task and not self._heartbeat_task.done():
            self._heartbeat_task.cancel()
        self._heartbeat_task = None

    # ---------------------------
    # Player record guarantees (contract-aligned)
    # ---------------------------

    def _baseline_stats(self) -> Dict[str, int]:
        return {
            "strength": 10,
            "dexterity": 10,
            "constitution": 10,
            "intelligence": 10,
            "wisdom": 10,
            "charisma": 10,
            "max_hp": 20,
            "hp": 20,
        }

    def _baseline_pools(self) -> Dict[str, Dict[str, int]]:
        return {
            "earth": {"current": 0, "max": 0},
            "water": {"current": 0, "max": 0},
            "fire": {"current": 0, "max": 0},
            "air": {"current": 0, "max": 0},
            "ether": {"current": 0, "max": 0},
            "spirit": {"current": 0, "max": 0},
        }

    def _ensure_dict(self, parent: Dict[str, Any], key: str, default: Optional[dict] = None) -> Dict[str, Any]:
        v = parent.get(key)
        if not isinstance(v, dict):
            parent[key] = {} if default is None else dict(default)
        return parent[key]

    def _coerce_int_or(self, value: Any, fallback: int) -> int:
        try:
            return int(value)
        except Exception:
            return int(fallback)

    # ─────────────────────────────────────────────────────────────
    # ensure_player_records()
    #
    # INVARIANT (BINDING):
    # - Guarantees SHAPE ONLY for characters.json
    # - Must align exactly with JSON_CONTRACTS.md
    # - MUST NOT:
    #   • migrate legacy data (beyond shape safety)
    #   • infer intent
    #   • add new canonical fields not listed in JSON_CONTRACTS.md
    #   • modify cube state semantics (cube authority is cubes.json)
    #
    # Special hard ban:
    # - NO character-level cube session keys:
    #   ch["cube"], ch["in_cube"], ch["cube_context"]
    #
    # NOTE:
    # - This function does NOT mutate lockers/cubes/vault stores.
    #   Those are Storage-owned boundaries.
    # ─────────────────────────────────────────────────────────────
    def ensure_player_records(self, user_id: str) -> None:
        s = self.storage
        uid = str(user_id)

        # ---------- Character (characters.json) ----------
        if uid not in s.characters or not isinstance(s.characters.get(uid), dict):
            s.characters[uid] = {}
        ch: Dict[str, Any] = s.characters[uid]

        # Required: id (string)
        ch["id"] = uid

        # Required: name
        if not isinstance(ch.get("name"), str) or not ch.get("name"):
            ch["name"] = f"wanderer-{uid[-4:]}"

        # Required: birthdate (YYYY-MM-DD)
        if not isinstance(ch.get("birthdate"), str) or not ch.get("birthdate"):
            ch["birthdate"] = "2000-01-01"

        # Recommended for astrology: birth_time (HH:MM or None)
        if "birth_time" not in ch:
            ch["birth_time"] = None
        else:
            bt = ch.get("birth_time")
            if bt is not None and not isinstance(bt, str):
                ch["birth_time"] = str(bt)

        # Recommended for astrology: tz_offset_minutes (int or None)
        if "tz_offset_minutes" not in ch:
            ch["tz_offset_minutes"] = None
        else:
            tz = ch.get("tz_offset_minutes")
            if tz is not None and not isinstance(tz, int):
                try:
                    ch["tz_offset_minutes"] = int(tz)
                except Exception:
                    ch["tz_offset_minutes"] = None

        # Required: current_room
        if not isinstance(ch.get("current_room"), str) or not ch.get("current_room"):
            ch["current_room"] = START_ROOM

        # Required: stats (baseline + safe clamp)
        stats = self._ensure_dict(ch, "stats")
        baseline = self._baseline_stats()
        for k, v in baseline.items():
            if not isinstance(stats.get(k), int):
                stats[k] = int(v)

        # Safe hp clamp
        if stats.get("max_hp", 0) <= 0:
            stats["max_hp"] = 20
        if not isinstance(stats.get("hp"), int):
            stats["hp"] = int(stats["max_hp"])
        if stats["hp"] > stats["max_hp"]:
            stats["hp"] = stats["max_hp"]
        if stats["hp"] < 0:
            stats["hp"] = 0

        # Required: pools (mana + spirit) — contract shape + clamp
        pools = self._ensure_dict(ch, "pools")
        baseline_pools = self._baseline_pools()

        for pool_key, base in baseline_pools.items():
            pv = pools.get(pool_key)
            if not isinstance(pv, dict):
                pv = {}
                pools[pool_key] = pv

            pmax = self._coerce_int_or(pv.get("max", base["max"]), base["max"])
            pcur = self._coerce_int_or(pv.get("current", base["current"]), base["current"])

            if pmax < 0:
                pmax = 0
            if pcur < 0:
                pcur = 0
            if pcur > pmax:
                pcur = pmax

            pv["max"] = int(pmax)
            pv["current"] = int(pcur)

        # Required: bag
        self._ensure_dict(ch, "bag")

        # Required: equipped
        self._ensure_dict(ch, "equipped")

        # Required: flags
        flags = self._ensure_dict(ch, "flags")
        if "unlocked_commands" not in flags or not isinstance(flags.get("unlocked_commands"), list):
            flags["unlocked_commands"] = []
        if "in_combat" not in flags or not isinstance(flags.get("in_combat"), bool):
            flags["in_combat"] = False

        # Router-owned: run_channel_id (allow None; coerce to str if present)
        if "run_channel_id" not in ch:
            ch["run_channel_id"] = None
        if ch["run_channel_id"] is not None and not isinstance(ch["run_channel_id"], str):
            ch["run_channel_id"] = str(ch["run_channel_id"])

        # Tolerate legacy router field without enforcing type
        if "run_seeded_channel_id" in ch and ch["run_seeded_channel_id"] is not None:
            if not isinstance(ch["run_seeded_channel_id"], (str, int)):
                ch["run_seeded_channel_id"] = str(ch["run_seeded_channel_id"])

        # Required: extra (structured non-authoritative namespace)
        extra = self._ensure_dict(ch, "extra")
        tn = self._ensure_dict(extra, "thread_nodes")
        if "active_thread_node" not in tn:
            tn["active_thread_node"] = None
        if tn["active_thread_node"] is not None and not isinstance(tn["active_thread_node"], str):
            tn["active_thread_node"] = str(tn["active_thread_node"])
        if not isinstance(tn.get("events_completed"), list):
            tn["events_completed"] = []
        self._ensure_dict(extra, "status")

        # Strip known redundant mirrors if present
        for redundant_key in ("active_thread_node", "pending_return_echo"):
            if redundant_key in ch:
                ch.pop(redundant_key, None)

        # Hard-ban character-level cube session keys if they exist (defensive)
        for banned in ("cube", "in_cube", "cube_context"):
            if banned in ch:
                ch.pop(banned, None)

        # Legacy-tolerant field (keep minimal; do not expand here)
        if "locker_tier" in ch:
            if not isinstance(ch.get("locker_tier"), int) or ch.get("locker_tier", 1) < 0:
                ch["locker_tier"] = 1

    # ---------------------------
    # Void rescue / room resolution
    # ---------------------------

    def pick_fallback_room(self) -> str:
        if START_ROOM in self.storage.rooms:
            return START_ROOM
        return next(iter(self.storage.rooms.keys()), START_ROOM)

    def resolve_room_for_user(self, user_id: str) -> str:
        uid = str(user_id)
        self.ensure_player_records(uid)
        ch = self.storage.characters[uid]

        r = ch.get("current_room")
        if isinstance(r, str) and r in self.storage.rooms:
            return r

        # Void rescue: ONLY repair invalid/missing rooms to a safe fallback.
        safe = self.pick_fallback_room()
        ch["current_room"] = safe
        self.storage.save_characters()
        return safe

    # ---------------------------
    # Shared gameplay helpers
    # ---------------------------

    def can_use_shared_portal(self, user_id: str) -> bool:
        uid = str(user_id)
        self.ensure_player_records(uid)
        ch = self.storage.characters[uid]
        bag = ch.get("bag", {})
        if not isinstance(bag, dict):
            return False
        return bag.get("Key of Commotion (Prototype)", 0) > 0
