from __future__ import annotations

import streamlit as st

from src.config import HEOS_HOST, HEOS_PASSWORD, HEOS_PLAYER_ID, HEOS_USERNAME
from src.heos_client import HeosClient
from src.ui.common import section_title


def _render_now_playing_box(track: str | None, artist: str | None, album: str | None) -> None:
    box_html_start = """
    <div class="card card-top-equal" style="min-height:120px;">
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
            "<p><small>Käynnistä toisto, niin tiedot näkyvät tässä.</small></p></div>"
            + box_html_end
        )

    st.markdown(html, unsafe_allow_html=True)


def card_heos() -> None:
    section_title("🎧 HEOS / Tidal", mt=10, mb=4)

    st.markdown(
        """
    <style>
    /* Keskitetään HEOS-nappien stButton-wrapperit sarakkeissaan */
    .st-key-heos_prev div[data-testid="stButton"],
    .st-key-heos_play_pause div[data-testid="stButton"],
    .st-key-heos_next div[data-testid="stButton"] {
    display:flex !important;
    justify-content:center !important;
    }

    /* Now playing: varma keskitys ja täysi leveys */
    .heos-np {
    text-align:center !important;
    width: 100%;
    max-width: none;
    margin: 10px auto 0 auto;
    }
    .heos-np .card-title,
    .heos-np .card-body { text-align:center !important; }
    </style>
        """,
        unsafe_allow_html=True,
    )

    client = HeosClient(
        HEOS_HOST,
        username=HEOS_USERNAME,
        password=HEOS_PASSWORD,
    )
    try:
        client.sign_in()
    except Exception:
        pass

    # Isot ikonipainikkeet (kohdistus key-luokilla, ei globaalisti kaikkiin nappeihin)
    st.markdown(
        """
<style>
/* Streamlitissä key näkyy yleensä wrapperissa .st-key-<key> */
.st-key-heos_prev button,
.st-key-heos_play_pause button,
.st-key-heos_next button {
  width: 56px !important;
  height: 56px !important;
  min-width: 56px !important;
  border-radius: 999px !important;
  border: 1px solid rgba(255,255,255,0.16) !important;
  background: rgba(255,255,255,0.07) !important;
  font-size: 28px !important;
  line-height: 1 !important;
  padding: 0 !important;
}

.st-key-heos_play_pause button {
  width: 64px !important;
  height: 64px !important;
  min-width: 64px !important;
  font-size: 32px !important;
  background: rgba(255,255,255,0.10) !important;
  border-color: rgba(255,255,255,0.22) !important;
}

.st-key-heos_prev button:hover,
.st-key-heos_play_pause button:hover,
.st-key-heos_next button:hover {
  background: rgba(255,255,255,0.12) !important;
}

.st-key-heos_prev button:active,
.st-key-heos_play_pause button:active,
.st-key-heos_next button:active {
  transform: translateY(1px);
}

/* HEOS now playing center */
.heos-np .card-title,
.heos-np .card-body {
  text-align: center !important;
}
.heos-np .card-body p {
  margin-left: auto !important;
  margin-right: auto !important;
}

</style>
        """,
        unsafe_allow_html=True,
    )

    # Symmetriset reunasarakkeet -> nappiryhmä keskelle korttia
    g0, c_prev, c_play, c_next, g1 = st.columns([2, 1, 1, 1, 2])

    with c_prev:
        if st.button("⏮", key="heos_prev"):
            try:
                client.play_previous(HEOS_PLAYER_ID)
            except Exception:
                pass

    with c_play:
        if st.button("⏯", key="heos_play_pause"):
            try:
                client.play_pause(HEOS_PLAYER_ID)
            except Exception:
                pass

    with c_next:
        if st.button("⏭", key="heos_next"):
            try:
                client.play_next(HEOS_PLAYER_ID)
            except Exception:
                pass

    # Now playing (testit lukevat tästä viimeisimmästä markdownista Track/Artist/Album tai tyhjätilan)
    try:
        resp = client.get_now_playing(HEOS_PLAYER_ID)
    except Exception:
        resp = {}

    np = resp.get("payload") if isinstance(resp, dict) else None
    if not isinstance(np, dict):
        np = resp if isinstance(resp, dict) else {}

    track = (np.get("song") or np.get("track") or np.get("title") or "").strip()
    artist = (np.get("artist") or "").strip()
    album = (np.get("album") or "").strip()

    def esc(s: str) -> str:
        return (
            s.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#39;")
        )

    track_h = esc(track)
    artist_h = esc(artist)
    album_h = esc(album)

    if track_h:
        html = (
            f"<div class='card-title'>{track_h}</div>"
            "<div class='card-body'>"
            + (f"<p>{artist_h}</p>" if artist_h else "")
            + (f"<p><small>{album_h}</small></p>" if album_h else "")
            + "</div>"
        )
    else:
        html = (
            "<div class='card-body'>"
            "<p>Ei HEOS-toistoa käynnissä.</p>"
            "<p><small>Käynnistä toisto, niin tiedot näkyvät tässä.</small></p>"
            "</div>"
        )

    st.markdown(f"<div class='heos-np'>{html}</div>", unsafe_allow_html=True)
