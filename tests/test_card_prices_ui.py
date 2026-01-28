from __future__ import annotations

import importlib

import pytest

from src.ui.card_prices import card_prices

card_prices_module = importlib.import_module("src.ui.card_prices")


def test_card_prices_runs_happy_path(monkeypatch):
    vm = {
        "rows": [{"label": "10:00"}, {"label": "10:15"}],
        "current_cents": 4.2,
        "values": [4.2, 5.0],
        "colors": ["#00ff00", "#00ff00"],
        "line_colors": ["#000000", "#000000"],
        "line_widths": [1, 1],
        "y_min": -5.0,
        "y_max": 20.0,
        "y_step": 5.0,
    }

    # card_prices() → build_prices_15min_vm(...)
    monkeypatch.setattr(
        card_prices_module,
        "build_prices_15min_vm",
        lambda now_dt: vm,
    )

    titles: list[str] = []
    plots: list[object] = []
    markdowns: list[str] = []
    cards: list[tuple[str, str]] = []

    def fake_section_title(html: str, **kwargs) -> None:
        titles.append(html)

    def fake_plotly_chart(fig, **kwargs) -> None:
        plots.append(fig)

    def fake_markdown(html: str, unsafe_allow_html: bool = False) -> None:
        markdowns.append(html)

    def fake_card(title: str, body: str, **kwargs) -> None:
        cards.append((title, body))

    monkeypatch.setattr(card_prices_module, "section_title", fake_section_title)
    monkeypatch.setattr(card_prices_module.st, "plotly_chart", fake_plotly_chart)
    monkeypatch.setattr(card_prices_module.st, "markdown", fake_markdown)
    monkeypatch.setattr(card_prices_module, "card", fake_card)

    # act
    card_prices()  # funktio

    # assert
    assert titles, "section_title pitää kutsua"
    title_html = titles[0]
    assert "⚡ Pörssisähkö" in title_html
    assert "15 min" in title_html
    assert "4.20 snt/kWh" in title_html  # badge

    assert len(plots) == 1
    # ei fallback-korttia, koska rows ei tyhjä
    assert cards == []
    # värilegendan teksti
    assert any("≤ 5 snt" in m for m in markdowns)


def test_card_prices_shows_error_message_on_exception(monkeypatch):
    def boom(now_dt):
        raise RuntimeError("network down")

    monkeypatch.setattr(card_prices_module, "build_prices_15min_vm", boom)

    titles: list[str] = []
    messages: list[str] = []

    monkeypatch.setattr(
        card_prices_module,
        "section_title",
        lambda html, **kw: titles.append(html),
    )
    monkeypatch.setattr(
        card_prices_module.st,
        "markdown",
        lambda html, unsafe_allow_html=False: messages.append(html),
    )

    # varmistetaan, ettei virhepolulla käytetä card()-funktiota
    monkeypatch.setattr(
        card_prices_module,
        "card",
        lambda *a, **k: pytest.fail("card() ei pitäisi kutsua error-haarassa"),
    )

    # act
    card_prices()

    # assert
    assert titles == ["Pörssisähkö – seuraavat 12 h"]
    assert messages, "Virheviestin pitäisi mennä markdownilla"
    assert "Virhe hinnanhaussa: network down" in messages[0]
