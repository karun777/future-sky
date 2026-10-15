# ============================================================
# FILE META — fsbot/events/relevance.py
# Feather 21 candidate: Read-only contextual relevance
#
# Relevance is applicability of evidence to an explicit context,
# not significance, resonance, interpretation or meaning.
# No persistence, event publication, activation or scoring.
# ============================================================

from __future__ import annotations

from typing import Any, Dict


def comet_pressure_relevance(
    pattern: Dict[str, Any],
    *,
    current_pressure_band: str,
) -> Dict[str, Any]:
    """Check whether a remembered comet-pressure pattern applies to a band.

    Only a caller-supplied, explicitly identified present pressure band is
    compared. No current world truth is inferred from historical observations.
    """
    band = str(current_pressure_band or "").strip()
    pattern_type = pattern.get("pattern_type")
    bands = pattern.get("pressure_bands")
    source_ids = pattern.get("source_observation_event_ids")

    valid = (
        pattern_type == "comet_pressure_sequence"
        and isinstance(bands, list)
        and isinstance(source_ids, list)
        and len(bands) == len(source_ids)
        and len(bands) > 0
        and all(isinstance(b, str) and bool(b.strip()) for b in bands)
        and all(isinstance(i, str) and bool(i.strip()) for i in source_ids)
    )

    if not band or not valid:
        status = "insufficient_evidence"
    elif band == bands[-1]:
        status = "applicable"
    else:
        status = "not_applicable"

    return {
        "relevance_type": "comet_pressure_band_continuity",
        "status": status,
        "context": {"current_pressure_band": band},
        "pattern_type": pattern_type,
        "source_observation_event_ids": list(source_ids) if valid else [],
        "relevance_version": "comet_pressure_relevance_v0",
    }
