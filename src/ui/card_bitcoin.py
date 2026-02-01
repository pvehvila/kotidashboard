from __future__ import annotations

import streamlit as st

from src.api import fetch_btc_ath_eur, fetch_eth_ath_eur, fetch_eth_eur_range
from src.config import PLOTLY_CONFIG
from src.ui.card_bitcoin_parts import (
    build_btc_figure,
    build_title_html,
    get_btc_series_for_window,
)
from src.ui.common import card, section_title


def card_bitcoin() -> None:
    """Renderöi Bitcoin-kortin, käyttäen apufunktioita erillisestä parts-tiedostosta."""
    try:
        window = "1y"

        # historiasarjat
        series, _ = get_btc_series_for_window(window)
        eth_series = fetch_eth_eur_range(days=365)
        if not series:
            raise ValueError("Bitcoin-hinnan nouto epäonnistui.")

        # ATH
        ath_eur, ath_date = fetch_btc_ath_eur()
        eth_ath_eur, _ = fetch_eth_ath_eur()
        eth_scale = None
        if ath_eur and eth_ath_eur and eth_ath_eur > 0:
            eth_scale = ath_eur / eth_ath_eur

        # otsikko
        title_html = build_title_html()
        section_title(title_html, mt=10, mb=4)

        # kuvaaja
        fig = build_btc_figure(
            series,
            window,
            ath_eur,
            ath_date,
            eth_series=eth_series,
            eth_scale=eth_scale,
        )
        st.plotly_chart(fig, use_container_width=True, theme=None, config=PLOTLY_CONFIG)

    except Exception as e:
        card("Bitcoin (EUR)", f"<span class='hint'>Virhe: {e}</span>", height_dvh=18)
