# src/ui/card_nameday.py
from __future__ import annotations

from datetime import datetime

import streamlit as st

from src.api.calendar_nameday import fetch_holiday_today, fetch_nameday_today
from src.config import LAT, LON, TZ
from src.ui.card_nameday_helpers import get_background_image, get_flag_info

# aurinko – sama fallback-logiikka kuin aiemmin
try:
    from src.utils_sun import _sun_icon, fetch_sun_times  # type: ignore
except Exception:
    try:
        from src.utils import fetch_sun_times  # type: ignore

        def _sun_icon(kind: str, size: int = 18) -> str:
            return "🌅" if kind == "rise" else "🌇"
    except Exception:
        fetch_sun_times = None  # type: ignore

        def _sun_icon(kind: str, size: int = 18) -> str:
            return "🌅" if kind == "rise" else "🌇"


def _weekday_fi(dt_: datetime) -> str:
    weekdays = [
        "maanantaina",
        "tiistaina",
        "keskiviikkona",
        "torstaina",
        "perjantaina",
        "lauantaina",
        "sunnuntaina",
    ]
    return weekdays[dt_.weekday()]


def _get_sun_times() -> tuple[str | None, str | None]:
    """Käärii eri palautusmuodot yhdeksi (sunrise, sunset) -tuplaksi."""
    sunrise = sunset = None
    if callable(fetch_sun_times):  # type: ignore
        try:
            tz_key = TZ.key if hasattr(TZ, "key") else str(TZ)
            sun_data = fetch_sun_times(LAT, LON, tz_key)  # type: ignore

            if isinstance(sun_data, tuple) and len(sun_data) == 2:
                sunrise, sunset = sun_data
            elif isinstance(sun_data, dict):
                sunrise = sun_data.get("sunrise")
                sunset = sun_data.get("sunset")
        except Exception:
            pass
    return sunrise, sunset


def get_nameday_vm() -> dict:
    """Kokaa kaiken datan yhteen sanakirjaan korttia varten."""
    today = datetime.now(TZ)
    names = fetch_nameday_today() or "—"
    sunrise, sunset = _get_sun_times()
    flag_txt, flag_debug = get_flag_info(today)

    # mahdollinen pyhä-/liputuspäivä samasta moduulista
    holiday_info = fetch_holiday_today()

    try:
        day_str = today.strftime("%-d.%m.")
    except ValueError:
        # Windows
        day_str = today.strftime("%#d.%m.")

    return {
        "today": today,
        "names": names,
        "weekday_label": _weekday_fi(today),
        "day_str": day_str,
        "sunrise": sunrise or "—",
        "sunset": sunset or "—",
        "flag_txt": flag_txt,
        "flag_debug": flag_debug,
        "background": get_background_image(),
        "holiday_info": holiday_info,
    }


def render_nameday_card(vm: dict) -> None:
    """Tekee varsinaisen HTML:n."""
    bg = vm["background"]
    overlay = "linear-gradient(90deg, rgba(11,15,20,0.65) 0%, rgba(11,15,20,0.00) 72%)"
    bg_layer = f"{overlay}, url('{bg}')" if bg else overlay

    fi_flag_svg = (
        "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 9 6' width='14' height='10'>"
        "<rect width='9' height='6' fill='white'/>"
        "<rect y='2' width='9' height='2' fill='#003580'/>"
        "<rect x='2' width='2' height='6' fill='#003580'/>"
        "</svg>"
    )

    html: list[str] = []
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

    # liputusbalooni, jos on
    if vm["flag_txt"]:
        html.append(
            "<div style=\"display:inline-flex;align-items:center;gap:6px;"
            "background:rgba(255,255,255,.12);padding:4px 10px;"
            "border-radius:999px;font-size:.75rem;margin-bottom:4px;\">"
            f"{fi_flag_svg}<span>{vm['flag_txt']}</span></div>"
        )

    # otsikkorivi
    html.append(
        "<div style=\"font-size:.8rem; opacity:.9; margin-bottom:2px;\">"
        f"Nimipäivät {vm['weekday_label']} {vm['day_str']}</div>"
    )
    # nimet
    html.append(
        "<div style=\"font-size:1.3rem; font-weight:700; "
        "text-shadow:0 1px 2px rgba(0,0,0,.35);\">"
        f"{vm['names']}</div>"
    )

    # auringot
    html.append('<div style="display:flex; gap:6px; flex-wrap:wrap; margin-top:2px;">')
    html.append(
        "<div style=\"display:inline-flex;align-items:center;gap:6px;"
        "background:rgba(0,0,0,.35);padding:4px 10px;"
        "border-radius:999px;font-size:.75rem;\">"
        f"{_sun_icon('rise', 16)} <strong>{vm['sunrise']}</strong></div>"
    )
    html.append(
        "<div style=\"display:inline-flex;align-items:center;gap:6px;"
        "background:rgba(0,0,0,.35);padding:4px 10px;"
        "border-radius:999px;font-size:.75rem;\">"
        f"{_sun_icon('set', 16)} <strong>{vm['sunset']}</strong></div>"
    )
    html.append("</div>")  # aurinko-div

    html.append("</div></section>")  # card-body + section

    st.markdown("".join(html), unsafe_allow_html=True)


def card_nameday() -> None:
    """Streamlit-entrypoint."""
    vm = get_nameday_vm()
    render_nameday_card(vm)
