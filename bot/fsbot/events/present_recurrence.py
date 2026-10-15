"""Feather 26: relate an unfolding context sequence to historical recurrence.

Pure, read-only composition of existing evidence. Context and historical
observation identities are kept separate; no interpretation or prediction.
"""
from __future__ import annotations

from typing import Any, Dict, List

from fsbot.events.recurrence import find_comet_pressure_recurrences


def recurrence_for_present_context(
    pattern: Dict[str, Any], context_events: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Find historical occurrences of an explicitly ordered present sequence.

    Requires at least two distinct, strictly time-ordered context events.
    Historical matches are independent of the supplied present events.
    """
    contexts = []
    if isinstance(context_events, list):
        for event in context_events:
            if not isinstance(event, dict) or event.get("event_type") != "world_moment.context":
                contexts = []
                break
            payload = event.get("payload")
            comet = payload.get("comet") if isinstance(payload, dict) else None
            band = comet.get("pressure_band") if isinstance(comet, dict) else None
            moment = payload.get("moment_world_time_seconds") if isinstance(payload, dict) else None
            event_id = event.get("event_id")
            if (
                not isinstance(event_id, str) or not event_id.strip()
                or not isinstance(band, str) or not band.strip()
                or type(moment) is not int or moment < 0
            ):
                contexts = []
                break
            contexts.append((event_id, band.strip(), moment))

    valid = (
        len(contexts) >= 2
        and len({c[0] for c in contexts}) == len(contexts)
        and all(contexts[i][2] < contexts[i + 1][2] for i in range(len(contexts) - 1))
    )
    bands = [c[1] for c in contexts] if valid else []
    recurrence = find_comet_pressure_recurrences(pattern, pressure_bands=bands)
    return {
        "relevance_type": "comet_pressure_present_recurrence",
        "status": recurrence["status"] if valid else "insufficient_evidence",
        "context_event_ids": [c[0] for c in contexts] if valid else [],
        "context_pressure_bands": bands,
        "historical_occurrences": recurrence["occurrences"] if valid else [],
        "relevance_version": "comet_pressure_present_recurrence_v0",
    }
