# File: fsbot/config.py
# Project: Future Sky
# Role: Canonical config + path authority (no I/O side-effects)
# Version: 3.6.2
# Last updated: 2026-01-18 (user-reported ~4 days ago; confirm via git/ls when possible)
# Authority: AUTHORITATIVE
# Notes:
# - All canonical JSON paths MUST be defined here.
# - Env parsing must remain safe (never throw on blank/missing vars).


from __future__ import annotations

import os


VERSION = "3.6.2"


# -------------------------
# Env helpers
# -------------------------

def env_int(name: str, default: int) -> int:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    try:
        return int(raw)
    except Exception:
        return default


def env_str(name: str, default: str) -> str:
    raw = os.getenv(name)
    if raw is None:
        return default
    raw = raw.strip()
    return raw if raw else default


# -------------------------
# Canonical paths (authoritative runtime JSON)
# -------------------------

CHARACTERS_FILE = "data/characters/characters.json"
ROOMS_FILE = "data/rooms/rooms.json"
ENEMIES_FILE = "data/enemies/enemies.json"
THREAD_NODES_FILE = "data/thread_nodes/thread_nodes.json"

# Modifiers / systems
LAYERS_FILE = "data/modifiers/layers.json"
ERA_TIME_PROFILES_FILE = "data/modifiers/era_time_profiles.json"

# Items & storage
ITEMS_FILE = "data/items/items.json"
LOCKERS_FILE = "data/storage/lockers.json"
EFIISHENT_VAULT = "data/storage/efiishent_vault.json"
CUBES_FILE = "data/storage/cubes.json"

# World clock / time
WORLD_CLOCK_FILE = "data/time/world_clock.json"

# Channels (safe env override)
REALM_FEED_CHANNEL_ID = env_int("REALM_FEED_CHANNEL_ID", 1440871448653856778)
GOSSIP_CHANNEL_ID = env_int("GOSSIP_CHANNEL_ID", 1440871520862994563)

# Run-channel category (used by router.ensure_player_run_channel)
FS_PLAYERS_CATEGORY_ID = env_int("FS_PLAYERS_CATEGORY_ID", 0)

# Movement safety
START_ROOM = env_str("START_ROOM", "pod_room")

# Lavalink
LAVALINK_URI = env_str("LAVALINK_URI", "http://localhost:2333")
LAVALINK_PASSWORD = env_str("LAVALINK_PASSWORD", "youshallnotpass")
