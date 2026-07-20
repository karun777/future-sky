from __future__ import annotations

import discord

# ============================================================
# Future Sky Console v2
# Eight Voices:
# PLACE, SELF, OTHER, WORLD, SIGNAL, CHOICE, SYSTEM, THRESHOLD
# ============================================================

FS_BLUE = 0x2F6BFF      # PLACE
FS_PURPLE = 0x7C4DFF    # WORLD
FS_GOLD = 0xF5C451      # CHOICE / SYSTEM
FS_RED = 0xC63F3F       # THRESHOLD / ERROR
FS_GREY = 0x555555      # SELF / HUD
FS_GREEN = 0x4CAF50     # SIGNAL / STABLE
FS_BLACK = 0x111111     # DEEP SYSTEM


# ============================================================
# Voice: PLACE
# "You are somewhere."
# ============================================================

def place_embed(
    title: str,
    description: str,
    *,
    color: int = FS_BLUE,
    image: str | None = None,
    thumbnail: str | None = None,
    footer: str | None = None,
) -> discord.Embed:
    embed = discord.Embed(
        title=f"🜂 {title}",
        description=description,
        color=color,
    )

    if thumbnail:
        embed.set_thumbnail(url=thumbnail)

    if image:
        embed.set_image(url=image)

    if footer:
        embed.set_footer(text=footer)

    return embed


# Backwards-compatible wrapper
def room_embed(*args, **kwargs) -> discord.Embed:
    return place_embed(*args, **kwargs)


# ============================================================
# Voice: SELF
# "You notice yourself."
# ============================================================

def self_embed(
    text: str,
    *,
    title: str = "💭 INTERNAL",
    color: int = FS_GREY,
) -> discord.Embed:
    return discord.Embed(
        title=title,
        description=text,
        color=color,
    )


# Backwards-compatible wrapper
def internal_embed(text: str) -> discord.Embed:
    return self_embed(text)


# ============================================================
# Voice: OTHER
# "Someone notices you."
# ============================================================

def other_embed(
    name: str,
    text: str,
    *,
    portrait: str | None = None,
    color: int = FS_GOLD,
) -> discord.Embed:
    embed = discord.Embed(
        title=f"◌ {name}",
        description=text,
        color=color,
    )

    if portrait:
        embed.set_image(url=portrait)

    return embed


# ============================================================
# Voice: WORLD
# "Reality changes."
# ============================================================

def world_embed(
    title: str,
    description: str,
    *,
    color: int = FS_PURPLE,
    image: str | None = None,
    thumbnail: str | None = None,
) -> discord.Embed:
    embed = discord.Embed(
        title="◉ WORLD EVENT",
        description=f"**{title}**\n\n{description}",
        color=color,
    )

    if thumbnail:
        embed.set_thumbnail(url=thumbnail)

    if image:
        embed.set_image(url=image)

    return embed


# Backwards-compatible wrapper
def thread_embed(*args, **kwargs) -> discord.Embed:
    return world_embed(*args, **kwargs)


# ============================================================
# Voice: SIGNAL
# "Something is trying to communicate."
# ============================================================

def signal_embed(
    title: str,
    text: str,
    *,
    image: str | None = None,
    color: int = FS_GREEN,
) -> discord.Embed:
    embed = discord.Embed(
        title=f"📡 {title}",
        description=text,
        color=color,
    )

    if image:
        embed.set_image(url=image)

    embed.set_footer(text="FEED7 // SIGNAL DETECTED")

    return embed


# ============================================================
# Voice: CHOICE
# "Agency awakens."
# ============================================================

def choice_embed(
    title: str,
    choices: list[str],
    *,
    color: int = FS_GOLD,
) -> discord.Embed:
    body = "\n".join(
        f"`{i + 1}`  {choice}"
        for i, choice in enumerate(choices)
    )

    return discord.Embed(
        title=f"◇ {title}",
        description=body,
        color=color,
    )


# Backwards-compatible wrapper
def choices_embed(title: str, choices: list[str]) -> discord.Embed:
    return choice_embed(title, choices)


# ============================================================
# Voice: SYSTEM
# "The machinery speaks."
# ============================================================

def system_embed(
    title: str,
    text: str,
    *,
    color: int = FS_GOLD,
) -> discord.Embed:
    return discord.Embed(
        title=f"⚙ {title}",
        description=text,
        color=color,
    )


def error_embed(text: str) -> discord.Embed:
    return discord.Embed(
        title="⚠ SYSTEM",
        description=text,
        color=FS_RED,
    )


# ============================================================
# Voice: THRESHOLD
# "Something irreversible is happening."
# ============================================================

def threshold_embed(
    title: str,
    description: str,
    *,
    image: str | None = None,
    footer: str = "STATUS: ENTANGLED",
    color: int = FS_RED,
) -> discord.Embed:
    embed = discord.Embed(
        title=f"◇ THRESHOLD • {title}",
        description=description,
        color=color,
    )

    if image:
        embed.set_image(url=image)

    embed.set_footer(text=footer)

    return embed


# Backwards-compatible wrapper
def arrival_embed(
    title: str,
    description: str,
    *,
    image: str | None = None,
) -> discord.Embed:
    return threshold_embed(title, description, image=image)


# ============================================================
# Telemetry
# ============================================================

def hud_embed(
    *,
    coherence: int = 97,
    parallelism: int = 78,
    commotion: str = "LOW",
) -> discord.Embed:
    embed = discord.Embed(
        title="◉ TELEMETRY",
        color=FS_GREY,
    )

    embed.add_field(
        name="♆ COHERENCE",
        value=f"{coherence}%",
        inline=True,
    )

    embed.add_field(
        name="♄ PARALLELISM",
        value=f"{parallelism}%",
        inline=True,
    )

    embed.add_field(
        name="✦ COMMOTION",
        value=str(commotion),
        inline=True,
    )

    return embed


def add_hud(
    embed: discord.Embed,
    *,
    coherence: int = 97,
    parallelism: int = 78,
    commotion: str = "LOW",
) -> discord.Embed:
    embed.add_field(
        name="♆ COHERENCE",
        value=f"{coherence}%",
        inline=True,
    )

    embed.add_field(
        name="♄ PARALLELISM",
        value=f"{parallelism}%",
        inline=True,
    )

    embed.add_field(
        name="✦ COMMOTION",
        value=str(commotion),
        inline=True,
    )

    return embed