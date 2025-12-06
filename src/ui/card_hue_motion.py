from __future__ import annotations

import streamlit as st

from src.viewmodels.hue_motion import load_hue_motion_viewmodel


def card_hue_motion() -> None:
    """Piirtää ovien liikesensorit -kortin."""

    rows = load_hue_motion_viewmodel()

    st.markdown("### Ovien liikesensorit")

    # Yksi rivi per ovi
    for row in rows:
        col_name, col_status, col_time = st.columns([2, 2, 1])

        with col_name:
            st.write(row.name)

        with col_status:
            if row.active:
                # Vihreä “liike”-indikaattori
                st.markdown("**🟢 Liike**")
            else:
                st.markdown("⚪ Ei liikettä")

        with col_time:
            st.caption(row.last_updated_str)
