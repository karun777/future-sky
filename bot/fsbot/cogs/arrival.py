"""Private, bounded creation rehearsal; existing characters can preview only."""
from datetime import datetime
import discord
from discord.ext import commands
from fsbot.cogs.core import CLASS_IDS, build_arrival_character
from fsbot.pod_opening import prepare_observation
from fsbot.arrival_media import pending_stage, stage_embed, STAGES

START_CLASSES = [c for c in CLASS_IDS if c != "unwritten"]
PROMPT = ("**Before you awaken**\nChoose a starting inclination with "
          "\x60!begin class dreamer_technician\x60.\nAvailable: " +
          ", ".join(c.replace("_", " ").title() for c in START_CLASSES) +
          "\nThen use !begin name <name>, !begin date <YYYY-MM-DD> "
          "(your fictional character's date, used for existing astrology), "
          "!begin body familiar|unfamiliar, and !begin embodiment familiar|unfamiliar.\n"
          "Optional: !begin background <a few lines>.\n"
          "!begin review shows your beginning; !begin cancel discards it. "
          "Drafts are temporary and disappear if the bot restarts.")

class ArrivalCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.drafts = {}

    @commands.command(name="begin")
    async def begin(self, ctx, *, action: str = ""):
        if getattr(ctx, "guild", None) is not None:
            await ctx.send("Send !begin in a direct message to Future Sky for private character setup. "
                           "Existing characters can use !begin preview there.")
            return
        uid = str(ctx.author.id)
        text = action.strip()
        command, _, value = text.partition(" ")
        command = command.casefold()
        value = value.strip()
        existing = uid in self.bot.storage.characters
        if command == "cancel" and not value:
            self.drafts.pop(uid, None)
            await ctx.send("Draft discarded. Your saved character is unchanged.")
            return
        if command == "preview" and not value:
            self.drafts[uid] = {"preview": True}
            await ctx.send("**PREVIEW — nothing will be saved.**",
                           embed=stage_embed("inclination", preview=True))
            return
        if existing and not self.drafts.get(uid, {}).get("preview"):
            await ctx.send("You already have a character. Use !begin preview for a disposable rehearsal; "
                           "your existing character will not be replaced.")
            return
        if command == "help" and not value:
            await ctx.send(PROMPT)
            return
        if not command:
            draft = self.drafts.setdefault(uid, {"preview": False})
            await ctx.send(embed=stage_embed(pending_stage(draft), preview=draft["preview"]))
            return
        if uid not in self.drafts:
            await ctx.send("Start with !begin, or !begin preview for a disposable rehearsal.")
            return
        draft = self.drafts[uid]
        if command == "inspect" and draft.get("preview") and draft.get("preview_character"):
            from fsbot.pod_opening import scene_target
            target = scene_target(value)
            if not target:
                await ctx.send("Try !begin inspect hands, body, pod, panels or wardrobe.")
                return
            character, view = prepare_observation(draft["preview_character"], target)
            draft["preview_character"] = character
            title, description, guidance = view
            await ctx.send(embed=discord.Embed(title="PREVIEW // " + title, description=description))
            await ctx.send("Continue with !begin inspect hands, body, pod, panels or wardrobe. "
                           "!begin cancel ends this disposable preview; ordinary game commands are outside it.")
            return
        fields = {"class": "class_id", "name": "name", "date": "birthdate",
                  "body": "body_recognition", "embodiment": "embodiment_familiarity",
                  "background": "origin_note"}
        if command in fields:
            if not value or len(value) > (1000 if command == "background" else 80):
                await ctx.send("Supply a short value; background can be up to 1000 characters, other fields 80.")
                return
            if command == "class":
                value = "_".join(value.casefold().replace("-", " ").replace("_", " ").split())
                if value not in START_CLASSES:
                    await ctx.send("Choose a listed starting class. Unwritten is not offered by this guided first pass.")
                    return
            if command in {"body", "embodiment"}:
                value = value.casefold()
                if value not in {"familiar", "unfamiliar"}:
                    await ctx.send("Choose familiar or unfamiliar.")
                    return
            if command == "date":
                try:
                    datetime.strptime(value, "%Y-%m-%d")
                except ValueError:
                    await ctx.send("Use YYYY-MM-DD for your fictional character's date.")
                    return
            previous_stage = pending_stage(draft)
            draft[fields[command]] = value
            draft.pop("reviewed", None)
            next_stage = pending_stage(draft)
            if next_stage != previous_stage:
                await ctx.send(embed=stage_embed(next_stage, preview=draft["preview"]))
            else:
                await ctx.send("Updated. " + STAGES[next_stage][2])
            return
        required = {"class_id", "name", "birthdate", "body_recognition", "embodiment_familiarity"}
        if command in {"review", "awaken"} and not value:
            missing = sorted(required - draft.keys())
            if missing:
                await ctx.send("Still needed: " + ", ".join(missing) + ". Use !begin for instructions.")
                return
            if command == "review":
                embed = stage_embed("gathering", preview=draft["preview"])
                embed.title = "Your beginning" + (" — PREVIEW" if draft["preview"] else "")
                embed.clear_fields()
                for label, key in [("Name", "name"), ("Starting inclination", "class_id"),
                                   ("Character date", "birthdate"), ("Recognising your body", "body_recognition"),
                                   ("Being embodied", "embodiment_familiarity"), ("Background", "origin_note")]:
                    embed.add_field(name=label, value=(draft.get(key, "").replace("_", " ").title() if key == "class_id" else draft.get(key)) or "Left open.", inline=False)
                embed.set_footer(text="Edit any field, or !begin awaken to continue. !begin cancel discards this draft.")
                draft["reviewed"] = True
                await ctx.send(embed=embed)
                return
            if not draft.get("reviewed"):
                await ctx.send("Use !begin review before awakening.")
                return
            if existing and not draft["preview"]:
                await ctx.send("A character now exists; this draft cannot replace it.")
                return
            character = build_arrival_character(uid, draft["name"], draft["birthdate"],
                                                draft["class_id"], draft.get("origin_note", ""),
                                                self.bot.storage.items_db)
            character["extra"]["arrival"] = {
                "body_recognition": draft["body_recognition"],
                "embodiment_familiarity": draft["embodiment_familiarity"],
                "origin": "guided_creation_v1",
                "performance_booking": False,
            }
            character, view = prepare_observation(character)
            if not draft["preview"]:
                # No awaits between existence check, insertion and durable save.
                if uid in self.bot.storage.characters:
                    await ctx.send("A character now exists; no replacement was made.")
                    return
                self.bot.storage.characters[uid] = character
                try:
                    self.bot.storage.save_characters()
                except Exception:
                    self.bot.storage.characters.pop(uid, None)
                    await ctx.send("Your beginning could not be saved. Your draft is retained; try again.")
                    return
            if draft["preview"]:
                draft["preview_character"] = character
            title, description, guidance = view
            if draft["preview"]:
                guidance = guidance.replace("!inspect ", "!begin inspect ")
            embed = stage_embed("awakening", preview=draft["preview"])
            embed.title = title + (" — PREVIEW" if draft["preview"] else "")
            embed.description += "\n\n" + description
            await ctx.send(embed=embed)
            await ctx.send(("**PREVIEW ONLY — no character changed.**\n" if draft["preview"] else "") +
                           guidance + "\n" +
                           ("Use !begin cancel to finish this rehearsal." if draft["preview"] else
                            "You can continue here, or use !look in the server to enter your run-channel flow."))
            if not draft["preview"]:
                self.drafts.pop(uid, None)
            return
        await ctx.send("Use !begin for setup instructions. Nothing was changed.")

async def setup(bot):
    await bot.add_cog(ArrivalCog(bot))
