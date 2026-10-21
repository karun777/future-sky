"""Real navigation/inspection/exchange callbacks; temporary fictional storage only."""
from copy import deepcopy
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock
import unittest
import discord
from discord.ext import commands
import test_display
from fsbot.cogs.navigation import NavigationCog
from fsbot.cogs.wardrobe import WardrobeCog
from fsbot.cogs.router import ROUTE_GAMEPLAY_COMMANDS
from fsbot.lounge_arrival import arrival_attention, counterkeeper_view
from fsbot.pod_opening import prepare_observation
from fsbot.token_exchange import TOKEN

class LoungeArrivalTests(unittest.IsolatedAsyncioTestCase):
    setUp = test_display.DisplayTests.setUp
    reload = test_display.DisplayTests.reload
    char = test_display.DisplayTests.char
    inspect = test_display.DisplayTests.inspect
    look = test_display.DisplayTests.look

    def rooms(self):
        self.storage.rooms = json.loads((Path(__file__).resolve().parents[1] / "data/rooms/rooms.json").read_text())
        # Room media playback and other participants are outside this callback trial.
        self.bot.state.play_music = AsyncMock()
        self.bot.presence.get_room_members = lambda room: []
        self.bot.state.resolve_era_for_room = lambda room: "manzo"

    async def test_walk_inspect_exchange_reload_and_no_replay(self):
        self.rooms()
        started, _ = prepare_observation(self.char())
        self.storage.characters[self.uid] = started
        wardrobe = WardrobeCog(self.bot)
        await WardrobeCog.search_pod.callback(wardrobe, self.ctx, target="panel")
        other = deepcopy(self.storage.characters["other"])
        self.bot.events = SimpleNamespace(publish=AsyncMock())
        nav = NavigationCog(self.bot)
        # Register the cog as Discord does, including binding its look command.
        registry = commands.Bot(command_prefix="!", intents=discord.Intents.none())
        await registry.add_cog(nav)
        self.addAsyncCleanup(registry.close)
        for direction, destination in [("west", "hostel_hallway"), ("down", "hostel_stairwell"), ("down", "neptune_lounge")]:
            self.ctx.messages.clear()
            await NavigationCog.go.callback(nav, self.ctx, direction)
            self.assertEqual(self.char()["current_room"], destination)
            persisted = json.loads(self.path.read_text())[self.uid]
            self.assertEqual(persisted["current_room"], destination)
            self.assertIn("!go down" if destination != "neptune_lounge" else "!inspect counterkeeper", self.ctx.text())
        self.assertEqual(self.bot.events.publish.await_count, 3)
        before = self.path.read_text()
        await self.inspect("counterkeeper")
        self.assertIn("!offer token", self.ctx.text())
        self.assertEqual(self.path.read_text(), before)
        await WardrobeCog.offer_item.callback(wardrobe, self.ctx, target="token")
        self.assertIn("exchange is remembered", self.ctx.text())
        self.reload()
        self.assertNotIn(TOKEN, self.char()["bag"])
        self.assertTrue(self.char()["flags"]["counterkeeper_token_received"])
        self.assertEqual(self.storage.characters["other"], other)
        before = self.path.read_text()
        await self.inspect("counterkeeper")
        self.assertIn("has your brass token", self.ctx.text())
        wardrobe = WardrobeCog(self.bot)
        await WardrobeCog.offer_item.callback(wardrobe, self.ctx, target="token")
        self.assertEqual(self.path.read_text(), before)
        self.assertIn("already has your token", self.ctx.text())

    async def test_generic_arrival_has_no_booking_or_token_requirement(self):
        self.rooms()
        started, _ = prepare_observation(self.char())
        started["extra"]["arrival"]["performance_booking"] = False
        started["extra"]["arrival"]["opening"]["discoveries"] = ["booking"]
        started["current_room"] = "neptune_lounge"
        self.storage.characters[self.uid] = started
        before = self.path.read_text()
        await self.look()
        self.assertNotIn("gig tomorrow", self.ctx.text())
        await self.inspect("counterkeeper")
        self.assertIn("No exchange is required", self.ctx.text())
        self.assertNotIn("!offer token", self.ctx.text())
        self.assertEqual(self.path.read_text(), before)

    async def test_known_booking_only_and_no_secret_identity(self):
        self.rooms()
        ch, _ = prepare_observation(self.char())
        ch["current_room"] = "neptune_lounge"
        room = self.storage.rooms["neptune_lounge"]
        self.assertNotIn("gig tomorrow", arrival_attention(ch, room)[1])
        ch["extra"]["arrival"]["opening"]["discoveries"].append("booking")
        text = arrival_attention(ch, room)[1]
        self.assertIn("gig tomorrow", text)
        for secret in ["Queen", "ambassador", "princess", "meet someone"]:
            self.assertNotIn(secret, text)

    def test_local_scope_and_exit_truth(self):
        ch, _ = prepare_observation(self.char())
        ch["current_room"] = "hostel_hallway"
        self.assertIsNone(arrival_attention(ch, {"exits": {"down": "elsewhere"}}))
        self.assertIsNone(counterkeeper_view(ch, "counterkeeper"))
        ch["current_room"] = "neptune_lounge"
        ch["in_cube"] = True
        self.assertIsNone(arrival_attention(ch, {}))
        self.assertIsNone(counterkeeper_view(ch, "counterkeeper"))
        ch["in_cube"] = False
        self.assertIsNone(counterkeeper_view(ch, "unrelated object"))
        ch["extra"].pop("arrival")
        self.assertIsNone(arrival_attention(ch, {}))

    def test_route_commands_have_private_run_routing(self):
        self.assertTrue({"go", "inspect", "offer", "bar", "buy"} <= ROUTE_GAMEPLAY_COMMANDS)

if __name__ == "__main__":
    unittest.main()
