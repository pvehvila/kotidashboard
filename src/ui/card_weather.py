# src/ui/card_weather.py
from __future__ import annotations

import streamlit as st
from streamlit.components.v1 import html as st_html

from src.api import fetch_weather_points
from src.config import LAT, LON
from src.ui.common import section_title, card
from src.weather_icons import render_foreca_icon


def card_weather() -> None:
    """Render a card displaying weather forecast for Riihimäki (1h/3h/6h)."""
    try:
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

        weather_data = fetch_weather_points(
            LAT, LON, "Europe/Helsinki", offsets=offsets
        )
        points = weather_data["points"]
        min_temp = weather_data["min_temp"]
        max_temp = weather_data["max_temp"]

        title_left = "🌤️ Sää — Riihimäki"
        if (min_temp is not None) and (max_temp is not None):
            title_left += (
                f"&nbsp; | &nbsp; Tänään: {round(min_temp)}°C — {round(max_temp)}°C"
            )

        def pill(opt: str) -> str:
            is_active = opt == interval
            wint = opt.replace(" ", "")
            base_style = (
                "display:inline-block;margin-left:8px;padding:2px 8px;border-radius:8px;"
                "font-size:.85rem;text-decoration:none;border:1px solid rgba(255,255,255,.18);"
            )
            if is_active:
                style = base_style + "background:#e7eaee;color:#111;"
            else:
                style = base_style + "background:rgba(255,255,255,0.10);color:#e7eaee;"
            return f'<a href="?wint={wint}" target="_self" style="{style}">{opt}</a>'

        pills_html = "".join(pill(opt) for opt in ("1 h", "3 h", "6 h"))
        full_title_html = f"{title_left}&nbsp;&nbsp;{pills_html}"
        section_title(full_title_html, mb=3)

        def cell(point: dict) -> str:
            icon_html = render_foreca_icon(point["key"], size=48)
            temp = "—" if point["temp"] is None else f"{round(point['temp'])}"
            pop = "—" if point["pop"] is None else f"{point['pop']}%"
            return f"""
                <div class="weather-cell">
                  <div class="label">{point["label"]}</div>
                  <div class="sub">{point["hour"]}:00</div>
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
        card("Sää — Riihimäki", f"<span class='hint'>Virhe: {e}</span>", height_dvh=15)
