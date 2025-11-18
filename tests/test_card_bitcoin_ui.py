from __future__ import annotations

import importlib
from datetime import datetime

from src.ui import card_bitcoin as card_bitcoin_fn  # tämä on FUNKTIO, ei moduuli

# Selvitetään moduuli, jossa funktio on määritelty (esim. "src.ui.card_bitcoin")
CB_MODULE_NAME = card_bitcoin_fn.__module__
cbm = importlib.import_module(CB_MODULE_NAME)


class DummySt:
    def __init__(self) -> None:
        # Streamlit-koodi käyttää näitä
        self.query_params: dict[str, str] = {}
        self.session_state: dict[str, object] = {}
        # ja näihin kerätään, jos halutaan tarkistaa myöhemmin
        self.plots: list[tuple[object, dict | None]] = []
        self.markdowns: list[str] = []

    def plotly_chart(self, fig, use_container_width=None, theme=None, config=None):
        self.plots.append((fig, config))

    def markdown(self, html: str, unsafe_allow_html: bool = False):
        self.markdowns.append(html)


def test_card_bitcoin_runs_happy_path(monkeypatch):
    """Peruspolku: kortti renderöityy ilman poikkeusta."""

    dummy_st = DummySt()
    dummy_st.query_params = {"bwin": "24h"}

    # Patchataan moduulin st suoraan moduuliobjektiin
    monkeypatch.setattr(cbm, "st", dummy_st, raising=False)

    # Mockataan API- ja datankeruufunktiot
    monkeypatch.setattr(
        cbm,
        "fetch_btc_eur",
        lambda: {"price": 65000.0, "change": 2.5},
        raising=False,
    )
    monkeypatch.setattr(
        cbm,
        "get_btc_series_for_window",
        lambda window: ([(datetime(2025, 1, 1), 65000.0)], False),
        raising=False,
    )
    monkeypatch.setattr(
        cbm,
        "fetch_btc_ath_eur",
        lambda: (69000.0, "2021-11-10T15:00:00Z"),
        raising=False,
    )

    # annetaan build_* -funktioiden juosta normaalisti
    # (niitä testataan tarkemmin test_card_bitcoin_parts.py:ssä)

    # Jos funktio ei nosta poikkeusta, happy path on ok
    card_bitcoin_fn()


def test_card_bitcoin_shows_error_card_on_failure(monkeypatch):
    """Virhepolku: fetch_btc_eur palauttaa virheellisen datan → card()-virhekortti kutsutaan."""

    dummy_st = DummySt()
    dummy_st.query_params = {}  # käytetään oletusikkunaa

    monkeypatch.setattr(cbm, "st", dummy_st, raising=False)

    # Palautetaan None-hinta → korttilogiikan pitäisi tulkita tämä virheeksi
    monkeypatch.setattr(
        cbm,
        "fetch_btc_eur",
        lambda: {"price": None, "change": None},
        raising=False,
    )

    # Varmuuden vuoksi pehmennetään muut riippuvuudet (niiden ei pitäisi edes ehtiä ajautua)
    monkeypatch.setattr(
        cbm,
        "get_btc_series_for_window",
        lambda window: ([], False),
        raising=False,
    )
    monkeypatch.setattr(
        cbm,
        "fetch_btc_ath_eur",
        lambda: (None, None),
        raising=False,
    )

    card_calls: list[tuple[str, str, int | None]] = []

    def fake_card(title: str, body: str, height_dvh: int | None = None):
        card_calls.append((title, body, height_dvh))

    # Patchataan moduulin card-globaali (tämä on se, jota except-haara käyttää)
    monkeypatch.setattr(cbm, "card", fake_card, raising=False)

    card_bitcoin_fn()

    # Nyt virhepolun pitäisi olla kuljettu ja card() kutsuttu
    assert card_calls, "Virhekortin pitäisi renderöityä"
    title, body, height = card_calls[0]
    assert title == "Bitcoin (EUR)"
    assert "Virhe" in body
