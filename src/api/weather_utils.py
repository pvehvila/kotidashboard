from __future__ import annotations

from typing import Any

import pandas as pd

from src.config import (
    CLOUD_T_ALMOST,
    CLOUD_T_CLEAR,
    CLOUD_T_MOSTLY,
    CLOUD_T_PARTLY,
)


def _cast_to_bool(value: Any) -> bool | None:
    """Muunna annettu arvo bool-tyypiksi, tai palauta None jos ei järkevää tulkintaa."""
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

        # yritetään vielä tulkita numeerisena
        try:
            return bool(int(float(s)))
        except (ValueError, TypeError):
            return None

    # viimeinen fallback: Pythonin oma bool-tulkinta
    return bool(value)


def _cast_to_float(value: Any) -> float | None:
    """Muunna annettu arvo float-tyypiksi, tai palauta None jos muunnos epäonnistuu."""
    if isinstance(value, str):
        value = value.strip().replace(",", ".")

    try:
        return float(value)  # type: ignore[arg-type]
    except Exception:
        return None


def _cast_to_int(value: Any) -> int | None:
    """Muunna annettu arvo int-tyypiksi, tai palauta None jos muunnos epäonnistuu."""
    if isinstance(value, str):
        value = value.strip().replace(",", ".")

    try:
        return int(float(value))  # type: ignore[arg-type]
    except Exception:
        return None


def _normalize_scalar(value: Any) -> Any | None:
    """
    Yhtenäinen esikäsittely eri lähdetyypeille:
    - None → None
    - pandas Series/DataFrame → ensimmäinen alkio tai None jos tyhjä
    - pandas NA → None
    - numpy-scalar tms. → .item()
    """
    if value is None:
        return None

    # pandas Series tms.
    if hasattr(value, "iloc"):
        try:
            if len(value) == 0:  # type: ignore[arg-type]
                return None
            value = value.iloc[0]  # type: ignore[index]
        except Exception:
            # jos value ei käyttäydy odotetusti, jatketaan sellaisenaan
            pass

    # pandas NA
    try:
        if pd.isna(value):
            return None
    except Exception:
        # jos pd.isna ei osaa käsitellä tyyppiä, jatketaan ilman tätä tarkistusta
        pass

    # numpy-scalar tms.
    if hasattr(value, "item"):
        try:
            value = value.item()  # type: ignore[assignment]
        except Exception:
            # jos item() ei toimi, käytetään alkuperäistä arvoa
            pass

    return value


def safe_cast(value: Any, type_: type) -> Any | None:
    """
    Turvallinen muunnos annetuksi tyypiksi (bool, int, float, str, ...).

    Vastuut:
    - normalisoi arvon (_normalize_scalar)
    - valitsee oikean _cast_* -funktion per primitiivityyppi
    - fallback: type_(value) muille tyypeille
    - palauttaa None, jos muunnos ei onnistu
    """
    try:
        value = _normalize_scalar(value)
        if value is None:
            return None

        dispatch = {
            bool: _cast_to_bool,
            int: _cast_to_int,
            float: _cast_to_float,
        }

        caster = dispatch.get(type_)
        if caster is not None:
            return caster(value)

        if type_ is str:
            # eksplisiittinen haara, jos halutaan selkeyttä str-muunnokselle
            try:
                return str(value)
            except Exception:
                return None

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
