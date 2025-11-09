# src/api/calendar.py
"""
Kalenterirajapinta (nimipäivät + pyhäpäivät).
Pidetään tässä vain julkiset entrypointit, logiikka on omissa moduuleissaan.
"""

from __future__ import annotations

import datetime as dt
from typing import Any

from src.api.calendar_data import (
    load_json,
    resolve_holiday_file,
    resolve_nameday_file,
)
from src.api.calendar_holiday import fetch_holiday_today
from src.api.calendar_nameday import fetch_nameday_today

__all__ = [
    "fetch_nameday_today",
    "fetch_holiday_today",
    "resolve_nameday_file",
    "resolve_holiday_file",
    "load_json",
    "get_nameday_and_holiday",
]


def get_nameday_and_holiday(today: dt.date | None = None) -> dict[str, Any]:
    """
    Yhdistelmä, jos UI haluaa molemmat samalla kertaa.
    """
    # today-param on mukana vain API-yhtenäisyyden vuoksi, ei pakollinen.
    return {
        "nameday": fetch_nameday_today(),
        "holiday": fetch_holiday_today(),
    }
