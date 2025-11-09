# src/api/electricity.py
"""
Sähkön pörssihinnan haku ja normalisointi (irrotettu api.py:stä).

Perusajatus:
- yritä ensin porssisahko v2 (latest-prices) -> siitä voidaan tehdä sekä tuntidata että 15 min
- jos se ei onnistu, hae sahkonhintatanaan.fi v1
- palautetaan samat rakenteet kuin alkuperäinen dashboard odottaa:
    try_fetch_prices(...)      -> [{"hour": 0, "cents": 5.3}, ...]
    try_fetch_prices_15min(...) -> [{"ts": datetime, "cents": 5.3}, ...]
"""

from __future__ import annotations

import json
import datetime as dt
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
import logging

import requests
import streamlit as st

from src.config import TZ, CACHE_TTL_MED
from src.utils import report_error
from src.api.http import http_get_json

logger = logging.getLogger(__name__)

# tyyppi 15 min -hinnoille
Price15 = Dict[str, Union[datetime, float]]  # {"ts": datetime, "cents": float}


# ---------------------------------------------------------------------------
# JULKINEN RAJAPINTA
# ---------------------------------------------------------------------------


@st.cache_data(ttl=CACHE_TTL_MED)
def try_fetch_prices(date_ymd: dt.date) -> Optional[List[Dict[str, float]]]:
    """
    Palauttaa päivän TUNTIhinnat muodossa:
        [{"hour": 0, "cents": 5.3}, ...]
    tai None jos haku epäonnistui.
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
def try_fetch_prices_15min(date_ymd: dt.date) -> Optional[List[Price15]]:
    """
    Palauttaa päivän 15 min hinnat muodossa:
        [{"ts": datetime, "cents": 5.3}, ...]
    Logiikka on sama kuin alkuperäisessä api.py:ssä:
      1) yritä suoraan porssisahko v2:n 48h varttidataa
      2) jos ei onnistu, hae tuntidata ja laajenna 15 minuuttiin
    """
    # 1) yritä v2
    try:
        v2_items = _fetch_15min_from_porssisahko_v2()
        if v2_items:
            out = _normalize_prices_list_15min(v2_items, date_ymd)
            if out:
                return out
    except Exception as e:
        report_error(f"prices: v2 15min {date_ymd.isoformat()}", e)

    # 2) fallback: tuntidata -> 15 min
    base_items = fetch_prices_for(date_ymd)
    if not base_items:
        return None

    # jos tuntidatassa on jo aikaleimat, normalisoidaan suoraan 15 min -muotoon
    has_ts = any(
        any(k in item for k in ("time", "Time", "timestamp", "Timestamp",
                                "datetime", "DateTime", "start", "Start",
                                "startDate", "endDate"))
        for item in base_items
    )
    if has_ts:
        return _normalize_prices_list_15min(base_items, date_ymd)

    # muuten laajennetaan “hour+cents” -> 4 kpl
    return _expand_hourly_to_15min(base_items, date_ymd)


# ---------------------------------------------------------------------------
# PÄIVÄN HINTA (TUNTITASO)
# ---------------------------------------------------------------------------


def fetch_prices_for(date_ymd: dt.date) -> List[Dict[str, float]]:
    """
    Yrittää hakea hinnat ensin api.porssisahko.net v2:sta,
    ja jos se ei onnistu, sahkonhintatanaan.fi v1:stä.
    Palauttaa aina listan muodossa [{"hour": h, "cents": x}, ...]
    """
    # 1) porssisahko v2
    try:
        prices = _fetch_from_porssisahko(date_ymd)
        if prices:
            return prices
    except requests.HTTPError as e:
        # 400/404 -> jatketaan fallbackiin, muut -> logi
        if not (e.response and e.response.status_code in (400, 404)):
            report_error(f"prices: porssisahko {date_ymd.isoformat()}", e)
    except Exception as e:
        report_error(f"prices: porssisahko {date_ymd.isoformat()}", e)

    # 2) sahkonhintatanaan v1
    try:
        prices = _fetch_from_sahkonhintatanaan(date_ymd)
        if prices:
            return prices
    except requests.HTTPError as e:
        if not (e.response and e.response.status_code in (400, 404)):
            report_error(f"prices: sahkonhintatanaan {date_ymd.isoformat()}", e)
    except Exception as e:
        report_error(f"prices: sahkonhintatanaan {date_ymd.isoformat()}", e)

    return []


def _fetch_from_sahkonhintatanaan(date_ymd: dt.date) -> List[Dict[str, float]]:
    # käytetään samaa v1-osoitetta kuin alkuperäisessä koodissa
    url = f"https://www.sahkonhintatanaan.fi/api/v1/prices/{date_ymd:%Y}/{date_ymd:%m-%d}.json"
    data = http_get_json(url)
    _log_raw_prices("sahkonhintatanaan", date_ymd, data)

    items = data.get("prices", []) if isinstance(data, dict) else data or []
    prices = _normalize_prices_list(items, date_ymd)
    logger.info(
        "norm_hours source=%s date=%s items=%s",
        "sahkonhintatanaan",
        date_ymd.isoformat(),
        prices,
    )
    return prices


def _fetch_from_porssisahko(date_ymd: dt.date) -> List[Dict[str, float]]:
    """
    Hakee hinnat porssisahko v2 -rajapinnasta (latest-prices),
    suodattaa oikean päivän ja tekee niistä tuntihinnat.
    Tämä on se sama logiikka, joka oli alkuperäisessä api.py:ssä. :contentReference[oaicite:1]{index=1}
    """
    url = "https://api.porssisahko.net/v2/latest-prices.json"
    data = http_get_json(url)

    items = data.get("prices", []) if isinstance(data, dict) else []
    per_hour: Dict[int, List[float]] = {}

    for item in items:
        start = item.get("startDate")
        price = item.get("price")
        if not start or price is None:
            continue

        try:
            dt_utc = datetime.fromisoformat(str(start).replace("Z", "+00:00"))
            dt_local = dt_utc.astimezone(TZ)
        except Exception:
            continue

        if dt_local.date() != date_ymd:
            continue

        hour = dt_local.hour
        per_hour.setdefault(hour, []).append(float(price))

    out: List[Dict[str, float]] = []
    for hour, quarter_prices in sorted(per_hour.items()):
        if not quarter_prices:
            continue
        avg_cents = sum(quarter_prices) / len(quarter_prices)
        out.append({"hour": hour, "cents": avg_cents})

    return out


# ---------------------------------------------------------------------------
# 15 MIN -TASO
# ---------------------------------------------------------------------------


def _fetch_15min_from_porssisahko_v2() -> List[dict]:
    """
    Hakee suoraan 48h varttidatan.
    Palauttaa sellaisenaan listan, jossa on kentät:
      price (snt/kWh, ALV mukana)
      startDate (UTC, Z)
      endDate (UTC, Z)
    """
    url = "https://api.porssisahko.net/v2/latest-prices.json"
    data = http_get_json(url)
    if isinstance(data, dict):
        return data.get("prices", []) or []
    return []


def _normalize_prices_list_15min(items: List[dict], date_ymd: dt.date) -> List[Price15]:
    """
    Muuttaa varttidatan muotoon [{"ts": ..., "cents": ...}, ...]
    ja suodattaa vain pyydetyn päivän. Tämäkin on suoraan alkuperäisestä. :contentReference[oaicite:2]{index=2}
    """
    out_map: Dict[datetime, float] = {}

    for idx, item in enumerate(items or []):
        ts: Optional[datetime] = None
        # etsi aikaleima monesta eri kentästä
        for key in (
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
        ):
            if key in item and item[key]:
                try:
                    tmp = str(item[key]).replace("Z", "+00:00")
                    dt_obj = datetime.fromisoformat(tmp)
                    if dt_obj.tzinfo is None:
                        dt_obj = dt_obj.replace(tzinfo=TZ)
                    else:
                        dt_obj = dt_obj.astimezone(TZ)
                    ts = dt_obj
                except Exception:
                    ts = None
                break

        if ts is None:
            # fallback: klo 00:00 + idx * 15 min
            base = datetime.combine(date_ymd, datetime.min.time()).replace(tzinfo=TZ)
            ts = base + timedelta(minutes=15 * idx)

        # pyöristetään varttiin
        q = (ts.minute // 15) * 15
        ts = ts.replace(minute=q, second=0, microsecond=0)

        if ts.date() != date_ymd:
            # v2 antaa 48h -> otetaan vain pyydetty
            continue

        cents = _parse_cents_from_item(item)
        if cents is None:
            continue

        if ts not in out_map:
            out_map[ts] = float(cents)

    return [{"ts": ts, "cents": out_map[ts]} for ts in sorted(out_map.keys())]


def _expand_hourly_to_15min(hourly: List[Dict[str, float]], date_ymd: dt.date) -> List[Price15]:
    """
    Vanhan mallinen tuntidata -> neljä 15 min -pätkää per tunti. :contentReference[oaicite:3]{index=3}
    """
    out: List[Price15] = []

    for item in hourly:
        hour = int(item["hour"])
        cents = float(item["cents"])

        base = (
            datetime.combine(date_ymd, datetime.min.time())
            .replace(tzinfo=TZ)
            + timedelta(hours=hour)
        )

        for q in range(4):
            ts = base + timedelta(minutes=15 * q)
            out.append({"ts": ts, "cents": cents})

    return out


# ---------------------------------------------------------------------------
# APUFUNKTIOT (SAMAT NIMET KUIN ALKUPERÄISESSÄ)
# ---------------------------------------------------------------------------


def _parse_cents_from_item(item: dict) -> Optional[float]:
    # v2:lla on startDate / endDate → niissä price on jo snt/kWh
    is_v2_like = "startDate" in item or "endDate" in item

    for key in ("cents", "cents_per_kwh", "price", "Price", "value", "Value", "EUR_per_kWh"):
        if value := item.get(key):
            try:
                price = float(value)
            except ValueError:
                continue

            if is_v2_like:
                return price

            return price if price >= 1.0 else price * 100.0

    return None


def _parse_hour_from_item(item: dict, idx: int, date_ymd: dt.date) -> Optional[int]:
    # suorat tuntikentät
    for key in ("hour", "Hour", "H"):
        if value := item.get(key):
            try:
                hour = int(value)
                if 0 <= hour <= 23:
                    return hour
            except ValueError:
                pass

    # aikaleimat
    for key in ("time", "Time", "timestamp", "Timestamp", "datetime", "DateTime", "start", "Start", "startDate"):
        if value := item.get(key):
            try:
                ts = str(value).replace("Z", "+00:00")
                dt_obj = datetime.fromisoformat(ts)
                if dt_obj.tzinfo is None:
                    dt_obj = dt_obj.replace(tzinfo=TZ)
                else:
                    dt_obj = dt_obj.astimezone(TZ)
                if dt_obj.date() == date_ymd and 0 <= dt_obj.hour <= 23:
                    return dt_obj.hour
            except ValueError:
                continue

    # fallback: rivin järjestys
    return idx if 0 <= idx <= 23 else None


def _normalize_prices_list(items: List[dict], date_ymd: dt.date) -> List[Dict[str, float]]:
    out_map: Dict[int, float] = {}
    for idx, item in enumerate(items or []):
        try:
            hour = _parse_hour_from_item(item, idx, date_ymd)
            cents = _parse_cents_from_item(item)
            if hour is not None and cents is not None and 0 <= hour <= 23 and hour not in out_map:
                out_map[hour] = float(cents)
        except Exception:
            continue
    return [{"hour": h, "cents": out_map[h]} for h in sorted(out_map.keys())]


def _log_raw_prices(source: str, date_ymd: dt.date, data: object) -> None:
    try:
        dumped = json.dumps(data, ensure_ascii=False)
    except Exception:
        dumped = str(data)

    if len(dumped) > 2000:
        dumped = dumped[:2000] + "... (truncated)"

    logger.info("raw_prices source=%s date=%s data=%s", source, date_ymd.isoformat(), dumped)
