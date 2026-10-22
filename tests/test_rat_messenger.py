"""Persisted real callbacks; messenger distinct from combat and music custody."""
from copy import deepcopy
from pathlib import Path
import ast
import unittest
import discord
from discord.ext import commands
import test_terrace_delivery as fixture
from fsbot.cogs.rat_messenger import RatMessengerCog
from fsbot.cogs.inspection import InspectionCog
from fsbot.cogs.navigation import NavigationCog
from fsbot.rat_messenger import KEY, tip, guidance, prepare
from fsbot.terrace_delivery import KEY as DELIVERY, APPROACH
from fsbot.cogs.router import ROUTE_GAMEPLAY_COMMANDS

class MessengerTests(unittest.IsolatedAsyncioTestCase):
    setUp = fixture.TerraceDeliveryTests.setUp
    reload = fixture.TerraceDeliveryTests.reload
    char = fixture.TerraceDeliveryTests.char
    performer = fixture.TerraceDeliveryTests.performer
    action = fixture.TerraceDeliveryTests.action
    sequence = fixture.TerraceDeliveryTests.sequence

    async def ready(self):
        self.performer()
        await self.sequence()
        self.char()["current_room"] = "neptune_lounge"
        self.storage.save_characters()
        self.messenger = RatMessengerCog(self.bot)

    async def inspect_counter(self):
        self.ctx.messages.clear()
        await InspectionCog.inspect.callback(InspectionCog(self.bot), self.ctx, item="counterkeeper")

    async def send(self, action="message"):
        self.ctx.messages.clear()
        await RatMessengerCog.rat.callback(RatMessengerCog(self.bot), self.ctx, action=action)

    async def test_counter_tip_persists_then_one_message_arranges_and_reloads(self):
        await self.ready()
        music = deepcopy(self.char()["extra"][DELIVERY])
        other = deepcopy(self.storage.characters["other"])
        rooms = deepcopy(self.storage.rooms)
        await self.inspect_counter()
        self.assertIn("Low down", self.ctx.text())
        self.assertIn("!go south", self.ctx.text())
        self.assertEqual(self.char()["extra"][KEY]["stage"], "tip")
        self.reload()
        nav = NavigationCog(self.bot)
        registry = commands.Bot(command_prefix="!", intents=discord.Intents.none())
        await registry.add_cog(nav)
        self.addAsyncCleanup(registry.close)
        await NavigationCog.go.callback(nav, self.ctx, "inside")
        await NavigationCog.go.callback(nav, self.ctx, "south")
        self.assertEqual(self.char()["current_room"], APPROACH)
        self.assertIn("warm conduit", self.ctx.text())
        await self.send()
        self.assertIn("I’ll meet you here", self.ctx.text())
        self.reload()
        self.assertEqual(self.char()["extra"][KEY]["meeting"]["status"], "arranged")
        before = self.path.read_bytes()
        await self.send()
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(self.char()["extra"][DELIVERY], music)
        self.assertEqual(self.storage.characters["other"], other)
        self.assertEqual(self.storage.rooms, rooms)

    async def test_tip_save_failure_rolls_back_and_retry(self):
        await self.ready()
        # Settle the separate performance-tab transaction before testing tip failure.
        from fsbot.performance_tab import claim_tab
        claim_tab(self.storage, self.uid)
        before = self.path.read_bytes()
        self.storage.fail_next = True
        await self.inspect_counter()
        self.assertIn("could not be remembered", self.ctx.text())
        self.assertNotIn(KEY, self.char()["extra"])
        self.assertEqual(self.path.read_bytes(), before)
        await self.inspect_counter()
        self.assertIn("Low down", self.ctx.text())

    async def test_message_failure_never_announces_success(self):
        await self.ready()
        await self.inspect_counter()
        self.char()["current_room"] = APPROACH
        self.storage.save_characters()
        before = self.path.read_bytes()
        self.storage.fail_next = True
        await self.send()
        self.assertNotIn("embed", self.ctx.messages[-1])
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(self.char()["extra"][KEY]["stage"], "tip")
        await self.send()
        self.assertEqual(self.char()["extra"][KEY]["stage"], "arranged")

    async def test_location_tip_and_body_gates(self):
        await self.ready()
        await self.send()
        self.assertIn("Stardock", self.ctx.text())
        self.char()["current_room"] = APPROACH
        await self.send()
        self.assertIn("no lead", self.ctx.text())
        self.char()["current_room"] = "neptune_lounge"
        await self.inspect_counter()
        self.char()["current_room"] = APPROACH
        for field, value in [("in_cube", True), ("extra", dict(self.char()["extra"], recovery={"stage":"reanimating"}))]:
            original = deepcopy(self.char())
            self.char()[field] = value
            before = deepcopy(self.char())
            await self.send()
            self.assertNotIn("embed", self.ctx.messages[-1])
            self.assertEqual(self.char(), before)
            self.storage.characters[self.uid] = original

    async def test_no_tip_before_delivery_and_corrupt_state_fails_closed(self):
        self.performer("neptune_lounge")
        original = deepcopy(self.char())
        updated, text = tip(self.char())
        self.assertEqual(updated, original)
        self.assertIsNone(text)
        await self.ready()
        self.char()["extra"][KEY] = {"version":1,"stage":"arranged"}
        before = deepcopy(self.char())
        with self.assertRaises(ValueError):
            tip(self.char())
        self.assertEqual(self.char(), before)

    async def test_inspect_rat_optional_and_registration(self):
        await self.ready()
        await self.inspect_counter()
        self.char()["current_room"] = APPROACH
        self.assertTrue(await self.messenger.inspect_target(self.ctx, "rat"))
        self.assertIn("warm conduit", self.ctx.text())
        self.assertEqual(self.char()["extra"][KEY]["stage"], "tip")
        registry = commands.Bot(command_prefix="!", intents=discord.Intents.none())
        await registry.add_cog(self.messenger)
        self.addAsyncCleanup(registry.close)
        self.assertIsNotNone(registry.get_command("rat"))
        self.assertIn("rat", ROUTE_GAMEPLAY_COMMANDS)
        tree=ast.parse((Path(__file__).resolve().parents[1]/"bot/run_bot.py").read_text())
        extensions=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=="EXTENSIONS" for t in n.targets))
        self.assertIn("fsbot.cogs.rat_messenger", extensions)
