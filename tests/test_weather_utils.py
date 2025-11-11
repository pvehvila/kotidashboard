# tests/test_weather_utils.py
from __future__ import annotations

import src.api.weather_utils as wu


def test_as_bool_various_inputs():
    assert wu.as_bool(True) is True
    assert wu.as_bool(False) is False
    assert wu.as_bool(1) is True
    assert wu.as_bool(0) is False
    assert wu.as_bool("true") is True
    assert wu.as_bool("False") is False
    # tuntematon string → None
    assert wu.as_bool("maybe") is None
    # None → None
    assert wu.as_bool(None) is None


def test_as_int_and_as_float():
    assert wu.as_int(10) == 10
    assert wu.as_int(10.9) == 10
    assert wu.as_int("12") == 12
    assert wu.as_int(None) is None

    assert wu.as_float(10) == 10.0
    assert wu.as_float("10.5") == 10.5
    assert wu.as_float(None) is None


def test_cloud_icon_from_cover_can_be_forced(monkeypatch):
    # pakotetaan modulissa käytetyt rajat mataliksi, jotta saadaan kaikki haarat helposti
    monkeypatch.setattr(wu, "CLOUD_T_CLEAR", 10, raising=False)
    monkeypatch.setattr(wu, "CLOUD_T_ALMOST", 20, raising=False)
    monkeypatch.setattr(wu, "CLOUD_T_PARTLY", 40, raising=False)
    monkeypatch.setattr(wu, "CLOUD_T_MOSTLY", 70, raising=False)

    assert wu.cloud_icon_from_cover(0, True) == "d000"
    assert wu.cloud_icon_from_cover(15, True) == "d100"
    assert wu.cloud_icon_from_cover(30, True) == "d200"
    assert wu.cloud_icon_from_cover(60, True) == "d300"
    assert wu.cloud_icon_from_cover(90, True) == "d400"

    # yö
    assert wu.cloud_icon_from_cover(0, False) == "n000"


def test_safe_cast_basic():
    assert wu.safe_cast("true", bool) is True
    assert wu.safe_cast("12,5", float) == 12.5
    assert wu.safe_cast("12,0", int) == 12
    assert wu.safe_cast("maybe", bool) is None
