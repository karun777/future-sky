import os, asyncio
FS_DB_ENABLED = os.getenv("FS_DB_ENABLED") == "1"

if not FS_DB_ENABLED:
    async def init_db_pool(): return None
    async def close_db_pool(): return None

    async def overlay_character(master_id: int, char: dict):
        """Read-through overlay: copy selected fields from SQL → in-memory JSON.
        JSON remains authoritative; no writes to SQL here."""
        global _pool
        if not _pool:
            await init_db_pool()
        async with _pool.acquire() as con:
            row = await con.fetchrow(
                """
                SELECT birthdate, astro_profile
                FROM creatures
                WHERE master_id = $1
                LIMIT 1
                """,
                int(master_id),
            )
        if row:
            # birthdate as YYYY-MM-DD string
            if row["birthdate"]:
                char["birthdate"] = str(row["birthdate"])

            # astro_profile may be JSONB (dict-like) or text JSON
            if row["astro_profile"] is not None:
                import json as _json
                val = row["astro_profile"]
                try:
                    if isinstance(val, str):
                        char["astro_profile"] = _json.loads(val)
                    elif isinstance(val, dict):
                        char["astro_profile"] = dict(val)
                    else:
                        # asyncpg may return a Mapping; try to cast
                        char["astro_profile"] = dict(val)
                except Exception:
                    char["astro_profile"] = {"raw": str(val)}
        return char

else:
    import asyncpg

    _pool = None

    async def init_db_pool():
        global _pool
        if _pool: return _pool
        url = os.getenv("DATABASE_URL")
        if url:
            _pool = await asyncpg.create_pool(dsn=url, min_size=1, max_size=3)
        else:
            _pool = await asyncpg.create_pool(
                user=os.getenv("PGUSER"),
                password=os.getenv("PGPASSWORD"),
                database=os.getenv("PGDATABASE", "futuresky"),
                host=os.getenv("PGHOST", "127.0.0.1"),
                port=int(os.getenv("PGPORT", "5432")),
                min_size=1, max_size=3,
            )
        return _pool

    async def close_db_pool():
        global _pool
        if _pool:
            await _pool.close()
            _pool = None

    async def overlay_character(master_id: int, char: dict):
        """Read-through overlay: copy selected fields from SQL → in-memory JSON.
        JSON remains authoritative; no writes to SQL here."""
        global _pool
        if not _pool:
            await init_db_pool()
        async with _pool.acquire() as con:
            row = await con.fetchrow(
                """
                SELECT birthdate, astro_profile
                FROM creatures
                WHERE master_id = $1
                LIMIT 1
                """,
                int(master_id),
            )
        if row:
            # birthdate as YYYY-MM-DD string
            if row["birthdate"]:
                char["birthdate"] = str(row["birthdate"])

            # astro_profile may be JSONB (dict-like) or text JSON
            if row["astro_profile"] is not None:
                import json as _json
                val = row["astro_profile"]
                try:
                    if isinstance(val, str):
                        char["astro_profile"] = _json.loads(val)
                    elif isinstance(val, dict):
                        char["astro_profile"] = dict(val)
                    else:
                        # asyncpg may return a Mapping; try to cast
                        char["astro_profile"] = dict(val)
                except Exception:
                    char["astro_profile"] = {"raw": str(val)}
        return char

