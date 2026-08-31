# ============================================================
# FILE META — fsbot/cogs/world_moments.py
# Canonical name: WorldMomentsCog
#
# Version: v0.2.0 — Feather 10: World Moment Fact
#
# Scope:
# - Subscribe to heartbeat.advanced.
# - Detect six-world-hour boundaries crossed by world time.
# - Publish one immutable world_moment.eligible fact per crossed boundary.
# - Return observable EventResult data to the Flight Recorder.
#
# Authority:
# - Owns no gameplay state.
# - Owns no narrative meaning.
# - Reads immutable heartbeat facts only.
#
# Does NOT:
# - select or activate scenarios
# - inspect astrology or comet pressure
# - mutate characters or world state
# - send Discord output
# - decide whether an eligible moment is important
# ============================================================

from __future__ import annotations

from typing import Any, Dict, Optional

from discord.ext import commands

from fsbot.events import EventResult, create_event


WORLD_MOMENT_INTERVAL_HOURS = 6
SECONDS_PER_WORLD_HOUR = 60 * 60
WORLD_MOMENT_INTERVAL_SECONDS = (
    WORLD_MOMENT_INTERVAL_HOURS * SECONDS_PER_WORLD_HOUR
)


class WorldMomentsCog(commands.Cog):
    """Publish deterministic world-moment boundary facts."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._subscribed = False
        self._last_world_time_seconds: Optional[int] = None

    async def cog_load(self) -> None:
        events = getattr(self.bot, "events", None)
        if events is None:
            raise RuntimeError("WorldMomentsCog requires bot.events")

        events.subscribe(
            "heartbeat.advanced",
            self.on_heartbeat_advanced,
        )
        self._subscribed = True

    def cog_unload(self) -> None:
        if not self._subscribed:
            return

        events = getattr(self.bot, "events", None)
        if events is not None:
            events.unsubscribe(
                "heartbeat.advanced",
                self.on_heartbeat_advanced,
            )

        self._subscribed = False

    async def on_heartbeat_advanced(
        self,
        event: Dict[str, Any],
    ) -> EventResult:
        payload = (
            event.get("payload")
            if isinstance(event.get("payload"), dict)
            else {}
        )
        scope = (
            event.get("scope")
            if isinstance(event.get("scope"), dict)
            else {}
        )

        try:
            current_world_time = int(payload["world_time_seconds"])
        except (KeyError, TypeError, ValueError):
            return EventResult.skipped("missing world_time_seconds")

        if current_world_time < 0:
            return EventResult.skipped("invalid world_time_seconds")

        previous_world_time = self._last_world_time_seconds

        # Establish an observation baseline on first heartbeat after load.
        if previous_world_time is None:
            self._last_world_time_seconds = current_world_time
            return EventResult.ok(
                "world moment baseline established",
                world_time_seconds=current_world_time,
            )

        if current_world_time <= previous_world_time:
            self._last_world_time_seconds = current_world_time
            return EventResult.skipped(
                "world time did not advance",
                previous_world_time_seconds=previous_world_time,
                world_time_seconds=current_world_time,
            )

        first_boundary = (
            (previous_world_time // WORLD_MOMENT_INTERVAL_SECONDS) + 1
        ) * WORLD_MOMENT_INTERVAL_SECONDS

        published = 0
        boundary_time = first_boundary

        while boundary_time <= current_world_time:
            boundary_world_hour = (
                boundary_time // SECONDS_PER_WORLD_HOUR
            )

            moment_event = create_event(
                event_type="world_moment.eligible",
                source_system="world_moments",
                world_time=boundary_time,
                scope={
                    "era": scope.get("era"),
                },
                payload={
                    "boundary_interval_world_hours":
                        WORLD_MOMENT_INTERVAL_HOURS,
                    "boundary_world_hour":
                        boundary_world_hour,
                    "boundary_world_time_seconds":
                        boundary_time,
                    "observed_world_time_seconds":
                        current_world_time,
                },
                causation_id=event.get("event_id"),
                correlation_id=event.get("correlation_id"),
            )

            await self.bot.events.publish(moment_event)

            published += 1
            boundary_time += WORLD_MOMENT_INTERVAL_SECONDS

        self._last_world_time_seconds = current_world_time

        if published == 0:
            return EventResult.no_match(
                "no world moment boundary crossed",
                previous_world_time_seconds=previous_world_time,
                world_time_seconds=current_world_time,
            )

        return EventResult.matched(
            "world moment boundary crossed",
            moments_published=published,
            previous_world_time_seconds=previous_world_time,
            world_time_seconds=current_world_time,
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(WorldMomentsCog(bot))
