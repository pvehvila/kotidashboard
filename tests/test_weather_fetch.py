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
    # tehdään tunnit: 10, 13, 16, 19, 22
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
    # 1) pakotetaan aika
    monkeypatch.setattr(wf, "datetime", DummyDT)
    # 2) pakotetaan HTTP-paluuarvo
    monkeypatch.setattr(wf, "http_get_json", lambda url: _fake_hourly_payload())
    # 3) ei haluta oikeaa ikonimappia
    monkeypatch.setattr(wf, "wmo_to_foreca_code", lambda *a, **k: "d000")

    out = wf.fetch_weather_points(
        lat=60.733,
        lon=24.77,
        tz_name="Europe/Helsinki",
    )

    assert "points" in out
    points = out["points"]

    # pitäisi tulla viisi offsetia
    assert len(points) == 5
    # ensimmäinen on "Nyt" ja klo 10
    assert points[0]["label"] == "Nyt"
    assert points[0]["hour"] == 10
    # kaikille tuli key
    assert all("key" in p for p in points)

    # päivälle lasketut min/max pitää tulla samasta listasta
    assert out["min_temp"] == 3.0
    assert out["max_temp"] == 7.0


def test_fetch_weather_points_skips_missing_hours(monkeypatch):
    monkeypatch.setattr(wf, "datetime", DummyDT)

    payload = _fake_hourly_payload()
    # poistetaan viimeinen tunti -> viimeinen offset ei löydy
    for key in (
        "time",
        "temperature_2m",
        "precipitation_probability",
        "weathercode",
        "cloudcover",
        "is_day",
    ):
        payload["hourly"][key].pop()

    monkeypatch.setattr(wf, "http_get_json", lambda url: payload)
    monkeypatch.setattr(wf, "wmo_to_foreca_code", lambda *a, **k: "d000")

    out = wf.fetch_weather_points(60.7, 24.7, "Europe/Helsinki")

    # nyt 5 → 4
    assert len(out["points"]) == 4
