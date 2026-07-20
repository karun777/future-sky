# fsbot/astrology.py
# Future Sky — Pure Astrology Calculator (v0)
#
# Purpose:
# - Compute tropical zodiac SIGN placements for major planets from birth date/time.
# - NO houses, NO aspects, NO rising sign (v0).
# - Output is safe to store in JSON under extra.astrology.
#
# Accuracy:
# - Uses Swiss Ephemeris via `swisseph` with MOSEPH (no external ephemeris files required).
#
# Inputs:
# - birthdate: "YYYY-MM-DD" (required)
# - birth_time: "HH:MM" (optional; defaults to 12:00)
# - tz_offset_minutes: integer minutes offset from UTC (optional; defaults to 0)
#
# Notes:
# - If tz_offset_minutes is unknown, this v0 module assumes UTC. We record assumptions.

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, date, time, timedelta, timezone
from typing import Dict, Any, Optional, Tuple

import swisseph as swe


ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

# Swiss Ephemeris planet constants we care about at v0
PLANETS = {
    "sun": swe.SUN,
    "moon": swe.MOON,
    "mercury": swe.MERCURY,
    "venus": swe.VENUS,
    "mars": swe.MARS,
    "jupiter": swe.JUPITER,
    "saturn": swe.SATURN,
    "uranus": swe.URANUS,
    "neptune": swe.NEPTUNE,
    "pluto": swe.PLUTO,
}

# Use MOSEPH to avoid reliance on external ephemeris data files
FLAGS = swe.FLG_MOSEPH | swe.FLG_SPEED


@dataclass(frozen=True)
class BirthInput:
    birthdate: str                 # YYYY-MM-DD
    birth_time: Optional[str]      # HH:MM or None
    tz_offset_minutes: Optional[int]  # minutes offset from UTC or None


def _parse_birth_input(b: BirthInput) -> Tuple[datetime, Dict[str, Any]]:
    """
    Returns (dt_utc, assumptions)
    """
    assumptions: Dict[str, Any] = {
        "time_assumed": False,
        "tz_assumed": False,
        "tropical_zodiac": True,
        "houses_computed": False,
        "rising_computed": False,
        "aspects_computed": False,
        "ephemeris_mode": "MOSEPH",
    }

    # Date
    try:
        y, m, d = (int(x) for x in b.birthdate.split("-"))
        birth_d = date(y, m, d)
    except Exception as e:
        raise ValueError(f"Invalid birthdate '{b.birthdate}'. Expected YYYY-MM-DD.") from e

    # Time
    if b.birth_time:
        try:
            hh, mm = (int(x) for x in b.birth_time.split(":"))
            birth_t = time(hh, mm)
        except Exception as e:
            raise ValueError(f"Invalid birth_time '{b.birth_time}'. Expected HH:MM.") from e
    else:
        birth_t = time(12, 0)  # v0 default
        assumptions["time_assumed"] = True

    # TZ
    if b.tz_offset_minutes is None:
        tz_offset_minutes = 0
        assumptions["tz_assumed"] = True
    else:
        tz_offset_minutes = int(b.tz_offset_minutes)

    tz = timezone(timedelta(minutes=tz_offset_minutes))
    dt_local = datetime.combine(birth_d, birth_t).replace(tzinfo=tz)
    dt_utc = dt_local.astimezone(timezone.utc)

    assumptions["birth_input"] = {
        "birthdate": b.birthdate,
        "birth_time": b.birth_time if b.birth_time else "12:00 (assumed)",
        "tz_offset_minutes": b.tz_offset_minutes if b.tz_offset_minutes is not None else "0 (assumed)",
    }
    assumptions["computed_utc"] = dt_utc.isoformat()

    return dt_utc, assumptions


def _julian_day_ut(dt_utc: datetime) -> float:
    """
    Swiss Ephemeris expects UT Julian Day.
    """
    if dt_utc.tzinfo is None:
        raise ValueError("dt_utc must be timezone-aware UTC datetime.")
    dt_utc = dt_utc.astimezone(timezone.utc)

    y = dt_utc.year
    m = dt_utc.month
    d = dt_utc.day
    hour = dt_utc.hour + (dt_utc.minute / 60.0) + (dt_utc.second / 3600.0) + (dt_utc.microsecond / 3_600_000_000.0)

    return swe.julday(y, m, d, hour, swe.GREG_CAL)


def _sign_from_longitude(lon_deg: float) -> Tuple[str, float]:
    """
    Convert ecliptic longitude (0..360) to (sign_name, deg_in_sign).
    """
    lon = lon_deg % 360.0
    sign_index = int(lon // 30.0)  # 0..11
    deg_in_sign = lon - (sign_index * 30.0)
    return ZODIAC_SIGNS[sign_index], deg_in_sign


def compute_planet_signs(
    birthdate: str,
    birth_time: Optional[str] = None,
    tz_offset_minutes: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Pure calculation: returns a JSON-safe dict containing:
    - assumptions
    - placements: planet -> { sign, lon_deg, deg_in_sign, speed_deg_per_day }
    """
    dt_utc, assumptions = _parse_birth_input(
        BirthInput(birthdate=birthdate, birth_time=birth_time, tz_offset_minutes=tz_offset_minutes)
    )
    jd_ut = _julian_day_ut(dt_utc)

    placements: Dict[str, Any] = {}

    for planet_key, planet_id in PLANETS.items():
        # swe.calc_ut returns (xx, retflag)
        # where xx[0] is longitude, xx[3] is speed in longitude (deg/day) when FLG_SPEED used
        xx, _ = swe.calc_ut(jd_ut, planet_id, FLAGS)
        lon = float(xx[0])
        speed = float(xx[3]) if len(xx) > 3 else 0.0

        sign, deg_in_sign = _sign_from_longitude(lon)
        placements[planet_key] = {
            "sign": sign,
            "lon_deg": round(lon % 360.0, 6),
            "deg_in_sign": round(deg_in_sign, 6),
            "speed_deg_per_day": round(speed, 6),
        }

    return {
        "assumptions": assumptions,
        "placements": placements,
        "version": "astrology_signs_v0",
    }
