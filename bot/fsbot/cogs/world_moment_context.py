# ============================================================
# FILE META — fsbot/cogs/world_moment_context.py
# Canonical name: WorldMomentContextCog
#
# Version: v0.1.0 — Feather 11: World Moment Context
#
# Scope:
# - Subscribe to world_moment.eligible.
# - Read current durable world facts.
# - Bind those facts into one immutable moment-context event.
# - Publish world_moment.context.
#
# Authority:
# - Owns no world truth.
# - Owns no narrative or semantic interpretation.
# - Persists no gameplay state.
#
# Does NOT:
# - select scenarios
# - activate moments
# - classify danger, mood, urgency, or meaning
# - mutate characters or world authorities
# - send Discord output
# ============================================================

from __future__ import annotations

from typing import Any, Dict

from discord.ext import commands

from fsbot.events import EventResult, create_event
from fsbot.storage import load_json


ERA_PROFILES_FILE = "data/modifiers/era_time_profiles.json"
ASTROLOGY_FILE = "data/astrology/current_snapshot.json"
COMET_FILE = "data/comet/current_state.json"
TEMPORAL_FILE = "data/time/temporal_resolver.json"


def _load_required(path: str) -> Dict[str, Any]:
    state = load_json(path, {})
    if not isinstance(state, dict) or not state:
        raise ValueError(f"required world fact unavailable: {path}")
    return state


class WorldMomentContextCog(commands.Cog):
    """Bind durable world facts to an eligible world moment."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._subscribed = False

    async def cog_load(self) -> None:
        events = getattr(self.bot, "events", None)

        if events is None:
            raise RuntimeError("WorldMomentContextCog requires bot.events")

        events.subscribe(
            "world_moment.eligible",
            self.on_world_moment_eligible,
        )
        self._subscribed = True

    def cog_unload(self) -> None:
        if not self._subscribed:
            return

        events = getattr(self.bot, "events", None)

        if events is not None:
            events.unsubscribe(
                "world_moment.eligible",
                self.on_world_moment_eligible,
            )

        self._subscribed = False

    async def on_world_moment_eligible(
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
            moment_world_time = int(
                payload["boundary_world_time_seconds"]
            )
        except (KeyError, TypeError, ValueError):
            return EventResult.skipped(
                "missing world moment boundary time"
            )

        era_id = str(scope.get("era") or "").strip().lower()

        try:
            era_profiles = _load_required(ERA_PROFILES_FILE)
            astrology = _load_required(ASTROLOGY_FILE)
            comet = _load_required(COMET_FILE)
            temporal = _load_required(TEMPORAL_FILE)

            if not era_id:
                era_id = str(
                    temporal.get("era") or ""
                ).strip().lower()

            profiles = era_profiles.get("profiles")
            if not isinstance(profiles, dict):
                raise ValueError("era profiles unavailable")

            era_profile = profiles.get(era_id)
            if not isinstance(era_profile, dict):
                raise ValueError(
                    f"era profile unavailable: {era_id}"
                )

            placements = astrology.get("placements")
            if not isinstance(placements, dict):
                raise ValueError("astrology placements unavailable")

            sun = placements.get("sun")
            moon = placements.get("moon")

            if not isinstance(sun, dict):
                raise ValueError("sun placement unavailable")

            if not isinstance(moon, dict):
                raise ValueError("moon placement unavailable")

        except (TypeError, ValueError) as exc:
            return EventResult.failed(
                "world moment context unavailable",
                reason=str(exc),
            )

        context_payload = {
            "moment_world_time_seconds": moment_world_time,
            "era": {
                "id": era_id,
                "label": era_profile.get("label"),
                "needs_multiplier":
                    era_profile.get("needs_multiplier"),
                "opportunity_fade_multiplier":
                    era_profile.get(
                        "opportunity_fade_multiplier"
                    ),
                "ambient_intensity_multiplier":
                    era_profile.get(
                        "ambient_intensity_multiplier"
                    ),
                "hard_time_threshold":
                    era_profile.get("hard_time_threshold"),
            },
            "comet": {
                "phase": comet.get("phase"),
                "pressure": comet.get("pressure"),
                "pressure_band": comet.get("pressure_band"),
                "cycle_position": comet.get("cycle_position"),
                "cycle_number": comet.get("cycle_number"),
            },
            "temporal": {
                "effective_multiplier":
                    temporal.get(
                        "effective_temporal_multiplier"
                    ),
            },
            "astrology": {
                "sun": {
                    "sign": sun.get("sign"),
                    "degree_in_sign":
                        sun.get("degree_in_sign"),
                },
                "moon": {
                    "sign": moon.get("sign"),
                    "degree_in_sign":
                        moon.get("degree_in_sign"),
                },
            },
            "source_versions": {
                "era_profiles":
                    era_profiles.get("version"),
                "astrology":
                    astrology.get("version"),
                "comet":
                    comet.get("version"),
                "temporal":
                    temporal.get("version"),
            },
        }

        context_event = create_event(
            event_type="world_moment.context",
            source_system="world_moment_context",
            world_time=moment_world_time,
            scope={
                "era": era_id,
            },
            payload=context_payload,
            causation_id=event.get("event_id"),
            correlation_id=(
                event.get("correlation_id")
                or event.get("event_id")
            ),
        )

        await self.bot.events.publish(context_event)

        return EventResult.delivered(
            "world moment context published",
            era=era_id,
            moment_world_time_seconds=moment_world_time,
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(WorldMomentContextCog(bot))
