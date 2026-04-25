# tests/test_weather_mapping.py
from __future__ import annotations

import src.api.weather_utils as wu
import src.api.wmo_foreca_code as wf


def test_wmo_to_foreca_code_none_returns_default_day(monkeypatch):
    # tracing pois
    monkeypatch.setattr("src.api.wmo_foreca_code.trace_map", lambda *a, **k: None)

    key = wf.wmo_to_foreca_code(
        code=None,
        is_day=True,
        pop=None,
        temp_c=None,
        cloudcover=None,
    )
    assert key == "d000"


def test_wmo_to_foreca_code_uses_open_meteo_rain_before_file_mapping(monkeypatch):
    def fake_load():
        return {
            "day": {61: "d610"},
            "night": {61: "n610"},
        }

    monkeypatch.setattr(wf, "load_wmo_foreca_map", fake_load)
    monkeypatch.setattr("src.api.wmo_foreca_code.trace_map", lambda *a, **k: None)

    assert wf.wmo_to_foreca_code(61, True, pop=80, temp_c=5.0, cloudcover=90) == "d410"
    assert wf.wmo_to_foreca_code(61, False, pop=80, temp_c=5.0, cloudcover=90) == "n410"


def test_wmo_to_foreca_code_turns_cloudy_high_pop_into_rain(monkeypatch):
    def fake_load():
        return {"day": {}, "night": {}}

    monkeypatch.setattr(wf, "load_wmo_foreca_map", fake_load)
    monkeypatch.setattr("src.api.wmo_foreca_code.trace_map", lambda *a, **k: None)

    assert wf.wmo_to_foreca_code(3, False, pop=69, temp_c=3.0, cloudcover=90) == "n410"
    assert wf.wmo_to_foreca_code(3, False, pop=98, temp_c=2.0, cloudcover=90) == "n420"
    assert wf.wmo_to_foreca_code(3, False, pop=43, temp_c=1.0, cloudcover=80) == "n300"
    assert wf.wmo_to_foreca_code(3, True, pop=0, temp_c=2.0, cloudcover=20) == "d100"


def test_wmo_to_foreca_code_falls_back_to_cloud_cover(monkeypatch):
    def fake_load():
        return {"day": {}, "night": {}}

    monkeypatch.setattr(wf, "load_wmo_foreca_map", fake_load)
    monkeypatch.setattr("src.api.wmo_foreca_code.trace_map", lambda *a, **k: None)

    # pakotetaan kynnykset alas, jotta tulos on deterministinen
    monkeypatch.setattr(wu, "CLOUD_T_CLEAR", 10, raising=False)
    monkeypatch.setattr(wu, "CLOUD_T_ALMOST", 20, raising=False)
    monkeypatch.setattr(wu, "CLOUD_T_PARTLY", 40, raising=False)
    monkeypatch.setattr(wu, "CLOUD_T_MOSTLY", 70, raising=False)

    key = wf.wmo_to_foreca_code(999, True, pop=0, temp_c=10, cloudcover=5)
    assert key == "d000"
