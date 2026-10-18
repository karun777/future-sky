"""Fictional records only. No runtime entrypoint or Discord network connection."""
import asyncio
from copy import deepcopy
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock

import discord
from discord.ext import commands
from fsbot.storage import save_json
from fsbot.recovery import RecoveryService, DURATION, begin, record, recovering
from fsbot.cogs.recovery import RecoveryCog
from fsbot.cogs.rebirth import RebirthCog
from fsbot.cogs.combat import CombatCog
from fsbot.cogs.ambient import AmbientCog
from fsbot.cogs.inspection import InspectionCog
from fsbot.events import EventBus, create_event


class Capture:
    def __init__(self, name="recovery"):
        self.author = SimpleNamespace(id="fictional")
        self.command = SimpleNamespace(qualified_name=name)
        self.messages = []

    async def send(self, text):
        self.messages.append(text)


class RecoveryTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.path = self.root / "characters.json"
        self.clock = self.root / "clock.json"
        self.set_time(100)
        self.original = {
            "id": "fictional", "name": "Fictional", "birthdate": "2000-01-01",
            "birth_time": "10:30", "tz_offset_minutes": 480, "current_room": "arena",
            "bag": {"stone": 3, "sword": 1}, "equipped": {"main_hand": "sword", "off_hand": "sword", "chest": "coat"},
            "stats": {"hp": 5, "max_hp": 25, "wisdom": 16}, "credits": 9, "xp": 44,
            "knowledge": ["remember"], "run_channel_id": 123,
            "flags": {"in_combat": False, "quest": "kept"},
            "extra": {"profile": {"class_id": "wizard"}, "arrival": {"opening": {"id": "old"}},
                      "thread_nodes": {"events_completed": ["past"], "active_thread_node": "unfinished"}}}
        self.other = {"name": "Other", "bag": {"gift": 1}, "extra": {}}
        save_json(str(self.path), {"fictional": self.original, "other": self.other})
        self.reload()
        self.ctx = Capture()

    def set_time(self, now):
        save_json(str(self.clock), {"world_time_seconds": now})

    def reload(self):
        storage = SimpleNamespace(characters=json.loads(self.path.read_text()),
            items_db={"sword": {"equip": {"hands_required": 2}}},
            cubes={"private": "untouched"}, lockers={"private": "untouched"})
        self.fail = False
        self.writes = 0
        def save():
            self.writes += 1
            if self.fail:
                raise OSError("injected fixture failure")
            save_json(str(self.path), storage.characters)
        storage.save_characters = save
        self.bot = SimpleNamespace(storage=storage,
            state=SimpleNamespace(WORLD_CLOCK_FILE=str(self.clock), world_time_seconds=999999999), events=EventBus())
        self.service = RecoveryService(self.bot)
        self.cog = RecoveryCog(self.bot)

    def char(self):
        return self.bot.storage.characters["fictional"]

    def start(self, **kwargs):
        return self.service.start("fictional", **kwargs)

    def test_possessions_delivered_once_and_remote_stores_unchanged(self):
        self.start()
        self.reload()
        pod = self.char()["extra"]["pod_delivery"]
        self.assertEqual(pod["items"], {"stone": 3, "sword": 2, "coat": 1})
        self.assertEqual(self.char()["bag"], {})
        self.assertEqual(self.char()["equipped"], {})
        before = deepcopy(self.char())
        self.assertFalse(self.start())
        self.assertEqual(self.char(), before)
        self.assertEqual(self.bot.storage.cubes, {"private": "untouched"})
        self.assertEqual(self.bot.storage.lockers, {"private": "untouched"})
        self.assertEqual(self.bot.storage.characters["other"], self.other)

    def test_same_type_one_handed_items_are_distinct(self):
        self.bot.storage.items_db["sword"]["equip"]["hands_required"] = 1
        self.start()
        self.assertEqual(self.char()["extra"]["pod_delivery"]["items"]["sword"], 3)

    def test_continuity_fields_survive(self):
        self.start()
        for key in ["name", "birthdate", "birth_time", "tz_offset_minutes", "credits", "xp", "knowledge", "run_channel_id"]:
            self.assertEqual(self.char()[key], self.original[key])
        for key in ["profile", "arrival", "thread_nodes"]:
            self.assertEqual(self.char()["extra"][key], self.original["extra"][key])
        self.assertEqual(self.char()["flags"]["quest"], "kept")

    def test_exact_deadline_restart_and_soft_clock_ignored(self):
        self.start()
        self.assertEqual(record(self.char())["started_at"], 100)
        self.set_time(100 + DURATION - 1)
        self.reload()
        self.assertFalse(self.service.refresh("fictional"))
        self.assertEqual(self.char()["stats"]["hp"], 0)
        self.set_time(100 + DURATION)
        self.assertTrue(self.service.refresh("fictional"))
        self.reload()
        self.assertEqual(record(self.char())["stage"], "ready")
        self.assertEqual(self.char()["stats"]["hp"], 25)
        self.assertEqual(self.char()["current_room"], "pod_room")
        self.assertFalse(self.service.refresh("fictional"))

    def test_collection_is_private_local_and_idempotent(self):
        self.start()
        with self.assertRaises(ValueError):
            self.service.collect("fictional")
        self.set_time(100 + DURATION)
        self.service.refresh("fictional")
        self.char()["current_room"] = "elsewhere"
        with self.assertRaises(ValueError):
            self.service.collect("fictional")
        self.char()["current_room"] = "pod_room"
        self.service.collect("fictional")
        self.reload()
        self.assertEqual(self.char()["bag"], {"stone": 3, "sword": 2, "coat": 1})
        before = deepcopy(self.char())
        self.service.collect("fictional")
        self.assertEqual(self.char(), before)
        self.assertEqual(len(self.char()["extra"]["pod_delivery"]["receipts"]), 1)

    def test_failure_start_is_atomic_and_retry_does_not_duplicate(self):
        before = self.path.read_text()
        self.fail = True
        with self.assertRaises(OSError):self.start()
        self.assertEqual(self.char(), self.original)
        self.assertEqual(self.path.read_text(), before)
        self.fail = False
        self.start()
        self.assertEqual(len(self.char()["extra"]["pod_delivery"]["receipts"]), 1)

    def test_failure_completion_and_collection_retry(self):
        self.start()
        self.set_time(100 + DURATION)
        self.fail = True
        with self.assertRaises(OSError):self.service.refresh("fictional")
        self.assertTrue(recovering(self.char()))
        self.fail = False
        self.service.refresh("fictional")
        before = self.path.read_text()
        self.fail = True
        with self.assertRaises(OSError):self.service.collect("fictional")
        self.assertEqual(self.path.read_text(), before)
        self.assertEqual(self.char()["bag"], {})
        self.fail = False
        self.service.collect("fictional")
        self.assertEqual(self.char()["bag"]["stone"], 3)

    def test_brain_boundary_has_no_automatic_wipe_or_completion(self):
        self.start(brain_intact=False)
        self.set_time(100 + 100 * DURATION)
        self.service.refresh("fictional")
        self.assertEqual(record(self.char())["stage"], "brain_review")
        self.assertIsNone(record(self.char())["ready_at"])
        self.assertEqual(self.char()["knowledge"], ["remember"])

    def test_invalid_inventory_and_clock_abort_without_mutation(self):
        for value in [True, -1, "lots"]:
            self.char()["bag"]["stone"] = value
            before = deepcopy(self.char())
            with self.assertRaises(ValueError):self.start()
            self.assertEqual(self.char(), before)
        self.char()["bag"]["stone"] = 3
        self.set_time(-1)
        with self.assertRaises(ValueError):self.start()

    async def test_renewal_actual_confirmation_preserves_date_and_channel(self):
        rebirth = RebirthCog(self.bot)
        await RebirthCog.reincarnate.callback(rebirth, self.ctx)
        self.assertFalse(recovering(self.char()))
        await RebirthCog.reincarnate.callback(rebirth, self.ctx, arg="confirm")
        self.assertTrue(recovering(self.char()))
        self.assertEqual(self.char()["birthdate"], self.original["birthdate"])
        self.assertEqual(self.char()["run_channel_id"], 123)
        self.assertIn("Reanimation has begun", self.ctx.messages[-1])

    async def test_failed_confirmation_never_announces_success(self):
        rebirth = RebirthCog(self.bot)
        await RebirthCog.reincarnate.callback(rebirth, self.ctx)
        self.fail = True
        await RebirthCog.reincarnate.callback(rebirth, self.ctx, arg="confirm")
        self.assertIn("could not be saved", self.ctx.messages[-1])
        self.assertEqual(self.char(), self.original)

    async def test_global_gate_blocks_admin_and_alias_bypasses_then_resumes(self):
        self.start()
        for name in ["go", "awaken", "create_character", "suicide", "equip", "choose", "cube"]:
            self.ctx.command.qualified_name = name
            self.assertFalse(await self.cog.bot_check(self.ctx))
        self.ctx.command.qualified_name = "recovery"
        self.assertTrue(await self.cog.bot_check(self.ctx))
        self.set_time(100 + DURATION)
        self.ctx.command.qualified_name = "awaken"
        self.assertTrue(await self.cog.bot_check(self.ctx))

    async def test_durable_heartbeat_dispatch_and_restart(self):
        self.start()
        self.reload()
        await self.cog.cog_load()
        self.set_time(100 + DURATION)
        await self.bot.events.publish(create_event(event_type="heartbeat.advanced", source_system="clock"))
        self.assertEqual(record(self.char())["stage"], "ready")
        await self.cog.cog_unload()

    async def test_legacy_severance_cannot_erase_progress(self):
        before = deepcopy(self.char())
        rebirth = RebirthCog(self.bot)
        for arg in ["Other Name", "confirm", "confirm"]:
            await RebirthCog.suicide.callback(rebirth, self.ctx, arg=arg)
        self.assertEqual(self.char(), before)

    async def test_combat_lethal_hit_uses_shared_recovery(self):
        await self.combat_hit()
        self.reload()
        self.assertTrue(recovering(self.char()))
        self.assertEqual(record(self.char())["cause"], "combat")
        self.assertEqual(self.char()["extra"]["pod_delivery"]["items"]["coat"], 1)

    async def combat_hit(self, fail=False):
        cog = CombatCog(self.bot)
        st = {"active": True, "engaged": {"fictional"}, "intents": {"fictional": {}}, "pending_join": set()}
        cog._combat_state = lambda room: st
        cog._lock_for_room = lambda room: asyncio.Lock()
        cog._room_members = lambda room: [("fictional", self.char())]
        cog._ensure_character_schema = lambda uid: self.char()
        cog._get_room_enemies_effective = lambda room: {"enemy": {"attack": 100, "name": "Fixture"}}
        cog._send_to_player = AsyncMock()
        cog._broadcast_room = AsyncMock()
        self.fail = fail
        await cog._enemy_step(self.ctx, "arena", "enemy")
        return cog

    async def test_failed_combat_transition_restores_pre_hit_and_publishes_nothing(self):
        with self.assertRaises(OSError):await self.combat_hit(fail=True)
        self.assertEqual(self.char(), self.original)
        self.assertEqual(json.loads(self.path.read_text())["fictional"], self.original)

    async def test_idle_rest_does_not_move_recovering_body(self):
        self.start()
        cog = object.__new__(AmbientCog)
        before = deepcopy(self.char())
        self.assertTrue(await cog._maybe_handle_rest(guild=None, user_id="fictional", char=self.char(), idle_for=99999, now=99999))
        self.assertEqual(self.char(), before)

    async def test_completed_recovery_hands_off_to_w4f4(self):
        self.char()["extra"]["arrival"] = {}
        self.char()["extra"]["thread_nodes"] = {"events_completed": ["past"]}
        self.bot.storage.rooms = {"pod_room": {"exits": {"west": "corridor"}}}
        self.start()
        self.set_time(100 + DURATION)
        self.service.refresh("fictional")
        self.service.collect("fictional")
        class OpeningCapture:
            author = SimpleNamespace(id="fictional")
            messages = []
            async def send(self, content=None, **kwargs):
                self.messages.append((content, kwargs))
        ctx = OpeningCapture()
        cog = InspectionCog(self.bot)
        await InspectionCog.awaken.callback(cog, ctx)
        self.assertIn("You do not recognise them", ctx.messages[-1][1]["embed"].description)
        self.assertEqual(self.char()["bag"]["stone"], 3)
        self.assertEqual(self.char()["extra"]["thread_nodes"]["events_completed"], ["past"])

    def test_second_recovery_keeps_uncollected_delivery_without_duplication(self):
        self.start()
        self.set_time(100 + DURATION)
        self.service.refresh("fictional")
        self.start()
        self.set_time(100 + 2 * DURATION)
        self.service.collect("fictional")
        self.assertEqual(self.char()["bag"], {"stone": 3, "sword": 2, "coat": 1})
        self.assertEqual(len(self.char()["extra"]["pod_delivery"]["receipts"]), 2)

    async def test_status_commands_and_collection_callback(self):
        self.start()
        await RecoveryCog.recovery.callback(self.cog, self.ctx)
        self.assertIn("7.000", self.ctx.messages[-1])
        await RecoveryCog.pod_delivery.callback(self.cog, self.ctx)
        self.assertIn("6 item(s)", self.ctx.messages[-1])
        self.set_time(100 + DURATION)
        await RecoveryCog.recovery.callback(self.cog, self.ctx)
        self.assertIn("Reanimation is complete", self.ctx.messages[-1])
        await RecoveryCog.pod_delivery.callback(self.cog, self.ctx, "collect")
        self.reload()
        self.assertEqual(self.char()["bag"]["stone"], 3)

    async def test_command_registration_and_alias_global_gate(self):
        bot = commands.Bot(command_prefix="!", intents=discord.Intents.none())
        bot.storage, bot.state, bot.events = self.bot.storage, self.bot.state, self.bot.events
        cog = RecoveryCog(bot)
        await bot.add_cog(cog)
        await bot.add_cog(RebirthCog(bot))
        self.assertIsNotNone(bot.get_command("recovery"))
        self.assertIsNotNone(bot.get_command("reincarnate"))
        self.start()
        ctx = Capture()
        ctx.command = SimpleNamespace(qualified_name="go")
        self.assertFalse(await bot.can_run(ctx))
        await bot.close()


if __name__ == "__main__":
    unittest.main()
