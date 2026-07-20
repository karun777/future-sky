import os, json, asyncio, asyncpg, sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env from bot directory
load_dotenv("/home/karun777/futuresky/bot/.env")

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_USER = os.getenv("DB_USER", "futuresky_user")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME", "futuresky")

# Default JSON file path (override with sys.argv[1] if given)
JSON_PATH = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/home/karun777/futuresky/data/rooms/rooms.json")

UPSERT_ROOM_SQL = """
INSERT INTO rooms (slug, name, description, media, tags, ambient_events)
VALUES ($1, $2, $3, $4::jsonb, $5::jsonb, $6::jsonb)
ON CONFLICT (slug) DO UPDATE
SET name = EXCLUDED.name,
    description = EXCLUDED.description,
    media = COALESCE(EXCLUDED.media, rooms.media),
    tags = COALESCE(EXCLUDED.tags, rooms.tags),
    ambient_events = COALESCE(EXCLUDED.ambient_events, rooms.ambient_events)
RETURNING room_id;
"""

ADD_COLUMNS_SQL = """
DO $$ BEGIN
  BEGIN ALTER TABLE rooms ADD COLUMN slug text UNIQUE; EXCEPTION WHEN duplicate_column THEN END;
  BEGIN ALTER TABLE rooms ADD COLUMN media jsonb;       EXCEPTION WHEN duplicate_column THEN END;
  BEGIN ALTER TABLE rooms ADD COLUMN tags jsonb;        EXCEPTION WHEN duplicate_column THEN END;
  BEGIN ALTER TABLE rooms ADD COLUMN ambient_events jsonb; EXCEPTION WHEN duplicate_column THEN END;
  BEGIN ALTER TABLE rooms ADD COLUMN exits jsonb;       EXCEPTION WHEN duplicate_column THEN END;
END $$;
"""

FETCH_ROOM_IDS_BY_SLUG = "SELECT slug, room_id FROM rooms WHERE slug = ANY($1);"
UPDATE_EXITS_SQL = "UPDATE rooms SET exits = $2::jsonb WHERE slug = $1;"

# Get-or-create item without needing a unique index on name
async def get_or_create_item(conn, item_name: str) -> int:
    iid = await conn.fetchval(
        "SELECT item_id FROM items WHERE lower(name)=lower($1) LIMIT 1;",
        item_name
    )
    if iid:
        return iid
    return await conn.fetchval(
        """
        INSERT INTO items (name, item_type, stackable, max_stack, weight_grams, effects, requirements)
        VALUES ($1, 'misc', true, 99, 0, '{}'::jsonb, '{}'::jsonb)
        RETURNING item_id;
        """,
        item_name,
    )

async def main():
    if not DB_PASS:
        print("ERROR: DB_PASS not found in .env file.")
        sys.exit(1)
    if not JSON_PATH.exists():
        print(f"ERROR: JSON file not found: {JSON_PATH}")
        sys.exit(1)

    data = json.loads(JSON_PATH.read_text())

    pool = await asyncpg.create_pool(
        user=DB_USER, password=DB_PASS, database=DB_NAME, host=DB_HOST, port=DB_PORT
    )

    async with pool.acquire() as conn:
        await conn.execute(ADD_COLUMNS_SQL)

        # === CLEAN REIMPORT ===
        # Delete child tables first to satisfy FKs, then parent rooms
        await conn.execute("DELETE FROM room_items;")
        await conn.execute("DELETE FROM room_ambient_events;")
        await conn.execute("DELETE FROM room_state_overlays;")
        await conn.execute("DELETE FROM room_npcs;")
        await conn.execute("DELETE FROM rooms;")

        slug_to_roomid = {}
        raw_exits = {}
        raw_items = {}

        # Pass 1: insert/update rooms (without exits yet)
        for slug, obj in data.items():
            title = obj.get("title") or obj.get("name") or slug.replace("_", " ").title()
            description = obj.get("description") or ""

            media = {}
            if obj.get("image"):       media["image"] = obj["image"]
            if obj.get("soundcloud"):  media["soundcloud"] = obj["soundcloud"]
            if obj.get("youtube"):     media["youtube"] = obj["youtube"]

            tags = obj.get("tags") or []
            ambient = obj.get("ambient_events") or []

            rid = await conn.fetchval(
                UPSERT_ROOM_SQL,
                slug, title, description, json.dumps(media), json.dumps(tags), json.dumps(ambient)
            )
            slug_to_roomid[slug] = rid

            exits = obj.get("exits") or {}
            if isinstance(exits, dict):
                raw_exits[slug] = exits

            # aggregate items by name (qty)
            room_item_counts = {}
            for it in (obj.get("items") or []):
                room_item_counts[it] = room_item_counts.get(it, 0) + 1
            if room_item_counts:
                raw_items[slug] = room_item_counts

        # Refresh any pre-existing slugs → ids
        rows = await conn.fetch(FETCH_ROOM_IDS_BY_SLUG, list(data.keys()))
        for r in rows:
            slug_to_roomid[r["slug"]] = r["room_id"]

        # Pass 2: convert exits {dir: slug} → {dir: room_id}
        for slug, exits in raw_exits.items():
            numeric = {}
            for direction, target_slug in exits.items():
                target_id = slug_to_roomid.get(target_slug)
                if target_id:
                    numeric[direction] = target_id
            await conn.execute(UPDATE_EXITS_SQL, slug, json.dumps(numeric))

        # Pass 3: seed items into room_items (create items if missing)
        for slug, items_map in raw_items.items():
            room_id = slug_to_roomid.get(slug)
            if not room_id:
                continue
            for item_name, qty in items_map.items():
                item_id = await get_or_create_item(conn, item_name)
                await conn.execute(
                    """
                    INSERT INTO room_items (room_id, item_id, qty)
                    VALUES ($1, $2, $3)
                    ON CONFLICT (room_id, item_id) DO UPDATE
                    SET qty = room_items.qty + EXCLUDED.qty;
                    """,
                    room_id, item_id, qty,
                )

    await pool.close()
    print(f"Imported {len(data)} rooms from {JSON_PATH}")

if __name__ == "__main__":
    asyncio.run(main())
