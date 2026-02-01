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
    COLOR_TEXT_GRAY,
    TZ,
)

# ------------------------------------------------------------
#  Data & series
# ------------------------------------------------------------


def _try_fetch_series_for_window(window: str) -> list[tuple[datetime, float]] | None:
    """Hae BTC-sarja pyydetylle ikkunalle (24h, 7d, 30d, 1y)."""
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

    if window == "1y":
        return fetch_btc_eur_range(days=365)

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
    degraded on varattu mahdollisille future-fallbackeille.
    """
    now = datetime.now(TZ)

    if window == "1y":
        s = _try_fetch_series_for_window("1y")
        if s:
            return s, False
        raise ValueError("BTC-historiasarjaa ei saatu (1 v).")

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
#  UI-palaset (otsikko)
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
    eur_now: float | None = None,
    change_24h: float | None = None,
    window: str | None = None,
) -> str:
    # Uusi "Kryptot" -otsikko (kun parametreja ei annettu)
    if eur_now is None and change_24h is None and (window is None or window == "1y"):
        window_label = "Viimeiset 12 kk"
        title_html = (
            "Kryptot"
            " <span style='margin-left:8px; font-size:0.9rem;'>"
            "ATH: <span style='color:#4ade80; font-weight:700;'>- - -</span>"
            " &nbsp;|&nbsp; "
            "<span style='color:#f7931a; font-weight:700;'>BTC</span>"
            " · "
            "<span style='color:#8ab4f8; font-weight:700;'>ETH</span>"
            "</span>"
        )
        title_html += (
            f" <span style='background:{COLOR_GRAY}; color:{COLOR_TEXT_GRAY}; padding:2px 10px; "
            "border-radius:999px; font-weight:600; font-size:0.95rem'>"
            f"{window_label}</span>"
        )
        return title_html

    # Legacy-otsikko (24h/7d/30d)
    window = window or "7d"
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

    if eur_now is not None and change_24h is not None:
        is_up = change_24h >= 0
        badge_bg = "#5cd65c" if is_up else "#ff6666"
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


def _format_eur_tick(value: float) -> str:
    rounded = int(round(value / 200.0) * 200)
    return f"{rounded:,.0f}".replace(",", " ") + " €"


def _build_tick_vals(y_min: float, y_max: float, step: float) -> list[float]:
    if step <= 0:
        return []
    vals: list[float] = []
    v = float(y_min)
    for _ in range(2000):
        if v > y_max + 1e-6:
            break
        vals.append(v)
        v += step
    return vals


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
    extra_ys: Iterable[float] | None = None,
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
    elif window == "1y":
        name = "BTC/EUR (12 kk)"
        hover = "%{x|%d.%m.%Y} — %{y:.0f} €"
        dtick = "M1"
        tickformat = "%m/%y"
    else:
        name = "BTC/EUR (7 d)"
        hover = "%{x|%d.%m %H:%M} — %{y:.0f} €"
        dtick = "D1"
        tickformat = "%d.%m"

    ys_for_range = list(ys)
    if extra_ys:
        ys_for_range.extend(list(extra_ys))
    y_min, y_max, step = _y_axis_range(ys_for_range, ath_eur)

    label_text = None
    if xs and ys:
        label_text = "BTC " + f"{ys[-1]:,.0f}".replace(",", " ") + " €"

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
    eth_series: list[tuple[datetime, float]] | None = None,
    eth_scale: float | None = None,
) -> go.Figure:
    eth_scaled: list[tuple[datetime, float]] | None = None
    scale = eth_scale if eth_scale and eth_scale > 0 else None
    if eth_series and scale:
        eth_scaled = [(t, v * scale) for t, v in eth_series]

    extra_ys = [v for _, v in eth_scaled] if eth_scaled else None
    vm = get_btc_figure_vm(series, window, ath_eur, ath_date, extra_ys=extra_ys)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=vm.xs,
            y=vm.ys,
            mode="lines",
            name=vm.name,
            line=dict(color="#f7931a", width=2),
            hovertemplate=vm.hovertemplate + "<extra></extra>",
        )
    )
    if eth_series:
        fig.add_trace(
            go.Scatter(
                x=[t for t, _ in eth_series],
                y=[v for _, v in eth_series],
                mode="lines",
                name="ETH",
                yaxis="y2",
                line=dict(color="#8ab4f8", width=2),
                hovertemplate="%{x|%d.%m.%Y} — %{y:.0f} €<extra></extra>",
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
                line=dict(dash="dot", color="#4ade80", width=2),
                hovertemplate="ATH — %{y:.0f} € (%{x|%d.%m})<extra></extra>",
            )
        )

    # y-akseli (BTC)
    if vm.y_min is not None and vm.y_max is not None and vm.y_step is not None:
        tick_vals = _build_tick_vals(vm.y_min, vm.y_max, vm.y_step)
        tick_text = [_format_eur_tick(v) for v in tick_vals]
        fig.update_yaxes(
            range=[vm.y_min, vm.y_max],
            tickvals=tick_vals,
            ticktext=tick_text,
            title=dict(text="BTC €", font=dict(color="#f7931a")),
        )
    else:
        fig.update_yaxes(autorange=True)

    # y-akseli (ETH oikealla)
    if eth_series:
        y2_range = None
        y2_step = None
        y2_vals: list[float] | None = None
        y2_text: list[str] | None = None
        if vm.y_min is not None and vm.y_max is not None and scale:
            y2_range = [vm.y_min / scale, vm.y_max / scale]
            if vm.y_step is not None:
                y2_step = vm.y_step / scale
        else:
            eth_ys = [v for _, v in eth_series]
            y2_min, y2_max, y2_dtick = _y_axis_range(eth_ys, None)
            if y2_min is not None and y2_max is not None:
                y2_range = [y2_min, y2_max]
                y2_step = y2_dtick
        if y2_range is not None and y2_step is not None:
            y2_vals = _build_tick_vals(y2_range[0], y2_range[1], y2_step)
            y2_text = [_format_eur_tick(v) for v in y2_vals]
        fig.update_layout(
            yaxis2=dict(
                title=dict(text="ETH €", font=dict(color="#8ab4f8")),
                overlaying="y",
                side="right",
                showgrid=False,
                tickformat="~s",
                tickfont=dict(size=11, color="#cfd3d8"),
                range=y2_range,
                tickvals=y2_vals,
                ticktext=y2_text,
                fixedrange=True,
            )
        )

    fig.update_layout(
        margin=dict(l=64, r=46, t=8, b=32),
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
            title=dict(text="BTC €", font=dict(color="#f7931a")),
            gridcolor="rgba(255,255,255,0.28)",
            tickfont=dict(size=11, color="#cfd3d8"),
            tickformat="~s",
            fixedrange=True,
            automargin=True,
        ),
        hoverlabel=dict(font_size=11),
    )

    return fig
