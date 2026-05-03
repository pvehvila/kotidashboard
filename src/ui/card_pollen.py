from __future__ import annotations

import html

import streamlit as st

from src.api.pollen import fetch_pollen_view
from src.ui.common import card, section_title

LEVEL_CLASS = {
    "ei havaittu": "none",
    "vähän": "low",
    "kohtalaisesti": "medium",
    "runsaasti": "high",
}


def card_pollen() -> None:
    """Renderöi Riihimäen siitepölytilanteen."""
    try:
        vm = fetch_pollen_view()
        section_title("🌿 Siitepöly — Riihimäki", mt=10, mb=4)
        st.markdown(_render_pollen_html(vm), unsafe_allow_html=True)
    except Exception as e:
        card("Siitepöly — Riihimäki", f"<span class='hint'>Virhe: {html.escape(str(e))}</span>")


def _render_pollen_html(vm: dict) -> str:
    rows = "".join(_render_plant_row(plant) for plant in vm.get("plants", []))

    return f"""
    <section class="card pollen-card" style="height:200px;">
      <style>
        .pollen-card .card-body {{ padding:8px 12px 10px 12px; }}
        .pollen-grid {{ display:grid; gap:6px; }}
        .pollen-row {{
          display:grid; grid-template-columns:1fr 112px 112px; gap:8px;
          align-items:center; min-height:36px; padding:6px 10px; border-radius:8px;
          background:rgba(255,255,255,.06);
        }}
        .pollen-header {{
          min-height:auto; padding:0 10px 2px; background:transparent;
          color:#aab3c2; font-size:.78rem; font-weight:700;
        }}
        .pollen-name {{ font-weight:700; font-size:.92rem; }}
        .pollen-level {{
          text-align:center; border-radius:999px; padding:4px 8px;
          font-size:.86rem; font-weight:700; border:1px solid rgba(255,255,255,.18);
        }}
        .pollen-level.none {{ background:#26313a; color:#cbd5e1; }}
        .pollen-level.low {{ background:#14532d; color:#dcfce7; }}
        .pollen-level.medium {{ background:#854d0e; color:#fef3c7; }}
        .pollen-level.high {{ background:#7f1d1d; color:#fee2e2; }}
      </style>
      <div class="card-body">
        <div class="pollen-grid">
          <div class="pollen-row pollen-header">
            <div>Allergeeni</div><div>Nyt</div><div>Ennuste</div>
          </div>
          {rows}
        </div>
      </div>
    </section>
    """


def _render_plant_row(plant: dict) -> str:
    name = html.escape(str(plant.get("name") or ""))
    level = html.escape(str(plant.get("level") or "ei havaittu"))
    forecast_level_raw = str(plant.get("forecast_level") or "ei havaittu")
    forecast_level = html.escape(forecast_level_raw)
    level_class = LEVEL_CLASS.get(str(plant.get("level")), "none")
    forecast_level_class = LEVEL_CLASS.get(forecast_level_raw, "none")

    return f"""
    <div class="pollen-row">
      <div class="pollen-name">{name}</div>
      <div class="pollen-level {level_class}">{level}</div>
      <div class="pollen-level {forecast_level_class}">{forecast_level}</div>
    </div>
    """
