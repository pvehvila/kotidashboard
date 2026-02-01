from __future__ import annotations

from base64 import b64encode

import streamlit as st

from src.api import fetch_eth_ath_eur, fetch_eth_eur
from src.config import COLOR_GREEN, COLOR_RED
from src.paths import asset_path
from src.ui.common import section_title


def card_ethereum_ticker() -> None:
    """Render a compact Ethereum price card (logo, price, 24h change)."""
    title_html = "💎 ATH"
    svg_uri = ""
    try:
        svg_path = asset_path("ethereum-eth-icon.svg")
        svg_uri = f"data:image/svg+xml;base64,{b64encode(svg_path.read_bytes()).decode('ascii')}"
    except Exception:
        svg_uri = ""

    try:
        ath_eur, ath_date = fetch_eth_ath_eur()
        if ath_eur is not None and ath_date:
            date_txt = ath_date[:10]
            value_txt = f"{ath_eur:,.0f} €".replace(",", " ")
            title_html = (
                "<span style='display:inline-block; white-space:nowrap; font-size:0.9rem;'>"
                "💎 ATH "
                f"<span style='color:#9aa5b1; font-weight:600;'>{date_txt}</span> "
                f"<span style='color:#8ab4f8; font-weight:700;'>{value_txt}</span>"
                "</span>"
            )
    except Exception:
        pass

    try:
        eth_data = fetch_eth_eur()
        eur_now = eth_data.get("price")
        change_24h = eth_data.get("change")
        if eur_now is None:
            price_fmt = "—"
        else:
            price_fmt = f"{eur_now:,.0f}".replace(",", " ") + " €"

        if change_24h is not None:
            is_up = change_24h >= 0
            color = COLOR_GREEN if is_up else COLOR_RED
            sign = "+" if is_up else ""
            arrow = "▲" if is_up else "▼"
            change_html = (
                f"<span style='color:{color}; font-weight:700;'>{arrow} {sign}{change_24h:.2f}%</span>"
                " <span class='hint'>(24 h)</span>"
            )
        else:
            change_html = "<span class='hint'>— (24 h)</span>"

        bg_img = (
            f"<img src='{svg_uri}' style='position:absolute; inset:0; width:100%; height:100%; "
            "object-fit:contain; opacity:0.28;'/>"
            if svg_uri
            else ""
        )
        body_html = f"""
        <div style="position:relative; height:100%;">
          {bg_img}
          <div style="
            position:absolute; top:10px; left:0; right:0; text-align:center;
            font-size:1.6rem; font-weight:800; line-height:1.2; z-index:1;">
            {price_fmt}
          </div>
          <div style="
            position:absolute; bottom:8px; left:0; right:0; text-align:center;
            font-size:0.9rem; line-height:1.2; z-index:1;">
            {change_html}
          </div>
        </div>
        """
        section_title(title_html, mt=10, mb=4)
        st.markdown(
            f"""
            <section class="card" style="height:232px; min-height:232px; box-sizing:border-box; position:relative; overflow:hidden; padding:0 !important;">
              <div class="card-body" style="position:relative; height:100%; padding:0;">
                {body_html}
              </div>
            </section>
            """,
            unsafe_allow_html=True,
        )
    except Exception as e:
        section_title(title_html, mt=10, mb=4)
        st.markdown(
            f"""
            <section class="card" style="height:232px; min-height:232px; box-sizing:border-box; position:relative; overflow:hidden; padding:0 !important;">
              <div class="card-body" style="position:relative; height:100%; padding:0;">
                <span class='hint'>Virhe: {e}</span>
              </div>
            </section>
            """,
            unsafe_allow_html=True,
        )
