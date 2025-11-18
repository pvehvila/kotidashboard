# tests/test_wmo_icon_map.py
import src.api.wmo_icon_map as w


def test_wmo_to_icon_key_valid_codes():
    assert w.wmo_to_icon_key(0, True) == "clear-day"
    assert w.wmo_to_icon_key(0, False) == "clear-night"
    assert w.wmo_to_icon_key(61, True) == "rain"
    assert w.wmo_to_icon_key(95, False) == "thunderstorm"


def test_wmo_to_icon_key_unknown_code_returns_na():
    assert w.wmo_to_icon_key(999, True) == "na"
    assert w.wmo_to_icon_key(999, False) == "na"


def test_wmo_to_icon_key_none_returns_na():
    assert w.wmo_to_icon_key(None, True) == "na"
    assert w.wmo_to_icon_key(None, False) == "na"
