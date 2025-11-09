# src/ui/card_zen.py
from __future__ import annotations

import base64
from datetime import datetime

import streamlit as st

from src.api import fetch_daily_quote
from src.config import TZ
from src.paths import asset_path
from src.ui.common import card
from src.utils import report_error


def card_zen() -> None:
    """Render a card displaying the daily Zen quote (korkea kortti, sama tausta)."""
    try:
        today_iso = datetime.now(TZ).date().isoformat()
        quote = fetch_daily_quote(today_iso)
        quote_text = (quote.get("text") or "").strip()
        quote_author = (quote.get("author") or "").strip()

        bg_dataurl = None
        img_path = asset_path("zen-bg.png")
        if img_path.exists():
            try:
                with img_path.open("rb") as f:
                    bg_dataurl = "data:image/png;base64," + base64.b64encode(
                        f.read()
                    ).decode("ascii")
            except Exception as e:
                report_error("zen: load bg", e)

        overlay = "linear-gradient(rgba(11,15,20,0.55), rgba(11,15,20,0.55))"
        bg_layer = f"{overlay}, url('{bg_dataurl}')" if bg_dataurl else overlay

        html = f"""
            <section class="card card-top-equal" style="height:180px; position:relative; overflow:hidden; background-image:{bg_layer}; background-size:cover; background-position:center;">
              <div class="card-title">Päivän zen</div>
              <div class="card-body" style="display:flex; justify-content:center; align-items:center; text-align:center; flex:1;">
                <div style="margin:0; line-height:1.35;">
                  <em>“{quote_text}”</em>{(" — " + quote_author) if quote_author else ""}
                </div>
              </div>
            </section>
            """
        st.markdown(html, unsafe_allow_html=True)
    except Exception as e:
        card(
            "Päivän zen",
            f"<span class='hint'>Ei saatu tietoa: {e}</span>",
            height_dvh=12,
        )
