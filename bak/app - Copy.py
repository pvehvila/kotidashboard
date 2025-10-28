# =============================================================================
# 1) METATIEDOT & ASETUKSET
# =============================================================================
# -*- coding: utf-8 -*-
import json, base64, socket
import datetime as dt
from pathlib import Path
from urllib.parse import quote
from zoneinfo import ZoneInfo

import requests
import streamlit as st
# Autorefresh optional: käytä streamlit_extras jos saatavilla, muuten kevyt JS-fallback
try:
    from streamlit_extras.st_autorefresh import st_autorefresh
except Exception:
    def st_autorefresh(interval=None, key=None, **_):
        if interval:
            st.markdown(
                f"<script>setTimeout(() => window.location.reload(), {int(interval)});</script>",
                unsafe_allow_html=True,
            )

import plotly.graph_objects as go

# =============================================================================
# 1) VAKIOT (aikavyöhyke, sääikonit, sähkön värikynnykset, kutsuajat ja cachet, graafien yläpalkki, polku, paikallistiedostot, geolokaatio)
# =============================================================================
from weather_icons import WX_SVGS
from config import TZ, PRICE_LOW_THR, PRICE_HIGH_THR, HTTP_TIMEOUT_S, CACHE_TTL_SHORT, CACHE_TTL_MED, CACHE_TTL_LONG, PLOTLY_CONFIG, DEV, HERE, ATH_CACHE_FILE, NAMEDAY_FILE, LAT, LON 

# =============================================================================
# 2) YLEISET APURIT (ei verkkoa)
# =============================================================================
from utils import report_error, _color_by_thresholds, _color_for_value, get_ip

# =============================================================================
# 3) UI-APURIT (Streamlit/HTML/CSS)
# =============================================================================
def load_css(file_name: str):
    p = HERE / file_name
    if not p.exists():
        return
    try:
        with p.open("r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except Exception as e:
        report_error("load_css", e)

def section_title(html: str, mt: int = 10, mb: int = 4):
    st.markdown(f"<div style='margin:{mt}px 0 {mb}px 0'>{html}</div>", unsafe_allow_html=True)

def card(title: str, body_html: str, height_dvh: int = 16):
    st.markdown(
        f"""
        <section class="card" style="min-height:{height_dvh}dvh; position:relative; overflow:hidden;">
          <div class="card-title">{title}</div>
          <div class="card-body">{body_html}</div>
        </section>
        """,
        unsafe_allow_html=True,
    )

# =============================================================================
# 4) VERKKOAPURIT & VÄLIMUISTI
# =============================================================================
def http_get_json(url: str, timeout: float = HTTP_TIMEOUT_S):
    r = requests.get(url, timeout=timeout)
    r.raise_for_status()
    return r.json()

# ---- BTC ATH ----
def fetch_btc_ath_eur():
    if ATH_CACHE_FILE.exists():
        stat = ATH_CACHE_FILE.stat()
        cache_age = dt.datetime.now().timestamp() - stat.st_mtime
        if cache_age < 7 * 24 * 3600:  # 7 päivää
            try:
                j = json.loads(ATH_CACHE_FILE.read_text(encoding="utf-8"))
                return float(j["ath_eur"]), str(j["ath_date"])
            except Exception:
                pass

# ---- SÄHKÖHINNAT ----
def _parse_hour_from_item(item: dict, idx: int, date_ymd: dt.date) -> int | None:
    # 1) suora hour-kenttä
    for k in ("hour", "Hour", "H"):
        v = item.get(k)
        if v is not None:
            try:
                h = int(v)
                if 0 <= h <= 23:
                    return h
            except Exception:
                pass
    # 2) aikaleimasta
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
    # 3) fallback: käytä listan indeksiä jos näyttää päivän tunneilta
    if 0 <= idx <= 23:
        return idx
    return None

def _parse_cents_from_item(item: dict) -> float | None:
    # Salli sekä snt/kWh että €/kWh (alle 1.0 tulkitaan €/kWh → *100)
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
    out_map = {}  # hour -> cents
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
    url = f"https://www.sahkonhintatanaan.fi/api/v1/prices/{date_ymd:%Y}/{date_ymd:%m-%d}.json"
    data = http_get_json(url)
    items = data.get("prices") if isinstance(data, dict) else data
    if not isinstance(items, list):
        items = []
    return _normalize_prices_list(items, date_ymd)

def _fetch_from_porssisahko(date_ymd: dt.date):
    # Tunnettu avoin API. Palauttaa tyypillisesti { prices: [ { startDate: ISO, EUR_per_kWh: float }, ... ] }
    url = f"https://api.porssisahko.net/v1/price.json?date={date_ymd:%Y-%m-%d}"
    data = http_get_json(url)
    items = data.get("prices") if isinstance(data, dict) else data
    if not isinstance(items, list):
        items = []
    return _normalize_prices_list(items, date_ymd)

def fetch_prices_for(date_ymd: dt.date):
    """Hae sähkön tuntihinnat (snt/kWh) annetulle päivälle. Useampi lähde + normalisointi."""
    # 1) sahkonhintatanaan.fi
    try:
        res = _fetch_from_sahkonhintatanaan(date_ymd)
        if res:
            return res
    except requests.HTTPError as e:
        if not (e.response is not None and e.response.status_code == 404):
            report_error(f"prices: sahkonhintatanaan {date_ymd.isoformat()}", e)
    except Exception as e:
        report_error(f"prices: sahkonhintatanaan {date_ymd.isoformat()}", e)

    # 2) fallback: api.porssisahko.net
    try:
        res = _fetch_from_porssisahko(date_ymd)
        if res:
            return res
    except requests.HTTPError as e:
        if not (e.response is not None and e.response.status_code == 404):
            report_error(f"prices: porssisahko {date_ymd.isoformat()}", e)
    except Exception as e:
        report_error(f"prices: porssisahko {date_ymd.isoformat()}", e)

    # Ei dataa kummastakaan
    return []

@st.cache_data(ttl=CACHE_TTL_MED)
def try_fetch_prices(date_ymd: dt.date):
    """Kääre: 404 huomiselle ei ole virhe vaan 'ei vielä dataa'."""
    try:
        return fetch_prices_for(date_ymd)
    except requests.HTTPError as e:
        if e.response is not None and e.response.status_code == 404:
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
    try:
        data = http_get_json("https://zenquotes.io/api/today", timeout=HTTP_TIMEOUT_S)
        if isinstance(data, list) and data:
            q = data[0]
            return {"text": q.get("q", ""), "author": q.get("a", ""), "source": "zenquotes"}
    except Exception as e:
        report_error("zen: zenquotes-today", e)
    return None

def _from_quotable() -> dict | None:
    try:
        data = http_get_json("https://api.quotable.io/random?tags=wisdom|life|inspirational", timeout=HTTP_TIMEOUT_S)
        return {"text": data.get("content", ""), "author": data.get("author", ""), "source": "quotable"}
    except Exception as e:
        report_error("zen: quotable", e)
    return None

@st.cache_data(ttl=CACHE_TTL_LONG)
def fetch_daily_quote(day_iso: str) -> dict:
    """Päivän lainaus (cache): ZenQuotes → Quotable → paikallisfallback."""
    q = _from_zenquotes()
    if not q:
        q = _from_quotable()
    if not q:
        i = (sum(map(ord, day_iso)) % len(LOCAL_ZEN))
        q = dict(LOCAL_ZEN[i])
        q["source"] = "local"
    return q

# ---- SÄÄ (Open-Meteo) ----
@st.cache_data(ttl=CACHE_TTL_MED)
def fetch_weather_points(lat: float, lon: float, tz_name: str, offsets=(0,3,6,9,12)):
    """
    Hae sääennusteen pisteet seuraaville tunneille.
    Palauttaa: {"points": [...], "min_temp": float|None, "max_temp": float|None}
    """
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&hourly=temperature_2m,precipitation_probability,weathercode"
        f"&timezone={quote(tz_name)}"
    )
    data = http_get_json(url)
    hourly = data.get("hourly", {})
    times = hourly.get("time", [])
    temps = hourly.get("temperature_2m", [])
    pops  = hourly.get("precipitation_probability", [])
    wmos  = hourly.get("weathercode", [])

    now = dt.datetime.now(TZ).replace(minute=0, second=0, microsecond=0)
    pts = []
    for off in offsets:
        t = now + dt.timedelta(hours=off)
        # Etsi lähin tunnin indeksi
        try:
            idx = times.index(t.strftime("%Y-%m-%dT%H:00"))
        except ValueError:
            continue
        temp = temps[idx] if idx < len(temps) else None
        pop  = pops[idx]  if idx < len(pops)  else None
        wmo  = wmos[idx]  if idx < len(wmos)  else None
        pts.append({
            "label": "Nyt" if off == 0 else f"+{off} h",
            "hour": t.hour,
            "temp": temp,
            "pop": pop,
            "key": wmo_to_icon_key(wmo, is_day=(6 <= t.hour <= 20))
        })

    # Päivän min/max (nykyhetken päivästä)
    min_t = max_t = None
    try:
        # suodata saman päivän tunnit
        day_str = now.strftime("%Y-%m-%d")
        idxs = [i for i, ts in enumerate(times) if ts.startswith(day_str)]
        vals = [temps[i] for i in idxs if i < len(temps)]
        if vals:
            min_t, max_t = min(vals), max(vals)
    except Exception:
        pass

    return {"points": pts, "min_temp": min_t, "max_temp": max_t}

# ---- NIMIPÄIVÄT (paikallinen json → fallback tyhjä) ----
@st.cache_data(ttl=CACHE_TTL_LONG)
def fetch_nameday_today() -> str:
    """Palauta tämän päivän nimipäivät (FI) paikallisesta JSONista."""
    try:
        if NAMEDAY_FILE.exists():
            with NAMEDAY_FILE.open("r", encoding="utf-8") as f:
                data = json.load(f)
            today = dt.datetime.now(TZ).strftime("%m-%d")
            names = data.get(today, [])
            if isinstance(names, list):
                return ", ".join(names)
            if isinstance(names, str):
                return names
    except Exception as e:
        report_error("nameday: local json", e)
    return "—"

# ---- BITCOIN ----
@st.cache_data(ttl=CACHE_TTL_SHORT)
def fetch_btc_eur():
    """Nykykurssi ja 24h muutos CoinGeckosta."""
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=eur&include_24hr_change=true"
    j = http_get_json(url)
    b = j.get("bitcoin", {})
    return {"price": b.get("eur"), "change": b.get("eur_24h_change")}

@st.cache_data(ttl=CACHE_TTL_MED)
def fetch_btc_last_7d_eur():
    """Viimeiset 7 päivää / 5 min välein → yksinkertaistetaan 1h välein näyttöön."""
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=eur&days=7"
    j = http_get_json(url)
    prices = j.get("prices", [])
    xs, ys = [], []
    keep_every = max(len(prices) // (24*7), 1)  # ~1h
    for i, (ts, val) in enumerate(prices):
        if i % keep_every == 0:
            xs.append(dt.datetime.fromtimestamp(ts/1000, tz=TZ))
            ys.append(float(val))
    return list(zip(xs, ys))

@st.cache_data(ttl=CACHE_TTL_LONG)
def fetch_btc_ath_eur():
    """ATH + pvm CoinGeckosta, varmuuskopio paikalliseen tiedostoon."""
    try:
        url = "https://api.coingecko.com/api/v3/coins/bitcoin"
        j = http_get_json(url)
        ath = j.get("market_data", {}).get("ath", {}).get("eur")
        ath_date = j.get("market_data", {}).get("ath_date", {}).get("eur")
        if ath:
            # tallenna cacheen
            try:
                ATH_CACHE_FILE.write_text(json.dumps({"ath_eur": float(ath), "ath_date": ath_date}), encoding="utf-8")
            except Exception as e:
                report_error("btc_ath: write cache", e)
            return float(ath), str(ath_date)
    except requests.HTTPError as e:
        # 429 tms. → yritä lukea paikallinen cache
        try:
            j = json.loads(ATH_CACHE_FILE.read_text(encoding="utf-8"))
            return float(j.get("ath_eur")), str(j.get("ath_date"))
        except Exception as e2:
            report_error("btc_ath: read cache on 429", e2)
    except Exception as e:
        report_error("btc_ath: network", e)
        # viimeinen oljenkorsi: paikallinen
        try:
            j = json.loads(ATH_CACHE_FILE.read_text(encoding="utf-8"))
            return float(j.get("ath_eur")), str(j.get("ath_date"))
        except Exception as e2:
            report_error("btc_ath: read local cache", e2)
    return None, None

# =============================================================================
# 5) DOMAIN-APURIT (muotoilu/renderointi)
# =============================================================================
def _next_12h_df(prices_today, prices_tomorrow, now_dt: dt.datetime):
    """List[dict]: {ts, hour_label, cents, is_now} seuraaville 12 tunnille."""
    rows = []
    base = now_dt.replace(minute=0, second=0, microsecond=0)
    for i in range(12):
        t = base + dt.timedelta(hours=i)
        src = prices_today if (src_date := t.date()) == now_dt.date() else prices_tomorrow
        if not src:
            continue
        item = next((p for p in src if p["hour"] == t.hour), None)
        if not item:
            continue
        rows.append({
            "ts": t,
            "hour_label": t.strftime("%H") + ":00",
            "cents": float(item["cents"]),
            "is_now": (i == 0),
        })
    return rows

# Yhdistetty WMO→ikoni-avain
def wmo_to_icon_key(code: int | None, is_day: bool) -> str:
    if code is None:
        return "na"
    if code == 0:
        return "clear-day" if is_day else "clear-night"
    if code in (1, 2):
        return "partly-cloudy-day" if is_day else "partly-cloudy-night"
    if code in (3, 45, 48):
        return "cloudy"
    if code in (51, 53, 55, 56, 57):
        return "drizzle"
    if code in (61, 63, 65, 80, 81, 82):
        return "rain"
    if code in (71, 73, 75, 85, 86):
        return "snow"
    if code in (95, 96, 99):
        return "thunderstorm"
    return "na"

def svg_icon_markup(key: str, color_hex: str = "#e7eaee") -> str:
    svg = WX_SVGS.get(key, WX_SVGS["na"])
    return svg.replace("currentColor", color_hex)

# =============================================================================
# 6) ALUSTUS (PAGE CONFIG, CSS, AUTOREFRESH)
# =============================================================================
st.set_page_config(page_title="Kotidashboard", layout="wide", page_icon="🏠")
load_css("style.css")
# Päivitä minuutin välein (voit muuttaa/poistaa)
st_autorefresh(interval=60_000, key="refresh")

# =============================================================================
# 7) KORTIT (ylhäältä alas)
# =============================================================================
def card_nameday():
    try:
        names = fetch_nameday_today()  # välimuistissa
        now_dt = dt.datetime.now(TZ)
        WEEKDAYS_FI = ["maanantaina","tiistaina","keskiviikkona","torstaina","perjantaina","lauantaina","sunnuntaina"]
        weekday_fi = WEEKDAYS_FI[now_dt.weekday()]
        date_str = f"{now_dt.day}.{now_dt.month}."
        title_text = f"Nimipäivät<br>{weekday_fi} {date_str}"

        BG_DATAURL = None
        for fname in ("butterfly-bg.png","butterfly-bg.webp","butterfly-bg.jpg"):
            p = HERE / fname
            if p.exists():
                b = p.read_bytes()
                ext = p.suffix.lower()
                mime = "image/png" if ext==".png" else ("image/webp" if ext==".webp" else "image/jpeg")
                BG_DATAURL = f"data:{mime};base64," + base64.b64encode(b).decode("ascii")
                break

        overlay = "linear-gradient(90deg, rgba(11,15,20,0.65) 0%, rgba(11,15,20,0.25) 45%, rgba(11,15,20,0.00) 70%)"
        html = f"""
        <section class="card" style="min-height:12dvh; position:relative; overflow:hidden;">
          <div class="card-title" style="position:relative; z-index:2;">{title_text}</div>
          <div class="card-body" style="display:flex; justify-content:flex-start; align-items:center; text-align:left; flex:1; position:relative; z-index:2;">
            <div style="font-size:1.35rem; font-weight:800; margin:0 0 6px 0;">{names}</div>
          </div>
          {'<div style="position:absolute; inset:0; background-image:url('+BG_DATAURL+'); background-repeat:no-repeat; background-size:contain; background-position:100% center; background-size:100%; pointer-events:none; filter: blur(0.4px) drop-shadow(0 6px 16px rgba(0,0,0,.45)); opacity:0.9; z-index:0;"></div>' if BG_DATAURL else ''}
          <div style="position:absolute; inset:0; background:{overlay}; pointer-events:none; z-index:1;"></div>
        </section>
        """
        st.markdown(html, unsafe_allow_html=True)

    except Exception as e:
        card("Nimipäivät", f"<span class='hint'>Ei saatu tietoa: {e}</span>", height_dvh=12)

def card_zen():
    try:
        today_iso = dt.datetime.now(TZ).date().isoformat()
        q = fetch_daily_quote(today_iso)  # {text, author, source}
        q_text = (q.get("text") or "").strip()
        q_author = (q.get("author") or "").strip()

        ZEN_BG_DATAURL = None
        try:
            img_path = HERE / "zen-bg.png"
            if img_path.exists():
                with img_path.open("rb") as f:
                    ZEN_BG_DATAURL = "data:image/png;base64," + base64.b64encode(f.read()).decode("ascii")
        except Exception as e:
            report_error("zen: load bg", e)

        overlay = "linear-gradient(rgba(11,15,20,0.55), rgba(11,15,20,0.55))"
        bg_layer = f"{overlay}, url('{ZEN_BG_DATAURL}')" if ZEN_BG_DATAURL else overlay

        zen_html = f"""
        <section class="card" style="
          min-height:12dvh; position:relative; overflow:hidden;
          background-image:{bg_layer}; background-size:cover; background-position:center;">
          <div class="card-title">Päivän zen</div>
          <div class="card-body" style="display:flex; justify-content:center; align-items:center; text-align:center; flex:1;">
            <div style="margin:0; line-height:1.35;">
              <em>“{q_text}”</em>{(' — ' + q_author) if q_author else ''}
            </div>
          </div>
        </section>
        """
        st.markdown(zen_html, unsafe_allow_html=True)

    except Exception as e:
        card("Päivän zen", f"<span class='hint'>Ei saatu tietoa: {e}</span>", height_dvh=12)

def card_weather():
    from streamlit.components.v1 import html as st_html

    try:
        weather_data = fetch_weather_points(LAT, LON, "Europe/Helsinki", offsets=(0,3,6,9,12))
        pts = weather_data["points"]
        min_temp = weather_data["min_temp"]
        max_temp = weather_data["max_temp"]

        title = "Sää — Riihimäki"
        if (min_temp is not None) and (max_temp is not None):
            title += f"&nbsp; | &nbsp; Tänään: {round(min_temp)}°C — {round(max_temp)}°C"

        st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
        section_title(title, mb=3)

        def cell(p):
            svg_html = svg_icon_markup(p["key"], "#e7eaee")
            t = "—" if p["temp"] is None else f"{round(p['temp'])}"
            pop = "—" if p["pop"] is None else f"{p['pop']}%"
            return f"""
            <div class="weather-cell">
              <div class="label">{p['label']}</div>
              <div class="sub">{p['hour']}:00</div>
              <div class="icon" style="width:48px; height:48px;">{svg_html}</div>
              <div class="temp">{t}°C</div>
              <div class="pop">Sade {pop}</div>
            </div>
            """

        inner_html = f"""
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<style>
  :root {{
    --fg: #e7eaee;
    --bg2: rgba(255,255,255,0.06);
  }}
  html, body {{
    margin:0; padding:0; background:transparent; color:var(--fg);
    font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, Noto Sans, Helvetica Neue, Arial, Apple Color Emoji, Segoe UI Emoji;
  }}
  .weather-card {{ padding: 8px 12px 6px; }}
  .weather-row {{
    display: grid; grid-template-columns: repeat(5, minmax(88px, 1fr));
    gap: 10px; align-items: stretch;
  }}
  .weather-cell {{
    display: grid; grid-template-rows: auto auto 1fr auto auto;
    align-items: center; justify-items: center;
    background: var(--bg2); border-radius: 14px; padding: 6px 6px; min-height: 110px;
  }}
  .label {{ font-size:.9rem; opacity:.9; margin:2px 0 0; }}
  .sub {{ font-size:.8rem; opacity:.75; margin:0 0 4px; }}
  .icon svg {{ width:48px; height:48px; display:block; }}
  .temp {{ font-size:1.1rem; margin-top:6px; }}
  .pop {{ font-size:.85rem; opacity:.85; margin-top:2px; }}
</style>
</head>
<body>
<div class="weather-card"><div class="weather-row">
  {''.join(cell(p) for p in pts)}
</div></div>
</body>
</html>
        """
        st_html(inner_html, height=155, scrolling=False)

    except Exception as e:
        report_error("weather card", e)
        card("Sää — Riihimäki", f"<span class='hint'>Ei saatu säätietoa: {e}</span>", height_dvh=15)

def card_prices():
    try:
        today = dt.datetime.now(TZ).date()
        tomorrow = today + dt.timedelta(days=1)
        prices_today = try_fetch_prices(today)
        prices_tomorrow = try_fetch_prices(tomorrow)  # voi olla None ennen julkaisua

        # Otsikko + nykyinen tuntihinta "badgella"
        current_cents = None
        if prices_today:
            now_h = dt.datetime.now(TZ).hour
            hit = next((p for p in prices_today if p["hour"] == now_h), None)
            if hit:
                current_cents = float(hit["cents"])

        title_html = "Pörssisähkö – seuraavat 12 h"
        if current_cents is not None:
            badge_bg = _color_for_value(current_cents)
            title_html = (
                "Pörssisähkö – nykyinen tuntihinta: "
                f"<span class='price-badge' style='background:{badge_bg};"
                "color:#000; padding:2px 8px; border-radius:8px; font-weight:600'>"
                f"{current_cents:.2f} snt/kWh</span>"
            )

        section_title(title_html, mt=10, mb=4)

        # 12 h pylväs
        df12 = _next_12h_df(prices_today, prices_tomorrow, now_dt=dt.datetime.now(TZ))

        if not df12:
            card("Pörssisähkö", "<span class='hint'>Ei dataa vielä seuraaville tunneille</span>", height_dvh=16)
            return

        vals = [row["cents"] for row in df12]
        cols = _color_by_thresholds(vals)

        line_colors = ["rgba(255,255,255,0.9)" if row["is_now"] else "rgba(0,0,0,0)" for row in df12]
        line_widths = [1.5 if row["is_now"] else 0 for row in df12]

        fig = go.Figure([
            go.Bar(
                x=[row["hour_label"] for row in df12],
                y=[round(v, 2) for v in vals],
                marker=dict(color=cols, line=dict(color=line_colors, width=line_widths)),
                hovertemplate="<b>%{x}</b><br>%{y} snt/kWh<extra></extra>",
            )
        ])

        fig.update_layout(
            title=None, title_x=0, title_font_size=14,
            margin=dict(l=10, r=10, t=24, b=44),
            xaxis_title=None, yaxis_title="snt/kWh",
            height=190,
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(gridcolor="rgba(255,255,255,0.08)"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.08)"),
        )

        st.plotly_chart(fig, use_container_width=True, theme=None, config=PLOTLY_CONFIG)

        st.markdown("""
<div class='hint' style='margin-top:0px; margin-bottom:2px;'>
  <span style='color:#00b400;'>&#9632;</span> ≤ 5 snt &nbsp;
  <span style='color:#cccc00;'>&#9632;</span> 5–15 snt &nbsp;
  <span style='color:#dc0000;'>&#9632;</span> ≥ 15 snt &nbsp;
  (vihreä = halpa, punainen = kallis)
</div>
""", unsafe_allow_html=True)

    except Exception as e:
        section_title("Pörssisähkö – seuraavat 12 h")
        st.markdown(f"<span class='hint'>Virhe hinnanhaussa: {e}</span>", unsafe_allow_html=True)

def card_bitcoin():
    try:
        btc_data = fetch_btc_eur()
        eur_now = btc_data.get("price")
        change_24h = btc_data.get("change")
        if eur_now is None:
            raise ValueError("Bitcoin-hinnan nouto CoinGeckosta epäonnistui.")

        eur_now_fmt = f"{eur_now:,.0f}".replace(",", " ")
        title_html = f"Bitcoin - viimeiset 7 päivää. Arvo nyt: {eur_now_fmt} €"
        if change_24h is not None:
            color = "#4ade80" if change_24h >= 0 else "#f87171"
            sign = "+" if change_24h >= 0 else ""
            change_fmt = f"{sign}{change_24h:.2f}%"
            title_html += f' <span style="font-size: 1.1rem; color: {color};">{change_fmt} (24h)</span>'
        section_title(title_html)

        series = fetch_btc_last_7d_eur()
        ath_eur, ath_date = fetch_btc_ath_eur()
        xs = [t for t, _ in series]
        ys = [v for _, v in series]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=xs, y=ys, mode="lines", name="BTC/EUR (7 d)",
            hovertemplate="%{x|%d.%m %H:%M} — %{y:.0f} €<extra></extra>",
        ))
        if ath_eur:
            fig.add_trace(go.Scatter(
                x=[xs[0] if xs else dt.datetime.now(TZ), xs[-1] if xs else dt.datetime.now(TZ)],
                y=[ath_eur, ath_eur], mode="lines",
                name=f"ATH {ath_eur:,.0f} €", line=dict(dash="dot"),
                hovertemplate="ATH — %{y:.0f} € (%{x|%d.%m})<extra></extra>",
            ))

        if ys:
            base_low = eur_now - 5000
            base_high = max(max(ys), ath_eur or eur_now) + 5000
            y_min = int((base_low // 5000) * 5000)
            y_max = int(((base_high + 4999) // 5000) * 5000)
        else:
            y_min, y_max = 0, None

        if xs and ys:
            label_text = f"{ys[-1]:,.0f}".replace(",", " ") + " €"
            fig.add_annotation(
                x=xs[-1], y=ys[-1], xref="x", yref="y",
                text=label_text, showarrow=False,
                xanchor="right", align="right", xshift=-12,
                font=dict(color="#e7eaee", size=12)
            )

        fig.update_layout(
            margin=dict(l=64, r=12, t=8, b=32),
            height=210,
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            showlegend=False, font=dict(size=12, color="#e7eaee"),
            xaxis=dict(type="date", title=None, gridcolor="rgba(255,255,255,0.28)",
                       tickformat="%d.%m", dtick="D1", tickfont=dict(size=11, color="#cfd3d8"), automargin=True),
            yaxis=dict(title="€", gridcolor="rgba(255,255,255,0.28)", tickfont=dict(size=11, color="#cfd3d8"),
                       tickformat="~s", range=[y_min, y_max], fixedrange=True, automargin=True),
            hoverlabel=dict(font_size=11)
        )

        st.plotly_chart(fig, use_container_width=True, theme=None, config=PLOTLY_CONFIG)
        st.markdown(
            "<div class='hint' style='margin-top:4px;'>Näytetään viimeiset 7 päivää (CoinGecko), katkoviiva = ATH{}</div>".format(
                f" ({ath_date[:10]})" if ath_date else ""
            ),
            unsafe_allow_html=True
        )
        st.markdown("<div style='margin-top:6px;'></div>", unsafe_allow_html=True)

    except Exception as e:
        card("Bitcoin (EUR)", f"<span class='hint'>Virhe: {e}</span>", height_dvh=18)

def card_system():
    sys_html = f"""
    <div style="display:grid; grid-template-columns:auto 1fr; gap:6px 12px;">
      <div class="hint">IP:</div><div>{get_ip()}</div>
      <div class="hint">Päivitetty:</div><div>{dt.datetime.now(TZ):%H:%M:%S}</div>
      <div class="hint">Kioskitila:</div><div>Fully Kiosk Browser</div>
    </div>
    """
    card("Järjestelmätila", sys_html, height_dvh=10)

# =============================================================================
# 8) MAIN / LAYOUT
# =============================================================================
def main():
    # Rivi 1: Nimipäivät + Zen
    col1, col2 = st.columns(2, gap="small")
    with col1: card_nameday()
    with col2: card_zen()

    # Rivi 2: Sää
    card_weather()

    # Rivi 3: Pörssisähkö
    card_prices()

    # Rivi 4: Bitcoin
    card_bitcoin()

    # Rivi 5: Järjestelmätila
    card_system()

if __name__ == "__main__":
    main()