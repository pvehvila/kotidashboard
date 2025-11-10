"""
Sähkön pörssihinnan julkiset entrypointit.

Tämä tiedosto pidetään ohuehkona: varsinaiset haut, normalisoinnit ja lokit ovat
omissa moduuleissaan.
"""

from __future__ import annotations

from datetime import datetime

from src.api.electricity_service import (
    fetch_prices_for,
    try_fetch_prices,
    try_fetch_prices_15min,
)

Price15 = dict[str, datetime | float]

__all__ = [
    "try_fetch_prices",
    "try_fetch_prices_15min",
    "fetch_prices_for",
    "Price15",
]
