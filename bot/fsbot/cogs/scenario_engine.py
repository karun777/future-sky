# ============================================================
# FILE META — fsbot/cogs/scenario_engine.py
# Canonical name: ScenarioEngineCog (EventBus bridge + diagnostics)
#
# Version: v0.2.0 — Feather 1.5: Living Scenario State
# Last edited: 2026-07-17 (Australia/Perth)
#
# Scope:
# - Subscribe ScenarioService to character.entered_room
# - Demonstrate variables, flags, factual history, and authored notes
# - Provide minimal development diagnostics
# - No persistence, rendering authority, or movement authority
# ============================================================

from __future__ import annotations

from typing import Any, Dict

from discord.ext import commands

from fsbot.events import EventResult


class ScenarioEngineCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log = getattr(bot, "log", None)
        self._subscribed = False

    async def cog_load(self) -> None:
        events = getattr(self.bot, "events", None)
        if events is None:
            raise RuntimeError("ScenarioEngineCog requires bot.events")
        if getattr(self.bot, "scenarios", None) is None:
            raise RuntimeError("ScenarioEngineCog requires bot.scenarios")

        events.subscribe("character.entered_room", self.on_character_entered_room)
        self._subscribed = True

    def cog_unload(self) -> None:
        if not self._subscribed:
            return
        events = getattr(self.bot, "events", None)
        if events is not None:
            events.unsubscribe("character.entered_room", self.on_character_entered_room)
        self._subscribed = False

    async def on_character_entered_room(self, event: Dict[str, Any]) -> EventResult:
        """Advance Portal Run only when the player enters its expected room."""
        source = event.get("source") if isinstance(event.get("source"), dict) else {}
        scope = event.get("scope") if isinstance(event.get("scope"), dict) else {}
        payload = event.get("payload") if isinstance(event.get("payload"), dict) else {}

        player_id = source.get("actor_id")
        room_id = payload.get("to_room_id") or scope.get("room_id")
        if not player_id or not room_id:
            return EventResult.skipped("missing player or room")

        uid = str(player_id)
        entered_room = str(room_id)
        service = self.bot.scenarios
        scenario_id = service.PORTAL_RUN_ID

        if not service.is_active(uid, scenario_id):
            return EventResult.no_match("no active portal run")

        expected = service.expected_room(uid, scenario_id)
        if expected != entered_room:
            return EventResult.no_match(
                "off route; progress preserved",
                expected_room=expected,
                entered_room=entered_room,
            )

        instance = service.get_active(uid, scenario_id)
        if not isinstance(instance, dict):
            return EventResult.skipped("active instance unavailable")

        current_index = int(instance.get("step_index", 0))
        is_final_room = current_index >= len(service.PORTAL_RUN_ROUTE) - 1

        service.increment_variable(uid, scenario_id, "rooms_advanced", 1)
        service.set_variable(uid, scenario_id, "last_room_id", entered_room)

        if entered_room == "neptune_lounge":
            service.add_flag(uid, scenario_id, "entered_neptune_lounge")
            note = "You crossed into Neptune Lounge and the journey took hold."
        elif entered_room == "main_square":
            service.add_flag(uid, scenario_id, "reached_main_square")
            note = "The market confluence became part of your remembered route."
        else:
            service.add_flag(uid, scenario_id, "reached_efiishents_office")
            note = "You reached Efiishent's office and completed the portal run."

        if is_final_room:
            completed = service.complete(
                uid,
                scenario_id,
                history_event="room.entered",
                history_details={
                    "room_id": entered_room,
                    "completed_scenario": True,
                },
                note=note,
            )
            return EventResult.applied(
                "portal run completed",
                scenario_id=scenario_id,
                status=(completed or {}).get("status"),
                history_count=len((completed or {}).get("history", [])),
            )

        advanced = service.advance(
            uid,
            scenario_id,
            history_event="room.entered",
            history_details={"room_id": entered_room},
            note=note,
        )
        return EventResult.applied(
            "portal run advanced",
            scenario_id=scenario_id,
            step_id=(advanced or {}).get("step_id"),
            expected_room=service.expected_room(uid, scenario_id),
            rooms_advanced=(advanced or {}).get("variables", {}).get("rooms_advanced"),
        )

    # --------------------------------------------------
    # Development commands
    # --------------------------------------------------

    @commands.command(name="scenario_start")
    async def scenario_start(self, ctx: commands.Context, scenario_id: str = "portal_run"):
        sid = str(scenario_id or "").strip().lower()
        if sid != self.bot.scenarios.PORTAL_RUN_ID:
            await ctx.send(f"Unknown Feather 1.5 scenario: `{sid}`")
            return

        uid = str(ctx.author.id)
        instance = self.bot.scenarios.start(
            uid,
            sid,
            variables={
                "rooms_advanced": 0,
                "orientation": 0,
                "clues_found": 0,
            },
            note="A route opened before you, though its meaning was not yet clear.",
        )
        expected = self.bot.scenarios.expected_room(uid, sid)
        await ctx.send(
            f"🧭 Scenario started: **{sid}**\n"
            f"Chapter: `{instance.get('chapter_id')}`\n"
            f"Current step: `{instance.get('step_id')}`\n"
            f"Expected room: `{expected}`\n"
            f"World time: `{instance.get('started_at_world')}`"
        )

    @commands.command(name="scenario_status")
    async def scenario_status(self, ctx: commands.Context):
        uid = str(ctx.author.id)
        active = self.bot.scenarios.get_active(uid)
        if not active:
            await ctx.send("No active scenarios.")
            return

        lines = []
        for instance in active:
            sid = str(instance.get("scenario_id"))
            expected = self.bot.scenarios.expected_room(uid, sid)
            variables = instance.get("variables", {})
            lines.append(
                f"• **{sid}** — `{instance.get('step_id')}` "
                f"(expected: `{expected}`)\n"
                f"  variables: `{variables}`\n"
                f"  flags: `{instance.get('flags', [])}`\n"
                f"  history: `{len(instance.get('history', []))}` | "
                f"notes: `{len(instance.get('notes', []))}`"
            )
        await ctx.send("🧭 Active scenarios\n" + "\n".join(lines))

    @commands.command(name="scenario_memory")
    async def scenario_memory(self, ctx: commands.Context):
        """Show active memory, or the most recently completed scenario."""
        uid = str(ctx.author.id)
        active = self.bot.scenarios.get_active(uid)
        if active:
            instance = active[-1]
        else:
            completed = self.bot.scenarios.get_completed(uid)
            if not completed:
                await ctx.send("No scenario memory exists for your character.")
                return
            instance = completed[-1]

        history_lines = [
            f"• `{entry.get('world_time')}` — **{entry.get('event_type')}** "
            f"`{entry.get('details', {})}`"
            for entry in instance.get("history", [])[-8:]
        ] or ["• No factual history recorded."]

        note_lines = [
            f"• `{entry.get('world_time')}` — {entry.get('text')}"
            for entry in instance.get("notes", [])[-8:]
        ] or ["• No authored notes recorded."]

        await ctx.send(
            f"📖 **Scenario memory — {instance.get('scenario_id')}**\n"
            f"Status: `{instance.get('status')}` | Chapter: `{instance.get('chapter_id')}`\n"
            f"Variables: `{instance.get('variables', {})}`\n"
            f"Flags: `{instance.get('flags', [])}`\n\n"
            f"**History**\n" + "\n".join(history_lines) + "\n\n"
            f"**Notes**\n" + "\n".join(note_lines)
        )

    @commands.command(name="scenario_reset")
    async def scenario_reset(self, ctx: commands.Context):
        uid = str(ctx.author.id)
        self.bot.scenarios.reset_player(uid)
        await ctx.send("🧹 Scenario runtime state reset for your character.")


async def setup(bot):
    await bot.add_cog(ScenarioEngineCog(bot))
