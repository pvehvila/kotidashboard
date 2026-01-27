import json
from datetime import datetime

import requests
import streamlit as st

from src.api.http_client import http_get_json
from src.config import (
    ATH_CACHE_FILE,
    CACHE_TTL_LONG,
    CACHE_TTL_MED,
    CACHE_TTL_SHORT,
    HTTP_TIMEOUT_S,
    TZ,
)
from src.utils import report_error

# ------------------ Julkinen nykyinen rajapinta ------------------


@st.cache_data(ttl=CACHE_TTL_SHORT)
def fetch_btc_eur() -> dict[str, float | None]:
    url = (
        "https://api.coingecko.com/api/v3/simple/price"
        "?ids=bitcoin&vs_currencies=eur&include_24hr_change=true"
    )
    data = http_get_json(url)
    btc = data.get("bitcoin", {})
    return {"price": btc.get("eur"), "change": btc.get("eur_24h_change")}


@st.cache_data(ttl=CACHE_TTL_MED)
def fetch_btc_last_24h_eur() -> list[tuple[datetime, float]]:
    return _btc_market_chart(1, vs="eur")


@st.cache_data(ttl=CACHE_TTL_MED)
def fetch_btc_last_7d_eur() -> list[tuple[datetime, float]]:
    return _btc_market_chart(7, vs="eur")


@st.cache_data(ttl=CACHE_TTL_MED)
def fetch_btc_last_30d_eur() -> list[tuple[datetime, float]]:
    return _btc_market_chart(30, vs="eur")


@st.cache_data(ttl=CACHE_TTL_MED)
def fetch_btc_eur_range(
    days: int | None = None, hours: int | None = None
) -> list[tuple[datetime, float]]:
    if days is None and hours is not None:
        days = max(1, int((hours + 23) // 24))
    if days is None:
        days = 7
    return _btc_market_chart(int(days), vs="eur")


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
                    json.dumps({"ath_eur": float(ath), "ath_date": ath_date}),
                    encoding="utf-8",
                )
            except Exception as e:
                report_error("btc_ath: write cache", e)
            return float(ath), str(ath_date)
    except requests.HTTPError:
        # CoinGecko voi antaa 429 → luetaan paikallinen cache
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


# ------------------ Uusi sisäinen pilkottu rakenne ------------------


@st.cache_data(ttl=CACHE_TTL_MED)
def _btc_market_chart(days: int, vs: str = "eur") -> list[tuple[datetime, float]]:
    """
    Orkestroi markkinadatn haun:
    1) yritä CoinGecko kolmessa vaiheessa
    2) jos ei onnistu, yritä CryptoCompare kolmessa vaiheessa
    """
    # ---- 1) CoinGecko-polku
    try:
        raw = _get_coingecko_market_chart(days, vs)
        prices_ms = _extract_coingecko_prices(raw)
        if prices_ms:
            return _to_dashboard_from_ms(prices_ms, days)
    except Exception as e:
        report_error("btc: market_chart coingecko", e)

    # ---- 2) CryptoCompare fallback
    try:
        raw_cc = _get_cryptocompare_histohour(days, vs)
        prices_unix = _extract_cryptocompare_prices(raw_cc)
        if prices_unix:
            return _to_dashboard_from_unix(prices_unix)
    except Exception as e:
        report_error("btc: market_chart cryptocompare", e)

    return []


# ---------- 1. HTTP-pyynnöt ----------


def _get_coingecko_market_chart(days: int, vs: str) -> dict:
    """
    Hakee raakadatan CoinGeckosta. Ei muunna mitään.
    """
    url = (
        "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
        f"?vs_currency={vs}&days={days}"
    )
    return http_get_json(url, timeout=HTTP_TIMEOUT_S)


def _get_cryptocompare_histohour(days: int, vs: str) -> dict:
    """
    Hakee raakadatan CryptoComparesta. Ei muunna mitään.
    """
    limit = min(24 * int(max(1, days)), 2000)
    alt_url = (
        "https://min-api.cryptocompare.com/data/v2/histohour"
        f"?fsym=BTC&tsym={vs.upper()}&limit={limit}"
    )
    return http_get_json(alt_url, timeout=HTTP_TIMEOUT_S)


# ---------- 2. Raakadatan prices-listan poiminta ----------


def _extract_coingecko_prices(data: dict) -> list[tuple[int, float]]:
    """
    Ottaa CoinGeckon market_chart-vastauksesta ulos listan (timestamp_ms, price).
    Palauttaa tyhjän listan, jos data ei ole odotetussa muodossa.
    """
    prices = data.get("prices", []) if isinstance(data, dict) else []
    out: list[tuple[int, float]] = []
    for item in prices:
        # CoinGecko: [timestamp_ms, price]
        if (
            isinstance(item, (list | tuple))
            and len(item) == 2
            and isinstance(item[0], (int | float))
        ):
            ts_ms = int(item[0])
            price = float(item[1])
            out.append((ts_ms, price))
    return out


def _extract_cryptocompare_prices(data: dict) -> list[tuple[int, float]]:
    """
    Ottaa CryptoComparen histohour-vastauksesta ulos listan (timestamp_unix_s, price).
    """
    rows = data.get("Data", {}).get("Data", []) if isinstance(data, dict) else []
    out: list[tuple[int, float]] = []
    for r in rows:
        if not isinstance(r, dict):
            continue
        ts = r.get("time")
        # käytetään close → high → low fallbackia kuten ennen
        price = r.get("close") or r.get("high") or r.get("low") or 0.0
        if ts and price:
            out.append((int(ts), float(price)))
    return out


# ---------- 3. Muunto dashboardin muotoon ----------


def _to_dashboard_from_ms(
    prices_ms: list[tuple[int, float]], days: int
) -> list[tuple[datetime, float]]:
    """
    Muuntaa millisekunteina olevat aikaleimat dashboardin tuple-muotoon.
    Sisältää downsamplauksen kuten alkuperäinen koodi.
    """
    if not prices_ms:
        return []

    target_points = max(24 * int(days), 24)
    keep_every = max(len(prices_ms) // target_points, 1)

    out: list[tuple[datetime, float]] = []
    for i, (ts_ms, val) in enumerate(prices_ms):
        if i % keep_every != 0:
            continue
        ts = datetime.fromtimestamp(ts_ms / 1000, tz=TZ)
        out.append((ts, float(val)))

    out.sort(key=lambda x: x[0])
    return out


def _to_dashboard_from_unix(
    prices_unix: list[tuple[int, float]],
) -> list[tuple[datetime, float]]:
    """
    Muuntaa sekunteina olevat aikaleimat dashboardin tuple-muotoon.
    CryptoCompare on jo tuntatasolla, joten downsamplaus ei ole välttämätön.
    """
    if not prices_unix:
        return []

    out: list[tuple[datetime, float]] = []
    for ts_s, val in prices_unix:
        ts = datetime.fromtimestamp(ts_s, tz=TZ)
        if val > 0.0:
            out.append((ts, float(val)))

    out.sort(key=lambda x: x[0])
    return out
