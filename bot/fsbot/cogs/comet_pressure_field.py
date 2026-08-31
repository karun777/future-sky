# ============================================================
# FILE META — fsbot/cogs/comet_pressure_field.py
# Canonical name: CometPressureFieldCog
#
# Version: v0.2.0 — Feather 9, Commit 2
# Last edited: 2026-08-04 (Australia/Perth)
#
# Scope:
# - Subscribe to heartbeat.advanced.
# - Read the Comet Cycle authority's durable pressure truth.
# - Project that pressure into an explicitly spatial field.
# - Persist the field after every heartbeat.
# - Publish comet_pressure_field.changed when the field fingerprint changes.
#
# Authority:
# - Owns the distribution of comet pressure across world scopes.
# - Writes only data/fields/comet_pressure/current_state.json.
#
# Does NOT own:
# - comet phase, cycle position, pressure, or temporal modifier
# - canonical world time
# - temporal resolution
# - semantic meaning
# - narrative consequences
#
# Distribution v0:
# - uniform_global_v0
# - one addressable scope: global
# - no invented regional, institutional, or character attenuation
#
# Must NOT:
# - mutate another authority
# - reinterpret comet pressure as emotion, meaning, or story
# - activate moments or scenarios
# - publish commands or mutate another authority
# ============================================================

from __future__ import annotations

import math
import os
from typing import Any, Dict, Optional, Tuple

from discord.ext import commands

from fsbot.events import EventResult, create_event
from fsbot.storage import load_json, save_json


STATE_FILE = "data/fields/comet_pressure/current_state.json"
COMET_STATE_FILE = "data/comet/current_state.json"

DISTRIBUTION_MODEL = "uniform_global_v0"
FIELD_SCOPE = "global"

Fingerprint = Tuple[str, str, float, str]


def _safe_unit_interval(raw: Any, *, name: str) -> float:
    value = float(raw)

    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")

    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{name}={value!r} outside range 0.0..1.0")

    return value


def _load_comet_state() -> Dict[str, Any]:
    state = load_json(COMET_STATE_FILE, {})

    if not isinstance(state, dict) or not state:
        raise ValueError("durable comet state unavailable")

    phase = str(state.get("phase") or "").strip()
    pressure_band = str(state.get("pressure_band") or "").strip()

    if not phase:
        raise ValueError("comet phase unavailable")

    if not pressure_band:
        raise ValueError("comet pressure band unavailable")

    return {
        "phase": phase,
        "pressure": _safe_unit_interval(
            state.get("pressure"),
            name="comet pressure",
        ),
        "pressure_band": pressure_band,
        "cycle_position": _safe_unit_interval(
            state.get("cycle_position"),
            name="comet cycle position",
        ),
        "world_time_seconds": int(state["world_time_seconds"]),
        "version": str(state.get("version") or "unknown"),
    }


def _fingerprint(state: Dict[str, Any]) -> Fingerprint:
    era = str(state.get("era") or "").strip().lower()
    model = str(state.get("distribution_model") or "").strip()
    band = str(state.get("band") or "").strip()

    samples = state.get("samples")
    if not isinstance(samples, dict):
        raise ValueError("field samples unavailable")

    global_sample = samples.get(FIELD_SCOPE)
    if not isinstance(global_sample, dict):
        raise ValueError("global field sample unavailable")

    intensity = _safe_unit_interval(
        global_sample.get("intensity"),
        name="global comet-pressure intensity",
    )

    if not era:
        raise ValueError("field era unavailable")

    if not model:
        raise ValueError("distribution model unavailable")

    if not band:
        raise ValueError("field band unavailable")

    return era, model, intensity, band


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


def _project_uniform_global_field(
    *,
    era: str,
    world_time_seconds: int,
    comet: Dict[str, Any],
) -> Dict[str, Any]:
    """Project comet pressure into the first spatial field geometry.

    This model intentionally applies no attenuation. It establishes the
    field contract and one addressable global sample without inventing
    regional physics that the world does not yet possess.
    """
    intensity = float(comet["pressure"])

    return {
        "version": "comet_pressure_field_v0",
        "field": "comet_pressure",
        "era": era,
        "distribution_model": DISTRIBUTION_MODEL,
        "band": comet["pressure_band"],
        "samples": {
            FIELD_SCOPE: {
                "intensity": intensity,
                "band": comet["pressure_band"],
            }
        },
        "source": {
            "authority": "comet_cycle",
            "phase": comet["phase"],
            "pressure": intensity,
            "pressure_band": comet["pressure_band"],
            "cycle_position": comet["cycle_position"],
            "state_version": comet["version"],
            "world_time_seconds": comet["world_time_seconds"],
        },
        "resolved_at_world_time_seconds": world_time_seconds,
    }


class CometPressureFieldCog(commands.Cog):
    """Project comet pressure across addressable world scopes."""

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
            raise RuntimeError("CometPressureFieldCog requires bot.events")

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
            era = str(scope.get("era") or "").strip().lower()

            if world_time_seconds < 0:
                raise ValueError("world_time_seconds must be non-negative")

            if not era:
                raise ValueError("heartbeat era unavailable")

            comet = _load_comet_state()

            if comet["world_time_seconds"] != world_time_seconds:
                raise ValueError(
                    "comet state is not aligned with the current heartbeat"
                )

            state = _project_uniform_global_field(
                era=era,
                world_time_seconds=world_time_seconds,
                comet=comet,
            )
            fingerprint = _fingerprint(state)

        except (KeyError, TypeError, ValueError) as exc:
            return EventResult.skipped(
                "comet-pressure field inputs unavailable",
                reason=str(exc),
            )

        previous_state = self._last_state
        previous_fingerprint = self._last_fingerprint

        try:
            _persist_state(state)
        except Exception as exc:
            return EventResult.failed(
                "comet-pressure field persistence failed",
                error_type=type(exc).__name__,
            )

        self._last_state = state
        self._last_fingerprint = fingerprint

        diagnostics = {
            "era": era,
            "distribution_model": DISTRIBUTION_MODEL,
            "global_intensity": (
                state["samples"][FIELD_SCOPE]["intensity"]
            ),
            "band": state["band"],
            "source_phase": state["source"]["phase"],
            "state_file": STATE_FILE,
        }

        if previous_fingerprint == fingerprint:
            return EventResult.unchanged(
                "comet-pressure field unchanged; state refreshed",
                **diagnostics,
            )

        changed_fields = [
            field
            for index, field in enumerate(
                (
                    "era",
                    "distribution_model",
                    "global_intensity",
                    "band",
                )
            )
            if previous_fingerprint is None
            or fingerprint[index] != previous_fingerprint[index]
        ]

        field_event = create_event(
            event_type="comet_pressure_field.changed",
            source_system="comet_pressure_field",
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
            await self.bot.events.publish(field_event)
        except Exception as exc:
            return EventResult.failed(
                "comet-pressure field publication failed",
                error_type=type(exc).__name__,
                state_persisted=True,
                field_event_id=field_event["event_id"],
            )

        if previous_fingerprint is None:
            detail = "initial comet-pressure field persisted and published"
        else:
            detail = "comet-pressure field changed, persisted and published"

        return EventResult.changed(
            detail,
            field_event_id=field_event["event_id"],
            changed_fields=changed_fields,
            **diagnostics,
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(CometPressureFieldCog(bot))
