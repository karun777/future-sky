"""Explicit command sequences. No learned or scheduled behaviour."""
import re
MAX_STEPS = 12
def result(ctx, status):
    ctx.sequence_result = status

def parse_sequence(bot, script):
    if len(script) > 1200:
        raise ValueError("Sequence is too long (maximum 1200 characters).")
    steps = [part.strip() for part in script.split(";")]
    if not steps or len(steps) > MAX_STEPS or any(not part for part in steps):
        raise ValueError("Use 1–12 commands separated by semicolons; no empty steps.")
    parsed = []
    for part in steps:
        if "\n" in part or "\r" in part or "`" in part:
            raise ValueError("Use one plain line of semicolon-separated commands.")
        text = part.removeprefix("!").strip()
        words = text.split()
        command = bot.get_command(words[0]) if words else None
        if not command or len(words) != 2:
            raise ValueError("Unsupported sequence step. Use go <direction>, work bar or queen pay.")
        if not re.fullmatch(r"[a-zA-Z_]+", words[1]):
            raise ValueError("Sequence arguments must be plain direction or action names.")
        canonical = command.qualified_name
        if not (canonical == "go" or (canonical == "work" and words[1].casefold() == "bar")
                or (canonical == "queen" and words[1].casefold() == "pay")):
            raise ValueError("Unsupported sequence step. Use go <direction>, work bar or queen pay.")
        parsed.append(" ".join(words))
    return parsed

def requires_choice(character):
    extra = character.get("extra") or {}
    thread = extra.get("thread_nodes") or {}
    return bool(thread.get("active_thread_node") or thread.get("active_encounter_id")
                or (character.get("flags") or {}).get("in_combat"))
