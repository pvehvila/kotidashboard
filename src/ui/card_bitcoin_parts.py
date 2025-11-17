from __future__ import annotations

import math
from collections.abc import Iterable
from dataclasses import dataclass
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


def _try_fetch_series_for_window(window: str) -> list[tuple[datetime, float]] | None:
    """Hae BTC-sarja pyydetylle ikkunalle (24h, 7d, 30d)."""
    if window == "24h":
        s = fetch_btc_last_24h_eur()
        if not s:
            s = fetch_btc_eur_range(hours=24)
        return s

    if window == "7d":
        s = fetch_btc_last_7d_eur()
        if not s:
            s = fetch_btc_eur_range(days=7)
        return s

    if window == "30d":
        s = fetch_btc_last_30d_eur()
        if not s:
            s = fetch_btc_eur_range(days=30)
        return s

    return None


def _build_24h_from_7d(
    now: datetime,
    series_7d: list[tuple[datetime, float]],
) -> tuple[list[tuple[datetime, float]], bool]:
    """
    Viipaloi 24h sarja 7d-datasta.

    Palauttaa (sarja, degraded):
      - degraded = True jos jouduttiin näyttämään koko 7d, koska 24h-ikkunasta ei
        saatu tarpeeksi pisteitä.
    """
    cutoff = now - timedelta(hours=24)
    s24 = [(t, v) for (t, v) in series_7d if t >= cutoff]
    if len(s24) >= 2:
        return s24, False
    return series_7d, True


def _fallback_7d(window: str) -> tuple[list[tuple[datetime, float]], bool]:
    """Viimesijainen fallback: hae 7d mihin tahansa ikkunaan."""
    s7 = fetch_btc_last_7d_eur()
    if s7:
        return s7, (window != "7d")
    raise ValueError("BTC-historiasarjaa ei saatu mistään lähteestä.")


def get_btc_series_for_window(window: str) -> tuple[list[tuple[datetime, float]], bool]:
    """
    Palauttaa (sarja, degraded).
    Sarja on aina aikajärjestyksessä.
    degraded = True jos jouduttiin käyttämään kapeampaa ikkunaa
    kuin mitä käyttäjä pyysi (esim. 30d → 7d).
    """
    now = datetime.now(TZ)

    # 24 h: ensin suoraan 24h-lähteet, sitten 7d->24h downsample
    if window == "24h":
        s = _try_fetch_series_for_window("24h")
        if s:
            return s, False

        s7 = _try_fetch_series_for_window("7d")
        if s7:
            return _build_24h_from_7d(now, s7)

    # 7 d
    if window == "7d":
        s = _try_fetch_series_for_window("7d")
        if s:
            return s, False

    # 30 d
    if window == "30d":
        s30 = _try_fetch_series_for_window("30d")
        if s30:
            return s30, False

        # fallback 7d
        s7 = _try_fetch_series_for_window("7d")
        if s7:
            return s7, True

    # Viimesijainen fallback: 7d mihin tahansa ikkunaan
    return _fallback_7d(window)


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
        f" {ath_date[:10]}, {ath_eur:,.0f} €".replace(",", " ")
        if ath_eur is not None and ath_date
        else ""
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


@dataclass
class BtcFigureVM:
    xs: list[datetime]
    ys: list[float]
    name: str
    hovertemplate: str
    x_dtick: int | str
    x_tickformat: str
    y_min: float | None
    y_max: float | None
    y_step: float | None
    ath_eur: float | None
    ath_date: str | None
    label_text: str | None


def get_btc_figure_vm(
    series: list[tuple[datetime, float]],
    window: str,
    ath_eur: float | None,
    ath_date: str | None,
) -> BtcFigureVM:
    """Viewmodel: kaikki datamuotoilu yhteen paikkaan."""
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

    y_min, y_max, step = _y_axis_range(ys, ath_eur)

    label_text = None
    if xs and ys:
        label_text = f"{ys[-1]:,.0f}".replace(",", " ") + " €"

    return BtcFigureVM(
        xs=xs,
        ys=ys,
        name=name,
        hovertemplate=hover,
        x_dtick=dtick,
        x_tickformat=tickformat,
        y_min=y_min,
        y_max=y_max,
        y_step=step,
        ath_eur=ath_eur,
        ath_date=ath_date,
        label_text=label_text,
    )


def build_btc_figure(
    series: list[tuple[datetime, float]],
    window: str,
    ath_eur: float | None,
    ath_date: str | None,
) -> go.Figure:
    vm = get_btc_figure_vm(series, window, ath_eur, ath_date)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=vm.xs,
            y=vm.ys,
            mode="lines",
            name=vm.name,
            hovertemplate=vm.hovertemplate + "<extra></extra>",
        )
    )

    # ATH katkoviivana
    if vm.ath_eur:
        x0 = vm.xs[0] if vm.xs else datetime.now(TZ)
        x1 = vm.xs[-1] if vm.xs else datetime.now(TZ)
        fig.add_trace(
            go.Scatter(
                x=[x0, x1],
                y=[vm.ath_eur, vm.ath_eur],
                mode="lines",
                name=f"ATH {vm.ath_eur:,.0f} €",
                line=dict(dash="dot"),
                hovertemplate="ATH — %{y:.0f} € (%{x|%d.%m})<extra></extra>",
            )
        )

    # y-akseli
    if vm.y_min is not None and vm.y_max is not None and vm.y_step is not None:
        fig.update_yaxes(range=[vm.y_min, vm.y_max], tick0=vm.y_min, dtick=vm.y_step)
    else:
        fig.update_yaxes(autorange=True)

    # hintalappu oikeaan laitaan
    if vm.xs and vm.ys and vm.label_text:
        fig.add_annotation(
            x=vm.xs[-1],
            y=vm.ys[-1],
            xref="x",
            yref="y",
            text=vm.label_text,
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
            tickformat=vm.x_tickformat,
            dtick=vm.x_dtick,
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
