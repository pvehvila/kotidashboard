# src/api/weather_mapping.py
"""
Yhteensopivuuskerros vanhaa koodia varten.

Aiemmin kaikki oli yhdessä tiedostossa (wmo-mapit, tracing, ikonit).
Nyt varsinainen logiikka on jaettu neljään moduuliin, mutta vanhat importit
`from src.api.weather_mapping import ...` halutaan pitää toimivina.
"""

from src.api.wmo_foreca_code import wmo_to_foreca_code
from src.api.wmo_icon_map import wmo_to_icon_key
from src.api.wmo_map_loader import load_wmo_foreca_map
from src.api.wmo_trace import (
    MAP_TRACE_ENABLED,
    clear_map_trace,
    get_map_trace,
    trace_map,
)

__all__ = [
    "wmo_to_foreca_code",
    "wmo_to_icon_key",
    "load_wmo_foreca_map",
    "get_map_trace",
    "clear_map_trace",
    "MAP_TRACE_ENABLED",
    "trace_map",
]
