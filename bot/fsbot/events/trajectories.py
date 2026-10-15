"""Feather 29: bounded, evidenced historical trajectories after matching contexts.

Reports observed sequences, including shorter terminal histories, without
prediction, probability, ranking, mutation or interpretation.
"""
from __future__ import annotations
from typing import Any, Dict, List

from fsbot.events.present_recurrence import recurrence_for_present_context


def historical_trajectories_for_present_context(
    pattern: Dict[str, Any], context_events: List[Dict[str, Any]], *, steps: int = 3
) -> Dict[str, Any]:
    """Return up to 'steps' subsequent observations for each historical match.

    A bounded horizon (1..10) avoids treating an unbounded remainder of
    history as one causal trajectory. Historical windows never wrap around.
    """
    base = recurrence_for_present_context(pattern, context_events)
    bands = pattern.get("pressure_bands") if isinstance(pattern, dict) else None
    ids = pattern.get("source_observation_event_ids") if isinstance(pattern, dict) else None
    valid = (
        type(steps) is int and 1 <= steps <= 10
        and base["status"] != "insufficient_evidence"
        and isinstance(bands, list) and isinstance(ids, list)
        and len(bands) == len(ids)
    )
    trajectories = []
    if valid:
        width = len(base["context_pressure_bands"])
        for occurrence in base["historical_occurrences"]:
            start = occurrence["start_index"] + width
            end = min(start + steps, len(bands))
            trajectories.append({
                "matched_source_observation_event_ids": list(occurrence["source_observation_event_ids"]),
                "following_pressure_bands": list(bands[start:end]),
                "following_source_observation_event_ids": list(ids[start:end]),
                "complete_horizon_observed": end - start == steps,
            })
    return {
        "relevance_type": "comet_pressure_historical_trajectories",
        "status": (
            "insufficient_evidence" if not valid
            else "historical_trajectories_observed" if any(t["following_pressure_bands"] for t in trajectories)
            else "no_observed_trajectory"
        ),
        "context_event_ids": list(base["context_event_ids"]),
        "context_pressure_bands": list(base["context_pressure_bands"]),
        "requested_steps": steps,
        "historical_trajectories": trajectories,
        "relevance_version": "comet_pressure_historical_trajectories_v0",
    }
