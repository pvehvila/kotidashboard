from __future__ import annotations

from src.api.weather_utils import cloud_icon_from_cover
from src.api.wmo_map_loader import load_wmo_foreca_map
from src.api.wmo_trace import trace_map


def wmo_to_foreca_code(
    code: int | None,
    is_day: bool,
    pop: int | None = None,
    temp_c: float | None = None,
    cloudcover: int | None = None,
) -> str:
    """
    Päämäppäys: WMO → Foreca-koodi ("d000"/"n000"/"d100"...)

    1. Yritetään Excel/CSV-mäppäystä
    2. Jos ei löydy -> pilvisyyspohjainen fallback
    """
    maps = load_wmo_foreca_map()

    if code is None:
        key = "d000" if is_day else "n000"
        trace_map(code, is_day, pop, temp_c, cloudcover, key, "none → clear (default)")
        return key

    lookup = maps["day" if is_day else "night"]
    if code in lookup:
        key = lookup[code]
        trace_map(code, is_day, pop, temp_c, cloudcover, key, "Excel mapping")
        return key

    # fallback pilvisyyden perusteella
    key = cloud_icon_from_cover(cloudcover, is_day)
    trace_map(code, is_day, pop, temp_c, cloudcover, key, "fallback: cloudcover")
    return key
