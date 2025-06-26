import discord
from discord.ext import commands
import wavelink
import json
import os
import random
import asyncio
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# File paths
CHARACTERS_FILE = "characters.json"
ROOMS_FILE = "rooms.json"
ENEMIES_FILE = "enemies.json"
RESPAWN_TIMERS_FILE = "respawn_timers.json"
IRL_NODES_FILE = "irl_nodes.json"

# Load JSON data
def load_json(file):
    try:
        with open(file, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

characters = load_json(CHARACTERS_FILE)
rooms = load_json(ROOMS_FILE)
enemies = load_json(ENEMIES_FILE)
respawn_timers = load_json(RESPAWN_TIMERS_FILE)
irl_nodes = load_json(IRL_NODES_FILE)

# Save JSON data
def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

def save_character_data():
    save_json(CHARACTERS_FILE, characters)

def save_rooms_data():
    save_json(ROOMS_FILE, rooms)

def save_respawn_timers():
    save_json(RESPAWN_TIMERS_FILE, respawn_timers)

# Enemy respawn system
async def check_respawns():
    while True:
        now = datetime.utcnow()
        for room, enemy_data in list(respawn_timers.items()):
            for enemy, respawn_time in list(enemy_data.items()):
                if now >= datetime.fromisoformat(respawn_time):
                    if room in rooms and "enemies" in rooms[room]:
                        rooms[room]["enemies"][enemy] = enemies.get(enemy, {"hp": 20, "attack": 5, "xp": 10, "loot": ["Gold Coin"]})
                        await bot.get_channel(1348677286118817853).send(f"💀 {enemy} has respawned in {room.replace('_', ' ').title()}!")
                    del respawn_timers[room][enemy]
        save_respawn_timers()
        await asyncio.sleep(60)

# Discord bot setup
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.voice_states = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Lavalink setup
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    node = wavelink.Node(uri="http://localhost:2333", password="youshallnotpass")
    await wavelink.Pool.connect(client=bot, nodes=[node])
    bot.loop.create_task(check_respawns())

# Commands
@bot.command()
async def create_character(ctx, name: str, birthdate: str):
    user_id = str(ctx.author.id)
    if user_id in characters:
        await ctx.send("You already have a character!")
        return
    try:
        birthdate_dt = datetime.strptime(birthdate, "%Y-%m-%d").date()
    except ValueError:
        await ctx.send("Invalid birthdate format. Use YYYY-MM-DD.")
        return
    characters[user_id] = {
        "name": name,
        "birthdate": str(birthdate_dt),
        "stats": {"strength": 10, "dexterity": 10, "constitution": 10, "intelligence": 10, "wisdom": 10, "charisma": 10},
        "current_room": "neptune_lounge",
        "inventory": [],
        "xp": 0
    }
    save_character_data()
    await ctx.send(f"Character {name} created!")

@bot.command()
async def character(ctx):
    user_id = str(ctx.author.id)
    if user_id not in characters:
        await ctx.send("You don't have a character!")
        return
    char = characters[user_id]
    stats = "\n".join([f"• {k}: {v}" for k, v in char['stats'].items()])
    inventory = ", ".join(char["inventory"]) if char["inventory"] else "Empty"
    await ctx.send(f"""```Character: {char['name']}
XP: {char['xp']}
Location: {char['current_room']}
Stats:
{stats}
Inventory: {inventory}```""")

@bot.command()
async def scan_token(ctx, token: str):
    for node_id, node_data in irl_nodes.items():
        if node_data.get("token", "").lower() == token.lower():
            user_id = str(ctx.author.id)
            if user_id not in characters:
                await ctx.send("Create a character first with !create_character.")
                return
            if "Crystal Dice" not in characters[user_id]["inventory"]:
                characters[user_id]["inventory"].append("Crystal Dice")
                save_character_data()
                await ctx.send(f"✅ IRL Token recognized: {node_data['label']}\n🎁 Reward: Crystal Dice added to inventory.")
            else:
                await ctx.send(f"Token recognized, but you've already claimed this reward.")
            return
    await ctx.send("❌ Token not recognized.")

bot.run(os.getenv("DISCORD_BOT_TOKEN"))