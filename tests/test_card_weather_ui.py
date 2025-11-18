from __future__ import annotations

import importlib

import pytest

from src.ui.card_weather import card_weather

card_weather_module = importlib.import_module("src.ui.card_weather")


class DummySt:
    """Kevyt stub streamlitille card_weather-testejä varten."""

    def __init__(self, query_params=None):
        self.query_params = query_params or {}
        self.session_state: dict[str, object] = {}


def test_card_weather_happy_path(monkeypatch):
    dummy_st = DummySt()
    monkeypatch.setattr(card_weather_module, "st", dummy_st)

    vm = {
        "min_temp": 1.2,
        "max_temp": 3.4,
        "points": [
            {"label": "Nyt", "hour": 12, "key": "d000", "temp": 2.0, "pop": 42},
            {"label": "14", "hour": 14, "key": "d000", "temp": 3.0, "pop": 10},
        ],
    }

    intervals: list[str] = []

    def fake_build_weather_view(interval: str):
        intervals.append(interval)
        return vm

    titles: list[str] = []
    rendered: dict[str, str] = {}

    monkeypatch.setattr(
        card_weather_module,
        "build_weather_view",
        fake_build_weather_view,
    )
    monkeypatch.setattr(
        card_weather_module,
        "render_foreca_icon",
        lambda key, size=48: f"<icon {key}>",
    )
    monkeypatch.setattr(
        card_weather_module,
        "section_title",
        lambda html, **kw: titles.append(html),
    )

    def fake_html(html: str, height: int, scrolling: bool) -> None:
        rendered["html"] = html
        rendered["height"] = str(height)
        rendered["scrolling"] = "true" if scrolling else "false"

    monkeypatch.setattr(card_weather_module, "st_html", fake_html)

    # act
    card_weather()

    # oletusinterval = "3 h"
    assert dummy_st.session_state["weather_interval"] == "3 h"
    assert intervals == ["3 h"]

    title = titles[0]
    assert "Sää — Riihimäki" in title
    assert "Tänään:" in title

    html = rendered["html"]
    assert "Nyt" in html
    assert "Sade 42%" in html
    assert rendered["height"] == "155"
    assert rendered["scrolling"] == "false"


def test_card_weather_respects_query_param(monkeypatch):
    dummy_st = DummySt(query_params={"wint": "6h"})
    monkeypatch.setattr(card_weather_module, "st", dummy_st)

    intervals: list[str] = []

    def fake_build_weather_view(interval: str):
        intervals.append(interval)
        return {"min_temp": None, "max_temp": None, "points": []}

    monkeypatch.setattr(
        card_weather_module,
        "build_weather_view",
        fake_build_weather_view,
    )
    monkeypatch.setattr(
        card_weather_module,
        "render_foreca_icon",
        lambda key, size=48: "",
    )
    monkeypatch.setattr(
        card_weather_module,
        "section_title",
        lambda *a, **k: None,
    )
    monkeypatch.setattr(card_weather_module, "st_html", lambda *a, **k: None)

    # act
    card_weather()

    # query-param "6h" → interval "6 h"
    assert dummy_st.session_state["weather_interval"] == "6 h"
    assert intervals == ["6 h"]


def test_card_weather_shows_error_card_on_exception(monkeypatch):
    dummy_st = DummySt()
    monkeypatch.setattr(card_weather_module, "st", dummy_st)

    def boom(interval: str):
        raise RuntimeError("oops")

    monkeypatch.setattr(card_weather_module, "build_weather_view", boom)

    called_cards: list[tuple[str, str]] = []

    def fake_card(title: str, body: str, **kwargs) -> None:
        called_cards.append((title, body))

    monkeypatch.setattr(card_weather_module, "card", fake_card)
    monkeypatch.setattr(card_weather_module, "section_title", lambda *a, **k: None)
    monkeypatch.setattr(
        card_weather_module,
        "st_html",
        lambda *a, **k: pytest.fail("st_html() ei pitäisi kutsua error-haarassa"),
    )

    # act
    card_weather()

    # assert
    assert called_cards, "Virhetilanteessa card() pitäisi kutsua"
    title, body = called_cards[0]
    assert "Sää — Riihimäki" in title
    assert "Virhe: oops" in body
