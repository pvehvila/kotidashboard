
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import quote
from src.api.http import http_get_json

from src.paths import DATA

from src.config import (
    TZ,
    CLOUD_T_CLEAR,
    CLOUD_T_ALMOST,
    CLOUD_T_PARTLY,
    CLOUD_T_MOSTLY,
)
from src.weather_icons import render_foreca_icon

import pandas as pd
import streamlit as st

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
    candidates = []
    if path:
        candidates.append(Path(path))

    root = Path(__file__).parent
    for name in ("wmo_foreca_map.xlsx", "wmo_foreca_map.csv", "mappings.xlsx", "mappings.csv"):
        candidates.append(root / name)

    # UUSI: katso data-kansioon se sinun oikea nimi
    candidates.append(DATA / "WMO_Foreca-koodit.xlsx")
    
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
