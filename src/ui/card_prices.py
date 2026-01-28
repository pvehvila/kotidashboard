# src/ui/card_prices.py
from __future__ import annotations

from datetime import datetime

import plotly.graph_objects as go
import streamlit as st

from src.api.prices_15min_vm import (  # noqa: F401 (backwards compat)
    build_prices_15min_vm,
    current_price_15min,
    next_12h_15min,
)
from src.config import (
    COLOR_GRAY,
    COLOR_TEXT_GRAY,
    PLOTLY_CONFIG,
    TZ,
)
from src.ui.common import card, section_title
from src.utils import _color_for_value

# ------------------------------------------------------------------
# Takautuva yhteensopivuus vanhoihin testeihin:
# näistä ohjataan uuteen viewmodel-implementaatioon.
# ------------------------------------------------------------------


def _current_price_15min(
    prices_today,
    now_dt,
):
    """Wrapper: delegoi src.api.prices_15min_vm.current_price_15min-funktioon."""
    return current_price_15min(prices_today, now_dt=now_dt)


def _next_12h_15min(
    prices_today,
    prices_tomorrow,
    now_dt,
):
    """Wrapper: delegoi src.api.prices_15min_vm.next_12h_15min-funktioon."""
    return next_12h_15min(
        prices_today=prices_today,
        prices_tomorrow=prices_tomorrow,
        now_dt=now_dt,
    )


def card_prices() -> None:
    """Render a card displaying electricity prices for the next 12 hours (15 min)."""
    try:
        vm = build_prices_15min_vm(now_dt=datetime.now(TZ))

        rows = vm["rows"]
        current_cents = vm["current_cents"]

        title_html = (
            "⚡ Pörssisähkö " + "<span style='background:{0}; color:{1}; padding:2px 10px; "
            "border-radius:999px; font-weight:600; font-size:0.95rem'>15 min</span>"
        ).format(COLOR_GRAY, COLOR_TEXT_GRAY)

        if current_cents is not None:
            badge_bg = _color_for_value(current_cents)
            title_html += (
                f" <span style='background:{badge_bg}; color:#000; padding:2px 10px; "
                f"border-radius:10px; font-weight:700; font-size:0.95rem'>{current_cents:.2f} snt/kWh</span>"
            )

        section_title(title_html, mt=10, mb=4)

        if not rows:
            card(
                "Pörssisähkö",
                "<span class='hint'>Ei dataa vielä seuraaville 15 min jaksoille</span>",
                height_dvh=16,
            )
            return

        values = vm["values"]
        colors = vm["colors"]
        line_colors = vm["line_colors"]
        line_widths = vm["line_widths"]
        y_min = vm["y_min"]
        y_max = vm["y_max"]
        step = vm["y_step"]

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
            </div>
            """,
            unsafe_allow_html=True,
        )
    except Exception as e:
        section_title("Pörssisähkö – seuraavat 12 h")
        st.markdown(f"<span class='hint'>Virhe hinnanhaussa: {e}</span>", unsafe_allow_html=True)
