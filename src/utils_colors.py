# src/utils_colors.py
"""Color utility functions for HomeDashboard."""

from src.config import PRICE_HIGH_THR, PRICE_LOW_THR


def _color_by_thresholds(
    vals: list[float | None],
    low_thr: float = PRICE_LOW_THR,
    high_thr: float = PRICE_HIGH_THR,
) -> list[str]:
    """Generate a list of colors based on value thresholds for visualization."""
    colors: list[str] = []
    for value in vals:
        if value is None:
            colors.append("rgba(128,128,128,0.5)")  # Gray for None
        elif value < low_thr:
            colors.append("rgba(60,180,75,0.9)")  # Green
        elif value <= high_thr:
            colors.append("rgba(255,225,25,0.9)")  # Yellow
        else:
            colors.append("rgba(230,25,75,0.9)")  # Red
    return colors


def _color_for_value(
    value: float | None,
    low_thr: float = PRICE_LOW_THR,
    high_thr: float = PRICE_HIGH_THR,
) -> str:
    """Get a single color for a value based on thresholds."""
    return _color_by_thresholds([value], low_thr, high_thr)[0]
