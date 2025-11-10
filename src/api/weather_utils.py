from __future__ import annotations

from typing import Any

import pandas as pd

from src.config import (
    CLOUD_T_ALMOST,
    CLOUD_T_CLEAR,
    CLOUD_T_MOSTLY,
    CLOUD_T_PARTLY,
)


def as_bool(x: Any) -> bool | None:
    try:
        if x is None:
            return None

        if hasattr(x, "iloc"):
            if len(x) == 0:  # type: ignore[arg-type]
                return None
            x = x.iloc[0]  # type: ignore[index]

        # pandas NA
        try:
            if pd.isna(x):
                return None
        except Exception:
            pass

        if hasattr(x, "item"):
            x = x.item()  # type: ignore[assignment]

        if isinstance(x, bool):
            return x
        if isinstance(x, (int | float)):
            return bool(int(x))
        if isinstance(x, str):
            s = x.strip().lower()
            if s in ("true", "1", "yes"):
                return True
            if s in ("false", "0", "no", ""):
                return False
            try:
                return bool(int(float(s)))
            except (ValueError, TypeError):
                return None

        return bool(x)
    except Exception:
        return None


def as_float(x: Any) -> float | None:
    try:
        if x is None:
            return None

        if hasattr(x, "iloc"):
            if len(x) == 0:  # type: ignore[arg-type]
                return None
            x = x.iloc[0]  # type: ignore[index]

        try:
            if pd.isna(x):
                return None
        except Exception:
            pass

        if hasattr(x, "item"):
            x = x.item()  # type: ignore[assignment]

        return float(x)
    except Exception:
        return None


def as_int(x: Any) -> int | None:
    try:
        if x is None:
            return None

        if hasattr(x, "iloc"):
            if len(x) == 0:  # type: ignore[arg-type]
                return None
            x = x.iloc[0]  # type: ignore[index]

        try:
            if pd.isna(x):
                return None
        except Exception:
            pass

        if hasattr(x, "item"):
            x = x.item()  # type: ignore[assignment]

        return int(float(x))
    except Exception:
        return None


def cloud_icon_from_cover(cover: Any, is_day: bool) -> str:
    """
    Fallback: valitse pilvi-ikoni pelkän pilvisyysprosentin ja päivä/yö -tiedon perusteella.
    Tämä oli aiemmin _cloud_icon_from_cover.
    """

    # mahdollisimman pieni sisäinen apu:
    def _ensure_int(x: Any) -> int:
        if isinstance(x, pd.Series):
            if x.empty:
                raise TypeError("empty Series")
            x = x.iloc[0]
        if isinstance(x, str):
            s = x.strip().replace(",", ".")
            return int(float(s))
        return int(float(x))

    try:
        cov = _ensure_int(cover)
    except Exception:
        cov = 100

    prefix = "d" if is_day else "n"

    if cov < CLOUD_T_CLEAR:
        return f"{prefix}000"
    if cov < CLOUD_T_ALMOST:
        return f"{prefix}100"
    if cov < CLOUD_T_PARTLY:
        return f"{prefix}200"
    if cov < CLOUD_T_MOSTLY:
        return f"{prefix}300"
    return f"{prefix}400"
