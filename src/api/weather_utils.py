from __future__ import annotations

from typing import Any

import pandas as pd

from src.config import (
    CLOUD_T_ALMOST,
    CLOUD_T_CLEAR,
    CLOUD_T_MOSTLY,
    CLOUD_T_PARTLY,
)


def safe_cast(value: Any, type_: type) -> Any | None:
    """
    Turvallinen muunnos annetuksi tyypiksi (bool, int, float).
    Palauttaa None, jos arvoa ei voi järkevästi tulkita.
    """
    try:
        if value is None:
            return None

        # pandas Series tms.
        if hasattr(value, "iloc"):
            if len(value) == 0:  # type: ignore[arg-type]
                return None
            value = value.iloc[0]  # type: ignore[index]

        # pandas NA
        try:
            if pd.isna(value):
                return None
        except Exception:
            pass

        # numpy-scalar tms.
        if hasattr(value, "item"):
            value = value.item()  # type: ignore[assignment]

        # ---- bool ----
        if type_ is bool:
            if isinstance(value, bool):
                return value
            if isinstance(value, int | float):
                return bool(int(value))
            if isinstance(value, str):
                s = value.strip().lower()
                if s in ("true", "1", "yes"):
                    return True
                if s in ("false", "0", "no", ""):
                    return False
                try:
                    return bool(int(float(s)))
                except (ValueError, TypeError):
                    return None
            return bool(value)

        # ---- float ----
        if type_ is float:
            if isinstance(value, str):
                value = value.strip().replace(",", ".")
            return float(value)

        # ---- int ----
        if type_ is int:
            if isinstance(value, str):
                value = value.strip().replace(",", ".")
            return int(float(value))

        # ---- muu tyyppi ----
        return type_(value)

    except Exception:
        return None


# Vanhojen nimien aliakset (pidetään taaksepäin yhteensopivuus)
def as_bool(x: Any) -> bool | None:
    return safe_cast(x, bool)


def as_int(x: Any) -> int | None:
    return safe_cast(x, int)


def as_float(x: Any) -> float | None:
    return safe_cast(x, float)


def cloud_icon_from_cover(cover: Any, is_day: bool) -> str:
    """
    Fallback: valitse pilvi-ikoni pelkän pilvisyysprosentin ja päivä/yö -tiedon perusteella.
    Tämä oli aiemmin _cloud_icon_from_cover.
    """
    cov = safe_cast(cover, int)
    if cov is None:
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
