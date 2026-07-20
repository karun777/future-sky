# ============================================================
# FILE META — fsbot/cogs/core.py
# Canonical name: CoreCog (character creation + sheet/inventory + worldtime telemetry)
#
# Version: v3.6.7
# Last edited: 2026-02-03 (Australia/Perth)
#
# Purpose:
# - Provides canonical v0 character creation command (!create_character / !create / !cc)
# - Seeds initial stats, HP, starter inventory, and v0 mana pools
# - Ensures cube records exist via Storage helpers (no cube schema logic here)
# - Provides player-facing inventory and character sheet embeds
# - Provides equip/unequip v0 (bag <-> equipped slot map; item_id based)
# - Provides telemetry command !time (world clock + era multiplier)
# - Provides DPC-only introspection command !loaded (lists loaded commands)
#
# Spine reconciliation (v3.6.7):
# - Starter kit is item_id-based (aligns with items.json + ITEMS_CONTRACTS_v0)
# - Inventory display reconciles equipped vs bag (equipped items are not shown in bag)
#   and handles 2H weapons stored in both hands by subtracting only once (unique set)
# - Equipped is seeded as a stable slot-map (contract-shape)
# - Astrology must live at top-level `char["astro"]` for resolver/storage spine.
# - `extra.astrology` is kept as a legacy mirror only (non-authoritative).
# ============================================================

from __future__ import annotations

from datetime import datetime
from typing import Dict, Any, Optional

import discord
from discord.ext import commands

from fsbot.cogs.router import ensure_player_run_channel
from fsbot.utils import fmt_bag, fmt_equipped, STAT_KEYS

# Optional: astrology placements (we already have fsbot/astrology.py in repo)
try:
    from fsbot.astrology import compute_planet_signs

    ASTRO_OK = True
except Exception:
    ASTRO_OK = False


# -------------------------
# v0 helpers (pure python)
# -------------------------

CLASS_IDS = [
    "dreamer_technician",
    "mystic_kin",
    "rebel_architect",
    "primal_rider",
    "glyph_speaker",
    "shadow_echo",
    "astro_cartographer",
    "commotionist",
    "unwritten",
]

# +2, +2, -1 mapping from CHARACTER_CREATION_CORE_STATS_V0.md
CLASS_TENDENCIES = {
    "dreamer_technician": ("intelligence", "wisdom", "strength"),
    "mystic_kin": ("wisdom", "charisma", "intelligence"),
    "rebel_architect": ("strength", "constitution", "charisma"),
    "primal_rider": ("constitution", "dexterity", "intelligence"),
    "glyph_speaker": ("intelligence", "charisma", "constitution"),
    "shadow_echo": ("dexterity", "wisdom", "strength"),
    "astro_cartographer": ("wisdom", "intelligence", "constitution"),
    "commotionist": ("charisma", "dexterity", "wisdom"),
    "unwritten": (None, None, None),
}

SIGN_TO_ELEMENT = {
    # Fire
    "Aries": "fire",
    "Leo": "fire",
    "Sagittarius": "fire",
    # Earth
    "Taurus": "earth",
    "Virgo": "earth",
    "Capricorn": "earth",
    # Air
    "Gemini": "air",
    "Libra": "air",
    "Aquarius": "air",
    # Water
    "Cancer": "water",
    "Scorpio": "water",
    "Pisces": "water",
}

# Weighting: make Sun/Moon matter most, other personals matter, outers minimal
PLANET_WEIGHTS = {
    "sun": 2,
    "moon": 2,
    "mercury": 1,
    "venus": 1,
    "mars": 1,
    "jupiter": 1,
    "saturn": 1,
    "uranus": 0,
    "neptune": 0,
    "pluto": 0,
}


def stat_mod(score: int) -> int:
    return (int(score) - 10) // 2


def clamp_int(v: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, int(v)))


def base_stats_for_class(class_id: str) -> Dict[str, int]:
    stats = {k: 10 for k in STAT_KEYS}
    a, b, neg = CLASS_TENDENCIES.get(class_id, (None, None, None))
    if a:
        stats[a] = stats.get(a, 10) + 2
    if b:
        stats[b] = stats.get(b, 10) + 2
    if neg:
        stats[neg] = stats.get(neg, 10) - 1
    return stats


def hp_from_stats(stats: Dict[str, int]) -> int:
    base = 10
    con = int(stats.get("constitution", 10))
    mhp = base + stat_mod(con)
    # v0 guardrails
    return clamp_int(mhp, 6, 20)


def compute_mana_pools_v0(stats: Dict[str, int], astro: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    v0 mana pools (elemental):
    - earth, water, fire, air, ether
    - max derived from relevant classic stat + (small) astrology element weighting
    """
    # Base from stats: simple, stable, testable
    # earth ~ STR, water ~ DEX, fire ~ CON, air ~ CHA, ether ~ INT
    base_max = {
        "earth": 10 + stat_mod(stats.get("strength", 10)) * 2,
        "water": 10 + stat_mod(stats.get("dexterity", 10)) * 2,
        "fire": 10 + stat_mod(stats.get("constitution", 10)) * 2,
        "air": 10 + stat_mod(stats.get("charisma", 10)) * 2,
        "ether": 10 + stat_mod(stats.get("intelligence", 10)) * 2,
    }

    # Apply mild astrology bumps by element (educational + flavorful; not overpowering)
    elem_bonus = {"earth": 0, "water": 0, "fire": 0, "air": 0}
    if astro and isinstance(astro, dict):
        placements = astro.get("placements", {})
        if isinstance(placements, dict):
            for p, data in placements.items():
                if not isinstance(data, dict):
                    continue
                sign = data.get("sign")
                if not sign:
                    continue
                element = SIGN_TO_ELEMENT.get(str(sign))
                if not element:
                    continue
                w = int(PLANET_WEIGHTS.get(str(p).lower(), 0))
                if w > 0 and element in elem_bonus:
                    elem_bonus[element] += w

    # Convert element bonus → pool max nudge (texture only)
    for elem, bonus in elem_bonus.items():
        base_max[elem] = clamp_int(base_max[elem] + bonus, 6, 30)

    # Ether isn’t classical element; keep it purely stat-driven in v0.
    base_max["ether"] = clamp_int(base_max["ether"], 6, 30)

    return {
        "earth": {"current": base_max["earth"], "max": base_max["earth"]},
        "water": {"current": base_max["water"], "max": base_max["water"]},
        "fire": {"current": base_max["fire"], "max": base_max["fire"]},
        "air": {"current": base_max["air"], "max": base_max["air"]},
        "ether": {"current": base_max["ether"], "max": base_max["ether"]},
        "notes": {
            "v": "mana_pools_v0",
            "stat_basis": {
                "earth": "strength",
                "water": "dexterity",
                "fire": "constitution",
                "air": "charisma",
                "ether": "intelligence",
            },
            "astro_influence": "elements_from_planet_signs (small bonuses)",
        },
    }


def default_extra_status_v0() -> Dict[str, Any]:
    """
    Minimal, world-context status scaffolding (v0).
    Keep it stable. Don’t encode combat/turn state here.
    """
    return {
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


def default_equipped_slots_v0() -> Dict[str, Optional[str]]:
    """
    Canonical equipped slot map (v0).
    Values are item_ids or None.
    """
    return {
        "head": None,
        "neck": None,
        "chest": None,
        "back": None,
        "hands": None,
        "waist": None,
        "legs": None,
        "feet": None,
        "ring_1": None,
        "ring_2": None,
        "trinket": None,
        "main_hand": None,
        "off_hand": None,
    }


def _ensure_contract_pools_and_astro_fields(
    bot,
    user_id: str,
    *,
    mana_snapshot: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Feather C2:
    - Call ensure_player_records (shape only)
    - Ensure top-level pools keys exist (earth/water/fire/air/ether/spirit) with current/max ints
    - Ensure birth_time/tz_offset_minutes exist (nullable)
    - If mana_snapshot provided, best-effort inject into top-level pools for earth..ether
    """
    try:
        bot.state.ensure_player_records(user_id)
    except Exception:
        pass

    try:
        s = bot.storage
        c = s.characters.get(str(user_id), {})
        if not isinstance(c, dict):
            return

        c["id"] = str(user_id)
        c.setdefault("birth_time", None)
        c.setdefault("tz_offset_minutes", None)

        baseline_pools = {
            "earth": {"current": 0, "max": 0},
            "water": {"current": 0, "max": 0},
            "fire": {"current": 0, "max": 0},
            "air": {"current": 0, "max": 0},
            "ether": {"current": 0, "max": 0},
            "spirit": {"current": 0, "max": 0},
        }

        if not isinstance(c.get("pools"), dict):
            c["pools"] = {}

        pools = c["pools"]
        for k, v in baseline_pools.items():
            if not isinstance(pools.get(k), dict):
                pools[k] = dict(v)
            else:
                pools[k].setdefault("current", 0)
                pools[k].setdefault("max", 0)
                try:
                    mx = int(pools[k].get("max", 0))
                    cur = int(pools[k].get("current", 0))
                except Exception:
                    mx, cur = 0, 0
                if mx < 0:
                    mx = 0
                if cur < 0:
                    cur = 0
                if cur > mx:
                    cur = mx
                pools[k]["max"] = mx
                pools[k]["current"] = cur

        # Inject mana snapshot → pools earth..ether (best-effort)
        if isinstance(mana_snapshot, dict):
            for k in ["earth", "water", "fire", "air", "ether"]:
                d = mana_snapshot.get(k)
                if not isinstance(d, dict):
                    continue
                try:
                    mx = int(d.get("max", 0))
                    cur = int(d.get("current", mx))
                except Exception:
                    mx, cur = 0, 0
                if mx < 0:
                    mx = 0
                if cur < 0:
                    cur = 0
                if cur > mx:
                    cur = mx
                pools[k] = {"current": cur, "max": mx}

        s.characters[str(user_id)] = c
    except Exception:
        pass


class CoreCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def _is_dpc(self, ctx: commands.Context) -> bool:
        if getattr(ctx.author, "guild_permissions", None) and ctx.author.guild_permissions.administrator:
            return True
        role = discord.utils.get(getattr(ctx.author, "roles", []), name="DPC")
        return role is not None

    # -------------------------
    # Equip / Unequip helpers (v0)
    # -------------------------

    def _items_db(self) -> Dict[str, Any]:
        db = getattr(self.bot.storage, "items_db", {}) or {}
        return db if isinstance(db, dict) else {}

    def _item_name(self, item_id: str) -> str:
        it = self._items_db().get(item_id)
        if isinstance(it, dict):
            nm = it.get("name")
            if isinstance(nm, str) and nm.strip():
                return nm.strip()
        return item_id

    def _get_item_def(self, item_id: str) -> Optional[Dict[str, Any]]:
        it = self._items_db().get(item_id)
        return it if isinstance(it, dict) else None

    def _ensure_equipped_map(self, c: Dict[str, Any]) -> Dict[str, Optional[str]]:
        eq = c.get("equipped")
        if isinstance(eq, dict) and eq:
            return eq
        eq = default_equipped_slots_v0()
        c["equipped"] = eq
        return eq

    def _bag_get_qty(self, bag: Dict[str, Any], item_id: str) -> int:
        try:
            return int(bag.get(item_id, 0))
        except Exception:
            return 0

    def _bag_add(self, bag: Dict[str, Any], item_id: str, delta: int) -> None:
        cur = self._bag_get_qty(bag, item_id)
        nxt = cur + int(delta)
        if nxt <= 0:
            if item_id in bag:
                del bag[item_id]
        else:
            bag[item_id] = nxt

    def _resolve_target_slot(
        self,
        item_def: Dict[str, Any],
        equipped: Dict[str, Optional[str]],
        requested_slot: Optional[str],
    ) -> Optional[str]:
        equip_def = item_def.get("equip") if isinstance(item_def.get("equip"), dict) else {}
        allowed = equip_def.get("allowed_slots") if isinstance(equip_def.get("allowed_slots"), list) else []

        allowed = [str(s).strip().lower() for s in allowed if str(s).strip()]
        req = (requested_slot or "").strip().lower() or None

        if req:
            if req not in allowed:
                return None
            return req

        # pick first allowed empty slot
        for slot in allowed:
            if equipped.get(slot) in (None, ""):
                return slot

        # v0 policy: replace first allowed slot
        return allowed[0] if allowed else None

    def _hands_required(self, item_def: Dict[str, Any]) -> int:
        equip_def = item_def.get("equip") if isinstance(item_def.get("equip"), dict) else {}
        try:
            return max(1, int(equip_def.get("hands_required", 1)))
        except Exception:
            return 1

    def _is_equipment(self, item_def: Dict[str, Any]) -> bool:
        return str(item_def.get("type", "")).strip().lower() == "equipment"

    def _allowed_slots(self, item_def: Dict[str, Any]) -> set:
        equip_def = item_def.get("equip") if isinstance(item_def.get("equip"), dict) else {}
        allowed = equip_def.get("allowed_slots") if isinstance(equip_def.get("allowed_slots"), list) else []
        return {str(s).strip().lower() for s in allowed if str(s).strip()}

    def _enforce_stat_requirements(self, c: Dict[str, Any], item_def: Dict[str, Any]) -> Optional[str]:
        """
        Returns error string if requirements not met, else None.
        Supports:
          equip.requirements.stat_requirements: { "str": 12 } (aliases to character stats)
        """
        equip_def = item_def.get("equip") if isinstance(item_def.get("equip"), dict) else {}
        reqs = equip_def.get("requirements") if isinstance(equip_def.get("requirements"), dict) else {}
        stat_reqs = reqs.get("stat_requirements") if isinstance(reqs.get("stat_requirements"), dict) else {}

        if not stat_reqs:
            return None

        stats = c.get("stats") if isinstance(c.get("stats"), dict) else {}

        alias = {
            "str": "strength",
            "dex": "dexterity",
            "con": "constitution",
            "int": "intelligence",
            "wis": "wisdom",
            "cha": "charisma",
        }

        for k, v in stat_reqs.items():
            k2 = alias.get(str(k).strip().lower(), str(k).strip().lower())
            try:
                need = int(v)
                have = int(stats.get(k2, 0))
            except Exception:
                need, have = 9999, 0
            if have < need:
                return f"Requires {k2} {need} (you have {have})."

        return None

    # -------------------------
    # Telemetry: World Time
    # -------------------------
    @commands.command(name="time", aliases=["gtime", "worldtime"])
    async def time_cmd(self, ctx: commands.Context):
        try:
            user_id = str(ctx.author.id)
            era = self.bot.state.resolve_era_for_user(user_id)
            profile = self.bot.state.get_era_time_profile(era)
            label = profile.get("label", era)
            mult = int(profile.get("era_time_multiplier", 60))

            w = int(getattr(self.bot.state, "world_time_seconds", 0))
            days = w // 86400
            rem = w % 86400
            hours = rem // 3600
            rem = rem % 3600
            minutes = rem // 60

            mult_line = f"{mult}x"
            if mult == 60:
                mult_line += " (1 real minute ≈ 1 in-world hour)"
            elif mult == 1:
                mult_line += " (real-time)"
            else:
                mult_line += f" (1 real second = {mult} in-world seconds)"

            embed = discord.Embed(title="🕰️ World Time")
            embed.add_field(name="Era", value=f"`{era}` — {label}", inline=False)
            embed.add_field(name="Multiplier", value=mult_line, inline=False)
            embed.add_field(name="World Clock", value=f"`{w:,}s`  (~{days}d {hours}h {minutes}m)", inline=False)

            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send("⚠️ Time telemetry failed.")
            try:
                self.bot.state.log.warning(f"[TIME] failed: {type(e).__name__}: {e}")
            except Exception:
                pass

    # -------------------------
    # DPC-only: debug / introspection
    # -------------------------
    @commands.command(name="loaded", aliases=["loaded_commands"])
    async def loaded_cmd(self, ctx: commands.Context):
        if not self._is_dpc(ctx):
            await ctx.send("⛔ You don’t have permission to use `!loaded`.")
            return

        names = sorted({c.qualified_name for c in self.bot.commands})
        prefix = "✅ **Loaded commands:**\n"
        cur = prefix
        chunks = []

        for n in names:
            piece = f"`{n}`, "
            if len(cur) + len(piece) > 1900:
                chunks.append(cur.rstrip(", "))
                cur = ""
            cur += piece

        if cur.strip():
            chunks.append(cur.rstrip(", "))

        for ch in chunks:
            await ctx.send(ch)

    # -------------------------
    # Character creation (CANON v0)
    # -------------------------
    @commands.command(name="create_character", aliases=["create", "cc"])
    async def create_character(
        self,
        ctx: commands.Context,
        name: str,
        birthdate: str,
        class_id: str,
        *,
        origin_note: str = "",
    ):
        """
        v0 canonical:
        !create_character <name> <YYYY-MM-DD> <class_id> [origin_note...]
        """
        s = self.bot.storage
        user_id = str(ctx.author.id)

        class_id = class_id.strip().lower()
        if class_id not in CLASS_IDS:
            await ctx.send(
                "Invalid class_id.\n"
                "Use one of:\n" + ", ".join(f"`{c}`" for c in CLASS_IDS)
            )
            return

        # Validate birthdate
        try:
            _ = datetime.strptime(birthdate, "%Y-%m-%d").date()
        except ValueError:
            await ctx.send("Invalid birthdate. Use format `YYYY-MM-DD`.")
            return

        # Compute base stats + hp
        stats = base_stats_for_class(class_id)
        max_hp = hp_from_stats(stats)
        stats["max_hp"] = max_hp
        stats["hp"] = max_hp

        # Astrology placements (pure calculation, noon UTC assumption)
        astro_payload: Optional[Dict[str, Any]] = None
        if ASTRO_OK:
            try:
                astro_payload = compute_planet_signs(birthdate)
            except Exception:
                astro_payload = None

        # Mana pools (v0) derived from stats + mild astrology element bumps
        mana = compute_mana_pools_v0(stats, astro_payload)

        # Starter kit (v0) — item IDs (aligns with items.json contracts)
        starter_bag: Dict[str, int] = {}
        starter_ids = [
            "itm_rusty_knife",
            "itm_leather_jacket",
            # Add later when defined in items.json:
            # "itm_triton_lager",
        ]
        for iid in starter_ids:
            if iid in getattr(s, "items_db", {}):
                starter_bag[iid] = starter_bag.get(iid, 0) + 1

        # Room
        start_room = "pod_room"

        # Astro (top-level) — spine expects this key
        astro_top = astro_payload if astro_payload else {
            "version": "astrology_signs_v0",
            "error": "astrology module unavailable",
        }

        # Canonical character record (align to JSON_CONTRACTS)
        s.characters[user_id] = {
            "id": user_id,
            "name": name,
            "birthdate": birthdate,
            "birth_time": None,
            "tz_offset_minutes": None,
            "current_room": start_room,
            "stats": stats,
            "astro": astro_top,
            "pools": {
                "earth":  {"current": int(mana.get("earth", {}).get("current", 0)),  "max": int(mana.get("earth", {}).get("max", 0))},
                "water":  {"current": int(mana.get("water", {}).get("current", 0)),  "max": int(mana.get("water", {}).get("max", 0))},
                "fire":   {"current": int(mana.get("fire", {}).get("current", 0)),   "max": int(mana.get("fire", {}).get("max", 0))},
                "air":    {"current": int(mana.get("air", {}).get("current", 0)),    "max": int(mana.get("air", {}).get("max", 0))},
                "ether":  {"current": int(mana.get("ether", {}).get("current", 0)),  "max": int(mana.get("ether", {}).get("max", 0))},
                "spirit": {"current": 0, "max": 0},
            },
            "bag": starter_bag,
            "equipped": default_equipped_slots_v0(),
            "flags": {
                "unlocked_commands": [],
                "in_combat": False,
            },
            "run_channel_id": None,
            "run_seeded_channel_id": None,
            "extra": {
                "profile": {
                    "class_id": class_id,
                    "origin_note": origin_note.strip() if origin_note else "",
                },
                "thread_nodes": {
                    "active_thread_node": None,
                    "events_completed": [],
                },
                "status": default_extra_status_v0(),
                "astrology": astro_top,  # legacy mirror only
            },
        }

        _ensure_contract_pools_and_astro_fields(self.bot, user_id, mana_snapshot=mana)

        # Optional bridge stores (non-authoritative)
        try:
            if user_id not in getattr(s, "lockers", {}):
                s.lockers[user_id] = {"capacity": 20, "items": {}}
        except Exception:
            pass
        try:
            if user_id not in getattr(s, "efi_vault", {}):
                s.efi_vault[user_id] = {}
        except Exception:
            pass

        # ---- Cubes (contract v0) ----
        try:
            if hasattr(s, "ensure_personal_cube"):
                s.ensure_personal_cube(user_id)

            if hasattr(s, "ensure_efiishent_prime_cube"):
                if self._is_dpc(ctx):
                    s.ensure_efiishent_prime_cube(dpc_user_id=user_id)
                else:
                    s.ensure_efiishent_prime_cube()
        except Exception:
            pass

        # Persist
        try:
            s.save_characters()
        except Exception:
            pass
        try:
            s.save_lockers()
        except Exception:
            pass
        try:
            s.save_efi_vault()
        except Exception:
            pass
        try:
            s.save_cubes()
        except Exception:
            pass

        # Ensure run channel + persist its id
        try:
            ch = await ensure_player_run_channel(self.bot, ctx, user_id, name)
            if ch:
                s.characters[user_id]["run_channel_id"] = str(ch.id)
                try:
                    s.save_characters()
                except Exception:
                    pass
                await ctx.send(f"✅ Your run channel is ready: {ch.mention}")
        except Exception as e:
            print(f"[RUN-CHANNEL] create failed for {user_id}: {type(e).__name__}: {e}")

        await ctx.send(
            f"**Welcome, {name}.** You stumble through a blue-edged portal into the Neptune Lounge. "
            f"Neptune’s storms glow beyond the dome. Chips sizzle. Somewhere, a Cube hums."
        )

        if hasattr(self.bot, "send_to_realm_feed"):
            try:
                await self.bot.send_to_realm_feed(f"✨ {name} steps into Triton Central for the first time.")
            except Exception:
                pass

    # -------------------------
    # Inventory (presentation + reconciliation)
    # -------------------------
    @commands.command(name="inventory", aliases=["inv"])
    async def inventory(self, ctx: commands.Context):
        s = self.bot.storage
        user_id = str(ctx.author.id)

        if user_id not in s.characters:
            await ctx.send("🧬 You don’t have a character yet. Use `!create_character <name> <YYYY-MM-DD> <class_id>`.")
            return

        c = s.characters[user_id]

        equipped = c.get("equipped", {})
        if not isinstance(equipped, dict) or not equipped:
            equipped = default_equipped_slots_v0()

        # --- Equipped IDs (unique set so 2H mirror doesn't subtract twice) ---
        equipped_ids = set()
        for _, v in equipped.items():
            if isinstance(v, str) and v.strip():
                equipped_ids.add(v.strip())

        # --- Bag (copy) and reconcile equipped items (display rule) ---
        bag = c.get("bag", {}) if isinstance(c.get("bag"), dict) else {}
        bag_view = dict(bag)  # display copy
        for iid in equipped_ids:
            if iid in bag_view:
                try:
                    bag_view[iid] = max(0, int(bag_view.get(iid, 0)) - 1)
                except Exception:
                    bag_view[iid] = 0

        bag_view = {k: v for k, v in bag_view.items() if isinstance(v, int) and v > 0}

        # Pretty display: show names where possible
        items_db = getattr(s, "items_db", {}) or {}

        def _pretty_key(iid: str) -> str:
            it = items_db.get(iid)
            if isinstance(it, dict):
                nm = it.get("name")
                if isinstance(nm, str) and nm.strip():
                    return nm
            return iid

        bag_pretty = {}
        for k, v in bag_view.items():
            if not isinstance(k, str):
                continue
            try:
                qty = int(v)
            except Exception:
                continue
            if qty <= 0:
                continue
            bag_pretty[_pretty_key(k)] = qty

        equipped_pretty: Dict[str, Optional[str]] = {}
        for slot, val in equipped.items():
            if val is None:
                equipped_pretty[slot] = None
            elif isinstance(val, str):
                equipped_pretty[slot] = _pretty_key(val)
            else:
                equipped_pretty[slot] = None

        embed = discord.Embed(title=f"{c.get('name', 'Traveler')} — Inventory")
        embed.add_field(name="Equipped", value=fmt_equipped(equipped_pretty), inline=False)
        embed.add_field(name="Bag", value=fmt_bag(bag_pretty), inline=False)
        await ctx.send(embed=embed)

    # -------------------------
    # Equip / Unequip (v0)
    # -------------------------
    @commands.command(name="equip")
    async def equip_cmd(self, ctx: commands.Context, item_id: str, slot: Optional[str] = None):
        """
        Equip an item from your bag.
        Usage:
          !equip <item_id>
          !equip <item_id> <slot>
        Example:
          !equip itm_leather_jacket chest
          !equip itm_rusty_knife main_hand
        """
        s = self.bot.storage
        user_id = str(ctx.author.id)

        if user_id not in s.characters:
            await ctx.send("🧬 You don’t have a character yet. Use `!create_character ...`.")
            return

        c = s.characters[user_id]
        bag = c.get("bag") if isinstance(c.get("bag"), dict) else {}
        c["bag"] = bag
        equipped = self._ensure_equipped_map(c)

        item_id = (item_id or "").strip()
        if not item_id:
            await ctx.send("Usage: `!equip <item_id> [slot]`")
            return

        item_def = self._get_item_def(item_id)
        if not item_def:
            await ctx.send(f"⚠️ Unknown item_id: `{item_id}`")
            return

        if not self._is_equipment(item_def):
            await ctx.send(f"🚫 `{self._item_name(item_id)}` is not equipable.")
            return

        qty = self._bag_get_qty(bag, item_id)
        if qty <= 0:
            await ctx.send(f"🚫 You don’t have `{self._item_name(item_id)}` in your bag.")
            return

        req_err = self._enforce_stat_requirements(c, item_def)
        if req_err:
            await ctx.send(f"🚫 Cannot equip `{self._item_name(item_id)}` — {req_err}")
            return

        target_slot = self._resolve_target_slot(item_def, equipped, slot)
        if not target_slot:
            allowed = sorted(self._allowed_slots(item_def))
            await ctx.send(f"🚫 No valid slot. Allowed slots: {', '.join(f'`{x}`' for x in allowed) or '—'}")
            return

        # If replacing something already in that slot, unequip it first (put back into bag)
        replaced = equipped.get(target_slot)
        if isinstance(replaced, str) and replaced.strip():
            # Handle two-hand mirror: clear both if same
            if target_slot == "main_hand" and equipped.get("off_hand") == replaced:
                equipped["off_hand"] = None
            if target_slot == "off_hand" and equipped.get("main_hand") == replaced:
                equipped["main_hand"] = None

            equipped[target_slot] = None
            self._bag_add(bag, replaced, +1)

        # Two-hand enforcement
        hands = self._hands_required(item_def)
        if hands >= 2:
            if target_slot != "main_hand":
                await ctx.send("🚫 Two-handed weapons must be equipped to `main_hand`.")
                return

            off = equipped.get("off_hand")
            if isinstance(off, str) and off.strip():
                if off != item_id:
                    equipped["off_hand"] = None
                    self._bag_add(bag, off, +1)

        # Equip
        equipped[target_slot] = item_id

        # Two-hand: mirror into off_hand
        if hands >= 2:
            equipped["off_hand"] = item_id

        # Move from bag -> equipped (one unit)
        self._bag_add(bag, item_id, -1)

        # Persist
        try:
            s.characters[user_id] = c
            s.save_characters()
        except Exception:
            pass

        nm = self._item_name(item_id)
        if hands >= 2:
            await ctx.send(f"🗡️ Equipped **{nm}** (two-handed) to `main_hand` + `off_hand`.")
        else:
            await ctx.send(f"🧤 Equipped **{nm}** to `{target_slot}`.")

    @commands.command(name="unequip")
    async def unequip_cmd(self, ctx: commands.Context, slot: str):
        """
        Unequip whatever is in a slot.
        Usage:
          !unequip <slot>
        Example:
          !unequip main_hand
          !unequip chest
        """
        s = self.bot.storage
        user_id = str(ctx.author.id)

        if user_id not in s.characters:
            await ctx.send("🧬 You don’t have a character yet. Use `!create_character ...`.")
            return

        c = s.characters[user_id]
        bag = c.get("bag") if isinstance(c.get("bag"), dict) else {}
        c["bag"] = bag
        equipped = self._ensure_equipped_map(c)

        slot = (slot or "").strip().lower()
        if not slot:
            await ctx.send("Usage: `!unequip <slot>`")
            return

        if slot not in equipped:
            await ctx.send(f"⚠️ Unknown slot `{slot}`.")
            return

        item_id = equipped.get(slot)
        if not isinstance(item_id, str) or not item_id.strip():
            await ctx.send(f"— Nothing equipped in `{slot}`.")
            return

        item_id = item_id.strip()

        # Clear slot
        equipped[slot] = None

        # Two-hand mirrored: clear other slot too, return ONE item to bag
        if slot == "main_hand" and equipped.get("off_hand") == item_id:
            equipped["off_hand"] = None
        elif slot == "off_hand" and equipped.get("main_hand") == item_id:
            equipped["main_hand"] = None

        self._bag_add(bag, item_id, +1)

        # Persist
        try:
            s.characters[user_id] = c
            s.save_characters()
        except Exception:
            pass

        await ctx.send(f"🎒 Unequipped **{self._item_name(item_id)}** from `{slot}`.")

    # -------------------------
    # Character sheet
    # -------------------------
    @commands.command(name="character_sheet", aliases=["sheet"])
    async def character_sheet(self, ctx: commands.Context):
        s = self.bot.storage
        user_id = str(ctx.author.id)

        if user_id not in s.characters:
            await ctx.send("🧬 You don’t have a character yet. Use `!create_character <name> <YYYY-MM-DD> <class_id>`.")
            return

        c = s.characters[user_id]
        stats = c.get("stats", {}) if isinstance(c.get("stats"), dict) else {}

        name = c.get("name", ctx.author.display_name)
        birthdate = c.get("birthdate", "2000-01-01")
        class_id = (((c.get("extra") or {}).get("profile") or {}).get("class_id")) or "unknown"

        embed = discord.Embed(
            title=f"{name} — Sheet",
            description=f"Birthdate: {birthdate}\nClass: `{class_id}`",
        )

        embed.add_field(
            name="Location",
            value=(c.get("current_room", "?")).replace("_", " ").title(),
            inline=False,
        )
        embed.add_field(name="HP", value=f"{stats.get('hp', 0)}/{stats.get('max_hp', 0)}", inline=True)

        s_txt = "\n".join(f"{k.capitalize()}: {stats.get(k, 0)}" for k in STAT_KEYS)
        embed.add_field(name="Stats", value=s_txt or "—", inline=False)

        # Mana snapshot: prefer top-level pools (contract)
        try:
            mana_lines = []
            pools_top = c.get("pools") if isinstance(c.get("pools"), dict) else None
            if isinstance(pools_top, dict):
                for k in ["earth", "water", "fire", "air", "ether"]:
                    d = pools_top.get(k, {}) if isinstance(pools_top.get(k), dict) else {}
                    mana_lines.append(f"{k}: {d.get('current', 0)}/{d.get('max', 0)}")
            if mana_lines:
                embed.add_field(name="Mana", value="\n".join(mana_lines), inline=False)
        except Exception:
            pass

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(CoreCog(bot))
