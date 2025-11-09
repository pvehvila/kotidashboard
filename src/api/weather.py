"""
Säärajapinnan julkiset entrypointit.

Tämä tiedosto pidetään lyhyenä, jotta Radon ei huomauta liiallisesta monimutkaisuudesta.
Varsinainen logiikka on jaettu:
- weather_fetch -> Open-Meteo haku
- weather_mapping -> WMO <-> Foreca -mäppäys
- weather_utils -> tyypinmuunnokset
- weather_debug -> Streamlitin testikortti
"""

from __future__ import annotations

from typing import Any

# debug-kortti vain jos dashboard tarvitsee sitä
from src.api.weather_debug import card_weather_debug_matrix  # noqa: F401
from src.api.weather_fetch import fetch_weather_points
from src.api.weather_mapping import (
    clear_map_trace,
    get_map_trace,
    wmo_to_foreca_code,
    wmo_to_icon_key,
)

__all__ = [
    "fetch_weather_points",
    "wmo_to_foreca_code",
    "wmo_to_icon_key",
    "get_map_trace",
    "clear_map_trace",
    "card_weather_debug_matrix",
]


def get_weather_for_dashboard(lat: float, lon: float, tz_name: str) -> dict[str, Any]:
    """
    Yksinkertainen “orkestroija”, jota UI voi kutsua:
    """
    return fetch_weather_points(lat=lat, lon=lon, tz_name=tz_name)
