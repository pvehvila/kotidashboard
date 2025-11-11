import importlib
from pathlib import Path

import src.api.quotes as quotes

# ------------------------
# Testit quotes.py-funktioille
# ------------------------


def _clear_quote_cache():
    # streamlitin @st.cache_data antaa .clear()
    if hasattr(quotes.fetch_daily_quote, "clear"):
        quotes.fetch_daily_quote.clear()


def test_fetch_daily_quote_prefers_zenquotes(monkeypatch):
    _clear_quote_cache()

    # 1. lähde palauttaa
    monkeypatch.setattr(
        quotes,
        "_from_zenquotes",
        lambda: {"text": "A", "author": "B", "source": "zenquotes"},
    )
    # tämä ei saisi edes tulla käytetyksi
    monkeypatch.setattr(
        quotes,
        "_from_quotable",
        lambda: {"text": "C", "author": "D", "source": "quotable"},
    )

    result = quotes.fetch_daily_quote("2025-11-11")

    assert result["source"] == "zenquotes"
    assert result["text"] == "A"


def test_fetch_daily_quote_uses_quotable_if_zenquotes_fails(monkeypatch):
    _clear_quote_cache()

    monkeypatch.setattr(quotes, "_from_zenquotes", lambda: None)
    monkeypatch.setattr(
        quotes,
        "_from_quotable",
        lambda: {"text": "Q", "author": "W", "source": "quotable"},
    )

    result = quotes.fetch_daily_quote("2025-11-11")

    assert result["source"] == "quotable"
    assert result["text"] == "Q"


def test_fetch_daily_quote_fallback_to_local(monkeypatch):
    _clear_quote_cache()

    monkeypatch.setattr(quotes, "_from_zenquotes", lambda: None)
    monkeypatch.setattr(quotes, "_from_quotable", lambda: None)

    result = quotes.fetch_daily_quote("2025-11-11")

    assert result["source"] == "local"
    assert "text" in result
    assert "author" in result


# ------------------------
# Testit card_zen.py -kortille
# ------------------------


def test_card_zen_renders_html(monkeypatch):
    """Varmistetaan, että kortin HTML oikeasti renderöidään."""
    # haetaan nimenomaan varsinainen moduuli, ei src.ui:n re-exporttaamaa funktiota
    zen_mod = importlib.import_module("src.ui.card_zen")

    called_html = {}

    def fake_markdown(html, unsafe_allow_html):
        called_html["html"] = html

    def fake_fetch_daily_quote(day_iso):
        return {"text": "Zen test", "author": "Tester"}

    # mockataan riippuvuudet moduuliin
    monkeypatch.setattr(zen_mod, "fetch_daily_quote", fake_fetch_daily_quote)
    monkeypatch.setattr(zen_mod.st, "markdown", fake_markdown)
    # asset_pathin pitää palauttaa polku-olio, jolla on .exists()
    monkeypatch.setattr(zen_mod, "asset_path", lambda name: Path("does-not-exist.png"))

    # kutsu korttia
    zen_mod.card_zen()

    assert "Päivän zen" in called_html["html"]
    assert "Zen test" in called_html["html"]
    assert "Tester" in called_html["html"]


def test_card_zen_handles_exception(monkeypatch):
    """Jos kortin sisällä tulee virhe, näytetään varakortti."""
    zen_mod = importlib.import_module("src.ui.card_zen")

    called = {}

    def fake_card(title, msg, height_dvh):
        called["title"] = title
        called["msg"] = msg

    def fake_fetch_daily_quote(day_iso):
        raise RuntimeError("API error")

    monkeypatch.setattr(zen_mod, "fetch_daily_quote", fake_fetch_daily_quote)
    monkeypatch.setattr(zen_mod, "card", fake_card)

    zen_mod.card_zen()

    assert called["title"] == "Päivän zen"
    assert "Ei saatu tietoa" in called["msg"]
