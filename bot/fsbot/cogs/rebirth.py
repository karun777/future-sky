from __future__ import annotations

"""
# ============================================================
# FILE META — fsbot/cogs/rebirth.py
# Canonical name: RebirthCog (reincarnate + suicide / severance)
#
# Version: v1.2.0
# Last edited: 2026-10-18 (Australia/Perth)
#
# Purpose:
# - Voluntary same-person renewal delegates to RecoveryService.
# - Preserves continuity/routing; delivers carried/worn items privately to the pod.
# - Legacy severance is disabled pending brain-death rules.
# - Older builder/archive helpers remain for compatibility, not the renewal execution path.
#
# Contract notes (STRICT):
# - Character record NEVER stores cube/in_cube/cube_context.
# - Cube items live in cubes.json only.
# - Router owns routing. This cog does NOT create channels and does NOT assume channel IDs are valid.
#   It may set routing fields to None when creating a fresh character record (bootstrap default),
#   but thereafter routing should be reconciled by RouterCog helpers.
# ============================================================
"""

from datetime import datetime
from typing import Any, Dict, Optional, Tuple

import discord
from fsbot.recovery import RecoveryService, recovering
from discord.ext import commands


# ============================================================
# Helpers: name + birthdate
# ============================================================

def _is_name_unique(storage, new_name: str, exclude_user_id: str | None = None) -> bool:
    """Case-insensitive global character name uniqueness."""
    lname = (new_name or "").strip().lower()
    chars = getattr(storage, "characters", {}) or {}
    if not isinstance(chars, dict):
        return True

    for uid, ch in chars.items():
        if exclude_user_id and str(uid) == str(exclude_user_id):
            continue
        if isinstance(ch, dict) and (ch.get("name", "") or "").strip().lower() == lname:
            return False
    return True


def _parse_name_and_birthdate(arg: str | None) -> Tuple[str, Optional[str]]:
    """
    Accept:
      "!reincarnate <new_name>"
      "!reincarnate <new_name> YYYY-MM-DD"
    Everything except a final YYYY-MM-DD token is treated as the name.
    """
    raw = (arg or "").strip()
    if not raw:
        return "", None

    parts = raw.split()
    if len(parts) >= 2:
        last = parts[-1]
        try:
            _ = datetime.strptime(last, "%Y-%m-%d").date()
            name = " ".join(parts[:-1]).strip()
            return name, last
        except Exception:
            pass

    return raw, None


def _valid_birthdate(birthdate: str | None) -> str:
    if not birthdate:
        return "2000-01-01"
    try:
        _ = datetime.strptime(birthdate, "%Y-%m-%d").date()
        return birthdate
    except Exception:
        return "2000-01-01"


# ============================================================
# Canonical v0 defaults (match Core’s naming)
# ============================================================

def _default_stats() -> Dict[str, int]:
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


def _default_extra_status_v0() -> Dict[str, Any]:
    """
    NOTE:
    - JSON_CONTRACTS v0.3.2 contracts (if present):
      - extra.status.coherence (recommended enum)
    We default coherence to "unknown" to be safe.
    """
    return {
        "coherence": "unknown",
        "hunger": 0,
        "thirst": 0,
        "fatigue": 0,
        "stress": 0,
        "shelter": "unknown",
        "temperature": "ok",
        "luck": 0,
        "intoxication": 0,
        "tripping": 0,
        "withdrawal": 0,
        "sneaking": False,
        "pending_return_echo": False,
    }


def _safe_list(x: Any) -> list:
    return x if isinstance(x, list) else []


def _safe_dict(x: Any) -> dict:
    return x if isinstance(x, dict) else {}


def _default_pools_v0_from_stats(stats: Dict[str, Any]) -> Dict[str, Dict[str, int]]:
    """
    Canonical pools skeleton:
      earth, water, fire, air, ether, spirit
    Gentle baseline derived from stats.
    """

    def _as_int(x, d=0):
        try:
            return int(x)
        except Exception:
            return d

    def _mk(v: int) -> Dict[str, int]:
        v = max(0, int(v))
        return {"current": v, "max": v}

    base = 10
    earth = max(0, base + ((_as_int(stats.get("strength", 10)) - 10) // 2) * 2)
    water = max(0, base + ((_as_int(stats.get("dexterity", 10)) - 10) // 2) * 2)
    fire = max(0, base + ((_as_int(stats.get("constitution", 10)) - 10) // 2) * 2)
    air = max(0, base + ((_as_int(stats.get("charisma", 10)) - 10) // 2) * 2)
    ether = max(0, base + ((_as_int(stats.get("intelligence", 10)) - 10) // 2) * 2)
    spirit = 0

    return {
        "earth": _mk(earth),
        "water": _mk(water),
        "fire": _mk(fire),
        "air": _mk(air),
        "ether": _mk(ether),
        "spirit": _mk(spirit),
    }


# ============================================================
# Cube helpers (Option B boundary)
# - character record never stores cube state
# - cube items live in cubes.json only
# ============================================================

def _personal_cube_id(storage, user_id: str) -> str:
    """
    Best-effort stable cube id derivation WITHOUT creating a cube.
    If Storage provides helper, use it; else fall back to legacy convention.
    """
    if hasattr(storage, "personal_cube_id"):
        try:
            cid = storage.personal_cube_id(user_id)
            return str(cid)
        except Exception:
            pass
    return f"cube_personal_{user_id}"


def _get_personal_cube_record(storage, user_id: str) -> Optional[Dict[str, Any]]:
    """
    Option B: Storage.ensure_personal_cube(user_id) returns cube_id.
    We then write into storage.cubes[cube_id].
    """
    if not hasattr(storage, "ensure_personal_cube"):
        return None

    try:
        cube_id = storage.ensure_personal_cube(user_id)  # may create if missing (OK for reincarnate)
    except Exception:
        return None

    cubes = getattr(storage, "cubes", None)
    if not isinstance(cubes, dict):
        return None

    c = cubes.get(str(cube_id))
    return c if isinstance(c, dict) else None


def _cube_items_dict(cube: Dict[str, Any]) -> Dict[str, Any]:
    """
    Contract v0 prefers cube["stash"]["items"].
    Accept legacy cube["items"] too.
    """
    stash = cube.get("stash")
    if isinstance(stash, dict):
        items = stash.get("items")
        if isinstance(items, dict):
            return items
        stash["items"] = {}
        return stash["items"]

    # If legacy exists, tolerate it.
    items = cube.get("items")
    if isinstance(items, dict):
        return items

    # Prefer stash.items for new writes.
    cube["stash"] = {"items": {}}
    return cube["stash"]["items"]


# ============================================================
# Canonical character builder (rebirth outputs)
# ============================================================

def build_canonical_character_record(
    *,
    user_id: str,
    name: str,
    birthdate: str,
    stats: Dict[str, Any],
    flags: Dict[str, Any],
    current_room: str = "pod_room",
    preserved: Optional[Dict[str, Any]] = None,
    carry_progress: bool = True,
) -> Dict[str, Any]:
    """
    FULL canonical character record consistent with Core+Storage boundary.

    Invariants:
    - NO cube/in_cube/cube_context inside character.
    - pools are top-level (6 pools).
    - extra contains profile/thread/status/astrology + legacy-safe extra.pools.mana bridge.

    Routing:
    - Router owns channel routing.
    - We seed run_channel_id/run_seeded_channel_id as None when creating the fresh record
      so the record is structurally complete on disk.
    """
    preserved = preserved or {}

    extra_prev = _safe_dict(preserved.get("extra"))
    profile_prev = _safe_dict(extra_prev.get("profile"))
    thread_prev = _safe_dict(extra_prev.get("thread_nodes"))
    status_prev = _safe_dict(extra_prev.get("status"))
    astrology_prev = extra_prev.get("astrology") if isinstance(extra_prev.get("astrology"), dict) else None

    class_id = profile_prev.get("class_id", "unknown")
    origin_note = profile_prev.get("origin_note", "")

    events_completed = _safe_list(thread_prev.get("events_completed"))
    pools = _default_pools_v0_from_stats(_safe_dict(stats))

    status = status_prev if status_prev else _default_extra_status_v0()
    if isinstance(status, dict):
        status.setdefault("coherence", "unknown")

    if astrology_prev is None:
        astrology_prev = {
            "version": "astrology_signs_v0",
            "note": "not computed on rebirth",
        }

    # Keep extra.pools.mana as a bridge (legacy: some cogs still read it)
    extra_pools_prev = _safe_dict(extra_prev.get("pools"))
    mana_prev = extra_pools_prev.get("mana") if isinstance(extra_pools_prev.get("mana"), dict) else None
    extra_pools_out = {"mana": (mana_prev or {})}

    out: Dict[str, Any] = {
        "id": str(user_id),
        "name": name,
        "birthdate": birthdate,
        "birth_time": None,
        "tz_offset_minutes": None,
        "current_room": str(current_room),
        "stats": _safe_dict(stats),
        "bag": {},
        "equipped": {},
        "flags": _safe_dict(flags),
        # Router-owned fields: seeded as None for schema completeness; Router reconciles next.
        "run_channel_id": None,
        "run_seeded_channel_id": None,
        "pools": pools,
        "extra": {
            "profile": {"class_id": class_id, "origin_note": origin_note},
            "thread_nodes": {"active_thread_node": None, "events_completed": events_completed},
            "status": status,
            "pools": extra_pools_out,   # legacy-safe bridge
            "astrology": astrology_prev,
        },
    }

    # Progress meta: contract currently tolerates these; keep only if requested.
    if carry_progress:
        out["xp"] = int(preserved.get("xp", 0) or 0)
        out["badges"] = _safe_list(preserved.get("badges"))
        out["knowledge"] = _safe_list(preserved.get("knowledge"))

    return out


# ============================================================
# Cog
# ============================================================

class RebirthCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._pending: Dict[str, Dict[str, Any]] = {}  # user_id -> state

    # ============================================================
    # !reincarnate <new_name> [YYYY-MM-DD]
    # ============================================================
    @commands.command()
    async def reincarnate(self, ctx: commands.Context, *, arg: str | None = None):
        uid = str(ctx.author.id)
        storage = self.bot.storage
        character = storage.characters.get(uid)
        if not isinstance(character, dict):
            await ctx.send("Create a character first.")
            return
        if recovering(character):
            await ctx.send("Recovery is already underway. Use `!recovery`.")
            return
        if arg == "cancel":
            self._pending.pop(uid, None)
            await ctx.send("Renewal cancelled.")
            return
        if arg != "confirm":
            name, birthdate = _parse_name_and_birthdate(arg)
            name = name or character.get("name", "Traveller")
            if not _is_name_unique(storage, name, exclude_user_id=uid):
                await ctx.send("That name is already in use.")
                return
            self._pending[uid] = {"mode": "renewal", "name": name, "birthdate": birthdate}
            await ctx.send(
                "Bodily renewal preserves your identity and progress. Carried and worn possessions "
                "will be delivered privately to your pod. Reanimation takes seven in-world days. "
                "The world continues during recovery. Use `!reincarnate confirm` or `!reincarnate cancel`.")
            return
        pending = self._pending.get(uid)
        if not pending or pending.get("mode") != "renewal":
            await ctx.send("No renewal is awaiting confirmation.")
            return
        if not _is_name_unique(storage, pending["name"], exclude_user_id=uid):
            await ctx.send("That name is now in use. Begin again.")
            return
        if character.get("flags", {}).get("in_combat"):
            await ctx.send("Leave combat before voluntary bodily renewal.")
            return
        if character.get("in_cube"):
            await ctx.send("Leave the Cube before voluntary bodily renewal.")
            return
        try:
            RecoveryService(self.bot).start(uid, name=pending["name"], birthdate=pending["birthdate"])
        except Exception:
            await ctx.send("Renewal could not be saved safely. Nothing has been transferred; please retry.")
            return
        self._pending.pop(uid, None)
        await ctx.send("Reanimation has begun. Your possessions are secured in your pod. Use `!recovery`.")

    # ============================================================
    # !suicide <new_name> [YYYY-MM-DD]
    # ============================================================
    @commands.command()
    async def suicide(self, ctx: commands.Context, *, arg: str | None = None):
        await ctx.send("Severance is unavailable while brain-death continuity rules are being authored. No character or possessions have been erased.")

    # ============================================================
    # Helpers
    # ============================================================
    async def _archive_run_channel(self, ctx, char: Dict[str, Any], final_text: str):
        """
        Best-effort channel archive:
        - Rename to archive-<name>-<stamp>
        - Lock author to read-only
        - Post final_text
        This does NOT create channels.
        This does NOT assume it can safely mutate routing fields (Router owns).
        """
        run_id = char.get("run_channel_id")
        if not run_id or not ctx.guild:
            return

        try:
            ch = ctx.guild.get_channel(int(run_id))
        except Exception:
            ch = None

        if not isinstance(ch, discord.TextChannel):
            return

        stamp = datetime.now().strftime("%Y%m%d-%H%M")
        archive_name = f"archive-{ch.name}-{stamp}"[:90]

        try:
            overwrites = ch.overwrites
            overwrites[ctx.author] = discord.PermissionOverwrite(
                view_channel=True,
                read_message_history=True,
                send_messages=False,
                add_reactions=False,
            )
            await ch.edit(
                name=archive_name,
                overwrites=overwrites,
                reason="Future Sky: archive run",
            )
        except Exception:
            pass

        try:
            await ch.send(final_text)
        except Exception:
            pass


async def setup(bot):
    await bot.add_cog(RebirthCog(bot))
