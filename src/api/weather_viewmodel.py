# src/api/weather_viewmodel.py
from __future__ import annotations

from typing import Any

from src.api import fetch_weather_points
from src.config import LAT, LON


def build_weather_view(interval: str) -> dict[str, Any]:
    """
    Palauttaa kortin tarvitsemat säädatan osat.
    interval: esim. '1 h', '3 h' tai '6 h'
    """
    step = int(interval.split()[0])
    offsets = tuple(step * i for i in range(5))

    weather_data = fetch_weather_points(LAT, LON, "Europe/Helsinki", offsets=offsets)
    points = weather_data["points"]
    min_temp = weather_data["min_temp"]
    max_temp = weather_data["max_temp"]

    return {
        "points": points,
        "min_temp": min_temp,
        "max_temp": max_temp,
        "interval": interval,
        "offsets": offsets,
    }
