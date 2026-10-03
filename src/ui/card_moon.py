from __future__ import annotations

from base64 import b64encode
from datetime import date, datetime, timezone
from functools import lru_cache
from math import cos, pi

import streamlit as st

from src.config import TZ
from src.paths import asset_path
from src.ui.common import section_title

SYNODIC_MONTH_DAYS = 29.530588853
NEW_MOON_REFERENCE = datetime(2000, 1, 6, 18, 14, tzinfo=timezone.utc)
PHASES = (
    ("Uusikuu", "🌑"),
    ("Kasvava sirppi", "🌒"),
    ("Ensimmäinen neljännes", "🌓"),
    ("Kasvava kuperakuu", "🌔"),
    ("Täysikuu", "🌕"),
    ("Vähenevä kuperakuu", "🌖"),
    ("Viimeinen neljännes", "🌗"),
    ("Vähenevä sirppi", "🌘"),
)


def get_moon_view(day: date | None = None) -> dict:
    """Arvioi päivän kuun vaiheen keskimääräisen synodisen kuukauden avulla."""
    day = day if day is not None else datetime.now(TZ).date()
    noon = datetime(day.year, day.month, day.day, 12, tzinfo=TZ)
    elapsed_days = (noon - NEW_MOON_REFERENCE).total_seconds() / 86400
    phase = (elapsed_days / SYNODIC_MONTH_DAYS) % 1
    name, icon = PHASES[int(phase * 8 + 0.5) % 8]
    return {
        "day": day,
        "name": name,
        "icon": icon,
        "phase": phase,
        "illumination": round((1 - cos(2 * pi * phase)) * 50),
    }


def card_moon() -> None:
    """Renderöi päivittäin vaihtuvan kuun vaiheen siitepölykortin kokoisena."""
    vm = get_moon_view()
    section_title("🌙 Kuun vaihe", mt=10, mb=4)
    st.markdown(_render_moon_html(vm), unsafe_allow_html=True)


def _render_moon_html(vm: dict) -> str:
    day = vm["day"]
    moon = _render_moon_svg(vm["phase"])
    return f"""
    <section class="card moon-card" style="height:200px;">
      <div class="card-body" style="height:100%;box-sizing:border-box;display:flex;
           align-items:center;justify-content:center;gap:24px;padding:10px 16px;">
        <div role="img" aria-label="{vm['name']}"
             style="width:180px;max-width:45%;flex-shrink:0;">{moon}</div>
        <div style="min-width:0;">
          <div class="hint">{day.day}.{day.month}.{day.year}</div>
          <div style="font-size:1.25rem;font-weight:700;margin:6px 0;">{vm['illumination']} %</div>
          <div>{vm['name']}</div>
        </div>
      </div>
    </section>
    """


@lru_cache(maxsize=1)
def _moon_image_uri() -> str:
    encoded = b64encode(asset_path("moon-full.jpg").read_bytes()).decode("ascii")
    return f"data:image/jpeg;base64,{encoded}"


def _moon_light_path(phase: float) -> str:
    """Projisoi pallon valaistun puoliskon ympyrän ja ellipsin rajaamaksi alueeksi."""
    phase %= 1
    waxing = phase < 0.5
    terminator = cos(2 * pi * phase)
    radius = abs(terminator) * 90
    outer_sweep = 1 if waxing else 0
    inner_sweep = int((terminator < 0) == waxing)
    boundary = "L 100 10" if radius < 0.0001 else f"A {radius:.4f} 90 0 0 {inner_sweep} 100 10"
    return f"M 100 10 A 90 90 0 0 {outer_sweep} 100 190 {boundary} Z"


def _render_moon_svg(phase: float) -> str:
    image_uri = _moon_image_uri()
    light_path = _moon_light_path(phase)
    return f"""
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200"
         style="display:block;width:100%;height:auto;" aria-hidden="true">
      <defs>
        <filter id="moon-warm" color-interpolation-filters="sRGB">
          <feComponentTransfer>
            <feFuncR type="linear" slope="1"/>
            <feFuncG type="linear" slope="0.90"/>
            <feFuncB type="linear" slope="0.65"/>
          </feComponentTransfer>
        </filter>
        <g id="moon-surface" filter="url(#moon-warm)">
          <svg x="10" y="10" width="180" height="180" viewBox="373 37 790 790">
            <image href="{image_uri}" width="1536" height="864"/>
          </svg>
        </g>
        <clipPath id="moon-disc"><circle cx="100" cy="100" r="90"/></clipPath>
        <clipPath id="moon-light"><path d="{light_path}"/></clipPath>
        <filter id="moon-shadow" color-interpolation-filters="sRGB">
          <feComponentTransfer>
            <feFuncR type="linear" slope="0.09"/>
            <feFuncG type="linear" slope="0.09"/>
            <feFuncB type="linear" slope="0.09"/>
          </feComponentTransfer>
        </filter>
      </defs>
      <g clip-path="url(#moon-disc)">
        <use href="#moon-surface" filter="url(#moon-shadow)"/>
        <use href="#moon-surface" clip-path="url(#moon-light)"/>
      </g>
    </svg>
    """
