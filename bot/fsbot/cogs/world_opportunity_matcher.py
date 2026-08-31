# ============================================================
# FILE META — fsbot/cogs/world_opportunity_matcher.py
# Canonical name: WorldOpportunityMatcherCog
#
# Version: v0.1.0 — Feather 12: World Opportunity Matcher
#
# Scope:
# - Subscribe to world_moment.context.
# - Read authored world opportunity definitions.
# - Deterministically match context against requirements.
# - Publish world_opportunity.eligible for each match.
#
# Authority:
# - Owns no world truth.
# - Owns no scenario runtime state.
# - Persists no gameplay state.
#
# Does NOT:
# - activate scenarios
# - choose among multiple matches
# - mutate characters or world authorities
# - send Discord output
# - invent narrative meaning
# ============================================================

from __future__ import annotations

from typing import Any, Dict, List

from discord.ext import commands

from fsbot.events import EventResult, create_event
from fsbot.storage import load_json


CATALOGUE_FILE = "data/world_opportunities/catalogue.json"


def _normalise_list(value: Any) -> List[str]:
    if isinstance(value, list):
        return [
            str(item).strip().lower()
            for item in value
            if str(item).strip()
        ]

    if value is None:
        return []

    text = str(value).strip().lower()
    return [text] if text else []


def _matches(opportunity: Dict[str, Any], context: Dict[str, Any]) -> bool:
    requirements = opportunity.get("requirements")

    if not isinstance(requirements, dict):
        return True

    era = context.get("era")
    comet = context.get("comet")

    era_id = ""
    pressure_band = ""

    if isinstance(era, dict):
        era_id = str(era.get("id") or "").strip().lower()

    if isinstance(comet, dict):
        pressure_band = str(
            comet.get("pressure_band") or ""
        ).strip().lower()

    allowed_eras = _normalise_list(requirements.get("era"))
    if allowed_eras and era_id not in allowed_eras:
        return False

    allowed_pressure_bands = _normalise_list(
        requirements.get("comet_pressure_band")
    )
    if (
        allowed_pressure_bands
        and pressure_band not in allowed_pressure_bands
    ):
        return False

    return True


class WorldOpportunityMatcherCog(commands.Cog):
    """Match authored opportunities against immutable moment context."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._subscribed = False

    async def cog_load(self) -> None:
        events = getattr(self.bot, "events", None)

        if events is None:
            raise RuntimeError(
                "WorldOpportunityMatcherCog requires bot.events"
            )

        events.subscribe(
            "world_moment.context",
            self.on_world_moment_context,
        )
        self._subscribed = True

    def cog_unload(self) -> None:
        if not self._subscribed:
            return

        events = getattr(self.bot, "events", None)

        if events is not None:
            events.unsubscribe(
                "world_moment.context",
                self.on_world_moment_context,
            )

        self._subscribed = False

    async def on_world_moment_context(
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

        catalogue = load_json(CATALOGUE_FILE, {})

        if not isinstance(catalogue, dict):
            return EventResult.failed(
                "world opportunity catalogue unavailable"
            )

        opportunities = catalogue.get("opportunities")

        if not isinstance(opportunities, list):
            return EventResult.failed(
                "world opportunity catalogue invalid"
            )

        matched_ids: List[str] = []

        for raw in opportunities:
            if not isinstance(raw, dict):
                continue

            if raw.get("enabled") is False:
                continue

            opportunity_id = str(
                raw.get("id") or ""
            ).strip()

            if not opportunity_id:
                continue

            if not _matches(raw, payload):
                continue

            eligible_event = create_event(
                event_type="world_opportunity.eligible",
                source_system="world_opportunity_matcher",
                world_time=int(
                    payload.get(
                        "moment_world_time_seconds",
                        event.get("occurred_at_world_time", 0),
                    )
                ),
                scope={
                    "era": scope.get("era"),
                    "opportunity_id": opportunity_id,
                },
                payload={
                    "opportunity_id": opportunity_id,
                    "catalogue_version":
                        catalogue.get("version"),
                    "requirements":
                        raw.get("requirements", {}),
                },
                causation_id=event.get("event_id"),
                correlation_id=(
                    event.get("correlation_id")
                    or event.get("event_id")
                ),
            )

            await self.bot.events.publish(eligible_event)
            matched_ids.append(opportunity_id)

        if not matched_ids:
            return EventResult.no_match(
                "no authored world opportunity matched"
            )

        return EventResult.matched(
            "authored world opportunities matched",
            match_count=len(matched_ids),
            opportunity_ids=matched_ids,
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(WorldOpportunityMatcherCog(bot))
