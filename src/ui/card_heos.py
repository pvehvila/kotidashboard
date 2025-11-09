# src/ui/card_heos.py
from __future__ import annotations

import streamlit as st

from src.config import HEOS_HOST, HEOS_USERNAME, HEOS_PASSWORD, HEOS_PLAYER_ID
from src.heos_client import HeosClient
from src.ui.common import section_title


def card_heos() -> None:
    section_title("🎧 HEOS / Tidal", mt=10, mb=4)

    client = HeosClient(HEOS_HOST, username=HEOS_USERNAME, password=HEOS_PASSWORD)
    client.sign_in()

    # ohjausnapit
    c1, c2, c3 = st.columns(3)
    if c1.button("⏮️", help="Edellinen kappale"):
        client.play_previous(HEOS_PLAYER_ID)
        try:
            st.rerun()
        except AttributeError:
            st.experimental_rerun()

    if c2.button("⏯️", help="Mykistä / palauta ääni"):
        paused_key = "heos_paused"
        vol_key = "heos_prev_volume"
        if not st.session_state.get(paused_key):
            current_vol = client.get_volume(HEOS_PLAYER_ID)
            st.session_state[vol_key] = current_vol
            client.set_mute(HEOS_PLAYER_ID, "on")
            st.session_state[paused_key] = True
        else:
            prev_vol = st.session_state.get(vol_key, 20)
            client.set_mute(HEOS_PLAYER_ID, "off")
            client.set_volume(HEOS_PLAYER_ID, prev_vol)
            st.session_state[paused_key] = False

    if c3.button("⏭️", help="Seuraava kappale"):
        client.play_next(HEOS_PLAYER_ID)
        try:
            st.rerun()
        except AttributeError:
            st.experimental_rerun()

    # nyt soi
    now = client.get_now_playing(HEOS_PLAYER_ID)
    payload = now.get("payload", {})
    track = payload.get("song")
    artist = payload.get("artist")
    album = payload.get("album")

    box_html_start = """
    <div style="
        background:rgba(255,255,255,0.04);
        border:1px solid rgba(255,255,255,0.08);
        border-radius:14px;
        padding:10px 12px;
        min-height:120px;
        display:flex;
        flex-direction:column;
        justify-content:center;
    ">
    """
    box_html_end = "</div>"

    if track:
        st.markdown(
            box_html_start
            + f"<div style='font-size:1.05rem; font-weight:600;'>{track}</div>"
            + (f"<div style='opacity:.85; margin-top:2px;'>{artist}</div>" if artist else "")
            + (f"<div style='opacity:.6; margin-top:2px;'>{album}</div>" if album else "")
            + box_html_end,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            box_html_start
            + "<div style='opacity:.8;'>Ei HEOS-toistoa käynnissä.<br>Käynnistä Tidal HEOSiin, niin tiedot näkyvät tässä.</div>"
            + box_html_end,
            unsafe_allow_html=True,
        )
