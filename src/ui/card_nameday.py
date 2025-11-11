from __future__ import annotations

import base64
import json
from datetime import datetime
from pathlib import Path

import streamlit as st

from src.api.calendar_nameday import fetch_nameday_today
from src.config import LAT, LON, TZ
from src.paths import asset_path

# aurinko
try:
    from src.utils_sun import fetch_sun_times, _sun_icon  # type: ignore
except Exception:
    try:
        from src.utils import fetch_sun_times  # type: ignore

        def _sun_icon(kind: str, size: int = 18) -> str:
            return "🌅" if kind == "rise" else "🌇"
    except Exception:
        fetch_sun_times = None  # type: ignore

        def _sun_icon(kind: str, size: int = 18) -> str:
            return "🌅" if kind == "rise" else "🌇"


def _weekday_fi(dt: datetime) -> str:
    weekdays = [
        "maanantaina",
        "tiistaina",
        "keskiviikkona",
        "torstaina",
        "perjantaina",
        "lauantaina",
        "sunnuntaina",
    ]
    return weekdays[dt.weekday()]


def _butterfly_bg() -> str:
    for name in ("butterfly-bg.png", "butterfly-bg.webp", "butterfly-bg.jpg"):
        p = asset_path(name)
        if p.exists():
            b64 = base64.b64encode(p.read_bytes()).decode("ascii")
            ext = p.suffix.lstrip(".").lower()
            mime = {"png": "image/png", "webp": "image/webp", "jpg": "image/jpeg"}[ext]
            return f"data:{mime};base64,{b64}"
    return ""


def _find_pyhat() -> Path | None:
    # etsi ylöspäin nykyisestä hakemistosta
    cwd = Path.cwd().resolve()
    for parent in (cwd, *cwd.parents):
        cand = parent / "data" / "pyhat_fi.json"
        if cand.exists():
            return cand

    # varmuudeksi tämän tiedoston sijainnista myös ylöspäin
    here = Path(__file__).resolve()
    for parent in (here.parent, *here.parents):
        cand = parent / "data" / "pyhat_fi.json"
        if cand.exists():
            return cand

    return None


def _get_flag(today: datetime) -> tuple[str | None, str | None]:
    """Palauta (lipputeksti, debug)"""
    key = today.strftime("%Y-%m-%d")
    path = _find_pyhat()
    if path is None:
        return None, "data/pyhat_fi.json ei löytynyt mistään yläkansiosta"

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        return None, f"pyhat_fi.json löytyi ({path}), mutta sitä ei voitu lukea: {e}"

    info = data.get(key)
    if info and info.get("flag"):
        return info.get("name") or "Liputuspäivä", None
    else:
        # näytä vähän mitä siellä on
        some_keys = ", ".join(list(data.keys())[:8])
        return None, f"pyhat_fi.json löytyi ({path}), mutta avainta {key} ei ollut. Avaimet: {some_keys}"


def card_nameday() -> None:
    today = datetime.now(TZ)

    names = fetch_nameday_today() or "—"
    flag_txt, flag_debug = _get_flag(today)

    # aurinko
    sunrise = sunset = None
    if callable(fetch_sun_times):
        try:
            tz_key = TZ.key if hasattr(TZ, "key") else str(TZ)
            sun_data = fetch_sun_times(LAT, LON, tz_key)

            # 1) vanha malli: palautti (sunrise, sunset)
            if isinstance(sun_data, tuple) and len(sun_data) == 2:
                sunrise, sunset = sun_data

            # 2) uusi malli: palauttaa dictin
            elif isinstance(sun_data, dict):
                sunrise = sun_data.get("sunrise")
                sunset = sun_data.get("sunset")

            # muut muodot ohitetaan siististi
        except Exception:
            pass


    # päivämäärä
    try:
        day_str = today.strftime("%-d.%m.")
    except ValueError:
        day_str = today.strftime("%#d.%m.")

    # tausta
    bg = _butterfly_bg()
    overlay = "linear-gradient(90deg, rgba(11,15,20,0.65) 0%, rgba(11,15,20,0.00) 72%)"
    bg_layer = f"{overlay}, url('{bg}')" if bg else overlay

    # pieni valkoinen Suomen lippu (SVG, näkyy tummalla taustalla)
    fi_flag_svg = (
        "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 9 6' width='14' height='10'>"
        "<rect width='9' height='6' fill='white'/>"
        "<rect y='2' width='9' height='2' fill='#003580'/>"
        "<rect x='2' width='2' height='6' fill='#003580'/>"
        "</svg>"
    )

    html = []
    html.append(
        f'<section class="card card-top-equal" '
        f'style="height:180px; position:relative; overflow:hidden; '
        f'background-image:{bg_layer}; background-size:cover; background-position:center;">'
    )
    html.append(
        '<div class="card-body" '
        'style="display:flex; flex-direction:column; gap:6px; text-align:left; '
        'padding:12px 16px; color:#fff;">'
    )

    # LIPUTUS tai DEBUG ENSIMMÄISENÄ
    if flag_txt:
        html.append(
            "<div style=\"display:inline-flex;align-items:center;gap:6px;"
            "background:rgba(255,255,255,.12);padding:4px 10px;"
            "border-radius:999px;font-size:.75rem;margin-bottom:4px;\">"
            f"{fi_flag_svg}<span>{flag_txt}</span></div>"
        )
    elif flag_debug:
        html.append(
            "<div style=\"font-size:.6rem;opacity:.7;background:rgba(0,0,0,.35);"
            "padding:3px 6px;border-radius:6px;\">"
            f"{flag_debug}</div>"
        )

    # Nimipäivä ja nimet
    html.append(
        f'<div style="font-size:.8rem; opacity:.9; margin-bottom:2px;">'
        f'Nimipäivät {_weekday_fi(today)} {day_str}</div>'
    )
    html.append(
        f'<div style="font-size:1.3rem; font-weight:700; '
        f'text-shadow:0 1px 2px rgba(0,0,0,.35);">{names}</div>'
    )

    # Aurinko
    html.append('<div style="display:flex; gap:6px; flex-wrap:wrap; margin-top:2px;">')
    html.append(
        "<div style=\"display:inline-flex;align-items:center;gap:6px;"
        "background:rgba(0,0,0,.35);padding:4px 10px;"
        "border-radius:999px;font-size:.75rem;\">"
        f"{_sun_icon('rise', 16)} <strong>{sunrise or '—'}</strong></div>"
    )
    html.append(
        "<div style=\"display:inline-flex;align-items:center;gap:6px;"
        "background:rgba(0,0,0,.35);padding:4px 10px;"
        "border-radius:999px;font-size:.75rem;\">"
        f"{_sun_icon('set', 16)} <strong>{sunset or '—'}</strong></div>"
    )
    html.append("</div></div></section>")

    st.markdown("".join(html), unsafe_allow_html=True)
