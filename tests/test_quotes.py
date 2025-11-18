# tests/test_quotes.py

import src.api.quotes as q


# --- APUFUNKTIO ---
def _force_no_streamlit_cache(monkeypatch):
    """Korvaa @st.cache_data wrapperin, jotta testi ei cacheta tuloksia."""

    def identity_decorator(*args, **kwargs):
        def wrap(func):
            return func

        return wrap

    monkeypatch.setattr(q.st, "cache_data", identity_decorator)


# --------------------------
# 1) ZenQuotes OK → käytetään sitä
# --------------------------


def test_fetch_daily_quote_uses_zenquotes_first(monkeypatch):
    _force_no_streamlit_cache(monkeypatch)

    def fake_http_get_json(url, timeout=None):
        assert "zenquotes" in url
        return [{"q": "Hello Zen", "a": "Zen Master"}]

    monkeypatch.setattr(q, "http_get_json", fake_http_get_json)

    # varmistetaan ettei quotablea tai lokal fallbackia käytetä
    def fake_report_error(msg, exc):  # pragma: no cover
        raise AssertionError("report_error was called unexpectedly")

    monkeypatch.setattr(q, "report_error", fake_report_error)

    out = q.fetch_daily_quote("2025-01-01")

    assert out["text"] == "Hello Zen"
    assert out["author"] == "Zen Master"
    assert out["source"] == "zenquotes"


# --------------------------
# 2) ZenQuotes fail → Quotable OK
# --------------------------


def test_fetch_daily_quote_falls_back_to_quotable(monkeypatch):
    _force_no_streamlit_cache(monkeypatch)

    # Zen fail
    def fake_zen(url, timeout=None):
        raise RuntimeError("ZenQuotes API down")

    # Quotable OK
    def fake_quotable(url, timeout=None):
        assert "quotable" in url
        return {"content": "Quotable text", "author": "Quotable Author"}

    report_calls = []

    def fake_report_error(msg, exc):
        report_calls.append(msg)

    def fake_http_get_json(url, timeout=None):
        if "zenquotes" in url:
            return fake_zen(url, timeout)
        else:
            return fake_quotable(url, timeout)

    monkeypatch.setattr(q, "http_get_json", fake_http_get_json)
    monkeypatch.setattr(q, "report_error", fake_report_error)

    out = q.fetch_daily_quote("2025-01-02")

    assert out["text"] == "Quotable text"
    assert out["author"] == "Quotable Author"
    assert out["source"] == "quotable"

    # ZenQuotes virhe logitettiin
    assert any("zenquotes" in msg for msg in report_calls)


# --------------------------
# 3) ZenQuotes fail → Quotable fail → Local fallback
# --------------------------


def test_fetch_daily_quote_falls_back_to_local(monkeypatch):
    _force_no_streamlit_cache(monkeypatch)

    def fake_http_get_json(url, timeout=None):
        raise RuntimeError("API down")

    report_calls = []

    def fake_report_error(msg, exc):
        report_calls.append(msg)

    monkeypatch.setattr(q, "http_get_json", fake_http_get_json)
    monkeypatch.setattr(q, "report_error", fake_report_error)

    out = q.fetch_daily_quote("2025-01-03")

    # paikallinen sitaatti
    assert out["source"] == "local"
    assert "text" in out and out["text"]
    assert "author" in out

    # kahden API-lähteen virheet raportoitu
    assert len(report_calls) == 2
    assert any("zenquotes" in msg for msg in report_calls)
    assert any("quotable" in msg for msg in report_calls)
