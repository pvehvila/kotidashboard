import json
from datetime import datetime

import requests
import streamlit as st

from src.api.http import http_get_json
from src.config import (
    ATH_CACHE_FILE,
    CACHE_TTL_LONG,
    CACHE_TTL_MED,
    CACHE_TTL_SHORT,
    HTTP_TIMEOUT_S,
    TZ,
)
from src.utils import report_error


@st.cache_data(ttl=CACHE_TTL_SHORT)
def fetch_btc_eur() -> dict[str, float | None]:
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=eur&include_24hr_change=true"
    data = http_get_json(url)
    btc = data.get("bitcoin", {})
    return {"price": btc.get("eur"), "change": btc.get("eur_24h_change")}


@st.cache_data(ttl=CACHE_TTL_MED)
def _coingecko_market_chart(days: int, vs: str = "eur") -> list[tuple[datetime, float]]:
    # 1) CoinGecko
    try:
        url = f"https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency={vs}&days={days}"
        data = http_get_json(url, timeout=HTTP_TIMEOUT_S)
        prices = data.get("prices", []) or []
        if prices:
            target_points = max(24 * int(days), 24)
            keep_every = max(len(prices) // target_points, 1)
            out: list[tuple[datetime, float]] = []
            for i, (ts_ms, val) in enumerate(prices):
                if i % keep_every != 0:
                    continue
                ts = datetime.fromtimestamp(ts_ms / 1000, tz=TZ)
                out.append((ts, float(val)))
            out.sort(key=lambda x: x[0])
            if out:
                return out
    except Exception as e:
        report_error("btc: market_chart coingecko", e)

    # 2) CryptoCompare fallback tuntitasolla
    try:
        limit = min(24 * int(max(1, days)), 2000)
        alt_url = f"https://min-api.cryptocompare.com/data/v2/histohour?fsym=BTC&tsym={vs.upper()}&limit={limit}"
        alt = http_get_json(alt_url, timeout=HTTP_TIMEOUT_S)
        rows = alt.get("Data", {}).get("Data", []) or []
        if rows:
            out = [
                (
                    datetime.fromtimestamp(r["time"], tz=TZ),
                    float(r.get("close", r.get("high", r.get("low", 0.0)))),
                )
                for r in rows
                if isinstance(r, dict) and "time" in r
            ]
            out = [p for p in out if p[1] > 0.0]
            out.sort(key=lambda x: x[0])
            return out
    except Exception as e:
        report_error("btc: market_chart cryptocompare", e)

    return []


@st.cache_data(ttl=CACHE_TTL_MED)
def fetch_btc_last_24h_eur() -> list[tuple[datetime, float]]:
    return _coingecko_market_chart(1, vs="eur")


@st.cache_data(ttl=CACHE_TTL_MED)
def fetch_btc_last_7d_eur() -> list[tuple[datetime, float]]:
    return _coingecko_market_chart(7, vs="eur")


@st.cache_data(ttl=CACHE_TTL_MED)
def fetch_btc_last_30d_eur() -> list[tuple[datetime, float]]:
    return _coingecko_market_chart(30, vs="eur")


@st.cache_data(ttl=CACHE_TTL_MED)
def fetch_btc_eur_range(
    days: int | None = None, hours: int | None = None
) -> list[tuple[datetime, float]]:
    if days is None and hours is not None:
        days = max(1, int((hours + 23) // 24))
    if days is None:
        days = 7
    return _coingecko_market_chart(int(days), vs="eur")


@st.cache_data(ttl=CACHE_TTL_LONG)
def fetch_btc_ath_eur() -> tuple[float | None, str | None]:
    try:
        url = "https://api.coingecko.com/api/v3/coins/bitcoin"
        data = http_get_json(url)
        market_data = data.get("market_data", {})
        ath = market_data.get("ath", {}).get("eur")
        ath_date = market_data.get("ath_date", {}).get("eur")
        if ath:
            try:
                ATH_CACHE_FILE.write_text(
                    json.dumps({"ath_eur": float(ath), "ath_date": ath_date}), encoding="utf-8"
                )
            except Exception as e:
                report_error("btc_ath: write cache", e)
            return float(ath), str(ath_date)
    except requests.HTTPError:
        try:
            cached = json.loads(ATH_CACHE_FILE.read_text(encoding="utf-8"))
            return float(cached.get("ath_eur")), str(cached.get("ath_date"))
        except Exception as e2:
            report_error("btc_ath: read cache on 429", e2)
    except Exception as e:
        report_error("btc_ath: network", e)
        try:
            cached = json.loads(ATH_CACHE_FILE.read_text(encoding="utf-8"))
            return float(cached.get("ath_eur")), str(cached.get("ath_date"))
        except Exception as e2:
            report_error("btc_ath: read local cache", e2)
    return None, None
