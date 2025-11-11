# tests/test_electricity_sources.py
import datetime as dt

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
