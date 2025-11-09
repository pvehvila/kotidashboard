from __future__ import annotations

import math
from collections.abc import Iterable
from datetime import datetime, timedelta

import plotly.graph_objects as go

from src.api import (
    fetch_btc_eur_range,
    fetch_btc_last_7d_eur,
    fetch_btc_last_24h_eur,
    fetch_btc_last_30d_eur,
)
from src.config import (
    BTC_Y_PAD_EUR,
    BTC_Y_PAD_PCT,
    BTC_Y_STEP_EUR,
    BTC_Y_USE_PCT_PAD,
    COLOR_GRAY,
    COLOR_GREEN,
    COLOR_RED,
    COLOR_TEXT_GRAY,
    TZ,
)

# ------------------------------------------------------------
#  Data & series
# ------------------------------------------------------------


def get_btc_series_for_window(window: str) -> tuple[list[tuple[datetime, float]], bool]:
    """
    Palauttaa (sarja, degraded).
    Sarja on aina aikajärjestyksessä.
    degraded = True jos jouduttiin käyttämään kapeampaa ikkunaa
    kuin mitä käyttäjä pyysi (esim. 30d → 7d).
    """
    now = datetime.now(TZ)

    # 24 h
    if window == "24h":
        s = fetch_btc_last_24h_eur()
        if s:
            return s, False

        s = fetch_btc_eur_range(hours=24)
        if s:
            return s, False

        s7 = fetch_btc_last_7d_eur()
        if s7:
            cutoff = now - timedelta(hours=24)
            s24 = [(t, v) for (t, v) in s7 if t >= cutoff]
            return (s24 if len(s24) >= 2 else s7), (len(s24) < 2)

    # 7 d
    if window == "7d":
        s = fetch_btc_last_7d_eur()
        if s:
            return s, False
        s = fetch_btc_eur_range(days=7)
        if s:
            return s, False

    # 30 d
    if window == "30d":
        s = fetch_btc_last_30d_eur()
        if s:
            return s, False
        s = fetch_btc_eur_range(days=30)
        if s:
            return s, False

        # fallback 7d
        s7 = fetch_btc_last_7d_eur()
        if s7:
            return s7, True

    # viimesijainen fallback: 7d mihin tahansa ikkunaan
    s7 = fetch_btc_last_7d_eur()
    if s7:
        return s7, (window != "7d")

    raise ValueError("BTC-historiasarjaa ei saatu mistään lähteestä.")


# ------------------------------------------------------------
#  UI-palaset (otsikko, footer)
# ------------------------------------------------------------


def build_window_pill(active: str, opt_code: str, label: str) -> str:
    is_active = opt_code == active
    base = (
        "display:inline-block;margin-left:8px;padding:2px 10px;border-radius:999px;"
        "font-size:.95rem;text-decoration:none;border:1px solid rgba(255,255,255,.18);font-weight:600;"
    )
    if is_active:
        style = base + "background:#e7eaee;color:#111;"
    else:
        style = base + "background:rgba(255,255,255,0.10);color:#e7eaee;"
    return f'<a href="?bwin={opt_code}" target="_self" style="{style}">{label}</a>'


def build_title_html(
    eur_now: float,
    change_24h: float | None,
    window: str,
) -> str:
    window_label = {
        "24h": "Viimeiset 24 h",
        "7d": "Viimeiset 7 päivää",
        "30d": "Viimeiset 30 päivää",
    }.get(window, "Viimeiset 7 päivää")

    title_html = (
        "🪙 Bitcoin "
        + build_window_pill(window, "24h", "24 h")
        + build_window_pill(window, "7d", "7 d")
        + build_window_pill(window, "30d", "30 d")
    )

    if change_24h is not None:
        is_up = change_24h >= 0
        badge_bg = COLOR_GREEN if is_up else COLOR_RED
        sign = "+" if is_up else ""
        change_fmt = f"{sign}{change_24h:.2f}%"
        badge_text = f"{eur_now:,.0f}".replace(",", " ") + f" € {change_fmt} (24 h)"
        title_html += (
            f" <span style='background:{badge_bg}; color:#000; padding:2px 10px; "
            f"border-radius:10px; font-weight:700; font-size:0.95rem'>{badge_text}</span>"
        )

    title_html += (
        f" <span style='background:{COLOR_GRAY}; color:{COLOR_TEXT_GRAY}; padding:2px 10px; "
        "border-radius:999px; font-weight:600; font-size:0.95rem'>"
        f"{window_label}</span>"
    )

    return title_html


def build_footer_html(
    window: str,
    degraded: bool,
    ath_eur: float | None,
    ath_date: str | None,
) -> str:
    ath_info = (
        f" {ath_date[:10]}, {ath_eur:,.0f} €".replace(",", " ") if ath_eur and ath_date else ""
    )
    extra = ""
    if window == "30d" and degraded:
        extra = " &nbsp;|&nbsp; Näytetään 7 d (30 d data ei saatavilla)"
    if window == "24h" and degraded:
        extra = " &nbsp;|&nbsp; Viimeiset 24 h viipaloitu 7 d -datasta"

    return (
        f"<div class='hint' style='margin-top:4px;'>💎 ATH{ath_info} (pun. katkoviiva){extra}</div>"
    )


# ------------------------------------------------------------
#  Plotly-kuvaaja
# ------------------------------------------------------------


def _y_axis_range(
    ys: Iterable[float],
    ath_eur: float | None,
) -> tuple[float | None, float | None, float | None]:
    ys = list(ys)
    if not ys:
        return None, None, None

    data_min = min(ys)
    data_max = max(max(ys), ath_eur or -float("inf"))

    pad_abs = (
        max(BTC_Y_PAD_EUR, (data_max - data_min) * BTC_Y_PAD_PCT)
        if BTC_Y_USE_PCT_PAD
        else BTC_Y_PAD_EUR
    )
    low = data_min - pad_abs
    high = data_max + pad_abs
    step = max(100.0, float(BTC_Y_STEP_EUR))
    y_min = int(math.floor(low / step) * step)
    y_max = int(math.ceil(high / step) * step)
    return y_min, y_max, step


def build_btc_figure(
    series: list[tuple[datetime, float]],
    window: str,
    ath_eur: float | None,
    ath_date: str | None,
) -> go.Figure:
    xs = [t for t, _ in series]
    ys = [v for _, v in series]

    if window == "24h":
        name = "BTC/EUR (24 h)"
        hover = "%{x|%H:%M} — %{y:.0f} €"
        dtick = 3 * 60 * 60 * 1000  # 3 h ms
        tickformat = "%H:%M"
    elif window == "30d":
        name = "BTC/EUR (30 d)"
        hover = "%{x|%d.%m} — %{y:.0f} €"
        dtick = "D2"
        tickformat = "%d.%m"
    else:
        name = "BTC/EUR (7 d)"
        hover = "%{x|%d.%m %H:%M} — %{y:.0f} €"
        dtick = "D1"
        tickformat = "%d.%m"

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=xs,
            y=ys,
            mode="lines",
            name=name,
            hovertemplate=hover + "<extra></extra>",
        )
    )

    # ATH katkoviivana
    if ath_eur:
        x0 = xs[0] if xs else datetime.now(TZ)
        x1 = xs[-1] if xs else datetime.now(TZ)
        fig.add_trace(
            go.Scatter(
                x=[x0, x1],
                y=[ath_eur, ath_eur],
                mode="lines",
                name=f"ATH {ath_eur:,.0f} €",
                line=dict(dash="dot"),
                hovertemplate="ATH — %{y:.0f} € (%{x|%d.%m})<extra></extra>",
            )
        )

    # y-akseli
    y_min, y_max, step = _y_axis_range(ys, ath_eur)
    if y_min is not None:
        fig.update_yaxes(range=[y_min, y_max], tick0=y_min, dtick=step)
    else:
        fig.update_yaxes(autorange=True)

    # hintalappu oikeaan laitaan
    if xs and ys:
        label_text = f"{ys[-1]:,.0f}".replace(",", " ") + " €"
        fig.add_annotation(
            x=xs[-1],
            y=ys[-1],
            xref="x",
            yref="y",
            text=label_text,
            showarrow=False,
            xanchor="right",
            align="right",
            xshift=-12,
            font=dict(color="#e7eaee", size=12),
        )

    fig.update_layout(
        margin=dict(l=64, r=12, t=8, b=32),
        height=210,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        font=dict(size=12, color="#e7eaee"),
        xaxis=dict(
            type="date",
            title=None,
            gridcolor="rgba(255,255,255,0.28)",
            tickformat=tickformat,
            dtick=dtick,
            tickfont=dict(size=11, color="#cfd3d8"),
            automargin=True,
        ),
        yaxis=dict(
            title="€",
            gridcolor="rgba(255,255,255,0.28)",
            tickfont=dict(size=11, color="#cfd3d8"),
            tickformat="~s",
            fixedrange=True,
            automargin=True,
        ),
        hoverlabel=dict(font_size=11),
    )

    return fig
