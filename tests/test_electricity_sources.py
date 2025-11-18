# tests/test_electricity_sources.py
import datetime as dt

import src.api.electricity_sources as es
from src.api.electricity_sources import filter_latest_to_day


def test_filter_latest_to_day_groups_by_hour_and_day():
    day = dt.date(2025, 11, 11)

    # kaksi itemiä samalle tunnille samana päivänä + yksi seuraavalle päivälle
    items = [
        {"startDate": "2025-11-11T07:00:00Z", "price": 5.0},
        {"startDate": "2025-11-11T07:15:00Z", "price": 6.0},
        {"startDate": "2025-11-12T07:00:00Z", "price": 99.0},
    ]

    out = filter_latest_to_day(items, day)

    # UTC 07 -> Helsinki 09
    assert 9 in out
    assert out[9] == [5.0, 6.0]
    # seuraavan päivän rivi ei saa olla mukana
    assert len(out.keys()) == 1


def test_fetch_from_sahkonhintatanaan_dict_with_prices(monkeypatch):
    date = dt.date(2023, 1, 1)

    def fake_http_get_json(url: str):
        assert "sahkonhintatanaan" in url
        return {"prices": [{"hour": 0, "cents": 5.0}]}

    monkeypatch.setattr(es, "http_get_json", fake_http_get_json)

    out = es.fetch_from_sahkonhintatanaan(date)
    assert out == [{"hour": 0, "cents": 5.0}]


def test_fetch_from_sahkonhintatanaan_dict_without_prices_returns_empty(monkeypatch):
    date = dt.date(2023, 1, 1)

    def fake_http_get_json(_url: str):
        return {"foo": "bar"}

    monkeypatch.setattr(es, "http_get_json", fake_http_get_json)

    out = es.fetch_from_sahkonhintatanaan(date)
    assert out == []


def test_fetch_from_sahkonhintatanaan_list_and_none(monkeypatch):
    date = dt.date(2023, 1, 1)
    calls: list[int] = []

    def fake_http_get_json(_url: str):
        # ensimmäinen kutsu: lista, toinen: None
        if not calls:
            calls.append(1)
            return [{"hour": 0, "cents": 3.0}]
        return None

    monkeypatch.setattr(es, "http_get_json", fake_http_get_json)

    out1 = es.fetch_from_sahkonhintatanaan(date)
    out2 = es.fetch_from_sahkonhintatanaan(date)

    assert out1 == [{"hour": 0, "cents": 3.0}]
    assert out2 == []


def test_filter_latest_to_day_skips_invalid_and_other_dates():
    tz_date = dt.date(2023, 1, 1)

    items = [
        # puuttuva startDate
        {"price": 1.0},
        # puuttuva price
        {"startDate": "2023-01-01T00:00:00Z"},
        # väärä muoto → except-haara
        {"startDate": "not-a-datetime", "price": 2.0},
        # eri päivä
        {"startDate": "2023-01-02T00:00:00Z", "price": 3.0},
    ]

    out = es.filter_latest_to_day(items, tz_date)
    assert out == {}


# tests/test_electricity_sources.py


def test_filter_latest_to_day_collects_prices_for_matching_day():
    date = dt.date(2023, 1, 1)

    items = [
        {"startDate": "2023-01-01T00:00:00Z", "price": 1.0},
        {"startDate": "2023-01-01T00:15:00Z", "price": 2.0},
        {"startDate": "2023-01-01T01:00:00Z", "price": 3.0},
    ]

    out = es.filter_latest_to_day(items, date)

    # talviaikana (UTC+2) nämä ovat tunteja 2 ja 3
    assert set(out.keys()) == {2, 3}
    # tunti 2: kaksi varttia, tunti 3: yksi
    assert out[2] == [1.0, 2.0]
    assert out[3] == [3.0]
