import datetime as dt  # <-- TÄRKEÄ: dt = datetime
import json
from datetime import datetime
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


def _resolve_nameday_file() -> Path:
    """Palauta ensimmäinen olemassa oleva nimipäiväpolku configista."""
    for path in NAMEDAY_PATHS:
        try:
            if path and Path(path).exists():
                return Path(path)
        except Exception:
            continue
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


def _load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


@st.cache_data(ttl=CACHE_TTL_LONG)
def fetch_nameday_today(_cache_buster: int | None = None) -> str:
    """
    fetch -> transform -> return
    Tukee kahta rakennetta:
      1) {"11-11": ["Panu"]} tai {"11-11": "Panu"}
      2) {"nimipäivät": {"marraskuu": {"11": "Panu"}}}
    """
    try:
        path = _resolve_nameday_file()
        if not path.exists():
            return "—"

        data = _load_json(path)
        now = datetime.now(TZ)
        key_md = now.strftime("%m-%d")
        day_str = str(now.day)
        month_name = [
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
        ][now.month - 1]

        # 1) litteä muoto: {"11-11": [...]}
        if isinstance(data, dict) and key_md in data:
            names = data[key_md]
            if isinstance(names, list):
                return ", ".join(n.strip() for n in names if str(n).strip()) or "—"
            if isinstance(names, str) and names.strip():
                return names.strip()
            return "—"

        # 2) sisäkkäinen muoto: {"nimipäivät": {"marraskuu": {"11": "Panu"}}}
        root = data.get("nimipäivät") if isinstance(data, dict) else None
        if isinstance(root, dict):
            # avaimet voivat olla eri kirjainkoossa, joten vertaillaan lowerilla
            month_obj = next(
                (
                    v
                    for k, v in root.items()
                    if isinstance(k, str) and k.strip().lower() == month_name
                ),
                None,
            )
            if isinstance(month_obj, dict):
                names = month_obj.get(day_str)
                if isinstance(names, list):
                    return ", ".join(n.strip() for n in names if str(n).strip()) or "—"
                if isinstance(names, str) and names.strip():
                    return names.strip()

        return "—"
    except Exception as e:
        report_error("nameday: local json", e)
        return "—"


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
    out = {"holiday": None, "is_flag_day": False, "is_holiday": False}
    try:
        p = _resolve_first_existing(HOLIDAY_PATHS)
        if not p or not p.exists():
            return out

        data = _load_json(p)
        now = dt.datetime.now(TZ)
        key_md = now.strftime("%m-%d")
        key_iso = now.strftime("%Y-%m-%d")

        def parse_entry(entry: dict) -> dict:
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

        # dict-muoto
        if isinstance(data, dict):
            entry = data.get(key_md) or data.get(key_iso)
            if isinstance(entry, dict):
                return parse_entry(entry)
            return out

        # lista-muoto
        if isinstance(data, list):
            for item in data:
                if not isinstance(item, dict):
                    continue
                d = str(item.get("date") or "").strip()
                if d in (key_iso, key_md):
                    return parse_entry(item)
        return out
    except Exception as e:
        report_error("holiday: local json", e)
        return out


__all__ = [
    "TZ",
    "_resolve_nameday_file",
    "_resolve_first_existing",
    "fetch_nameday_today",
    "fetch_holiday_today",
]
