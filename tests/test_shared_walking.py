"""Shared navigation race and persistence tests; no live player data."""
import asyncio
from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import AsyncMock
import unittest
from fsbot.cogs.navigation import NavigationCog
from fsbot.cogs.idle_home import IdleHomeCog
from fsbot.idle_home import configure, record


def fixture():
    storage = SimpleNamespace(
        characters={"123": {"name": "Pilot", "current_room": "a",
                            "extra": {}, "bag": {}, "credits": 4},
                    "456": {"name": "Other", "current_room": "c"}},
        rooms={"a": {"title": "A", "description": "Room A", "exits": {"east": "b"}},
               "b": {"title": "B", "description": "Room B", "exits": {"west": "a", "east": "c"}},
               "c": {"title": "C", "exits": {"west": "b"}}},
        items_db={})
    saved = []
    storage.save_characters = lambda: saved.append(deepcopy(storage.characters))
    cogs = {}
    bot = SimpleNamespace(storage=storage, guilds=[], is_ready=lambda: True,
                          get_cog=lambda name: cogs.get(name),
                          presence=SimpleNamespace(get_room_members=lambda room: []),
                          state=SimpleNamespace(resolve_era_for_room=lambda room: "Manzo",
                                                world_time_seconds=123))
    nav = NavigationCog(bot)
    cogs["NavigationCog"] = nav
    return bot, nav, cogs, saved


class SharedWalkingTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.bot, self.nav, self.cogs, self.saved = fixture()

    async def web(self, direction="east", room="a", revision=0):
        return await self.nav.web_walk("123", direction, expected_room=room,
                                      expected_revision=revision)

    async def test_saved_once_before_event_and_other_player_unchanged(self):
        other = deepcopy(self.bot.storage.characters["456"])
        async def publish(event):
            self.assertEqual(self.saved[-1]["123"]["current_room"], "b")
            self.assertEqual(event["payload"]["from_room_id"], "a")
        self.bot.events = SimpleNamespace(publish=AsyncMock(side_effect=publish))
        result = await self.web()
        self.assertTrue(result["ok"])
        self.assertEqual(len(self.saved), 1)
        self.bot.events.publish.assert_awaited_once()
        self.assertEqual(self.bot.storage.characters["456"], other)

    async def test_stale_view_and_return_to_same_room_are_rejected(self):
        self.assertTrue((await self.web())["ok"])
        self.assertFalse((await self.web())["ok"])
        self.assertTrue((await self.web("west", "b", 1))["ok"])
        self.assertFalse((await self.web())["ok"])
        self.assertEqual(len(self.saved), 2)

    async def test_failed_save_rolls_back_and_releases_busy(self):
        def fail():
            raise OSError("fictional disk failure")
        self.bot.storage.save_characters = fail
        with self.assertRaises(OSError):
            await self.web()
        self.assertEqual(self.bot.storage.characters["123"]["current_room"], "a")
        self.assertEqual(self.nav.walk_revision("123"), 0)
        self.assertFalse(self.nav.walking)

    async def test_unknown_exit_target_missing_owner_and_cube_denied(self):
        self.assertFalse((await self.web("north"))["ok"])
        self.bot.storage.rooms["a"]["exits"]["east"] = "missing"
        self.assertFalse((await self.web())["ok"])
        self.bot.storage.rooms["a"]["exits"]["east"] = "b"
        self.bot.storage.characters["123"]["in_cube"] = True
        self.assertFalse((await self.web())["ok"])
        del self.bot.storage.characters["123"]
        self.assertFalse((await self.web())["ok"])
        self.assertEqual(self.saved, [])

    async def test_web_blocks_recovery_combat_choice_and_sequence(self):
        ch = self.bot.storage.characters["123"]
        for extra, flags in [
            ({"recovery": {"stage": "reanimating"}}, {}),
            ({}, {"in_combat": True}),
            ({"thread_nodes": {"active_thread_node": "choice"}}, {})]:
            ch["extra"], ch["flags"] = extra, flags
            self.assertFalse((await self.web())["ok"])
        ch["extra"], ch["flags"] = {}, {}
        self.cogs["SequenceCog"] = SimpleNamespace(running={"123": object()})
        self.assertFalse((await self.web())["ok"])
        self.assertEqual(self.saved, [])

    async def test_overlap_refused_while_departure_waits(self):
        entered, release = asyncio.Event(), asyncio.Event()
        async def pause(*args):
            entered.set()
            await release.wait()
        task = asyncio.create_task(self.nav.walk("123", "east", departure=pause))
        await entered.wait()
        self.assertFalse((await self.web())["ok"])
        release.set()
        self.assertTrue((await task)["ok"])
        self.assertEqual(len(self.saved), 1)

    async def test_latest_record_preserved_after_concurrent_activity(self):
        async def replace(*args):
            updated = deepcopy(self.bot.storage.characters["123"])
            updated["credits"] = 19
            self.bot.storage.characters["123"] = updated
        result = await self.nav.walk("123", "east", departure=replace)
        self.assertTrue(result["ok"])
        self.assertEqual(self.saved[-1]["123"]["credits"], 19)

    async def test_changed_room_exit_or_recovery_during_departure_denies(self):
        for mutation in ("room", "exit", "recovery"):
            self.setUp()
            async def change(*args):
                if mutation == "room":
                    self.bot.storage.characters["123"]["current_room"] = "c"
                elif mutation == "exit":
                    self.bot.storage.rooms["a"]["exits"]["east"] = "c"
                else:
                    self.bot.storage.characters["123"]["extra"]["recovery"] = {"stage": "reanimating"}
            result = await self.nav.walk("123", "east", departure=change)
            self.assertFalse(result["ok"])
            self.assertEqual(self.saved, [])

    async def test_web_input_rearms_idle_and_preserves_source_message(self):
        ch = self.bot.storage.characters["123"]
        self.bot.storage.characters["123"] = configure(ch, 100, idle_seconds=60)
        idle = IdleHomeCog(self.bot)
        idle.now = lambda: 200
        self.cogs["IdleHomeCog"] = idle
        self.assertTrue((await self.web())["ok"])
        self.assertEqual(record(self.bot.storage.characters["123"])["last_input_at"], 200)
        self.assertEqual(record(self.bot.storage.characters["123"])["generation"], 2)

    async def test_failed_activity_save_prevents_web_move(self):
        self.bot.storage.characters["123"] = configure(
            self.bot.storage.characters["123"], 100, idle_seconds=60)
        self.cogs["IdleHomeCog"] = IdleHomeCog(self.bot)
        def fail():
            raise OSError("fictional disk failure")
        self.bot.storage.save_characters = fail
        self.assertFalse((await self.web())["ok"])
        self.assertEqual(self.bot.storage.characters["123"]["current_room"], "a")

    async def test_cancellation_releases_busy_before_commit(self):
        entered = asyncio.Event()
        async def pause(*args):
            entered.set()
            await asyncio.Event().wait()
        task = asyncio.create_task(self.nav.walk("123", "east", departure=pause))
        await entered.wait()
        task.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await task
        self.assertFalse(self.nav.walking)
        self.assertEqual(self.saved, [])
