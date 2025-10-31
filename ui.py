# ui.py
"""User interface components for the HomeDashboard application."""
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import base64
import json
import math

import plotly.graph_objects as go
import streamlit as st
from streamlit.components.v1 import html as st_html

from api import (
    fetch_btc_ath_eur,
    fetch_btc_eur,
    fetch_btc_last_7d_eur,
    fetch_daily_quote,
    fetch_nameday_today,
    fetch_nameday_today,
    fetch_holiday_today,
    fetch_weather_points,
    get_map_trace,
    wmo_to_icon_key,
    try_fetch_prices,
)
from config import (
    BTC_Y_PAD_EUR,
    BTC_Y_PAD_PCT,
    BTC_Y_STEP_EUR,
    BTC_Y_USE_PCT_PAD,
    COLOR_GRAY,
    COLOR_GREEN,
    COLOR_RED,
    COLOR_TEXT_GRAY,
    HERE,
    LAT,
    LON,
    NAMEDAY_PATHS,
    HOLIDAY_PATHS,
    PLOTLY_CONFIG,
    PRICE_Y_MIN_SNT,
    PRICE_Y_STEP_SNT,
    TZ,
)
from utils import (
    get_ip,
    report_error,
    _color_by_thresholds,
    _color_for_value,
    fetch_sun_times,
    _sun_icon,
)
from weather_icons import render_foreca_icon

# ------------------- UTILITY FUNCTIONS -------------------


def load_css(file_name: str) -> None:
    """Load and apply a CSS file to the Streamlit app.

    Args:
        file_name: Name of the CSS file in the project directory.
    """
    path = HERE / file_name
    if not path.exists():
        return
    try:
        with path.open("r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except Exception as e:
        report_error("load_css", e)


def section_title(html: str, mt: int = 10, mb: int = 4) -> None:
    """Render a section title with customizable margins.

    Args:
        html: HTML content for the title.
        mt: Top margin in pixels (default: 10).
        mb: Bottom margin in pixels (default: 4).
    """
    st.markdown(
        f"<div style='margin:{mt}px 0 {mb}px 0'>{html}</div>", unsafe_allow_html=True
    )


def card(title: str, body_html: str, height_dvh: int = 16) -> None:
    """Render a card with a title and HTML body.

    Args:
        title: Card title text.
        body_html: HTML content for the card body.
        height_dvh: Minimum height in dvh units (default: 16).
    """
    st.markdown(
        f"""
        <section class="card" style="min-height:{height_dvh}dvh; position:relative; overflow:hidden;">
          <div class="card-title">{title}</div>
          <div class="card-body">{body_html}</div>
        </section>
        """,
        unsafe_allow_html=True,
    )


# ------------------- NAMEDAY CARD -------------------


def card_nameday() -> None:
    """Render a card displaying today's Finnish namedays."""
    try:
        # --- cache-busterit mtime:stä ---
        p_names = next((p for p in NAMEDAY_PATHS if Path(p).exists()), None)
        mtime_names = Path(p_names).stat().st_mtime_ns if p_names else 0
        p_holidays = next((p for p in HOLIDAY_PATHS if Path(p).exists()), None)
        mtime_holidays = Path(p_holidays).stat().st_mtime_ns if p_holidays else 0

        names = fetch_nameday_today(_cache_buster=mtime_names) or "—"
        hol = fetch_holiday_today(_cache_buster=max(mtime_names, mtime_holidays)) or {}

        # --- otsikkoteksti ---
        now = datetime.now(TZ)
        weekdays_fi = [
            "maanantaina",
            "tiistaina",
            "keskiviikkona",
            "torstaina",
            "perjantaina",
            "lauantaina",
            "sunnuntaina",
        ]
        title_text = (
            f"Nimipäivät<br>{weekdays_fi[now.weekday()]} {now.day}.{now.month}."
        )

        # --- tausta suoraan kortin backgroundiksi ---
        bg_dataurl = None
        for fname in ("butterfly-bg.png", "butterfly-bg.webp", "butterfly-bg.jpg"):
            path = HERE / fname
            if path.exists():
                mime = {"png": "image/png", "webp": "image/webp", "jpg": "image/jpeg"}[
                    path.suffix.lstrip(".")
                ]
                bg_dataurl = f"data:{mime};base64," + base64.b64encode(
                    path.read_bytes()
                ).decode("ascii")
                break

        overlay_css = "linear-gradient(90deg, rgba(11,15,20,0.65) 0%, rgba(11,15,20,0.25) 45%, rgba(11,15,20,0.00) 70%)"
        bg_css = overlay_css + (f", url({bg_dataurl})" if bg_dataurl else "")

        # --- statusrivi (vain jos flag/loma) ---
        is_flag = bool(hol.get("is_flag_day"))
        is_hday = bool(hol.get("is_holiday"))
        holiday_name = (hol.get("holiday") or "").strip()
        has_status = is_flag or is_hday  # <-- tämä

        status_html = ""
        if is_flag or is_hday:
            flag_svg = (
                "<svg xmlns='http://www.w3.org/2000/svg' width='22' height='16' viewBox='0 0 22 16' aria-label='Suomen lippu' style='flex:0 0 auto;'>"
                "<rect width='22' height='16' fill='#ffffff'/>"
                "<rect x='0' y='6' width='22' height='4' fill='#003580'/>"
                "<rect x='6' y='0' width='4' height='16' fill='#003580'/>"
                "</svg>"
            )
            if is_flag and is_hday:
                label_html = (
                    f"{flag_svg}<strong>Liputus- ja lomapäivä:</strong> {holiday_name}"
                )
            elif is_flag:
                label_html = f"{flag_svg}<strong>Liputuspäivä:</strong> {holiday_name}"
            else:
                label_html = f"<strong>Lomapäivä:</strong> {holiday_name}"

            status_html = (
                "<div style='display:flex; align-items:center; gap:8px; "
                "padding:6px 10px; border-radius:999px; width:max-content; "
                "background:rgba(255,255,255,.12); backdrop-filter:blur(2px); "
                "margin:4px 0 6px 0; font-size:.95rem; line-height:1;'>"
                f"{label_html}</div>"
            )

        # --- nimirivi + meta (meta vain jos ei statusriviä) ---
        names_html = (
            "<div style='font-size:1.35rem; font-weight:800; "
            f"margin:{'4px 0 6px 0' if has_status else '0 0 6px 0'}; "
            "color:#fff; text-shadow: 0 1px 2px rgba(0,0,0,.45);'>"
            f"{names}</div>"
        )

        # --- Auringon nousu/lasku: haetaan ja näytetään pillerit ---
        sr, ss = fetch_sun_times(
            LAT, LON, TZ.key
        )  # TZ on pytz/zoneinfo; TZ.key antaa esim. 'Europe/Helsinki'
        sun_html = ""
        if sr or ss:
            # pillerit (lähellä muun kortin tyyliä)
            style_pill = (
                "display:inline-flex;align-items:center;gap:6px;padding:4px 10px;border-radius:999px;"
                "background:rgba(255,255,255,.12);backdrop-filter:blur(2px);margin-right:8px;"
                "font-size:.95rem;line-height:1;color:#fff;"
            )
            rise = f"<span style='{style_pill}'>{_sun_icon('rise',18)}<strong>{sr or '—'}</strong></span>"
            sett = f"<span style='{style_pill}'>{_sun_icon('set',18)}<strong>{ss or '—'}</strong></span>"
            sun_html = f"<div style='margin:2px 0 6px 0;'>{rise}{sett}</div>"

        meta_html = ""
        if (not is_flag and not is_hday) and holiday_name:
            meta_html = (
                "<div class='meta' style='margin-top:6px; font-size:.95rem; opacity:.95;'>"
                "<span style='display:inline-block; padding:4px 8px; border-radius:999px; "
                "background:rgba(255,255,255,.10); color:#fff;'>"
                f"{holiday_name}</span></div>"
            )

        # --- KORTTI normaalissa virrassa, ilman absoluuttisia kerroksia ---
        html = f"""
        <section class="card"
                 style="min-height:12dvh; position:relative; overflow:hidden;
                        background-image:{bg_css}; background-size:cover; background-position:center;">
          <div class="card-body" style="display:flex; align-items:flex-start; text-align:left; padding:10px 16px 12px 16px;">
            <div style="font-size:1.0rem; line-height:1.2; margin:0; color:#fff; text-shadow:0 1px 2px rgba(0,0,0,.45); width:100%;">
              {status_html}  <!-- nyt ENSIMMÄISENÄ -->
              <div class="card-title" style="margin:{'6px 0 0 0' if has_status else '0'}; color:#f2f4f7;">
                {title_text}
              </div>
              {names_html}
              {sun_html}   <!--  🔆🔅   TÄMÄ UUSI RIVI   -->
              {meta_html}
            </div>
          </div>
        </section>
        """

        st.markdown(html, unsafe_allow_html=True)

    except Exception as e:
        card(
            "Nimipäivät",
            f"<span class='hint'>Ei saatu tietoa: {e}</span>",
            height_dvh=12,
        )


# ------------------- ZEN QUOTE CARD -------------------


def card_zen() -> None:
    """Render a card displaying the daily Zen quote."""
    try:
        today_iso = datetime.now(TZ).date().isoformat()
        quote = fetch_daily_quote(today_iso)
        quote_text = (quote.get("text") or "").strip()
        quote_author = (quote.get("author") or "").strip()

        bg_dataurl = None
        img_path = HERE / "zen-bg.png"
        if img_path.exists():
            try:
                with img_path.open("rb") as f:
                    bg_dataurl = "data:image/png;base64," + base64.b64encode(
                        f.read()
                    ).decode("ascii")
            except Exception as e:
                report_error("zen: load bg", e)

        overlay = "linear-gradient(rgba(11,15,20,0.55), rgba(11,15,20,0.55))"
        bg_layer = f"{overlay}, url('{bg_dataurl}')" if bg_dataurl else overlay

        html = f"""
            <section class="card" style="min-height:12dvh; position:relative; overflow:hidden; background-image:{bg_layer}; background-size:cover; background-position:center;">
              <div class="card-title">Päivän zen</div>
              <div class="card-body" style="display:flex; justify-content:center; align-items:center; text-align:center; flex:1;">
                <div style="margin:0; line-height:1.35;">
                  <em>“{quote_text}”</em>{(' — ' + quote_author) if quote_author else ''}
                </div>
              </div>
            </section>
            """
        st.markdown(html, unsafe_allow_html=True)
    except Exception as e:
        card(
            "Päivän zen",
            f"<span class='hint'>Ei saatu tietoa: {e}</span>",
            height_dvh=12,
        )


# ------------------- WEATHER CARD -------------------


def card_weather() -> None:
    """Render a card displaying weather forecast for Riihimäki (1h/3h/6h -vaihdin otsikkorivillä, ilman JS)."""
    try:
        # --- Valinnan luku URL:sta ja sessioon ---
        qp = st.query_params
        if "wint" in qp:
            raw = str(qp.get("wint"))
            norm = raw.replace(" ", "").lower()
            if norm in ("1h", "3h", "6h"):
                st.session_state["weather_interval"] = f"{norm[0]} h"

        if "weather_interval" not in st.session_state:
            st.session_state["weather_interval"] = "3 h"

        interval = st.session_state["weather_interval"]
        step = int(interval.split()[0])
        offsets = tuple(step * i for i in range(5))

        # --- Hae säädata valitulla välillä ---
        weather_data = fetch_weather_points(
            LAT, LON, "Europe/Helsinki", offsets=offsets
        )
        points = weather_data["points"]
        min_temp = weather_data["min_temp"]
        max_temp = weather_data["max_temp"]

        # --- Otsikko + pillerit (linkkeinä) ---
        title_left = "🌤️ Sää — Riihimäki"
        if (min_temp is not None) and (max_temp is not None):
            title_left += (
                f"&nbsp; | &nbsp; Tänään: {round(min_temp)}°C — {round(max_temp)}°C"
            )

        def pill(opt: str) -> str:
            is_active = opt == interval
            wint = opt.replace(" ", "")  # 1h / 3h / 6h
            base_style = (
                "display:inline-block;margin-left:8px;padding:2px 8px;border-radius:8px;"
                "font-size:.85rem;text-decoration:none;border:1px solid rgba(255,255,255,.18);"
            )
            if is_active:
                style = base_style + "background:#e7eaee;color:#111;"
            else:
                style = base_style + "background:rgba(255,255,255,0.10);color:#e7eaee;"
            # Tässä korjaus: target="_self"
            return f'<a href="?wint={wint}" target="_self" style="{style}">{opt}</a>'

        pills_html = "".join(pill(opt) for opt in ("1 h", "3 h", "6 h"))
        full_title_html = f"{title_left}&nbsp;&nbsp;{pills_html}"

        section_title(full_title_html, mb=3)

        # --- Solun renderöinti ---
        def cell(point: Dict) -> str:
            icon_html = render_foreca_icon(point["key"], size=48)
            temp = "—" if point["temp"] is None else f"{round(point['temp'])}"
            pop = "—" if point["pop"] is None else f"{point['pop']}%"
            return f"""
                <div class="weather-cell">
                  <div class="label">{point['label']}</div>
                  <div class="sub">{point['hour']}:00</div>
                  <div class="icon" style="width:48px; height:48px;">{icon_html}</div>
                  <div class="temp">{temp}°C</div>
                  <div class="pop">Sade {pop}</div>
                </div>
            """

        inner_html = (
            """
            <!doctype html>
            <html><head><meta charset="utf-8">
            <style>
              :root { --fg:#e7eaee; --bg2:rgba(255,255,255,0.06); }
              html,body {margin:0;padding:0;background:transparent;color:var(--fg);
                         font-family:ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,Ubuntu;}
              .weather-card { padding:8px 12px 6px; }
              .weather-row {display:grid;grid-template-columns:repeat(5,minmax(88px,1fr));
                            gap:10px;align-items:stretch;}
              .weather-cell {display:grid;grid-template-rows:auto auto 1fr auto auto;
                             align-items:center;justify-items:center;
                             background:var(--bg2);border-radius:14px;
                             padding:6px 6px;min-height:110px;}
              .label{font-size:.9rem;opacity:.9;margin:2px 0 0;}
              .sub{font-size:.8rem;opacity:.75;margin:0 0 4px;}
              .icon svg{width:48px;height:48px;display:block;}
              .temp{font-size:1.1rem;margin-top:6px;}
              .pop{font-size:.85rem;opacity:.85;margin-top:2px;}
            </style></head><body>
              <div class="weather-card"><div class="weather-row">
            """
            + "".join(cell(p) for p in points)
            + "</div></div></body></html>"
        )

        st_html(inner_html, height=155, scrolling=False)

    except Exception as e:
        report_error("weather card", e)
        card(
            "Sää — Riihimäki",
            f"<span class='hint'>Ei saatu säätietoa: {e}</span>",
            height_dvh=15,
        )


# ------------------- ELECTRICITY PRICES CARD -------------------


def _next_12h_df(
    prices_today: Optional[List[Dict]],
    prices_tomorrow: Optional[List[Dict]],
    now_dt: datetime,
) -> List[Dict]:
    """Generate a list of price data for the next 12 hours.

    Args:
        prices_today: List of today's price data.
        prices_tomorrow: List of tomorrow's price data.
        now_dt: Current datetime.

    Returns:
        List of dictionaries with timestamp, hour label, cents, and is_now flag.
    """
    rows = []
    base = now_dt.replace(minute=0, second=0, microsecond=0)
    for i in range(12):
        timestamp = base + timedelta(hours=i)
        src = prices_today if timestamp.date() == now_dt.date() else prices_tomorrow
        if not src:
            continue
        item = next((p for p in src if p["hour"] == timestamp.hour), None)
        if not item:
            continue
        rows.append(
            {
                "ts": timestamp,
                "hour_label": timestamp.strftime("%H") + ":00",
                "cents": float(item["cents"]),
                "is_now": i == 0,
            }
        )
    return rows


def card_prices() -> None:
    """Render a card displaying electricity prices for the next 12 hours."""
    try:
        today = datetime.now(TZ).date()
        tomorrow = today + timedelta(days=1)
        prices_today = try_fetch_prices(today)
        prices_tomorrow = try_fetch_prices(tomorrow)

        current_cents = None
        if prices_today:
            now_hour = datetime.now(TZ).hour
            hit = next((p for p in prices_today if p["hour"] == now_hour), None)
            if hit:
                current_cents = float(hit["cents"])

        title_html = (
            "⚡ Pörssisähkö "
            + f"<span style='background:{COLOR_GRAY}; color:{COLOR_TEXT_GRAY}; padding:2px 10px; "
            "border-radius:999px; font-weight:600; font-size:0.95rem'>Seuraavat 12 h</span>"
        )
        if current_cents is not None:
            badge_bg = _color_for_value(current_cents)
            title_html += (
                f" <span style='background:{badge_bg}; color:#000; padding:2px 10px; "
                f"border-radius:10px; font-weight:700; font-size:0.95rem'>{current_cents:.2f} snt/kWh</span>"
            )

        section_title(title_html, mt=10, mb=4)

        df12 = _next_12h_df(prices_today, prices_tomorrow, now_dt=datetime.now(TZ))
        if not df12:
            card(
                "Pörssisähkö",
                "<span class='hint'>Ei dataa vielä seuraaville tunneille</span>",
                height_dvh=16,
            )
            return

        values = [row["cents"] for row in df12]
        colors = _color_by_thresholds(values)
        line_colors = [
            "rgba(255,255,255,0.9)" if row["is_now"] else "rgba(0,0,0,0)"
            for row in df12
        ]
        line_widths = [1.5 if row["is_now"] else 0 for row in df12]

        step = float(max(1, PRICE_Y_STEP_SNT))
        y_min_src = min(values, default=0)
        y_max_src = max(values, default=step)

        # Pyöristetään lähimmille askelille alaspäin ja ylöspäin
        y_min = float(math.floor(y_min_src / step) * step)
        y_max = float(math.ceil(y_max_src / step) * step)

        # Jos kaikki arvot ovat samoja
        if y_max <= y_min:
            y_max = y_min + step

        fig = go.Figure(
            [
                go.Bar(
                    x=[row["hour_label"] for row in df12],
                    y=[round(v, 2) for v in values],
                    marker=dict(
                        color=colors, line=dict(color=line_colors, width=line_widths)
                    ),
                    hovertemplate="<b>%{x}</b><br>%{y} snt/kWh<extra></extra>",
                )
            ]
        )

        fig.update_layout(
            title=None,
            title_x=0,
            title_font_size=14,
            margin=dict(l=60, r=10, t=24, b=44),  # lisätty vasenta tilaa
            xaxis_title=None,
            yaxis_title="snt/kWh",
            height=190,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(gridcolor="rgba(255,255,255,0.08)"),
            yaxis=dict(
                gridcolor="rgba(255,255,255,0.08)",
                range=[y_min, y_max],
                tick0=y_min,
                dtick=step,
                automargin=True,
            ),
        )
        fig.add_hline(y=0, line=dict(color="rgba(255,255,255,0.25)", width=1))

        st.plotly_chart(fig, use_container_width=True, theme=None, config=PLOTLY_CONFIG)
        st.markdown(
            """
            <div class='hint' style='margin-top:0px; margin-bottom:2px;'>
              <span style='color:#00b400;'>&#9632;</span> ≤ 5 snt &nbsp;
              <span style='color:#cccc00;'>&#9632;</span> 5–15 snt &nbsp;
              <span style='color:#dc0000;'>&#9632;</span> ≥ 15 snt &nbsp;
              (vihreä = halpa, punainen = kallis)
            </div>
            """,
            unsafe_allow_html=True,
        )
    except Exception as e:
        section_title("Pörssisähkö – seuraavat 12 h")
        st.markdown(
            f"<span class='hint'>Virhe hinnanhaussa: {e}</span>", unsafe_allow_html=True
        )


# ------------------- BITCOIN CARD -------------------


def card_bitcoin() -> None:
    """Render a card displaying Bitcoin price with selectable history window (24h / 7d / 30d)."""
    try:
        # --- Luetaan valinta URL-kyselyparamista ja pidetään sessiossa ---
        qp = st.query_params
        if "bwin" in qp:
            raw = str(qp.get("bwin")).lower().strip()
            if raw in ("24h", "7d", "30d"):
                st.session_state["btc_window"] = raw

        if "btc_window" not in st.session_state:
            st.session_state["btc_window"] = "7d"  # oletus

        window = st.session_state["btc_window"]  # '24h' | '7d' | '30d'

        # --- Nykyhinta + 24h muutos ---
        btc_data = fetch_btc_eur()
        eur_now = btc_data.get("price")
        change_24h = btc_data.get("change")
        if eur_now is None:
            raise ValueError("Bitcoin-hinnan nouto CoinGeckosta epäonnistui.")

        # --- Apuri: hae aikasarja halutulle ikkunalle robustisti ---
        from datetime import timedelta

        def _get_series(win: str):
            """
            Palauttaa listan (ts, price) aikajärjestyksessä.
            Yrittää useita funktioita. Jos 24h -> slice 7d-datasta tarvittaessa.
            Jos 30d ei saatavilla, palauttaa 7d ja lipun 'degraded'.
            """
            now = datetime.now(TZ)

            def _call_if_exists(fname, *args, **kwargs):
                fn = globals().get(fname)
                if callable(fn):
                    return fn(*args, **kwargs)
                return None

            # ensisijaiset yritykset
            if win == "24h":
                for name in ("fetch_btc_last_24h_eur", "fetch_btc_last_1d_eur"):
                    series = _call_if_exists(name)
                    if series:
                        return series, False
                # geneeriset
                series = _call_if_exists("fetch_btc_last_hours_eur", 24)
                if series:
                    return series, False
                series = _call_if_exists(
                    "fetch_btc_eur_range", None, 24
                )  # esim. (days=None, hours=24)
                if series:
                    return series, False
                # fallback: slice 7d -> 24h
                s7 = _call_if_exists("fetch_btc_last_7d_eur")
                if s7:
                    cutoff = now - timedelta(hours=24)
                    s24 = [(t, v) for (t, v) in s7 if t >= cutoff]
                    if len(s24) >= 2:
                        return s24, False
                    # jos liian vähän pisteitä, palauta silti 7d
                    return s7, True

            if win == "7d":
                for name in ("fetch_btc_last_7d_eur",):
                    series = _call_if_exists(name)
                    if series:
                        return series, False
                # geneerinen
                series = _call_if_exists(
                    "fetch_btc_eur_range", 7, None
                )  # (days=7, hours=None)
                if series:
                    return series, False

            if win == "30d":
                for name in ("fetch_btc_last_30d_eur", "fetch_btc_last_1m_eur"):
                    series = _call_if_exists(name)
                    if series:
                        return series, False
                # geneerinen
                series = _call_if_exists("fetch_btc_eur_range", 30, None)  # (days=30)
                if series:
                    return series, False
                # fallback: jos ei 30d, ota 7d
                s7 = _call_if_exists("fetch_btc_last_7d_eur")
                if s7:
                    return s7, True

            # viimeinen oljenkorsi: koeta 7d
            s7 = _call_if_exists("fetch_btc_last_7d_eur")
            if s7:
                return s7, (win != "7d")
            raise ValueError("BTC-historiasarjaa ei saatu mistään lähteestä.")

        series, degraded = _get_series(window)

        # --- ATH-taso (sama kaikille ikkunoille) ---
        ath_eur, ath_date = fetch_btc_ath_eur()

        xs = [t for t, _ in series]
        ys = [v for _, v in series]

        # --- Otsikon pillerit: aktiivinen = vaalea harmaa, teksti tumma ---
        def pill(opt_code: str, label: str) -> str:
            is_active = opt_code == window
            base = (
                "display:inline-block;margin-left:8px;padding:2px 10px;border-radius:999px;"
                "font-size:.95rem;text-decoration:none;border:1px solid rgba(255,255,255,.18);font-weight:600;"
            )
            if is_active:
                style = base + "background:#e7eaee;color:#111;"
            else:
                style = base + "background:rgba(255,255,255,0.10);color:#e7eaee;"
            return (
                f'<a href="?bwin={opt_code}" target="_self" style="{style}">{label}</a>'
            )

        window_label = {
            "24h": "Viimeiset 24 h",
            "7d": "Viimeiset 7 päivää",
            "30d": "Viimeiset 30 päivää",
        }[window]

        title_html = (
            "🪙 Bitcoin "
            + pill("24h", "24 h")
            + pill("7d", "7 d")
            + pill("30d", "30 d")
        )

        # 24h-muutosbadgi (pidetään kuten ennen)
        if change_24h is not None:
            is_up = change_24h >= 0
            badge_bg = COLOR_GREEN if is_up else COLOR_RED
            sign = "+" if is_up else ""
            change_fmt = f"{sign}{change_24h:.2f}%"
            badge_text = f"{eur_now:,.0f}".replace(",", " ") + f" € {change_fmt} (24 h)"
            title_html += (
                f" <span style='background:{badge_bg}; color:#000; padding:2px 10px; "
                f"border-radius:10px; font-weight:700; font-size:0.95rem'>{badge_text}</span>"
            )

        # Lisätään valitun ikkunan pilleriotsikko harmaalla kapselilla lopuksi
        title_html += (
            f" <span style='background:{COLOR_GRAY}; color:{COLOR_TEXT_GRAY}; padding:2px 10px; "
            "border-radius:999px; font-weight:600; font-size:0.95rem'>"
            f"{window_label}</span>"
        )

        section_title(title_html, mt=10, mb=4)

        # --- Piirretään kuvaaja ---
        # Hover + tickit riippuen ikkunasta
        if window == "24h":
            name = "BTC/EUR (24 h)"
            hover = "%{x|%H:%M} — %{y:.0f} €"
            dtick = 3 * 60 * 60 * 1000  # 3 h millisekunteina
            tickformat = "%H:%M"
        elif window == "30d":
            name = "BTC/EUR (30 d)"
            hover = "%{x|%d.%m} — %{y:.0f} €"
            dtick = "D2"
            tickformat = "%d.%m"
        else:
            name = "BTC/EUR (7 d)"
            hover = "%{x|%d.%m %H:%M} — %{y:.0f} €"
            dtick = "D1"
            tickformat = "%d.%m"

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=xs,
                y=ys,
                mode="lines",
                name=name,
                hovertemplate=hover + "<extra></extra>",
            )
        )

        # ATH katkoviivana
        if ath_eur:
            x0 = xs[0] if xs else datetime.now(TZ)
            x1 = xs[-1] if xs else datetime.now(TZ)
            fig.add_trace(
                go.Scatter(
                    x=[x0, x1],
                    y=[ath_eur, ath_eur],
                    mode="lines",
                    name=f"ATH {ath_eur:,.0f} €",
                    line=dict(dash="dot"),
                    hovertemplate="ATH — %{y:.0f} € (%{x|%d.%m})<extra></extra>",
                )
            )

        # Y-akselin skaalaus kuten ennen
        if ys:
            data_min = min(ys)
            data_max = max(max(ys), ath_eur or -float("inf"))
            pad_abs = (
                max(BTC_Y_PAD_EUR, (data_max - data_min) * BTC_Y_PAD_PCT)
                if BTC_Y_USE_PCT_PAD
                else BTC_Y_PAD_EUR
            )
            low = data_min - pad_abs
            high = data_max + pad_abs
            step = max(100.0, float(BTC_Y_STEP_EUR))
            y_min = int(math.floor(low / step) * step)
            y_max = int(math.ceil(high / step) * step)
            fig.update_yaxes(range=[y_min, y_max], tick0=y_min, dtick=step)
        else:
            fig.update_yaxes(autorange=True)

        # Hintalappu oikeaan reunaan
        if xs and ys:
            label_text = f"{ys[-1]:,.0f}".replace(",", " ") + " €"
            fig.add_annotation(
                x=xs[-1],
                y=ys[-1],
                xref="x",
                yref="y",
                text=label_text,
                showarrow=False,
                xanchor="right",
                align="right",
                xshift=-12,
                font=dict(color="#e7eaee", size=12),
            )

        fig.update_layout(
            margin=dict(l=64, r=12, t=8, b=32),
            height=210,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
            font=dict(size=12, color="#e7eaee"),
            xaxis=dict(
                type="date",
                title=None,
                gridcolor="rgba(255,255,255,0.28)",
                tickformat=tickformat,
                dtick=dtick,
                tickfont=dict(size=11, color="#cfd3d8"),
                automargin=True,
            ),
            yaxis=dict(
                title="€",
                gridcolor="rgba(255,255,255,0.28)",
                tickfont=dict(size=11, color="#cfd3d8"),
                tickformat="~s",
                fixedrange=True,
                automargin=True,
            ),
            hoverlabel=dict(font_size=11),
        )

        st.plotly_chart(fig, use_container_width=True, theme=None, config=PLOTLY_CONFIG)

        # ATH-vihje + mahdollinen degradaatioilmoitus
        ath_info = (
            f" {ath_date[:10]}, {ath_eur:,.0f} €".replace(",", " ")
            if ath_eur and ath_date
            else ""
        )
        extra = ""
        if window == "30d" and degraded:
            extra = " &nbsp;|&nbsp; Näytetään 7 d (30 d data ei saatavilla)"
        if window == "24h" and degraded:
            extra = " &nbsp;|&nbsp; Viimeiset 24 h viipaloitu 7 d -datasta"
        st.markdown(
            f"<div class='hint' style='margin-top:4px;'>💎 ATH{ath_info} (pun. katkoviiva){extra}</div>",
            unsafe_allow_html=True,
        )
        st.markdown("<div style='margin-top:6px;'></div>", unsafe_allow_html=True)

    except Exception as e:
        card("Bitcoin (EUR)", f"<span class='hint'>Virhe: {e}</span>", height_dvh=18)


# ------------------- SYSTEM STATUS CARD -------------------


def card_system() -> None:
    """Render a system status card incl. device/browser info (no debug box, no UA dump)."""
    try:
        section_title("🖥️ Järjestelmätila", mt=10, mb=4)

        ip_addr = get_ip()
        now_str = datetime.now(TZ).strftime("%H:%M:%S")

        html = f"""
<!doctype html>
<html><head><meta charset="utf-8">
<style>
  :root {{
    --fg:#e7eaee;
    --bg:rgba(255,255,255,0.04);
    --bd:rgba(255,255,255,0.08);
    --fg-hint:rgba(231,234,238,0.8);
  }}
  html,body {{ margin:0; padding:0; background:transparent; color:var(--fg);
               font-family:ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,Ubuntu; }}
  .card {{ position:relative; overflow:hidden; border-radius:14px; background:var(--bg); border:1px solid var(--bd); }}
  .card-body {{ padding:8px 12px 10px 12px; }}
  .grid {{ display:grid; grid-template-columns:auto 1fr; gap:4px 10px; align-items:center;
           font-size:.92rem; line-height:1.25; }}
  .hint {{ color:var(--fg-hint); }}
  .muted {{ opacity:.7; font-size:.85rem; padding-top:2px; }}
</style>
</head><body>
  <section class="card">
    <div class="card-body">
      <div class="grid" style="margin-bottom:4px;">
        <div class="hint">IP:</div><div>{ip_addr}</div>
        <div class="hint">Päivitetty:</div><div>{now_str}</div>
        <div class="hint">Kioskitila:</div><div>Fully Kiosk Browser</div>
      </div>

      <div id="device-info" class="grid muted" style="margin-top:6px;">
        <div class="muted">Kerätään laitteen tietoja…</div><div></div>
      </div>
    </div>
  </section>

<script>
window.addEventListener('DOMContentLoaded', function () {{
  // DEBUG pois päältä: ei näytetä mitään debug-tekstiä tai laatikkoa
  var ENABLE_DEBUG = false;

  function debugLog(msg) {{
    if (!ENABLE_DEBUG) return;
    // (ei debug-laatikkoa enää)
  }}

  var target = document.getElementById('device-info');

  function show(rows) {{
    var html = "";
    for (var i=0;i<rows.length;i++) {{
      html += "<div class='hint'>" + rows[i][0] + ":</div><div>" + rows[i][1] + "</div>";
    }}
    target.innerHTML = html;
  }}

  try {{
    var ua = navigator.userAgent || "";
    var platform = navigator.platform || "—";
    var lang = (navigator.languages && navigator.languages[0]) || navigator.language || "—";
    var dpr = (window.devicePixelRatio || 1);
    var vw = Math.round(window.innerWidth || 0);
    var vh = Math.round(window.innerHeight || 0);
    var sw = (screen && screen.width) ? screen.width : 0;
    var sh = (screen && screen.height) ? screen.height : 0;

    function isOnePlus(str) {{ return /OnePlus/i.test(str) || /CPH25\\d{{2}}|CPH24\\d{{2}}|CPH23\\d{{2}}/i.test(str); }}
    var isOP = isOnePlus(ua);

    function detectOS() {{
      if (ua.indexOf("Windows NT") > -1) {{
        var m = /Windows NT (\\d+\\.\\d+)/.exec(ua);
        var name = "Windows";
        if (m && m[1] && m[1].indexOf("10.0") === 0) {{
          var v = (/Edg\\/(\\d+)/.exec(ua) || /Chrome\\/(\\d+)/.exec(ua) || [,"0"])[1];
          name = (parseInt(v,10) >= 95) ? "Windows 11" : "Windows 10";
        }}
        var is64 = /Win64|x64|WOW64/i.test(ua);
        return name + " " + (is64 ? "(64-bit)" : "(32-bit)");
      }}
      if (/CrOS/i.test(ua)) return "ChromeOS";
      if (/iPhone|iPod/i.test(ua)) return "iOS";
      if (/iPad/i.test(ua) || (ua.indexOf("Macintosh")>-1 && 'ontouchend' in document)) return "iPadOS";
      if (/Android/i.test(ua)) {{
        var av = /Android\\s([\\d\\.]+)/i.exec(ua);
        var ver = av ? av[1] : "";
        var androidStr = ver ? ("Android " + ver) : "Android";
        if (isOP) androidStr += " (OxygenOS)";
        return androidStr;
      }}
      if (/Mac OS X|Macintosh/i.test(ua)) return "macOS";
      if (/Linux/i.test(ua)) {{
        if (/aarch64|arm64/i.test(ua)) return "Linux (ARM64)";
        if (/armv7|armv8/i.test(ua)) return "Linux (ARM)";
        return "Linux";
      }}
      return navigator.platform || "Tuntematon";
    }}

    var isAndroid = /Android/i.test(ua);
    var isIPad = /iPad/i.test(ua) || (ua.indexOf("Macintosh")>-1 && 'ontouchend' in document);
    var isPhoneHint = /(Mobile|Android.*Mobile|Phone)/i.test(ua);
    var isTV = /(SmartTV|TV|BRAVIA|AFT[BMT]|AppleTV|Tizen|Web0S)/i.test(ua);
    var isTablet = isIPad || (isAndroid && !isPhoneHint && !isTV);
    var deviceType = isTablet ? "Tablet" : (isPhoneHint ? "Puhelin" : "Tietokone");

    var b = (/(Edg|OPR|Chrome|Firefox|Safari)/i.exec(ua) || ["","Tuntematon"])[1];
    if (b === "OPR") b = "Opera";
    if (b === "Edg") b = "Edge";

    var osLabel = detectOS();

    var deviceName = "—";
    if (isOP) {{
      var match = /CPH(25[78][0135]|24[58][17]|23\\d{{2}})/i.exec(ua);
      if (match) {{
        var code = match[0].toUpperCase();
        if (/CPH2581|CPH2573|CPH2575/i.test(code)) deviceName = "OnePlus 12";
        else if (/CPH2487|CPH2451/i.test(code)) deviceName = "OnePlus 11";
        else deviceName = code;
      }} else {{
        deviceName = "OnePlus";
      }}
    }}

    // HUOM: EI User-Agent -riviä
    var rows = [
      ["Laitetyyppi", deviceType],
      ["Käyttöjärjestelmä", osLabel],
      ["Selain", b],
      ["Kieli", lang],
      ["DPR", String(dpr)],
      ["Viewport", vw + "&times;" + vh],
      ["Resoluutio", sw + "&times;" + sh],
      ["Laite", deviceName]
    ];
    show(rows);

    if (navigator.userAgentData && navigator.userAgentData.getHighEntropyValues) {{
      navigator.userAgentData.getHighEntropyValues(['platform','platformVersion','model','fullVersionList'])
        .then(function (d) {{
          var os = osLabel;
          var platform = (d.platform || '').toLowerCase();
          var model = (d.model || '').trim();
          var major = parseInt(String(d.platformVersion || '').split('.')[0] || '', 10);

          if (platform === 'android' && !isNaN(major)) {{
            os = "Android " + major + (isOnePlus(model) ? " (OxygenOS)" : "");
            var labels = Array.prototype.slice.call(document.querySelectorAll('#device-info .hint'));
            for (var i=0; i<labels.length; i++) {{
              var key = labels[i].textContent.replace(':','').trim();
              if (key === "Käyttöjärjestelmä") {{
                var valEl = labels[i].nextElementSibling;
                if (valEl) valEl.innerHTML = os;
              }}
              if (key === "Laite" && model && model !== 'Android SDK built for x86') {{
                var mEl = labels[i].nextElementSibling;
                if (mEl) mEl.innerHTML = model;
              }}
            }}
          }}
        }});
    }}
  }} catch (err) {{
    target.innerHTML = "<div class='hint'>Virhe:</div><div>" + (err && err.message ? err.message : String(err)) + "</div>";
  }}
}});
</script>
</body></html>
"""
        # laatikkoa ei tarvita korkeaksi enää
        st_html(html, height=240, scrolling=False)

    except Exception as e:
        section_title("🖥️ Järjestelmätila")
        st.markdown(f"<span class='hint'>Virhe: {e}</span>", unsafe_allow_html=True)
