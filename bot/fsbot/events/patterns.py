# ============================================================
# FILE META — fsbot/events/patterns.py
# Canonical name: ObservationPatterns
#
# Version: v0.1.1 — Feather 20: First Remembered Pattern
#
# Purpose:
# - Inspect remembered observation facts.
# - Recognise neutral structural relationships across observations.
#
# Does NOT:
# - interpret narrative meaning
# - score significance
# - detect convergence
# - activate scenarios or moments
# - mutate history
# - replay events
# ============================================================

from __future__ import annotations

from typing import Any, Dict, List

from fsbot.events.history import EventHistory


def comet_pressure_sequence(
    history: EventHistory,
    *,
    limit: int = 10,
) -> Dict[str, Any]:
    events = history.recent_events(
        event_type_prefix="observation.comet_state",
        limit=limit,
    )

    # EventHistory returns newest-first.
    events = list(reversed(events))

    bands: List[str] = []
    pressures: List[float] = []
    event_ids: List[str] = []

    for event in events:
        payload = (
            event.get("payload")
            if isinstance(event.get("payload"), dict)
            else {}
        )

        band = str(payload.get("pressure_band") or "").strip()

        try:
            pressure = float(payload["pressure"])
        except (KeyError, TypeError, ValueError):
            continue

        if not band:
            continue

        bands.append(band)
        pressures.append(pressure)
        event_ids.append(str(event.get("event_id") or ""))

    direction = "insufficient"

    if len(pressures) >= 2:
        if all(
            pressures[i] < pressures[i + 1]
            for i in range(len(pressures) - 1)
        ):
            direction = "increasing"
        elif all(
            pressures[i] > pressures[i + 1]
            for i in range(len(pressures) - 1)
        ):
            direction = "decreasing"
        elif all(
            pressures[i] == pressures[i + 1]
            for i in range(len(pressures) - 1)
        ):
            direction = "stable"
        else:
            direction = "mixed"

    return {
        "pattern_type": "comet_pressure_sequence",
        "observation_count": len(pressures),
        "pressure_bands": bands,
        "pressures": pressures,
        "direction": direction,
        "source_observation_event_ids": event_ids,
        "pattern_version": "comet_pressure_pattern_v0",
    }
