# ============================================================
# FILE META — fsbot/cogs/world_opportunity_gate.py
# Canonical name: WorldOpportunityGateCog
#
# Version: v0.2.0 — Feather 16: Single Active Opportunity Gate
#
# Scope:
# - Subscribe to world_opportunity.eligible.
# - Read authored gate policy.
# - Read durable opportunity runtime state when required.
# - Decide whether an eligible opportunity may awaken.
# - Publish world_opportunity.awakened when permitted.
#
# Authority:
# - Owns the eligibility -> awakening decision.
# - Owns no opportunity runtime state.
# - Owns no world truth.
#
# Does NOT:
# - create or mutate runtime instances
# - activate scenarios
# - select players
# - mutate characters or world authorities
# - send Discord output
# - invent narrative meaning
# ============================================================

from __future__ import annotations

from typing import Any, Dict, Optional

from discord.ext import commands

from fsbot.events import EventResult, create_event
from fsbot.storage import load_json


CATALOGUE_FILE = "data/world_opportunities/catalogue.json"
RUNTIME_STATE_FILE = "data/world_opportunities/runtime_state.json"


def _find_opportunity(
    catalogue: Dict[str, Any],
    opportunity_id: str,
) -> Optional[Dict[str, Any]]:
    opportunities = catalogue.get("opportunities")

    if not isinstance(opportunities, list):
        return None

    for raw in opportunities:
        if not isinstance(raw, dict):
            continue

        candidate_id = str(raw.get("id") or "").strip()

        if candidate_id == opportunity_id:
            return raw

    return None


def _active_instance_for(opportunity_id: str) -> Optional[Dict[str, Any]]:
    state = load_json(RUNTIME_STATE_FILE, {})

    if not isinstance(state, dict):
        return None

    instances = state.get("instances")

    if not isinstance(instances, list):
        return None

    for instance in instances:
        if not isinstance(instance, dict):
            continue

        if str(instance.get("opportunity_id") or "").strip() != opportunity_id:
            continue

        if str(instance.get("status") or "").strip().lower() != "active":
            continue

        return instance

    return None


class WorldOpportunityGateCog(commands.Cog):
    """Decide whether an eligible world opportunity may awaken."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._subscribed = False

    async def cog_load(self) -> None:
        events = getattr(self.bot, "events", None)

        if events is None:
            raise RuntimeError(
                "WorldOpportunityGateCog requires bot.events"
            )

        events.subscribe(
            "world_opportunity.eligible",
            self.on_world_opportunity_eligible,
        )
        self._subscribed = True

    def cog_unload(self) -> None:
        if not self._subscribed:
            return

        events = getattr(self.bot, "events", None)

        if events is not None:
            events.unsubscribe(
                "world_opportunity.eligible",
                self.on_world_opportunity_eligible,
            )

        self._subscribed = False

    async def on_world_opportunity_eligible(
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

        opportunity_id = str(
            payload.get("opportunity_id")
            or scope.get("opportunity_id")
            or ""
        ).strip()

        if not opportunity_id:
            return EventResult.skipped("missing opportunity id")

        catalogue = load_json(CATALOGUE_FILE, {})

        if not isinstance(catalogue, dict):
            return EventResult.failed(
                "world opportunity catalogue unavailable"
            )

        opportunity = _find_opportunity(
            catalogue,
            opportunity_id,
        )

        if opportunity is None:
            return EventResult.no_match(
                "eligible opportunity no longer exists",
                opportunity_id=opportunity_id,
            )

        if opportunity.get("enabled") is False:
            return EventResult.no_match(
                "eligible opportunity is disabled",
                opportunity_id=opportunity_id,
            )

        gate = opportunity.get("gate")

        if gate is None:
            gate = {"mode": "always"}

        if not isinstance(gate, dict):
            return EventResult.failed(
                "opportunity gate invalid",
                opportunity_id=opportunity_id,
            )

        mode = str(
            gate.get("mode") or "always"
        ).strip().lower()

        if mode == "single_active":
            active = _active_instance_for(opportunity_id)

            if active is not None:
                return EventResult.suppressed(
                    "active opportunity instance already exists",
                    opportunity_id=opportunity_id,
                    gate_mode=mode,
                    active_instance_id=active.get("instance_id"),
                )

        elif mode != "always":
            return EventResult.no_match(
                "unsupported opportunity gate mode",
                opportunity_id=opportunity_id,
                gate_mode=mode,
            )

        world_time = int(
            event.get("occurred_at_world_time", 0)
        )

        awakened_event = create_event(
            event_type="world_opportunity.awakened",
            source_system="world_opportunity_gate",
            world_time=world_time,
            scope={
                "era": scope.get("era"),
                "opportunity_id": opportunity_id,
            },
            payload={
                "opportunity_id": opportunity_id,
                "catalogue_version":
                    catalogue.get("version"),
                "gate": gate,
            },
            causation_id=event.get("event_id"),
            correlation_id=(
                event.get("correlation_id")
                or event.get("event_id")
            ),
        )

        await self.bot.events.publish(awakened_event)

        return EventResult.applied(
            "world opportunity awakened",
            opportunity_id=opportunity_id,
            gate_mode=mode,
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(WorldOpportunityGateCog(bot))
