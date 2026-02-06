from __future__ import annotations

import importlib


class DummySt:
    def __init__(self) -> None:
        self.markdowns: list[str] = []

    def markdown(self, html: str, unsafe_allow_html: bool = False) -> None:
        self.markdowns.append(html)


def test_card_bitcoin_ticker_happy_path(monkeypatch, tmp_path):
    card_mod = importlib.import_module("src.ui.card_bitcoin_ticker")

    dummy = DummySt()
    monkeypatch.setattr(card_mod, "st", dummy)

    captured: dict[str, str] = {}
    monkeypatch.setattr(
        card_mod,
        "section_title",
        lambda title, mt=None, mb=None: captured.setdefault("title", title),
    )

    svg_path = tmp_path / "btc.svg"
    svg_path.write_text("<svg></svg>", encoding="utf-8")
    monkeypatch.setattr(card_mod, "asset_path", lambda name: svg_path)

    monkeypatch.setattr(
        card_mod,
        "fetch_btc_ath_eur",
        lambda: (100000.0, "2024-01-01T00:00:00Z"),
    )
    monkeypatch.setattr(
        card_mod,
        "fetch_btc_eur",
        lambda: {"price": 12345.0, "change": 1.23},
    )

    card_mod.card_bitcoin_ticker()

    assert "2024-01-01" in captured["title"]
    assert "100 000" in captured["title"]
    html = "".join(dummy.markdowns)
    assert "12 345" in html
    assert "(24 h)" in html


def test_card_bitcoin_ticker_error(monkeypatch, tmp_path):
    card_mod = importlib.import_module("src.ui.card_bitcoin_ticker")

    dummy = DummySt()
    monkeypatch.setattr(card_mod, "st", dummy)
    monkeypatch.setattr(card_mod, "section_title", lambda *a, **k: None)

    svg_path = tmp_path / "btc.svg"
    svg_path.write_text("<svg></svg>", encoding="utf-8")
    monkeypatch.setattr(card_mod, "asset_path", lambda name: svg_path)

    monkeypatch.setattr(card_mod, "fetch_btc_ath_eur", lambda: (None, None))
    monkeypatch.setattr(
        card_mod,
        "fetch_btc_eur",
        lambda: (_ for _ in ()).throw(RuntimeError("boom")),
    )

    card_mod.card_bitcoin_ticker()

    html = "".join(dummy.markdowns)
    assert "Virhe" in html


def test_card_ethereum_ticker_happy_path(monkeypatch, tmp_path):
    card_mod = importlib.import_module("src.ui.card_ethereum_ticker")

    dummy = DummySt()
    monkeypatch.setattr(card_mod, "st", dummy)

    captured: dict[str, str] = {}
    monkeypatch.setattr(
        card_mod,
        "section_title",
        lambda title, mt=None, mb=None: captured.setdefault("title", title),
    )

    svg_path = tmp_path / "eth.svg"
    svg_path.write_text("<svg></svg>", encoding="utf-8")
    monkeypatch.setattr(card_mod, "asset_path", lambda name: svg_path)

    monkeypatch.setattr(
        card_mod,
        "fetch_eth_ath_eur",
        lambda: (5000.0, "2024-02-01T00:00:00Z"),
    )
    monkeypatch.setattr(
        card_mod,
        "fetch_eth_eur",
        lambda: {"price": 2345.0, "change": -1.5},
    )

    card_mod.card_ethereum_ticker()

    assert "2024-02-01" in captured["title"]
    assert "5 000" in captured["title"]
    html = "".join(dummy.markdowns)
    assert "2 345" in html
    assert "(24 h)" in html


def test_card_ethereum_ticker_error(monkeypatch, tmp_path):
    card_mod = importlib.import_module("src.ui.card_ethereum_ticker")

    dummy = DummySt()
    monkeypatch.setattr(card_mod, "st", dummy)
    monkeypatch.setattr(card_mod, "section_title", lambda *a, **k: None)

    svg_path = tmp_path / "eth.svg"
    svg_path.write_text("<svg></svg>", encoding="utf-8")
    monkeypatch.setattr(card_mod, "asset_path", lambda name: svg_path)

    monkeypatch.setattr(card_mod, "fetch_eth_ath_eur", lambda: (None, None))
    monkeypatch.setattr(
        card_mod,
        "fetch_eth_eur",
        lambda: (_ for _ in ()).throw(RuntimeError("boom")),
    )

    card_mod.card_ethereum_ticker()

    html = "".join(dummy.markdowns)
    assert "Virhe" in html
