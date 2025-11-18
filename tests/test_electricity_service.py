# tests/test_electricity_service.py
import datetime as dt

import src.api.electricity_service as es
import src.api.electricity_service as svc


def test_fetch_prices_for_uses_primary_first(monkeypatch):
    day = dt.date(2025, 11, 11)

    # ensisijainen lähde palauttaa
    monkeypatch.setattr(
        "src.api.electricity_service.get_hourly_from_porssisahko",
        lambda d: [{"hour": 0, "cents": 5.0}],
    )
    # varalähde ei saisi edes tulla kutsutuksi, mutta annetaan tyhjä
    monkeypatch.setattr(
        "src.api.electricity_service.get_hourly_from_sahkonhintatanaan",
        lambda d: [],
    )

    out = svc.fetch_prices_for(day)
    assert out == [{"hour": 0, "cents": 5.0}]


def test_fetch_prices_for_falls_back_to_sahkonhintatanaan(monkeypatch):
    day = dt.date(2025, 11, 11)

    monkeypatch.setattr(
        "src.api.electricity_service.get_hourly_from_porssisahko",
        lambda d: [],
    )
    monkeypatch.setattr(
        "src.api.electricity_service.get_hourly_from_sahkonhintatanaan",
        lambda d: [{"hour": 1, "cents": 10.0}],
    )

    out = svc.fetch_prices_for(day)
    assert out == [{"hour": 1, "cents": 10.0}]


def test_try_fetch_prices_15min_prefers_direct_15min(monkeypatch):
    day = dt.date(2025, 11, 11)

    direct = [
        {"ts": dt.datetime(2025, 11, 11, 0, 0), "cents": 5.0},
        {"ts": dt.datetime(2025, 11, 11, 0, 15), "cents": 5.5},
    ]

    monkeypatch.setattr(
        "src.api.electricity_service.get_15min_from_porssisahko",
        lambda d: direct,
    )
    # jos tämä kutsuttaisiin, se palauttaisi tyhjää
    monkeypatch.setattr(
        "src.api.electricity_service.fetch_prices_for",
        lambda d: [],
    )

    out = svc.try_fetch_prices_15min(day)
    # Pylance: varmistetaan ensin ettei None
    assert out is not None
    assert out == direct


def test_try_fetch_prices_15min_expands_hourly_when_no_ts(monkeypatch):
    day = dt.date(2025, 11, 11)

    # ei suoraa 15 min dataa
    monkeypatch.setattr(
        "src.api.electricity_service.get_15min_from_porssisahko",
        lambda d: None,
    )
    # mutta tuntidata löytyy (ilman aikaleimaa)
    monkeypatch.setattr(
        "src.api.electricity_service.fetch_prices_for",
        lambda d: [{"hour": 0, "cents": 5.0}],
    )

    out = svc.try_fetch_prices_15min(day)

    # 1) ei saa olla None
    assert out is not None
    # 2) pitää olla lista
    assert isinstance(out, list)
    # 3) jokaisella rivillä on ts ja cents ja oikea päivä
    for row in out:
        assert "ts" in row
        assert "cents" in row
        ts = row["ts"]
        assert isinstance(ts, dt.datetime)
        assert ts.date() == day

    # 4) ensimmäinen hinta on se, jonka annoimme
    assert out[0]["cents"] == 5.0
    # 5) ja listassa on vähintään yksi rivi
    assert len(out) >= 1


def test_try_fetch_prices_returns_none_when_no_prices(monkeypatch):
    def fake_fetch(_date):
        return []

    monkeypatch.setattr(es, "fetch_prices_for", fake_fetch)

    out = es.try_fetch_prices(dt.date(2023, 1, 1))
    assert out is None


def test_try_fetch_prices_15min_returns_none_when_no_sources(monkeypatch):
    def fake_get_15min(_date):
        return None

    def fake_fetch_prices_for(_date):
        return []

    monkeypatch.setattr(es, "get_15min_from_porssisahko", fake_get_15min)
    monkeypatch.setattr(es, "fetch_prices_for", fake_fetch_prices_for)

    out = es.try_fetch_prices_15min(dt.date(2023, 1, 1))
    assert out is None


# tests/test_electricity_service.py


def test_try_fetch_prices_15min_when_only_hourly_returns_none(monkeypatch):
    def fake_get_15min(_date):
        # pakotetaan fallback-haara
        return None

    base_items = [
        {"timestamp": dt.datetime(2023, 1, 1, 0, 0), "price": 1.0},
        {"timestamp": dt.datetime(2023, 1, 1, 0, 15), "price": 2.0},
    ]

    def fake_fetch_prices_for(_date):
        return base_items

    # varmistetaan vain, ettei normalizea kutsuta vahingossa;
    # jos kutsutaan, tämä kaataa testin → havaitsemme muutoksen
    def fake_normalize(items, date):  # pragma: no cover - ei pitäisi kutsua nykykoodilla
        raise AssertionError(
            "normalize_prices_list_15min should not be called in current implementation"
        )

    monkeypatch.setattr(es, "get_15min_from_porssisahko", fake_get_15min)
    monkeypatch.setattr(es, "fetch_prices_for", fake_fetch_prices_for)
    monkeypatch.setattr(es, "normalize_prices_list_15min", fake_normalize)

    out = es.try_fetch_prices_15min(dt.date(2023, 1, 1))
    # NYKYKÄYTTÄYTYMINEN: palauttaa None
    assert out is None
