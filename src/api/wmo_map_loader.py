from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.paths import DATA

# ---------------------------------------------------------
# 1) TIEDOSTONLUKU – vain I/O
# ---------------------------------------------------------


def read_raw_wmo_mapping(path: str | None = None) -> pd.DataFrame:
    """
    Etsii ja lukee WMO→Foreca -mäppäysdatan.

    Ei tee mitään validointia tai transformaatioita.
    Palauttaa tyhjän DataFramen jos mitään ei löydy.
    """
    candidates: list[Path] = []

    if path:
        candidates.append(Path(path))

    root = Path(__file__).parent
    candidates.extend(
        [
            root / "wmo_foreca_map.xlsx",
            root / "wmo_foreca_map.csv",
            root / "mappings.xlsx",
            root / "mappings.csv",
            DATA / "WMO_Foreca-koodit.xlsx",
        ]
    )

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


# ---------------------------------------------------------
# 2) APUMETODIT – scalar / tyhjäarvot / viimeinen arvo
# ---------------------------------------------------------


def _scalar(cell: Any) -> Any:
    if hasattr(cell, "iloc"):
        return cell.iloc[0] if len(cell) > 0 else None  # type: ignore[arg-type]
    if hasattr(cell, "item"):
        try:
            return cell.item()
        except Exception:
            return cell
    return cell


def _normalize_cell(value: Any) -> str:
    if value is None or pd.isna(value):
        return ""
    return str(value).strip()


# ---------------------------------------------------------
# 3) TRANSFORMAATIO – pelkkä rivien käsittely DataFramesta
# ---------------------------------------------------------


def build_wmo_foreca_maps(
    df: pd.DataFrame,
    wmo_col: str,
    day_col: str,
    night_col: str,
) -> dict[str, dict[int, str]]:
    """
    Muuntaa DataFramen lopulliseen muotoon:

        {"day": {wmo: "d100"}, "night": {wmo: "n200"}}

    Ei lue tiedostoja eikä tee fallbackeja.
    """
    if df.empty:
        return {"day": {}, "night": {}}

    maps_day: dict[int, str] = {}
    maps_night: dict[int, str] = {}
    last_day_full: str | None = None
    last_night_full: str | None = None

    for _, row in df.iterrows():
        # WMO-koodi
        try:
            current_wmo = int(_scalar(row[wmo_col]))
        except Exception:
            continue

        # Raaka-arvot
        raw_day = _normalize_cell(_scalar(row[day_col]))
        raw_night = _normalize_cell(_scalar(row[night_col]))

        # Viimeisin täysi arvo kulkee riviltä toiselle
        day_full = raw_day or last_day_full
        night_full = raw_night or last_night_full

        if day_full:
            maps_day[current_wmo] = day_full
            last_day_full = day_full

        if night_full:
            maps_night[current_wmo] = night_full
            last_night_full = night_full

    return {"day": maps_day, "night": maps_night}


# ---------------------------------------------------------
# 4) JULKINEN FUNKTIO – ohut orchestrator (A/B-taso)
# ---------------------------------------------------------


def load_wmo_foreca_map(
    df: pd.DataFrame | None = None,
    wmo_col: str = "wmo",
    day_col: str = "day",
    night_col: str = "night",
) -> dict[str, dict[int, str]]:
    """
    Lataa WMO→Foreca -mäppäyksen ja muuntaa
    sen dashboardin käyttämään muotoon.

    CC-taso: matala, pelkkä orkestrointi.
    """
    df = df if df is not None else read_raw_wmo_mapping()
    return build_wmo_foreca_maps(df, wmo_col, day_col, night_col)
