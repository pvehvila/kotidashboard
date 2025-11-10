# src/ui/card_prices.py
from __future__ import annotations

import math
from datetime import datetime, timedelta

import plotly.graph_objects as go
import streamlit as st

from src.api import try_fetch_prices_15min
from src.config import (
    COLOR_GRAY,
    COLOR_TEXT_GRAY,
    PLOTLY_CONFIG,
    PRICE_Y_STEP_SNT,
    TZ,
)
from src.ui.common import card, section_title
from src.utils import _color_by_thresholds, _color_for_value


def _current_price_15min(
    prices_today: list[dict[str, datetime | float]] | None,
    now_dt: datetime,
) -> float | None:
    if not prices_today:
        return None
    minute = (now_dt.minute // 15) * 15
    slot = now_dt.replace(minute=minute, second=0, microsecond=0)
    hit = next(
        (p for p in prices_today if isinstance(p.get("ts"), datetime) and p["ts"] == slot),
        None,
    )
    if not hit:
        return None
    cents_val = hit.get("cents")
    if not isinstance(cents_val, (int | float)):
        return None
    return float(cents_val)


def _next_12h_15min(
    prices_today: list[dict[str, datetime | float]] | None,
    prices_tomorrow: list[dict[str, datetime | float]] | None,
    now_dt: datetime,
) -> list[dict[str, datetime | str | float | bool]]:
    if not prices_today and not prices_tomorrow:
        return []

    rows: list[dict[str, datetime | str | float | bool]] = []
    minute = (now_dt.minute // 15) * 15
    base = now_dt.replace(minute=minute, second=0, microsecond=0)

    for i in range(48):
        ts = base + timedelta(minutes=15 * i)

        src = prices_today if ts.date() == now_dt.date() else prices_tomorrow
        if not src:
            continue

        hit = next(
            (p for p in src if isinstance(p.get("ts"), datetime) and p["ts"] == ts),
            None,
        )

        if not hit:
            # etsi lähellä, joskus ts voi heittää vähän
            for p in src:
                ts_p = p.get("ts")
                if not isinstance(ts_p, datetime):
                    continue
                if abs((ts_p - ts).total_seconds()) < 60:
                    hit = p
                    break

        if not hit:
            continue

        cents_val = hit.get("cents")
        if not isinstance(cents_val, (int | float)):
            cents_val = 0.0

        rows.append(
            {
                "ts": ts,
                "label": ts.strftime("%H:%M"),
                "cents": float(cents_val),
                "is_now": i == 0,
            }
        )

    return rows


def card_prices() -> None:
    """Render a card displaying electricity prices for the next 12 hours (15 min)."""
    try:
        now_dt = datetime.now(TZ)
        today = now_dt.date()
        tomorrow = today + timedelta(days=1)

        prices_today = try_fetch_prices_15min(today)
        prices_tomorrow = try_fetch_prices_15min(tomorrow)

        current_cents = _current_price_15min(prices_today, now_dt)

        title_html = (
            "⚡ Pörssisähkö " + "<span style='background:{0}; color:{1}; padding:2px 10px; "
            "border-radius:999px; font-weight:600; font-size:0.95rem'>Seuraavat 12 h (15 min)</span>"
        ).format(COLOR_GRAY, COLOR_TEXT_GRAY)

        if current_cents is not None:
            badge_bg = _color_for_value(current_cents)
            title_html += (
                f" <span style='background:{badge_bg}; color:#000; padding:2px 10px; "
                f"border-radius:10px; font-weight:700; font-size:0.95rem'>{current_cents:.2f} snt/kWh</span>"
            )

        section_title(title_html, mt=10, mb=4)

        rows = _next_12h_15min(prices_today, prices_tomorrow, now_dt=now_dt)
        if not rows:
            card(
                "Pörssisähkö",
                "<span class='hint'>Ei dataa vielä seuraaville 15 min jaksoille</span>",
                height_dvh=16,
            )
            return

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
        st.markdown(f"<span class='hint'>Virhe hinnanhaussa: {e}</span>", unsafe_allow_html=True)
