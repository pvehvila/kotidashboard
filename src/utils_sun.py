# src/utils_sun.py
"""Sunrise/sunset utilities using Open-Meteo."""

import json as _json
import urllib.parse
import urllib.request


def fetch_sun_times(lat: float, lon: float, tz_str: str) -> tuple[str | None, str | None]:
    """Return (sunrise_HH:MM, sunset_HH:MM) in local time or (None, None)."""
    try:
        qs = urllib.parse.urlencode(
            {
                "latitude": f"{lat:.6f}",
                "longitude": f"{lon:.6f}",
                "daily": "sunrise,sunset",
                "timezone": tz_str,
                "forecast_days": 1,
            }
        )

        url = f"https://api.open-meteo.com/v1/forecast?{qs}"

        parsed = urllib.parse.urlparse(url)
        if parsed.scheme not in ("http", "https"):
            raise ValueError(f"Unexpected URL scheme: {parsed.scheme}")

        # schema checked above
        with urllib.request.urlopen(url, timeout=6) as r:  # nosec B310
            data = _json.loads(r.read().decode("utf-8"))

        sunrise_iso = (data.get("daily", {}).get("sunrise") or [None])[0]
        sunset_iso = (data.get("daily", {}).get("sunset") or [None])[0]

        def _fmt(iso: str | None) -> str | None:
            if not iso:
                return None
            try:
                return iso[11:16]
            except Exception:
                from datetime import datetime as _dt

                return _dt.fromisoformat(iso).strftime("%H:%M")

        return _fmt(sunrise_iso), _fmt(sunset_iso)
    except Exception:
        return None, None


def _sun_icon(kind: str, size: int = 18) -> str:
    """Small inline SVG icon for sunrise/sunset."""
    if kind == "rise":
        return (
            f"<svg width='{size}' height='{size}' viewBox='0 0 24 24' aria-label='Auringonnousu' "
            "xmlns='http://www.w3.org/2000/svg' fill='none' stroke='currentColor' stroke-width='2' "
            "stroke-linecap='round' stroke-linejoin='round'>"
            "<path d='M3 18h18'/>"
            "<path d='M12 2v8'/>"
            "<path d='M9 7l3-3 3 3'/>"
            "<path d='M5 18a7 7 0 0 1 14 0'/>"
            "</svg>"
        )
    return (
        f"<svg width='{size}' height='{size}' viewBox='0 0 24 24' aria-label='Auringonlasku' "
        "xmlns='http://www.w3.org/2000/svg' fill='none' stroke='currentColor' stroke-width='2' "
        "stroke-linecap='round' stroke-linejoin='round'>"
        "<path d='M3 18h18'/>"
        "<path d='M12 10v8'/>"
        "<path d='M15 15l-3 3-3-3'/>"
        "<path d='M5 18a7 7 0 0 1 14 0'/>"
        "</svg>"
    )
