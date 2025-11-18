# tests/test_bitcoin.py
from __future__ import annotations

import importlib
import json
from datetime import datetime, timedelta

import pytest

import src.api.bitcoin as btc

# ---------------------------------------------------------------------------
# Otetaan streamlit-cache pois ja ladataan bitcoin.py uudestaan
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def no_streamlit_cache(monkeypatch):
    # tee st.cache_data:sta no-op ENNEN kuin moduulin dekorointia käytetään
    def _noop_cache(*args, **kwargs):
        def _decorator(func):
            return func

        return _decorator

    # patchataan olemassa oleva btc.st.cache_data
    monkeypatch.setattr(btc.st, "cache_data", _noop_cache)
    # ladataan moduuli uudelleen, jotta decoratorit ajetaan tällä no-opilla
    importlib.reload(btc)
    yield


# ---------------------------------------------------------------------------
# Perus extract -funktioiden testit
# ---------------------------------------------------------------------------


def test_extract_coingecko_prices_ok():
    raw = {
        "prices": [
            [1731300000000, 65000.0],
            [1731300600000, 65100.5],
            ["bad", 123],  # tämä pitää suodattaa pois
            [1731301200000, "65200"],  # string → float
        ]
    }
    out = btc._extract_coingecko_prices(raw)
    # vain 3 kelvollista
    assert len(out) == 3
    assert out[0] == (1731300000000, 65000.0)
    assert out[-1][1] == 65200.0


def test_extract_cryptocompare_prices_ok():
    raw = {
        "Data": {
            "Data": [
                {"time": 1731300000, "close": 65000.0},
                {"time": 1731303600, "close": 65100.0, "high": 65200.0},
                {"time": 1731307200, "high": 65300.0},  # close puuttuu → high
                "bad",
            ]
        }
    }
    out = btc._extract_cryptocompare_prices(raw)
    assert len(out) == 3
    # kolmannessa käytettiin high-arvoa
    assert out[2] == (1731307200, 65300.0)


# ---------------------------------------------------------------------------
# _to_dashboard_from_ms ja _to_dashboard_from_unix
# ---------------------------------------------------------------------------


def test_to_dashboard_from_ms_downsamples_to_days():
    # tehdään 2 päivän verran tiheää dataa
    tz = btc.TZ
    prices_ms = []
    base = datetime(2025, 11, 10, tzinfo=tz)
    for i in range(0, 200):  # 200 pistettä
        ts_ms = int((base + timedelta(minutes=10 * i)).timestamp() * 1000)
        prices_ms.append((ts_ms, 60000.0 + i))

    out = btc._to_dashboard_from_ms(prices_ms, days=2)
    # target_points = max(24*2, 24) = 48 → pitäisi olla noin 48 pistettä
    assert 30 <= len(out) <= 60
    # aikajärjestys
    assert out[0][0] < out[-1][0]


def test_to_dashboard_from_unix_keeps_positive_only():
    tz = btc.TZ
    prices_unix = [
        (1731300000, 65000.0),
        (1731303600, 0.0),  # tämä suodatetaan pois
        (1731307200, 65100.0),
    ]
    out = btc._to_dashboard_from_unix(prices_unix)
    assert len(out) == 2
    assert all(isinstance(t, datetime) for t, _ in out)
    assert all(v > 0 for _, v in out)
    # järjestys
    assert out[0][0].tzinfo == tz


# ---------------------------------------------------------------------------
# _btc_market_chart – onnistunut coingecko ja fallback cryptocompare
# ---------------------------------------------------------------------------


def test_btc_market_chart_prefers_coingecko(monkeypatch):
    # 1) coingecko palauttaa kelvollisen datan → cryptocomparea ei tarvita
    cg_raw = {
        "prices": [
            [1731300000000, 65000.0],
            [1731303600000, 65100.0],
        ]
    }

    called_cc = {"value": False}

    def fake_cg(days, vs):
        return cg_raw

    def fake_cc(days, vs):
        called_cc["value"] = True
        return {}

    monkeypatch.setattr(btc, "_get_coingecko_market_chart", fake_cg)
    monkeypatch.setattr(btc, "_get_cryptocompare_histohour", fake_cc)

    out = btc._btc_market_chart(1, vs="eur")
    assert len(out) == 2
    # varmista ettei cryptocompareen menty
    assert called_cc["value"] is False


def test_btc_market_chart_falls_back_to_cryptocompare(monkeypatch):
    # 1) coingecko kaatuu → 2) cryptocompare antaa datan
    def fake_cg(days, vs):
        raise RuntimeError("429")

    cc_raw = {
        "Data": {
            "Data": [
                {"time": 1731300000, "close": 65000.0},
                {"time": 1731303600, "close": 65100.0},
            ]
        }
    }

    monkeypatch.setattr(btc, "_get_coingecko_market_chart", fake_cg)
    monkeypatch.setattr(btc, "_get_cryptocompare_histohour", lambda d, v: cc_raw)

    out = btc._btc_market_chart(1, vs="eur")
    assert len(out) == 2
    # tulee unix → konvertoituu datetimeksi
    assert isinstance(out[0][0], datetime)


# ---------------------------------------------------------------------------
# fetch_btc_eur_range – hours → days muunto
# ---------------------------------------------------------------------------


def test_fetch_btc_eur_range_hours_converted_to_days(monkeypatch):
    # ohjataan sisäinen _btc_market_chart ja katsotaan mitä se saa argumentiksi
    called = {}

    def fake_chart(days, vs="eur"):
        called["days"] = days
        return []

    monkeypatch.setattr(btc, "_btc_market_chart", fake_chart)

    btc.fetch_btc_eur_range(hours=26)  # pitäisi mennä 2 päivää
    assert called["days"] == 2

    btc.fetch_btc_eur_range(hours=5)  # min 1 päivä
    assert called["days"] == 1


# ---------------------------------------------------------------------------
# fetch_btc_eur – yksinkertainen happy path
# ---------------------------------------------------------------------------


def test_fetch_btc_eur_happy(monkeypatch):
    def fake_http(url, timeout=None):
        return {"bitcoin": {"eur": 65000.0, "eur_24h_change": 1.23}}

    monkeypatch.setattr(btc, "http_get_json", fake_http)

    out = btc.fetch_btc_eur()
    assert out["price"] == 65000.0
    assert out["change"] == 1.23


def test_fetch_btc_eur_missing_fields(monkeypatch):
    # CoinGecko palauttaa tyhjää
    monkeypatch.setattr(btc, "http_get_json", lambda *a, **k: {})

    out = btc.fetch_btc_eur()
    # ei saa kaatua ja avaimet pitää olla
    assert "price" in out and "change" in out
    assert out["price"] is None
    assert out["change"] is None


# ---------------------------------------------------------------------------
# fetch_btc_ath_eur – sekä verkosta että cachesta
# ---------------------------------------------------------------------------


def test_fetch_btc_ath_eur_from_network_and_writes_cache(monkeypatch, tmp_path):
    ath_file = tmp_path / "ath.json"
    monkeypatch.setattr(btc, "ATH_CACHE_FILE", ath_file)

    def fake_http(url, timeout=None):
        return {
            "market_data": {
                "ath": {"eur": 69000.0},
                "ath_date": {"eur": "2021-11-10T15:00:00Z"},
            }
        }

    monkeypatch.setattr(btc, "http_get_json", fake_http)

    ath_val, ath_date = btc.fetch_btc_ath_eur()
    assert ath_val == 69000.0
    assert ath_date == "2021-11-10T15:00:00Z"

    # cache kirjoitettu
    cached = json.loads(ath_file.read_text(encoding="utf-8"))
    assert cached["ath_eur"] == 69000.0


def test_fetch_btc_ath_eur_uses_local_cache_on_http_error(monkeypatch, tmp_path):
    ath_file = tmp_path / "ath.json"
    ath_file.write_text(
        json.dumps({"ath_eur": 68000.0, "ath_date": "2021-11-09T13:00:00Z"}),
        encoding="utf-8",
    )
    monkeypatch.setattr(btc, "ATH_CACHE_FILE", ath_file)

    class FakeHTTPError(Exception):
        pass

    # simuloi 429 tms.
    monkeypatch.setattr(
        btc, "http_get_json", lambda *a, **k: (_ for _ in ()).throw(FakeHTTPError("429"))
    )
    # bitcoin.py tekee except requests.HTTPError: ...
    monkeypatch.setattr(btc, "requests", btc.requests)
    monkeypatch.setattr(btc.requests, "HTTPError", FakeHTTPError)

    ath_val, ath_date = btc.fetch_btc_ath_eur()
    assert ath_val == 68000.0
    assert ath_date == "2021-11-09T13:00:00Z"


# ---------------------------------------------------------------------------
# Lisätestejä: market_chart-virhetilanteet ja wrapperit
# ---------------------------------------------------------------------------


def test_btc_market_chart_returns_empty_when_all_providers_fail(monkeypatch):
    def fake_cg(days, vs):
        raise RuntimeError("cg down")

    def fake_cc(days, vs):
        raise RuntimeError("cc down")

    monkeypatch.setattr(btc, "_get_coingecko_market_chart", fake_cg)
    monkeypatch.setattr(btc, "_get_cryptocompare_histohour", fake_cc)

    out = btc._btc_market_chart(1, vs="eur")
    assert out == []


def test_fetch_btc_last_wrappers_use_market_chart(monkeypatch):
    called = []

    def fake_chart(days, vs="eur"):
        called.append((days, vs))
        # Palautetaan yksinkertainen dummy-data
        return [("dummy-ts", 123.0)]

    monkeypatch.setattr(btc, "_btc_market_chart", fake_chart)

    d24 = btc.fetch_btc_last_24h_eur()
    d7 = btc.fetch_btc_last_7d_eur()
    d30 = btc.fetch_btc_last_30d_eur()

    assert d24 == [("dummy-ts", 123.0)]
    assert d7 == [("dummy-ts", 123.0)]
    assert d30 == [("dummy-ts", 123.0)]

    # Varmistetaan että päivät menevät oikein wrapperien läpi
    assert (1, "eur") in called
    assert (7, "eur") in called
    assert (30, "eur") in called
