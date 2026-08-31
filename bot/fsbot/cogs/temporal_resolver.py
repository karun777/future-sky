# ============================================================
# FILE META — fsbot/cogs/temporal_resolver.py
# Canonical name: TemporalResolverCog
#
# Version: v0.2.0 — Feather 8, Commit 2
# Last edited: 2026-08-04 (Australia/Perth)
#
# Scope:
# - Subscribe to heartbeat.advanced.
# - Read the current era baseline.
# - Read the Comet Cycle authority's durable temporal modifier.
# - Resolve those independent truths into one effective multiplier.
# - Persist the resolved temporal state after every heartbeat.
# - Publish temporal.resolved when the resolved fingerprint changes.
#
# Authority:
# - Owns effective_temporal_multiplier.
# - Writes only data/time/temporal_resolver.json.
#
# Reads:
# - heartbeat.advanced immutable facts.
# - GameState era time profiles.
# - data/comet/current_state.json.
#
# Must NOT:
# - Advance world time.
# - Modify comet or era state.
# - Publish commands or mutate another authority.
# - Influence the current heartbeat.
# ============================================================

from __future__ import annotations

import math
import os
from typing import Any, Dict, Optional, Tuple

from discord.ext import commands

from fsbot.events import EventResult, create_event
from fsbot.storage import load_json, save_json


STATE_FILE = "data/time/temporal_resolver.json"
COMET_STATE_FILE = "data/comet/current_state.json"

Fingerprint = Tuple[str, float, float, float]


def _safe_positive_multiplier(
    raw: Any,
    *,
    name: str,
    minimum: float,
    maximum: float,
) -> float:
    value = float(raw)

    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")

    if not minimum <= value <= maximum:
        raise ValueError(
            f"{name}={value!r} outside safe range "
            f"{minimum}..{maximum}"
        )

    return value


def _fingerprint(state: Dict[str, Any]) -> Fingerprint:
    era = str(state.get("era") or "").strip().lower()
    contributors = state.get("contributors")

    if not era:
        raise ValueError("resolved state missing era")

    if not isinstance(contributors, dict):
        raise ValueError("resolved state missing contributors")

    era_multiplier = _safe_positive_multiplier(
        contributors.get("era"),
        name="era multiplier",
        minimum=0.01,
        maximum=100000.0,
    )
    comet_modifier = _safe_positive_multiplier(
        contributors.get("comet"),
        name="comet modifier",
        minimum=0.10,
        maximum=10.0,
    )
    effective_multiplier = _safe_positive_multiplier(
        state.get("effective_temporal_multiplier"),
        name="effective temporal multiplier",
        minimum=0.001,
        maximum=1000000.0,
    )

    return (
        era,
        era_multiplier,
        comet_modifier,
        effective_multiplier,
    )


def _load_persisted_state() -> Optional[Dict[str, Any]]:
    state = load_json(STATE_FILE, {})

    if not isinstance(state, dict) or not state:
        return None

    try:
        _fingerprint(state)
    except (TypeError, ValueError):
        return None

    return state


def _load_comet_state() -> Dict[str, Any]:
    state = load_json(COMET_STATE_FILE, {})

    if not isinstance(state, dict) or not state:
        raise ValueError("durable comet state unavailable")

    modifier = _safe_positive_multiplier(
        state.get("temporal_modifier"),
        name="comet temporal modifier",
        minimum=0.10,
        maximum=10.0,
    )

    return {
        "phase": str(state.get("phase") or "unknown"),
        "temporal_band": str(state.get("temporal_band") or "unknown"),
        "temporal_modifier": modifier,
        "version": str(state.get("version") or "unknown"),
    }


def _persist_state(state: Dict[str, Any]) -> None:
    directory = os.path.dirname(STATE_FILE)

    if directory:
        os.makedirs(directory, exist_ok=True)

    save_json(STATE_FILE, state)


class TemporalResolverCog(commands.Cog):
    """Resolve temporal authorities into one durable multiplier."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._subscribed = False
        self._last_state = _load_persisted_state()
        self._last_fingerprint: Optional[Fingerprint] = (
            _fingerprint(self._last_state)
            if self._last_state is not None
            else None
        )

    async def cog_load(self) -> None:
        events = getattr(self.bot, "events", None)

        if events is None:
            raise RuntimeError("TemporalResolverCog requires bot.events")

        if getattr(self.bot, "state", None) is None:
            raise RuntimeError("TemporalResolverCog requires bot.state")

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
            world_time_seconds = int(payload["world_time_seconds"])

            era = str(
                scope.get("era")
                or self.bot.state.resolve_default_era()
            ).strip().lower()

            profile = self.bot.state.get_era_time_profile(era)

            era_multiplier = _safe_positive_multiplier(
                profile.get("era_time_multiplier"),
                name="era multiplier",
                minimum=0.01,
                maximum=100000.0,
            )

            comet_state = _load_comet_state()
            comet_modifier = float(
                comet_state["temporal_modifier"]
            )

            effective_multiplier = era_multiplier * comet_modifier

            state = {
                "version": "temporal_resolver_v0",
                "effective_temporal_multiplier": round(
                    effective_multiplier,
                    6,
                ),
                "contributors": {
                    "era": era_multiplier,
                    "comet": comet_modifier,
                },
                "era": era,
                "context": {
                    "era_profile_label": str(
                        profile.get("label") or era
                    ),
                    "comet_phase": comet_state["phase"],
                    "comet_temporal_band": comet_state["temporal_band"],
                },
                "source_versions": {
                    "era_profiles": str(
                        self.bot.state
                        .load_era_time_profiles()
                        .get("version", "unknown")
                    ),
                    "comet_cycle": comet_state["version"],
                },
                "resolved_at_world_time_seconds": world_time_seconds,
            }

            fingerprint = _fingerprint(state)

        except (KeyError, TypeError, ValueError) as exc:
            return EventResult.skipped(
                "temporal inputs unavailable",
                reason=str(exc),
            )

        previous_state = self._last_state
        previous_fingerprint = self._last_fingerprint

        try:
            _persist_state(state)
        except Exception as exc:
            return EventResult.failed(
                "temporal resolution persistence failed",
                error_type=type(exc).__name__,
            )

        self._last_state = state
        self._last_fingerprint = fingerprint

        diagnostics = {
            "effective_temporal_multiplier": (
                state["effective_temporal_multiplier"]
            ),
            "era_multiplier": state["contributors"]["era"],
            "comet_modifier": state["contributors"]["comet"],
            "era": state["era"],
            "comet_phase": state["context"]["comet_phase"],
            "state_file": STATE_FILE,
        }

        if previous_fingerprint == fingerprint:
            return EventResult.unchanged(
                "temporal contributors unchanged; state refreshed",
                **diagnostics,
            )


        changed_fields = [
            field
            for index, field in enumerate(
                (
                    "era",
                    "era_multiplier",
                    "comet_modifier",
                    "effective_temporal_multiplier",
                )
            )
            if previous_fingerprint is None
            or fingerprint[index] != previous_fingerprint[index]
        ]

        temporal_event = create_event(
            event_type="temporal.resolved",
            source_system="temporal_resolver",
            world_time=world_time_seconds,
            scope=scope,
            payload={
                "previous_state": previous_state,
                "current_state": state,
                "changed_fields": changed_fields,
            },
            causation_id=str(event.get("event_id") or "") or None,
            correlation_id=(
                str(event.get("correlation_id") or "")
                or str(event.get("event_id") or "")
                or None
            ),
        )

        try:
            await self.bot.events.publish(temporal_event)
        except Exception as exc:
            return EventResult.failed(
                "temporal fact publication failed",
                error_type=type(exc).__name__,
                state_persisted=True,
                temporal_event_id=temporal_event["event_id"],
            )

        if previous_fingerprint is None:
            detail = "initial temporal resolution persisted and published"
        else:
            detail = "temporal resolution changed, persisted and published"

        return EventResult.changed(
            detail,
            temporal_event_id=temporal_event["event_id"],
            changed_fields=changed_fields,
            **diagnostics,
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(TemporalResolverCog(bot))
