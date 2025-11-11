from __future__ import annotations

import src.api.weather_viewmodel as vm


def test_build_weather_view_delegates_and_formats(monkeypatch):
    called = {}
    fake_points = [{"label": "Nyt", "hour": 10, "key": "d000", "temp": 5, "pop": 10}]
    fake_weather = {"points": fake_points, "min_temp": 5.0, "max_temp": 6.0}

    def fake_fetch(lat, lon, tz_name, offsets):
        called["args"] = (lat, lon, tz_name, offsets)
        return fake_weather

    monkeypatch.setattr("src.api.weather_viewmodel.fetch_weather_points", fake_fetch)

    out = vm.build_weather_view("3 h")

    # palautusarvon rakenne
    assert set(out.keys()) == {"points", "min_temp", "max_temp", "interval", "offsets"}
    assert out["interval"] == "3 h"
    # viisi offsettia: (0,3,6,9,12)
    assert out["offsets"] == (0, 3, 6, 9, 12)
    # varmista delegointi
    assert called["args"][2] == "Europe/Helsinki"
    assert out["points"][0]["label"] == "Nyt"
