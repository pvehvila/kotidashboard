"""
Yhdistetty kalenteri-/nimipäivämoduuli.

Varsinainen logiikka on src.api.calendarissa, jotta olemassa olevat testit
(monkeypatch src.api.calendar.*) eivät rikkoudu.
"""

from src.api.calendar import (
    TZ,
    _resolve_first_existing,
    _resolve_nameday_file,
    fetch_holiday_today,
    fetch_nameday_today,
)

__all__ = [
    "TZ",
    "_resolve_nameday_file",
    "_resolve_first_existing",
    "fetch_nameday_today",
    "fetch_holiday_today",
]
