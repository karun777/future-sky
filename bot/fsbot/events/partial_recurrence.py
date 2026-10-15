"""Feather 27: identify evidenced historical continuations of present prefixes.

Describes what followed earlier matching sequences, never what must follow now.
Read-only, non-authoritative, with no scoring or event publication.
"""
from __future__ import annotations
from typing import Any, Dict, List

from fsbot.events.present_recurrence import recurrence_for_present_context


def historical_continuations_for_present_context(
    pattern: Dict[str, Any], context_events: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Return observed historical next bands after present-sequence matches.

    Excludes matches at the end of the historical record: those have no
    observed continuation. Each returned continuation carries its own source ID.
    """
    base = recurrence_for_present_context(pattern, context_events)
    bands = pattern.get("pressure_bands") if isinstance(pattern, dict) else None
    ids = pattern.get("source_observation_event_ids") if isinstance(pattern, dict) else None
    valid = (
        base["status"] != "insufficient_evidence"
        and isinstance(bands, list) and isinstance(ids, list)
        and len(bands) == len(ids)
        and len(set(ids)) == len(ids)
    )
    continuations = []
    if valid:
        width = len(base["context_pressure_bands"])
        for occurrence in base["historical_occurrences"]:
            next_index = occurrence["start_index"] + width
            if next_index < len(bands):
                continuations.append({
                    "matched_source_observation_event_ids": list(occurrence["source_observation_event_ids"]),
                    "following_pressure_band": bands[next_index],
                    "following_source_observation_event_id": ids[next_index],
                })
    return {
        "relevance_type": "comet_pressure_historical_continuations",
        "status": (
            "insufficient_evidence" if not valid
            else "historical_continuations_observed" if continuations
            else "no_observed_continuation"
        ),
        "context_event_ids": base["context_event_ids"],
        "context_pressure_bands": base["context_pressure_bands"],
        "historical_occurrences": base["historical_occurrences"] if valid else [],
        "historical_continuations": continuations,
        "relevance_version": "comet_pressure_historical_continuations_v0",
    }
