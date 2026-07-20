# fsbot/storage.py
#
# Storage v3.4 (rooms instances + template merge + resolver bridge)
#
# Key guarantees (aligned with your current rooms.json):
# - rooms.json may store enemy instances with full overrides (hp/attack/xp/loot/etc).
# - resolve_room_enemies(room_id) returns template+instance merged (instance wins).
# - Combat should only mutate instance["hp"] and should never clobber overrides.
#
# Optional world reset:
# - FS_RESET_ROOMS_ON_BOOT=1 will copy rooms_base.json -> rooms.json at startup.
# - If rooms_base.json missing but rooms.json exists, it will create the base copy once.
#
# Notes:
# - This module intentionally avoids importing discord or bot state.
# - All JSON writes are atomic (tmp + replace).

from __future__ import annotations

import os
import json
import shutil
from typing import Any, Dict, List, Optional

from fsbot.config import (
    CHARACTERS_FILE,
    ROOMS_FILE,
    ENEMIES_FILE,
    ITEMS_FILE,
    LOCKERS_FILE,
    EFIISHENT_VAULT,
    CUBES_FILE,
    LAYERS_FILE,
)

# Resolver (Phase 1: character effective view for combat)
# Note: fsbot/resolver.py must exist.
from fsbot.resolver import resolve_effective_character

# Baseline rooms template (immutable). Optional:
# If FS_RESET_ROOMS_ON_BOOT=1, we reset rooms.json from this on startup.
ROOMS_BASE_FILE = "data/rooms/rooms_base.json"

ITEMS_FALLBACK: Dict[str, Dict[str, Any]] = {
    "Rusty Dagger": {
        "type": "weapon",
        "slot": "main_hand",
        "damage": [2, 5],
        "scaling": "DEX",
        "weight": 1,
        "rarity": "common",
    },
    "Pilot Jacket": {
        "type": "armor",
        "slot": "body",
        "defense": 2,
        "resists": {"cold": 1},
        "rarity": "common",
    },
    "Triton Lager": {"type": "consumable", "heal": 4, "stackable": True, "rarity": "common"},
    "Key of Commotion (Prototype)": {
        "type": "artifact",
        "effects": ["unlock_shared_portal"],
        "consumable": False,
        "rarity": "quest",
    },
}


def save_json(path: str, data: Any) -> None:
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp, path)


def load_json(path: str, default: Any) -> Any:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        try:
            save_json(path, default)
        except Exception:
            pass
        return default
    except json.JSONDecodeError:
        return default
    except Exception:
        return default


def _ensure_dirs() -> None:
    for path in [
        "data",
        "data/characters",
        "data/rooms",
        "data/enemies",
        "data/items",
        "data/storage",
        "data/modifiers",
    ]:
        os.makedirs(path, exist_ok=True)

    # Ensure layers file exists (empty list) to avoid FileNotFound churn
    try:
        if not os.path.exists(LAYERS_FILE):
            save_json(LAYERS_FILE, [])
    except Exception:
        pass


def _reset_rooms_from_base() -> None:
    """
    Optional world reset (enemy respawn v0):
    - If rooms_base.json exists, overwrite rooms.json from it on startup.
    - If base does not exist but rooms.json does, create base from rooms.json.
    Controlled by env var FS_RESET_ROOMS_ON_BOOT=1.
    """
    try:
        if not os.path.exists(ROOMS_BASE_FILE) and os.path.exists(ROOMS_FILE):
            shutil.copyfile(ROOMS_FILE, ROOMS_BASE_FILE)

        if os.path.exists(ROOMS_BASE_FILE):
            shutil.copyfile(ROOMS_BASE_FILE, ROOMS_FILE)
    except Exception:
        pass


def _safe_layers_list(data: Any) -> List[Dict[str, Any]]:
    """Ensure layers are a list[dict]. Filters out non-dicts."""
    if not isinstance(data, list):
        return []
    out: List[Dict[str, Any]] = []
    for x in data:
        if isinstance(x, dict):
            out.append(x)
    return out


def _deepcopy_jsonable(x: Any) -> Any:
    """Cheap deep copy for JSON-y data structures."""
    try:
        return json.loads(json.dumps(x))
    except Exception:
        return x


def build_character_spine_for_combat(char: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    """
    Minimal, safe spine extractor for resolver input.
    DOES NOT mutate stored character. Returns a new dict.

    Back-compat rules:
    - stats defaults to 10s (str/dex/con/int/wis/cha) using legacy or long names when present.
    - pools.hp created from pools.hp if present, else from stats.hp/max_hp, else from hp/hp_max/health.
    """
    name = char.get("name") or char.get("character_name") or "Unknown"

    # stats: accept either short keys (str/dex/...) or long keys (strength/dexterity/...)
    stats = char.get("stats")
    if not isinstance(stats, dict):
        stats = {}

    def _get_stat(short: str, long: str, default: int = 10) -> int:
        try:
            if short in stats:
                return int(stats.get(short, default))
            return int(stats.get(long, default))
        except Exception:
            return default

    stats_out: Dict[str, int] = {
        "str": _get_stat("str", "strength", 10),
        "dex": _get_stat("dex", "dexterity", 10),
        "con": _get_stat("con", "constitution", 10),
        "int": _get_stat("int", "intelligence", 10),
        "wis": _get_stat("wis", "wisdom", 10),
        "cha": _get_stat("cha", "charisma", 10),
    }

    # pools
    pools = char.get("pools")
    if not isinstance(pools, dict):
        pools = {}
    pools_out: Dict[str, Any] = _deepcopy_jsonable(pools) if pools else {}

    # Determine hp/hp_max:
    # Priority:
    # 1) pools.hp.current/max
    # 2) stats.hp/max_hp
    # 3) legacy top-level hp/hp_max/health/health_max
    hp = None
    hp_max = None

    if isinstance(pools_out.get("hp"), dict):
        hp = pools_out["hp"].get("current")
        hp_max = pools_out["hp"].get("max")

    if hp is None:
        hp = stats.get("hp", char.get("hp", char.get("health", 20)))
    if hp_max is None:
        hp_max = stats.get("max_hp", char.get("hp_max", char.get("health_max", hp)))

    try:
        hp = int(hp)
    except Exception:
        hp = 20
    try:
        hp_max = int(hp_max)
    except Exception:
        hp_max = max(1, hp)

    if hp_max < 1:
        hp_max = 1
    if hp < 0:
        hp = 0
    if hp > hp_max:
        hp = hp_max

    pools_out.setdefault("hp", {"current": hp, "max": hp_max})

    # minimal combat container (resolver can mod combat.*)
    combat = char.get("combat")
    if not isinstance(combat, dict):
        combat = {}
    combat_out = _deepcopy_jsonable(combat) if combat else {}

    # Optional namespaces (read-only)
    profile = char.get("profile")
    if not isinstance(profile, dict):
        profile = {}
    progression = char.get("progression")
    if not isinstance(progression, dict):
        progression = {}
    astro = char.get("astro")
    if not isinstance(astro, dict):
        astro = {}
    vitals = char.get("vitals")
    if not isinstance(vitals, dict):
        vitals = {}

    return {
        "id": str(user_id),
        "name": name,
        "stats": stats_out,
        "pools": pools_out,
        "combat": combat_out,
        "vitals": _deepcopy_jsonable(vitals) if vitals else {},
        "profile": _deepcopy_jsonable(profile) if profile else {},
        "progression": _deepcopy_jsonable(progression) if progression else {},
        "astro": _deepcopy_jsonable(astro) if astro else {},
    }


class Storage:
    """Centralized persistence layer (JSON-authoritative)."""

    def __init__(self):
        _ensure_dirs()

        # Optional: reset world state on restart (rooms.json) from immutable baseline.
        if os.getenv("FS_RESET_ROOMS_ON_BOOT", "0") == "1":
            _reset_rooms_from_base()

        self.characters: Dict[str, Any] = load_json(CHARACTERS_FILE, {})
        self.rooms: Dict[str, Any] = load_json(ROOMS_FILE, {})
        self.enemies_db: Dict[str, Any] = load_json(ENEMIES_FILE, {})

        self.items_db: Dict[str, Any] = load_json(ITEMS_FILE, ITEMS_FALLBACK)
        self.lockers: Dict[str, Any] = load_json(LOCKERS_FILE, {})
        self.efi_vault: Dict[str, Any] = load_json(EFIISHENT_VAULT, {})
        self.cubes: Dict[str, Any] = load_json(CUBES_FILE, {})

        # ✅ Canonical layers load (single source of truth)
        self.layers: List[Dict[str, Any]] = _safe_layers_list(load_json(LAYERS_FILE, []))

    # Save helpers
    def save_characters(self) -> None:
        save_json(CHARACTERS_FILE, self.characters)

    def save_rooms(self) -> None:
        save_json(ROOMS_FILE, self.rooms)

    def save_lockers(self) -> None:
        save_json(LOCKERS_FILE, self.lockers)

    def save_efi_vault(self) -> None:
        save_json(EFIISHENT_VAULT, self.efi_vault)

    def save_cubes(self) -> None:
        save_json(CUBES_FILE, self.cubes)

    def save_items(self) -> None:
        save_json(ITEMS_FILE, self.items_db)

    def save_layers(self) -> None:
        save_json(LAYERS_FILE, self.layers)

    # -------------------------
    # Enemy templates + instances (rooms.json instances, enemies.json templates)
    # -------------------------
    def get_enemy_template(self, enemy_type: str) -> Dict[str, Any]:
        """
        Returns the canonical enemy template from enemies.json (self.enemies_db).
        Always returns a dict (possibly empty) and never mutates the DB.
        """
        if not enemy_type:
            return {}
        t = self.enemies_db.get(enemy_type, {})
        return t if isinstance(t, dict) else {}

    def _slugify(self, s: str) -> str:
        """
        Best-effort slugify for stable instance ids:
        'Sewer Cyber-Rat' -> 'sewer_cyber_rat'
        """
        s = (s or "").strip().lower()
        out: List[str] = []
        prev_underscore = False
        for ch in s:
            if ch.isalnum():
                out.append(ch)
                prev_underscore = False
            else:
                if not prev_underscore:
                    out.append("_")
                    prev_underscore = True
        slug = "".join(out).strip("_")
        return slug or "enemy"

    def normalize_room_enemies(self, room_id: str) -> Dict[str, Dict[str, Any]]:
        """
        Normalizes enemies in a room into instance-id format.

        Preferred (new) format:
          enemies: { "rat#1": {"type":"Sewer Cyber-Rat","hp":12, ...overrides }, ... }

        Legacy (supported) format:
          enemies: { "Sewer Cyber-Rat": {"hp":12,"attack":4,...}, ... }

        Returns normalized dict. Does NOT auto-save.
        """
        room_id = str(room_id)
        room = self.rooms.get(room_id, {})
        if not isinstance(room, dict):
            return {}

        enemies = room.get("enemies", {})
        if not isinstance(enemies, dict) or not enemies:
            return {}

        normalized: Dict[str, Dict[str, Any]] = {}

        for key, data in enemies.items():
            if not isinstance(data, dict):
                continue

            # New format: instance-id -> dict with "type"
            if "type" in data and isinstance(data.get("type"), str):
                inst_id = str(key)
                normalized[inst_id] = _deepcopy_jsonable(data)
                continue

            # Legacy format: key is the enemy type/name
            enemy_type = str(key)
            inst_id = f"{self._slugify(enemy_type)}#1"

            # Preserve legacy inline stats as instance overrides (so nothing breaks),
            # but also set type so templates can be used.
            inst = _deepcopy_jsonable(data)
            inst["type"] = enemy_type
            normalized[inst_id] = inst

        return normalized

    def resolve_room_enemies(self, room_id: str) -> Dict[str, Dict[str, Any]]:
        """
        Returns effective enemies for combat:
        template (from enemies.json) merged with instance overrides (from rooms.json).

        Precedence: instance overrides win (e.g., current hp / attack / loot).
        Output shape:
          { "rat#1": { "type":"Sewer Cyber-Rat", "hp":9, "attack":4, ... }, ... }
        """
        enemies_norm = self.normalize_room_enemies(room_id)
        out: Dict[str, Dict[str, Any]] = {}

        for inst_id, inst in enemies_norm.items():
            enemy_type = inst.get("type", "")
            template = self.get_enemy_template(str(enemy_type))

            effective: Dict[str, Any] = {}
            if isinstance(template, dict) and template:
                effective.update(_deepcopy_jsonable(template))

            # Ensure type is always present, then apply instance overrides
            effective["type"] = str(enemy_type)
            effective.update(_deepcopy_jsonable(inst))

            # Ensure hp exists (template hp if instance missing)
            if "hp" not in effective:
                if isinstance(template, dict) and "hp" in template:
                    effective["hp"] = template.get("hp", 1)
                else:
                    effective["hp"] = 1

            out[str(inst_id)] = effective

        return out

    def get_room_enemy_instances(self, room_id: str) -> Dict[str, Dict[str, Any]]:
        """
        Returns the raw enemies dict stored in rooms.json for this room (normalized in-memory).
        Does NOT save. Use persist_room_enemy_hp/remove_room_enemy_instance/etc to mutate safely.
        """
        return self.normalize_room_enemies(room_id)

    def save_room_enemies_normalized(self, room_id: str) -> None:
        """
        Converts the room's enemies into instance-id format and persists to rooms.json.
        Safe migration helper. Call once per room (or for all rooms) to migrate.
        """
        room_id = str(room_id)
        room = self.rooms.get(room_id, {})
        if not isinstance(room, dict):
            return

        room["enemies"] = self.normalize_room_enemies(room_id)
        self.rooms[room_id] = room
        self.save_rooms()

    def migrate_all_rooms_enemies_to_instances(self) -> None:
        """
        One-shot migration: normalizes enemies for every room and saves rooms.json.
        Safe because legacy inline stats are preserved as instance overrides.
        """
        changed = False
        for room_id, room in list(self.rooms.items()):
            if not isinstance(room, dict):
                continue
            enemies = room.get("enemies", {})
            if not isinstance(enemies, dict) or not enemies:
                continue

            needs = False
            for _, data in enemies.items():
                if isinstance(data, dict) and "type" in data and isinstance(data.get("type"), str):
                    continue
                needs = True
                break

            if needs:
                room["enemies"] = self.normalize_room_enemies(room_id)
                self.rooms[str(room_id)] = room
                changed = True

        if changed:
            self.save_rooms()

    def persist_room_enemy_hp(self, room_id: str, instance_id: str, new_hp: int, *, enemy_type_hint: Optional[str] = None) -> None:
        """
        Persist ONLY hp to the room instance record, preserving any existing overrides.

        If the instance is missing, we create a minimal record:
          {"type": enemy_type_hint or instance_id, "hp": new_hp}

        This is the safe persistence primitive combat should use.
        """
        room_id = str(room_id)
        instance_id = str(instance_id)

        room = self.rooms.get(room_id, {})
        if not isinstance(room, dict):
            return

        enemies = room.get("enemies", {})
        if not isinstance(enemies, dict):
            enemies = {}

        inst = enemies.get(instance_id)
        if not isinstance(inst, dict):
            inst = {"type": str(enemy_type_hint) if enemy_type_hint else instance_id}

        inst["hp"] = int(new_hp)
        enemies[instance_id] = inst
        room["enemies"] = enemies
        self.rooms[room_id] = room

    def remove_room_enemy_instance(self, room_id: str, instance_id: str) -> None:
        """
        Remove an enemy instance from rooms.json (defeat).
        """
        room_id = str(room_id)
        instance_id = str(instance_id)

        room = self.rooms.get(room_id, {})
        if not isinstance(room, dict):
            return

        enemies = room.get("enemies", {})
        if not isinstance(enemies, dict):
            return

        enemies.pop(instance_id, None)
        room["enemies"] = enemies
        self.rooms[room_id] = room

    # -------------------------
    # Resolver bridge (Phase 1)
    # -------------------------
    def resolve_for_combat(self, user_id: str, *, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Builds a minimal combat spine from the authoritative character record,
        applies modifier layers via resolver, and returns the resolver result.

        NOTE:
        - Read-only: does not mutate stored character JSON.
        - Persistence remains the responsibility of existing combat logic.
        """
        uid = str(user_id)
        char = self.characters.get(uid, {})
        if not isinstance(char, dict):
            char = {}

        spine = build_character_spine_for_combat(char, uid)

        layers = self.layers if isinstance(self.layers, list) else []
        ctx = context if isinstance(context, dict) else {}

        return resolve_effective_character(spine=spine, context=ctx, layers=layers)
