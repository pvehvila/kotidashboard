from __future__ import annotations

from typing import Any

MAP_TRACE_ENABLED = False
_MAP_TRACE: list[dict[str, Any]] = []


def trace_map(
    wmo: int | None,
    is_day: bool,
    pop: int | None,
    temp_c: float | None,
    cloudcover: int | None,
    chosen_key: str,
    reason: str,
) -> None:
    if not MAP_TRACE_ENABLED:
        return
    try:
        _MAP_TRACE.append(
            {
                "wmo": wmo,
                "is_day": is_day,
                "pop": pop,
                "temp_c": temp_c,
                "cloudcover": cloudcover,
                "key": chosen_key,
                "reason": reason,
            }
        )
        if len(_MAP_TRACE) > 200:
            del _MAP_TRACE[:-120]
    except Exception:
        # tracing ei saa kaataa dashboardia
        pass


def get_map_trace() -> list[dict[str, Any]]:
    return list(_MAP_TRACE)


def clear_map_trace() -> None:
    _MAP_TRACE.clear()
