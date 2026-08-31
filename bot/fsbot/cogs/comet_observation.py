# ============================================================
# FILE META — fsbot/cogs/comet_observation.py
# Canonical name: CometObservationCog
#
# Version: v0.1.0 — Feather 18: First Observation Fact
#
# Scope:
# - Subscribe to comet.state_changed.
# - Observe the canonical comet state transition.
# - Publish one neutral observation.comet_state fact.
#
# Authority:
# - AUTHORITATIVE only for the fact that this observer observed
#   a canonical comet state transition.
#
# Does NOT:
# - own or mutate comet state
# - read comet persistence directly
# - persist a separate observation store
# - interpret meaning or narrative significance
# - score signals
# - detect convergence
# - activate opportunities or scenarios
# - send Discord output
# ============================================================

from __future__ import annotations

from typing import Any, Dict

from discord.ext import commands

from fsbot.events import EventResult, create_event


OBSERVATION_VERSION = "comet_observation_v0"


class CometObservationCog(commands.Cog):
    """Neutral observer of canonical comet state-change facts."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._subscribed = False

    async def cog_load(self) -> None:
        events = getattr(self.bot, "events", None)
        if events is None:
            raise RuntimeError(
                "CometObservationCog requires bot.events"
            )

        events.subscribe(
            "comet.state_changed",
            self.on_comet_state_changed,
        )
        self._subscribed = True

    def cog_unload(self) -> None:
        if not self._subscribed:
            return

        events = getattr(self.bot, "events", None)
        if events is not None:
            events.unsubscribe(
                "comet.state_changed",
                self.on_comet_state_changed,
            )

        self._subscribed = False

    async def on_comet_state_changed(
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

        current_state = payload.get("current_state")
        if not isinstance(current_state, dict):
            return EventResult.skipped(
                "canonical comet state unavailable"
            )

        changed_fields = payload.get("changed_fields")
        if not isinstance(changed_fields, list):
            changed_fields = []

        try:
            world_time = int(
                event.get("occurred_at_world_time", 0)
            )
        except (TypeError, ValueError):
            return EventResult.failed(
                "invalid comet observation world time"
            )

        observation_event = create_event(
            event_type="observation.comet_state",
            source_system="comet_observation",
            world_time=world_time,
            scope=scope,
            payload={
                "observed_event_id": event.get("event_id"),
                "observed_event_type": event.get("event_type"),
                "phase": current_state.get("phase"),
                "pressure": current_state.get("pressure"),
                "pressure_band": current_state.get(
                    "pressure_band"
                ),
                "temporal_modifier": current_state.get(
                    "temporal_modifier"
                ),
                "temporal_band": current_state.get(
                    "temporal_band"
                ),
                "changed_fields": list(changed_fields),
                "observation_version": OBSERVATION_VERSION,
            },
            causation_id=event.get("event_id"),
            correlation_id=(
                event.get("correlation_id")
                or event.get("event_id")
            ),
        )

        try:
            await self.bot.events.publish(observation_event)
        except Exception as exc:
            return EventResult.failed(
                "comet observation publication failed",
                error_type=type(exc).__name__,
                observation_event_id=observation_event[
                    "event_id"
                ],
            )

        return EventResult.applied(
            "canonical comet state observed",
            observation_event_id=observation_event["event_id"],
            observed_event_id=event.get("event_id"),
            phase=current_state.get("phase"),
            pressure_band=current_state.get("pressure_band"),
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(CometObservationCog(bot))
