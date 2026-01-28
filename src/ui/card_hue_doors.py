from __future__ import annotations

import html

import streamlit as st

from src.api.hue_contacts_v2 import HueV2ConfigError
from src.ui.common import section_title
from src.viewmodels.hue_contacts import WANTED_DOORS, DoorRow, load_hue_contacts_viewmodel


def _bg_color_for_role(role: str) -> str:
    """Valitsee taustavärin roolin mukaan."""
    if role == "closed":
        # tumma vihreä
        return "linear-gradient(135deg,#064e3b,#022c22)"
    if role == "open":
        # tumma keltainen / meripihka
        return "linear-gradient(135deg,#854d0e,#451a03)"
    if role == "stale":
        # hieman varoitus-oranssi
        return "linear-gradient(135deg,#7c2d12,#431407)"
    # unknown
    return "var(--panel)"


def _icon_for_row(row: DoorRow) -> str:
    """Valitsee ovikohtaisen ikonin tilan mukaan."""
    if row.bg_role == "open":
        return "🚪🔓"
    if row.bg_role == "closed":
        return "🚪🔒"
    if row.bg_role == "stale":
        return "🚪⏳"
    return "🚪❔"


def _render_door_card(row: DoorRow) -> None:
    """Piirtää yksittäisen oven kortin."""
    bg = _bg_color_for_role(row.bg_role)
    icon = _icon_for_row(row)
    title = html.escape(row.name)
    status = html.escape(row.status_label)
    idle = html.escape(row.idle_for_str)

    st.markdown(
        f"""
        <div class="card" style="background:{bg}; margin-top:8px;">
          <div class="card-title">{icon} {title}</div>
          <div class="card-body">
            <p>{status}</p>
            <p><small>Viimeisin muutos: {idle}</small></p>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def card_hue_doors() -> None:
    """Alarivi: ovikontaktit kolmena erillisenä korttina + Hue Secure -health."""

    bridge_ok = True
    error_text = ""

    try:
        rows = load_hue_contacts_viewmodel()
    except HueV2ConfigError as e:  # konfiguraatio- / key-ongelma
        bridge_ok = False
        error_text = str(e)
        rows = [
            DoorRow(
                name=name,
                status_label="Hue Secure -konfiguraatio puuttuu",
                idle_for_str="ei dataa",
                bg_role="unknown",
            )
            for name in WANTED_DOORS
        ]
    except Exception as e:  # pragma: no cover (yleinen häiriötilanne)
        bridge_ok = False
        error_text = str(e)
        rows = [
            DoorRow(
                name=name,
                status_label="Ei yhteyttä Hue Bridgeen",
                idle_for_str="ei dataa",
                bg_role="unknown",
            )
            for name in WANTED_DOORS
        ]

    # Otsikko samaan tyyliin kuin muut kortit
    section_title("🚪 Ovien tila", mt=14, mb=4)

    # Hue Secure / v2 health chip
    if bridge_ok:
        st.markdown(
            '<div class="chip green" style="margin-bottom:14px;">Hue Secure: OK</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div class="chip red" style="margin-bottom:14px;">Hue Secure: OFFLINE</div>
            <p style="margin-top:-6px;"><small>{html.escape(error_text)}</small></p>
            """,
            unsafe_allow_html=True,
        )

    # Lisää tilaa statuschipin ja ovikorttien väliin
    st.markdown('<div style="height:6px;"></div>', unsafe_allow_html=True)

    # Oletus: kolme ovea → kolme kolumnia; zip leikkaa ylimääräiset pois jos rivejä vähemmän
    col1, col2, col3 = st.columns(3, gap="small")
    cols = [col1, col2, col3]

    for col, row in zip(cols, rows, strict=False):
        with col:
            _render_door_card(row)

    # pieni väli dashboardin alareunaan
    st.markdown('<div class="rowgap"></div>', unsafe_allow_html=True)
