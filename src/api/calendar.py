# src/api/calendar.py
"""
Säilytetty yhteensopivuuskerros.

Varsinainen logiikka on src.api.calendar_nameday:ssä, jotta koodi ei duplikoidu
ja UI-koodi voi käyttää yhtä public-pintaa.
"""

from src.api.calendar_nameday import (
    TZ,
    _load_nameday_data,
    _pick_today_name,
    _resolve_first_existing,
    _resolve_nameday_file,
    fetch_holiday_today,
    fetch_nameday_today,
)

__all__ = [
    "TZ",
    "_resolve_nameday_file",
    "_resolve_first_existing",
    "_load_nameday_data",
    "_pick_today_name",
    "fetch_nameday_today",
    "fetch_holiday_today",
]
