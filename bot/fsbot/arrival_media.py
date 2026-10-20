"""Five approved threshold concepts; presentation only, no draft/world mutation."""
import discord
ASSET_ROOT = "assets/images/arrival/before_first_breath/v1/"
BASE_URL = "https://future-sky.net/" + ASSET_ROOT
STAGES = {
    "inclination": ("Inclination", "Something draws your attention.\nYou have followed it before.",
                    "Choose a starting inclination: !begin class Dreamer-Technician. "
                    "Use !begin help for all available classes and commands."),
    "history": ("History", "Some journeys return as memories.\nOthers still feel like dreams.",
                "Set !begin name <name> and !begin date <YYYY-MM-DD> "
                "(a fictional character date, used for astrology). "
                "Optional: !begin background <a few lines>."),
    "embodiment": ("Embodiment", "Weight. Warmth.\nThe possibility of touch.\nA shape you might call yours.",
                   "Set !begin body familiar|unfamiliar for recognition, then "
                   "!begin embodiment familiar|unfamiliar for how accustomed being embodied feels."),
    "gathering": ("Gathering", "Enough to begin.\nMuch remains beyond reach.",
                  "Use !begin review. You can still edit any choice or add !begin background <a few lines>."),
    "awakening": ("Awakening", "A sound reaches you.\nThen the surface beneath your fingers.", ""),
}
def pending_stage(draft):
    if "class_id" not in draft:
        return "inclination"
    if any(k not in draft for k in ("name", "birthdate")):
        return "history"
    if any(k not in draft for k in ("body_recognition", "embodiment_familiarity")):
        return "embodiment"
    return "gathering"

def stage_embed(stage, *, preview=False):
    title, prose, guidance = STAGES[stage]
    embed=discord.Embed(title=title + (" — PREVIEW" if preview else ""), description=prose, color=0x73629A)
    embed.set_image(url=BASE_URL + stage + ".webp")
    if guidance:
        embed.add_field(name="Your next step", value=guidance, inline=False)
    embed.set_footer(text=("Preview only; no saved character changes. " if preview else "") +
                          "Drafts are temporary. !begin cancel discards; !begin help explains.")
    return embed
