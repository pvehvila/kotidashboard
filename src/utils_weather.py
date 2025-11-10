# src/utils_weather.py
"""Weather-related utility functions for HomeDashboard."""

from src.config import (
    CLOUD_T_ALMOST,
    CLOUD_T_CLEAR,
    CLOUD_T_MOSTLY,
    CLOUD_T_PARTLY,
)


def _cloud_icon_from_cover(cover: int | None, is_day: bool) -> str:
    """Map cloud cover percentage to a Foreca-style icon code."""
    prefix = "d" if is_day else "n"
    cloud = 100 if cover is None else int(cover)

    if cloud < CLOUD_T_CLEAR:
        return f"{prefix}000"  # Clear
    if cloud < CLOUD_T_ALMOST:
        return f"{prefix}100"  # Almost clear
    if cloud < CLOUD_T_PARTLY:
        return f"{prefix}200"  # Partly cloudy
    if cloud < CLOUD_T_MOSTLY:
        return f"{prefix}300"  # Mostly cloudy
    return f"{prefix}400"  # Fully cloudy
