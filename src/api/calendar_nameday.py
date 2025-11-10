# src/api/calendar_nameday.py
from __future__ import annotations

from datetime import datetime

import streamlit as st

from src.api.calendar_data import load_json, resolve_nameday_file
from src.config import CACHE_TTL_LONG, TZ
from src.utils import report_error


@st.cache_data(ttl=CACHE_TTL_LONG)
def fetch_nameday_today(_cache_buster: int | None = None) -> str:
    """
    Palauttaa tämän päivän nimipäivät merkkijonona, esim:
        "Aino"
        "Aino, Aini"

    Tämä säilyttää alkuperäisen kortin odottaman rajapinnan.
    """
    try:
        path = resolve_nameday_file()
        if not path.exists():
            return "—"

        data = load_json(path)
        now = datetime.now(TZ)
        key_md = now.strftime("%m-%d")
        day_str = str(now.day)

        # 1) yksinkertainen muoto: {"11-09": ["Teuvo", "Tero"]}
        if isinstance(data, dict) and key_md in data:
            names = data[key_md]
            if isinstance(names, list):
                return ", ".join(str(n).strip() for n in names if str(n).strip()) or "—"
            if isinstance(names, str) and names.strip():
                return names.strip()
            return "—"

        # 2) kuukausi -> päivä -muoto: {"nimipäivät": { "joulukuu": { "9": ["..."] } } }
        root = data.get("nimipäivät") if isinstance(data, dict) else None
        if isinstance(root, dict):
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
            month_obj = root.get(month_name)
            if isinstance(month_obj, dict):
                names = month_obj.get(day_str)
                if isinstance(names, list):
                    return ", ".join(str(n).strip() for n in names if str(n).strip()) or "—"
                if isinstance(names, str) and names.strip():
                    return names.strip()

        return "—"
    except Exception as e:
        report_error("nameday: load failed", e)
        return "—"
