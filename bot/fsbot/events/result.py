# fsbot/events/result.py — Event Result primitive v1.0
#
# Purpose:
# - Represents the observable outcome of one event subscriber.
# - Keeps gameplay meaning owned by the subscriber.
# - Gives EventBus a common, structured shape for tracing.
#
# Contract:
# - Immutable.
# - Optional: subscribers may still return None.
# - Contains no persistence or gameplay logic.
# - `status` is required.
# - `detail` is a short human-readable explanation.
# - `data` is optional structured diagnostic metadata.

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Optional


@dataclass(frozen=True)
class EventResult:
    """Structured outcome returned by an event subscriber."""

    status: str
    detail: Optional[str] = None
    data: Optional[Mapping[str, Any]] = None

    def __post_init__(self) -> None:
        status = str(self.status or "").strip()
        if not status:
            raise ValueError("EventResult.status is required")

        object.__setattr__(self, "status", status)

        if self.detail is not None:
            detail = str(self.detail).strip()
            object.__setattr__(self, "detail", detail or None)

        if self.data is not None and not isinstance(self.data, Mapping):
            raise TypeError("EventResult.data must be a mapping or None")

    @classmethod
    def ok(
        cls,
        detail: str | None = None,
        **data: Any,
    ) -> "EventResult":
        return cls("ok", detail, data or None)

    @classmethod
    def delivered(
        cls,
        detail: str | None = None,
        **data: Any,
    ) -> "EventResult":
        return cls("delivered", detail, data or None)

    @classmethod
    def matched(
        cls,
        detail: str | None = None,
        **data: Any,
    ) -> "EventResult":
        return cls("matched", detail, data or None)

    @classmethod
    def no_match(
        cls,
        detail: str | None = None,
        **data: Any,
    ) -> "EventResult":
        return cls("no_match", detail, data or None)

    @classmethod
    def suppressed(
        cls,
        detail: str | None = None,
        **data: Any,
    ) -> "EventResult":
        return cls("suppressed", detail, data or None)

    @classmethod
    def skipped(
        cls,
        detail: str | None = None,
        **data: Any,
    ) -> "EventResult":
        return cls("skipped", detail, data or None)

    @classmethod
    def queued(
        cls,
        detail: str | None = None,
        **data: Any,
    ) -> "EventResult":
        return cls("queued", detail, data or None)

    @classmethod
    def applied(
        cls,
        detail: str | None = None,
        **data: Any,
    ) -> "EventResult":
        return cls("applied", detail, data or None)

    @classmethod
    def refreshed(
        cls,
        detail: str | None = None,
        **data: Any,
    ) -> "EventResult":
        return cls("refreshed", detail, data or None)

    @classmethod
    def changed(
        cls,
        detail: str | None = None,
        **data: Any,
    ) -> "EventResult":
        return cls("changed", detail, data or None)

    @classmethod
    def unchanged(
        cls,
        detail: str | None = None,
        **data: Any,
    ) -> "EventResult":
        return cls("unchanged", detail, data or None)

    @classmethod
    def failed(
        cls,
        detail: str | None = None,
        **data: Any,
    ) -> "EventResult":
        return cls("failed", detail, data or None)

    def with_data(self, **extra: Any) -> "EventResult":
        """Return a new result with merged diagnostic metadata."""
        merged = dict(self.data or {})
        merged.update(extra)
        return EventResult(
            status=self.status,
            detail=self.detail,
            data=merged or None,
        )

    def as_dict(self) -> dict[str, Any]:
        """Return a JSON-friendly diagnostic representation."""
        return {
            "status": self.status,
            "detail": self.detail,
            "data": dict(self.data) if self.data is not None else None,
        }
