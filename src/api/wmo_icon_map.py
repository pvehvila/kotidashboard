from __future__ import annotations

from typing import Final

# WMO-koodi → (päiväikoni, yöikoni)
_ICON_BY_WMO: Final[dict[int, tuple[str, str]]] = {
    0: ("clear-day", "clear-night"),
    1: ("partly-cloudy-day", "partly-cloudy-night"),
    2: ("partly-cloudy-day", "partly-cloudy-night"),
    3: ("cloudy", "cloudy"),
    45: ("fog", "fog"),
    48: ("fog", "fog"),
    51: ("drizzle", "drizzle"),
    53: ("drizzle", "drizzle"),
    55: ("drizzle", "drizzle"),
    56: ("drizzle", "drizzle"),
    57: ("drizzle", "drizzle"),
    61: ("rain", "rain"),
    63: ("rain", "rain"),
    65: ("rain", "rain"),
    80: ("rain", "rain"),
    81: ("rain", "rain"),
    82: ("rain", "rain"),
    66: ("freezing-rain", "freezing-rain"),
    67: ("freezing-rain", "freezing-rain"),
    71: ("snow", "snow"),
    73: ("snow", "snow"),
    75: ("snow", "snow"),
    85: ("snow", "snow"),
    86: ("snow", "snow"),
    95: ("thunderstorm", "thunderstorm"),
    96: ("thunderstorm", "thunderstorm"),
    99: ("thunderstorm", "thunderstorm"),
}


def wmo_to_icon_key(code: int | None, is_day: bool) -> str:
    """
    Yksinkertainen WMO → "sääikoniavain" -mäppäys.
    """
    if code is None:
        return "na"

    icons = _ICON_BY_WMO.get(code)
    if icons is None:
        return "na"

    day_icon, night_icon = icons
    return day_icon if is_day else night_icon
