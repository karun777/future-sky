"""Real Discord callbacks and production JSON saves on fictional temp records."""
import ast
from copy import deepcopy
from pathlib import Path
from unittest.mock import AsyncMock
import unittest
import discord
from discord.ext import commands
import test_display
from fsbot.cogs.terrace import TerraceCog
from fsbot.cogs.navigation import NavigationCog
from fsbot.cogs.core import CoreCog
from fsbot.cogs.router import ROUTE_GAMEPLAY_COMMANDS
from fsbot.terrace_delivery import (
    KEY, ROOM, APPROACH, TerraceError, register_room, prepare, inventory_lines,
    state_of, secured_inventory_lines,
)
from fsbot.pod_opening import prepare_observation
from fsbot.recovery import begin, complete, DURATION, RecoveryService
from fsbot.item_transfer import transfer, TransferError

PASSAGE = ("attend", "sky", "inspect package", "take package", "open package",
           "inspect box", "unlock box", "open box", "inspect usb", "take usb")


class TerraceDeliveryTests(unittest.IsolatedAsyncioTestCase):
    setUp = test_display.DisplayTests.setUp
    char = test_display.DisplayTests.char
    inspect = test_display.DisplayTests.inspect
    look = test_display.DisplayTests.look

    def reload(self):
        test_display.DisplayTests.reload(self)
        register_room(self.storage.rooms)
        self.terrace = TerraceCog(self.bot)
        previous = self.bot.get_cog
        self.bot.get_cog = lambda name: self.terrace if name == "TerraceCog" else previous(name)
        self.bot.presence.get_room_members = lambda room: []
        self.bot.state.play_music = AsyncMock()
        self.bot.state.resolve_era_for_room = lambda room: "manzo"

    def performer(self, room=ROOM):
        ch, _ = prepare_observation(self.char())
        ch["extra"]["arrival"]["opening"]["discoveries"] = ["booking", "chain"]
        ch["current_room"] = room
        self.storage.characters[self.uid] = ch
        self.storage.save_characters()

    async def action(self, action):
        self.ctx.messages.clear()
        await TerraceCog.terrace.callback(self.terrace, self.ctx, action=action)
        return self.ctx.text()

    async def sequence(self, actions=PASSAGE):
        for action in actions:
            await self.action(action)

    async def test_walk_actual_navigation_then_delivery_reload_and_inventory(self):
        self.performer("lounge_main_floor")
        nav = NavigationCog(self.bot)
        registry = commands.Bot(command_prefix="!", intents=discord.Intents.none())
        await registry.add_cog(nav)
        self.addAsyncCleanup(registry.close)
        self.bot.events = type("Events", (), {"publish": AsyncMock()})()
        for direction, room in [("south", APPROACH), ("out", ROOM)]:
            await NavigationCog.go.callback(nav, self.ctx, direction)
            self.assertEqual(self.char()["current_room"], room)
        self.assertIn("!terrace attend", self.ctx.text())
        other = deepcopy(self.storage.characters["other"])
        for action in PASSAGE:
            await self.action(action)
            self.assertIn("embed", self.ctx.messages[-1], action)
            self.reload()
        state = state_of(self.char())
        self.assertEqual(state["stage"], "usb_collected")
        self.assertEqual(state["objects"]["usb"]["holder"], self.uid)
        self.assertEqual(self.storage.characters["other"], other)
        self.ctx.messages.clear()
        await CoreCog.inventory.callback(CoreCog(self.bot), self.ctx)
        self.assertIn("USB marked tunes", self.ctx.text())
        self.assertEqual(self.char()["bag"], self.original["bag"])

    async def test_inspection_bridge_hides_unopened_contents(self):
        self.performer()
        await self.sequence(("attend", "sky"))
        await self.inspect("package")
        self.assertIn("label reads", self.ctx.text())
        self.assertNotIn("antique", self.ctx.text())
        self.assertNotIn("USB", self.ctx.text())
        await self.sequence(("take package", "open package"))
        await self.inspect("box")
        self.assertIn("key at your neck", self.ctx.text())
        await self.inspect("usb")
        self.assertIn("locked", self.ctx.text())
        self.assertNotIn("label reads **tunes**", self.ctx.text())
        await self.sequence(("unlock box", "open box"))
        await self.inspect("tunes")
        self.assertIn("unexamined", str(state_of(self.char())))
        self.assertIn("label reads **tunes**", self.ctx.text())

    async def test_each_failed_save_rolls_back_then_retries_once(self):
        self.performer()
        for action in PASSAGE:
            with self.subTest(action=action):
                before = self.path.read_bytes()
                memory = deepcopy(self.storage.characters)
                self.storage.fail_next = True
                text = await self.action(action)
                self.assertIn("could not remember", text)
                self.assertNotIn("embed", self.ctx.messages[-1])
                self.assertEqual(self.path.read_bytes(), before)
                self.assertEqual(self.storage.characters, memory)
                self.reload()
                await self.action(action)
                self.assertIn("embed", self.ctx.messages[-1])
        history = state_of(self.char())["history"]
        self.assertEqual(sum(f["kind"] == "package.landed" for f in history), 1)
        self.assertEqual(sum(f["kind"] == "usb.collected" for f in history), 1)

    async def test_replay_and_reentry_cannot_duplicate(self):
        self.performer()
        await self.sequence()
        before = self.path.read_bytes()
        for action in ("attend", "sky", "take package", "open package", "unlock box",
                       "open box", "take usb", "inventory", ""):
            await self.action(action)
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(len(state_of(self.char())["objects"]), 3)

    async def test_non_performance_arrivals_and_missing_attention(self):
        self.performer()
        self.assertIn("First linger", await self.action("sky"))
        self.assertIsNone(state_of(self.char()))
        self.char()["extra"]["arrival"]["performance_booking"] = False
        self.storage.save_characters()
        before = self.path.read_bytes()
        self.assertIn("No performance delivery", await self.action("attend"))
        self.assertEqual(self.path.read_bytes(), before)
        await self.look()
        self.assertIn("enjoy the view", self.ctx.text())

    async def test_no_discovered_booking_no_delivery(self):
        self.performer()
        self.char()["extra"]["arrival"]["opening"]["discoveries"] = []
        before = deepcopy(self.char())
        self.assertIn("No performance delivery", await self.action("attend"))
        self.assertEqual(self.char(), before)

    async def test_location_cube_and_recovering_gates(self):
        self.performer(APPROACH)
        self.assertIn("begins at", await self.action("attend"))
        self.char()["current_room"] = ROOM
        self.char()["in_cube"] = True
        self.assertIn("Return from the Cube", await self.action("attend"))
        self.char()["in_cube"] = False
        self.char()["extra"]["recovery"] = {"stage": "reanimating"}
        self.assertIn("body is in recovery", await self.action("attend"))

    async def test_departure_before_pickup_and_carried_opening_elsewhere(self):
        self.performer()
        await self.sequence(("attend", "sky"))
        self.char()["current_room"] = APPROACH
        self.assertIn("begins at", await self.action("take package"))
        self.char()["current_room"] = ROOM
        await self.action("take package")
        self.char()["current_room"] = "lounge_main_floor"
        self.assertIn("antique locked box", await self.action("open package"))

    async def test_pickup_need_not_read_address_but_lock_needs_neck_key(self):
        self.performer()
        await self.sequence(("attend", "sky", "take package", "open package"))
        self.assertNotIn("package.address_read", state_of(self.char())["discoveries"])
        self.char()["extra"].pop("arrival")
        before = deepcopy(self.char())
        self.assertIn("No matching neck key", await self.action("unlock box"))
        self.assertEqual(self.char(), before)

    async def test_no_spoilers_in_address_or_inventory(self):
        self.performer()
        await self.sequence()
        text = await self.action("inventory")
        text += await self.action("inspect package")
        for hidden in ["Queen", "Vitriol", "future_condition", "provisional", "lineage"]:
            self.assertNotIn(hidden, text)
        self.assertIn(self.char()["name"], text)

    async def test_corrupt_or_other_owned_state_fails_closed(self):
        self.performer()
        self.char()["extra"][KEY] = {"version": 1, "stage": "open"}
        before = deepcopy(self.char())
        self.assertIn("unavailable", await self.action("take usb"))
        self.assertEqual(self.char(), before)
        self.char()["extra"].pop(KEY)
        await self.action("attend")
        self.char()["extra"][KEY]["owner"] = "another-fixture"
        self.assertIn("another traveller", await self.action("sky"))

    async def test_private_instances_do_not_change_rooms_or_other_character(self):
        self.performer()
        rooms = deepcopy(self.storage.rooms)
        other = deepcopy(self.storage.characters["other"])
        await self.sequence()
        self.assertEqual(self.storage.rooms, rooms)
        self.assertEqual(self.storage.characters["other"], other)
        with self.assertRaises(TransferError):
            transfer(self.char(), self.storage.rooms[ROOM], self.storage.items_db, "tunes", "drop")

    async def test_recovery_secures_and_pod_collection_restores_identity(self):
        self.performer()
        await self.sequence()
        original_id = state_of(self.char())["objects"]["usb"]["instance_id"]
        dying = begin(self.char(), 100, self.storage.items_db, cause="fictional-test")
        self.assertEqual(inventory_lines(dying), [])
        self.assertEqual(len(secured_inventory_lines(dying)), 2)
        self.assertEqual(state_of(dying)["objects"]["usb"]["holder"], "pod_delivery")
        ready = complete(dying, 100 + DURATION)
        self.storage.characters[self.uid] = ready
        self.storage.save_characters()
        self.assertIn("secured in the pod", await self.action("inspect usb"))
        before = deepcopy(self.storage.characters)
        disk = self.path.read_bytes()
        self.storage.fail_next = True
        with self.assertRaises(OSError):
            RecoveryService(self.bot).collect(self.uid)
        self.assertEqual(self.storage.characters, before)
        self.assertEqual(self.path.read_bytes(), disk)
        RecoveryService(self.bot).collect(self.uid)
        self.assertEqual(state_of(self.char())["objects"]["usb"]["instance_id"], original_id)
        self.assertEqual(state_of(self.char())["objects"]["usb"]["holder"], self.uid)
        self.assertIn("USB marked tunes", inventory_lines(self.char()))
        before = self.path.read_bytes()
        RecoveryService(self.bot).collect(self.uid)
        self.assertEqual(self.path.read_bytes(), before)

    def test_room_registration_preserves_all_existing_content_and_is_idempotent(self):
        rooms = deepcopy(self.storage.rooms)
        before = deepcopy(rooms)
        register_room(rooms)
        self.assertEqual(rooms, before)
        for mutation in ("exit", "id"):
            collision = {APPROACH: {"exits": {}}}
            if mutation == "exit":
                collision[APPROACH]["exits"]["out"] = "someone_else"
            else:
                collision[ROOM] = {"title": "Unrelated"}
            original = deepcopy(collision)
            with self.assertRaises(TerraceError):
                register_room(collision)
            self.assertEqual(collision, original)

    async def test_extension_registration_routing_and_safe_generic_inspection(self):
        self.assertIn("terrace", ROUTE_GAMEPLAY_COMMANDS)
        registry = commands.Bot(command_prefix="!", intents=discord.Intents.none())
        await registry.add_cog(self.terrace)
        self.addAsyncCleanup(registry.close)
        self.assertIsNotNone(registry.get_command("terrace"))
        path = Path(__file__).resolve().parents[1] / "bot/run_bot.py"
        tree = ast.parse(path.read_text())
        extensions = next(ast.literal_eval(node.value) for node in tree.body
                          if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "EXTENSIONS" for t in node.targets))
        self.assertIn("fsbot.cogs.terrace", extensions)
        self.assertFalse(await self.terrace.inspect_target(self.ctx, "keepsake"))

    def test_pure_transition_preserves_unrelated_namespaces(self):
        self.performer()
        original = deepcopy(self.char())
        updated, view = prepare(self.char(), self.uid, "attend")
        self.assertEqual(self.char(), original)
        self.assertEqual(updated["extra"]["hud"], original["extra"]["hud"])
        self.assertEqual(updated["bag"], original["bag"])


if __name__ == "__main__":
    unittest.main()
