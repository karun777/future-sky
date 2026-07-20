# db/repo.py
from typing import Optional
import json

async def get_creature_by_master(conn, master_id: int):
    return await conn.fetchrow("SELECT * FROM creatures WHERE master_id=$1", master_id)

async def get_creature_id(conn, master_id: int) -> Optional[int]:
    return await conn.fetchval("SELECT creature_id FROM creatures WHERE master_id=$1", master_id)

async def upsert_creature_stat(conn, creature_id: int, stat_name: str, delta: int):
    await conn.execute("""
      INSERT INTO creature_stats (creature_id, stat_id, value)
      SELECT $1, st.stat_id, $3
      FROM stats st WHERE lower(st.name)=lower($2)
      ON CONFLICT (creature_id, stat_id)
      DO UPDATE SET value = creature_stats.value + EXCLUDED.value
    """, creature_id, stat_name, delta)

async def upsert_mana(conn, creature_id: int, mana_type: str, delta: int):
    await conn.execute("""
      INSERT INTO creature_mana (creature_id, mana_type, value)
      VALUES ($1,$2,$3)
      ON CONFLICT (creature_id, mana_type)
      DO UPDATE SET value = creature_mana.value + EXCLUDED.value
    """, creature_id, mana_type.lower(), delta)

async def set_astro_profile(conn, creature_id: int, birthdate, profile_dict: dict):
    await conn.execute("""
      UPDATE creatures
      SET birthdate=$1, astro_profile=$2::jsonb
      WHERE creature_id=$3
    """, birthdate, json.dumps(profile_dict), creature_id)
