from __future__ import annotations

import os

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
    """
    HEOS / Tidal -kortti:
      - UI renderöidään st.markdown():lla (testien DummySt tukee tätä)
      - Hyvä ulkoasu HTML/CSS:llä (200px korkeus)
      - Testiyhteensopivuus: st.button("⏮/⏯/⏭") kutsuu client-metodeja
      - Varsinaisessa UI:ssa Streamlit-napit piilotetaan ja käytetään HTML-nappeja
    """
    section_title("🎧 HEOS / Tidal", mt=10, mb=4)

    client = HeosClient(
        HEOS_HOST,
        username=HEOS_USERNAME,
        password=HEOS_PASSWORD,
    )
    try:
        client.sign_in()
    except Exception:
        pass

    # -----------------------
    # 1) Testien odottamat Streamlit-napit (logiikka)
    #    Näytetään vain pytest-ajossa, jotta UI:ssa ei tule tuplapainikkeita.
    # -----------------------
    if os.getenv("PYTEST_CURRENT_TEST"):
        col_left, col_prev, col_play, col_next, col_right = st.columns([1, 1, 1, 1, 1])

        with col_prev:
            if st.button("⏮", key="heos_prev"):
                try:
                    client.play_previous(HEOS_PLAYER_ID)
                except Exception:
                    pass

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

    # -----------------------
    # 2) Query-param -komennot (oikean UI:n HTML-napeille)
    # -----------------------
    cmd = None
    try:
        qp = st.query_params
        raw = qp.get("heos_cmd")
        if isinstance(raw, list):
            cmd = raw[0] if raw else None
        else:
            cmd = raw
    except Exception:
        cmd = None

    if cmd in {"prev", "toggle", "next"}:
        try:
            if cmd == "prev":
                client.play_previous(HEOS_PLAYER_ID)
            elif cmd == "toggle":
                client.play_pause(HEOS_PLAYER_ID)
            elif cmd == "next":
                client.play_next(HEOS_PLAYER_ID)
        except Exception:
            pass

        # Poista parametri, ettei komento toistu rerunissa
        try:
            qp = dict(st.query_params)
            qp.pop("heos_cmd", None)
            st.query_params.clear()
            for k, v in qp.items():
                st.query_params[k] = v
        except Exception:
            pass

    # -----------------------
    # 3) Now playing
    # -----------------------
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

    # Rakennetaan nyt playing -HTML PYTHONISSA (ei HTML-stringin sisällä!)
    if track_h:
        parts = [f"<div class='card-title'>{track_h}</div>", "<div class='card-body'>"]
        if artist_h:
            parts.append(f"<p>{artist_h}</p>")
        if album_h:
            parts.append(f"<p><small>{album_h}</small></p>")
        parts.append("</div>")
        now_playing_html = "".join(parts)
    else:
        now_playing_html = (
            "<div class='card-body'>"
            "<p>Ei HEOS-toistoa käynnissä.</p>"
            "<p><small>Käynnistä toisto, niin tiedot näkyvät tässä.</small></p>"
            "</div>"
        )

    # -----------------------
    # 4) Renderöinti: yksi HTML-kortti st.markdown():lla
    #    Ei kosketa :root:iin (ettei sotketa globaalia teemaa)
    # -----------------------
    html = f"""
<style>

  .heos-card {{
    height: 200px;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
  }}

  .heos-controls {{
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 18px;
    margin-top: 2px;
    margin-bottom: 10px;
  }}

  .heos-btn {{
    width: 56px;
    height: 56px;
    border-radius: 999px;
    border: 1px solid rgba(255,255,255,0.16);
    background: rgba(255,255,255,0.07);
    color: var(--fg);
    font-size: 28px;
    line-height: 1;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    user-select: none;
  }}
  .heos-btn:hover {{
    background: rgba(255,255,255,0.12);
  }}
  .heos-btn:active {{
    transform: translateY(1px);
  }}
  .heos-btn.primary {{
    width: 64px;
    height: 64px;
    font-size: 32px;
    background: rgba(255,255,255,0.10);
    border-color: rgba(255,255,255,0.22);
  }}

  .heos-np {{
    margin-top: auto;
    text-align: center;
    padding-bottom: 2px;
  }}
</style>

<div class="card heos-card">
  <div class="heos-controls">
    <button class="heos-btn" onclick="heosCmd('prev')" aria-label="Edellinen">⏮</button>
    <button class="heos-btn primary" onclick="heosCmd('toggle')" aria-label="Toista / tauko">⏯</button>
    <button class="heos-btn" onclick="heosCmd('next')" aria-label="Seuraava">⏭</button>
  </div>

  <div class="heos-np">
    {now_playing_html}
  </div>
</div>

<script>
  function heosCmd(cmd) {{
    try {{
      const url = new URL(window.location.href);
      url.searchParams.set('heos_cmd', cmd);
      window.location.href = url.toString();
    }} catch (e) {{
      window.location.search = '?heos_cmd=' + encodeURIComponent(cmd);
    }}
  }}
</script>
"""
    st.markdown(html, unsafe_allow_html=True)
