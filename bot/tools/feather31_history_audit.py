"""Feather 31: read-only history sample; run from bot/ with PYTHONPATH=."""
import sys
from collections import Counter
from fsbot.events.history import EventHistory
from fsbot.events.patterns import comet_pressure_sequence
from fsbot.events.present_recurrence import recurrence_for_present_context

def audit(path):
    history = EventHistory(path)
    recent = history.recent_events(limit=500)
    counts = Counter(e.get("event_type") for e in recent)
    contexts = [e for e in reversed(recent) if e.get("event_type") == "world_moment.context"]
    pattern = comet_pressure_sequence(history, limit=100)
    sample = contexts[-2:]
    relevance = recurrence_for_present_context(pattern, sample)
    return {
        "events_sampled": len(recent),
        "event_types": dict(counts),
        "context_events_sampled": len(contexts),
        "remembered_observations": pattern["observation_count"],
        "remembered_pressure_bands": pattern["pressure_bands"],
        "context_bands": relevance["context_pressure_bands"],
        "recurrence_status": relevance["status"],
        "historical_matches": len(relevance["historical_occurrences"]),
    }

if __name__ == "__main__":
    import json
    print(json.dumps(audit(sys.argv[1]), indent=2))
