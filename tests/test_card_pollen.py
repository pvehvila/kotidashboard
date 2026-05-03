from __future__ import annotations

import importlib

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


def test_card_pollen_shows_error_card(monkeypatch):
    def boom():
        raise RuntimeError("pollen unavailable")

    called: list[tuple[str, str]] = []
    monkeypatch.setattr(card_pollen_module, "fetch_pollen_view", boom)
    monkeypatch.setattr(
        card_pollen_module, "card", lambda title, body: called.append((title, body))
    )

    card_pollen_module.card_pollen()

    assert called
    assert "Siitepöly" in called[0][0]
    assert "pollen unavailable" in called[0][1]
