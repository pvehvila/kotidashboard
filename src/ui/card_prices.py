from __future__ import annotations

import math

import plotly.graph_objects as go
import streamlit as st

from src.api.electricity_viewmodel import build_electricity_12h_view
from src.config import (
    COLOR_GRAY,
    COLOR_TEXT_GRAY,
    PLOTLY_CONFIG,
    PRICE_Y_STEP_SNT,
)
from src.ui.common import card, section_title
from src.utils import _color_by_thresholds, _color_for_value


def card_prices() -> None:
    """Renderöi pörssisähkön hintakortin käyttäen valmista viewmodelia."""
    try:
        vm = build_electricity_12h_view()
        rows = vm["rows"]
        current_cents = vm["current_cents"]

        # otsikko + badge
        title_html = (
            "⚡ Pörssisähkö "
            f"<span style='background:{COLOR_GRAY}; color:{COLOR_TEXT_GRAY}; padding:2px 10px; "
            "border-radius:999px; font-weight:600; font-size:0.95rem'>Seuraavat 12 h (15 min)</span>"
        )

        if current_cents is not None:
            badge_bg = _color_for_value(current_cents)
            title_html += (
                f" <span style='background:{badge_bg}; color:#000; padding:2px 10px; "
                f"border-radius:10px; font-weight:700; font-size:0.95rem'>{current_cents:.2f} snt/kWh</span>"
            )

        section_title(title_html, mt=10, mb=4)

        # jos ei rivejä -> näytä tyhjäkortti
        if not rows:
            card(
                "Pörssisähkö",
                "<span class='hint'>Ei dataa vielä seuraaville 15 min jaksoille</span>",
                height_dvh=16,
            )
            return

        # plotdata
        values: list[float] = []
        for row in rows:
            val = row.get("cents")
            if isinstance(val, (int | float)):
                values.append(float(val))
            else:
                values.append(0.0)

        colors = _color_by_thresholds(list(values))
        line_colors = [
            "rgba(255,255,255,0.9)" if row["is_now"] else "rgba(0,0,0,0)" for row in rows
        ]
        line_widths = [1.5 if row["is_now"] else 0 for row in rows]

        step = float(max(1, PRICE_Y_STEP_SNT))
        y_min_src = min(values, default=0.0)
        y_max_src = max(values, default=step)

        y_min = float(math.floor(y_min_src / step) * step)
        y_max = float(math.ceil(y_max_src / step) * step)
        if y_max <= y_min:
            y_max = y_min + step

        fig = go.Figure(
            [
                go.Bar(
                    x=[row["label"] for row in rows],
                    y=[round(v, 2) for v in values],
                    marker=dict(color=colors, line=dict(color=line_colors, width=line_widths)),
                    hovertemplate="<b>%{x}</b><br>%{y} snt/kWh<extra></extra>",
                )
            ]
        )

        fig.update_layout(
            title=None,
            title_x=0,
            title_font_size=14,
            margin=dict(l=60, r=10, t=24, b=44),
            xaxis_title=None,
            yaxis_title="snt/kWh",
            height=190,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(gridcolor="rgba(255,255,255,0.08)"),
            yaxis=dict(
                gridcolor="rgba(255,255,255,0.08)",
                range=[y_min, y_max],
                tick0=y_min,
                dtick=step,
                automargin=True,
            ),
        )
        fig.add_hline(y=0, line=dict(color="rgba(255,255,255,0.25)", width=1))

        st.plotly_chart(fig, use_container_width=True, theme=None, config=PLOTLY_CONFIG)
        st.markdown(
            """
            <div class='hint' style='margin-top:0px; margin-bottom:2px;'>
              <span style='color:#00b400;'>&#9632;</span> ≤ 5 snt &nbsp;
              <span style='color:#cccc00;'>&#9632;</span> 5–15 snt &nbsp;
              <span style='color:#dc0000;'>&#9632;</span> ≥ 15 snt &nbsp;
              (vihreä = halpa, punainen = kallis)
            </div>
            """,
            unsafe_allow_html=True,
        )
    except Exception as e:
        section_title("Pörssisähkö – seuraavat 12 h")
        st.markdown(
            f"<span class='hint'>Virhe hinnanhaussa: {e}</span>",
            unsafe_allow_html=True,
        )
