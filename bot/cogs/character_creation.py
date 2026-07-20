# cogs/character_creation.py
import asyncio
import datetime as dt
from typing import Dict, Optional, Tuple

import discord
from discord.ext import commands

# ---------- Sun sign ranges (Western tropical, inclusive) ----------
# Stored as (start_month, start_day, end_month, end_day)
SUN_SIGN_RANGES = [
    ("Capricorn",  (12, 22), ( 1, 19), "Earth"),
    ("Aquarius",   ( 1, 20), ( 2, 18), "Air"),
    ("Pisces",     ( 2, 19), ( 3, 20), "Water"),
    ("Aries",      ( 3, 21), ( 4, 19), "Fire"),
    ("Taurus",     ( 4, 20), ( 5, 20), "Earth"),
    ("Gemini",     ( 5, 21), ( 6, 20), "Air"),
    ("Cancer",     ( 6, 21), ( 7, 22), "Water"),
    ("Leo",        ( 7, 23), ( 8, 22), "Fire"),
    ("Virgo",      ( 8, 23), ( 9, 22), "Earth"),
    ("Libra",      ( 9, 23), (10, 22), "Air"),
    ("Scorpio",    (10, 23), (11, 21), "Water"),
    ("Sagittarius",(11, 22), (12, 21), "Fire"),
]

# ---------- Element → initial bonuses (light-touch; tweak from Red Book later) ----------
# Applies ONCE at creation. If DB columns exist, they’re incremented; otherwise
# we store these deltas in astro_profile["bonuses"] and you can add them at read-time.
ASTRO_BONUS_BY_ELEMENT: Dict[str, Dict[str, int]] = {
    "Fire":  {"strength": 2, "charisma": 1, "fire_mana": 5},
    "Earth": {"constitution": 2, "strength": 1, "earth_mana": 5},
    "Air":   {"dexterity": 2, "intelligence": 1, "air_mana": 5},
    "Water": {"wisdom": 2, "charisma": 1, "water_mana": 5},
    # Ether and Spirit are reserved for later layers (Ascendant, Moon, class synergy)
}

# If you already record class on the creature, you can layer a small class synergy later:
CLASS_SYNERGY: Dict[str, Dict[str, int]] = {
    # "Dreamer-Technician": {"intelligence": 1, "ether_mana": 3},
    # Fill from Red Book v7.2 when you’re ready
}

# ---------- utility ----------
def compute_sun_sign(birthdate: dt.date) -> Tuple[str, str]:
    md = (birthdate.month, birthdate.day)
    for name, start, end, element in SUN_SIGN_RANGES:
        if start <= end:
            if start <= md <= end:
                return name, element
        else:
            # wraps new year (e.g., Capricorn)
            if md >= start or md <= end:
                return name, element
    # Fallback (shouldn’t happen)
    return "Unknown", "Unknown"

def parse_birthdate(text: str) -> Optional[dt.date]:
    text = text.strip()
    fmts = [
        "%Y-%m-%d",     # 1990-03-21
        "%d/%m/%Y",     # 21/03/1990
        "%d-%m-%Y",     # 21-03-1990
        "%d %b %Y",     # 21 Mar 1990
        "%d %B %Y",     # 21 March 1990
    ]
    for f in fmts:
        try:
            return dt.datetime.strptime(text, f).date()
        except ValueError:
            pass
    return None

async def get_pool(bot) -> object:
    # Support common names: bot.db_pool, bot.pool, bot.db
    for attr in ("db_pool", "pool", "db"):
        pool = getattr(bot, attr, None)
        if pool:
            return pool
    raise RuntimeError("No database pool found on bot (expected bot.db_pool / bot.pool / bot.db)")

# columns we know how to add bonuses to if they exist
STAT_MANA_COLUMNS = [
    "strength","dexterity","constitution","intelligence","wisdom","charisma",
    "earth_mana","water_mana","fire_mana","air_mana","ether_mana","spirit_power"
]

async def columns_present(pool, table: str, candidates) -> set:
    sql = """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = $1
          AND column_name = ANY($2::text[])
    """
    async with pool.acquire() as con:
        rows = await con.fetch(sql, table, candidates)
    return {r["column_name"] for r in rows}

async def ensure_creature_row(pool, master_id: int) -> int:
    # returns creature.id (primary key). Adjust table/PK names if different.
    async with pool.acquire() as con:
        row = await con.fetchrow("SELECT id FROM creatures WHERE master_id = $1", master_id)
        if row:
            return row["id"]
        # create a minimal row; name can be updated later elsewhere
        row = await con.fetchrow(
            "INSERT INTO creatures (master_id) VALUES ($1) RETURNING id",
            master_id
        )
        return row["id"]

async def load_astro_profile(pool, creature_id: int) -> Dict:
    async with pool.acquire() as con:
        row = await con.fetchrow(
            "SELECT astro_profile FROM creatures WHERE id = $1", creature_id
        )
        data = row["astro_profile"] if row and row["astro_profile"] else {}
        if isinstance(data, dict):
            return data
        return {}

async def save_birth_and_profile(pool, creature_id: int, birthdate: dt.date, profile: Dict):
    async with pool.acquire() as con:
        await con.execute(
            "UPDATE creatures SET birthdate = $1, astro_profile = $2 WHERE id = $3",
            birthdate, profile, creature_id
        )

async def apply_astro_bonuses(pool, creature_id: int, bonuses: Dict[str,int]) -> Dict[str,int]:
    """Apply bonuses to real columns if they exist; otherwise just return them for JSON storage."""
    present = await columns_present(pool, "creatures", STAT_MANA_COLUMNS)
    sets, values = [], []
    i = 1
    for col, inc in bonuses.items():
        if col in present:
            # produce e.g. strength = COALESCE(strength, 0) + $1
            sets.append(f'{col} = COALESCE({col}, 0) + ${i}')
            values.append(inc)
            i += 1
    if sets:
        sql = f"UPDATE creatures SET {', '.join(sets)} WHERE id = ${i}"
        values.append(creature_id)
        async with pool.acquire() as con:
            await con.execute(sql, *values)
    return bonuses

def format_astro_brief(astro_profile: Dict, birthdate: Optional[dt.date]) -> str:
    sign = astro_profile.get("sun_sign", "—")
    element = astro_profile.get("element", "—")
    return f"Sun: {sign} ({element}) • Born: {birthdate.isoformat() if birthdate else '—'}"

# ---------- Cog ----------
class CharacterCreation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="create_character", help="Create your character with birthdate + Sun sign bonuses.")
    @commands.guild_only()
    async def create_character(self, ctx: commands.Context):
        pool = await get_pool(ctx.bot)
        user_id = ctx.author.id

        # ensure creature row
        creature_id = await ensure_creature_row(pool, user_id)

        # check if already applied to avoid duplicate bonuses
        existing_profile = await load_astro_profile(pool, creature_id)
        if existing_profile.get("sun_sign") and existing_profile.get("bonuses_applied"):
            return await ctx.reply("You’ve already set your birthdate and Sun sign bonuses. Use `!character_sheet` to view.")

        # prompt for birthdate
        await ctx.reply(
            "What’s your birthdate? (formats: `YYYY-MM-DD`, `DD/MM/YYYY`, `DD Mon YYYY`)\n"
            "Example: `1990-03-21` or `21/03/1990`"
        )

        def check(m: discord.Message):
            return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id

        try:
            msg = await ctx.bot.wait_for("message", timeout=120.0, check=check)
        except asyncio.TimeoutError:
            return await ctx.reply("Timed out. Run `!create_character` again when you’re ready.")

        bdate = parse_birthdate(msg.content)
        if not bdate:
            return await ctx.reply("I couldn’t parse that date. Please try again with `!create_character`.")

        # compute sign + element
        sign, element = compute_sun_sign(bdate)
        if sign == "Unknown":
            return await ctx.reply("Something went sideways computing your Sun sign. Try again.")

        bonuses = ASTRO_BONUS_BY_ELEMENT.get(element, {})
        # (hook for class synergy later)
        # class_name = await fetch_class_name_if_you_store_it(pool, creature_id)
        # bonuses = merge_bonuses(bonuses, CLASS_SYNERGY.get(class_name, {}))

        # apply to DB if columns exist
        applied = await apply_astro_bonuses(pool, creature_id, bonuses)

        # build astro_profile JSON
        profile = {
            "sun_sign": sign,
            "element": element,
            "bonuses": applied,              # the deltas we intended
            "bonuses_applied": True,         # to prevent re-application
            "applied_at": dt.datetime.now().isoformat(timespec="seconds"),
            "v": 1,                          # schema version for later extensions (Moon, Asc, etc.)
        }

        await save_birth_and_profile(pool, creature_id, bdate, profile)

        # confirmation
        pretty_bonuses = ", ".join([f"{k} +{v}" for k, v in applied.items()]) or "stored in profile"
        await ctx.reply(
            f"Locked in. Sun **{sign}** ({element}).\n"
            f"Birthdate: `{bdate.isoformat()}`\n"
            f"Applied bonuses: {pretty_bonuses}\n"
            f"Use `!character_sheet` to view your zodiac line."
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(CharacterCreation(bot))
