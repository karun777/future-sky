# Feather 22 — Read-only bridge from a published world context to relevance.
# No world-store reads, event publication, persistence or interpretation.

from __future__ import annotations

from typing import Any, Dict

from fsbot.events.relevance import comet_pressure_relevance


def relevance_for_world_moment_context(
    pattern: Dict[str, Any],
    context_event: Dict[str, Any],
) -> Dict[str, Any]:
    """Evaluate a remembered pattern against an existing context fact.

    Only a world_moment.context event supplies the present comet band.
    The caller is responsible for obtaining the event and the pattern.
    """
    if not isinstance(context_event, dict) or context_event.get("event_type") != "world_moment.context":
        band = ""
    else:
        payload = context_event.get("payload")
        comet = payload.get("comet") if isinstance(payload, dict) else None
        band = comet.get("pressure_band") if isinstance(comet, dict) else ""

    result = comet_pressure_relevance(
        pattern, current_pressure_band=band if isinstance(band, str) else ""
    )
    result["context_event_id"] = (
        str(context_event.get("event_id") or "")
        if isinstance(context_event, dict)
        and context_event.get("event_type") == "world_moment.context"
        else ""
    )
    # No evidence of present context means no applicability claim.
    if not result["context_event_id"]:
        result["status"] = "insufficient_evidence"
    return result


def relevance_for_context_transition(
    pattern: Dict[str, Any],
    previous_context_event: Dict[str, Any],
    current_context_event: Dict[str, Any],
) -> Dict[str, Any]:
    """Compare an observed context transition with a remembered transition.

    The comparison is descriptive: it neither predicts the next context nor
    interprets why the transition occurred. Both context events must be
    distinct, time-ordered published world-moment contexts.
    """
    def extract(event: Dict[str, Any]):
        if not isinstance(event, dict) or event.get("event_type") != "world_moment.context":
            return None
        event_id = event.get("event_id")
        payload = event.get("payload")
        comet = payload.get("comet") if isinstance(payload, dict) else None
        band = comet.get("pressure_band") if isinstance(comet, dict) else None
        time = payload.get("moment_world_time_seconds") if isinstance(payload, dict) else None
        if not isinstance(event_id, str) or not event_id.strip():
            return None
        if not isinstance(band, str) or not band.strip():
            return None
        if type(time) is not int or time < 0:
            return None
        return event_id, band.strip(), time

    previous = extract(previous_context_event)
    current = extract(current_context_event)
    bands = pattern.get("pressure_bands") if isinstance(pattern, dict) else None
    ids = pattern.get("source_observation_event_ids") if isinstance(pattern, dict) else None

    evidence_valid = (
        isinstance(pattern, dict)
        and pattern.get("pattern_type") == "comet_pressure_sequence"
        and isinstance(bands, list)
        and isinstance(ids, list)
        and len(bands) >= 2
        and len(bands) == len(ids)
        and all(isinstance(b, str) and bool(b.strip()) for b in bands)
        and all(isinstance(i, str) and bool(i.strip()) for i in ids)
    )
    contexts_valid = (
        previous is not None and current is not None
        and previous[0] != current[0] and previous[2] < current[2]
    )

    if not evidence_valid or not contexts_valid:
        status = "insufficient_evidence"
    elif bands[-2:] == [previous[1], current[1]]:
        status = "applicable"
    else:
        status = "not_applicable"

    return {
        "relevance_type": "comet_pressure_transition_continuity",
        "status": status,
        "context_event_ids": [previous[0], current[0]] if contexts_valid else [],
        "context_pressure_bands": [previous[1], current[1]] if contexts_valid else [],
        "source_observation_event_ids": list(ids) if evidence_valid else [],
        "relevance_version": "comet_pressure_transition_relevance_v0",
    }
