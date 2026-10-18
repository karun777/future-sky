"""W6-F3: isolated player output and activity wiring, no Discord connection."""
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
import json
import unittest

import discord
from discord.ext import commands
from discord.ext.commands.view import StringView
from fsbot.cogs.hud import HudCog, render_panel
from fsbot.cogs.help import HelpCog
from fsbot.cogs.navigation import NavigationCog
from fsbot.cogs.inspection import InspectionCog
from fsbot.cogs.ambient import AmbientCog, DEFAULT_GLOBAL_AMBIENT
from fsbot.cogs.activity import ActivityCog
from fsbot.cogs.router import _should_route_ctx
from fsbot.pod_opening import prepare_observation
from fsbot.storage import save_json
from test_pod_opening import Capture, FixtureStorage


class DisplayTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "characters.json"
        self.ctx = Capture()
        self.ctx.author.bot = False
        self.uid = str(self.ctx.author.id)
        self.original = {"id": self.uid, "name": "Fictional", "current_room": "pod_room",
                         "bag": {"keepsake": 1}, "equipped": {}, "credits": 9,
                         "extra": {"status": {}, "narrator": {"seen": ["quiet-memory"]},
                                   "hud": {"enabled": True, "state": "normal", "coherence": 97,
                                           "parallelism": 78, "commotion": "LOW"}}}
        save_json(str(self.path), {self.uid: self.original, "other": {"name": "Other", "bag": {"gift": 2}}})
        self.reload()

    def reload(self):
        self.storage = FixtureStorage(self.path)
        self.bot = SimpleNamespace(storage=self.storage)
        self.bot.presence = SimpleNamespace(
            get_character=lambda uid: self.storage.characters.get(uid),
            get_players_in_room=lambda room, exclude_user_id=None: [])
        self.bot.state = SimpleNamespace(ensure_player_records=lambda uid: None,
            resolve_room_for_user=lambda uid: self.storage.characters[uid]["current_room"])
        self.hud = HudCog(self.bot)
        self.ambient = object.__new__(AmbientCog)
        self.ambient.bot = self.bot
        self.ambient._global = deepcopy(DEFAULT_GLOBAL_AMBIENT)
        self.ambient._last_action, self.ambient._last_ambient = {}, {}
        self.ambient._ambient_history, self.ambient._recent_lines = {}, {}
        self.ambient._resting, self.ambient._sleeping = {}, set()
        self.inspection = InspectionCog(self.bot)
        self.bot.get_cog = lambda name: {"HudCog": self.hud, "AmbientCog": self.ambient,
                                       "InspectionCog": self.inspection}.get(name)
        self.activity = ActivityCog(self.bot)

    def char(self):
        return self.storage.characters[self.uid]

    async def look(self):
        self.ctx.messages.clear()
        await NavigationCog.look.callback(NavigationCog(self.bot), self.ctx)

    async def start(self):
        await InspectionCog.awaken.callback(self.inspection, self.ctx)

    async def inspect(self, target):
        self.ctx.messages.clear()
        await InspectionCog.inspect.callback(self.inspection, self.ctx, item=target)

    async def test_fresh_hud_read_is_non_mutating_and_uncalibrated(self):
        self.char()["extra"].pop("hud")
        self.storage.save_characters()
        before = self.path.read_text()
        await HudCog.hud.callback(self.hud, self.ctx)
        self.assertIn("No signals or notices", self.ctx.text())
        self.assertNotIn("hud", self.char()["extra"])
        self.assertEqual(self.path.read_text(), before)

    async def test_legacy_defaults_preserved_without_false_readings(self):
        before = deepcopy(self.char())
        await self.look()
        self.assertEqual(len(self.ctx.messages), 1)
        await HudCog.hud.callback(self.hud, self.ctx)
        self.assertIn("YOUR DISPLAY", self.ctx.text())
        self.assertNotIn("97%", self.ctx.text())
        self.assertNotIn("78%", self.ctx.text())
        self.assertNotIn("LOW", self.ctx.text())
        self.assertEqual(self.char(), before)

    async def test_navigation_respects_off_and_retains_room_exits(self):
        await HudCog.hud_off.callback(self.hud, self.ctx)
        self.reload()
        await self.look()
        self.assertNotIn("TELEMETRY", self.ctx.text())
        self.assertIn("west", self.ctx.text())
        self.assertEqual(len(self.ctx.messages), 1)
        await HudCog.hud.callback(self.hud, self.ctx)
        self.assertIn("DISPLAY OFFLINE", self.ctx.text())

    async def test_degraded_and_dimmed_never_leak_readings(self):
        for state, label in [("signal_degraded", "SIGNAL DEGRADED"), ("dark_mode", "DISPLAY DIMMED")]:
            await HudCog.hud_state.callback(self.hud, self.ctx, state=state)
            self.reload()
            await self.look()
            self.assertEqual(len(self.ctx.messages), 1)
            await HudCog.hud.callback(self.hud, self.ctx)
            self.assertIn(label, self.ctx.text())
            self.assertNotIn("97", self.ctx.text())
            self.assertNotIn("78", self.ctx.text())
            self.assertNotIn("LOW", self.ctx.text())

    async def test_settings_failure_rolls_back_without_success(self):
        before = deepcopy(self.storage.characters)
        disk = self.path.read_text()
        self.storage.fail_next = True
        await HudCog.hud_off.callback(self.hud, self.ctx)
        self.assertIn("could not save", self.ctx.text())
        self.assertNotIn("DISPLAY OFFLINE", self.ctx.text())
        self.assertEqual(self.storage.characters, before)
        self.assertEqual(self.path.read_text(), disk)

    async def test_invalid_state_and_repeated_settings_preserve_state(self):
        before = self.path.read_text()
        await HudCog.hud_state.callback(self.hud, self.ctx, state="hacked")
        self.assertEqual(self.path.read_text(), before)
        count = self.storage.save_calls
        await HudCog.hud_on.callback(self.hud, self.ctx)
        self.assertEqual(self.storage.save_calls, count)

    async def test_discover_display_once_then_resume_after_reload(self):
        await self.start()
        await self.inspect("hands")
        self.assertIn("edge of your vision", self.ctx.text())
        self.assertIn("!inspect hud", self.ctx.text())
        self.reload()
        await self.inspect("hands")
        self.assertNotIn("edge of your vision", self.ctx.text())
        await self.inspect("hud")
        self.assertIn("interface waits quietly", self.ctx.text())
        self.assertIn("!hud off", self.ctx.text())

    async def test_hud_off_does_not_disable_internal_impressions(self):
        await HudCog.hud_off.callback(self.hud, self.ctx)
        await self.start()
        await self.inspect("hands")
        self.assertNotIn("edge of your vision", self.ctx.text())
        self.assertEqual(self.char()["extra"]["narrator"]["seen"], ["quiet-memory"])
        await self.inspect("hud")
        self.assertIn("switched off", self.ctx.text())
        await HudCog.hud_on.callback(self.hud, self.ctx)
        await self.inspect("hands")
        self.assertIn("edge of your vision", self.ctx.text())

    async def test_brochure_crash_once_and_existing_seen_record_stays_seen(self):
        await self.start()
        await self.inspect("brochure")
        self.assertIn("metallic crash", self.ctx.text())
        self.reload()
        await self.inspect("brochure")
        self.assertNotIn("metallic crash", self.ctx.text())
        self.assertIn("same reassurance", self.ctx.text())

    async def test_failed_brochure_save_has_no_crash_then_retry_once(self):
        await self.start()
        self.storage.fail_next = True
        await self.inspect("brochure")
        self.assertNotIn("metallic crash", self.ctx.text())
        await self.inspect("brochure")
        self.assertIn("metallic crash", self.ctx.text())

    async def test_display_discovery_failure_does_not_consume_first_notice(self):
        await self.start()
        self.storage.fail_next = True
        await self.inspect("hands")
        self.assertNotIn("edge of your vision", self.ctx.text())
        await self.inspect("hands")
        self.assertIn("edge of your vision", self.ctx.text())

    async def test_typing_in_own_run_channel_updates_ambient_and_cancels_rest(self):
        self.char()["run_channel_id"] = 55
        self.ambient._resting[self.uid] = 1
        self.ambient._sleeping.add(self.uid)
        with patch("fsbot.cogs.ambient.time.monotonic", return_value=12345):
            await self.activity.on_typing(SimpleNamespace(id=55), self.ctx.author, None)
        self.assertEqual(self.ambient._last_action[self.uid], 12345)
        self.assertNotIn(self.uid, self.ambient._resting)
        self.assertNotIn(self.uid, self.ambient._sleeping)

    async def test_typing_elsewhere_or_bot_does_not_postpone_ambient(self):
        self.char()["run_channel_id"] = 55
        await self.activity.on_typing(SimpleNamespace(id=66), self.ctx.author, None)
        await self.activity.on_typing(SimpleNamespace(id=55), SimpleNamespace(id=self.uid, bot=True), None)
        self.assertNotIn(self.uid, self.ambient._last_action)

    async def test_run_channel_message_updates_same_activity_path(self):
        self.char()["run_channel_id"] = 55
        message = SimpleNamespace(author=self.ctx.author, channel=SimpleNamespace(id=55), content="!look")
        await self.activity.on_message(message)
        self.assertIn(self.uid, self.ambient._last_action)

    def prepare_loop(self):
        self.bot.guilds = [SimpleNamespace(id=1)]
        self.bot.presence.iter_character_records = lambda: list(self.storage.characters.items())[:1]
        self.bot.presence.resolve_room_for_user = lambda uid: "pod_room"
        self.ambient._send_embed = AsyncMock(return_value=True)

    async def test_active_play_discovery_gives_ambient_breathing_space(self):
        self.prepare_loop()
        with patch("fsbot.cogs.ambient.time.monotonic", return_value=1000):
            await self.ambient.on_command(self.ctx)
        with patch("fsbot.cogs.ambient.time.monotonic", return_value=1119), \
             patch("fsbot.cogs.ambient.asyncio.sleep", new=AsyncMock()):
            await AmbientCog.ambient_loop.coro(self.ambient)
        self.ambient._send_embed.assert_not_awaited()
        with patch("fsbot.cogs.ambient.time.monotonic", return_value=1120), \
             patch("fsbot.cogs.ambient.asyncio.sleep", new=AsyncMock()):
            await AmbientCog.ambient_loop.coro(self.ambient)
        self.ambient._send_embed.assert_awaited_once()

    async def test_new_idle_choice_suppresses_ambient_in_same_iteration(self):
        self.prepare_loop()
        self.ambient._last_action[self.uid] = 1
        async def start_choice(*args):
            self.storage.characters[self.uid] = deepcopy(self.char())
            self.char()["extra"]["thread_nodes"] = {"active_thread_node": "fictional-choice"}
        original_get = self.bot.get_cog
        self.bot.get_cog = lambda name: SimpleNamespace(maybe_trigger_on_idle=start_choice) if name == "ThreadNodesCog" else original_get(name)
        with patch("fsbot.cogs.ambient.time.monotonic", return_value=1000), \
             patch("fsbot.cogs.ambient.asyncio.sleep", new=AsyncMock()):
            await AmbientCog.ambient_loop.coro(self.ambient)
        self.ambient._send_embed.assert_not_awaited()

    async def parse_hud(self, action, command_name="hud"):
        bot = commands.Bot(command_prefix="!", intents=discord.Intents.none())
        bot.presence, bot.storage = self.bot.presence, self.storage
        await bot.add_cog(self.hud)
        cmd = bot.get_command(command_name)
        message = SimpleNamespace(_state=SimpleNamespace(), attachments=[], author=self.ctx.author, channel=self.ctx.channel)
        context = commands.Context(message=message, bot=bot, view=StringView(action), prefix="!", command=cmd)
        context.send = self.ctx.send
        await cmd._parse_arguments(context)
        await cmd.callback(*context.args, **context.kwargs)
        await bot.close()

    async def test_spaced_on_off_real_parser_and_reload(self):
        await self.parse_hud("off")
        self.assertIn("DISPLAY OFFLINE", self.ctx.text())
        self.reload()
        self.assertFalse(self.char()["extra"]["hud"]["enabled"])
        self.ctx.messages.clear()
        await self.parse_hud("ON")
        self.assertIn("YOUR DISPLAY", self.ctx.text())
        self.reload()
        self.assertTrue(self.char()["extra"]["hud"]["enabled"])

    async def test_spaced_states_real_parser_accepts_multiple_words(self):
        for action, state, label in [
                ("state signal degraded", "signal_degraded", "SIGNAL DEGRADED"),
                ("state dark mode", "dark_mode", "DISPLAY DIMMED"),
                ("state normal", "normal", "YOUR DISPLAY")]:
            self.ctx.messages.clear()
            await self.parse_hud(action)
            self.assertEqual(self.char()["extra"]["hud"]["state"], state)
            self.assertIn(label, self.ctx.text())

    async def test_underscore_compatibility_and_invalid_alias_arguments(self):
        await self.parse_hud("", "hud_off")
        self.assertFalse(self.char()["extra"]["hud"]["enabled"])
        await self.parse_hud("", "hud_on")
        self.assertTrue(self.char()["extra"]["hud"]["enabled"])
        await self.parse_hud("signal_degraded", "hud_state")
        self.assertEqual(self.char()["extra"]["hud"]["state"], "signal_degraded")
        for alias in ["hud_on", "hud_off"]:
            before = deepcopy(self.char())
            self.ctx.messages.clear()
            await self.parse_hud("nonsense", alias)
            self.assertIn("Use `!hud`", self.ctx.text())
            self.assertEqual(self.char(), before)

    async def test_unknown_or_trailing_arguments_never_silently_ignored(self):
        before = deepcopy(self.char())
        disk = self.path.read_text()
        for action in ["off please", "state", "state mystery", "on nonsense", "frobnicate"]:
            self.ctx.messages.clear()
            await self.parse_hud(action)
            self.assertIn("Use `!hud`", self.ctx.text())
            self.assertEqual(self.char(), before)
            self.assertEqual(self.path.read_text(), disk)

    async def test_discovery_panel_does_not_reveal_undiscovered_signal_or_booking(self):
        await self.start()
        await HudCog.hud.callback(self.hud, self.ctx)
        self.assertNotIn("Remembered booking", self.ctx.text())
        self.assertNotIn("!feed7", self.ctx.text())
        await self.inspect("panels")
        self.ctx.messages.clear()
        await HudCog.hud.callback(self.hud, self.ctx)
        self.assertIn("Unread notice", [field.name for field in self.ctx.messages[-1]["embed"].fields])
        self.assertNotIn("!feed7", self.ctx.text())
        await self.inspect("display")
        self.ctx.messages.clear()
        await HudCog.hud.callback(self.hud, self.ctx)
        self.assertIn("!feed7", self.ctx.text())
        self.assertNotIn("tomorrow night", self.ctx.text())
        await self.inspect("booking")
        self.reload()
        self.ctx.messages.clear()
        await HudCog.hud.callback(self.hud, self.ctx)
        self.assertIn("Remembered booking", [field.name for field in self.ctx.messages[-1]["embed"].fields])
        self.assertIn("tomorrow night", self.ctx.text())

    async def test_off_and_degraded_conceal_discovered_information(self):
        await self.start()
        await self.inspect("display")
        await self.inspect("booking")
        for action in ["off", "on", "state signal degraded", "state dark mode"]:
            self.ctx.messages.clear()
            await HudCog.hud.callback(self.hud, self.ctx, action=action)
            if action != "on":
                self.assertNotIn("FEED7", self.ctx.text())
                self.assertNotIn("tomorrow night", self.ctx.text())

    async def test_player_help_uses_spaced_hud_forms(self):
        await HelpCog.help_cmd.callback(HelpCog(self.bot), self.ctx)
        self.assertIn("!hud on", self.ctx.text())
        self.assertIn("!hud off", self.ctx.text())
        self.assertNotIn("!hud_", self.ctx.text())

    def test_all_hud_commands_route_privately(self):
        for name in ("hud", "hud_on", "hud_off", "hud_state"):
            ctx = SimpleNamespace(command=SimpleNamespace(qualified_name=name, name=name))
            self.assertTrue(_should_route_ctx(ctx))

    async def test_other_character_and_possessions_unchanged(self):
        other = deepcopy(self.storage.characters["other"])
        await self.start()
        await self.inspect("hands")
        await HudCog.hud_off.callback(self.hud, self.ctx)
        self.assertEqual(self.storage.characters["other"], other)
        self.assertEqual(self.char()["bag"], {"keepsake": 1})
        self.assertEqual(self.char()["credits"], 9)


if __name__ == "__main__":
    unittest.main()
