# main.py
"""Main entry point for the HomeDashboard Streamlit application."""
import streamlit as st

from config import PLOTLY_CONFIG
from ui import (
    card_bitcoin,
    card_nameday,
    card_prices,
    card_system,
    card_weather,
    card_zen,
    load_css,
)


def st_autorefresh(
    interval: int | None = None, key: str | None = None, **kwargs
) -> None:
    """Fallback implementation for auto-refreshing the Streamlit page.

    Args:
        interval: Refresh interval in milliseconds (None to disable).
        key: Unique key for the refresh script (unused in fallback).
        **kwargs: Additional arguments (ignored).
    """
    if interval:
        st.markdown(
            f"<script>setTimeout(() => window.location.reload(), {int(interval)});</script>",
            unsafe_allow_html=True,
        )


def main() -> None:
    """Initialize and render the HomeDashboard layout."""
    # Configure Streamlit page settings
    st.set_page_config(
        page_title="Kotidashboard",
        layout="wide",
        page_icon="🏠",
    )
    load_css("style.css")
    st_autorefresh(interval=60_000, key="refresh")

    # Row 1: Nameday and Zen quote
    col1, col2 = st.columns(2, gap="small")
    with col1:
        card_nameday()
    with col2:
        card_zen()

    # Row 2: Weather
    card_weather()

    # Row 3: Electricity prices
    card_prices()

    # Row 4: Bitcoin
    card_bitcoin()

    # Row 5: System status
    card_system()


if __name__ == "__main__":
    main()
