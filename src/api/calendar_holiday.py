# src/api/calendar_holiday.py
from __future__ import annotations

import datetime as dt
from typing import Any

import streamlit as st

from src.api.calendar_data import load_json, resolve_holiday_file
from src.config import CACHE_TTL_LONG, TZ
from src.utils import report_error


def _normalize_holiday_entry(entry: dict[str, Any]) -> dict[str, Any]:
    """
    Yhtenäistää eri formaatit kortin odottamaan muotoon.
    """
    name = entry.get("holiday") or entry.get("name") or entry.get("title") or ""
    name = str(name).strip()
    return {
        "holiday": name or None,
        "is_flag_day": bool(entry.get("is_flag_day") or entry.get("flag")),
        "is_holiday": bool(entry.get("is_holiday", True)),
    }


@st.cache_data(ttl=CACHE_TTL_LONG)
def fetch_holiday_today(_cache_buster: int | None = None) -> dict[str, Any]:
    """
    Palauttaa aina dictin, jolla kortti pärjää:
        {
            "holiday": str|None,
            "is_flag_day": bool,
            "is_holiday": bool
        }
    """
    out: dict[str, Any] = {"holiday": None, "is_flag_day": False, "is_holiday": False}
    try:
        p = resolve_holiday_file()
        if not p or not p.exists():
            return out

        data = load_json(p)
        today = dt.datetime.now(TZ)
        key_md = today.strftime("%m-%d")
        key_iso = today.strftime("%Y-%m-%d")

        # dict-muoto
        if isinstance(data, dict):
            entry = data.get(key_iso) or data.get(key_md)
            if isinstance(entry, dict):
                return _normalize_holiday_entry(entry)
            if isinstance(entry, str):
                return {
                    "holiday": entry.strip(),
                    "is_flag_day": False,
                    "is_holiday": True,
                }
            return out

        # listamuoto
        if isinstance(data, list):
            for row in data:
                if not isinstance(row, dict):
                    continue
                d = str(row.get("date") or "").strip()
                if d in (key_iso, key_md):
                    return _normalize_holiday_entry(row)

        return out
    except Exception as e:
        report_error("holiday: load failed", e)
        return out
