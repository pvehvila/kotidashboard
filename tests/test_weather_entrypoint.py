# tests/test_weather_entrypoint.py
from __future__ import annotations

from src.api import weather


def test_get_weather_for_dashboard_delegates_to_fetch(monkeypatch):
    called = {}

    def fake_fetch(lat, lon, tz_name, offsets=(0, 3, 6, 9, 12)):
        called["args"] = (lat, lon, tz_name, offsets)
        return {"points": [], "min_temp": None, "max_temp": None}

    monkeypatch.setattr(weather, "fetch_weather_points", fake_fetch)

    out = weather.get_weather_for_dashboard(60.7, 24.7, "Europe/Helsinki")
    assert out == {"points": [], "min_temp": None, "max_temp": None}
    assert called["args"][0] == 60.7
    assert called["args"][1] == 24.7
    assert called["args"][2] == "Europe/Helsinki"
