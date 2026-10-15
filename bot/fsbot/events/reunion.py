"""Feather 30: recognise evidenced divergence and later reunion.

This compares only observed historical continuations, never hypothetical
outcomes. A reunion means equal pressure bands at the same later offset
after an earlier differing band; it is not causal or narrative significance.
"""
from __future__ import annotations
from typing import Any, Dict, List

from fsbot.events.trajectories import historical_trajectories_for_present_context


def historical_divergence_and_reunion(
    pattern: Dict[str, Any], context_events: List[Dict[str, Any]], *, steps: int = 3
) -> Dict[str, Any]:
    base = historical_trajectories_for_present_context(pattern, context_events, steps=steps)
    trajectories = base["historical_trajectories"]
    reunions = []
    if base["status"] != "insufficient_evidence":
        for i, left in enumerate(trajectories):
            for j in range(i + 1, len(trajectories)):
                right = trajectories[j]
                a = left["following_pressure_bands"]
                b = right["following_pressure_bands"]
                # A reunion requires a preceding observed divergence.
                diverged = False
                for offset in range(min(len(a), len(b))):
                    if a[offset] != b[offset]:
                        diverged = True
                    elif diverged:
                        reunions.append({
                            "historical_pair_indices": [i, j],
                            "reunion_offset": offset + 1,
                            "reunion_pressure_band": a[offset],
                            "left_reunion_source_observation_event_id": left["following_source_observation_event_ids"][offset],
                            "right_reunion_source_observation_event_id": right["following_source_observation_event_ids"][offset],
                            "left_matched_source_observation_event_ids": list(left["matched_source_observation_event_ids"]),
                            "right_matched_source_observation_event_ids": list(right["matched_source_observation_event_ids"]),
                        })
                        break

    return {
        "relevance_type": "comet_pressure_historical_divergence_reunion",
        "status": (
            "insufficient_evidence" if base["status"] == "insufficient_evidence"
            else "historical_reunion_observed" if reunions
            else "no_observed_reunion"
        ),
        "context_event_ids": list(base["context_event_ids"]),
        "context_pressure_bands": list(base["context_pressure_bands"]),
        "requested_steps": steps,
        "historical_reunions": reunions,
        "relevance_version": "comet_pressure_divergence_reunion_v0",
    }
