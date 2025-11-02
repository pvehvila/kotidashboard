# api.py
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import quote
import json

import datetime as dt
import pandas as pd
import requests
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

# ------------------- HTTP UTILS -------------------


def http_get_json(url: str, timeout: float = HTTP_TIMEOUT_S) -> dict:
    """Fetch JSON data from a URL with error handling."""
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    return response.json()


# ------------------- ELECTRICITY PRICES -------------------


def _parse_hour_from_item(
    item: dict, idx: int, date_ymd: datetime.date
) -> Optional[int]:
    """Parse hour from API item, handling various key formats."""
    for key in ("hour", "Hour", "H"):
        if value := item.get(key):
            try:
                hour = int(value)
                if 0 <= hour <= 23:
                    return hour
            except ValueError:
                pass

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
    ):
        if value := item.get(key):
            try:
                timestamp = str(value).replace("Z", "+00:00")
                dt_obj = datetime.fromisoformat(timestamp)
                dt_obj = (
                    dt_obj.replace(tzinfo=TZ)
                    if dt_obj.tzinfo is None
                    else dt_obj.astimezone(TZ)
                )
                if 0 <= dt_obj.hour <= 23 and dt_obj.date() == date_ymd:
                    return dt_obj.hour
            except ValueError:
                continue

    return idx if 0 <= idx <= 23 else None


def _parse_cents_from_item(item: dict) -> Optional[float]:
    """Parse price in cents from API item, handling various key formats."""
    for key in (
        "cents",
        "cents_per_kwh",
        "price",
        "Price",
        "value",
        "Value",
        "EUR_per_kWh",
    ):
        if value := item.get(key):
            try:
                price = float(value)
                return price if price >= 1.0 else price * 100.0
            except ValueError:
                pass
    return None


def _normalize_prices_list(
    items: List[dict], date_ymd: datetime.date
) -> List[Dict[str, float]]:
    """Normalize price data into a sorted list of hour-price dictionaries."""
    out_map = {}
    for idx, item in enumerate(items or []):
        try:
            hour = _parse_hour_from_item(item, idx, date_ymd)
            cents = _parse_cents_from_item(item)
            if (
                hour is not None
                and cents is not None
                and 0 <= hour <= 23
                and hour not in out_map
            ):
                out_map[hour] = float(cents)
        except Exception:
            continue
    return [{"hour": h, "cents": out_map[h]} for h in sorted(out_map.keys())]


def _fetch_from_sahkonhintatanaan(date_ymd: datetime.date) -> List[Dict[str, float]]:
    """Fetch electricity prices from sahkonhintatanaan.fi API."""
    url = f"https://www.sahkonhintatanaan.fi/api/v1/prices/{date_ymd:%Y}/{date_ymd:%m-%d}.json"
    data = http_get_json(url)
    items = data.get("prices", []) if isinstance(data, dict) else data or []
    return _normalize_prices_list(items, date_ymd)


def _fetch_from_porssisahko(date_ymd: datetime.date) -> List[Dict[str, float]]:
    """Fetch electricity prices from porssisahko.net API."""
    url = f"https://api.porssisahko.net/v1/price.json?date={date_ymd:%Y-%m-%d}"
    data = http_get_json(url)
    items = data.get("prices", []) if isinstance(data, dict) else data or []
    return _normalize_prices_list(items, date_ymd)


def fetch_prices_for(date_ymd: datetime.date) -> List[Dict[str, float]]:
    """Fetch electricity prices for a given date, trying multiple sources."""
    try:
        if prices := _fetch_from_sahkonhintatanaan(date_ymd):
            return prices
    except requests.HTTPError as e:
        if e.response and e.response.status_code not in (400, 404):
            report_error(f"prices: sahkonhintatanaan {date_ymd.isoformat()}", e)
    except Exception as e:
        report_error(f"prices: sahkonhintatanaan {date_ymd.isoformat()}", e)

    try:
        if prices := _fetch_from_porssisahko(date_ymd):
            return prices
    except requests.HTTPError as e:
        if e.response and e.response.status_code not in (400, 404):
            report_error(f"prices: porssisahko {date_ymd.isoformat()}", e)
    except Exception as e:
        report_error(f"prices: porssisahko {date_ymd.isoformat()}", e)

    return []


@st.cache_data(ttl=CACHE_TTL_MED)
def try_fetch_prices(date_ymd: datetime.date) -> Optional[List[Dict[str, float]]]:
    """Cached wrapper for fetching electricity prices."""
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
    {
        "text": "Paranna sitä, mihin kosket, ja jätä se paremmaksi kuin sen löysit.",
        "author": "Tuntematon",
    },
    {"text": "Kärsivällisyys on taito odottaa rauhassa.", "author": "Tuntematon"},
    {"text": "Päivän selkeys syntyy hetken huomiosta.", "author": "Tuntematon"},
]


def _from_zenquotes() -> Optional[Dict[str, str]]:
    """Fetch a daily quote from zenquotes.io."""
    try:
        data = http_get_json("https://zenquotes.io/api/today", timeout=HTTP_TIMEOUT_S)
        if isinstance(data, list) and data:
            quote = data[0]
            return {
                "text": quote.get("q", ""),
                "author": quote.get("a", ""),
                "source": "zenquotes",
            }
    except Exception as e:
        report_error("zen: zenquotes-today", e)
    return None


def _from_quotable() -> Optional[Dict[str, str]]:
    """Fetch a random quote from quotable.io."""
    try:
        data = http_get_json(
            "https://api.quotable.io/random?tags=wisdom|life|inspirational",
            timeout=HTTP_TIMEOUT_S,
        )
        return {
            "text": data.get("content", ""),
            "author": data.get("author", ""),
            "source": "quotable",
        }
    except Exception as e:
        report_error("zen: quotable", e)
    return None


@st.cache_data(ttl=CACHE_TTL_LONG)
def fetch_daily_quote(day_iso: str) -> Dict[str, str]:
    """Fetch or return a cached daily quote, falling back to local quotes."""
    if quote := _from_zenquotes():
        return quote
    if quote := _from_quotable():
        return quote
    idx = sum(map(ord, day_iso)) % len(LOCAL_ZEN)
    quote = dict(LOCAL_ZEN[idx])
    quote["source"] = "local"
    return quote


# ------------------- WEATHER -------------------

MAP_TRACE_ENABLED = False
_MAP_TRACE: List[Dict] = []


def _trace_map(
    wmo: Optional[int],
    is_day: bool,
    pop: Optional[int],
    temp_c: Optional[float],
    cloudcover: Optional[int],
    chosen_key: str,
    reason: str,
):
    """Log weather mapping decisions for debugging."""
    if not MAP_TRACE_ENABLED:
        return
    try:
        _MAP_TRACE.append(
            {
                "wmo": wmo,
                "is_day": is_day,
                "pop": pop,
                "temp_c": temp_c,
                "cloudcover": cloudcover,
                "key": chosen_key,
                "reason": reason,
            }
        )
        if len(_MAP_TRACE) > 200:
            del _MAP_TRACE[:-120]
    except Exception:
        pass


def get_map_trace() -> List[Dict]:
    """Return the current weather mapping trace."""
    return list(_MAP_TRACE)


def clear_map_trace():
    """Clear the weather mapping trace."""
    _MAP_TRACE.clear()


def _cloud_icon_from_cover(cover: Optional[int], is_day: bool) -> str:
    """Map cloud cover percentage to Foreca icon code."""
    prefix = "d" if is_day else "n"
    cover = 100 if cover is None else int(cover)
    if cover < CLOUD_T_CLEAR:
        return f"{prefix}000"  # Clear
    if cover < CLOUD_T_ALMOST:
        return f"{prefix}100"  # Almost clear
    if cover < CLOUD_T_PARTLY:
        return f"{prefix}200"  # Partly cloudy
    if cover < CLOUD_T_MOSTLY:
        return f"{prefix}300"  # Mostly cloudy
    return f"{prefix}400"  # Fully cloudy


@st.cache_data(ttl=CACHE_TTL_LONG)
def _load_wmo_foreca_map() -> Dict[str, Dict[int, str]]:
    """Load WMO to Foreca code mapping from Excel."""
    try:
        df = pd.read_excel("WMO_Foreca-koodit.xlsx", engine="openpyxl", header=[0, 1])
    except Exception:
        df = pd.read_excel("WMO_Foreca-koodit.xlsx", engine="openpyxl")

    def norm(s: str) -> str:
        return str(s).strip().lower().replace("ä", "a").replace("ö", "o")

    normcols = []
    if isinstance(df.columns, pd.MultiIndex):
        normcols = [(norm(c[0]), norm(c[1])) for c in df.columns]
    else:
        normcols = [(norm(c), "") for c in df.columns]

    wmo_idx = next(
        (i for i, (a, b) in enumerate(normcols) if "code" in a and "figure" in a), None
    )
    day_idx = next(
        (i for i, (a, b) in enumerate(normcols) if "foreca" in a and "paiva" in b), None
    )
    night_idx = next(
        (i for i, (a, b) in enumerate(normcols) if "foreca" in a and "yo" in b), None
    )
    if wmo_idx is None or day_idx is None or night_idx is None:
        raise KeyError(f"Columns not found: {list(df.columns)}")

    wmo_col = df.columns[wmo_idx]
    day_col = df.columns[day_idx]
    night_col = df.columns[night_idx]
    df = df.dropna(subset=[wmo_col])

    maps_day, maps_night = {}, {}
    last_day_full, last_night_full = None, None

    def _prep(val: str, prefix: str, last_full: Optional[str]) -> Optional[str]:
        if not val or val == "-" or pd.isna(val):
            return last_full
        val = str(val).strip().lower()
        if len(val) >= 4 and val[0] in ("d", "n") and val[1:].isdigit():
            return val
        if val.isdigit() and (len(val) == 3 or len(val) == 4):
            return prefix + val[-3:]
        return last_full

    for _, row in df.iterrows():
        try:
            wmo = int(row[wmo_col])
            raw_day = "" if pd.isna(row[day_col]) else str(row[day_col]).strip()
            raw_night = "" if pd.isna(row[night_col]) else str(row[night_col]).strip()
            day_full = _prep(raw_day, "d", last_day_full)
            night_full = _prep(raw_night, "n", last_night_full)

            if day_full:
                maps_day[wmo] = day_full
                last_day_full = day_full
            if night_full:
                maps_night[wmo] = night_full
                last_night_full = night_full
        except Exception:
            continue

    return {"day": maps_day, "night": maps_night}


def wmo_to_foreca_code(
    code: Optional[int],
    is_day: bool,
    pop: Optional[int] = None,
    temp_c: Optional[float] = None,
    cloudcover: Optional[int] = None,
) -> str:
    """Map WMO weather code to Foreca icon code, with cloud cover fallback."""
    maps = _load_wmo_foreca_map()
    if code is None:
        key = "d000" if is_day else "n000"
        _trace_map(code, is_day, pop, temp_c, cloudcover, key, "none → clear (default)")
        return key

    code = int(code)
    lookup = maps["day" if is_day else "night"]
    if key := lookup.get(code):
        _trace_map(
            code,
            is_day,
            pop,
            temp_c,
            cloudcover,
            key,
            "Excel mapping (päivä/yö, valmis avain)",
        )
        return key

    key = _cloud_icon_from_cover(cloudcover, is_day)
    _trace_map(
        code, is_day, pop, temp_c, cloudcover, key, "fallback: cloudcover bucket"
    )
    return key


@st.cache_data(ttl=CACHE_TTL_MED)
def fetch_weather_points(
    lat: float, lon: float, tz_name: str, offsets: Tuple[int, ...] = (0, 3, 6, 9, 12)
) -> Dict:
    """Fetch weather forecast points for specified hours."""
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

    now = datetime.now(TZ).replace(minute=0, second=0, microsecond=0)
    points = []

    for offset in offsets:
        target_time = now + timedelta(hours=offset)
        timestamp = target_time.strftime("%Y-%m-%dT%H:00")
        try:
            idx = times.index(timestamp)
        except ValueError:
            continue

        temp = temps[idx] if idx < len(temps) else None
        pop = pops[idx] if idx < len(pops) else None
        wmo = wmos[idx] if idx < len(wmos) else None
        ccov = covers[idx] if idx < len(covers) else None
        is_day_flag = (
            bool(int(isday[idx])) if idx < len(isday) else (6 <= target_time.hour <= 20)
        )

        points.append(
            {
                "label": "Nyt" if offset == 0 else f"+{offset} h",
                "hour": target_time.hour,
                "temp": temp,
                "pop": pop,
                "key": wmo_to_foreca_code(
                    wmo, is_day=is_day_flag, pop=pop, temp_c=temp, cloudcover=ccov
                ),
            }
        )

    min_temp, max_temp = None, None
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
    """Map WMO code to simplified weather icon key."""
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
    """Render a debug matrix for weather icons."""
    st.markdown(
        "<div class='card-title'>🧪 Sääikonit – pikatesti</div>", unsafe_allow_html=True
    )

    def render_row(label: str, items: List[Tuple[str, str]]) -> str:
        row_html = (
            "<div style='display:flex; gap:10px; flex-wrap:wrap; align-items:center;'>"
        )
        row_html += f"<div style='width:110px; opacity:.8;'>{label}</div>"
        for desc, key in items:
            img = render_foreca_icon(key, size=40)
            row_html += (
                f"<div style='display:grid; place-items:center; background:rgba(255,255,255,.06); padding:6px 8px; border-radius:10px; min-width:120px;'>"
                f"{img}<div style='font-size:.8rem; opacity:.85;'>{desc}<br/><code>{key}</code></div></div>"
            )
        row_html += "</div>"
        return row_html

    # Cloud cover variations
    cloud_rows = []
    for is_day in (True, False):
        items = [
            (
                f"cc {cc}%",
                wmo_to_foreca_code(0, is_day=is_day, pop=0, temp_c=10, cloudcover=cc),
            )
            for cc in (5, 30, 55, 75, 95)
        ]
        cloud_rows.append(
            render_row(f"{'Päivä' if is_day else 'Yö'} – pilvisyys", items)
        )

    # Continuous rain
    rain_rows = []
    for code in (61, 63, 65):
        cases = [
            (
                "päivä, PoP 20%",
                wmo_to_foreca_code(
                    code, is_day=True, pop=20, temp_c=5.0, cloudcover=70
                ),
            ),
            (
                "päivä, PoP 80%",
                wmo_to_foreca_code(
                    code, is_day=True, pop=80, temp_c=5.0, cloudcover=70
                ),
            ),
            (
                "päivä, 0°C (räntä)",
                wmo_to_foreca_code(
                    code, is_day=True, pop=80, temp_c=0.0, cloudcover=70
                ),
            ),
            (
                "yö, PoP 80%",
                wmo_to_foreca_code(
                    code, is_day=False, pop=80, temp_c=5.0, cloudcover=70
                ),
            ),
        ]
        rain_rows.append(render_row(f"WMO {code} – sade", cases))

    # Showers
    shower_rows = []
    for code in (80, 81, 82):
        cases = [
            (
                f"päivä, PoP {pop}%",
                wmo_to_foreca_code(
                    code, is_day=True, pop=pop, temp_c=10, cloudcover=60
                ),
            )
            for pop in (20, 80)
        ]
        shower_rows.append(render_row(f"WMO {code} – kuurot", cases))

    # Miscellaneous weather types
    misc_cases = [
        ("tihku heikko (51)", 51),
        ("tihku koht. (53)", 53),
        ("tihku voim. (55)", 55),
        ("jäätävä tihku (56)", 56),
        ("jäätävä sade h. (66)", 66),
        ("jäätävä sade v. (67)", 67),
        ("lumi (71)", 71),
        ("lumikuuro (85)", 85),
        ("ukkonen (95)", 95),
    ]
    misc_rows = render_row(
        "Muut",
        [
            (
                label,
                wmo_to_foreca_code(
                    code,
                    is_day=True,
                    pop=80,
                    temp_c=-2 if code in (71, 85) else 2,
                    cloudcover=80,
                ),
            )
            for label, code in misc_cases
        ],
    )

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
                f"<table style='width:100%; font-size:.9rem; border-collapse:collapse;'>"
                f"{head}{body}</table></div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                "<div class='hint'>Ei jälkiä vielä.</div>", unsafe_allow_html=True
            )


# ------------------- NAMEDAYS -------------------


def _resolve_nameday_file() -> Path:
    """Resolve the first existing nameday file from configured paths."""
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
    """Fetch today's namedays from a JSON file, supporting multiple schemas."""
    try:
        path = _resolve_nameday_file()
        if not path.exists():
            return "—"

        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        now = datetime.now(TZ)
        key_md = now.strftime("%m-%d")
        day_str = str(now.day)
        month_name = [
            "tammikuu",
            "helmikuu",
            "maaliskuu",
            "huhtikuu",
            "toukokuu",
            "kesäkuu",
            "heinäkuu",
            "elokuu",
            "syyskuu",
            "lokakuu",
            "marraskuu",
            "joulukuu",
        ][now.month - 1]

        # Schema A: Flat "%m-%d" mapping
        if isinstance(data, dict) and key_md in data:
            names = data[key_md]
            if isinstance(names, list):
                return ", ".join(n.strip() for n in names if str(n).strip()) or "—"
            if isinstance(names, str) and names.strip():
                return names.strip()
            return "—"

        # Schema B: Nested by month
        root = data.get("nimipäivät") if isinstance(data, dict) else None
        if isinstance(root, dict):
            month_obj = next(
                (
                    v
                    for k, v in root.items()
                    if isinstance(k, str) and k.strip().lower() == month_name
                ),
                None,
            )
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
    """
    Palauttaa dictin:
      {
        "holiday": <str|None>,       # päivän nimi (esim. "Itsenäisyyspäivä")
        "is_flag_day": <bool>,       # liputetaanko
        "is_holiday": <bool>         # onko vapaapyhä / lomapäivä
      }

    Tukee kahta skeemaa:
      A) {"10-09": {"name": "Aleksis Kiven päivä", "flag": true, "holiday": false}, ...}
         (tässä holiday on bool)
      B) [{"date":"2025-12-06","name":"Itsenäisyyspäivä","flag":true,"holiday":true}, ...]
         (lista objekteja)
    Huom: jos käytössä on vanhempi muoto, jossa "holiday" oli merkkijono (nimenä),
    tulkitaan se nimenä eikä lomapäivä-boolina.
    """
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
            # "holiday" voi olla joko bool (uudempi skeema) tai str (vanha: nimi)
            hol_field = entry.get("holiday")
            is_holiday = bool(entry.get("is_holiday")) or (
                isinstance(hol_field, bool) and hol_field is True
            )
            # jos name puuttuu mutta holiday on str, käytä sitä nimenä (takautuva tuki)
            if not name and isinstance(hol_field, str) and hol_field.strip():
                name = hol_field.strip()
            is_flag = bool(entry.get("flag") or entry.get("is_flag_day"))
            return {
                "holiday": (
                    name.strip() if isinstance(name, str) and name.strip() else None
                ),
                "is_flag_day": is_flag,
                "is_holiday": is_holiday,
            }

        # Skeema A: dict (%m-%d tai ISO)
        if isinstance(data, dict):
            entry = data.get(key_md) or data.get(key_iso)
            if isinstance(entry, dict):
                return parse_entry(entry)
            return out

        # Skeema B: lista
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
    """Fetch current Bitcoin price and 24h change in EUR."""
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=eur&include_24hr_change=true"
    data = http_get_json(url)
    btc = data.get("bitcoin", {})
    return {"price": btc.get("eur"), "change": btc.get("eur_24h_change")}


@st.cache_data(ttl=CACHE_TTL_MED)
def _coingecko_market_chart(days: int, vs: str = "eur") -> List[Tuple[datetime, float]]:
    """
    Palauttaa listan (datetime_tz, price) CoinGeckolta annetulle 'days' pituudelle.
    CoinGecko antaa ajat millisekunteina UTC:ssä -> muunnetaan TZ:ään.
    Downsamplataan maltillisesti, jotta pisteitä on noin 24 * days.
    """
    url = f"https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency={vs}&days={days}"
    data = http_get_json(url, timeout=HTTP_TIMEOUT_S)
    prices = data.get("prices", [])
    if not prices:
        return []

    # Tavoite ~24 pistettä / päivä
    target_points = max(24 * int(days), 24)
    keep_every = max(len(prices) // target_points, 1)

    out: List[Tuple[datetime, float]] = []
    for i, (ts_ms, val) in enumerate(prices):
        if i % keep_every != 0:
            continue
        ts = datetime.fromtimestamp(ts_ms / 1000, tz=TZ)
        out.append((ts, float(val)))

    # Varmuuden vuoksi järjestys
    out.sort(key=lambda x: x[0])
    return out


@st.cache_data(ttl=CACHE_TTL_MED)
def fetch_btc_last_24h_eur() -> List[Tuple[datetime, float]]:
    """BTC/EUR viimeiset 24 h."""
    return _coingecko_market_chart(1, vs="eur")


@st.cache_data(ttl=CACHE_TTL_MED)
def fetch_btc_last_7d_eur() -> List[Tuple[datetime, float]]:
    """BTC/EUR viimeiset 7 päivää."""
    return _coingecko_market_chart(7, vs="eur")


@st.cache_data(ttl=CACHE_TTL_MED)
def fetch_btc_last_30d_eur() -> List[Tuple[datetime, float]]:
    """BTC/EUR viimeiset 30 päivää."""
    return _coingecko_market_chart(30, vs="eur")


@st.cache_data(ttl=CACHE_TTL_MED)
def fetch_btc_eur_range(
    days: Optional[int] = None, hours: Optional[int] = None
) -> List[Tuple[datetime, float]]:
    """
    Generinen range-haku: jos annetaan hours, muunnetaan päiviksi (ylöspäin).
    """
    if days is None and hours is not None:
        days = max(1, int((hours + 23) // 24))
    if days is None:
        days = 7
    return _coingecko_market_chart(int(days), vs="eur")


@st.cache_data(ttl=CACHE_TTL_LONG)
def fetch_btc_ath_eur() -> Tuple[Optional[float], Optional[str]]:
    """Fetch Bitcoin all-time high price and date in EUR, with cache fallback."""
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


# api.py
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import streamlit as st

from config import (
    HTTP_TIMEOUT_S,
    CACHE_TTL_SHORT,
    CACHE_TTL_MED,
    CACHE_TTL_LONG,
)

# ------------------- HTTP UTILS -------------------


def http_get_json(url: str, timeout: float = HTTP_TIMEOUT_S) -> dict:
    """Fetch JSON data from a URL with error handling and a proper User-Agent."""
    headers = {
        "User-Agent": "HomeDashboard/1.0 (+https://github.com/pvehvila/kotidashboard)"
    }
    try:
        resp = requests.get(url, timeout=timeout, headers=headers)
        # Yritä uudestaan 429/403, lyhyt viive
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


def _parse_hour_from_item(
    item: dict, idx: int, date_ymd: datetime.date
) -> Optional[int]:
    """Parse hour from API item, handling various key formats."""
    for key in ("hour", "Hour", "H"):
        if value := item.get(key):
            try:
                hour = int(value)
                if 0 <= hour <= 23:
                    return hour
            except ValueError:
                pass

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
    ):
        if value := item.get(key):
            try:
                timestamp = str(value).replace("Z", "+00:00")
                dt_obj = datetime.fromisoformat(timestamp)
                dt_obj = (
                    dt_obj.replace(tzinfo=TZ)
                    if dt_obj.tzinfo is None
                    else dt_obj.astimezone(TZ)
                )
                if 0 <= dt_obj.hour <= 23 and dt_obj.date() == date_ymd:
                    return dt_obj.hour
            except ValueError:
                continue

    return idx if 0 <= idx <= 23 else None


def _parse_cents_from_item(item: dict) -> Optional[float]:
    """Parse price in cents from API item, handling various key formats."""
    for key in (
        "cents",
        "cents_per_kwh",
        "price",
        "Price",
        "value",
        "Value",
        "EUR_per_kWh",
    ):
        if value := item.get(key):
            try:
                price = float(value)
                return price if price >= 1.0 else price * 100.0
            except ValueError:
                pass
    return None


def _normalize_prices_list(
    items: List[dict], date_ymd: datetime.date
) -> List[Dict[str, float]]:
    """Normalize price data into a sorted list of hour-price dictionaries."""
    out_map = {}
    for idx, item in enumerate(items or []):
        try:
            hour = _parse_hour_from_item(item, idx, date_ymd)
            cents = _parse_cents_from_item(item)
            if (
                hour is not None
                and cents is not None
                and 0 <= hour <= 23
                and hour not in out_map
            ):
                out_map[hour] = float(cents)
        except Exception:
            continue
    return [{"hour": h, "cents": out_map[h]} for h in sorted(out_map.keys())]


def _fetch_from_sahkonhintatanaan(date_ymd: datetime.date) -> List[Dict[str, float]]:
    """Fetch electricity prices from sahkonhintatanaan.fi API."""
    url = f"https://www.sahkonhintatanaan.fi/api/v1/prices/{date_ymd:%Y}/{date_ymd:%m-%d}.json"
    data = http_get_json(url)
    items = data.get("prices", []) if isinstance(data, dict) else data or []
    return _normalize_prices_list(items, date_ymd)


def _fetch_from_porssisahko(date_ymd: datetime.date) -> List[Dict[str, float]]:
    """Fetch electricity prices from porssisahko.net API."""
    url = f"https://api.porssisahko.net/v1/price.json?date={date_ymd:%Y-%m-%d}"
    data = http_get_json(url)
    items = data.get("prices", []) if isinstance(data, dict) else data or []
    return _normalize_prices_list(items, date_ymd)


def fetch_prices_for(date_ymd: datetime.date) -> List[Dict[str, float]]:
    """Fetch electricity prices for a given date, trying multiple sources."""
    try:
        if prices := _fetch_from_sahkonhintatanaan(date_ymd):
            return prices
    except requests.HTTPError as e:
        if e.response and e.response.status_code not in (400, 404):
            report_error(f"prices: sahkonhintatanaan {date_ymd.isoformat()}", e)
    except Exception as e:
        report_error(f"prices: sahkonhintatanaan {date_ymd.isoformat()}", e)

    try:
        if prices := _fetch_from_porssisahko(date_ymd):
            return prices
    except requests.HTTPError as e:
        if e.response and e.response.status_code not in (400, 404):
            report_error(f"prices: porssisahko {date_ymd.isoformat()}", e)
    except Exception as e:
        report_error(f"prices: porssisahko {date_ymd.isoformat()}", e)

    return []


@st.cache_data(ttl=CACHE_TTL_MED)
def try_fetch_prices(date_ymd: datetime.date) -> Optional[List[Dict[str, float]]]:
    """Cached wrapper for fetching electricity prices."""
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
    {
        "text": "Paranna sitä, mihin kosket, ja jätä se paremmaksi kuin sen löysit.",
        "author": "Tuntematon",
    },
    {"text": "Kärsivällisyys on taito odottaa rauhassa.", "author": "Tuntematon"},
    {"text": "Päivän selkeys syntyy hetken huomiosta.", "author": "Tuntematon"},
]


def _from_zenquotes() -> Optional[Dict[str, str]]:
    """Fetch a daily quote from zenquotes.io."""
    try:
        data = http_get_json("https://zenquotes.io/api/today", timeout=HTTP_TIMEOUT_S)
        if isinstance(data, list) and data:
            quote = data[0]
            return {
                "text": quote.get("q", ""),
                "author": quote.get("a", ""),
                "source": "zenquotes",
            }
    except Exception as e:
        report_error("zen: zenquotes-today", e)
    return None


def _from_quotable() -> Optional[Dict[str, str]]:
    """Fetch a random quote from quotable.io."""
    try:
        data = http_get_json(
            "https://api.quotable.io/random?tags=wisdom|life|inspirational",
            timeout=HTTP_TIMEOUT_S,
        )
        return {
            "text": data.get("content", ""),
            "author": data.get("author", ""),
            "source": "quotable",
        }
    except Exception as e:
        report_error("zen: quotable", e)
    return None


@st.cache_data(ttl=CACHE_TTL_LONG)
def fetch_daily_quote(day_iso: str) -> Dict[str, str]:
    """Fetch or return a cached daily quote, falling back to local quotes."""
    if quote := _from_zenquotes():
        return quote
    if quote := _from_quotable():
        return quote
    idx = sum(map(ord, day_iso)) % len(LOCAL_ZEN)
    quote = dict(LOCAL_ZEN[idx])
    quote["source"] = "local"
    return quote


# ------------------- WEATHER -------------------

MAP_TRACE_ENABLED = False
_MAP_TRACE: List[Dict] = []


def _trace_map(
    wmo: Optional[int],
    is_day: bool,
    pop: Optional[int],
    temp_c: Optional[float],
    cloudcover: Optional[int],
    chosen_key: str,
    reason: str,
):
    """Log weather mapping decisions for debugging."""
    if not MAP_TRACE_ENABLED:
        return
    try:
        _MAP_TRACE.append(
            {
                "wmo": wmo,
                "is_day": is_day,
                "pop": pop,
                "temp_c": temp_c,
                "cloudcover": cloudcover,
                "key": chosen_key,
                "reason": reason,
            }
        )
        if len(_MAP_TRACE) > 200:
            del _MAP_TRACE[:-120]
    except Exception:
        pass


def get_map_trace() -> List[Dict]:
    """Return the current weather mapping trace."""
    return list(_MAP_TRACE)


def clear_map_trace():
    """Clear the weather mapping trace."""
    _MAP_TRACE.clear()


def _cloud_icon_from_cover(cover: Optional[int], is_day: bool) -> str:
    """Map cloud cover percentage to Foreca icon code."""
    prefix = "d" if is_day else "n"
    cover = 100 if cover is None else int(cover)
    if cover < CLOUD_T_CLEAR:
        return f"{prefix}000"  # Clear
    if cover < CLOUD_T_ALMOST:
        return f"{prefix}100"  # Almost clear
    if cover < CLOUD_T_PARTLY:
        return f"{prefix}200"  # Partly cloudy
    if cover < CLOUD_T_MOSTLY:
        return f"{prefix}300"  # Mostly cloudy
    return f"{prefix}400"  # Fully cloudy


@st.cache_data(ttl=CACHE_TTL_LONG)
def _load_wmo_foreca_map() -> Dict[str, Dict[int, str]]:
    """Load WMO to Foreca code mapping from Excel."""
    try:
        df = pd.read_excel("WMO_Foreca-koodit.xlsx", engine="openpyxl", header=[0, 1])
    except Exception:
        df = pd.read_excel("WMO_Foreca-koodit.xlsx", engine="openpyxl")

    def norm(s: str) -> str:
        return str(s).strip().lower().replace("ä", "a").replace("ö", "o")

    normcols = []
    if isinstance(df.columns, pd.MultiIndex):
        normcols = [(norm(c[0]), norm(c[1])) for c in df.columns]
    else:
        normcols = [(norm(c), "") for c in df.columns]

    wmo_idx = next(
        (i for i, (a, b) in enumerate(normcols) if "code" in a and "figure" in a), None
    )
    day_idx = next(
        (i for i, (a, b) in enumerate(normcols) if "foreca" in a and "paiva" in b), None
    )
    night_idx = next(
        (i for i, (a, b) in enumerate(normcols) if "foreca" in a and "yo" in b), None
    )
    if wmo_idx is None or day_idx is None or night_idx is None:
        raise KeyError(f"Columns not found: {list(df.columns)}")

    wmo_col = df.columns[wmo_idx]
    day_col = df.columns[day_idx]
    night_col = df.columns[night_idx]
    df = df.dropna(subset=[wmo_col])

    maps_day, maps_night = {}, {}
    last_day_full, last_night_full = None, None

    def _prep(val: str, prefix: str, last_full: Optional[str]) -> Optional[str]:
        if not val or val == "-" or pd.isna(val):
            return last_full
        val = str(val).strip().lower()
        if len(val) >= 4 and val[0] in ("d", "n") and val[1:].isdigit():
            return val
        if val.isdigit() and (len(val) == 3 or len(val) == 4):
            return prefix + val[-3:]
        return last_full

    for _, row in df.iterrows():
        try:
            wmo = int(row[wmo_col])
            raw_day = "" if pd.isna(row[day_col]) else str(row[day_col]).strip()
            raw_night = "" if pd.isna(row[night_col]) else str(row[night_col]).strip()
            day_full = _prep(raw_day, "d", last_day_full)
            night_full = _prep(raw_night, "n", last_night_full)

            if day_full:
                maps_day[wmo] = day_full
                last_day_full = day_full
            if night_full:
                maps_night[wmo] = night_full
                last_night_full = night_full
        except Exception:
            continue

    return {"day": maps_day, "night": maps_night}


def wmo_to_foreca_code(
    code: Optional[int],
    is_day: bool,
    pop: Optional[int] = None,
    temp_c: Optional[float] = None,
    cloudcover: Optional[int] = None,
) -> str:
    """Map WMO weather code to Foreca icon code, with cloud cover fallback."""
    maps = _load_wmo_foreca_map()
    if code is None:
        key = "d000" if is_day else "n000"
        _trace_map(code, is_day, pop, temp_c, cloudcover, key, "none → clear (default)")
        return key

    code = int(code)
    lookup = maps["day" if is_day else "night"]
    if key := lookup.get(code):
        _trace_map(
            code,
            is_day,
            pop,
            temp_c,
            cloudcover,
            key,
            "Excel mapping (päivä/yö, valmis avain)",
        )
        return key

    key = _cloud_icon_from_cover(cloudcover, is_day)
    _trace_map(
        code, is_day, pop, temp_c, cloudcover, key, "fallback: cloudcover bucket"
    )
    return key


@st.cache_data(ttl=CACHE_TTL_MED)
def fetch_weather_points(
    lat: float, lon: float, tz_name: str, offsets: Tuple[int, ...] = (0, 3, 6, 9, 12)
) -> Dict:
    """Fetch weather forecast points for specified hours."""
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

    now = datetime.now(TZ).replace(minute=0, second=0, microsecond=0)
    points = []

    for offset in offsets:
        target_time = now + timedelta(hours=offset)
        timestamp = target_time.strftime("%Y-%m-%dT%H:00")
        try:
            idx = times.index(timestamp)
        except ValueError:
            continue

        temp = temps[idx] if idx < len(temps) else None
        pop = pops[idx] if idx < len(pops) else None
        wmo = wmos[idx] if idx < len(wmos) else None
        ccov = covers[idx] if idx < len(covers) else None
        is_day_flag = (
            bool(int(isday[idx])) if idx < len(isday) else (6 <= target_time.hour <= 20)
        )

        points.append(
            {
                "label": "Nyt" if offset == 0 else f"+{offset} h",
                "hour": target_time.hour,
                "temp": temp,
                "pop": pop,
                "key": wmo_to_foreca_code(
                    wmo, is_day=is_day_flag, pop=pop, temp_c=temp, cloudcover=ccov
                ),
            }
        )

    min_temp, max_temp = None, None
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
    """Map WMO code to simplified weather icon key."""
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
    """Render a debug matrix for weather icons."""
    st.markdown(
        "<div class='card-title'>🧪 Sääikonit – pikatesti</div>", unsafe_allow_html=True
    )

    def render_row(label: str, items: List[Tuple[str, str]]) -> str:
        row_html = (
            "<div style='display:flex; gap:10px; flex-wrap:wrap; align-items:center;'>"
        )
        row_html += f"<div style='width:110px; opacity:.8;'>{label}</div>"
        for desc, key in items:
            img = render_foreca_icon(key, size=40)
            row_html += (
                f"<div style='display:grid; place-items:center; background:rgba(255,255,255,.06); padding:6px 8px; border-radius:10px; min-width:120px;'>"
                f"{img}<div style='font-size:.8rem; opacity:.85;'>{desc}<br/><code>{key}</code></div></div>"
            )
        row_html += "</div>"
        return row_html

    # Cloud cover variations
    cloud_rows = []
    for is_day in (True, False):
        items = [
            (
                f"cc {cc}%",
                wmo_to_foreca_code(0, is_day=is_day, pop=0, temp_c=10, cloudcover=cc),
            )
            for cc in (5, 30, 55, 75, 95)
        ]
        cloud_rows.append(
            render_row(f"{'Päivä' if is_day else 'Yö'} – pilvisyys", items)
        )

    # Continuous rain
    rain_rows = []
    for code in (61, 63, 65):
        cases = [
            (
                "päivä, PoP 20%",
                wmo_to_foreca_code(
                    code, is_day=True, pop=20, temp_c=5.0, cloudcover=70
                ),
            ),
            (
                "päivä, PoP 80%",
                wmo_to_foreca_code(
                    code, is_day=True, pop=80, temp_c=5.0, cloudcover=70
                ),
            ),
            (
                "päivä, 0°C (räntä)",
                wmo_to_foreca_code(
                    code, is_day=True, pop=80, temp_c=0.0, cloudcover=70
                ),
            ),
            (
                "yö, PoP 80%",
                wmo_to_foreca_code(
                    code, is_day=False, pop=80, temp_c=5.0, cloudcover=70
                ),
            ),
        ]
        rain_rows.append(render_row(f"WMO {code} – sade", cases))

    # Showers
    shower_rows = []
    for code in (80, 81, 82):
        cases = [
            (
                f"päivä, PoP {pop}%",
                wmo_to_foreca_code(
                    code, is_day=True, pop=pop, temp_c=10, cloudcover=60
                ),
            )
            for pop in (20, 80)
        ]
        shower_rows.append(render_row(f"WMO {code} – kuurot", cases))

    # Miscellaneous weather types
    misc_cases = [
        ("tihku heikko (51)", 51),
        ("tihku koht. (53)", 53),
        ("tihku voim. (55)", 55),
        ("jäätävä tihku (56)", 56),
        ("jäätävä sade h. (66)", 66),
        ("jäätävä sade v. (67)", 67),
        ("lumi (71)", 71),
        ("lumikuuro (85)", 85),
        ("ukkonen (95)", 95),
    ]
    misc_rows = render_row(
        "Muut",
        [
            (
                label,
                wmo_to_foreca_code(
                    code,
                    is_day=True,
                    pop=80,
                    temp_c=-2 if code in (71, 85) else 2,
                    cloudcover=80,
                ),
            )
            for label, code in misc_cases
        ],
    )

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
                f"<table style='width:100%; font-size:.9rem; border-collapse:collapse;'>"
                f"{head}{body}</table></div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                "<div class='hint'>Ei jälkiä vielä.</div>", unsafe_allow_html=True
            )


# ------------------- NAMEDAYS -------------------


def _resolve_nameday_file() -> Path:
    """Resolve the first existing nameday file from configured paths."""
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
    """Fetch today's namedays from a JSON file, supporting multiple schemas."""
    try:
        path = _resolve_nameday_file()
        if not path.exists():
            return "—"

        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        now = datetime.now(TZ)
        key_md = now.strftime("%m-%d")
        day_str = str(now.day)
        month_name = [
            "tammikuu",
            "helmikuu",
            "maaliskuu",
            "huhtikuu",
            "toukokuu",
            "kesäkuu",
            "heinäkuu",
            "elokuu",
            "syyskuu",
            "lokakuu",
            "marraskuu",
            "joulukuu",
        ][now.month - 1]

        # Schema A: Flat "%m-%d" mapping
        if isinstance(data, dict) and key_md in data:
            names = data[key_md]
            if isinstance(names, list):
                return ", ".join(n.strip() for n in names if str(n).strip()) or "—"
            if isinstance(names, str) and names.strip():
                return names.strip()
            return "—"

        # Schema B: Nested by month
        root = data.get("nimipäivät") if isinstance(data, dict) else None
        if isinstance(root, dict):
            month_obj = next(
                (
                    v
                    for k, v in root.items()
                    if isinstance(k, str) and k.strip().lower() == month_name
                ),
                None,
            )
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
    """
    Palauttaa dictin:
      {
        "holiday": <str|None>,       # päivän nimi (esim. "Itsenäisyyspäivä")
        "is_flag_day": <bool>,       # liputetaanko
        "is_holiday": <bool>         # onko vapaapyhä / lomapäivä
      }

    Tukee kahta skeemaa:
      A) {"10-09": {"name": "Aleksis Kiven päivä", "flag": true, "holiday": false}, ...}
         (tässä holiday on bool)
      B) [{"date":"2025-12-06","name":"Itsenäisyyspäivä","flag":true,"holiday":true}, ...]
         (lista objekteja)
    Huom: jos käytössä on vanhempi muoto, jossa "holiday" oli merkkijono (nimenä),
    tulkitaan se nimenä eikä lomapäivä-boolina.
    """
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
            # "holiday" voi olla joko bool (uudempi skeema) tai str (vanha: nimi)
            hol_field = entry.get("holiday")
            is_holiday = bool(entry.get("is_holiday")) or (
                isinstance(hol_field, bool) and hol_field is True
            )
            # jos name puuttuu mutta holiday on str, käytä sitä nimenä (takautuva tuki)
            if not name and isinstance(hol_field, str) and hol_field.strip():
                name = hol_field.strip()
            is_flag = bool(entry.get("flag") or entry.get("is_flag_day"))
            return {
                "holiday": (
                    name.strip() if isinstance(name, str) and name.strip() else None
                ),
                "is_flag_day": is_flag,
                "is_holiday": is_holiday,
            }

        # Skeema A: dict (%m-%d tai ISO)
        if isinstance(data, dict):
            entry = data.get(key_md) or data.get(key_iso)
            if isinstance(entry, dict):
                return parse_entry(entry)
            return out

        # Skeema B: lista
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
    """Fetch current Bitcoin price and 24h change in EUR."""
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=eur&include_24hr_change=true"
    data = http_get_json(url)
    btc = data.get("bitcoin", {})
    return {"price": btc.get("eur"), "change": btc.get("eur_24h_change")}


@st.cache_data(ttl=CACHE_TTL_MED)
def _coingecko_market_chart(days: int, vs: str = "eur") -> List[Tuple[datetime, float]]:
    """
    Palauttaa listan (datetime_tz, price) CoinGeckolta annetulle 'days' pituudelle.
    CoinGecko antaa ajat millisekunteina UTC:ssä -> muunnetaan TZ:ään.
    Downsamplataan maltillisesti, jotta pisteitä on noin 24 * days.
    """
    url = f"https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency={vs}&days={days}"
    data = http_get_json(url, timeout=HTTP_TIMEOUT_S)
    prices = data.get("prices", [])
    if not prices:
        return []

    # Tavoite ~24 pistettä / päivä
    target_points = max(24 * int(days), 24)
    keep_every = max(len(prices) // target_points, 1)

    out: List[Tuple[datetime, float]] = []
    for i, (ts_ms, val) in enumerate(prices):
        if i % keep_every != 0:
            continue
        ts = datetime.fromtimestamp(ts_ms / 1000, tz=TZ)
        out.append((ts, float(val)))

    # Varmuuden vuoksi järjestys
    out.sort(key=lambda x: x[0])
    return out


@st.cache_data(ttl=CACHE_TTL_MED)
def fetch_btc_last_24h_eur() -> List[Tuple[datetime, float]]:
    """BTC/EUR viimeiset 24 h."""
    return _coingecko_market_chart(1, vs="eur")


@st.cache_data(ttl=CACHE_TTL_MED)
def fetch_btc_last_7d_eur() -> List[Tuple[datetime, float]]:
    """BTC/EUR viimeiset 7 päivää."""
    return _coingecko_market_chart(7, vs="eur")


@st.cache_data(ttl=CACHE_TTL_MED)
def fetch_btc_last_30d_eur() -> List[Tuple[datetime, float]]:
    """BTC/EUR viimeiset 30 päivää."""
    return _coingecko_market_chart(30, vs="eur")


@st.cache_data(ttl=CACHE_TTL_MED)
def fetch_btc_eur_range(
    days: Optional[int] = None, hours: Optional[int] = None
) -> List[Tuple[datetime, float]]:
    """
    Generinen range-haku: jos annetaan hours, muunnetaan päiviksi (ylöspäin).
    """
    if days is None and hours is not None:
        days = max(1, int((hours + 23) // 24))
    if days is None:
        days = 7
    return _coingecko_market_chart(int(days), vs="eur")


@st.cache_data(ttl=CACHE_TTL_LONG)
def fetch_btc_ath_eur() -> Tuple[Optional[float], Optional[str]]:
    """Fetch Bitcoin all-time high price and date in EUR, with cache fallback."""
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
