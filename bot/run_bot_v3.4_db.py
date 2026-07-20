# run_bot.py — Future Sky Minimal DM Test (v3.4)
# ------------------------------------------------
# Purpose: prove DM routing + move to SQL (asyncpg). Nothing else.
# Commands:
#   !look            -> sends an embed via DM (fallback to channel if DMs closed)
#   !privacy [mode]  -> dm | public  (persists in Postgres)
#
# Env:
#   DISCORD_BOT_TOKEN   = "..."
#   FS_DB_DSN           = "postgresql://user:pass@localhost:5432/futuresky"
#     (or set FS_DB_HOST/FS_DB_NAME/FS_DB_USER/FS_DB_PASSWORD/FS_DB_PORT)
# ------------------------------------------------

import os
import asyncio
from typing import Optional

import asyncpg
import discord
from discord.ext import commands

VERSION = "0.1"

# ---------- Discord ----------
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# ---------- DB ----------
DB_POOL: Optional[asyncpg.Pool] = None

def _dsn_from_env() -> str:
    dsn = os.getenv("FS_DB_DSN")
    if dsn:
        return dsn
    host = os.getenv("FS_DB_HOST", "localhost")
    name = os.getenv("FS_DB_NAME", "futuresky")
    user = os.getenv("FS_DB_USER", "postgres")
    pwd  = os.getenv("FS_DB_PASSWORD", "")
    port = os.getenv("FS_DB_PORT", "5432")
    # Note: empty password is allowed for local trust auth
    return f"postgresql://{user}:{pwd}@{host}:{port}/{name}"

async def ensure_schema(pool: asyncpg.Pool):
    async with pool.acquire() as conn:
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS players (
            discord_id  BIGINT PRIMARY KEY,
            name        TEXT NOT NULL,
            privacy     TEXT NOT NULL DEFAULT 'dm',
            created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
        );
        """)

async def get_or_create_player(pool: asyncpg.Pool, discord_id: int, name: str) -> str:
    """Returns privacy mode."""
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT privacy FROM players WHERE discord_id=$1;", discord_id)
        if row:
            return row["privacy"]
        # default to dm
        await conn.execute(
            "INSERT INTO players(discord_id, name, privacy) VALUES($1,$2,'dm') ON CONFLICT DO NOTHING;",
            discord_id, name
        )
        return "dm"

async def get_privacy(pool: asyncpg.Pool, discord_id: int) -> str:
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT privacy FROM players WHERE discord_id=$1;", discord_id)
        return (row and row["privacy"]) or "dm"

async def set_privacy(pool: asyncpg.Pool, discord_id: int, name: str, mode: str):
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO players(discord_id, name, privacy)
            VALUES($1,$2,$3)
            ON CONFLICT (discord_id) DO UPDATE SET name=EXCLUDED.name, privacy=EXCLUDED.privacy;
        """, discord_id, name, mode)

# ---------- Feather privacy helpers ----------
PUBLIC_SUMMARY = True  # light echo in channel when privacy=dm

async def send_to_player(ctx: commands.Context, message: str = "", embed: discord.Embed | None = None):
    """Send to DM if player's privacy=dm, else to channel. If DMs are blocked, fall back to channel."""
    assert DB_POOL is not None
    user = ctx.author
    mode = await get_privacy(DB_POOL, user.id)
    if mode == "dm":
        try:
            if embed:
                await user.send(message or "", embed=embed)
            else:
                await user.send(message)
            return
        except discord.Forbidden:
            # DMs closed; fall back publicly
            pass
    if embed:
        await ctx.send(message or "", embed=embed)
    else:
        await ctx.send(message)

async def maybe_public_summary(ctx: commands.Context, summary: str):
    assert DB_POOL is not None
    if PUBLIC_SUMMARY and (await get_privacy(DB_POOL, ctx.author.id)) == "dm":
        await ctx.send(f"_{ctx.author.display_name}: {summary}_")

# ---------- Lifecycle ----------
@bot.event
async def on_ready():
    print(f"✅ Minimal DM Bot v{VERSION} logged in as {bot.user}")

async def _setup_db():
    global DB_POOL
    DB_POOL = await asyncpg.create_pool(_dsn_from_env(), min_size=1, max_size=5)
    await ensure_schema(DB_POOL)

# ---------- Commands ----------
@bot.command(name="help")
async def help_cmd(ctx: commands.Context):
    await send_to_player(ctx,
        "**Future Sky — Minimal DM Test**\n"
        "`!look` — sends an embed via DM\n"
        "`!privacy [dm|public]` — set where replies go"
    )

@bot.command()
async def look(ctx: commands.Context):
    """Minimal DM test: shows your privacy mode and a placeholder location."""
    assert DB_POOL is not None
    # ensure player exists with default privacy=dm
    mode = await get_or_create_player(DB_POOL, ctx.author.id, ctx.author.display_name)
    embed = discord.Embed(
        title="Neptune Lounge (placeholder)",
        description="DM routing test successful. This room text is deliberately minimal.",
    )
    embed.add_field(name="Privacy", value=mode, inline=True)
    await send_to_player(ctx, embed=embed)
    await maybe_public_summary(ctx, "looked around.")

@bot.command()
async def privacy(ctx: commands.Context, mode: Optional[str] = None):
    """Set or show your privacy mode."""
    assert DB_POOL is not None
    if mode is None:
        cur = await get_privacy(DB_POOL, ctx.author.id)
        await send_to_player(ctx, f"Your privacy mode is **{cur}**. Use `!privacy dm` or `!privacy public`.")
        return
    m = mode.strip().lower()
    if m not in ("dm", "public"):
        await send_to_player(ctx, "Choose `dm` or `public`.")
        return
    await set_privacy(DB_POOL, ctx.author.id, ctx.author.display_name, m)
    await send_to_player(ctx, f"Privacy set to **{m}**.")

# ---------- Run ----------
def main():
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        raise SystemExit("Set DISCORD_BOT_TOKEN.")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_setup_db())
    bot.run(token)

if __name__ == "__main__":
    main()
