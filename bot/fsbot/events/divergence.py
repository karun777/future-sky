"""Feather 28: identify divergent historical continuations without ranking them.

Pure read-only grouping of Feather 27's provenance-preserving observations.
A historical divergence is not a prediction, probability or narrative choice.
"""
from __future__ import annotations
from typing import Any, Dict, List

from fsbot.events.partial_recurrence import historical_continuations_for_present_context


def divergent_historical_continuations(
    pattern: Dict[str, Any], context_events: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Describe distinct next bands observed after matching historical prefixes."""
    base = historical_continuations_for_present_context(pattern, context_events)
    groups = []
    if base["status"] == "historical_continuations_observed":
        for observation in base["historical_continuations"]:
            band = observation["following_pressure_band"]
            group = next((g for g in groups if g["following_pressure_band"] == band), None)
            if group is None:
                group = {"following_pressure_band": band, "historical_evidence": []}
                groups.append(group)
            group["historical_evidence"].append({
                "matched_source_observation_event_ids": list(observation["matched_source_observation_event_ids"]),
                "following_source_observation_event_id": observation["following_source_observation_event_id"],
            })

    status = (
        "insufficient_evidence" if base["status"] == "insufficient_evidence"
        else "divergent_historical_continuations" if len(groups) >= 2
        else "single_historical_continuation" if len(groups) == 1
        else "no_observed_continuation"
    )
    return {
        "relevance_type": "comet_pressure_historical_divergence",
        "status": status,
        "context_event_ids": list(base["context_event_ids"]),
        "context_pressure_bands": list(base["context_pressure_bands"]),
        "historical_continuation_groups": groups,
        "relevance_version": "comet_pressure_historical_divergence_v0",
    }
