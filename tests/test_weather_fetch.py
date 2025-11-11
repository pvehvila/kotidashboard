# tests/test_weather_fetch.py
from __future__ import annotations

from datetime import datetime

import src.api.weather_fetch as wf


class DummyDT(datetime):
    @classmethod
    def now(cls, tz=None):
        # 2025-11-11 klo 10:00 → sopii testidataan
        return datetime(2025, 11, 11, 10, 0, tzinfo=tz)


def _fake_hourly_payload():
    # luodaan tunnit: 10, 13, 16, 19, 22
    base = "2025-11-11T"
    times = [f"{base}{h:02d}:00" for h in (10, 13, 16, 19, 22)]
    return {
        "hourly": {
            "time": times,
            "temperature_2m": [5.0, 6.0, 7.0, 4.0, 3.0],
            "precipitation_probability": [10, 20, 30, 40, 50],
            "weathercode": [0, 1, 2, 3, 61],
            "cloudcover": [5, 20, 40, 60, 80],
            "is_day": [1, 1, 1, 0, 0],
        }
    }


def test_fetch_weather_points_happy_path(monkeypatch):
    # 1) mokataan aika
    monkeypatch.setattr(wf, "datetime", DummyDT)

    # 2) mokataan http_get_json
    monkeypatch.setattr(wf, "http_get_json", lambda url: _fake_hourly_payload())

    # 3) mokataan wmo → foreca ikonin koodi, koska emme halua oikeaa Excel-lukua tähän testiin
    monkeypatch.setattr(wf, "wmo_to_foreca_code", lambda *a, **k: "d000")

    out = wf.fetch_weather_points(
        lat=60.733,  # ei väliä
        lon=24.77,
        tz_name="Europe/Helsinki",
    )

    assert "points" in out
    points = out["points"]
    # viiden offsetin pitäisi löytyä
    assert len(points) == 5
    # ensimmäinen on "Nyt"
    assert points[0]["label"] == "Nyt"
    assert points[0]["hour"] == 10
    # ja kaikille tehtiin avaimet
    assert all("key" in p for p in points)

    # min/max pitäisi laskea samasta päivästä
    assert out["min_temp"] == 3.0  # alin listassa
    assert out["max_temp"] == 7.0  # ylin listassa


def test_fetch_weather_points_skips_missing_hours(monkeypatch):
    monkeypatch.setattr(wf, "datetime", DummyDT)

    payload = _fake_hourly_payload()
    # poistetaan viimeinen tunti, niin viimeinen offset ei löydy
    payload["hourly"]["time"].pop()
    payload["hourly"]["temperature_2m"].pop()
    payload["hourly"]["precipitation_probability"].pop()
    payload["hourly"]["weathercode"].pop()
    payload["hourly"]["cloudcover"].pop()
    payload["hourly"]["is_day"].pop()

    monkeypatch.setattr(wf, "http_get_json", lambda url: payload)
    monkeypatch.setattr(wf, "wmo_to_foreca_code", lambda *a, **k: "d000")

    out = wf.fetch_weather_points(60.7, 24.7, "Europe/Helsinki")
    points = out["points"]
    # nyt 22:00 puuttuu, joten 5 → 4
    assert len(points) == 4
