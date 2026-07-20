# fsbot/cogs/help.py
from __future__ import annotations

from discord.ext import commands


CATALOG = {
    # Core (always visible)
    "look": {"tier": 0, "category": "core", "desc": "Describe your current location."},
    "go": {"tier": 0, "category": "core", "desc": "Move to a direction. Example: `!go north`."},
    "character_sheet": {"tier": 0, "category": "core", "desc": "Show your character summary."},
    "inventory": {"tier": 0, "category": "items", "desc": "Show what you’re carrying."},

    # Combat (core-visible)
    "combat": {"tier": 0, "category": "combat", "desc": "Opt in/out of combat. `!combat on|off|status`."},
    "draw": {"tier": 0, "category": "combat", "desc": "Draw a weapon (flavour). `!draw` or `!draw <name>`."},
    "status": {"tier": 0, "category": "combat", "desc": "Combat snapshot for the room."},
    "attack": {"tier": 0, "category": "combat", "desc": "Attack a foe (turn-based). Example: `!attack cyber-rat`."},

    # Discovery (unlocked via thread nodes)
    "sneak": {"tier": 1, "category": "movement", "desc": "Move quietly (later: skill check)."},
    "absorb": {"tier": 1, "category": "presence", "desc": "Hold impact without escalating (v0 narrative effect)."},
    "descalate": {"tier": 1, "category": "presence", "desc": "De-escalate social pressure (v0 narrative effect)."},
    "catalyse": {"tier": 1, "category": "presence", "desc": "Commit decisively; act before the moment chooses (v0)."},
    "say": {"tier": 0, "category": "social", "desc": "Speak into the room. Example: `!say hello`."},

    # Social / flavour (always available)
    "emote": {"tier": 0, "category": "social", "desc": "Express an action. Example: `!emote nods`."},
}

ALWAYS_LIST = {
    "look", "go", "character_sheet", "inventory",
    "combat", "draw", "status", "attack",
    "say", "emote",
}

DISCOVERY_LIST = {
    "sneak", "absorb", "descalate", "catalyse",
}

HINTS_BY_TIER = {
    1: "You feel social pressure has *techniques*… and you don’t know them all yet.",
    2: "Stronger verbs exist. Some will cost you something to learn.",
    3: "The Cube is listening. Not all doors are visible.",
}


def _get_char(bot, user_id: str) -> dict:
    s = bot.storage
    bot.state.ensure_player_records(user_id)
    return s.characters[user_id]


def _get_unlocked_commands(char: dict) -> set[str]:
    flags = char.get("flags") or {}
    unlocked = flags.get("unlocked_commands") or []
    return {str(c).strip().lower() for c in unlocked if str(c).strip()}


class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help_cmd(self, ctx: commands.Context):
        user_id = str(ctx.author.id)
        s = self.bot.storage

        if user_id not in s.characters:
            await ctx.send(
                "🧭 **Future Sky — Help**\n\n"
                "Start here:\n"
                "- `!look`\n"
                "- `!go <direction>` (e.g. `!go north`)\n\n"
                "Once you have a character, your responses will route to your run channel.\n"
                "Ask in **#general** if you get stuck."
            )
            return

        await ctx.send(
            "🧭 **Future Sky — Help**\n\n"
            "Try this loop:\n"
            "1) `!look`\n"
            "2) `!go <direction>`\n\n"
            "Combat basics:\n"
            "- `!combat on` (opt in)\n"
            "- `!draw`\n"
            "- `!attack <enemy>`\n\n"
            "Want the deeper toolbox?\n"
            "- `!commands` (your discovered verbs)\n"
        )

    @commands.command(name="commands", aliases=["command"])
    async def commands_cmd(self, ctx: commands.Context):
        user_id = str(ctx.author.id)
        s = self.bot.storage

        if user_id not in s.characters:
            await ctx.send("You don’t have a character yet. Use `!help` to begin.")
            return

        char = _get_char(self.bot, user_id)
        unlocked = _get_unlocked_commands(char)

        available_now = sorted({c for c in ALWAYS_LIST if c in CATALOG})
        discovered = sorted({c for c in unlocked if c in CATALOG and c in DISCOVERY_LIST})

        max_tier_unlocked = 0
        for c in discovered:
            max_tier_unlocked = max(max_tier_unlocked, int(CATALOG[c].get("tier", 0)))

        hint_lines = []
        if not discovered:
            hint_lines.append("🔒 **More commands exist.** Some are learned through encounters and choices.")
            hint_lines.append("🧩 Pay attention to thread nodes, NPCs, and strange moments.")

        next_tier = max_tier_unlocked + 1
        if next_tier in HINTS_BY_TIER:
            hint_lines.append(f"🫧 *{HINTS_BY_TIER[next_tier]}*")

        def fmt(cmd: str) -> str:
            meta = CATALOG.get(cmd, {})
            desc = meta.get("desc", "")
            return f"- `!{cmd}` — {desc}"

        out = []
        out.append("📜 **Your Commands**\n")

        out.append("✅ **Available now**")
        out.extend(fmt(c) for c in available_now)

        if discovered:
            out.append("\n🗝️ **Discovered**")
            out.extend(fmt(c) for c in discovered)

        if hint_lines:
            out.append("\n" + "\n".join(hint_lines))

        await ctx.send("\n".join(out))

    @commands.command(name="unlock_command")
    async def unlock_command_cmd(self, ctx: commands.Context, *, cmd_name: str):
        if not (getattr(ctx.author, "guild_permissions", None) and ctx.author.guild_permissions.administrator):
            await ctx.send("That function is not available to you.")
            return

        user_id = str(ctx.author.id)
        s = self.bot.storage
        if user_id not in s.characters:
            await ctx.send("No character found.")
            return

        cmd = cmd_name.strip().lower().lstrip("!")
        if cmd not in CATALOG:
            await ctx.send(f"Unknown command key: `{cmd}`")
            return

        if hasattr(ctx.bot, "unlock_command"):
            changed = await ctx.bot.unlock_command(user_id, cmd)  # type: ignore[attr-defined]
            char = _get_char(self.bot, user_id)
            if changed:
                await ctx.send(f"🗝️ Unlocked `!{cmd}` for **{char.get('name','traveler')}**.")
            else:
                await ctx.send(f"✅ `!{cmd}` is already unlocked for **{char.get('name','traveler')}**.")
            return

        await ctx.send("⚠️ unlock_command helper missing in this build.")


async def setup(bot):
    await bot.add_cog(HelpCog(bot))
