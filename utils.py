# ...existing code...
"""Utility functions for the HomeDashboard application."""
from typing import List, Tuple, Optional

import socket
import streamlit as st

from config import (
    DEV,
    PRICE_HIGH_THR,
    PRICE_LOW_THR,
    CLOUD_T_CLEAR,
    CLOUD_T_ALMOST,
    CLOUD_T_PARTLY,
    CLOUD_T_MOSTLY,
)


def report_error(ctx: str, e: Exception) -> None:
    """Log errors to the console and, in DEV mode, display them in the Streamlit UI.

    Args:
        ctx: Context or identifier for the error.
        e: Exception object to log.
    """
    print(f"[ERR] {ctx}: {type(e).__name__}: {e}")
    if DEV:
        st.caption(f"⚠ {ctx}: {type(e).__name__}: {e}")


def _color_by_thresholds(
    vals: List[Optional[float]],
    low_thr: float = PRICE_LOW_THR,
    high_thr: float = PRICE_HIGH_THR,
) -> List[str]:
    """Generate a list of colors based on value thresholds for visualization.

    Args:
        vals: List of values to color-code (e.g., electricity prices).
        low_thr: Low threshold for green color (default: PRICE_LOW_THR).
        high_thr: High threshold for yellow/red colors (default: PRICE_HIGH_THR).

    Returns:
        List of RGBA color strings corresponding to each value.
    """
    colors = []
    for value in vals:
        if value is None:
            colors.append("rgba(128,128,128,0.5)")  # Gray for None
        elif value < low_thr:
            colors.append("rgba(60,180,75,0.9)")  # Green
        elif value <= high_thr:
            colors.append("rgba(255,225,25,0.9)")  # Yellow
        else:
            colors.append("rgba(230,25,75,0.9)")  # Red
    return colors


def _color_for_value(
    value: Optional[float],
    low_thr: float = PRICE_LOW_THR,
    high_thr: float = PRICE_HIGH_THR,
) -> str:
    """Get a single color for a value based on thresholds.

    Args:
        value: Value to color-code (e.g., electricity price).
        low_thr: Low threshold for green color (default: PRICE_LOW_THR).
        high_thr: High threshold for yellow/red colors (default: PRICE_HIGH_THR).

    Returns:
        RGBA color string for the value.
    """
    return _color_by_thresholds([value], low_thr, high_thr)[0]


def _cloud_icon_from_cover(cover: Optional[int], is_day: bool) -> str:
    """Map cloud cover percentage to a Foreca-style icon code.

    Args:
        cover: Cloud cover percentage (None defaults to 100).
        is_day: True for daytime icons, False for nighttime.

    Returns:
        Foreca icon code (e.g., 'd000' for clear day, 'n400' for fully cloudy night).
    """
    prefix = "d" if is_day else "n"
    cloud = 100 if cover is None else int(cover)
    if cloud < CLOUD_T_CLEAR:
        return f"{prefix}000"  # Clear
    if cloud < CLOUD_T_ALMOST:
        return f"{prefix}100"  # Almost clear
    if cloud < CLOUD_T_PARTLY:
        return f"{prefix}200"  # Partly cloudy
    if cloud < CLOUD_T_MOSTLY:
        return f"{prefix}300"  # Mostly cloudy
    return f"{prefix}400"  # Fully cloudy


def get_ip() -> str:
    """Get the local IP address of the machine.

    Returns:
        IP address as a string, or 'localhost' if an error occurs.
    """
    try:
        return socket.gethostbyname(socket.gethostname())
    except Exception as e:
        report_error("get_ip", e)
        return "localhost"


# --- AURINGON NOUSU/LASKU (Open-Meteo, ei uusia riippuvuuksia) ---
def fetch_sun_times(
    lat: float, lon: float, tz_str: str
) -> Tuple[Optional[str], Optional[str]]:
    """Palauttaa (sunrise_HH:MM, sunset_HH:MM) merkkijonot paikallisajassa tai (None, None)."""
    try:
        import urllib.request, urllib.parse, json as _json

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
        with urllib.request.urlopen(url, timeout=6) as r:
            data = _json.loads(r.read().decode("utf-8"))
        sunrise_iso = (data.get("daily", {}).get("sunrise") or [None])[0]
        sunset_iso = (data.get("daily", {}).get("sunset") or [None])[0]

        def _fmt(iso: Optional[str]) -> Optional[str]:
            if not iso:
                return None
            # Open-Meteo palauttaa jo tz:n mukaisen paikallisajan kun timezone-parametri on annettu
            try:
                return iso[11:16]  # "YYYY-MM-DDTHH:MM"
            except Exception:
                from datetime import datetime as _dt

                return _dt.fromisoformat(iso).strftime("%H:%M")

        return _fmt(sunrise_iso), _fmt(sunset_iso)
    except Exception:
        return None, None


def _sun_icon(kind: str, size: int = 18) -> str:
    """Pieni inline-SVG ikoni: 'rise' tai 'set'."""
    if kind == "rise":
        # Aurinko horisontista ylöspäin
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
    # 'set' – aurinko alas
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
# ...existing code...