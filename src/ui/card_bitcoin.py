from __future__ import annotations

import streamlit as st

from src.api import fetch_btc_ath_eur, fetch_btc_eur
from src.config import PLOTLY_CONFIG
from src.ui.card_bitcoin_parts import (
    build_btc_figure,
    build_footer_html,
    build_title_html,
    get_btc_series_for_window,
)
from src.ui.common import card, section_title


def _get_window_from_query() -> str:
    qp = st.query_params
    if "bwin" in qp:
        raw = str(qp.get("bwin")).lower().strip()
        if raw in ("24h", "7d", "30d"):
            st.session_state["btc_window"] = raw
    if "btc_window" not in st.session_state:
        st.session_state["btc_window"] = "7d"
    return st.session_state["btc_window"]  # type: ignore[return-value]


def card_bitcoin() -> None:
    """Renderöi Bitcoin-kortin, käyttäen apufunktioita erillisestä parts-tiedostosta."""
    try:
        window = _get_window_from_query()

        # nykyhinta + 24h muutos
        btc_data = fetch_btc_eur()
        eur_now = btc_data.get("price")
        change_24h = btc_data.get("change")
        if eur_now is None:
            raise ValueError("Bitcoin-hinnan nouto epäonnistui.")

        # historiasarja + degradaatio
        series, degraded = get_btc_series_for_window(window)

        # ATH
        ath_eur, ath_date = fetch_btc_ath_eur()

        # otsikko
        title_html = build_title_html(eur_now, change_24h, window)
        section_title(title_html, mt=10, mb=4)

        # kuvaaja
        fig = build_btc_figure(series, window, ath_eur, ath_date)
        st.plotly_chart(fig, use_container_width=True, theme=None, config=PLOTLY_CONFIG)

        # footer
        footer_html = build_footer_html(window, degraded, ath_eur, ath_date)
        st.markdown(footer_html, unsafe_allow_html=True)
        st.markdown("<div style='margin-top:6px;'></div>", unsafe_allow_html=True)

    except Exception as e:
        card("Bitcoin (EUR)", f"<span class='hint'>Virhe: {e}</span>", height_dvh=18)
