"""Clock -> Comet -> Resolver -> next tick, entirely in temporary files."""
import asyncio
from copy import deepcopy
import json
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import os
import unittest
from unittest.mock import patch

from fsbot import state as state_module
from fsbot.state import GameState
from fsbot.events import EventBus, create_event
from fsbot.cogs.comet_cycle import CometCycleCog, CYCLE_DURATION_SECONDS
from fsbot.cogs.temporal_resolver import TemporalResolverCog
from fsbot.storage import save_json


class TemporalNextTickTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        # Relative production paths must resolve only into this temporary world.
        self.temp = TemporaryDirectory(prefix="futuresky-time-loop-")
        self.addCleanup(self.temp.cleanup)
        self.old_cwd = Path.cwd()
        self.addCleanup(os.chdir, self.old_cwd)
        self.root = Path(self.temp.name)
        for name in ["data/time", "data/comet", "data/modifiers"]:
            (self.root / name).mkdir(parents=True, exist_ok=True)
        source = Path(__file__).resolve().parents[1] / "data/modifiers/era_time_profiles.json"
        shutil.copyfile(source, self.root / "data/modifiers/era_time_profiles.json")
        os.chdir(self.root)

    def read(self, name):
        return json.loads((self.root / name).read_text())

    async def prime(self, start):
        save_json("data/time/world_clock.json",
                  {"version": "v1", "world_time_seconds": start})
        self.bus = EventBus()
        self.clock = GameState(SimpleNamespace(), events=self.bus)
        bot = SimpleNamespace(state=self.clock, events=self.bus)
        self.comet = CometCycleCog(bot)
        self.resolver = TemporalResolverCog(bot)
        # Same relative order as the production loader; unrelated cogs omitted.
        await self.comet.cog_load()
        await self.resolver.cog_load()
        await self.bus.publish(create_event(
            event_type="heartbeat.advanced", source_system="fixture_seed",
            world_time=start, scope={"era": "manzo"},
            payload={"world_time_seconds": start}))
        self.heartbeats = []
        self.resolutions = []
        self.snapshots = []

        async def capture_heartbeat(event):
            self.heartbeats.append(deepcopy(event))
            self.snapshots.append({
                "clock": self.read("data/time/world_clock.json"),
                "comet": self.read("data/comet/current_state.json"),
                "resolver": self.read("data/time/temporal_resolver.json"),
            })

        async def capture_resolution(event):
            self.resolutions.append(deepcopy(event))

        self.bus.subscribe("heartbeat.advanced", capture_heartbeat)
        self.bus.subscribe("temporal.resolved", capture_resolution)

    async def run_two_ticks(self):
        instants = iter([1000.0, 1060.0, 1120.0])
        sleeps = 0

        async def controlled_sleep(_delay):
            nonlocal sleeps
            sleeps += 1
            # Initial jitter + between-tick sleep are skipped; stop after tick 2.
            if sleeps == 3:
                raise asyncio.CancelledError()

        with patch.object(state_module, "time",
                          SimpleNamespace(time=lambda: next(instants))), \
             patch.object(state_module, "asyncio",
                          SimpleNamespace(sleep=controlled_sleep)):
            with self.assertRaises(asyncio.CancelledError):
                await self.clock._heartbeat_loop(interval_seconds=60)

    async def assert_transition(self, start, old_rate, new_rate, phase,
                                first_increment, second_increment):
        await self.prime(start)
        self.assertEqual(self.clock.get_resolved_temporal_state()
                         ["effective_temporal_multiplier"], old_rate)
        await self.run_two_ticks()
        self.assertEqual(len(self.heartbeats), 2)
        first, second = self.heartbeats
        self.assertEqual(first["payload"]["effective_time_multiplier"], old_rate)
        self.assertEqual(first["payload"]["era_advanced_seconds"], first_increment)
        self.assertEqual(first["occurred_at_world_time"], start + first_increment)
        self.assertEqual(second["payload"]["effective_time_multiplier"], new_rate)
        self.assertEqual(second["payload"]["era_advanced_seconds"], second_increment)
        self.assertEqual(second["payload"]["previous_world_time_seconds"],
                         start + first_increment)
        self.assertEqual(second["occurred_at_world_time"],
                         start + first_increment + second_increment)
        for event, snapshot in zip(self.heartbeats, self.snapshots):
            world_time = event["occurred_at_world_time"]
            self.assertEqual(event["payload"]["real_elapsed_seconds"], 60)
            self.assertEqual(snapshot["clock"]["world_time_seconds"], world_time)
            self.assertEqual(snapshot["comet"]["world_time_seconds"], world_time)
            self.assertEqual(snapshot["comet"]["phase"], phase)
            self.assertEqual(snapshot["resolver"]["resolved_at_world_time_seconds"],
                             world_time)
            self.assertEqual(snapshot["resolver"]["effective_temporal_multiplier"],
                             new_rate)
        self.assertEqual(len(self.resolutions), 1)
        self.assertEqual(self.resolutions[0]["causation_id"], first["event_id"])
        # Re-read persisted result in a fresh clock object, not cached resolver data.
        restored = GameState(SimpleNamespace())
        self.assertEqual(restored.world_time_seconds,
                         start + first_increment + second_increment)
        self.assertEqual(restored.get_resolved_temporal_state()
                         ["effective_temporal_multiplier"], new_rate)
        # A later resolver update never rewrites the earlier event's rate.
        self.assertEqual(first["payload"]["effective_time_multiplier"], old_rate)

    async def test_approaching_phase_accelerates_only_following_tick(self):
        start = CYCLE_DURATION_SECONDS // 4 - 1800
        await self.assert_transition(start, 60.0, 66.0, "approaching", 3600, 3960)

    async def test_cycle_wrap_slows_only_following_tick(self):
        start = CYCLE_DURATION_SECONDS - 1800
        await self.assert_transition(start, 63.0, 60.0, "dormant", 3780, 3600)
        self.assertEqual(self.read("data/comet/current_state.json")["cycle_number"], 1)

    async def test_clock_save_failure_does_not_publish_undurable_tick(self):
        start = CYCLE_DURATION_SECONDS // 4 - 1800
        await self.prime(start)
        save = self.clock.save_world_clock
        calls = 0

        def fail_first_save():
            nonlocal calls
            calls += 1
            return False if calls == 1 else save()

        with patch.object(self.clock, "save_world_clock", side_effect=fail_first_save):
            await self.run_two_ticks()
        # First tick advanced memory but failed durability and emitted no event;
        # the second still used the previously persisted 60x resolver state.
        self.assertEqual(len(self.heartbeats), 1)
        event = self.heartbeats[0]
        self.assertEqual(event["payload"]["tick"], 2)
        self.assertEqual(event["payload"]["effective_time_multiplier"], 60.0)
        self.assertEqual(event["payload"]["era_advanced_seconds"], 3600)
        self.assertEqual(event["occurred_at_world_time"], start + 7200)
        self.assertEqual(self.read("data/time/world_clock.json")
                         ["world_time_seconds"], start + 7200)
        self.assertEqual(self.read("data/time/temporal_resolver.json")
                         ["effective_temporal_multiplier"], 66.0)
        self.assertEqual(len(self.resolutions), 1)


if __name__ == "__main__":
    unittest.main()
