# src/api/nameday.py
from __future__ import annotations

import json
import os
from datetime import date
from src.paths import asset_path


def _find_existing_json() -> str:
    """Etsi nimipäivädata. Yritetään ensin nimipäiviä, sitten pyhiä."""
    candidates = [
        "data/nimipaivat_fi.json",
        "data/namedays_fi.json",
        "data/pyhat_fi.json",
    ]

    for rel in candidates:
        assets_path = asset_path(rel)
        if os.path.exists(assets_path):
            return str(assets_path)
        local_path = os.path.join("data", os.path.basename(rel))
        if os.path.exists(local_path):
            return str(local_path)

    raise FileNotFoundError("None of nimipaivat_fi.json / namedays_fi.json / pyhat_fi.json found")


def _load_json() -> dict:
    path = _find_existing_json()
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def fetch_nameday_today() -> str:
    """
    Palauttaa tämän päivän nimipäivät merkkijonona, esim. 'Panu'.
    Tukee nimipaivat_fi.json- ja pyhat_fi.json -rakenteita.
    """
    data = _load_json()
    today = date.today()

    # 1️⃣ Jos data on nimipaivat_fi.json-rakennetta
    if "nimipäivät" in data:
        months = [
            "tammikuu", "helmikuu", "maaliskuu", "huhtikuu",
            "toukokuu", "kesäkuu", "heinäkuu", "elokuu",
            "syyskuu", "lokakuu", "marraskuu", "joulukuu",
        ]
        month_name = months[today.month - 1]
        day_str = str(today.day)
        try:
            names = data["nimipäivät"][month_name][day_str]
            return names or ""
        except KeyError:
            return ""

    # 2️⃣ Jos data on pyhat_fi.json-rakennetta
    key = today.strftime("%Y-%m-%d")
    if key in data:
        info = data[key]
        if isinstance(info, dict):
            return info.get("name", "")
        elif isinstance(info, str):
            return info
    return ""
