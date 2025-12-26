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
    """
    HEOS / Tidal -kortti (deterministinen layout):
      - Renderöidään koko kortti st_html():lla (kuten card_system)
      - Painikkeet HTML:llä (isot, selkeät)
      - Klikit ohjataan query paramin kautta Pythonille (prev/toggle/next)
      - Kiinteä korkeus 200px → parina Järjestelmätila-kortille
    """
    from streamlit.components.v1 import html as st_html

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

    # --- 1) Käsittele mahdollinen komento query paramista ---
    # Streamlit query params: pidetään yksinkertaisena ja vältetään looppi.
    cmd = None
    try:
        # Streamlit 1.30+: st.query_params toimii dict-mäisesti (arvot voivat olla listoja/str)
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

        # Poista parametri heti, ettei sama komento toistu jokaisella rerunilla
        try:
            # jätetään muut parametrit ennalleen, poistetaan vain heos_cmd
            qp = dict(st.query_params)
            qp.pop("heos_cmd", None)
            st.query_params.clear()
            for k, v in qp.items():
                st.query_params[k] = v
        except Exception:
            pass

    # --- 2) Hae now playing ---
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

    # HTML-escape minimit (ettei metadatan erikoismerkit riko HTML:ää)
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

    # --- 3) Renderöi kortti HTML:llä (kiinteä korkeus 200) ---
    # Klikit: lisätään heos_cmd query param ja reload → Python käsittelee.
    html = f"""
<!doctype html>
<html><head><meta charset="utf-8">
<style>
  :root {{
    --fg:#e7eaee;
    --bg:rgba(255,255,255,0.04);
    --bd:rgba(255,255,255,0.08);
    --fg-hint:rgba(231,234,238,0.75);
    --btn-bg:rgba(255,255,255,0.07);
    --btn-bg-hover:rgba(255,255,255,0.12);
    --btn-bd:rgba(255,255,255,0.16);
  }}
  html,body {{
    margin:0; padding:0; background:transparent; color:var(--fg);
    font-family:ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,Ubuntu;
  }}
  .card {{
    position:relative; overflow:hidden; border-radius:14px;
    background:var(--bg); border:1px solid var(--bd);
    height:200px; box-sizing:border-box;
    padding:10px 12px;
    display:flex; flex-direction:column;
  }}
  .controls {{
    display:flex; justify-content:center; align-items:center;
    gap:18px; margin-top:2px; margin-bottom:10px;
  }}
  .btn {{
    width:56px; height:56px; border-radius:999px;
    border:1px solid var(--btn-bd);
    background:var(--btn-bg); color:var(--fg);
    font-size:28px; line-height:1; cursor:pointer;
    display:flex; align-items:center; justify-content:center;
    user-select:none;
  }}
  .btn:hover {{ background:var(--btn-bg-hover); }}
  .btn:active {{ transform:translateY(1px); }}

  .btn.primary {{
    width:64px; height:64px; font-size:32px;
    background:rgba(255,255,255,0.10);
    border-color:rgba(255,255,255,0.22);
  }}

  .np {{
    margin-top:auto;
    text-align:center;
    padding-bottom:2px;
  }}
  .track {{
    font-size:1.02rem; font-weight:650; letter-spacing:0.2px;
    margin:0 0 2px 0;
  }}
  .artist {{
    font-size:.95rem; margin:0 0 2px 0;
    color:rgba(231,234,238,0.92);
  }}
  .album {{
    font-size:.80rem; margin:0;
    color:rgba(231,234,238,0.72);
  }}
  .empty {{
    font-size:.95rem; margin:0 0 2px 0;
    color:rgba(231,234,238,0.86);
  }}
  .hint {{
    font-size:.80rem; margin:0;
    color:var(--fg-hint);
  }}
</style>
</head>
<body>
  <section class="card">
    <div class="controls">
      <button class="btn" onclick="heosCmd('prev')" aria-label="Edellinen">⏮</button>
      <button class="btn primary" onclick="heosCmd('toggle')" aria-label="Toista / tauko">⏯</button>
      <button class="btn" onclick="heosCmd('next')" aria-label="Seuraava">⏭</button>
    </div>

    <div class="np">
      {""
        if track_h
        else "<p class='empty'>Ei HEOS-toistoa käynnissä.</p><p class='hint'>Käynnistä toisto, niin tiedot näkyvät tässä.</p>"
      }
      {f"<p class='track'>{track_h}</p>" if track_h else ""}
      {f"<p class='artist'>{artist_h}</p>" if (track_h and artist_h) else ""}
      {f"<p class='album'>{album_h}</p>" if (track_h and album_h) else ""}
    </div>
  </section>

<script>
  function heosCmd(cmd) {{
    try {{
      const url = new URL(window.location.href);
      url.searchParams.set('heos_cmd', cmd);
      window.location.href = url.toString();
    }} catch (e) {{
      // fallback: naive
      window.location.search = '?heos_cmd=' + encodeURIComponent(cmd);
    }}
  }}
</script>
</body></html>
"""

    st_html(html, height=200, scrolling=False)
