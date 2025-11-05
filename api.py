import time
import json
import datetime as dt  # <-- TÄRKEÄ: dt = datetime

import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from urllib.parse import quote

import pandas as pd
import requests
from requests.exceptions import RequestException
import streamlit as st

from config import (
    TZ,
    HTTP_TIMEOUT_S,
    CACHE_TTL_SHORT,
    CACHE_TTL_MED,
    CACHE_TTL_LONG,
    ATH_CACHE_FILE,
    NAMEDAY_FILE,
    NAMEDAY_PATHS,
    HOLIDAY_PATHS,
    CLOUD_T_CLEAR,
    CLOUD_T_ALMOST,
    CLOUD_T_PARTLY,
    CLOUD_T_MOSTLY,
)
from utils import report_error
from weather_icons import render_foreca_icon

logger = logging.getLogger("homedashboard")

def api_request_with_retry(url: str, 
                          method: str = "GET", 
                          retry_count: int = 3, 
                          **kwargs) -> Optional[Dict[Any, Any]]:
    """Make API request with retry logic"""
    for attempt in range(retry_count):
        try:
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            logger.warning(f"API request failed (attempt {attempt + 1}/{retry_count}): {str(e)}")
            if attempt == retry_count - 1:
                logger.error(f"API request failed after {retry_count} attempts: {str(e)}")
                return None
            time.sleep(2 ** attempt)  # Exponential backoff

# ------------------- HTTP UTILS -------------------

def http_get_json(url: str, timeout: float = HTTP_TIMEOUT_S) -> dict:
    """Fetch JSON with UA + kevyt retry 429/403:lle."""
    headers = {"User-Agent": "HomeDashboard/1.0 (+https://github.com/pvehvila/kotidashboard)"}
    try:
        resp = requests.get(url, timeout=timeout, headers=headers)
        if resp.status_code in (429, 403):
            import time
            time.sleep(0.8)
            resp = requests.get(url, timeout=timeout, headers=headers)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        report_error(f"http_get_json: {url}", e)
        raise


# ------------------- ELECTRICITY PRICES -------------------

def _parse_cents_from_item(item: dict) -> Optional[float]:
    # v2:lla on startDate / endDate → niissä price on jo snt/kWh
    is_v2_like = "startDate" in item or "endDate" in item

    for key in ("cents", "cents_per_kwh", "price", "Price", "value", "Value", "EUR_per_kWh"):
        if value := item.get(key):
            try:
                price = float(value)
            except ValueError:
                continue

            # jos näyttää v2:lta, palautetaan sellaisenaan
            if is_v2_like:
                return price

            # vanha logiikka: jos iso luku → se on jo senteissä
            # jos pieni → se on euroja, kerrotaan sadalla
            return price if price >= 1.0 else price * 100.0

    return None

def _parse_hour_from_item(item: dict, idx: int, date_ymd: dt.date) -> Optional[int]:
    """Yritetään purkaa tunti monesta eri kenttämuodosta."""
    # suorat tuntikentät
    for key in ("hour", "Hour", "H"):
        if value := item.get(key):
            try:
                hour = int(value)
                if 0 <= hour <= 23:
                    return hour
            except ValueError:
                pass

    # aikaleimakentät -> poimi tunti jos sama päivä
    for key in (
        "time", "Time",
        "timestamp", "Timestamp",
        "datetime", "DateTime",
        "start", "Start",
        "startDate",  # v2
    ):
        if value := item.get(key):
            try:
                ts = str(value).replace("Z", "+00:00")
                dt_obj = datetime.fromisoformat(ts)
                # jos rajapinta ei antanut tz:tä, oletetaan dashboardin TZ
                if dt_obj.tzinfo is None:
                    dt_obj = dt_obj.replace(tzinfo=TZ)
                else:
                    dt_obj = dt_obj.astimezone(TZ)
                if dt_obj.date() == date_ymd and 0 <= dt_obj.hour <= 23:
                    return dt_obj.hour
            except ValueError:
                continue

    # fallback: järjestysindeksi
    return idx if 0 <= idx <= 23 else None


def _log_raw_prices(source: str, date_ymd: dt.date, data: object) -> None:
    """
    Kirjaa raakavastauksen lokiin. Lyhennetään ettei täytä lokia.
    """
    try:
        dumped = json.dumps(data, ensure_ascii=False)
    except Exception:
        dumped = str(data)

    # leikataan esim. 2000 merkkiin
    if len(dumped) > 2000:
        dumped = dumped[:2000] + "... (truncated)"

    logger.info("raw_prices source=%s date=%s data=%s", source, date_ymd.isoformat(), dumped)

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

def _floor_to_quarter(dt_obj: datetime) -> datetime:
    q = (dt_obj.minute // 15) * 15
    return dt_obj.replace(minute=q, second=0, microsecond=0)

def _parse_ts_15min_from_item(item: dict, date_ymd: dt.date, idx: int) -> Optional[datetime]:
    """
    Yritetään löytää täsmällinen aikaleima (esim. 2025-11-05T09:15:00Z) riviltä.
    Jos ei löydy, palataan None.
    """
    for key in ("time", "Time", "timestamp", "Timestamp", "datetime", "DateTime", "start", "Start", "startDate"):
        if value := item.get(key):
            try:
                ts = str(value).replace("Z", "+00:00")
                dt_obj = datetime.fromisoformat(ts)
                # jos ei ole tz:tä, oletetaan dashboardin TZ
                if dt_obj.tzinfo is None:
                    dt_obj = dt_obj.replace(tzinfo=TZ)
                else:
                    dt_obj = dt_obj.astimezone(TZ)
                # varmistetaan että päivä täsmää
                if dt_obj.date() == date_ymd:
                    return _floor_to_quarter(dt_obj)
            except Exception:
                continue
    # fallback: jos API antaa vain järjestysindeksin, voidaan tehdä arvauksia
    # esim. klo 00:00 + idx * 15 min
    base = datetime.combine(date_ymd, datetime.min.time()).replace(tzinfo=TZ)
    return base + timedelta(minutes=15 * idx)

# yksi yhteinen tyyppi 15 min -hinnoille
Price15 = Dict[str, Union[datetime, float]]  # "ts" -> datetime, "cents" -> float


def _normalize_prices_list_15min(items: List[dict], date_ymd: dt.date) -> List[Price15]:
    out_map: Dict[datetime, float] = {}

    for idx, item in enumerate(items or []):
        ts: Optional[datetime] = None
        for key in (
            "time", "Time",
            "timestamp", "Timestamp",
            "datetime", "DateTime",
            "start", "Start",
            "startDate",  # v2
            "endDate",    # varalle
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
            base = datetime.combine(date_ymd, datetime.min.time()).replace(tzinfo=TZ)
            ts = base + timedelta(minutes=15 * idx)

        ts = _floor_to_quarter(ts)

        if ts.date() != date_ymd:
            # v2 antaa 48h, suodatetaan vain pyydetty päivä
            continue

        cents = _parse_cents_from_item(item)
        if cents is None:
            continue

        if ts not in out_map:
            out_map[ts] = float(cents)

    return [{"ts": ts, "cents": out_map[ts]} for ts in sorted(out_map.keys())]



def _expand_hourly_to_15min(
    hourly: List[Dict[str, float]],
    date_ymd: dt.date,
) -> List[Price15]:
    """
    Vanhan mallinen tuntidata -> neljä 15 min -pätkää per tunti.
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


def _fetch_15min_from_porssisahko_v2() -> List[dict]:
    """
    Hakee suoraan v2/latest-prices.json -rajapinnasta 48h varttihinnat.
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

@st.cache_data(ttl=CACHE_TTL_MED)
def try_fetch_prices_15min(date_ymd: dt.date) -> Optional[List[Price15]]:
    """
    Yrittää lukea hinnat 15 min tarkkuudella.
    1) ensin yritetään v2/latest-prices.json (paras lähde vartteihin)
    2) jos se epäonnistuu, käytetään vanhaa tuntidata -> laajennus
    """
    # 1) yritä v2
    try:
        v2_items = _fetch_15min_from_porssisahko_v2()
        if v2_items:
            # v2:sta tulee UTC-aikoja => normalisoidaan ja suodatetaan
            out = _normalize_prices_list_15min(v2_items, date_ymd)
            if out:
                return out
    except Exception as e:
        # jos v2 kaatuu, jatketaan vanhaan tapaan
        report_error(f"prices: v2 15min {date_ymd.isoformat()}", e)

    # 2) vanha fallback: hae päivän hinnat (tuntina) ja laajenna
    base_items = fetch_prices_for(date_ymd)
    if not base_items:
        return None

    # tarkista onko niissä jo minuuttitietoa
    has_ts = any(
        any(k in item for k in ("time", "Time", "timestamp", "Timestamp",
                                "datetime", "DateTime", "start", "Start",
                                "startDate", "endDate"))
        for item in base_items
    )

    if has_ts:
        return _normalize_prices_list_15min(base_items, date_ymd)

    return _expand_hourly_to_15min(base_items, date_ymd)





def _fetch_from_sahkonhintatanaan(date_ymd: dt.date) -> List[Dict[str, float]]:
    url = f"https://www.sahkonhintatanaan.fi/api/v1/prices/{date_ymd:%Y}/{date_ymd:%m-%d}.json"
    data = http_get_json(url)
    _log_raw_prices("sahkonhintatanaan", date_ymd, data)

    items = data.get("prices", []) if isinstance(data, dict) else data or []
    prices = _normalize_prices_list(items, date_ymd)
    logger.info("norm_hours source=%s date=%s items=%s",
                "sahkonhintatanaan", date_ymd.isoformat(), prices)
    return prices



def _fetch_from_porssisahko(date_ymd: dt.date) -> List[Dict[str, float]]:
    """
    Hakee hinnat porssisahko v2 -rajapinnasta (latest-prices),
    suodattaa oikean päivän ja tekee niistä tuntihinnat.
    """
    url = "https://api.porssisahko.net/v2/latest-prices.json"
    data = http_get_json(url)

    # v2: {"prices": [{"price": 0.513, "startDate": "...Z", "endDate": "...Z"}, ...]}
    items = data.get("prices", []) if isinstance(data, dict) else []

    # suodatetaan vain ne rivit, joiden startDate osuu pyydettyyn päivään Helsingin ajassa
    per_hour: Dict[int, List[float]] = {}

    for item in items:
        start = item.get("startDate")
        price = item.get("price")
        if not start or price is None:
            continue

        try:
            # v2 on aina UTC:ssa → muutetaan dashboardin TZ:ään
            dt_utc = datetime.fromisoformat(str(start).replace("Z", "+00:00"))
            dt_local = dt_utc.astimezone(TZ)
        except Exception:
            continue

        if dt_local.date() != date_ymd:
            continue

        hour = dt_local.hour
        per_hour.setdefault(hour, []).append(float(price))

    # nyt meillä on per_hour[hour] = [4 varttia] → tehdään niistä keskiarvo
    out: List[Dict[str, float]] = []
    for hour, quarter_prices in sorted(per_hour.items()):
        if not quarter_prices:
            continue
        avg_cents = sum(quarter_prices) / len(quarter_prices)
        # API antaa snt/kWh → me palautetaan sama
        out.append({"hour": hour, "cents": avg_cents})

    return out



def fetch_prices_for(date_ymd: dt.date) -> List[Dict[str, float]]:
    # 1) yritä ensin api.porssisahko.net
    try:
        if prices := _fetch_from_porssisahko(date_ymd):
            return prices
    except requests.HTTPError as e:
        if e.response and e.response.status_code not in (400, 404):
            report_error(f"prices: porssisahko {date_ymd.isoformat()}", e)
    except Exception as e:
        report_error(f"prices: porssisahko {date_ymd.isoformat()}", e)

    # 2) fallback: sahkonhintatanaan.fi
    try:
        if prices := _fetch_from_sahkonhintatanaan(date_ymd):
            return prices
    except requests.HTTPError as e:
        if e.response and e.response.status_code not in (400, 404):
            report_error(f"prices: sahkonhintatanaan {date_ymd.isoformat()}", e)
    except Exception as e:
        report_error(f"prices: sahkonhintatanaan {date_ymd.isoformat()}", e)

    return []


@st.cache_data(ttl=CACHE_TTL_MED)
def try_fetch_prices(date_ymd: dt.date) -> Optional[List[Dict[str, float]]]:
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


# ------------------- ZEN QUOTES -------------------

LOCAL_ZEN = [
    {"text": "Hiljaisuus on vastaus, jota etsit.", "author": "Tuntematon"},
    {"text": "Paranna sitä, mihin kosket, ja jätä se paremmaksi kuin sen löysit.", "author": "Tuntematon"},
    {"text": "Kärsivällisyys on taito odottaa rauhassa.", "author": "Tuntematon"},
    {"text": "Päivän selkeys syntyy hetken huomiosta.", "author": "Tuntematon"},
]


def _from_zenquotes() -> Optional[Dict[str, str]]:
    try:
        data = http_get_json("https://zenquotes.io/api/today", timeout=HTTP_TIMEOUT_S)
        if isinstance(data, list) and data:
            q = data[0]
            quote = {"text": q.get("q", ""), "author": q.get("a", ""), "source": "zenquotes"}
            print("[ZEN] Haettu zenquotes:", quote)  # ← lokitus
            return quote
        else:
            print("[ZEN] Zenquotes palautti odottamattoman rakenteen:", data)
    except Exception as e:
        report_error("zen: zenquotes-today", e)
        print("[ZEN] Zenquotes virhe:", e)
    return None


def _from_quotable() -> Optional[Dict[str, str]]:
    try:
        data = http_get_json(
            "https://api.quotable.io/random?tags=wisdom|life|inspirational",
            timeout=HTTP_TIMEOUT_S,
        )
        quote = {"text": data.get("content", ""), "author": data.get("author", ""), "source": "quotable"}
        print("[ZEN] Haettu quotable:", quote)  # ← lokitus
        return quote
    except Exception as e:
        report_error("zen: quotable", e)
        print("[ZEN] Quotable virhe:", e)
    return None


@st.cache_data(ttl=CACHE_TTL_LONG)
def fetch_daily_quote(day_iso: str) -> Dict[str, str]:
    print(f"[ZEN] Päivän sitaatti haetaan ({day_iso})")
    if quote := _from_zenquotes():
        print("[ZEN] Käytetään zenquotes-lähdettä.")
        return quote
    if quote := _from_quotable():
        print("[ZEN] Käytetään quotable-lähdettä.")
        return quote
    idx = sum(map(ord, day_iso)) % len(LOCAL_ZEN)
    out = dict(LOCAL_ZEN[idx])
    out["source"] = "local"
    print("[ZEN] Käytetään paikallista sitaattia:", out)
    return out


# ------------------- WEATHER -------------------

MAP_TRACE_ENABLED = False
_MAP_TRACE: List[Dict] = []


def _trace_map(wmo: Optional[int], is_day: bool, pop: Optional[int],
               temp_c: Optional[float], cloudcover: Optional[int],
               chosen_key: str, reason: str):
    if not MAP_TRACE_ENABLED:
        return
    try:
        _MAP_TRACE.append({
            "wmo": wmo, "is_day": is_day, "pop": pop, "temp_c": temp_c,
            "cloudcover": cloudcover, "key": chosen_key, "reason": reason,
        })
        if len(_MAP_TRACE) > 200:
            del _MAP_TRACE[:-120]
    except Exception:
        pass


def get_map_trace() -> List[Dict]:
    return list(_MAP_TRACE)


def clear_map_trace():
    _MAP_TRACE.clear()


def _cloud_icon_from_cover(cover: Any, is_day: bool) -> str:
    def ensure_int_strict(x: Any) -> int:
        if isinstance(x, pd.Series):
            if x.empty:
                raise TypeError("empty Series")
            x = x.iloc[0]
        try:
            import numpy as np
            if isinstance(x, (np.integer, np.floating)):
                return int(x)
        except Exception:
            pass
        if isinstance(x, (int, float)):
            return int(x)
        if isinstance(x, str):
            s = x.strip().replace(",", ".")
            return int(float(s))
        raise TypeError(f"unsupported type: {type(x).__name__}")

    try:
        cov: int = ensure_int_strict(cover)
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

def create_icon_mappings(df: pd.DataFrame, wmo_col: str) -> tuple[Dict[int, str], Dict[int, str]]:
    maps_day: Dict[int, str] = {}
    maps_night: Dict[int, str] = {}

    for _, row in df.iterrows():
        try:
            current_wmo = int(row[wmo_col].item())  # <-- Määritelty
            day_full = row.get('day_full')
            night_full = row.get('night_full')

            if day_full:
                maps_day[current_wmo] = day_full
            if night_full:
                maps_night[current_wmo] = night_full
        except Exception:
            continue

    return maps_day, maps_night

# Fallback _prep jos ei ole määritelty muualla
if "_prep" not in globals():
    def _prep(raw: str, suffix: str, last: Optional[str]) -> Optional[str]:
        """Yksinkertainen valmistelu: palauta raw jos ei tyhjä, muuten viimeinen arvo."""
        s = raw.strip() if raw else ""
        return s if s else last

def _read_wmo_mapping(path: Optional[str] = None) -> "pd.DataFrame":
    """Try to read mapping dataframe from given path or common filenames in project root."""
    candidates = []
    if path:
        candidates.append(Path(path))
    root = Path(__file__).parent
    for name in ("wmo_foreca_map.xlsx", "wmo_foreca_map.csv", "mappings.xlsx", "mappings.csv"):
        candidates.append(root / name)

    for p in candidates:
        try:
            if not p or not p.exists():
                continue
            if p.suffix.lower() in (".xls", ".xlsx"):
                return pd.read_excel(p)
            return pd.read_csv(p)
        except Exception:
            continue
    return pd.DataFrame()  # empty fallback

# Muokattu: df voi olla None -> luetaan fallback-data jos tarvitaan
def _load_wmo_foreca_map(
    df: Optional["pd.DataFrame"] = None,
    wmo_col: str = "wmo",
    day_col: str = "day",
    night_col: str = "night",
) -> Dict[str, Dict[int, str]]:
    if df is None:
        df = _read_wmo_mapping()
    if df.empty:
        return {"day": {}, "night": {}}

    maps_day: Dict[int, str] = {}
    maps_night: Dict[int, str] = {}
    last_day_full: Optional[str] = None
    last_night_full: Optional[str] = None

    def _row_scalar(cell: Any) -> Any:
        try:
            if hasattr(cell, "iloc"):
                return cell.iloc[0] if len(cell) > 0 else None
            if hasattr(cell, "item"):
                try:
                    return cell.item()
                except Exception:
                    return cell
            return cell
        except Exception:
            return None

    for _, row in df.iterrows():
        try:
            current_wmo = int(_row_scalar(row[wmo_col]))  # turvallinen skalaarin haku

            val_day = _row_scalar(row[day_col])
            raw_day = "" if val_day is None or pd.isna(val_day) else str(val_day).strip()
            val_night = _row_scalar(row[night_col])
            raw_night = "" if val_night is None or pd.isna(val_night) else str(val_night).strip()

            day_full = _prep(raw_day, "d", last_day_full)
            night_full = _prep(raw_night, "n", last_night_full)

            if day_full:
                maps_day[current_wmo] = day_full
                last_day_full = day_full
            if night_full:
                maps_night[current_wmo] = night_full
                last_night_full = night_full
        except Exception:
            continue

    # estää "assigned but not used" lint-varoitukset
    _ = (last_day_full, last_night_full)

    return {"day": maps_day, "night": maps_night}


def wmo_to_foreca_code(code: Optional[int], is_day: bool,
                       pop: Optional[int] = None, temp_c: Optional[float] = None,
                       cloudcover: Optional[int] = None) -> str:
    maps = _load_wmo_foreca_map()
    if code is None:
        key = "d000" if is_day else "n000"
        _trace_map(code, is_day, pop, temp_c, cloudcover, key, "none → clear (default)")
        return key

    code = int(code)
    lookup = maps["day" if is_day else "night"]
    if key := lookup.get(code):
        _trace_map(code, is_day, pop, temp_c, cloudcover, key, "Excel mapping")
        return key

    key = _cloud_icon_from_cover(cloudcover, is_day)
    _trace_map(code, is_day, pop, temp_c, cloudcover, key, "fallback: cloudcover")
    return key

def _as_bool(x: Any) -> Optional[bool]:
    try:
        if x is None:
            return None
        if hasattr(x, 'iloc'):
            if len(x) == 0:
                return None
            x = x.iloc[0]
        try:
            import pandas as pd
            if pd.isna(x):
                return None
        except (ImportError, Exception):
            pass
        if hasattr(x, "item"):
            x = x.item()
        if isinstance(x, bool):
            return x
        if isinstance(x, (int, float)):
            return bool(int(x))
        if isinstance(x, str):
            s = x.strip().lower()
            if s in ('true', '1', 'yes'):
                return True
            if s in ('false', '0', 'no', ''):
                return False
            # KORJAUS: Lisää try-except tähän
            try:
                return bool(int(float(s)))
            except (ValueError, TypeError):
                return None
        return bool(x)
    except Exception:
        return None

def _as_float(x: Any) -> Optional[float]:
    """Convert various types to float, handling pandas/numpy types safely."""
    try:
        if x is None:
            return None
        
        # pandas.Series → extract first value
        if hasattr(x, 'iloc'):
            try:
                if len(x) == 0:
                    return None
                x = x.iloc[0]
            except TypeError:
                pass
        
        # Handle pandas NA/NaT
        try:
            import pandas as pd
            if pd.isna(x):
                return None
        except (ImportError, Exception):
            pass
        
        # numpy scalar → extract Python value
        if hasattr(x, "item"):
            x = x.item()
        
        return float(x)
    except Exception:
        return None


def _as_int(x: Any) -> Optional[int]:
    """Convert various types to int, handling pandas/numpy types safely."""
    try:
        if x is None:
            return None
        
        # pandas.Series → extract first value
        if hasattr(x, 'iloc'):
            if len(x) == 0:
                return None
            x = x.iloc[0]
        
        # Handle pandas NA/NaT
        try:
            import pandas as pd
            if pd.isna(x):
                return None
        except (ImportError, Exception):
            pass
        
        # numpy scalar → extract Python value
        if hasattr(x, "item"):
            x = x.item()
        
        return int(float(x))
    except Exception:
        return None


def fetch_weather_points(lat: float, lon: float, tz_name: str,
                        offsets: Tuple[int, ...] = (0, 3, 6, 9, 12)) -> Dict:
    url = (
        f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
        f"&hourly=temperature_2m,precipitation_probability,weathercode,cloudcover,is_day"
        f"&timezone={quote(tz_name)}"
    )
    data = http_get_json(url)
    hourly = data.get("hourly", {})
    times = hourly.get("time", [])
    temps = hourly.get("temperature_2m", [])
    pops = hourly.get("precipitation_probability", [])
    wmos = hourly.get("weathercode", [])
    covers = hourly.get("cloudcover", [])
    isday = hourly.get("is_day", [])

    # Korjattu: datetime.now(TZ)
    now = datetime.now(TZ).replace(minute=0, second=0, microsecond=0)
    points = []

    for offset in offsets:
        target_time = now + timedelta(hours=offset)
        timestamp = target_time.strftime("%Y-%m-%dT%H:00")
        try:
            idx = times.index(timestamp)
        except ValueError:
            continue

        raw_temp = temps[idx] if idx < len(temps) else None
        raw_pop = pops[idx] if idx < len(pops) else None
        raw_wmo = wmos[idx] if idx < len(wmos) else None
        raw_ccov = covers[idx] if idx < len(covers) else None
        raw_isday = isday[idx] if idx < len(isday) else None

        temp = _as_float(raw_temp)
        pop = _as_int(raw_pop)
        wmo = _as_int(raw_wmo)
        ccov = _as_int(raw_ccov)
        is_day_result = _as_bool(raw_isday)
        # Korjattu: käytetään bool-arvoa
        is_day_flag: bool = is_day_result if is_day_result is not None else (6 <= target_time.hour <= 20)

        points.append({
            "label": "Nyt" if offset == 0 else f"+{offset} h",
            "hour": target_time.hour,
            "temp": temp,
            "pop": pop,
            "key": wmo_to_foreca_code(wmo, is_day=is_day_flag, pop=pop, temp_c=temp, cloudcover=ccov),
        })

    min_temp = max_temp = None
    try:
        day_str = now.strftime("%Y-%m-%d")
        idxs = [i for i, ts in enumerate(times) if ts.startswith(day_str)]
        vals = [temps[i] for i in idxs if i < len(temps)]
        if vals:
            min_temp, max_temp = min(vals), max(vals)
    except Exception:
        pass

    return {"points": points, "min_temp": min_temp, "max_temp": max_temp}


def wmo_to_icon_key(code: Optional[int], is_day: bool) -> str:
    if code is None:
        return "na"
    if code == 0:
        return "clear-day" if is_day else "clear-night"
    if code in (1, 2):
        return "partly-cloudy-day" if is_day else "partly-cloudy-night"
    if code == 3:
        return "cloudy"
    if code in (45, 48):
        return "fog"
    if code in (51, 53, 55, 56, 57):
        return "drizzle"
    if code in (61, 63, 65, 80, 81, 82):
        return "rain"
    if code in (66, 67):
        return "freezing-rain"
    if code in (71, 73, 75, 85, 86):
        return "snow"
    if code in (95, 96, 99):
        return "thunderstorm"
    return "na"


# ------------------- WEATHER DEBUG MATRIX -------------------

def card_weather_debug_matrix():
    st.markdown("<div class='card-title'>🧪 Sääikonit – pikatesti</div>", unsafe_allow_html=True)

    def render_row(label: str, items: List[Tuple[str, str]]) -> str:
        row_html = "<div style='display:flex; gap:10px; flex-wrap:wrap; align-items:center;'>"
        row_html += f"<div style='width:110px; opacity:.8;'>{label}</div>"
        for desc, key in items:
            img = render_foreca_icon(key, size=40)
            row_html += (
                f"<div style='display:grid; place-items:center; background:rgba(255,255,255,.06); padding:6px 8px; border-radius:10px; min-width:120px;'>"
                f"{img}<div style='font-size:.8rem; opacity:.85;'>{desc}<br/><code>{key}</code></div></div>"
            )
        row_html += "</div>"
        return row_html

    cloud_rows = []
    for is_day in (True, False):
        items = [(f"cc {cc}%", wmo_to_foreca_code(0, is_day=is_day, pop=0, temp_c=10, cloudcover=cc))
                 for cc in (5, 30, 55, 75, 95)]
        cloud_rows.append(render_row(f"{'Päivä' if is_day else 'Yö'} – pilvisyys", items))

    rain_rows = []
    for code in (61, 63, 65):
        cases = [
            ("päivä, PoP 20%", wmo_to_foreca_code(code, is_day=True, pop=20, temp_c=5.0, cloudcover=70)),
            ("päivä, PoP 80%", wmo_to_foreca_code(code, is_day=True, pop=80, temp_c=5.0, cloudcover=70)),
            ("päivä, 0°C (räntä)", wmo_to_foreca_code(code, is_day=True, pop=80, temp_c=0.0, cloudcover=70)),
            ("yö, PoP 80%", wmo_to_foreca_code(code, is_day=False, pop=80, temp_c=5.0, cloudcover=70)),
        ]
        rain_rows.append(render_row(f"WMO {code} – sade", cases))

    shower_rows = []
    for code in (80, 81, 82):
        cases = [(f"päivä, PoP {pop}%", wmo_to_foreca_code(code, is_day=True, pop=pop, temp_c=10, cloudcover=60))
                 for pop in (20, 80)]
        shower_rows.append(render_row(f"WMO {code} – kuurot", cases))

    misc_cases = [("tihku heikko (51)", 51), ("tihku koht. (53)", 53), ("tihku voim. (55)", 55),
                  ("jäätävä tihku (56)", 56), ("jäätävä sade h. (66)", 66), ("jäätävä sade v. (67)", 67),
                  ("lumi (71)", 71), ("lumikuuro (85)", 85), ("ukkonen (95)", 95)]
    misc_rows = render_row("Muut", [
        (label, wmo_to_foreca_code(code, is_day=True, pop=80, temp_c=-2 if code in (71, 85) else 2, cloudcover=80))
        for label, code in misc_cases
    ])

    st.markdown(
        "<section class='card' style='min-height:12dvh; padding:10px;'>"
        "<div class='card-body' style='display:flex; flex-direction:column; gap:8px;'>"
        + "".join(cloud_rows + rain_rows + shower_rows + [misc_rows])
        + "</div></section>",
        unsafe_allow_html=True,
    )

    if st.toggle("Näytä päätösjäljet (trace)", value=False):
        rows = get_map_trace()
        if rows:
            head = "<tr><th>WMO</th><th>Päivä</th><th>PoP %</th><th>T °C</th><th>Cloud %</th><th>Key</th><th>Syynys</th></tr>"
            body = "".join(
                f"<tr><td>{r['wmo']}</td><td>{'d' if r['is_day'] else 'n'}</td>"
                f"<td>{r['pop']}</td><td>{r['temp_c']}</td><td>{r['cloudcover']}</td>"
                f"<td><code>{r['key']}</code></td><td>{r['reason']}</td></tr>"
                for r in rows[::-1]
            )
            st.markdown(
                f"<div class='card' style='padding:10px; overflow:auto;'>"
                f"<div class='card-title'>Päätösjälki (uusin ensin)</div>"
                f"<table style='width:100%; font-size:.9rem; border-collapse:collapse;'>{head}{body}</table></div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown("<div class='hint'>Ei jälkiä vielä.</div>", unsafe_allow_html=True)


# ------------------- NAMEDAYS & HOLIDAYS -------------------

def _resolve_nameday_file() -> Path:
    for path in NAMEDAY_PATHS:
        try:
            if path and Path(path).exists():
                return Path(path)
        except Exception:
            continue
    return Path(NAMEDAY_FILE)


def _resolve_first_existing(paths) -> Path:
    for p in paths:
        try:
            pp = Path(p)
            if pp.exists():
                return pp
        except Exception:
            continue
    return Path(paths[0]) if paths else Path()


def _load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


@st.cache_data(ttl=CACHE_TTL_LONG)
def fetch_nameday_today(_cache_buster: Optional[int] = None) -> str:
    try:
        path = _resolve_nameday_file()
        if not path.exists():
            return "—"
        data = _load_json(path)
        now = datetime.now(TZ)
        key_md = now.strftime("%m-%d")
        day_str = str(now.day)
        month_name = [
            "tammikuu", "helmikuu", "maaliskuu", "huhtikuu", "toukokuu", "kesäkuu",
            "heinäkuu", "elokuu", "syyskuu", "lokakuu", "marraskuu", "joulukuu",
        ][now.month - 1]

        if isinstance(data, dict) and key_md in data:
            names = data[key_md]
            if isinstance(names, list):
                return ", ".join(n.strip() for n in names if str(n).strip()) or "—"
            if isinstance(names, str) and names.strip():
                return names.strip()
            return "—"

        root = data.get("nimipäivät") if isinstance(data, dict) else None
        if isinstance(root, dict):
            month_obj = next((v for k, v in root.items()
                              if isinstance(k, str) and k.strip().lower() == month_name), None)
            if isinstance(month_obj, dict):
                names = month_obj.get(day_str)
                if isinstance(names, list):
                    return ", ".join(n.strip() for n in names if str(n).strip()) or "—"
                if isinstance(names, str) and names.strip():
                    return names.strip()
        return "—"
    except Exception as e:
        report_error("nameday: local json", e)
        return "—"


@st.cache_data(ttl=CACHE_TTL_LONG)
def fetch_holiday_today(_cache_buster: int | None = None) -> dict:
    out = {"holiday": None, "is_flag_day": False, "is_holiday": False}
    try:
        p = _resolve_first_existing(HOLIDAY_PATHS)
        if not p or not p.exists():
            return out

        data = _load_json(p)
        now = dt.datetime.now(TZ)
        key_md = now.strftime("%m-%d")
        key_iso = now.strftime("%Y-%m-%d")

        def parse_entry(entry: dict) -> dict:
            name = entry.get("name")
            hol_field = entry.get("holiday")
            is_holiday = bool(entry.get("is_holiday")) or (isinstance(hol_field, bool) and hol_field is True)
            if not name and isinstance(hol_field, str) and hol_field.strip():
                name = hol_field.strip()
            is_flag = bool(entry.get("flag") or entry.get("is_flag_day"))
            return {
                "holiday": (name.strip() if isinstance(name, str) and name.strip() else None),
                "is_flag_day": is_flag,
                "is_holiday": is_holiday,
            }

        if isinstance(data, dict):
            entry = data.get(key_md) or data.get(key_iso)
            if isinstance(entry, dict):
                return parse_entry(entry)
            return out

        if isinstance(data, list):
            for item in data:
                if not isinstance(item, dict):
                    continue
                d = str(item.get("date") or "").strip()
                if d in (key_iso, key_md):
                    return parse_entry(item)
        return out
    except Exception as e:
        report_error("holiday: local json", e)
        return out


# ------------------- BITCOIN -------------------

@st.cache_data(ttl=CACHE_TTL_SHORT)
def fetch_btc_eur() -> Dict[str, Optional[float]]:
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=eur&include_24hr_change=true"
    data = http_get_json(url)
    btc = data.get("bitcoin", {})
    return {"price": btc.get("eur"), "change": btc.get("eur_24h_change")}


@st.cache_data(ttl=CACHE_TTL_MED)
def _coingecko_market_chart(days: int, vs: str = "eur") -> List[Tuple[datetime, float]]:
    # 1) CoinGecko
    try:
        url = f"https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency={vs}&days={days}"
        data = http_get_json(url, timeout=HTTP_TIMEOUT_S)
        prices = data.get("prices", []) or []
        if prices:
            target_points = max(24 * int(days), 24)
            keep_every = max(len(prices) // target_points, 1)
            out: List[Tuple[datetime, float]] = []
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
                (datetime.fromtimestamp(r["time"], tz=TZ), float(r.get("close", r.get("high", r.get("low", 0.0)))))
                for r in rows if isinstance(r, dict) and "time" in r
            ]
            out = [p for p in out if p[1] > 0.0]
            out.sort(key=lambda x: x[0])
            return out
    except Exception as e:
        report_error("btc: market_chart cryptocompare", e)

    return []


@st.cache_data(ttl=CACHE_TTL_MED)
def fetch_btc_last_24h_eur() -> List[Tuple[datetime, float]]:
    return _coingecko_market_chart(1, vs="eur")


@st.cache_data(ttl=CACHE_TTL_MED)
def fetch_btc_last_7d_eur() -> List[Tuple[datetime, float]]:
    return _coingecko_market_chart(7, vs="eur")


@st.cache_data(ttl=CACHE_TTL_MED)
def fetch_btc_last_30d_eur() -> List[Tuple[datetime, float]]:
    return _coingecko_market_chart(30, vs="eur")


@st.cache_data(ttl=CACHE_TTL_MED)
def fetch_btc_eur_range(days: Optional[int] = None, hours: Optional[int] = None) -> List[Tuple[datetime, float]]:
    if days is None and hours is not None:
        days = max(1, int((hours + 23) // 24))
    if days is None:
        days = 7
    return _coingecko_market_chart(int(days), vs="eur")


@st.cache_data(ttl=CACHE_TTL_LONG)
def fetch_btc_ath_eur() -> Tuple[Optional[float], Optional[str]]:
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
