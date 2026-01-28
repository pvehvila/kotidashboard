from __future__ import annotations

import base64
import html

import streamlit as st

from src.api.home_assistant import HAConfigError, fetch_eqe_status
from src.paths import asset_path
from src.ui.common import section_title


def _get_eqe_background() -> str:
    """Palauttaa EQE-taustakuvan data-URLina, jos löytyy assets-hakemistosta."""
    name = "mercedes-benz-eqe-2023_00_original.jpg"
    p = asset_path(name)
    if not p.exists():
        return ""
    b64 = base64.b64encode(p.read_bytes()).decode("ascii")
    return f"data:image/jpeg;base64,{b64}"


def _fmt_value(value: float | None, unit: str | None, digits: int = 0) -> str:
    if value is None:
        return "<span class='hint'>—</span>"
    if digits <= 0:
        num = f"{value:.0f}"
    else:
        num = f"{value:.{digits}f}"
    unit_html = f"<span class='eqe-unit'>{html.escape(unit)}</span>" if unit else ""
    return f"{num}{unit_html}"


def _charging_chip(state: str | None) -> tuple[str, str]:
    if not state:
        return ("chip yellow", "Tuntematon")
    state_lower = state.lower()
    if "lataa" in state_lower or state_lower in ("charging", "on"):
        return ("chip green", state)
    if "ei" in state_lower or state_lower in ("idle", "off"):
        return ("chip orange", state)
    return ("chip yellow", state)


def card_eqe() -> None:
    """Render Mercedes EQE -kortti Home Assistant -datalla."""
    section_title("🚗 Mercedes EQE", mt=10, mb=4)
    try:
        vm = fetch_eqe_status()
        soc_html = _fmt_value(vm.soc_pct, vm.soc_unit or "%", digits=0)
        range_html = _fmt_value(vm.range_km, vm.range_unit or "km", digits=0)
        chip_class, chip_text = _charging_chip(vm.charging_state)
        updated = vm.last_changed.strftime("%H:%M") if vm.last_changed else "—"

        bg = _get_eqe_background()
        overlay = "linear-gradient(90deg, rgba(11,15,20,0.70) 0%, rgba(11,15,20,0.10) 72%)"
        bg_layer = f"{overlay}, url('{bg}')" if bg else overlay

        body = f"""
        <div class="eqe-grid">
          <div class="eqe-item">
            <div class="eqe-label">SoC</div>
            <div class="eqe-value">{soc_html}</div>
          </div>
          <div class="eqe-item">
            <div class="eqe-label">Range</div>
            <div class="eqe-value">{range_html}</div>
          </div>
          <div class="eqe-item">
            <div class="eqe-label">Charging</div>
            <div class="eqe-value"><span class="{chip_class}">{html.escape(chip_text)}</span></div>
          </div>
        </div>
        """
        st.markdown(
            f"""
            <section class="card eqe-card" style="background-image:{bg_layer}; background-size:cover; background-position:center;">
              <div class="card-body">{body}</div>
            </section>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<div class='hint' style='margin-top:4px;'>Päivitetty: {html.escape(updated)}</div>",
            unsafe_allow_html=True,
        )

    except HAConfigError as e:
        st.markdown(
            f"""
            <section class="card" style="min-height:12dvh;">
              <div class="card-body"><span class="hint">{html.escape(str(e))}</span></div>
            </section>
            """,
            unsafe_allow_html=True,
        )
    except Exception as e:
        st.markdown(
            f"""
            <section class="card" style="min-height:12dvh;">
              <div class="card-body"><span class="hint">Virhe: {html.escape(str(e))}</span></div>
            </section>
            """,
            unsafe_allow_html=True,
        )
