from __future__ import annotations

import base64
import html
import time

import streamlit as st

from src.api.home_assistant import HAConfigError, fetch_eqe_status, set_eqe_preclimate
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


def _get_mercedes_logo_svg_data() -> str:
    """Palauttaa Mercedes-logo-SVG data-URLina, jos löytyy assets-hakemistosta."""
    p = asset_path("Mercedes-Benz_Star.svg")
    if not p.exists():
        return ""
    b64 = base64.b64encode(p.read_bytes()).decode("ascii")
    return f"data:image/svg+xml;base64,{b64}"


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


def _lock_chip(state: str | None) -> tuple[str, str]:
    if not state:
        return ("chip yellow", "Tuntematon")
    state_lower = state.lower()
    if "lukossa" in state_lower or state_lower in ("locked", "on", "true"):
        return ("chip green", state)
    if "auki" in state_lower or state_lower in ("unlocked", "off", "false"):
        return ("chip orange", state)
    return ("chip yellow", state)


def _preclimate_chip(state: str | None) -> tuple[str, str]:
    if not state:
        return ("chip yellow", "Käynnistä")
    state_lower = state.lower()
    if "käynnissä" in state_lower or state_lower in ("on", "active", "running", "true"):
        return ("chip green", state)
    return ("chip yellow", state)


def _preclimate_is_on(state: str | None) -> bool:
    if not state:
        return False
    state_lower = state.lower()
    return state_lower in ("on", "active", "running", "true", "käynnissä")


def card_eqe() -> None:
    """Render Mercedes EQE -kortti Home Assistant -datalla."""
    logo = _get_mercedes_logo_svg_data()
    if logo:
        title_html = (
            "<span style='display:inline-flex; align-items:center; gap:6px;'>"
            f"<img src='{logo}' alt='Mercedes' "
            "style='width:16px; height:16px; vertical-align:middle; filter:drop-shadow(0 1px 1px rgba(0,0,0,0.35));'/>"
            "Mercedes EQE</span>"
        )
    else:
        title_html = "Mercedes EQE"
    section_title(title_html, mt=10, mb=4)
    try:
        action_raw = st.query_params.get("eqe_preclimate")
        if isinstance(action_raw, list):
            action = (action_raw[0] if action_raw else "") or ""
        else:
            action = action_raw or ""
        action = str(action).lower()
        if action:
            action_on = action == "on"
            try:
                set_eqe_preclimate(action_on)
                fetch_eqe_status.clear()
                st.session_state["eqe_preclimate_msg"] = (
                    "ok",
                    "Ilmastointi käynnistetään" if action_on else "Ilmastointi sammutetaan",
                )
                time.sleep(0.8)
            except Exception as e:
                st.session_state["eqe_preclimate_msg"] = (
                    "err",
                    f"Ilmastoinnin ohjaus epäonnistui: {e}",
                )
            try:
                del st.query_params["eqe_preclimate"]
            except Exception:
                st.query_params.clear()
            st.rerun()

        vm = fetch_eqe_status()
        soc_html = _fmt_value(vm.soc_pct, vm.soc_unit or "%", digits=0)
        range_html = _fmt_value(vm.range_km, vm.range_unit or "km", digits=0)
        chip_class, chip_text = _charging_chip(vm.charging_state)
        lock_class, lock_text = _lock_chip(vm.lock_state)
        preclimate_class, preclimate_text = _preclimate_chip(vm.preclimate_state)
        preclimate_on = _preclimate_is_on(vm.preclimate_state)
        power_html = _fmt_value(vm.charging_power_kw, vm.charging_power_unit or "kW", digits=1)
        updated = vm.last_changed.strftime("%H:%M") if vm.last_changed else "—"

        bg = _get_eqe_background()
        overlay = "linear-gradient(90deg, rgba(11,15,20,0.70) 0%, rgba(11,15,20,0.10) 72%)"
        bg_layer = f"{overlay}, url('{bg}')" if bg else overlay

        preclimate_action = "off" if preclimate_on else "on"
        preclimate_html = (
            "<form method='get' style='margin:0; display:inline;'>"
            f"<button class='eqe-switch' type='submit' "
            f"name='eqe_preclimate' value='{preclimate_action}'>"
            f"<span class='{preclimate_class}'>{html.escape(preclimate_text)}</span>"
            "</button></form>"
        )

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
          <div class="eqe-item">
            <div class="eqe-label">Lukitus</div>
            <div class="eqe-value"><span class="{lock_class}">{html.escape(lock_text)}</span></div>
          </div>
          <div class="eqe-item">
            <div class="eqe-label">Ilmastointi</div>
            <div class="eqe-value">{preclimate_html}</div>
          </div>
          <div class="eqe-item">
            <div class="eqe-label">Latausteho</div>
            <div class="eqe-value">{power_html}</div>
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
        msg = st.session_state.pop("eqe_preclimate_msg", None)
        if msg:
            kind, text = msg
            if kind == "err":
                st.error(text)
            else:
                st.markdown(f"<div class='hint'>{html.escape(text)}</div>", unsafe_allow_html=True)
        st.markdown(
            f"<div class='hint' style='margin-top:16px; margin-bottom:2px;'>Päivitetty: {html.escape(updated)}</div>",
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
