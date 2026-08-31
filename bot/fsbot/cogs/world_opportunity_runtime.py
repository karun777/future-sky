# ============================================================
# FILE META — fsbot/cogs/world_opportunity_runtime.py
# Canonical name: WorldOpportunityRuntimeCog
#
# Version: v0.2.0 — Feather 15: World Opportunity Lifecycle
#
# Scope:
# - Subscribe to world_opportunity.awakened.
# - Create durable world-scoped opportunity instances.
# - Subscribe to heartbeat.advanced.
# - Advance authored opportunity lifecycle.
# - Expire active instances when their world-time lifetime ends.
# - Publish world_opportunity.instantiated and
#   world_opportunity.expired facts.
#
# Authority:
# - AUTHORITATIVE for world opportunity runtime instances.
# - Owns instance identity, status, and lifecycle timestamps.
#
# Does NOT:
# - decide whether an opportunity may awaken
# - assign players
# - start scenarios
# - interpret narrative meaning
# - send Discord output
# ============================================================

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional
from uuid import uuid4

from discord.ext import commands

from fsbot.events import EventResult, create_event
from fsbot.storage import load_json, save_json


STATE_FILE = "data/world_opportunities/runtime_state.json"
CATALOGUE_FILE = "data/world_opportunities/catalogue.json"

STATE_VERSION = "world_opportunity_runtime_v0"
SECONDS_PER_WORLD_HOUR = 60 * 60


def _load_state() -> Dict[str, Any]:
    state = load_json(
        STATE_FILE,
        {
            "version": STATE_VERSION,
            "instances": [],
        },
    )

    if not isinstance(state, dict):
        state = {}

    instances = state.get("instances")
    if not isinstance(instances, list):
        instances = []

    return {
        "version": STATE_VERSION,
        "instances": [
            item for item in instances
            if isinstance(item, dict)
        ],
    }


def _save_state(state: Dict[str, Any]) -> None:
    directory = os.path.dirname(STATE_FILE)

    if directory:
        os.makedirs(directory, exist_ok=True)

    save_json(STATE_FILE, state)


def _find_authored_opportunity(
    opportunity_id: str,
) -> Optional[Dict[str, Any]]:
    catalogue = load_json(CATALOGUE_FILE, {})

    if not isinstance(catalogue, dict):
        return None

    opportunities = catalogue.get("opportunities")

    if not isinstance(opportunities, list):
        return None

    for raw in opportunities:
        if not isinstance(raw, dict):
            continue

        if str(raw.get("id") or "").strip() == opportunity_id:
            return raw

    return None


def _expiry_for(
    opportunity_id: str,
    awakened_at_world_time: int,
) -> Optional[int]:
    opportunity = _find_authored_opportunity(opportunity_id)

    if opportunity is None:
        return None

    lifecycle = opportunity.get("lifecycle")

    if not isinstance(lifecycle, dict):
        return None

    raw_hours = lifecycle.get("expires_after_world_hours")

    if raw_hours is None:
        return None

    try:
        hours = float(raw_hours)
    except (TypeError, ValueError):
        return None

    if hours <= 0:
        return None

    return awakened_at_world_time + int(
        hours * SECONDS_PER_WORLD_HOUR
    )


class WorldOpportunityRuntimeCog(commands.Cog):
    """Durable runtime authority for world opportunities."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._subscribed = False

    async def cog_load(self) -> None:
        events = getattr(self.bot, "events", None)

        if events is None:
            raise RuntimeError(
                "WorldOpportunityRuntimeCog requires bot.events"
            )

        # Establish / normalise durable state.
        state = _load_state()

        # Feather 15 compatibility:
        # backfill expiry for already-active Feather 14 instances.
        changed = False

        for instance in state["instances"]:
            if instance.get("status") != "active":
                continue

            if instance.get("expires_at_world_time") is not None:
                continue

            opportunity_id = str(
                instance.get("opportunity_id") or ""
            ).strip()

            try:
                awakened_at = int(
                    instance["awakened_at_world_time"]
                )
            except (KeyError, TypeError, ValueError):
                continue

            expires_at = _expiry_for(
                opportunity_id,
                awakened_at,
            )

            if expires_at is not None:
                instance["expires_at_world_time"] = expires_at
                changed = True

        if changed or not os.path.exists(STATE_FILE):
            _save_state(state)
        else:
            _save_state(state)

        events.subscribe(
            "world_opportunity.awakened",
            self.on_world_opportunity_awakened,
        )

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
                "world_opportunity.awakened",
                self.on_world_opportunity_awakened,
            )
            events.unsubscribe(
                "heartbeat.advanced",
                self.on_heartbeat_advanced,
            )

        self._subscribed = False

    async def on_world_opportunity_awakened(
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
            return EventResult.skipped(
                "missing opportunity id"
            )

        try:
            world_time = int(
                event.get("occurred_at_world_time", 0)
            )
        except (TypeError, ValueError):
            return EventResult.failed(
                "invalid awakening world time",
                opportunity_id=opportunity_id,
            )

        instance_id = f"wop_{uuid4().hex}"

        expires_at = _expiry_for(
            opportunity_id,
            world_time,
        )

        instance = {
            "instance_id": instance_id,
            "opportunity_id": opportunity_id,
            "status": "active",
            "era": scope.get("era"),
            "awakened_at_world_time": world_time,
            "updated_at_world_time": world_time,
            "expires_at_world_time": expires_at,
            "expired_at_world_time": None,
            "source_event_id": event.get("event_id"),
            "correlation_id": (
                event.get("correlation_id")
                or event.get("event_id")
            ),
        }

        state = _load_state()
        instances: List[Dict[str, Any]] = state["instances"]
        instances.append(instance)

        try:
            _save_state(state)
        except Exception as exc:
            return EventResult.failed(
                "world opportunity runtime persistence failed",
                opportunity_id=opportunity_id,
                reason=str(exc),
            )

        instantiated_event = create_event(
            event_type="world_opportunity.instantiated",
            source_system="world_opportunity_runtime",
            world_time=world_time,
            scope={
                "era": scope.get("era"),
                "opportunity_id": opportunity_id,
                "instance_id": instance_id,
            },
            payload={
                "instance_id": instance_id,
                "opportunity_id": opportunity_id,
                "status": "active",
                "awakened_at_world_time": world_time,
                "expires_at_world_time": expires_at,
                "runtime_version": STATE_VERSION,
            },
            causation_id=event.get("event_id"),
            correlation_id=(
                event.get("correlation_id")
                or event.get("event_id")
            ),
        )

        await self.bot.events.publish(instantiated_event)

        return EventResult.applied(
            "world opportunity instance created",
            instance_id=instance_id,
            opportunity_id=opportunity_id,
            status="active",
            expires_at_world_time=expires_at,
        )

    async def on_heartbeat_advanced(
        self,
        event: Dict[str, Any],
    ) -> EventResult:
        payload = (
            event.get("payload")
            if isinstance(event.get("payload"), dict)
            else {}
        )

        try:
            world_time = int(payload["world_time_seconds"])
        except (KeyError, TypeError, ValueError):
            return EventResult.skipped(
                "missing world_time_seconds"
            )

        state = _load_state()
        expired_instances: List[Dict[str, Any]] = []

        for instance in state["instances"]:
            if instance.get("status") != "active":
                continue

            expires_at = instance.get("expires_at_world_time")

            if expires_at is None:
                continue

            try:
                expiry_time = int(expires_at)
            except (TypeError, ValueError):
                continue

            if world_time < expiry_time:
                continue

            instance["status"] = "expired"
            instance["expired_at_world_time"] = expiry_time
            instance["updated_at_world_time"] = world_time

            expired_instances.append(instance)

        if not expired_instances:
            return EventResult.no_match(
                "no world opportunity lifecycle transition"
            )

        try:
            _save_state(state)
        except Exception as exc:
            return EventResult.failed(
                "world opportunity lifecycle persistence failed",
                reason=str(exc),
            )

        for instance in expired_instances:
            expired_event = create_event(
                event_type="world_opportunity.expired",
                source_system="world_opportunity_runtime",
                world_time=int(
                    instance["expired_at_world_time"]
                ),
                scope={
                    "era": instance.get("era"),
                    "opportunity_id":
                        instance.get("opportunity_id"),
                    "instance_id":
                        instance.get("instance_id"),
                },
                payload={
                    "instance_id":
                        instance.get("instance_id"),
                    "opportunity_id":
                        instance.get("opportunity_id"),
                    "status": "expired",
                    "awakened_at_world_time":
                        instance.get(
                            "awakened_at_world_time"
                        ),
                    "expired_at_world_time":
                        instance.get(
                            "expired_at_world_time"
                        ),
                    "observed_world_time_seconds":
                        world_time,
                    "runtime_version": STATE_VERSION,
                },
                causation_id=event.get("event_id"),
                correlation_id=(
                    instance.get("correlation_id")
                    or event.get("correlation_id")
                    or event.get("event_id")
                ),
            )

            await self.bot.events.publish(expired_event)

        return EventResult.changed(
            "world opportunity lifecycle advanced",
            expired_count=len(expired_instances),
            instance_ids=[
                instance.get("instance_id")
                for instance in expired_instances
            ],
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(WorldOpportunityRuntimeCog(bot))
