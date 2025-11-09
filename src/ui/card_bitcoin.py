# src/ui/card_bitcoin.py
from __future__ import annotations

from datetime import datetime
import math

import plotly.graph_objects as go
import streamlit as st

from src.api import (
    fetch_btc_ath_eur,
    fetch_btc_eur,
    fetch_btc_last_24h_eur,
    fetch_btc_last_7d_eur,
    fetch_btc_last_30d_eur,
    fetch_btc_eur_range,
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
    PLOTLY_CONFIG,
    TZ,
)
from src.ui.common import section_title, card

# ------------------- BITCOIN CARD -------------------


def card_bitcoin() -> None:
    """Render a card displaying Bitcoin price with selectable history window (24h / 7d / 30d)."""
    try:
        # --- Luetaan valinta URL-kyselyparamista ja pidetään sessiossa ---
        qp = st.query_params
        if "bwin" in qp:
            raw = str(qp.get("bwin")).lower().strip()
            if raw in ("24h", "7d", "30d"):
                st.session_state["btc_window"] = raw

        if "btc_window" not in st.session_state:
            st.session_state["btc_window"] = "7d"  # oletus

        window = st.session_state["btc_window"]  # '24h' | '7d' | '30d'

        # --- Nykyhinta + 24h muutos ---
        btc_data = fetch_btc_eur()
        eur_now = btc_data.get("price")
        change_24h = btc_data.get("change")
        if eur_now is None:
            raise ValueError("Bitcoin-hinnan nouto CoinGeckosta epäonnistui.")

        # --- Apuri: hae aikasarja halutulle ikkunalle robustisti ---
        from datetime import timedelta

        def _get_series(win: str):
            """
            Palauttaa listan (ts, price) aikajärjestyksessä.
            Yrittää useita lähteitä ja degradoi järkevästi.
            """
            now = datetime.now(TZ)

            if win == "24h":
                s = fetch_btc_last_24h_eur()
                if s:
                    return s, False
                # geneerinen fallback
                s = fetch_btc_eur_range(hours=24)
                if s:
                    return s, False
                # viipaloi 7d → 24h
                s7 = fetch_btc_last_7d_eur()
                if s7:
                    cutoff = now - timedelta(hours=24)
                    s24 = [(t, v) for (t, v) in s7 if t >= cutoff]
                    return (s24 if len(s24) >= 2 else s7), (len(s24) < 2)

            if win == "7d":
                s = fetch_btc_last_7d_eur()
                if s:
                    return s, False
                s = fetch_btc_eur_range(days=7)
                if s:
                    return s, False

            if win == "30d":
                s = fetch_btc_last_30d_eur()
                if s:
                    return s, False
                s = fetch_btc_eur_range(days=30)
                if s:
                    return s, False
                # fallback 7d, merkitään degradaatioksi
                s7 = fetch_btc_last_7d_eur()
                if s7:
                    return s7, True

            # viimeinen oljenkorsi: 7d mihin tahansa ikkunaan
            s7 = fetch_btc_last_7d_eur()
            if s7:
                return s7, (win != "7d")
            raise ValueError("BTC-historiasarjaa ei saatu mistään lähteestä.")


        series, degraded = _get_series(window)

        # --- ATH-taso (sama kaikille ikkunoille) ---
        ath_eur, ath_date = fetch_btc_ath_eur()

        xs = [t for t, _ in series]
        ys = [v for _, v in series]

        # --- Otsikon pillerit: aktiivinen = vaalea harmaa, teksti tumma ---
        def pill(opt_code: str, label: str) -> str:
            is_active = opt_code == window
            base = (
                "display:inline-block;margin-left:8px;padding:2px 10px;border-radius:999px;"
                "font-size:.95rem;text-decoration:none;border:1px solid rgba(255,255,255,.18);font-weight:600;"
            )
            if is_active:
                style = base + "background:#e7eaee;color:#111;"
            else:
                style = base + "background:rgba(255,255,255,0.10);color:#e7eaee;"
            return (
                f'<a href="?bwin={opt_code}" target="_self" style="{style}">{label}</a>'
            )

        window_label = {
            "24h": "Viimeiset 24 h",
            "7d": "Viimeiset 7 päivää",
            "30d": "Viimeiset 30 päivää",
        }[window]

        title_html = (
            "🪙 Bitcoin "
            + pill("24h", "24 h")
            + pill("7d", "7 d")
            + pill("30d", "30 d")
        )

        # 24h-muutosbadgi (pidetään kuten ennen)
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

        # Lisätään valitun ikkunan pilleriotsikko harmaalla kapselilla lopuksi
        title_html += (
            f" <span style='background:{COLOR_GRAY}; color:{COLOR_TEXT_GRAY}; padding:2px 10px; "
            "border-radius:999px; font-weight:600; font-size:0.95rem'>"
            f"{window_label}</span>"
        )

        section_title(title_html, mt=10, mb=4)

        # --- Piirretään kuvaaja ---
        # Hover + tickit riippuen ikkunasta
        if window == "24h":
            name = "BTC/EUR (24 h)"
            hover = "%{x|%H:%M} — %{y:.0f} €"
            dtick = 3 * 60 * 60 * 1000  # 3 h millisekunteina
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

        # Y-akselin skaalaus kuten ennen
        if ys:
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
            fig.update_yaxes(range=[y_min, y_max], tick0=y_min, dtick=step)
        else:
            fig.update_yaxes(autorange=True)

        # Hintalappu oikeaan reunaan
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

        st.plotly_chart(fig, use_container_width=True, theme=None, config=PLOTLY_CONFIG)

        # ATH-vihje + mahdollinen degradaatioilmoitus
        ath_info = (
            f" {ath_date[:10]}, {ath_eur:,.0f} €".replace(",", " ")
            if ath_eur and ath_date
            else ""
        )
        extra = ""
        if window == "30d" and degraded:
            extra = " &nbsp;|&nbsp; Näytetään 7 d (30 d data ei saatavilla)"
        if window == "24h" and degraded:
            extra = " &nbsp;|&nbsp; Viimeiset 24 h viipaloitu 7 d -datasta"
        st.markdown(
            f"<div class='hint' style='margin-top:4px;'>💎 ATH{ath_info} (pun. katkoviiva){extra}</div>",
            unsafe_allow_html=True,
        )
        st.markdown("<div style='margin-top:6px;'></div>", unsafe_allow_html=True)

    except Exception as e:
        card("Bitcoin (EUR)", f"<span class='hint'>Virhe: {e}</span>", height_dvh=18)