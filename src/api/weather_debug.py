from __future__ import annotations

import streamlit as st

from src.api.weather_mapping import (
    get_map_trace,
    wmo_to_foreca_code,
)
from src.weather_icons import render_foreca_icon


def card_weather_debug_matrix() -> None:
    st.markdown("<div class='card-title'>🧪 Sääikonit – pikatesti</div>", unsafe_allow_html=True)

    def _row(label: str, items: list[tuple[str, str]]) -> str:
        row_html = "<div style='display:flex; gap:10px; flex-wrap:wrap; align-items:center;'>"
        row_html += f"<div style='width:110px; opacity:.8;'>{label}</div>"
        for desc, key in items:
            img = render_foreca_icon(key, size=40)
            row_html += (
                "<div style='display:grid; place-items:center; "
                "background:rgba(255,255,255,.06); padding:6px 8px; border-radius:10px; min-width:120px;'>"
                f"{img}<div style='font-size:.8rem; opacity:.85;'>{desc}<br/><code>{key}</code></div></div>"
            )
        row_html += "</div>"
        return row_html

    cloud_rows: list[str] = []
    for is_day in (True, False):
        items = [
            (
                f"cc {cc}%",
                wmo_to_foreca_code(
                    0,
                    is_day=is_day,
                    pop=0,
                    temp_c=10,
                    cloudcover=cc,
                ),
            )
            for cc in (5, 30, 55, 75, 95)
        ]
        cloud_rows.append(_row("Päivä – pilvisyys" if is_day else "Yö – pilvisyys", items))

    rain_rows: list[str] = []
    for code in (61, 63, 65):
        cases = [
            ("päivä, PoP 20%", wmo_to_foreca_code(code, True, 20, 5.0, 70)),
            ("päivä, PoP 80%", wmo_to_foreca_code(code, True, 80, 5.0, 70)),
            ("päivä, 0°C (räntä)", wmo_to_foreca_code(code, True, 80, 0.0, 70)),
            ("yö, PoP 80%", wmo_to_foreca_code(code, False, 80, 5.0, 70)),
        ]
        rain_rows.append(_row(f"WMO {code} – sade", cases))

    shower_rows: list[str] = []
    for code in (80, 81, 82):
        cases = [
            (f"päivä, PoP {pop}%", wmo_to_foreca_code(code, True, pop, 10, 60)) for pop in (20, 80)
        ]
        shower_rows.append(_row(f"WMO {code} – kuurot", cases))

    misc_cases = [
        ("tihku heikko (51)", 51),
        ("tihku koht. (53)", 53),
        ("tihku voim. (55)", 55),
        ("jäätävä tihku (56)", 56),
        ("jäätävä sade h. (66)", 66),
        ("jäätävä sade v. (67)", 67),
        ("lumi (71)", 71),
        ("lumikuuro (85)", 85),
        ("ukkonen (95)", 95),
    ]
    misc_row = _row(
        "Muut",
        [
            (
                label,
                wmo_to_foreca_code(
                    code,
                    True,
                    80,
                    -2 if code in (71, 85) else 2,
                    80,
                ),
            )
            for label, code in misc_cases
        ],
    )

    st.markdown(
        "<section class='card' style='min-height:12dvh; padding:10px;'>"
        "<div class='card-body' style='display:flex; flex-direction:column; gap:8px;'>"
        + "".join(cloud_rows + rain_rows + shower_rows + [misc_row])
        + "</div></section>",
        unsafe_allow_html=True,
    )

    if st.toggle("Näytä päätösjäljet (trace)", value=False):
        rows = get_map_trace()
        if rows:
            head = (
                "<tr><th>WMO</th><th>Päivä</th><th>PoP %</th><th>T °C</th>"
                "<th>Cloud %</th><th>Key</th><th>Syynys</th></tr>"
            )
            body = "".join(
                f"<tr><td>{r['wmo']}</td><td>{'d' if r['is_day'] else 'n'}</td>"
                f"<td>{r['pop']}</td><td>{r['temp_c']}</td><td>{r['cloudcover']}</td>"
                f"<td><code>{r['key']}</code></td><td>{r['reason']}</td></tr>"
                for r in rows[::-1]
            )
            st.markdown(
                "<div class='card' style='padding:10px; overflow:auto;'>"
                "<div class='card-title'>Päätösjälki (uusin ensin)</div>"
                f"<table style='width:100%; font-size:.9rem; border-collapse:collapse;'>{head}{body}</table></div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown("<div class='hint'>Ei jälkiä vielä.</div>", unsafe_allow_html=True)
