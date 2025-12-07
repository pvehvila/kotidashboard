# src/api/calendar_nameday.py
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

import streamlit as st

from src.config import (
    CACHE_TTL_LONG,
    HOLIDAY_PATHS,
    NAMEDAY_FILE,
    NAMEDAY_PATHS,
    TZ,
)
from src.utils import report_error

# --- perus apurit ---------------------------------------------------------


def _resolve_nameday_file() -> Path:
    """
    Palauta nimipäivätiedoston polku.

    - Jos NAMEDAY_PATHS ei ole tyhjä, käytetään *ainoastaan* sitä listaa.
      Tällöin, jos mikään polku ei ole olemassa, palautetaan listan
      ensimmäinen polku (joka voi olla olematon), eikä pudota oletukseen.
    - Jos lista on tyhjä, käytetään NAMEDAY_FILE-oletusta.
    """
    if NAMEDAY_PATHS:
        return _resolve_first_existing(NAMEDAY_PATHS)
    return Path(NAMEDAY_FILE)


def _resolve_first_existing(paths) -> Path:
    """Palauta ensimmäinen olemassa oleva polku annetusta listasta."""
    for p in paths:
        try:
            pp = Path(p)
            if pp.exists():
                return pp
        except Exception:
            continue
    return Path(paths[0]) if paths else Path()


def _load_nameday_data(path: Path):
    """Lataa JSONin ja palauttaa python-datan."""
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


# --- varsinainen nimipäivälogiikka ----------------------------------------


_MONTHS_FI = [
    "tammikuu",
    "helmikuu",
    "maaliskuu",
    "huhtikuu",
    "toukokuu",
    "kesäkuu",
    "heinäkuu",
    "elokuu",
    "syyskuu",
    "lokakuu",
    "marraskuu",
    "joulukuu",
]


def _normalize_nameday_value(names) -> str:
    """Normalisoi nimipäiväkentän muodosta riippumatta."""
    if isinstance(names, list):
        joined = ", ".join(n.strip() for n in names if str(n).strip())
        return joined or "—"
    if isinstance(names, str) and names.strip():
        return names.strip()
    return "—"


def _pick_today_name_flat(data, today: dt.datetime) -> str:
    """Poimii tämän päivän nimipäivän litteästä rakenteesta."""
    if not isinstance(data, dict):
        return "—"

    key_md = today.strftime("%m-%d")
    if key_md not in data:
        return "—"

    names = data[key_md]
    return _normalize_nameday_value(names)


def _pick_today_name_nested(data, today: dt.datetime) -> str:
    """Poimii tämän päivän nimipäivän sisäkkäisestä rakenteesta."""
    if not isinstance(data, dict):
        return "—"

    root = data.get("nimipäivät")
    if not isinstance(root, dict):
        return "—"

    month_name = _MONTHS_FI[today.month - 1]
    day_str = str(today.day)

    # avaimet voivat olla eri kirjainkoossa
    month_obj = next(
        (v for k, v in root.items() if isinstance(k, str) and k.strip().lower() == month_name),
        None,
    )
    if not isinstance(month_obj, dict):
        return "—"

    names = month_obj.get(day_str)
    return _normalize_nameday_value(names)


def _pick_today_name(data, today: dt.datetime) -> str:
    """
    Poimii tämän päivän nimipäivän kahdesta yleisestä rakenteesta:

    1) litteä:
       {"11-11": ["Panu"]} tai {"11-11": "Panu"}

    2) sisäkkäinen:
       {"nimipäivät": {"marraskuu": {"11": "Panu"}}}
    """
    if not isinstance(data, dict):
        return "—"

    name = _pick_today_name_flat(data, today)
    if name != "—":
        return name

    return _pick_today_name_nested(data, today)


@st.cache_data(ttl=CACHE_TTL_LONG)
def fetch_nameday_today(_cache_buster: int | None = None) -> str:
    """
    Ohut julkinen funktio:
      1) valitse lähdetiedosto
      2) lataa data
      3) poimi tämän päivän nimi
    """
    try:
        path = _resolve_nameday_file()
        if not path.exists():
            return "—"
        data = _load_nameday_data(path)
        now = dt.datetime.now(TZ)
        return _pick_today_name(data, now)
    except Exception as e:
        report_error("nameday: local json", e)
        return "—"


# --- pyhä-/liputuspäivät samaan moduuliin ---------------------------------


def _default_holiday_result() -> dict:
    return {"holiday": None, "is_flag_day": False, "is_holiday": False}


def _parse_holiday_entry(entry: dict) -> dict:
    """Muuntaa raakadatadictin normalisoiduksi holiday-dictiksi."""
    name = entry.get("name")
    hol_field = entry.get("holiday")

    is_holiday = bool(entry.get("is_holiday")) or (
        isinstance(hol_field, bool) and hol_field is True
    )

    # joskus nimi on vain "holiday"-kentässä
    if not name and isinstance(hol_field, str) and hol_field.strip():
        name = hol_field.strip()

    is_flag = bool(entry.get("flag") or entry.get("is_flag_day"))

    return {
        "holiday": (name.strip() if isinstance(name, str) and name.strip() else None),
        "is_flag_day": is_flag,
        "is_holiday": is_holiday,
    }


def _pick_holiday_entry_for_today(data, today: dt.datetime) -> dict | None:
    """Valitsee tälle päivälle sopivan holiday-entryn dict- tai lista-rakenteesta."""
    key_md = today.strftime("%m-%d")
    key_iso = today.strftime("%Y-%m-%d")

    # dict-muoto
    if isinstance(data, dict):
        entry = data.get(key_md) or data.get(key_iso)
        return entry if isinstance(entry, dict) else None

    # lista-muoto
    if isinstance(data, list):
        for item in data:
            if not isinstance(item, dict):
                continue
            d = str(item.get("date") or "").strip()
            if d in (key_iso, key_md):
                return item

    return None


@st.cache_data(ttl=CACHE_TTL_LONG)
def fetch_holiday_today(_cache_buster: int | None = None) -> dict:
    """
    Palauttaa dictin:
      {
        "holiday": str | None,
        "is_flag_day": bool,
        "is_holiday": bool,
      }
    """
    out = _default_holiday_result()
    try:
        p = _resolve_first_existing(HOLIDAY_PATHS)
        if not p or not p.exists():
            return out

        with p.open("r", encoding="utf-8") as f:
            data = json.load(f)

        now = dt.datetime.now(TZ)
        entry = _pick_holiday_entry_for_today(data, now)
        if not isinstance(entry, dict):
            return out

        return _parse_holiday_entry(entry)
    except Exception as e:
        report_error("holiday: local json", e)
        return out


__all__ = [
    "TZ",
    "_resolve_nameday_file",
    "_resolve_first_existing",
    "_load_nameday_data",
    "_pick_today_name",
    "fetch_nameday_today",
    "fetch_holiday_today",
]
