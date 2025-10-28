# app.py — Lenovo M9 kioskiulkoasu (tumma, fixed layout, no scroll)

import os, json, datetime, random
import requests
import pandas as pd
import plotly.graph_objects as go
import socket, datetime as dt, zoneinfo, requests
import streamlit as st
from streamlit_autorefresh import st_autorefresh
from pathlib import Path
import urllib.parse  # <-- lisää
import math
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
import base64

# ... (Muu koodi pysyy samana, kuten section_title, TZ, LAT, LON, PORT, st.set_page_config, st_autorefresh) ...

def section_title(title: str, mt: int = 0, mb: int = 6):
    st.markdown(
        f"<div class='card-title' style='margin:{mt}px 0 {mb}px 0;'>{title}</div>",
        unsafe_allow_html=True,
    )


# ---- ASETUKSET ----
TZ = zoneinfo.ZoneInfo("Europe/Helsinki")
LAT, LON = 60.73769, 24.77726   # Riihimäki
PORT = 8787

st.set_page_config(page_title="Kotidashboard", layout="wide", initial_sidebar_state="collapsed")
st_autorefresh(interval=60 * 1000, key="refresh")  # automaattipäivitys 60 s

# app.py (lisäys)

def _svg_data_uri(svg: str, color_hex: str = "#e7eaee") -> str:
    """Korvaa currentColor halutulla värillä ja palauta data-URI."""
    svg_colored = svg.replace("currentColor", color_hex)
    return "data:image/svg+xml;utf8," + urllib.parse.quote(svg_colored)

def _wmo_to_icon(code: int, is_day: bool) -> str:
    """Palauttaa ikonitunnisteen (luokan tai nimen) WMO-koodin perusteella."""
    # Perusmäppäys; voit laajentaa tarvittaessa.
    day = is_day
    mapping = {
        0:  "clear-day" if day else "clear-night",
        1:  "mainly-clear-day" if day else "mainly-clear-night",
        2:  "partly-cloudy-day" if day else "partly-cloudy-night",
        3:  "cloudy",
        45: "fog",
        48: "fog",
        51: "drizzle",
        53: "drizzle",
        55: "drizzle",
        56: "freezing-drizzle",
        57: "freezing-drizzle",
        61: "rain",
        63: "rain",
        65: "rain",
        66: "freezing-rain",
        67: "freezing-rain",
        71: "snow",
        73: "snow",
        75: "snow",
        77: "snow-grains",
        80: "rain-showers",
        81: "rain-showers",
        82: "rain-showers",
        85: "snow-showers",
        86: "snow-showers",
        95: "thunderstorm",
        96: "thunderstorm-hail",
        99: "thunderstorm-hail",
    }
    return mapping.get(code, "na")

# ---- APUMETODIT ----
def get_ip():
    try:
        return socket.gethostbyname(socket.gethostname())
    except Exception:
        return "localhost"

def pct_bar(label: str, value: float, unit: str = "", hint: str = ""):
    v = max(0, min(100, value))
    return f"""
    <div class="bar">
      <div class="bar-head"><span>{label}</span><span>{v:.0f}{unit}</span></div>
      <div class="bar-rail"><div class="bar-fill" style="width:{v}%"></div></div>
      {'<div class="bar-hint">'+hint+'</div>' if hint else ''}
    </div>
    """

def price_chip(cents: float):
    if cents < 5:   cls = "green"
    elif cents < 9: cls = "yellow"
    elif cents < 14:cls = "orange"
    else:           cls = "red"
    return f'<span class="chip {cls}">{cents:.2f} snt/kWh</span>'
    
    # --- Heatmap-apurit (lisää heti price_chipin jälkeen) ---
def _stats(prices_list):
    if not prices_list:
        return None, None, None
    avg = sum(p['cents'] for p in prices_list) / len(prices_list)
    lo = min(prices_list, key=lambda x: x['cents'])
    hi = max(prices_list, key=lambda x: x['cents'])
    return avg, lo, hi

def _heat_color(value, vmin, vmax):
    # vihreä (halpa) -> punainen (kallis)
    if vmin is None or vmax is None or vmax <= vmin:
        return "background:#444;"
    t = (value - vmin) / (vmax - vmin)
    hue = 140 * (1 - max(0, min(1, t)))   # 140→0
    return f"background:hsl({hue:.0f},70%,45%);"

def _heatmap(prices, vmin, vmax, now_hour=None):
    """12x2 (0–11, 12–23) ruudukko."""
    by_hour = {p['hour']: p['cents'] for p in prices} if prices else {}
    rows = []
    for row_start in (0, 12):
        cells = []
        for h in range(row_start, row_start + 12):
            if h in by_hour:
                style = _heat_color(by_hour[h], vmin, vmax)
                outline = "outline:1px solid rgba(255,255,255,.8);" if (now_hour is not None and h == now_hour) else ""
                cells.append(f'<div class="c" title="{h:02d}:00 · {by_hour[h]:.2f} snt/kWh" style="{style}{outline}"></div>')
            else:
                cells.append('<div class="c" style="background:#242a33;"></div>')
        rows.append("".join(cells))
    return f'<div class="hm">{rows[0]}{rows[1]}</div>'

def _next_12h_df(prices_today, prices_tomorrow, now_dt: dt.datetime) -> pd.DataFrame:
    """Muodosta DataFrame seuraavista 12 tunnista:
       kolumnit: ts(datetime), hour_label('HH:00'), cents(float), is_now(bool)
    """
    rows = []
    for i in range(12):
        t = now_dt.replace(minute=0, second=0, microsecond=0) + dt.timedelta(hours=i)
        src = prices_today if t.date() == now_dt.date() else prices_tomorrow
        if not src:
            continue
        # etsi kyseisen päivän listasta oikea tunti
        item = next((p for p in src if p["hour"] == t.hour), None)
        if not item:
            continue
        rows.append({
            "ts": t,
            "hour_label": t.strftime("%H") + ":00",
            "cents": float(item["cents"]),
            "is_now": (i == 0)
        })
    return pd.DataFrame(rows)

def _color_by_thresholds(values, low_thr=5.0, high_thr=15.0):
    """
    Palauttaa värilistan arvoille kiinteillä rajoilla:
      ≤ low_thr  -> vihreä
      > low_thr & < high_thr -> keltainen
      ≥ high_thr -> punainen
    """
    cols = []
    for v in values:
        try:
            val = float(v)
        except Exception:
            cols.append("rgb(128,128,128)")
            continue

        if val <= low_thr:
            cols.append("rgb(0,180,0)")          # vihreä
        elif val >= high_thr:
            cols.append("rgb(220,0,0)")          # punainen
        else:
            # väliin liukuva keltainen (vihreä→punainen)
            ratio = (val - low_thr) / (high_thr - low_thr)
            r = int(0 + ratio * (220 - 0))
            g = int(180 - ratio * (180 - 180 * 0.3))
            cols.append(f"rgb({r},{g},0)")
    return cols

@st.cache_data(ttl=300)
def try_fetch_prices(date_ymd: dt.date):
    try:
        return fetch_prices_for(date_ymd)
    except Exception:
        return None

def card(title: str, body_html: str, height_dvh: float):
    st.markdown(
        f"""
<section class="card" style="min-height:{height_dvh}dvh">
  <div class="card-title">{title}</div>
  <div class="card-body">{body_html}</div>
</section>
""",
        unsafe_allow_html=True,
    )

# ... (TYYLIT osio pysyy samana) ...

st.markdown("""
<style>
/* Piilota Streamlitin header/toolbar/decoration ja koodilohkot */
header, div[data-testid="stDecoration"], div[data-testid="stToolbar"] { display:none !important; }
pre, code, kbd, samp { display:none !important; }

/* Perustausta ja mitoitus mobiilin dynaamisella viewport-korkeudella */
html, body, [data-testid="stAppViewContainer"] {
  margin:0 !important; padding:0 !important; height:100dvh !important;
  background:#0b0f14; color:#e7eaee; overflow:hidden;
}

/* Sisältösäiliö mahdollisimman tiiviiksi */
.main .block-container {
  padding-top:0.1rem !important; padding-bottom:0.1rem !important;
  max-width:880px; margin:0 auto;
}

/* Sticky header – matala */
.header{
  position:sticky; top:0; z-index:50;
  background:rgba(11,15,20,.85); backdrop-filter:blur(6px);
  border-bottom:1px solid rgba(255,255,255,.06);
  padding:6px 10px 4px; margin:0 0 4px 0; height:6dvh;
  display:flex; flex-direction:column; justify-content:center;
}
.header h1{font-size:1.12rem; line-height:1.1; margin:0; font-weight:700;}
.header .meta{font-size:.86rem; opacity:.75; margin-top:1px}

/* Kortit */
.card{
  background:rgba(255,255,255,0.04);
  border:1px solid rgba(255,255,255,0.07);
  border-radius:16px; padding:10px 12px;
  box-shadow:0 4px 16px rgba(0,0,0,0.18);
  display:flex; flex-direction:column; gap:8px;
}
.card-title{font-weight:700; font-size:1.0rem; color:#f2f4f7;}
.card-body{font-size:.96rem; color:#dfe3e8; line-height:1.35; flex:1;}
.card-body p{margin:0;}
small, .hint{opacity:.75}

.weather-card { padding: 0.75rem; }
.weather-row {
  display: grid;
  grid-template-columns: repeat(5, minmax(88px, 1fr)); /* Nyt, +3, +6, +9, +12 */
  gap: 10px;
  align-items: stretch;
}
.weather-cell {
  display: grid;
  grid-template-rows: auto auto 1fr auto auto; /* label, hour, icon, temp, pop */
  align-items: center;
  justify-items: center;
  background: var(--bg2);
  border-radius: 14px;
  padding: 6px 6px;
  min-height: 110px;
}

.weather-cell .label { font-size: .85rem; opacity: .8; margin-bottom: .25rem; }
.weather-cell .temp { font-size: 1.1rem; margin-top: .35rem; }

/* --- Sääikonit näkyviin --- */
.weather-cell .icon { 
  width: 48px; height: 48px; 
  color:#e7eaee;               /* ikonien perusväri */
}
.weather-cell .icon svg {
  width:100%; height:100%; 
  display:block;
  fill: currentColor;          /* väri ikonien täyttöön */
  stroke: currentColor;        /* väri ikonien ääriviivoihin */
}

.weather-cell .icon img { width:48px; height:48px; display:block; }

/* Minigrafiikat */
.bar{margin:6px 0 2px;}
.bar-head{display:flex; justify-content:space-between; font-size:.92rem; opacity:.9; margin-bottom:4px;}
.bar-rail{
  width:100%; height:8px; border-radius:999px; overflow:hidden;
  background:linear-gradient(90deg,#1b2330,#121822);
  border:1px solid rgba(255,255,255,0.1);
}
.bar-fill{height:100%; background:linear-gradient(90deg,#34d399,#fbbf24,#f97316,#ef4444);}

/* Hintachipit */
.chip{padding:3px 8px; border-radius:999px; font-weight:700; font-size:.92rem;}
.chip.green{background:#103225; color:#8ff5c0; border:1px solid #1f7a59;}
.chip.yellow{background:#332b10; color:#ffe08a; border:1px solid #8a6d1f;}
.chip.orange{background:#331d10; color:#ffc19a; border:1px solid #8a3f1f;}
.chip.red{background:#331012; color:#ff9aa7; border:1px solid #8a1f2b;}

/* Rivien välit dvh:llä */
.rowgap{height:0.5dvh}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
.hm{
  display:grid;
  grid-template-columns: repeat(12, 1fr);
  grid-auto-rows: 10px;   /* nosta 12px jos haluat isommat palat */
  gap:2px; margin-top:6px;
}
.hm .c{ height:10px; border-radius:3px; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
/* KAKSIPALSTAINEN RIVI, joka EI pinoudu tabletissa */
.two-col-row{
  display:grid;
  grid-template-columns: 1fr 1fr;  /* aina kaksi palstaa */
  gap:12px;
}
/* Halutessasi pinoudu vain hyvin kapealla (esim. puhelin <420px) */
@media (max-width: 420px){
  .two-col-row{ grid-template-columns: 1fr; }
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
@media (max-width: 780px){
  html, body, [data-testid="stAppViewContainer"]{
    overflow:auto;   /* jos joskus korkeudet ylittyvät */
  }
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
/* Pakota heti #zen-row-start -ankkurin JÄLKEINEN sarakerivi kahdeksi palstaksi */
#zen-row-start + div[data-testid="stHorizontalBlock"]{
  display:grid !important;
  grid-template-columns: 1fr 1fr !important;
  gap:12px !important;
}
/* Sarakesisällön oletusleveys järkeväksi */
#zen-row-start + div[data-testid="stHorizontalBlock"] > div[data-testid="column"]{
  width:auto !important;
  min-width:0 !important;
  flex: 1 1 auto !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
/* Override Android WebView media-breakpoints for Zen-row */
#zen-row-start + div[data-testid="stHorizontalBlock"]{
  display:grid !important;
  grid-template-columns: 1fr 1fr !important;
  gap:12px !important;
}
@media (max-width: 1200px){
  #zen-row-start + div[data-testid="stHorizontalBlock"]{
    display:grid !important;
    grid-template-columns: 1fr 1fr !important;
  }
}
</style>
""", unsafe_allow_html=True)


# ---- DATA ----
@st.cache_data(ttl=300)
def fetch_weather(lat, lon):
    url = ("https://api.open-meteo.com/v1/forecast"
           f"?latitude={lat}&longitude={lon}"
           "&hourly=temperature_2m,precipitation_probability"
           "&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max"
           "&timezone=Europe%2FHelsinki")
    r = requests.get(url, timeout=10); r.raise_for_status()
    return r.json()

# KORJAUS 1: Lisää puuttuva `fetch_prices_for` -funktio
@st.cache_data(ttl=300)
def fetch_prices_for(date_ymd: dt.date):
    y = date_ymd.strftime("%Y"); md = date_ymd.strftime("%m-%d")
    url = f"https://www.sahkonhintatanaan.fi/api/v1/prices/{y}/{md}.json"
    r = requests.get(url, timeout=10); r.raise_for_status()
    data = r.json()
    out = []
    for row in data:
        ts = dt.datetime.fromisoformat(row["time_start"]).astimezone(TZ)
        cents = round(row["EUR_per_kWh"] * 100, 3)
        out.append({"hour": ts.hour, "cents": cents})
    return out
    
def _stats(prices_list):
    """Palauta (avg, lo, hi) kun prices_list = [{'hour':int,'cents':float}, ...]."""
    if not prices_list:
        return None, None, None
    avg = sum(p['cents'] 
    for p in prices_list) / len(prices_list)
    lo = min(prices_list, key=lambda x: x['cents'])
    hi = max(prices_list, key=lambda x: x['cents'])
    return avg, lo, hi

@st.cache_data(ttl=300)
def try_fetch_prices(date_ymd: dt.date):
    """
    Kääre, joka yrittää hakea hinnat annetulle päivälle.
    Palauttaa listan (kuten fetch_prices_for) tai None jos dataa ei ole (404 tms).
    """
    try:
        return fetch_prices_for(date_ymd)
    except Exception:
        return None


@st.cache_data(ttl=120)
def fetch_btc_eur():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=eur"
    r = requests.get(url, timeout=10); r.raise_for_status()
    return float(r.json()["bitcoin"]["eur"])

# ... (Muu DATA-osio pysyy samana) ...

ATH_CACHE_FILE = Path(__file__).with_name("btc_ath_cache.json")

@st.cache_data(ttl=43200)  # 12 h – haetaan ATH korkeintaan pari kertaa päivässä
def fetch_btc_ath_eur():
    """
    Palauttaa (ath_eur: float, ath_date_iso: str) tai (None, None).
    Käyttää CoinGeckon /coins/bitcoin -päätettä, mutta:
      - Välimuisti 12 h
      - Tiedostovarmistus: jos API rajoittaa (429), luetaan viimeisin talletettu arvo btc_ath_cache.json:ista.
    """
    url = ("https://api.coingecko.com/api/v3/coins/bitcoin"
           "?localization=false&tickers=false&market_data=true"
           "&community_data=false&developer_data=false&sparkline=false")

    # 1) Yritä hakea verkosta
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        d = r.json()
        ath = d.get("market_data", {}).get("ath", {}).get("eur")
        ath_date = d.get("market_data", {}).get("ath_date", {}).get("eur")
        if ath is not None:
            # talleta varmuuskopioon
            try:
                ATH_CACHE_FILE.write_text(json.dumps({"ath_eur": float(ath), "ath_date": ath_date}), encoding="utf-8")
            except Exception:
                pass
            return float(ath), ath_date
    except requests.HTTPError as e:
        # 429 tms. – pudotaan paikalliseen varmuuskopioon
        if e.response is not None and e.response.status_code == 429:
            try:
                if ATH_CACHE_FILE.exists():
                    js = json.loads(ATH_CACHE_FILE.read_text(encoding="utf-8"))
                    return float(js.get("ath_eur")), js.get("ath_date")
            except Exception:
                pass
        # muu HTTP-virhe: jatketaan fallbackiin alla
    except Exception:
        pass

    # 2) Fallback: paikallinen varmuuskopio, jos saatavilla
    try:
        if ATH_CACHE_FILE.exists():
            js = json.loads(ATH_CACHE_FILE.read_text(encoding="utf-8"))
            return float(js.get("ath_eur")), js.get("ath_date")
    except Exception:
        pass

    # 3) Ei saatavilla
    return None, None

@st.cache_data(ttl=900)  # välimuisti 15 min
def fetch_btc_last_7d_eur():
    """
    Hakee Bitcoinin hinnat viimeiseltä 7 päivältä (EUR) CoinGeckosta.
    Käyttää CoinGeckon /market_chart/range -päätettä.
    Palauttaa listan (datetime, hinta_float) aikajärjestyksessä.
    """
    now = dt.datetime.now(TZ)
    start = now - dt.timedelta(days=7)
    start_ts = int(start.timestamp())
    end_ts = int(now.timestamp())

    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart/range"
    params = {"vs_currency": "eur", "from": start_ts, "to": end_ts}
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    data = r.json().get("prices", [])

    out = []
    for ms, price in data:
        try:
            t = dt.datetime.fromtimestamp(ms / 1000, tz=TZ)
            out.append((t, float(price)))
        except Exception:
            continue

    # Harvenna 1 h välein, jotta käyrä pysyy kevyenä
    pruned = []
    last_added = None
    for t, p in out:
        if (last_added is None) or ((t - last_added).total_seconds() >= 3600):
            pruned.append((t, p))
            last_added = t

    return pruned if pruned else out


@st.cache_data(ttl=43200)
def fetch_nameday_today():
    """
    1) Yritetään lukea nimipäivät paikallisesta tiedostosta nimipaivat_fi.json
       (sama hakemisto kuin app.py).
    2) Jos ei onnistu, kokeillaan kahta Abalin-APIa.
    3) Muuten palautetaan '—'.
    """
    # ---- 1) Paikallinen tiedosto
    try:
        here = Path(__file__).resolve().parent
        fp = here / "nimipaivat_fi.json"
        if fp.exists():
            with fp.open("r", encoding="utf-8") as f:
                js = json.load(f)

            # Odotettu rakenne: { "nimipäivät": { "<kuukausi>": { "<päivä>": "Nimi, Nimi2", ... }, ... } }
            months = {
                1: "tammikuu", 2: "helmikuu", 3: "maaliskuu", 4: "huhtikuu",
                5: "toukokuu", 6: "kesäkuu", 7: "heinäkuu", 8: "elokuu",
                9: "syyskuu", 10: "lokakuu", 11: "marraskuu", 12: "joulukuu"
            }
            today = dt.datetime.now(TZ)
            mkey = months[today.month]
            dkey = str(today.day)  # päivät ovat merkkijonoina JSONissa

            names = js["nimipäivät"][mkey].get(dkey)
            if names:
                return names
    except Exception:
        pass  # jatketaan verkko-APIn fallbackiin

    # ---- 2) Fallback: Abalin API (jos paikallinen puuttuu / muoto poikkeaa)
    for u in ("https://nameday.abalin.net/api/V1/today?country=fi",
              "https://api.abalin.net/today?country=fi"):
        try:
            r = requests.get(u, timeout=8); r.raise_for_status()
            js = r.json()
            names = (js.get("data", {}).get("name")
                     or js.get("data", {}).get("fi")
                     or js.get("name"))
            if names:
                return names
        except Exception:
            continue

    # ---- 3) Ei löytynyt
    return "—"

# ... (Muu koodi pysyy samana) ...

# ---- PÄIVÄN AJATUS / SITAATTI ----

ZEN_AUTHORS = [
    "Buddha", "Siddhartha", "Dalai Lama", "Tenzin Gyatso", "Thich Nhat Hanh",
    "Lao Tzu", "Laozi", "Dogen", "Eihei Dogen", "Shunryu Suzuki",
    "Bodhidharma", "Ryokan", "Hui Neng", "Huineng", "Zhuangzi", "Chuang Tzu"
]

def _is_zen_author(name: str) -> bool:
    if not name: 
        return False
    n = name.lower()
    return any(z.lower() in n for z in ZEN_AUTHORS)

def _from_zenquotes():
    # Päivän lainaus
    try:
        r = requests.get("https://zenquotes.io/api/today", timeout=6)
        if r.ok:
            data = r.json()
            if isinstance(data, list) and data:
                q = {"text": data[0].get("q", "").strip(),
                     "author": data[0].get("a", "").strip(),
                     "source": "zenquotes-today"}
                return q
    except Exception:
        pass
    # Varalle satunnainen
    try:
        r = requests.get("https://zenquotes.io/api/random", timeout=6)
        if r.ok:
            data = r.json()
            if isinstance(data, list) and data:
                q = {"text": data[0].get("q", "").strip(),
                     "author": data[0].get("a", "").strip(),
                     "source": "zenquotes-random"}
                return q
    except Exception:
        pass
    return None

def _from_quotable(prefer_zen=True, max_tries=6):
    # Hakee "wisdom|life|inspirational" -tageilla, pyrkii zen-kirjoittajaan
    last = None
    for _ in range(max_tries):
        try:
            r = requests.get(
                "https://api.quotable.io/random",
                params={"tags": "wisdom|life|inspirational"},
                timeout=6
            )
            if not r.ok:
                continue
            d = r.json()
            q = {"text": d.get("content", "").strip(),
                 "author": d.get("author", "").strip(),
                 "source": "quotable"}
            if q["text"]:
                last = q
                if not prefer_zen or _is_zen_author(q["author"]):
                    return q
        except Exception:
            continue
    return last

@st.cache_data(ttl=3600)
def fetch_daily_quote(day_iso: str):
    """
    Palauttaa sanakirjan {text, author, source}.
    Välimuistitetaan 1 h välein; day_iso sitoo cachen päivään.
    """
    # 1) ZenQuotes → jos ei zen-kirjoittaja, yritä Quotablea
    q = _from_zenquotes()
    if q and not _is_zen_author(q["author"]):
        q2 = _from_quotable(prefer_zen=True)
        if q2:
            q = q2

    # 2) Varalle Quotable
    if not q:
        q = _from_quotable(prefer_zen=True)

    # 3) Viimeinen varmistus
    if not q:
        q = {
            "text": "He who conquers himself is the mightiest warrior.",
            "author": "Confucius",
            "source": "fallback"
        }
    return q

# ---- HEADER ----
ip = get_ip()
now = dt.datetime.now(TZ)
# st.markdown(f"""
# <div class="header">
  # <h1>Kotidashboard</h1>

# </div>
# """, unsafe_allow_html=True)

 # <div class="meta">http://{ip}:{PORT} · {now:%Y-%m-%d %H:%M} · Lenovo M9 – kioski</div>

# --- Sääikonit (SVG) ja WMO->ikoninimi ---
WX_SVGS = {
    "clear-day": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="48" height="48" fill="currentColor" stroke="currentColor"><circle cx="12" cy="12" r="5"/><g stroke-width="2"><line x1="12" y1="1" x2="12" y2="4"/><line x1="12" y1="20" x2="12" y2="23"/><line x1="1" y1="12" x2="4" y2="12"/><line x1="20" y1="12" x2="23" y2="12"/><line x1="4.2" y1="4.2" x2="6.3" y2="6.3"/><line x1="17.7" y1="17.7" x2="19.8" y2="19.8"/><line x1="4.2" y1="19.8" x2="6.3" y2="17.7"/><line x1="17.7" y1="6.3" x2="19.8" y2="4.2"/></g></svg>',
    "clear-night": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="48" height="48" fill="currentColor" stroke="currentColor"><path d="M16.5 2a8.5 8.5 0 1 0 5.5 14.7A9.5 9.5 0 0 1 16.5 2z"/></svg>',
    "partly-cloudy-day": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="48" height="48" fill="currentColor" stroke="currentColor"><circle cx="7" cy="7" r="3"/><path d="M5 16h10a3 3 0 0 0 0-6 4 4 0 0 0-7-2 3 3 0 0 0-3 5z"/></svg>',
    "partly-cloudy-night": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="48" height="48" fill="currentColor" stroke="currentColor"><path d="M9 3a5 5 0 1 0 7 7 6 6 0 0 1-7-7z"/><path d="M5 16h10a3 3 0 0 0 0-6 4 4 0 0 0-7-2 3 3 0 0 0-3 5z"/></svg>',
    "cloudy": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="48" height="48" fill="currentColor" stroke="currentColor"><path d="M6 18h11a4 4 0 0 0 0-8 6 6 0 0 0-11-2A4 4 0 0 0 6 18z"/></svg>',
    "rain": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="48" height="48" fill="currentColor" stroke="currentColor"><path d="M6 15h11a4 4 0 0 0 0-8 6 6 0 0 0-11-2A4 4 0 0 0 6 15z"/><path d="M8 19l-1 3M12 19l-1 3M16 19l-1 3" stroke-width="2"/></svg>',
    "rain-showers": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="48" height="48" fill="currentColor" stroke="currentColor"><path d="M6 14h11a4 4 0 0 0 0-8 6 6 0 0 0-11-2A4 4 0 0 0 6 14z"/><path d="M8 17l-1 3M12 17l-1 3M16 17l-1 3" stroke-width="2"/></svg>',
    "snow": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="48" height="48" fill="currentColor" stroke="currentColor"><path d="M6 15h11a4 4 0 0 0 0-8 6 6 0 0 0-11-2A4 4 0 0 0 6 15z"/><path d="M10 18l2 2 2-2-2-2-2 2z"/></svg>',
    "thunderstorm": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="48" height="48" fill="currentColor" stroke="currentColor"><path d="M6 14h11a4 4 0 0 0 0-8 6 6 0 0 0-11-2A4 4 0 0 0 6 14z"/><path d="M11 16l-2 4h3l-1 4 4-6h-3l1-2z"/></svg>',
    "fog": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="48" height="48" fill="currentColor" stroke="currentColor"><path d="M3 10h18M3 13h18M3 16h18" stroke-width="2"/></svg>',
    "freezing-rain": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="48" height="48" fill="currentColor" stroke="currentColor"><path d="M6 15h11a4 4 0 0 0 0-8 6 6 0 0 0-11-2A4 4 0 0 0 6 15z"/><path d="M10 17v3M14 17v3" stroke-width="2"/></svg>',
    "drizzle": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="48" height="48" fill="currentColor" stroke="currentColor"><path d="M6 15h11a4 4 0 0 0 0-8 6 6 0 0 0-11-2A4 4 0 0 0 6 15z"/><path d="M9 18h6" stroke-width="2"/></svg>',
    "na": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="48" height="48" fill="currentColor" stroke="currentColor"><text x="6" y="16">?</text></svg>',
}

def _wmo_to_icon_key(code: int, is_day: bool) -> str:
    m = {
        0: "clear-day" if is_day else "clear-night",
        1: "partly-cloudy-day" if is_day else "partly-cloudy-night",
        2: "partly-cloudy-day" if is_day else "partly-cloudy-night",
        3: "cloudy",
        45: "fog", 48: "fog",
        51: "drizzle", 53: "drizzle", 55: "drizzle",
        56: "freezing-rain", 57: "freezing-rain",
        61: "rain", 63: "rain", 65: "rain",
        66: "freezing-rain", 67: "freezing-rain",
        71: "snow", 73: "snow", 75: "snow", 77: "snow",
        80: "rain-showers", 81: "rain-showers", 82: "rain-showers",
        85: "snow", 86: "snow",
        95: "thunderstorm", 96: "thunderstorm", 99: "thunderstorm",
    }
    return m.get(int(code) if code is not None else -1, "na")

@st.cache_data(ttl=300)
def fetch_weather_points(lat: float, lon: float, tz: str = "Europe/Helsinki", offsets=(0,3,6,9,12)):
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&current_weather=true"
        "&hourly=temperature_2m,weathercode,is_day,precipitation_probability"
        f"&timezone={tz}"
    )
    r = requests.get(url, timeout=10); r.raise_for_status()
    data = r.json()

    hel = zoneinfo.ZoneInfo(tz)
    base = dt.datetime.now(hel).replace(minute=0, second=0, microsecond=0)

    # Tuntidata
    hourly = data.get("hourly", {})
    times = hourly.get("time", [])
    temps = hourly.get("temperature_2m", [])
    codes = hourly.get("weathercode", [])
    isday = hourly.get("is_day", [])
    pops  = hourly.get("precipitation_probability", [])

    def find_index(target_dt: dt.datetime) -> int:
        try:
            return times.index(target_dt.strftime("%Y-%m-%dT%H:00"))
        except ValueError:
            diffs = [abs(dt.datetime.fromisoformat(t).replace(tzinfo=hel) - target_dt).total_seconds() for t in times]
            return diffs.index(min(diffs))

    points = []
    for h in offsets:
        target = base + dt.timedelta(hours=h)
        idx = find_index(target)
        temp = temps[idx] if idx < len(temps) else None
        code = codes[idx] if idx < len(codes) else None
        dayf = bool(isday[idx]) if idx < len(isday) else True
        pop  = pops[idx] if idx < len(pops) else None
        label = "Nyt" if h == 0 else f"+{h} h"
        clock = target.strftime("%H")  # tuntileima 00–23

        points.append({
            "label": label,
            "hour": clock,
            "temp": temp,
            "key": _wmo_to_icon_key(code, dayf),
            "pop": None if pop is None else int(round(pop)),
        })

    return points


# ---- YLÄMARGINAALI ----
st.markdown('<div style="height:1dvh"></div>', unsafe_allow_html=True)

# ---- RIVI 3: Nimipäivät + Päivän zen (2 saraketta, ei pinoutumista) ----
st.markdown('<div id="zen-row-start"></div>', unsafe_allow_html=True)  # ankkuri CSS-kohdistusta varten
col_names, col_zen = st.columns(2, gap="small")

with col_names:
    try:
        names = fetch_nameday_today()

        # --- Lue perhoskuva ja tee data-URI ---
        here = Path(__file__).resolve().parent
        p = here / "butterfly-bg.png"  # vaihda nimeä tarvittaessa
        BG_DATAURL = None
        if p.exists():
            b = p.read_bytes()
            # MIME valinta päätteestä
            ext = p.suffix.lower()
            mime = "image/png" if ext==".png" else ("image/webp" if ext==".webp" else "image/jpeg")
            BG_DATAURL = f"data:{mime};base64," + base64.b64encode(b).decode("ascii")

        # --- Kortin HTML ---
        overlay = "linear-gradient(rgba(11,15,20,0.35), rgba(11,15,20,0.55))"
        html = f"""
        <section class="card" style="
          min-height:16dvh; position:relative; overflow:hidden;
          background-image:{overlay};
          background-size:cover; background-position:center;">
          <div class="card-title">Nimipäivät</div>
          <div class="card-body">
            <div style="font-size:1.35rem; font-weight:800; margin:0 0 6px 0;">{names}</div>
          </div>

          <!-- Perhonen taustana oikealla: contain + right center -->
          {'<div style="position:absolute; inset:0; background-image:url('+BG_DATAURL+'); background-repeat:no-repeat; background-size:contain; background-position:right center; pointer-events:none; filter: drop-shadow(0 6px 16px rgba(0,0,0,.45));"></div>' if BG_DATAURL else ''}

          <!-- Hento tumma liuku päälle, jotta teksti pysyy luettavana -->
          <div style="position:absolute; inset:0; background:linear-gradient(90deg, rgba(11,15,20,0.65) 0%, rgba(11,15,20,0.25) 45%, rgba(11,15,20,0.00) 70%); pointer-events:none;"></div>
        </section>
        """
        st.markdown(html, unsafe_allow_html=True)

        if not BG_DATAURL:
            st.markdown("<small class='hint'>Perhoskuvaa ei löytynyt (butterfly-bg.png / .webp / .jpg).</small>", unsafe_allow_html=True)

    except Exception as e:
        card("Nimipäivät", f"<span class='hint'>Ei saatu tietoa: {e}</span>", height_dvh=16)




with col_zen:
    try:
# Kevyt "zen"-tausta: vuorilinja-aaltojen siluetti (himmeä)
        ZEN_BG_SVG = """
        <svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 800 600'>
          <defs>
            <linearGradient id='sky' x1='0' y1='0' x2='0' y2='1'>
              <stop offset='0' stop-color='#ffffff' stop-opacity='0.05'/>
              <stop offset='1' stop-color='#000000' stop-opacity='0'/>
            </linearGradient>
          </defs>
          <rect width='100%' height='100%' fill='url(#sky)'/>
          <path d='M0 420 Q100 360 220 420 T440 420 T660 420 T880 420 V600 H0 Z'
                fill='#ffffff' fill-opacity='0.04'/>
          <path d='M0 460 Q120 400 240 460 T480 460 T720 460 T880 460 V600 H0 Z'
                fill='#ffffff' fill-opacity='0.06'/>
          <path d='M0 500 Q140 440 280 500 T560 500 T840 500 T880 500 V600 H0 Z'
                fill='#ffffff' fill-opacity='0.08'/>
        </svg>
        """.strip()
        
        ZEN_BG_URL = "data:image/svg+xml;utf8," + urllib.parse.quote(ZEN_BG_SVG)


        ZEN_AUTHORS = [
            "Buddha","Siddhartha","Dalai Lama","Tenzin Gyatso","Thich Nhat Hanh",
            "Lao Tzu","Laozi","Dogen","Eihei Dogen","Shunryu Suzuki",
            "Bodhidharma","Ryokan","Hui Neng","Huineng","Zhuangzi","Chuang Tzu"
        ]
        def _is_zen_author(name: str) -> bool:
            return bool(name) and any(z.lower() in name.lower() for z in ZEN_AUTHORS)

        LOCAL_ZEN = [
            ("The mind is everything. What you think you become.", "Buddha"),
            ("The present moment is filled with joy and happiness. If you are attentive, you will see it.", "Thich Nhat Hanh"),
            ("Silence is a source of great strength.", "Laozi"),
            ("If you correct your mind, the rest of your life will fall into place.", "Laozi"),
            ("When you realize nothing is lacking, the whole world belongs to you.", "Laozi"),
            ("To conquer oneself is a greater task than conquering others.", "Buddha"),
            ("The practice of peace and reconciliation is one of the most vital and artistic of human actions.", "Thich Nhat Hanh"),
            ("If you cannot find the truth right where you are, where else do you expect to find it?", "Dogen")
        ]

        q_text, q_author = None, None

        # ZenQuotes (vain zen-tekijä)
        try:
            r = requests.get("https://zenquotes.io/api/today", timeout=6)
            if r.ok:
                data = r.json()
                if isinstance(data, list) and data and data[0].get("q"):
                    cand_text = str(data[0].get("q", "")).strip()
                    cand_author = str(data[0].get("a", "")).strip()
                    if _is_zen_author(cand_author):
                        q_text, q_author = cand_text, cand_author
        except Exception:
            pass

        # Quotable (vain zen-tekijä)
        if not q_text:
            for _ in range(10):
                try:
                    r = requests.get("https://api.quotable.io/random",
                        params={"tags":"wisdom|life|inspirational"}, timeout=6)
                    if not r.ok:
                        continue
                    d = r.json()
                    cand_text = str(d.get("content", "")).strip()
                    cand_author = str(d.get("author", "")).strip()
                    if cand_text and _is_zen_author(cand_author):
                        q_text, q_author = cand_text, cand_author
                        break
                except Exception:
                    continue

        if not q_text:
            import random
            q_text, q_author = random.choice(LOCAL_ZEN)

        # --- Taustakuva PNG data-URI:ksi ---
        
        ZEN_BG_DATAURL = None
        try:
            # Hakee tiedoston samasta hakemistosta kuin tämä ajettava tiedosto
            img_path = Path(__file__).resolve().parent / "zen-bg.png" 
            if img_path.exists():
                with img_path.open("rb") as f:
                    ZEN_BG_DATAURL = "data:image/png;base64," + base64.b64encode(f.read()).decode("ascii")
        except Exception:
            pass  # jos ei löydy, käytetään pelkkää taustaväriä

        # --- Kortin HTML taustalla ---
        overlay = "linear-gradient(rgba(11,15,20,0.55), rgba(11,15,20,0.55))"
        bg_layer = f"{overlay}, url('{ZEN_BG_DATAURL}')" if ZEN_BG_DATAURL else overlay

        zen_html = f"""
        <section class="card" style="
          min-height:16dvh;
          position:relative;
          overflow:hidden;
          background-image: {bg_layer};
          background-size: cover;
          background-position: center;">
          <div class="card-title">Päivän zen</div>
          <div class="card-body">
            <div style="margin:0; line-height:1.35;">
              <em>“{q_text}”</em>{' — ' + q_author if q_author else ''}
            </div>
          </div>
        </section>
        """
        st.markdown(zen_html, unsafe_allow_html=True)


    except Exception as e:
        card("Päivän zen", f"<span class='hint'>Ei saatu tietoa: {e}</span>", height_dvh=16)

# ---- RIVI 4: Bitcoin ----

# ---- RIVI 1: Sää (20dvh) ----
from streamlit.components.v1 import html as st_html

try:
    pts = fetch_weather_points(LAT, LON, "Europe/Helsinki", offsets=(0,3,6,9,12))

    def cell(p):
        # Ikoni kuvana (data-URI)
        svg = WX_SVGS.get(p["key"], WX_SVGS["na"])
        src = _svg_data_uri(svg, "#e7eaee")
        t = "–" if p["temp"] is None else f"{round(p['temp'])}"
        pop = "–" if p["pop"] is None else f"{p['pop']}%"
        # Label + tuntileima omilla riveillään:
        return f"""
        <div class="weather-cell">
          <div class="label">{p['label']}</div>
          <div class="sub">{p['hour']}:00</div>
          <div class="icon"><img src="{src}" alt="{p['key']}" width="48" height="48"></div>
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
    .title {{ font-weight:700; font-size:1.0rem; color:#f2f4f7; margin:0 0 4px 0; }}
  .weather-card {{ padding: 8px 12px 6px; }}
  .weather-row {{
  display: grid;
  grid-template-columns: repeat(5, minmax(88px, 1fr)); /* Nyt, +3, +6, +9, +12 */
  gap: 10px;
  align-items: stretch;
  }}
  .weather-cell {{
  display: grid;
  grid-template-rows: auto auto 1fr auto auto; /* label, hour, icon, temp, pop */
  align-items: center;
  justify-items: center;
  background: var(--bg2);
  border-radius: 14px;
  padding: 6px 6px;
  min-height: 110px;
  }}

  .label {{ font-size:.9rem; opacity:.9; margin:2px 0 0; }}
  .sub   {{ font-size:.8rem; opacity:.75; margin:0 0 4px; }}
  .icon img {{ width:48px; height:48px; display:block; }}
  .temp  {{ font-size:1.1rem; margin-top:6px; }}
  .pop   {{ font-size:.85rem; opacity:.85; margin-top:2px; }}
</style>
</head>
<body>
<div class="weather-card">
    <div class="weather-row">
      {''.join(cell(p) for p in pts)}
    </div>
  </div>
</body>
</html>
    """

    section_title("Sää – Riihimäki")


    st_html(inner_html, height=180, scrolling=False)

except Exception as e:
    card("Sää – Riihimäki", f"<span class='hint'>Ei saatu säätietoa: {e}</span>", height_dvh=20)


# ---- RIVI 2: Pörssisähkö

# ---- RIVI 2: Pörssisähkö (täyslevy) ----
with st.container():
    try:
        today = now.date()
        tomorrow = today + dt.timedelta(days=1)

        prices_today = try_fetch_prices(today)
        if not prices_today:
            # Korjattu: Nyt antaa virheen, jos päivän hintadata puuttuu
            raise RuntimeError("Ei päivän hintadataa")
        prices_tomorrow = try_fetch_prices(tomorrow)

        df12 = _next_12h_df(prices_today, prices_tomorrow, now)
        if df12.empty:
            section_title("Pörssisähkö – seuraavat 12 h")
            st.markdown("<span class='hint'>Ei hintoja saatavilla.</span>", unsafe_allow_html=True)
        else:
            vals = df12["cents"].tolist()
            cols = _color_by_thresholds(vals, low_thr=5.0, high_thr=15.0)
            line_colors = ["rgba(255,255,255,0.9)" if is_now else "rgba(0,0,0,0)" for is_now in df12["is_now"]]
            line_widths = [1.5 if is_now else 0 for is_now in df12["is_now"]]

            fig = go.Figure([
                go.Bar(
                    x=df12["hour_label"],
                    y=[round(v, 2) for v in vals],
                    marker=dict(color=cols, line=dict(color=line_colors, width=line_widths)),
                    hovertemplate="<b>%{x}</b><br>%{y} snt/kWh<extra></extra>",
                )
            ])
            section_title("Pörssisähkö – seuraavat 12 h")
            fig.update_layout(
                title=None,
                title_x=0,
                title_font_size=14,
                margin=dict(l=10, r=10, t=24, b=44),
                xaxis_title=None, yaxis_title="snt/kWh",
                height=240,
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(gridcolor="rgba(255,255,255,0.08)"),
                yaxis=dict(gridcolor="rgba(255,255,255,0.08)"),
            )
            st.plotly_chart(fig, use_container_width=True, theme=None, config={"displayModeBar": False})
            st.markdown("""
<div class='hint' style='margin-top:6px; margin-bottom:2px;'>
  <span style='color:#00b400;'>&#9632;</span> ≤ 5 snt &nbsp;
  <span style='color:#cccc00;'>&#9632;</span> 5–15 snt &nbsp;
  <span style='color:#dc0000;'>&#9632;</span> ≥ 15 snt &nbsp;
  (vihreä = halpa, punainen = kallis)
</div>
""", unsafe_allow_html=True)
    except Exception as e:
        # KORJAUS 2: Siirretty virheilmoitus catch-lohkon sisään
        section_title("Pörssisähkö – seuraavat 12 h")
        st.markdown(f"<span class='hint'>Virhe hinnanhaussa: {e}</span>", unsafe_allow_html=True)



# ---- RIVI 3: Nimipäivät

# ---- RIVI 4: Bitcoin ----
try:
    eur_now = fetch_btc_eur()
    series = fetch_btc_last_7d_eur()
    ath_eur, ath_date = fetch_btc_ath_eur()

    # Valmistellaan data
    xs = [t for t, _ in series]
    ys = [v for _, v in series]

    # --- Bitcoin-kortin otsikkorivi ---
    # Tuhansien erottaja = välilyönti
    eur_now_fmt = f"{eur_now:,.0f}".replace(",", " ")
    # top_html removed; use section_title below

    # <div style="font-size:1.35rem; font-weight:800">Bitcoin: {eur_now_fmt} €</div>

    # Piirretään 7 d käyrä + ATH-viiva
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=xs, y=ys,
        mode="lines",
        name="BTC/EUR (7 d)",
        hovertemplate="%{x|%d.%m %H:%M} — %{y:.0f} €<extra></extra>",
    ))

    if ath_eur:
        fig.add_trace(go.Scatter(
            x=[xs[0] if xs else dt.datetime.now(TZ), xs[-1] if xs else dt.datetime.now(TZ)],
            y=[ath_eur, ath_eur],
            mode="lines",
            name=f"ATH {ath_eur:,.0f} €",
            line=dict(dash="dot"),
            hovertemplate="ATH — %{y:.0f} € (%{x|%d.%m})<extra></extra>",
        ))

        # --- Laske dynaaminen skaala ---
    if ys:
        min_y = min(ys)
        max_y = max(ys)
        base_low = eur_now - 5000
        base_high = max(max_y, ath_eur or eur_now) + 5000
        # Pyöristetään lähimpään 5000 €
        y_min = int((base_low // 5000) * 5000)
        y_max = int(((base_high + 4999) // 5000) * 5000)
    else:
        y_min, y_max = 0, None

    # --- Laske dynaaminen skaala (kuten aiemmin) ---
    if ys:
        min_y = min(ys)
        max_y = max(ys)
        base_low = eur_now - 5000
        base_high = max(max_y, ath_eur or eur_now) + 5000
        # Pyöristys 5000 €:n tasoihin
        y_min = int((base_low // 5000) * 5000)
        y_max = int(((base_high + 4999) // 5000) * 5000)
    else:
        y_min, y_max = 0, None

    # --- Hintalappu (nykyarvo käyrän lopussa) ---
    if xs and ys:
        label_text = f"{ys[-1]:,.0f}".replace(",", " ") + " €"
        fig.add_annotation(
            x=xs[-1], y=ys[-1],
            xref="x", yref="y",
            text=label_text,
            showarrow=False,
            xanchor="right",     # tekstin oikea reuna osuu datapisteeseen
            align="right",
            xshift=-12,          # lisää tilaa vasemmalle (siirto pikseleinä)
            font=dict(color="#e7eaee", size=12)
            # halutessasi tausta:
            # bgcolor="rgba(0,0,0,0.35)", borderpad=3, bordercolor="rgba(255,255,255,0.25)"
        )


    section_title("Bitcoin – viimeiset 7 päivää")
    fig.update_layout(
        margin=dict(l=64, r=12, t=8, b=32),         # enemmän vasemmalle → ei leikkaannu
        height=220,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        font=dict(size=12, color="#e7eaee"),
        xaxis=dict(
            type="date",
            title=None,
            gridcolor="rgba(255,255,255,0.28)",
            tickformat="%d.%m", # päivä.kk
            dtick="D1",                 # yksi tikki/päivä
            tickfont=dict(size=11, color="#cfd3d8"),
            automargin=True
        ),

        yaxis=dict(
            title="€",
            gridcolor="rgba(255,255,255,0.28)",
            tickfont=dict(size=11, color="#cfd3d8"),
            tickformat="~s",                        # 5k, 10k jne.
            range=[y_min, y_max],
            fixedrange=True,
            automargin=True
        ),
        hoverlabel=dict(font_size=11)
    )

    # Kortti: otsikko + yläosan info + käyrä
    st.plotly_chart(fig, use_container_width=True, theme=None, config={"displayModeBar": False})
    st.markdown(
        "<div class='hint' style='margin-top:4px;'>Näytetään viimeiset 7 päivää (CoinGecko), katkoviiva = ATH{}</div>".format(
            f" ({ath_date[:10]})" if ath_date else ""
        ),
        unsafe_allow_html=True
    )
    # Kehys ympärille yhtenäisen ilmeen vuoksi
    # (hyödynnetään valmista card()-apua, wräpätään sisältö siihen)
    # Jos haluat täysin saman “card”-tyylin, tee näin:
    # card("Bitcoin (EUR)", st_plotly_html, height_dvh=16)
    # mutta koska st.plotly_chart renderöityy, käytämme alla pientä kikkaa:
    st.markdown("<div style='margin-top:6px;'></div>", unsafe_allow_html=True)

except Exception as e:
    card("Bitcoin (EUR)", f"<span class='hint'>Virhe: {e}</span>", height_dvh=16)



# ---- RIVI 5: Järjestelmätila ----

# ---- RIVI 5: Järjestelmätila ----
sys_html = f"""
<div style="display:grid; grid-template-columns:auto 1fr; gap:6px 12px;">
  <div class="hint">IP:</div><div>{get_ip()}</div>
  <div class="hint">Portti:</div><div>{PORT}</div>
  <div class="hint">Päivitetty:</div><div>{dt.datetime.now(TZ):%H:%M:%S}</div>
  <div class="hint">Kioskitila:</div><div>Fully Kiosk Browser</div>
</div>
"""
card("Järjestelmätila", sys_html, height_dvh=16)