# src/api/electricity_service.py
from __future__ import annotations

import datetime as dt
from datetime import datetime

import streamlit as st

from src.api.electricity_adapters import (
    get_15min_from_porssisahko,
    get_hourly_from_porssisahko,
    get_hourly_from_sahkonhintatanaan,
)
from src.api.electricity_normalize import (
    expand_hourly_to_15min,
    normalize_prices_list_15min,
)
from src.config import CACHE_TTL_MED

# sama tyyppi kuin aiemmin
Price15 = dict[str, datetime | float]


def _has_any_timestamp(items: list[dict]) -> bool:
    """
    Tarkistaa, onko tuntidatassa jo aikaleimoja.
    Jos on, voimme ajaa suoraan normalize_prices_list_15min(...).
    """
    ts_keys = (
        "time",
        "Time",
        "timestamp",
        "Timestamp",
        "datetime",
        "DateTime",
        "start",
        "Start",
        "startDate",
        "endDate",
    )
    return any(any(k in item for k in ts_keys) for item in items)


@st.cache_data(ttl=CACHE_TTL_MED)
def try_fetch_prices(date_ymd: dt.date) -> list[dict[str, float]] | None:
    """
    Julkinen entry point: yritä hakea tunnit.
    Palauttaa None jos kumpikaan lähde ei onnistu.
    """
    prices = fetch_prices_for(date_ymd)
    return prices if prices else None


@st.cache_data(ttl=CACHE_TTL_MED)
def try_fetch_prices_15min(date_ymd: dt.date) -> list[Price15] | None:
    """
    15 min -entry point:
    1) yritä suora v2-varttidata adapterista
    2) jos ei, hae tuntidata ja laajenna
    """
    # 1) suora 15 min pörssisähköstä
    v2_items = get_15min_from_porssisahko(date_ymd)
    if v2_items:
        return v2_items

    # 2) fallback: hae tunnit ja laske niistä
    base_items = fetch_prices_for(date_ymd)
    if not base_items:
        return None

    if _has_any_timestamp(base_items):
        # jos tunnit sisältävät ts:t, voimme normalisoida suoraan
        return normalize_prices_list_15min(base_items, date_ymd)

    # muutoin venytetään 4×
    return expand_hourly_to_15min(base_items, date_ymd)


def fetch_prices_for(date_ymd: dt.date) -> list[dict[str, float]]:
    """
    Orkestroi tuntihintojen hakemisen:
    1) pörssisähkö v2 (tunti)
    2) sahkonhintatanaan
    Palauttaa aina listan (voi olla tyhjä).
    """
    # 1) ensisijainen lähde
    prices = get_hourly_from_porssisahko(date_ymd)
    if prices:
        return prices

    # 2) varalähde
    prices = get_hourly_from_sahkonhintatanaan(date_ymd)
    if prices:
        return prices

    # 3) mitään ei saatu
    return []
