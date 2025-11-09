from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.api.weather_utils import cloud_icon_from_cover
from src.paths import DATA

# tracing vanhasta tiedostosta
MAP_TRACE_ENABLED = False
_MAP_TRACE: list[dict] = []


def trace_map(
    wmo: int | None,
    is_day: bool,
    pop: int | None,
    temp_c: float | None,
    cloudcover: int | None,
    chosen_key: str,
    reason: str,
) -> None:
    if not MAP_TRACE_ENABLED:
        return
    try:
        _MAP_TRACE.append(
            {
                "wmo": wmo,
                "is_day": is_day,
                "pop": pop,
                "temp_c": temp_c,
                "cloudcover": cloudcover,
                "key": chosen_key,
                "reason": reason,
            }
        )
        if len(_MAP_TRACE) > 200:
            del _MAP_TRACE[:-120]
    except Exception:
        # tracing ei saa kaataa dashboardia
        pass


def get_map_trace() -> list[dict]:
    return list(_MAP_TRACE)


def clear_map_trace() -> None:
    _MAP_TRACE.clear()


def _read_wmo_mapping(path: str | None = None) -> pd.DataFrame:
    candidates: list[Path] = []

    if path:
        candidates.append(Path(path))

    root = Path(__file__).parent
    for name in ("wmo_foreca_map.xlsx", "wmo_foreca_map.csv", "mappings.xlsx", "mappings.csv"):
        candidates.append(root / name)

    # käyttäjän oikea excel data-kansiosta
    candidates.append(DATA / "WMO_Foreca-koodit.xlsx")

    for p in candidates:
        try:
            if not p.exists():
                continue
            if p.suffix.lower() in (".xls", ".xlsx"):
                return pd.read_excel(p)
            return pd.read_csv(p)
        except Exception:
            continue

    return pd.DataFrame()


def _prep(raw: str, last: str | None) -> str | None:
    s = raw.strip() if raw else ""
    return s if s else last


def load_wmo_foreca_map(
    df: pd.DataFrame | None = None,
    wmo_col: str = "wmo",
    day_col: str = "day",
    night_col: str = "night",
) -> dict[str, dict[int, str]]:
    """
    Palauttaa: {"day": {wmo: "d100"}, "night": {wmo: "n200"}}
    """
    if df is None:
        df = _read_wmo_mapping()

    if df.empty:
        return {"day": {}, "night": {}}

    maps_day: dict[int, str] = {}
    maps_night: dict[int, str] = {}
    last_day_full: str | None = None
    last_night_full: str | None = None

    def _scalar(cell: Any) -> Any:
        if hasattr(cell, "iloc"):
            return cell.iloc[0] if len(cell) > 0 else None  # type: ignore[arg-type]
        if hasattr(cell, "item"):
            try:
                return cell.item()
            except Exception:
                return cell
        return cell

    for _, row in df.iterrows():
        try:
            current_wmo = int(_scalar(row[wmo_col]))
        except Exception:
            continue

        val_day = _scalar(row[day_col])
        val_night = _scalar(row[night_col])

        raw_day = "" if val_day is None or pd.isna(val_day) else str(val_day).strip()
        raw_night = "" if val_night is None or pd.isna(val_night) else str(val_night).strip()

        day_full = _prep(raw_day, last_day_full)
        night_full = _prep(raw_night, last_night_full)

        if day_full:
            maps_day[current_wmo] = day_full
            last_day_full = day_full
        if night_full:
            maps_night[current_wmo] = night_full
            last_night_full = night_full

    return {"day": maps_day, "night": maps_night}


def wmo_to_foreca_code(
    code: int | None,
    is_day: bool,
    pop: int | None = None,
    temp_c: float | None = None,
    cloudcover: int | None = None,
) -> str:
    """
    Päämäppäys, sama logiikka kuin alkuperäisessä tiedostossa.
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

    # fallback: pilvisyyden mukaan
    key = cloud_icon_from_cover(cloudcover, is_day)
    trace_map(code, is_day, pop, temp_c, cloudcover, key, "fallback: cloudcover")
    return key


def wmo_to_icon_key(code: int | None, is_day: bool) -> str:
    """
    Tämä oli alkuperäisen tiedoston loppupäässä – jätetään se tänne samaan "mapping"-pakettiin.
    """
    if code is None:
        return "na"
    if code == 0:
        return "clear-day" if is_day else "clear-night"
    if code in (1, 2):
        return "partly-cloudy-day" if is_day else "partly-cloudy-night"
    if code == 3:
        return "cloudy"
    if code in (45, 48):
        return "fog"
    if code in (51, 53, 55, 56, 57):
        return "drizzle"
    if code in (61, 63, 65, 80, 81, 82):
        return "rain"
    if code in (66, 67):
        return "freezing-rain"
    if code in (71, 73, 75, 85, 86):
        return "snow"
    if code in (95, 96, 99):
        return "thunderstorm"
    return "na"
