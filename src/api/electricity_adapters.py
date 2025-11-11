# src/api/electricity_adapters.py
from __future__ import annotations

import datetime as dt
from datetime import datetime

import requests

from src.api.electricity_log import log_raw_prices
from src.api.electricity_normalize import (
    normalize_prices_list,
    normalize_prices_list_15min,
)
from src.api.electricity_sources import (
    fetch_from_porssisahko_latest,
    fetch_from_sahkonhintatanaan,
    filter_latest_to_day,
)
from src.utils import report_error

# 15 min -rivin muoto
Price15 = dict[str, datetime | float]


def get_hourly_from_porssisahko(date_ymd: dt.date) -> list[dict[str, float]] | None:
    """
    Hakee pörssisähkö v2 -datasta tunnit annetulle päivälle.
    Palauttaa listan muotoa: [{"hour": 0, "cents": 5.3}, ...] tai None.
    """
    try:
        latest = fetch_from_porssisahko_latest()
        if not latest:
            return None

        per_hour = filter_latest_to_day(latest, date_ymd)
        if not per_hour:
            return None

        # lasketaan varttien keskiarvo tunnille
        out: list[dict[str, float]] = []
        for hour, vals in sorted(per_hour.items()):
            if not vals:
                continue
            out.append(
                {
                    "hour": hour,
                    "cents": sum(vals) / len(vals),
                }
            )
        return out

    except requests.HTTPError as e:
        # 400/404 = "ei tälle päivälle", ei tehdä virheraporttia
        if e.response is not None and e.response.status_code in (400, 404):
            return None
        report_error(f"prices: porssisahko {date_ymd.isoformat()}", e)
        return None
    except Exception as e:
        report_error(f"prices: porssisahko {date_ymd.isoformat()}", e)
        return None


def get_hourly_from_sahkonhintatanaan(date_ymd: dt.date) -> list[dict[str, float]] | None:
    """
    Hakee sahkonhintatanaan.fi:stä ja normalisoi saman muodon kuin yllä.
    """
    try:
        raw = fetch_from_sahkonhintatanaan(date_ymd)
        # logitetaan aina, jotta voidaan katsoa raakadataa myöhemmin
        log_raw_prices("sahkonhintatanaan", date_ymd, raw)
        prices = normalize_prices_list(raw, date_ymd)
        return prices
    except requests.HTTPError as e:
        if e.response is not None and e.response.status_code in (400, 404):
            return None
        report_error(f"prices: sahkonhintatanaan {date_ymd.isoformat()}", e)
        return None
    except Exception as e:
        report_error(f"prices: sahkonhintatanaan {date_ymd.isoformat()}", e)
        return None


def get_15min_from_porssisahko(date_ymd: dt.date) -> list[Price15] | None:
    """
    Yrittää saada suoraan pörssisähkö v2:n varttidatan tälle päivälle.
    Palauttaa valmiiksi normalize_prices_list_15min(...) -muotoisen listan tai None.
    """
    try:
        latest = fetch_from_porssisahko_latest()
        if not latest:
            return None

        out = normalize_prices_list_15min(latest, date_ymd)
        if not out:
            return None
        return out

    except Exception as e:
        # tähän ei yleensä pitäisi tulla HTTPErroria, mutta logitetaan kaikki
        report_error(f"prices: v2 15min {date_ymd.isoformat()}", e)
        return None
