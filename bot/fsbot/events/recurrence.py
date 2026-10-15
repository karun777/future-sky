"""Feather 25: neutral recurrence of a sequence within remembered history.

Pure read-only matching. Caller supplies a Feather 20 pattern and an explicit
sequence of pressure bands. No history reads, predictions, scoring or meaning.
"""

from __future__ import annotations

from typing import Any, Dict, List


def find_comet_pressure_recurrences(
    pattern: Dict[str, Any], *, pressure_bands: List[str]
) -> Dict[str, Any]:
    """Return all disjoint evidenced occurrences, oldest first.

    Adjacent windows are allowed; overlapping windows are not counted as
    independent recurrences. At least two non-overlapping occurrences are
    needed to report 'recurring'.
    """
    historical_bands = pattern.get("pressure_bands") if isinstance(pattern, dict) else None
    source_ids = pattern.get("source_observation_event_ids") if isinstance(pattern, dict) else None
    valid = (
        isinstance(pattern, dict)
        and pattern.get("pattern_type") == "comet_pressure_sequence"
        and isinstance(historical_bands, list)
        and isinstance(source_ids, list)
        and len(historical_bands) == len(source_ids)
        and len(historical_bands) > 0
        and isinstance(pressure_bands, list)
        and len(pressure_bands) >= 2
        and all(isinstance(b, str) and bool(b.strip()) for b in historical_bands)
        and all(isinstance(b, str) and bool(b.strip()) for b in pressure_bands)
        and all(isinstance(i, str) and bool(i.strip()) for i in source_ids)
        and len(set(source_ids)) == len(source_ids)
    )
    occurrences = []
    if valid:
        width = len(pressure_bands)
        index = 0
        while index <= len(historical_bands) - width:
            if historical_bands[index:index + width] == pressure_bands:
                occurrences.append({
                    "start_index": index,
                    "source_observation_event_ids": source_ids[index:index + width],
                })
                index += width
            else:
                index += 1

    return {
        "pattern_type": "comet_pressure_historical_recurrence",
        "status": (
            "insufficient_evidence" if not valid
            else "recurring" if len(occurrences) >= 2
            else "observed_once" if len(occurrences) == 1
            else "not_observed"
        ),
        "query_pressure_bands": list(pressure_bands) if isinstance(pressure_bands, list) else [],
        "occurrences": occurrences,
        "recurrence_version": "comet_pressure_recurrence_v0",
    }
