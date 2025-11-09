# src/utils.py
"""General-purpose utility functions for the HomeDashboard application."""

import streamlit as st

from src.config import DEV


def report_error(ctx: str, e: Exception) -> None:
    """Log errors to console and, in DEV mode, display them in the Streamlit UI."""
    print(f"[ERR] {ctx}: {type(e).__name__}: {e}")
    if DEV:
        st.caption(f"⚠ {ctx}: {type(e).__name__}: {e}")
