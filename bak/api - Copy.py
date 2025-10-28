# api.py
import datetime as dt
import json
import requests

from pathlib import Path
from config import TZ, HTTP_TIMEOUT_S, CACHE_TTL_SHORT, CACHE_TTL_MED, CACHE_TTL_LONG, ATH_CACHE_FILE, NAMEDAY_FILE, NAMEDAY_PATHS
from config import POP_POSSIBLE_THRESHOLD, SLEET_TEMP_MIN, SLEET_TEMP_MAX, CLOUD_T_CLEAR, CLOUD_T_ALMOST, CLOUD_T_PARTLY, CLOUD_T_MOSTLY    
from urllib.parse import quote
from utils import report_error

import streamlit as st

def http_get_json(url: str, timeout: float = HTTP_TIMEOUT_S):
    r = requests.get(url, timeout=timeout)
    r.raise_for_status()
    return r.json()

# ---- SÄHKÖHINNAT ----
def _parse_hour_from_item(item: dict, idx: int, date_ymd: dt.date) -> int | None:
    # (Sama koodi kuin alkuperäisessä)
    for k in ("hour", "Hour", "H"):
        v = item.get(k)
        if v is not None:
            try:
                h = int(v)
                if 0 <= h <= 23:
                    return h
            except Exception:
                pass
    for k in ("time", "Time", "timestamp", "Timestamp", "datetime", "DateTime", "start", "Start", "startDate"):
        v = item.get(k)
        if not v:
            continue
        try:
            s = str(v).replace("Z", "+00:00")
            dt_obj = dt.datetime.fromisoformat(s)
            if dt_obj.tzinfo is None:
                dt_obj = dt_obj.replace(tzinfo=TZ)
            else:
                dt_obj = dt_obj.astimezone(TZ)
            h = dt_obj.hour
            if 0 <= h <= 23 and dt_obj.date() == date_ymd:
                return h
        except Exception:
            continue
    if 0 <= idx <= 23:
        return idx
    return None

def _parse_cents_from_item(item: dict) -> float | None:
    # (Sama koodi kuin alkuperäisessä)
    for k in ("cents", "cents_per_kwh", "price", "Price", "value", "Value", "EUR_per_kWh"):
        v = item.get(k)
        if v is not None:
            try:
                f = float(v)
                return f if f >= 1.0 else (f * 100.0)
            except Exception:
                pass
    return None

def _normalize_prices_list(items, date_ymd: dt.date):
    # (Sama koodi kuin alkuperäisessä)
    out_map = {}
    for idx, item in enumerate(items or []):
        try:
            h = _parse_hour_from_item(item, idx, date_ymd)
            c = _parse_cents_from_item(item)
            if h is None or c is None:
                continue
            if 0 <= h <= 23 and h not in out_map:
                out_map[h] = float(c)
        except Exception:
            continue
    return [{"hour": h, "cents": out_map[h]} for h in sorted(out_map.keys())]

def _fetch_from_sahkonhintatanaan(date_ymd: dt.date):
    # (Sama koodi kuin alkuperäisessä)
    url = f"https://www.sahkonhintatanaan.fi/api/v1/prices/{date_ymd:%Y}/{date_ymd:%m-%d}.json"
    data = http_get_json(url)
    items = data.get("prices") if isinstance(data, dict) else data
    if not isinstance(items, list):
        items = []
    return _normalize_prices_list(items, date_ymd)

def _fetch_from_porssisahko(date_ymd: dt.date):
    # (Sama koodi kuin alkuperäisessä)
    url = f"https://api.porssisahko.net/v1/price.json?date={date_ymd:%Y-%m-%d}"
    data = http_get_json(url)
    items = data.get("prices") if isinstance(data, dict) else data
    if not isinstance(items, list):
        items = []
    return _normalize_prices_list(items, date_ymd)

def fetch_prices_for(date_ymd: dt.date):
    # (Sama koodi kuin alkuperäisessä)
    try:
        res = _fetch_from_sahkonhintatanaan(date_ymd)
        if res:
            return res
    except requests.HTTPError as e:
        if not (e.response is not None and e.response.status_code in (400, 404)):
            report_error(f"prices: porssisahko {date_ymd.isoformat()}", e)
    except Exception as e:
        report_error(f"prices: sahkonhintatanaan {date_ymd.isoformat()}", e)
    
    try:
        res = _fetch_from_porssisahko(date_ymd)
        if res:
            return res
    except requests.HTTPError as e:
        if not (e.response is not None and e.response.status_code in (400, 404)):
            report_error(f"prices: porssisahko {date_ymd.isoformat()}", e)
    except Exception as e:
        report_error(f"prices: porssisahko {date_ymd.isoformat()}", e)
    
    return []

@st.cache_data(ttl=CACHE_TTL_MED)
def try_fetch_prices(date_ymd: dt.date):
    # (Sama koodi kuin alkuperäisessä)
    try:
        return fetch_prices_for(date_ymd)
    except requests.HTTPError as e:
        if e.response is not None and e.response.status_code in (400, 404):
            return None
        report_error(f"prices: fetch {date_ymd.isoformat()}", e); return None
    except Exception as e:
        report_error(f"prices: fetch {date_ymd.isoformat()}", e); return None

# ---- ZEN-LAINAUKSET ----
LOCAL_ZEN = [
    {"text": "Hiljaisuus on vastaus, jota etsit.", "author": "Tuntematon"},
    {"text": "Paranna sitä, mihin kosket, ja jätä se paremmaksi kuin sen löysit.", "author": "Tuntematon"},
    {"text": "Kärsivällisyys on taito odottaa rauhassa.", "author": "Tuntematon"},
    {"text": "Päivän selkeys syntyy hetken huomiosta.", "author": "Tuntematon"},
]

def _from_zenquotes() -> dict | None:
    # (Sama koodi kuin alkuperäisessä)
    try:
        data = http_get_json("https://zenquotes.io/api/today", timeout=HTTP_TIMEOUT_S)
        if isinstance(data, list) and data:
            q = data[0]
            return {"text": q.get("q", ""), "author": q.get("a", ""), "source": "zenquotes"}
    except Exception as e:
        report_error("zen: zenquotes-today", e)
    return None

def _from_quotable() -> dict | None:
    # (Sama koodi kuin alkuperäisessä)
    try:
        data = http_get_json("https://api.quotable.io/random?tags=wisdom|life|inspirational", timeout=HTTP_TIMEOUT_S)
        return {"text": data.get("content", ""), "author": data.get("author", ""), "source": "quotable"}
    except Exception as e:
        report_error("zen: quotable", e)
    return None

@st.cache_data(ttl=CACHE_TTL_LONG)
def fetch_daily_quote(day_iso: str) -> dict:
    # (Sama koodi kuin alkuperäisessä)
    q = _from_zenquotes()
    if not q:
        q = _from_quotable()
    if not q:
        i = (sum(map(ord, day_iso)) % len(LOCAL_ZEN))
        q = dict(LOCAL_ZEN[i])
        q["source"] = "local"
    return q

# ---- SÄÄ ----

# --- Mapping trace (debug) ---
MAP_TRACE_ENABLED = False  # laita False kun et tarvitse jäljitystä
_MAP_TRACE = []  # kerää viimeisimmät rivit

def _trace_map(wmo, is_day, pop, temp_c, cloudcover, chosen_key, reason):
    if not MAP_TRACE_ENABLED:
        return
    try:
        _MAP_TRACE.append({
            "wmo": wmo, "is_day": is_day, "pop": pop,
            "temp_c": temp_c, "cloudcover": cloudcover,
            "key": chosen_key, "reason": reason
        })
        # pidä listan koko kurissa
        if len(_MAP_TRACE) > 200:
            del _MAP_TRACE[:-120]
    except Exception:
        pass

def get_map_trace():
    return list(_MAP_TRACE)

def clear_map_trace():
    _MAP_TRACE.clear()

def _cloud_icon_from_cover(cover: int | None, is_day: bool) -> str:
    p = "d" if is_day else "n"
    c = 100 if cover is None else int(cover)
    if c < CLOUD_T_CLEAR:   return f"{p}000"  # selkeä
    if c < CLOUD_T_ALMOST:  return f"{p}100"  # melkein selkeä
    if c < CLOUD_T_PARTLY:  return f"{p}200"  # puolipilvinen
    if c < CLOUD_T_MOSTLY:  return f"{p}300"  # pilvinen
    return f"{p}400"                          # täysin pilvessä

# --- WMO→Foreca mapping Excelistä (päivitetty) ---
import pandas as pd
import math

@st.cache_data(ttl=CACHE_TTL_LONG)
def _load_wmo_foreca_map() -> dict[str, dict[int, str]]:
    """
    maps['day'][wmo]   -> 'dXXX'
    maps['night'][wmo] -> 'nXXX'
    Lähde-Excel: 'Code figure' ja ('WMO to Forecan','Päivä'/'Yö').
    '-' = käytä edellistä ei-tyhjää arvoa sarakkeessa.
    Solussa voi olla valmiiksi 'dXXX'/'nXXX' TAI pelkkä 'XXX' → lisätään etuliite.
    """
    try:
        df = pd.read_excel("WMO_Foreca-koodit.xlsx", engine="openpyxl", header=[0, 1])
    except Exception:
        df = pd.read_excel("WMO_Foreca-koodit.xlsx", engine="openpyxl")

    def norm(s): return str(s).strip().lower().replace("ä","a").replace("ö","o")

    # Muodosta normalisoidut (level0, level1) otsikot
    normcols = []
    if isinstance(df.columns, pd.MultiIndex):
        for c in df.columns:
            t = tuple(list(c) + [""] * (2 - len(c)))[:2]
            normcols.append((norm(t[0]), norm(t[1])))
    else:
        for c in df.columns:
            normcols.append((norm(c), ""))

    # Löydä sarakkeet
    wmo_idx   = next((i for i,(a,b) in enumerate(normcols) if "code" in a and "figure" in a), None)
    day_idx   = next((i for i,(a,b) in enumerate(normcols) if "foreca" in a and "paiva" in b), None)
    night_idx = next((i for i,(a,b) in enumerate(normcols) if "foreca" in a and "yo"    in b), None)
    if wmo_idx is None or day_idx is None or night_idx is None:
        raise KeyError(f"Sarakkeita ei löytynyt: {list(df.columns)}")

    wmo_col   = df.columns[wmo_idx]
    day_col   = df.columns[day_idx]
    night_col = df.columns[night_idx]

    df = df.dropna(subset=[wmo_col])

    maps_day, maps_night = {}, {}
    last_day_full, last_night_full = None, None

    def _prep(val: str, prefix: str, last_full: str | None) -> str | None:
        # '-'/tyhjä → palaudu edelliseen
        if val is None or val == "" or val == "-":
            return last_full
        v = val.strip().lower()
        # Jos Excelissä on jo 'dxxx' tai 'nxxx', käytä sellaisenaan
        if len(v) >= 4 and v[0] in ("d","n") and v[1:].isdigit():
            return v
        # Jos pelkkä kolminumeroinen koodi, lisää etuliite 'd'/'n'
        if v.isdigit() and (len(v) == 3 or len(v) == 4):
            return prefix + v[-3:]
        # Muussa tapauksessa yritä viimeistä tunnettuakin
        return last_full

    for _, row in df.iterrows():
        try:
            wmo = int(row[wmo_col])
        except Exception:
            continue

        raw_day   = "" if pd.isna(row[day_col])   else str(row[day_col]).strip()
        raw_night = "" if pd.isna(row[night_col]) else str(row[night_col]).strip()

        day_full   = _prep(raw_day,   "d", last_day_full)
        night_full = _prep(raw_night, "n", last_night_full)

        if day_full:
            maps_day[wmo] = day_full
            last_day_full = day_full
        if night_full:
            maps_night[wmo] = night_full
            last_night_full = night_full

    return {"day": maps_day, "night": maps_night}


def wmo_to_foreca_code(
    code: int | None,
    is_day: bool,
    pop: int | None = None,
    temp_c: float | None = None,
    cloudcover: int | None = None
) -> str:
    """
    Palauttaa suoraan täyden Foreca-avaimen ('dXXX'/'nXXX') Excel-mappingista.
    Jos koodia ei löydy, käytetään pilvisyys-fallbackia (000/100/… + d/n).
    """
    maps = _load_wmo_foreca_map()

    if code is None:
        key = "d000" if is_day else "n000"
        _trace_map(code, is_day, pop, temp_c, cloudcover, key, "none → clear (default)")
        return key

    c = int(code)
    lookup = maps["day"] if is_day else maps["night"]
    key = lookup.get(c)

    if key:
        _trace_map(c, is_day, pop, temp_c, cloudcover, key, "Excel mapping (päivä/yö, valmis avain)")
        return key

    # Fallback: pilvisyyskartta
    base = _cloud_icon_from_cover(cloudcover, is_day)  # palauttaa esim. 'd200'/'n300'
    _trace_map(c, is_day, pop, temp_c, cloudcover, base, "fallback: cloudcover bucket")
    return base



@st.cache_data(ttl=CACHE_TTL_MED)
def fetch_weather_points(lat: float, lon: float, tz_name: str, offsets=(0,3,6,9,12)):
    url = (
        f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
        f"&hourly=temperature_2m,precipitation_probability,weathercode,cloudcover,is_day"
        f"&timezone={quote(tz_name)}"
    )

    # *** TÄMÄ RIVI ON OLEELLINEN ***
    data = http_get_json(url)

    hourly = data.get("hourly", {}) if isinstance(data, dict) else {}
    times  = hourly.get("time", []) or []
    temps  = hourly.get("temperature_2m", []) or []
    pops   = hourly.get("precipitation_probability", []) or []
    wmos   = hourly.get("weathercode", []) or []
    covers = hourly.get("cloudcover", []) or []
    isday  = hourly.get("is_day", []) or []

    now = dt.datetime.now(TZ).replace(minute=0, second=0, microsecond=0)
    pts = []

    for off in offsets:
        t = now + dt.timedelta(hours=off)
        ts = t.strftime("%Y-%m-%dT%H:00")
        try:
            idx = times.index(ts)
        except ValueError:
            continue

        # turvalliset haut
        temp = temps[idx]  if idx < len(temps)  else None
        pop  = pops[idx]   if idx < len(pops)   else None
        wmo  = wmos[idx]   if idx < len(wmos)   else None
        ccov = covers[idx] if idx < len(covers) else None

        # käytä Open-Meteon is_day:tä jos saatavilla; muuten kellonaika 6–20
        is_day_flag = None
        if idx < len(isday):
            try:
                is_day_flag = bool(int(isday[idx]))
            except Exception:
                is_day_flag = None
        if is_day_flag is None:
            is_day_flag = (6 <= t.hour <= 20)

        pts.append({
            "label": "Nyt" if off == 0 else f"+{off} h",
            "hour": t.hour,
            "temp": temp,
            "pop": pop,
            "key": wmo_to_foreca_code(
                wmo, is_day=is_day_flag, pop=pop, temp_c=temp, cloudcover=ccov
            ),
        })

    # Päivän min/max
    min_t = max_t = None
    try:
        day_str = now.strftime("%Y-%m-%d")
        idxs = [i for i, ts in enumerate(times) if ts.startswith(day_str)]
        vals = [temps[i] for i in idxs if i < len(temps)]
        if vals:
            min_t, max_t = min(vals), max(vals)
    except Exception:
        pass

    return {"points": pts, "min_temp": min_t, "max_temp": max_t}

def wmo_to_icon_key(code: int | None, is_day: bool) -> str:
    # Päivitetty versio, joka tukee weather_icons.py avaimia
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

# --- DEBUG: Sääikonien pikatesti-matriisi ---
from api import wmo_to_foreca_code
from weather_icons import render_foreca_icon

def card_weather_debug_matrix():
    st.markdown("<div class='card-title'>🧪 Sääikonit – pikatesti</div>", unsafe_allow_html=True)

    # 1) Pilvisyyden vaikutus (WMO 0–3): näytetään eri cloudcover-arvoilla
    cloud_rows = []
    for is_day in (True, False):
        row_html = "<div style='display:flex; gap:10px; flex-wrap:wrap; align-items:center;'>"
        row_html += f"<div style='width:110px; opacity:.8;'>{'Päivä' if is_day else 'Yö'} – pilvisyys</div>"
        for cc in (5, 30, 55, 75, 95):
            key = wmo_to_foreca_code(0, is_day=is_day, pop=0, temp_c=10, cloudcover=cc)
            img = render_foreca_icon(key, size=40)
            row_html += f"<div style='display:grid; place-items:center; background:rgba(255,255,255,.06); padding:6px 8px; border-radius:10px; min-width:86px;'>"
            row_html += f"{img}<div style='font-size:.8rem; opacity:.85;'>cc {cc}%<br/><code>{key}</code></div></div>"
        row_html += "</div>"
        cloud_rows.append(row_html)

    # 2) Jatkuva sade (61/63/65): PoP matala vs. korkea + nollakeli (räntä)
    rain_rows = []
    for c in (61, 63, 65):
        row_html = "<div style='display:flex; gap:10px; flex-wrap:wrap; align-items:center;'>"
        row_html += f"<div style='width:110px; opacity:.8;'>WMO {c} – sade</div>"
        cases = [
            ("päivä, PoP 20%", True, 20, 5.0),
            ("päivä, PoP 80%", True, 80, 5.0),
            ("päivä, 0°C (räntä)", True, 80, 0.0),
            ("yö, PoP 80%", False, 80, 5.0),
        ]
        for label, is_day, pop, temp in cases:
            key = wmo_to_foreca_code(c, is_day=is_day, pop=pop, temp_c=temp, cloudcover=70)
            img = render_foreca_icon(key, size=40)
            row_html += f"<div style='display:grid; place-items:center; background:rgba(255,255,255,.06); padding:6px 8px; border-radius:10px; min-width:120px;'>"
            row_html += f"{img}<div style='font-size:.8rem; opacity:.85;'>{label}<br/><code>{key}</code></div></div>"
        row_html += "</div>"
        rain_rows.append(row_html)

    # 3) Kuurot (80/81/82): PoP 20% vs. 80%
    shower_rows = []
    for c in (80, 81, 82):
        row_html = "<div style='display:flex; gap:10px; flex-wrap:wrap; align-items:center;'>"
        row_html += f"<div style='width:110px; opacity:.8;'>WMO {c} – kuurot</div>"
        for pop in (20, 80):
            key = wmo_to_foreca_code(c, is_day=True, pop=pop, temp_c=10, cloudcover=60)
            img = render_foreca_icon(key, size=40)
            row_html += f"<div style='display:grid; place-items:center; background:rgba(255,255,255,.06); padding:6px 8px; border-radius:10px; min-width:120px;'>"
            row_html += f"{img}<div style='font-size:.8rem; opacity:.85;'>päivä, PoP {pop}%<br/><code>{key}</code></div></div>"
        row_html += "</div>"
        shower_rows.append(row_html)

    # 4) Tihku, jäätävä sade, lumi, ukkonen
    misc_cases = [
        ("tihku heikko (51)", 51), ("tihku koht. (53)", 53), ("tihku voim. (55)", 55),
        ("jäätävä tihku (56)", 56), ("jäätävä sade h. (66)", 66), ("jäätävä sade v. (67)", 67),
        ("lumi (71)", 71), ("lumikuuro (85)", 85), ("ukkonen (95)", 95),
    ]
    misc_rows = "<div style='display:flex; gap:10px; flex-wrap:wrap; align-items:center;'>"
    misc_rows += "<div style='width:110px; opacity:.8;'>Muut</div>"
    for label, code in misc_cases:
        key = wmo_to_foreca_code(code, is_day=True, pop=80, temp_c=-2 if code in (71,85) else 2, cloudcover=80)
        img = render_foreca_icon(key, size=40)
        misc_rows += f"<div style='display:grid; place-items:center; background:rgba(255,255,255,.06); padding:6px 8px; border-radius:10px; min-width:130px;'>"
        misc_rows += f"{img}<div style='font-size:.8rem; opacity:.85;'>{label}<br/><code>{key}</code></div></div>"
    misc_rows += "</div>"

    st.markdown(
        "<section class='card' style='min-height:12dvh; padding:10px;'>"
        "<div class='card-body' style='display:flex; flex-direction:column; gap:8px;'>"
        + "".join(cloud_rows)
        + "".join(rain_rows)
        + "".join(shower_rows)
        + misc_rows
        + "</div></section>",
        unsafe_allow_html=True
    )
    
    if st.toggle("Näytä päätösjäljet (trace)", value=False):
        rows = get_map_trace()
        if rows:
            # kevyt HTML-taulukko – ei riippuvuutta pandasista
            head = "<tr><th>WMO</th><th>Päivä</th><th>PoP %</th><th>T °C</th><th>Cloud %</th><th>Key</th><th>Syynys</th></tr>"
            body = "".join(
                f"<tr><td>{r['wmo']}</td><td>{'d' if r['is_day'] else 'n'}</td>"
                f"<td>{r['pop']}</td><td>{r['temp_c']}</td><td>{r['cloudcover']}</td>"
                f"<td><code>{r['key']}</code></td><td>{r['reason']}</td></tr>"
                for r in rows[::-1]  # uusin ensimmäiseksi
            )
            st.markdown(
                f"<div class='card' style='padding:10px; overflow:auto;'>"
                f"<div class='card-title'>Päätösjälki (uusin ensin)</div>"
                f"<table style='width:100%; font-size:.9rem; border-collapse:collapse;'>"
                f"{head}{body}</table></div>",
                unsafe_allow_html=True
            )
        else:
            st.markdown("<div class='hint'>Ei jälkiä vielä.</div>", unsafe_allow_html=True)

# ---- NIMIPÄIVÄT ----
def _resolve_nameday_file() -> Path:
    # Palauta ensimmäinen olemassa oleva polku listalta
    for p in NAMEDAY_PATHS:
        try:
            if p and Path(p).exists():
                return Path(p)
        except Exception:
            continue
    # Jos mikään ei löydy, palauta oletuspolku (voi olla olematon)
    return Path(NAMEDAY_FILE)

@st.cache_data(ttl=CACHE_TTL_LONG)
def fetch_nameday_today(_cache_buster: int | None = None) -> str:
    """
    Palauttaa tämän päivän nimipäivät merkkijonona.
    Tukee kahta skeemaa:
      A) {"10-09": ["Ilona", "…"]}  (tasainen %m-%d → lista/merkkijono)
      B) {"nimipäivät":{"lokakuu":{"9":"Ilona, …"}}}  (kuukausittain)
    """
    try:
        p = _resolve_nameday_file()
        if not p.exists():
            return "—"

        with p.open("r", encoding="utf-8") as f:
            data = json.load(f)

        # Päivän indeksit
        now = dt.datetime.now(TZ)
        key_md = now.strftime("%m-%d")
        day_str = str(now.day)  # esim. "9"
        month_name = [
            "tammikuu","helmikuu","maaliskuu","huhtikuu","toukokuu","kesäkuu",
            "heinäkuu","elokuu","syyskuu","lokakuu","marraskuu","joulukuu"
        ][now.month - 1]

        # --- Skeema A: tasainen "%m-%d"
        if isinstance(data, dict) and key_md in data:
            names = data.get(key_md, [])
            if isinstance(names, list):
                return ", ".join(n.strip() for n in names if str(n).strip()) or "—"
            if isinstance(names, str) and names.strip():
                return names.strip()
            return "—"

        # --- Skeema B: kuukausittain ryhmitelty
        root = data.get("nimipäivät") if isinstance(data, dict) else None
        if isinstance(root, dict):
            month_obj = None
            # joustava: hyväksy avaimet tapaus- ja aksenttieroista välittämättä
            for k, v in root.items():
                if isinstance(k, str) and k.strip().lower() == month_name:
                    month_obj = v
                    break
            if isinstance(month_obj, dict):
                names = month_obj.get(day_str)
                if isinstance(names, list):
                    return ", ".join(n.strip() for n in names if str(n).strip()) or "—"
                if isinstance(names, str) and names.strip():
                    return names.strip()

        # Ei löytynyt
        return "—"

    except Exception as e:
        report_error("nameday: local json", e)
        return "—"

# ---- BITCOIN ----
@st.cache_data(ttl=CACHE_TTL_SHORT)
def fetch_btc_eur():
    # (Sama koodi kuin alkuperäisessä)
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=eur&include_24hr_change=true"
    j = http_get_json(url)
    b = j.get("bitcoin", {})
    return {"price": b.get("eur"), "change": b.get("eur_24h_change")}

@st.cache_data(ttl=CACHE_TTL_MED)
def fetch_btc_last_7d_eur():
    # (Sama koodi kuin alkuperäisessä)
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=eur&days=7"
    j = http_get_json(url)
    prices = j.get("prices", [])
    xs, ys = [], []
    keep_every = max(len(prices) // (24*7), 1)
    for i, (ts, val) in enumerate(prices):
        if i % keep_every == 0:
            xs.append(dt.datetime.fromtimestamp(ts/1000, tz=TZ))
            ys.append(float(val))
    return list(zip(xs, ys))

@st.cache_data(ttl=CACHE_TTL_LONG)
def fetch_btc_ath_eur():
    try:
        url = "https://api.coingecko.com/api/v3/coins/bitcoin"
        j = http_get_json(url)
        ath = j.get("market_data", {}).get("ath", {}).get("eur")
        ath_date = j.get("market_data", {}).get("ath_date", {}).get("eur")
        if ath:
            try:
                ATH_CACHE_FILE.write_text(json.dumps({"ath_eur": float(ath), "ath_date": ath_date}), encoding="utf-8")
            except Exception as e:
                report_error("btc_ath: write cache", e)
            return float(ath), str(ath_date)
    except requests.HTTPError as e:
        try:
            j = json.loads(ATH_CACHE_FILE.read_text(encoding="utf-8"))
            return float(j.get("ath_eur")), str(j.get("ath_date"))
        except Exception as e2:
            report_error("btc_ath: read cache on 429", e2)
    except Exception as e:
        report_error("btc_ath: network", e)
        try:
            j = json.loads(ATH_CACHE_FILE.read_text(encoding="utf-8"))
            return float(j.get("ath_eur")), str(j.get("ath_date"))
        except Exception as e2:
            report_error("btc_ath: read local cache", e2)
    return None, None

