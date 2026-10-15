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
