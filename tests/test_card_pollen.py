from __future__ import annotations

import importlib

import pytest
import requests

card_pollen_module = importlib.import_module("src.ui.card_pollen")


class DummySt:
    def __init__(self):
        self.markdowns: list[str] = []

    def markdown(self, html: str, unsafe_allow_html: bool = False) -> None:
        self.markdowns.append(html)


def test_card_pollen_renders_view(monkeypatch):
    dummy = DummySt()
    monkeypatch.setattr(card_pollen_module, "st", dummy)
    monkeypatch.setattr(card_pollen_module, "section_title", lambda *a, **k: None)
    monkeypatch.setattr(
        card_pollen_module,
        "fetch_pollen_view",
        lambda: {
            "location": "Riihimäki",
            "source": "Turun yliopiston siitepölytiedotus",
            "updated": "3.5.2026",
            "summary": "Ilmassa: Koivu",
            "plants": [
                {
                    "key": "koivu",
                    "name": "Koivu",
                    "level": "runsaasti",
                    "forecast_level": "runsaasti",
                    "forecast": "Koivun määrä pysyy runsaana.",
                },
                {
                    "key": "heinät",
                    "name": "Heinät",
                    "level": "ei havaittu",
                    "forecast_level": "ei havaittu",
                    "forecast": "Ei erillistä ennustetta.",
                },
            ],
        },
    )

    card_pollen_module.card_pollen()

    html = dummy.markdowns[0]
    assert "Koivu" in html
    assert "runsaasti" in html
    assert "Ennuste" in html
    assert "Allergeeni" in html
    assert "Ilmassa: Koivu" not in html
    assert "Turun yliopiston siitepölytiedotus" not in html
    assert "Koivun määrä pysyy runsaana." not in html
    assert html.count("Nyt") == 1
    assert html.count("Ennuste") == 1


@pytest.mark.parametrize(
    "error",
    [
        requests.Timeout("pollen timeout"),
        requests.ConnectionError("pollen unavailable"),
        requests.HTTPError("503 Service Unavailable"),
        RuntimeError("invalid pollen data"),
    ],
)
def test_card_pollen_shows_moon_on_fetch_error(monkeypatch, error):
    def boom():
        raise error

    dummy = DummySt()
    monkeypatch.setattr(card_pollen_module, "st", dummy)
    called = []
    monkeypatch.setattr(card_pollen_module, "fetch_pollen_view", boom)
    monkeypatch.setattr(card_pollen_module, "card_moon", lambda: called.append("moon"))

    card_pollen_module.card_pollen()

    assert called == ["moon"]
    assert dummy.markdowns == []


def test_card_pollen_shows_moon_when_no_current_pollen(monkeypatch):
    called = []
    monkeypatch.setattr(
        card_pollen_module,
        "fetch_pollen_view",
        lambda: {
            "plants": [
                {"level": "ei havaittu", "forecast_level": "runsaasti"},
                {"level": "ei havaittu", "forecast_level": "ei havaittu"},
            ]
        },
    )
    monkeypatch.setattr(card_pollen_module, "card_moon", lambda: called.append("moon"))

    card_pollen_module.card_pollen()

    assert called == ["moon"]


def test_card_pollen_does_not_treat_missing_data_as_no_pollen(monkeypatch):
    dummy = DummySt()
    monkeypatch.setattr(card_pollen_module, "st", dummy)
    monkeypatch.setattr(card_pollen_module, "section_title", lambda *a, **k: None)
    monkeypatch.setattr(card_pollen_module, "fetch_pollen_view", lambda: {"plants": []})
    called = []
    monkeypatch.setattr(card_pollen_module, "card_moon", lambda: called.append("moon"))

    card_pollen_module.card_pollen()

    assert called == []
    assert "pollen-card" in dummy.markdowns[0]
