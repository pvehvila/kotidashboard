from __future__ import annotations

import base64
from datetime import datetime
from pathlib import Path

import streamlit as st

from src.api import fetch_holiday_today, fetch_nameday_today
from src.config import HOLIDAY_PATHS, LAT, LON, NAMEDAY_PATHS, TZ
from src.paths import asset_path
from src.ui.common import card
from src.utils_sun import _sun_icon, fetch_sun_times


def card_nameday() -> None:
    try:
        p_names = next((p for p in NAMEDAY_PATHS if Path(p).exists()), None)
        mtime_names = Path(p_names).stat().st_mtime_ns if p_names else 0
        p_holidays = next((p for p in HOLIDAY_PATHS if Path(p).exists()), None)
        mtime_holidays = Path(p_holidays).stat().st_mtime_ns if p_holidays else 0

        names = fetch_nameday_today(_cache_buster=mtime_names) or "—"
        hol = fetch_holiday_today(_cache_buster=max(mtime_names, mtime_holidays)) or {}

        # jos holiday tuli avaimella "name", muunna se vanhaan muotoon
        if "holiday" not in hol and "name" in hol:
            hol["holiday"] = hol["name"]

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
        title_text = f"Nimipäivät<br>{weekdays_fi[now.weekday()]} {now.day}.{now.month}."

        bg_dataurl = None
        for fname in ("butterfly-bg.png", "butterfly-bg.webp", "butterfly-bg.jpg"):
            path = asset_path(fname)
            if path.exists():
                mime = {"png": "image/png", "webp": "image/webp", "jpg": "image/jpeg"}[
                    path.suffix.lstrip(".")
                ]
                bg_dataurl = f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode(
                    "ascii"
                )
                break

        overlay_css = "linear-gradient(90deg, rgba(11,15,20,0.65) 0%, rgba(11,15,20,0.25) 45%, rgba(11,15,20,0.00) 70%)"
        bg_css = overlay_css + (f", url({bg_dataurl})" if bg_dataurl else "")

        is_flag = bool(hol.get("is_flag_day"))
        is_hday = bool(hol.get("is_holiday"))
        holiday_name = (hol.get("holiday") or "").strip()
        has_status = is_flag or is_hday

        status_html = ""
        if has_status:
            flag_svg = (
                "<svg xmlns='http://www.w3.org/2000/svg' width='22' height='16' viewBox='0 0 22 16' aria-label='Suomen lippu' style='flex:0 0 auto;'>"
                "<rect width='22' height='16' fill='#ffffff'/>"
                "<rect x='0' y='6' width='22' height='4' fill='#003580'/>"
                "<rect x='6' y='0' width='4' height='16' fill='#003580'/>"
                "</svg>"
            )
            if is_flag and is_hday:
                label_html = f"{flag_svg}<strong>Liputus- ja lomapäivä:</strong> {holiday_name}"
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

        names_html = (
            "<div style='font-size:1.35rem; font-weight:800; "
            f"margin:{'4px 0 6px 0' if has_status else '0 0 6px 0'}; "
            "color:#fff; text-shadow: 0 1px 2px rgba(0,0,0,.45);'>"
            f"{names}</div>"
        )

        sr, ss = fetch_sun_times(LAT, LON, TZ.key)
        sun_html = ""
        if sr or ss:
            style_pill = (
                "display:inline-flex;align-items:center;gap:6px;padding:4px 10px;border-radius:999px;"
                "background:rgba(255,255,255,.12);backdrop-filter:blur(2px);margin-right:8px;"
                "font-size:.95rem;line-height:1;color:#fff;"
            )
            rise = f"<span style='{style_pill}'>{_sun_icon('rise', 18)}<strong>{sr or '—'}</strong></span>"
            sett = f"<span style='{style_pill}'>{_sun_icon('set', 18)}<strong>{ss or '—'}</strong></span>"
            sun_html = f"<div style='margin:2px 0 6px 0;'>{rise}{sett}</div>"

        meta_html = ""
        if (not is_flag and not is_hday) and holiday_name:
            meta_html = (
                "<div class='meta' style='margin-top:6px; font-size:.95rem; opacity:.95;'>"
                "<span style='display:inline-block; padding:4px 8px; border-radius:999px; "
                "background:rgba(255,255,255,.10); color:#fff;'>"
                f"{holiday_name}</span></div>"
            )

        html = f"""
        <section class="card card-top-equal"
         style="height:180px; position:relative; overflow:hidden;
                background-image:{bg_css}; background-size:cover; background-position:center;">
          <div class="card-body" style="display:flex; align-items:flex-start; text-align:left; padding:10px 16px 12px 16px;">
            <div style="font-size:1.0rem; line-height:1.2; margin:0; color:#fff; text-shadow: 0 1px 2px rgba(0,0,0,.45); width:100%;">
              {status_html}
              <div class="card-title" style="margin:{'6px 0 0 0' if has_status else '0'}; color:#f2f4f7;">
                {title_text}
              </div>
              {names_html}
              {sun_html}
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
