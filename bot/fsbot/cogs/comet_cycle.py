# ============================================================
# FILE META — fsbot/cogs/comet_cycle.py
# Canonical name: CometCycleCog
#
# Version: v0.1.0 — Feather 6: Comet Cycle Foundation
# Last edited: 2026-08-04 (Australia/Perth)
#
# Scope:
# - Subscribe to heartbeat.advanced.
# - Derive a deterministic authored comet cycle from world time.
# - Persist the current comet state after every heartbeat.
# - Publish comet.state_changed only when a meaningful state band changes.
# - Produce no Discord output and apply no temporal/gameplay effects yet.
#
# Authority:
# - Owns current comet cycle_position, phase, pressure and temporal_modifier.
# - Reads immutable heartbeat facts only.
# - Writes only data/comet/current_state.json.
# ============================================================

from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Any, Dict, Optional, Tuple

from discord.ext import commands

from fsbot.events import EventResult, create_event
from fsbot.storage import load_json, save_json


STATE_FILE = "data/comet/current_state.json"
SECONDS_PER_WORLD_DAY = 24 * 60 * 60

# Provisional authored cycle length. This is implementation scaffolding,
# not a canon duration. With the current Manzo multiplier it spans roughly
# nineteen real hours while still remaining deterministic across restarts.
CYCLE_DURATION_WORLD_DAYS = 48
CYCLE_DURATION_SECONDS = CYCLE_DURATION_WORLD_DAYS * SECONDS_PER_WORLD_DAY


@dataclass(frozen=True)
class PhaseDefinition:
    name: str
    start: float
    end: float
    pressure: float
    pressure_band: str
    temporal_modifier: float
    temporal_band: str


PHASES: Tuple[PhaseDefinition, ...] = (
    PhaseDefinition("dormant", 0.00, 0.15, 0.00, "still", 1.00, "baseline"),
    PhaseDefinition("detected", 0.15, 0.25, 0.10, "low", 1.00, "baseline"),
    PhaseDefinition("approaching", 0.25, 0.45, 0.30, "rising", 1.10, "stirring"),
    PhaseDefinition("visible", 0.45, 0.65, 0.55, "high", 1.25, "accelerated"),
    PhaseDefinition("dominant", 0.65, 0.82, 0.80, "severe", 1.60, "compressed"),
    PhaseDefinition("perihelion", 0.82, 0.88, 1.00, "peak", 2.00, "critical"),
    PhaseDefinition("departure", 0.88, 0.96, 0.60, "falling", 1.35, "accelerated"),
    PhaseDefinition("echo", 0.96, 1.00, 0.15, "residual", 1.05, "stirring"),
)

Fingerprint = Tuple[str, str, str]


def _phase_for_position(cycle_position: float) -> PhaseDefinition:
    """Return the authored phase containing a normalised cycle position."""
    position = float(cycle_position) % 1.0
    for phase in PHASES:
        if phase.start <= position < phase.end:
            return phase
    return PHASES[-1]


def _state_from_world_time(world_time_seconds: int) -> Dict[str, Any]:
    """Derive deterministic comet state from canonical world time."""
    if world_time_seconds < 0:
        raise ValueError("world_time_seconds must be non-negative")

    elapsed_in_cycle = world_time_seconds % CYCLE_DURATION_SECONDS
    cycle_position = elapsed_in_cycle / CYCLE_DURATION_SECONDS
    phase = _phase_for_position(cycle_position)
    remaining_seconds = CYCLE_DURATION_SECONDS - elapsed_in_cycle

    return {
        "cycle_position": round(cycle_position, 9),
        "cycle_number": world_time_seconds // CYCLE_DURATION_SECONDS,
        "phase": phase.name,
        "pressure": phase.pressure,
        "pressure_band": phase.pressure_band,
        "temporal_modifier": phase.temporal_modifier,
        "temporal_band": phase.temporal_band,
        "world_time_seconds": world_time_seconds,
        "world_seconds_until_cycle_reset": remaining_seconds,
        "cycle_duration_world_days": CYCLE_DURATION_WORLD_DAYS,
        "version": "comet_cycle_v0",
    }


def _fingerprint(state: Dict[str, Any]) -> Fingerprint:
    """Reduce the state to meaningful authored bands for event publication."""
    phase = str(state.get("phase") or "").strip()
    pressure_band = str(state.get("pressure_band") or "").strip()
    temporal_band = str(state.get("temporal_band") or "").strip()
    if not phase or not pressure_band or not temporal_band:
        raise ValueError("comet state missing fingerprint fields")
    return phase, pressure_band, temporal_band


def _load_persisted_state() -> Optional[Dict[str, Any]]:
    state = load_json(STATE_FILE, {})
    if not isinstance(state, dict) or not state:
        return None
    try:
        _fingerprint(state)
    except (TypeError, ValueError):
        return None
    return state


def _persist_state(state: Dict[str, Any]) -> None:
    directory = os.path.dirname(STATE_FILE)
    if directory:
        os.makedirs(directory, exist_ok=True)
    save_json(STATE_FILE, state)


class CometCycleCog(commands.Cog):
    """Persistent authored comet cycle driven by canonical world time."""

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
            raise RuntimeError("CometCycleCog requires bot.events")
        events.subscribe("heartbeat.advanced", self.on_heartbeat_advanced)
        self._subscribed = True

    def cog_unload(self) -> None:
        if not self._subscribed:
            return
        events = getattr(self.bot, "events", None)
        if events is not None:
            events.unsubscribe("heartbeat.advanced", self.on_heartbeat_advanced)
        self._subscribed = False

    async def on_heartbeat_advanced(self, event: Dict[str, Any]) -> EventResult:
        payload = event.get("payload") if isinstance(event.get("payload"), dict) else {}
        scope = event.get("scope") if isinstance(event.get("scope"), dict) else {}

        try:
            world_time_seconds = int(payload["world_time_seconds"])
            state = _state_from_world_time(world_time_seconds)
            fingerprint = _fingerprint(state)
        except (KeyError, TypeError, ValueError) as exc:
            return EventResult.skipped("comet state unavailable", reason=str(exc))

        previous_state = self._last_state
        previous_fingerprint = self._last_fingerprint

        try:
            _persist_state(state)
        except Exception as exc:
            return EventResult.failed(
                "comet state persistence failed",
                error_type=type(exc).__name__,
            )

        # Persistence succeeded. This state is now authoritative.
        self._last_state = state
        self._last_fingerprint = fingerprint

        diagnostics = {
            "phase": state["phase"],
            "cycle_position": state["cycle_position"],
            "pressure": state["pressure"],
            "pressure_band": state["pressure_band"],
            "temporal_modifier": state["temporal_modifier"],
            "temporal_band": state["temporal_band"],
            "state_file": STATE_FILE,
        }

        if fingerprint == previous_fingerprint:
            return EventResult.unchanged(
                "comet state bands unchanged",
                **diagnostics,
            )

        changed_fields = [
            field
            for index, field in enumerate(("phase", "pressure_band", "temporal_band"))
            if previous_fingerprint is None
            or fingerprint[index] != previous_fingerprint[index]
        ]

        comet_event = create_event(
            event_type="comet.state_changed",
            source_system="comet_cycle",
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
            await self.bot.events.publish(comet_event)
        except Exception as exc:
            return EventResult.failed(
                "comet fact publication failed",
                error_type=type(exc).__name__,
                state_persisted=True,
                comet_event_id=comet_event["event_id"],
            )

        if previous_fingerprint is None:
            detail = "initial comet state persisted and published"
        else:
            detail = "comet state bands persisted and published"

        return EventResult.changed(
            detail,
            comet_event_id=comet_event["event_id"],
            changed_fields=changed_fields,
            **diagnostics,
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(CometCycleCog(bot))
