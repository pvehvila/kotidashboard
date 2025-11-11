from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.paths import DATA


def _read_wmo_mapping(path: str | None = None) -> pd.DataFrame:
    """
    Lukee WMO → Foreca -mäppäyksen mahdollisista tiedostoista.

    Palauttaa tyhjän DataFramen jos mitään ei löydy.
    """
    candidates: list[Path] = []

    if path:
        candidates.append(Path(path))

    root = Path(__file__).parent
    # samat nimet kuin aiemmin
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
            # seuraavaan kandidaattiin
            continue

    return pd.DataFrame()


def _scalar(cell: Any) -> Any:
    # sama apu kuin aiemmin
    if hasattr(cell, "iloc"):
        return cell.iloc[0] if len(cell) > 0 else None  # type: ignore[arg-type]
    if hasattr(cell, "item"):
        try:
            return cell.item()
        except Exception:
            return cell
    return cell


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
    Palauttaa muodon:
        {"day": {wmo: "d100"}, "night": {wmo: "n200"}}
    """
    if df is None:
        df = _read_wmo_mapping()

    if df.empty:
        return {"day": {}, "night": {}}

    maps_day: dict[int, str] = {}
    maps_night: dict[int, str] = {}
    last_day_full: str | None = None
    last_night_full: str | None = None

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
