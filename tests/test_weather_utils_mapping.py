# tests/test_weather_mapping.py
from __future__ import annotations

import src.api.weather_mapping as wm


def test_wmo_to_foreca_code_none_returns_default_day(monkeypatch):
    # tracing pois ettei sotke
    monkeypatch.setattr(wm, "MAP_TRACE_ENABLED", False, raising=False)
    key = wm.wmo_to_foreca_code(
        code=None,
        is_day=True,
        pop=None,
        temp_c=None,
        cloudcover=None,
    )
    assert key == "d000"


def test_wmo_to_foreca_code_hits_mapping(monkeypatch):
    # mokataan load_wmo_foreca_map palauttamaan yksinkertainen taulu
    def fake_load():
        return {
            "day": {61: "d610"},
            "night": {61: "n610"},
        }

    monkeypatch.setattr(wm, "load_wmo_foreca_map", fake_load)
    monkeypatch.setattr(wm, "MAP_TRACE_ENABLED", False, raising=False)

    assert wm.wmo_to_foreca_code(61, True, pop=80, temp_c=5.0, cloudcover=90) == "d610"
    assert wm.wmo_to_foreca_code(61, False, pop=80, temp_c=5.0, cloudcover=90) == "n610"


def test_wmo_to_foreca_code_falls_back_to_cloud_cover(monkeypatch):
    # ei yhtään osumaa → cloud_icon_from_cover
    def fake_load():
        return {"day": {}, "night": {}}

    monkeypatch.setattr(wm, "load_wmo_foreca_map", fake_load)
    # ja vielä varmuuden vuoksi pakotetaan cloud-kynnykset
    import src.api.weather_utils as wu

    monkeypatch.setattr(wu, "CLOUD_T_CLEAR", 10, raising=False)
    monkeypatch.setattr(wu, "CLOUD_T_ALMOST", 20, raising=False)
    monkeypatch.setattr(wu, "CLOUD_T_PARTLY", 40, raising=False)
    monkeypatch.setattr(wu, "CLOUD_T_MOSTLY", 70, raising=False)

    key = wm.wmo_to_foreca_code(999, True, pop=0, temp_c=10, cloudcover=5)
    assert key == "d000"
