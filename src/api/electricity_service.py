from __future__ import annotations

import datetime as dt
from datetime import datetime

import requests
import streamlit as st

from src.api.electricity_log import log_raw_prices
from src.api.electricity_normalize import (
    expand_hourly_to_15min,
    normalize_prices_list,
    normalize_prices_list_15min,
)
from src.api.electricity_sources import (
    fetch_from_porssisahko_latest,
    fetch_from_sahkonhintatanaan,
    filter_latest_to_day,
)
from src.config import CACHE_TTL_MED
from src.utils import report_error

Price15 = dict[str, datetime | float]


@st.cache_data(ttl=CACHE_TTL_MED)
def try_fetch_prices(date_ymd: dt.date) -> list[dict[str, float]] | None:
    """
    Palauttaa päivän TUNTIhinnat [{"hour": 0, "cents": 5.3}, ...] tai None jos ei saada mitään.
    """
    try:
        return fetch_prices_for(date_ymd)
    except requests.HTTPError as e:
        if e.response and e.response.status_code in (400, 404):
            return None
        report_error(f"prices: fetch {date_ymd.isoformat()}", e)
        return None
    except Exception as e:
        report_error(f"prices: fetch {date_ymd.isoformat()}", e)
        return None


@st.cache_data(ttl=CACHE_TTL_MED)
def try_fetch_prices_15min(date_ymd: dt.date) -> list[Price15] | None:
    """
    15 min -taso:
    1) yritä suoraan v2:n vartteja
    2) jos ei, hae tuntidata ja laajenna
    """
    # 1) suora v2
    try:
        v2_items = fetch_from_porssisahko_latest()
        if v2_items:
            out = normalize_prices_list_15min(v2_items, date_ymd)
            if out:
                return out
    except Exception as e:
        report_error(f"prices: v2 15min {date_ymd.isoformat()}", e)

    # 2) fallback tuntidataan
    base_items = fetch_prices_for(date_ymd)
    if not base_items:
        return None

    # jos tuntidatassa on jo aikaleimat, muutetaan suoraan
    has_ts = any(
        any(
            k in item
            for k in (
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
        )
        for item in base_items
    )
    if has_ts:
        return normalize_prices_list_15min(base_items, date_ymd)

    return expand_hourly_to_15min(base_items, date_ymd)


def fetch_prices_for(date_ymd: dt.date) -> list[dict[str, float]]:
    """
    Yrittää ensin porssisähkö v2 -> tunti, sitten sahkonhintatanaan.
    Vastaa vanhaa `fetch_prices_for(...)`-funktiota.
    """
    # 1) porssisähkö v2 → tunti
    try:
        latest = fetch_from_porssisahko_latest()
        if latest:
            per_hour = filter_latest_to_day(latest, date_ymd)
            if per_hour:
                out = [
                    {"hour": hour, "cents": sum(vals) / len(vals)}
                    for hour, vals in sorted(per_hour.items())
                    if vals
                ]
                return out
    except requests.HTTPError as e:
        if not (e.response and e.response.status_code in (400, 404)):
            report_error(f"prices: porssisahko {date_ymd.isoformat()}", e)
    except Exception as e:
        report_error(f"prices: porssisahko {date_ymd.isoformat()}", e)

    # 2) sahkonhintatanaan
    try:
        raw = fetch_from_sahkonhintatanaan(date_ymd)
        log_raw_prices("sahkonhintatanaan", date_ymd, raw)
        prices = normalize_prices_list(raw, date_ymd)
        return prices
    except requests.HTTPError as e:
        if not (e.response and e.response.status_code in (400, 404)):
            report_error(f"prices: sahkonhintatanaan {date_ymd.isoformat()}", e)
    except Exception as e:
        report_error(f"prices: sahkonhintatanaan {date_ymd.isoformat()}", e)

    return []
