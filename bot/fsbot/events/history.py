# ============================================================
# FILE META — fsbot/events/history.py
# Canonical name: EventHistory
#
# Version: v0.1.0 — Feather 17: Durable Event History
#
# Purpose:
# - Persist completed EventBus dispatch records as append-only JSONL.
# - Preserve canonical event envelopes across process restarts.
# - Preserve subscriber outcomes for historical diagnostics.
#
# Authority:
# - Owns historical observation of published events only.
#
# Does NOT:
# - own gameplay state
# - make events authoritative
# - replay events
# - reconstruct runtime state
# - invoke subscribers
# - interpret event meaning
# ============================================================

from __future__ import annotations

import json
import os
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, List


HISTORY_VERSION = "event_history_v0"


class EventHistory:
    """Append-only durable history of completed EventBus dispatches."""

    def __init__(
        self,
        path: str = "data/events/event_history.jsonl",
    ) -> None:
        self.path = str(path)

        directory = os.path.dirname(self.path)
        if directory:
            os.makedirs(directory, exist_ok=True)

        # Establish the file without truncating existing history.
        with open(self.path, "a", encoding="utf-8"):
            pass

    def append(
        self,
        event: Dict[str, Any],
        traces: List[Dict[str, Any]],
    ) -> None:
        record = {
            "history_version": HISTORY_VERSION,
            "event": deepcopy(event),
            "subscribers": deepcopy(traces),
            "recorded_at_utc": datetime.now(timezone.utc)
            .isoformat()
            .replace("+00:00", "Z"),
        }

        line = json.dumps(
            record,
            ensure_ascii=False,
            separators=(",", ":"),
        )

        # Append-only persistence. One complete JSON object per line.
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(line)
            f.write("\n")
            f.flush()

    def count(self) -> int:
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return sum(1 for line in f if line.strip())
        except FileNotFoundError:
            return 0

    def recent_events(
        self,
        *,
        event_type_prefix: str | None = None,
        since_world_time: int | None = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Return newest remembered canonical events matching neutral filters.

        This is a read-only history query.

        It does not replay events, interpret meaning, or reconstruct state.
        """
        prefix = str(event_type_prefix or "").strip()
        max_results = max(0, int(limit))

        if max_results == 0:
            return []

        if since_world_time is not None:
            since_world_time = max(0, int(since_world_time))

        matches: List[Dict[str, Any]] = []

        try:
            with open(self.path, "r", encoding="utf-8") as f:
                for raw_line in f:
                    line = raw_line.strip()
                    if not line:
                        continue

                    try:
                        record = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    if not isinstance(record, dict):
                        continue

                    event = record.get("event")
                    if not isinstance(event, dict):
                        continue

                    event_type = str(event.get("event_type") or "")

                    if prefix and not event_type.startswith(prefix):
                        continue

                    if since_world_time is not None:
                        try:
                            world_time = int(
                                event.get("occurred_at_world_time", 0)
                            )
                        except (TypeError, ValueError):
                            continue

                        if world_time < since_world_time:
                            continue

                    matches.append(deepcopy(event))

        except FileNotFoundError:
            return []

        return list(reversed(matches[-max_results:]))
