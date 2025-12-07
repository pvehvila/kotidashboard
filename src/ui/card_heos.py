# src/ui/card_heos.py
from __future__ import annotations

import streamlit as st

from src.config import HEOS_HOST, HEOS_PASSWORD, HEOS_PLAYER_ID, HEOS_USERNAME
from src.heos_client import HeosClient
from src.ui.common import section_title


def _render_now_playing_box(track: str | None, artist: str | None, album: str | None) -> None:
    """Yksi kompaktin kokoinen kortti nykyiselle biisille."""
    box_html_start = """
    <div class="card card-top-equal" style="
        min-height:120px;
    ">
    """
    box_html_end = "</div>"

    if track:
        html = box_html_start + f"<div class='card-title'>{track}</div>"
        body_parts = []
        if artist:
            body_parts.append(f"<p>{artist}</p>")
        if album:
            body_parts.append(f"<p><small>{album}</small></p>")

        body_html = "<div class='card-body'>" + "".join(body_parts) + "</div>"
        html += body_html + box_html_end
    else:
        html = (
            box_html_start + "<div class='card-body'><p>Ei HEOS-toistoa käynnissä.</p>"
            "<p><small>Käynnistä Tidal HEOS-soittimeen, niin tiedot näkyvät tässä.</small></p></div>"
            + box_html_end
        )

    st.markdown(html, unsafe_allow_html=True)


def card_heos() -> None:
    section_title("🎧 HEOS / Tidal", mt=10, mb=4)

    client = HeosClient(HEOS_HOST, username=HEOS_USERNAME, password=HEOS_PASSWORD)
    client.sign_in()

    # Ohjauspainikkeet: keskitetty rivi
    col_left, col_prev, col_play, col_next, col_right = st.columns([1, 1, 1, 1, 1])

    with col_prev:
        if st.button("⏮", key="heos_prev"):
            try:
                client.play_previous(HEOS_PLAYER_ID)
            except Exception:
                pass  # ei kaadeta dashboardia

    with col_play:
        if st.button("⏯", key="heos_play_pause"):
            try:
                client.play_pause(HEOS_PLAYER_ID)
            except Exception:
                pass

    with col_next:
        if st.button("⏭", key="heos_next"):
            try:
                client.play_next(HEOS_PLAYER_ID)
            except Exception:
                pass

    # Nykyinen kappale
    try:
        payload = client.get_now_playing(HEOS_PLAYER_ID)
    except Exception:
        payload = {}

    track = payload.get("song") or payload.get("track") or payload.get("title") or None
    artist = payload.get("artist")
    album = payload.get("album")

    _render_now_playing_box(track, artist, album)
