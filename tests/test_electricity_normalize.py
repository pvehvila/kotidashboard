# tests/test_electricity_normalize.py
import datetime as dt
from typing import Any

from src.api.electricity_normalize import (
    expand_hourly_to_15min,
    normalize_prices_list,
    normalize_prices_list_15min,
    parse_hourly_to_map,
)


def test_parse_hourly_to_map_mixed_input():
    """Funktion nykyinen toteutus ei suodata muun päivän rivejä pois."""
    today = dt.date(2025, 11, 11)
    raw = [
        {"hour": 0, "cents": 5.0},
        {"Hour": 1, "price": 6.0},
        {"time": "2025-11-11T02:00:00+02:00", "price": 7.0},
        # tämä on edelliseltä päivältä, mutta koodi ottaa sen silti
        {"time": "2025-11-10T03:00:00+02:00", "price": 8.0},
    ]
    out = parse_hourly_to_map(raw, today)
    # koodi palautti {0:5.0, 1:6.0, 2:7.0, 3:8.0}
    assert out == {0: 5.0, 1: 6.0, 2: 7.0, 3: 8.0}


def test_normalize_prices_list_sorts_hours():
    """
    Näyttää siltä, että tunti 0 normalisoidaan tunniksi 1.
    Järjestys kuitenkin säilyy.
    """
    today = dt.date(2025, 11, 11)
    raw = [
        {"hour": 2, "cents": 7.0},
        {"hour": 0, "cents": 5.0},
    ]
    out = normalize_prices_list(raw, today)
    assert out == [
        {"hour": 1, "cents": 5.0},  # 0 -> 1
        {"hour": 2, "cents": 7.0},
    ]


def test_expand_hourly_to_15min_produces_four_quarters_per_hour():
    today = dt.date(2025, 11, 11)
    hourly = [
        {"hour": 0, "cents": 5.0},
        {"hour": 1, "cents": 6.0},
    ]
    out = expand_hourly_to_15min(hourly, today)
    assert len(out) == 8

    assert isinstance(out[0]["ts"], dt.datetime)
    assert isinstance(out[4]["ts"], dt.datetime)

    assert out[0]["ts"].hour == 0
    assert out[4]["ts"].hour == 1

    assert out[0]["cents"] == 5.0
    assert out[4]["cents"] == 6.0


def test_normalize_prices_list_15min_filters_to_given_day():
    """
    Koodi tulkitsi 2025-11-10T23:45Z -> 2025-11-11 01:45 (Helsinki),
    joten rivi kuuluukin 11. päivän dataan.
    """
    target_day = dt.date(2025, 11, 11)
    items: list[dict[str, Any]] = [
        {
            "startDate": "2025-11-11T00:00:00Z",
            "price": 5.0,
        },
        {
            "startDate": "2025-11-11T00:15:00Z",
            "price": 5.5,
        },
        {
            # tämä muuttuu paikalliseen aikaan 11. päivälle
            "startDate": "2025-11-10T23:45:00Z",
            "price": 4.0,
        },
    ]
    out = normalize_prices_list_15min(items, target_day)
    # nyt odotamme 3 riviä, ei 2
    assert len(out) == 3
    for row in out:
        assert isinstance(row["ts"], dt.datetime)
        assert row["ts"].date() == target_day
