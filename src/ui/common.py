# src/ui/common.py
from __future__ import annotations

import streamlit as st

from src.paths import asset_path


def load_css(file_name: str) -> None:
    path = asset_path(file_name)
    if not path.exists():
        return
    with path.open("r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def section_title(html: str, mt: int = 10, mb: int = 10) -> None:
    """Render a section title with customizable margins.

    Args:
        html: HTML content for the title.
        mt: Top margin in pixels (default: 10).
        mb: Bottom margin in pixels (default: 4).
    """
    st.markdown(
        f"<div class='section-title' style='margin:{mt}px 0 {mb}px 0'>{html}</div>",
        unsafe_allow_html=True,
    )


def card(title: str, body_html: str, height_dvh: int = 16) -> None:
    """Render a card with a title and HTML body.

    Args:
        title: Card title text.
        body_html: HTML content for the card body.
        height_dvh: Minimum height in dvh units (default: 16).
    """
    st.markdown(
        f"""
        <section class="card" style="min-height:{height_dvh}dvh; position:relative; overflow:hidden;">
          <div class="card-title">{title}</div>
          <div class="card-body">{body_html}</div>
        </section>
        """,
        unsafe_allow_html=True,
    )
