from __future__ import annotations

from src.api.weather_utils import cloud_icon_from_cover
from src.api.wmo_map_loader import load_wmo_foreca_map
from src.api.wmo_trace import trace_map
from src.config import (
    CLOUD_T_MOSTLY,
    CLOUD_T_PARTLY,
    POP_POSSIBLE_THRESHOLD,
    SLEET_TEMP_MAX,
    SLEET_TEMP_MIN,
)

_CLOUD_CODE_POP_THRESHOLD = max(POP_POSSIBLE_THRESHOLD, 60)


def _precip_suffix(temp_c: float | None, intensity: int) -> str:
    if temp_c is None:
        return str(intensity)
    if temp_c < SLEET_TEMP_MIN:
        return str(intensity + 2)
    if temp_c <= SLEET_TEMP_MAX:
        return str(intensity + 1)
    return str(intensity)


def _cloud_group(cloudcover: int | None) -> str:
    if cloudcover is None:
        return "4"
    if cloudcover < CLOUD_T_PARTLY:
        return "2"
    if cloudcover < CLOUD_T_MOSTLY:
        return "3"
    return "4"


def _precip_icon(
    is_day: bool,
    cloudcover: int | None,
    temp_c: float | None,
    intensity: int,
) -> str:
    prefix = "d" if is_day else "n"
    return f"{prefix}{_cloud_group(cloudcover)}{_precip_suffix(temp_c, intensity)}"


def _open_meteo_icon(
    code: int,
    is_day: bool,
    pop: int | None,
    temp_c: float | None,
    cloudcover: int | None,
) -> str | None:
    """
    Open-Meteo käyttää omaa WMO weather code -joukkoaan.

    Mukana oleva Excel-taulu on yleisempi SYNOP-taulu, joten esimerkiksi koodi 3 ei
    tarkoita siinä samaa asiaa kuin Open-Meteossa. Siksi dashboardin tuntiennuste
    päätellään tässä eksplisiittisesti Open-Meteon koodeista ja PoP-arvosta.
    """
    prefix = "d" if is_day else "n"

    if code == 0:
        return f"{prefix}000"
    if code in (1, 2, 3):
        if pop is not None and pop >= _CLOUD_CODE_POP_THRESHOLD:
            intensity = 20 if pop >= 80 else 10
            return _precip_icon(is_day, cloudcover, temp_c, intensity)
        return cloud_icon_from_cover(cloudcover, is_day)
    if code in (45, 48):
        return f"{prefix}600"
    if code in (51, 53, 55, 56, 57):
        return _precip_icon(is_day, cloudcover, temp_c, 10)
    if code in (61, 66):
        return _precip_icon(is_day, cloudcover, temp_c, 10)
    if code in (63, 67, 80, 81):
        return _precip_icon(is_day, cloudcover, temp_c, 20)
    if code in (65, 82):
        return _precip_icon(is_day, cloudcover, temp_c, 30)
    if code in (71, 85):
        return f"{prefix}{_cloud_group(cloudcover)}12"
    if code in (73,):
        return f"{prefix}{_cloud_group(cloudcover)}22"
    if code in (75, 77, 86):
        return f"{prefix}{_cloud_group(cloudcover)}32"
    if code in (95, 96, 99):
        return f"{prefix}{_cloud_group(cloudcover)}40"

    return None


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

    key = _open_meteo_icon(code, is_day, pop, temp_c, cloudcover)
    if key is not None:
        trace_map(code, is_day, pop, temp_c, cloudcover, key, "Open-Meteo mapping")
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
