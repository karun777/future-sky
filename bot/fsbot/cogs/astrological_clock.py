# ============================================================
# FILE META — fsbot/cogs/astrological_clock.py
# Canonical name: AstrologicalClockCog (real-sky observer)
#
# Version: v0.2.0 — Feather 5: First Astrological Fact
# Last edited: 2026-08-01 (Australia/Perth)
#
# Scope:
# - Subscribe to heartbeat.advanced.
# - Calculate tropical Sun and Moon positions for event UTC.
# - Compare a stable one-degree observational fingerprint.
# - Persist a changed snapshot before announcing it.
# - Publish astrology.snapshot_changed as an immutable fact.
# - Produce no Discord output and apply no gameplay effects.
#
# Authority:
# - Owns the current observed real-sky snapshot.
# - Reads immutable heartbeat facts only.
# - Writes only data/astrology/current_snapshot.json.
# ============================================================

from __future__ import annotations

from datetime import datetime, timezone
import os
from typing import Any, Dict, Optional, Tuple

from discord.ext import commands

import swisseph as swe

from fsbot.astrology import FLAGS, _julian_day_ut, _sign_from_longitude
from fsbot.events import EventResult, create_event
from fsbot.storage import load_json, save_json


SNAPSHOT_FILE = "data/astrology/current_snapshot.json"
Fingerprint = Tuple[Tuple[str, int], Tuple[str, int]]


def _compute_transit_snapshot(dt_utc: datetime) -> Dict[str, Any]:
    """Compute a minimal tropical Sun/Moon snapshot for an aware UTC instant."""
    jd_ut = _julian_day_ut(dt_utc.astimezone(timezone.utc))
    placements: Dict[str, Any] = {}

    for body_key, body_id in (("sun", swe.SUN), ("moon", swe.MOON)):
        xx, _ = swe.calc_ut(jd_ut, body_id, FLAGS)
        longitude = float(xx[0]) % 360.0
        speed = float(xx[3]) if len(xx) > 3 else 0.0
        sign, degree_in_sign = _sign_from_longitude(longitude)
        placements[body_key] = {
            "sign": sign,
            "longitude_deg": round(longitude, 6),
            "degree_in_sign": round(degree_in_sign, 6),
            "speed_deg_per_day": round(speed, 6),
        }

    return {
        "observed_at_utc": dt_utc.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
        "zodiac": "tropical",
        "ephemeris_mode": "MOSEPH",
        "placements": placements,
        "version": "transit_snapshot_v0",
    }


def _parse_event_utc(value: Any) -> datetime:
    """Parse the canonical event UTC timestamp into an aware UTC datetime."""
    text = str(value or "").strip()
    if not text:
        raise ValueError("missing occurred_at_utc")

    if text.endswith("Z"):
        text = f"{text[:-1]}+00:00"

    observed_at = datetime.fromisoformat(text)
    if observed_at.tzinfo is None:
        raise ValueError("occurred_at_utc must be timezone-aware")
    return observed_at.astimezone(timezone.utc)


def _fingerprint(snapshot: Dict[str, Any]) -> Fingerprint:
    """Reduce precise positions to sign + whole degree for change detection."""
    placements = snapshot.get("placements")
    if not isinstance(placements, dict):
        raise ValueError("snapshot missing placements")

    values = []
    for body in ("sun", "moon"):
        placement = placements.get(body)
        if not isinstance(placement, dict):
            raise ValueError(f"snapshot missing {body}")

        sign = str(placement.get("sign") or "").strip()
        degree = int(float(placement["degree_in_sign"]))
        if not sign:
            raise ValueError(f"snapshot missing {body} sign")
        values.append((sign, degree))

    return values[0], values[1]


def _persist_snapshot(snapshot: Dict[str, Any]) -> None:
    """Persist the authoritative snapshot atomically, creating its directory."""
    directory = os.path.dirname(SNAPSHOT_FILE)
    if directory:
        os.makedirs(directory, exist_ok=True)
    save_json(SNAPSHOT_FILE, snapshot)


def _load_persisted_snapshot() -> Optional[Dict[str, Any]]:
    """Load the last durable snapshot, rejecting malformed historical data."""
    snapshot = load_json(SNAPSHOT_FILE, {})
    if not isinstance(snapshot, dict) or not snapshot:
        return None

    try:
        _fingerprint(snapshot)
    except (KeyError, TypeError, ValueError):
        return None
    return snapshot


class AstrologicalClockCog(commands.Cog):
    """Real-sky observer driven by the authoritative heartbeat."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._subscribed = False
        self._last_snapshot = _load_persisted_snapshot()
        self._last_fingerprint: Optional[Fingerprint] = (
            _fingerprint(self._last_snapshot)
            if self._last_snapshot is not None
            else None
        )

    async def cog_load(self) -> None:
        events = getattr(self.bot, "events", None)
        if events is None:
            raise RuntimeError("AstrologicalClockCog requires bot.events")

        events.subscribe("heartbeat.advanced", self.on_heartbeat_advanced)
        self._subscribed = True

    def cog_unload(self) -> None:
        if not self._subscribed:
            return

        events = getattr(self.bot, "events", None)
        if events is not None:
            events.unsubscribe("heartbeat.advanced", self.on_heartbeat_advanced)
        self._subscribed = False

    async def on_heartbeat_advanced(self, event: Dict[str, Any]) -> EventResult:
        """Observe, persist, then announce a meaningful real-sky change."""
        try:
            observed_at = _parse_event_utc(event.get("occurred_at_utc"))
            snapshot = _compute_transit_snapshot(observed_at)
            fingerprint = _fingerprint(snapshot)
        except (KeyError, TypeError, ValueError) as exc:
            return EventResult.skipped(
                "astrological snapshot unavailable",
                reason=str(exc),
            )
        except Exception as exc:
            return EventResult.failed(
                "astrological calculation failed",
                error_type=type(exc).__name__,
            )

        previous_fingerprint = self._last_fingerprint
        previous_snapshot = self._last_snapshot

        sun = snapshot["placements"]["sun"]
        moon = snapshot["placements"]["moon"]
        diagnostics = {
            "observed_at_utc": snapshot["observed_at_utc"],
            "sun_sign": sun["sign"],
            "sun_degree": int(float(sun["degree_in_sign"])),
            "sun_longitude_deg": sun["longitude_deg"],
            "moon_sign": moon["sign"],
            "moon_degree": int(float(moon["degree_in_sign"])),
            "moon_longitude_deg": moon["longitude_deg"],
            "ephemeris_mode": snapshot["ephemeris_mode"],
        }

        if fingerprint == previous_fingerprint:
            return EventResult.unchanged(
                "Sun/Moon degree fingerprint unchanged",
                **diagnostics,
            )

        try:
            _persist_snapshot(snapshot)
        except Exception as exc:
            return EventResult.failed(
                "astrological snapshot persistence failed",
                error_type=type(exc).__name__,
            )

        # Durability has succeeded. This snapshot is now authoritative.
        self._last_snapshot = snapshot
        self._last_fingerprint = fingerprint

        payload: Dict[str, Any] = {
            "snapshot": snapshot,
            "previous_snapshot": previous_snapshot,
            "changed_bodies": [
                body
                for index, body in enumerate(("sun", "moon"))
                if previous_fingerprint is None
                or fingerprint[index] != previous_fingerprint[index]
            ],
            "change_granularity": "whole_degree",
        }

        world_time = int(event.get("occurred_at_world_time") or 0)
        scope = event.get("scope") if isinstance(event.get("scope"), dict) else {}
        sky_event = create_event(
            event_type="astrology.snapshot_changed",
            source_system="astrological_clock",
            world_time=world_time,
            scope=scope,
            payload=payload,
            causation_id=str(event.get("event_id") or "") or None,
            correlation_id=(
                str(event.get("correlation_id") or "")
                or str(event.get("event_id") or "")
                or None
            ),
        )

        try:
            await self.bot.events.publish(sky_event)
        except Exception as exc:
            return EventResult.failed(
                "astrological fact publication failed",
                error_type=type(exc).__name__,
                snapshot_persisted=True,
                astrological_event_id=sky_event["event_id"],
            )

        result_data = {
            **diagnostics,
            "astrological_event_id": sky_event["event_id"],
            "changed_bodies": payload["changed_bodies"],
            "snapshot_file": SNAPSHOT_FILE,
        }

        if previous_fingerprint is None:
            return EventResult.changed(
                "initial Sun/Moon snapshot persisted and published",
                **result_data,
            )

        return EventResult.changed(
            "Sun/Moon degree fingerprint persisted and published",
            previous_sun_sign=previous_fingerprint[0][0],
            previous_sun_degree=previous_fingerprint[0][1],
            previous_moon_sign=previous_fingerprint[1][0],
            previous_moon_degree=previous_fingerprint[1][1],
            **result_data,
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(AstrologicalClockCog(bot))
