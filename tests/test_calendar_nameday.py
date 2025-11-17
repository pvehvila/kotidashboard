# tests/test_calendar_nameday.py
import datetime as dt
import json
from pathlib import Path

import src.api.calendar_nameday as caln
import src.api.nameday as nd

# --- apu ------------------------------------------------------------


def _clear_calendar_caches():
    """Tyhjentää cachetut Streamlit-funktiot, jotta testit saavat uudet arvot."""
    try:
        caln.fetch_nameday_today.clear()
    except Exception:
        pass
    try:
        caln.fetch_holiday_today.clear()
    except Exception:
        pass


def _set_fixed_today(monkeypatch):
    """
    Pakottaa calendar_nameday-moduulin 'tämän päivän' olemaan 11.11.2025.
    Tämä tekee testeistä deterministisiä.
    """

    class FixedDatetime(dt.datetime):
        @classmethod
        def now(cls, tz=None):  # type: ignore[override]
            # käytetään samaa TZ:tä, mutta päivä on aina 11.11.2025
            return cls(2025, 11, 11, 12, 0, 0, tzinfo=tz)

    # patchataan nimenomaan calendar_nameday:ssä käytetty dt.datetime
    monkeypatch.setattr(caln.dt, "datetime", FixedDatetime)


# --- nimipäivien testit --------------------------------------------


def test_fetch_nameday_today_from_nested(monkeypatch, tmp_path):
    """Tarkistaa, että sisäkkäinen nimipäivärakenne toimii oikein."""
    _set_fixed_today(monkeypatch)

    data = {"nimipäivät": {"marraskuu": {"11": "Panu"}}}
    f = tmp_path / "nimipaivat.json"
    f.write_text(json.dumps(data), encoding="utf-8")

    monkeypatch.setattr(caln, "_resolve_nameday_file", lambda: f)
    _clear_calendar_caches()

    result = caln.fetch_nameday_today(_cache_buster=1)
    assert result == "Panu"


def test_fetch_nameday_today_from_flat(monkeypatch, tmp_path):
    """Tarkistaa, että litteä JSON toimii myös."""
    _set_fixed_today(monkeypatch)

    data = {"11-11": ["Mauno", "Maunu"]}
    f = tmp_path / "nimipaivat.json"
    f.write_text(json.dumps(data), encoding="utf-8")

    monkeypatch.setattr(caln, "_resolve_nameday_file", lambda: f)
    _clear_calendar_caches()

    result = caln.fetch_nameday_today(_cache_buster=2)
    assert result == "Mauno, Maunu"


def test_fetch_nameday_today_file_missing(monkeypatch, tmp_path):
    """Jos tiedostoa ei ole, palauttaa '—'."""
    _set_fixed_today(monkeypatch)

    f = tmp_path / "puuttuu.json"
    monkeypatch.setattr(caln, "_resolve_nameday_file", lambda: f)
    _clear_calendar_caches()

    result = caln.fetch_nameday_today(_cache_buster=3)
    assert result == "—"


def test_fetch_nameday_today_handles_error(monkeypatch):
    """Jos tiedoston luku epäonnistuu, palauttaa '—' eikä kaadu."""
    _set_fixed_today(monkeypatch)

    def bad_loader(_):
        raise ValueError("boom")

    monkeypatch.setattr(caln, "_resolve_nameday_file", lambda: Path("fake.json"))
    monkeypatch.setattr(caln, "_load_nameday_data", bad_loader)
    _clear_calendar_caches()

    result = caln.fetch_nameday_today(_cache_buster=4)
    assert result == "—"


def test_pick_today_name_variants():
    """Testaa _pick_today_name suoraan eri muodoilla."""
    today = dt.datetime(2025, 11, 11)

    data_flat = {"11-11": ["Mauno", "Maunu"]}
    assert caln._pick_today_name(data_flat, today) == "Mauno, Maunu"

    data_nested = {"nimipäivät": {"marraskuu": {"11": "Panu"}}}
    assert caln._pick_today_name(data_nested, today) == "Panu"

    data_invalid = {"foo": "bar"}
    assert caln._pick_today_name(data_invalid, today) == "—"


def test_calendar_nameday_wrapper_uses_same_impl(monkeypatch, tmp_path):
    """Varmistaa, että calendar_nameday toimii odotetusti (patchataan suoraan caln)."""
    _set_fixed_today(monkeypatch)
    _clear_calendar_caches()

    data = {"nimipäivät": {"marraskuu": {"11": "Panu"}}}
    f = tmp_path / "nimipaivat.json"
    f.write_text(json.dumps(data), encoding="utf-8")

    # Patchataan calendar_nameday eikä calendar
    monkeypatch.setattr(caln, "_resolve_nameday_file", lambda: f)
    result = caln.fetch_nameday_today(_cache_buster=10)
    assert result == "Panu"


def test_nameday_wrapper_calls_calendar_nameday(monkeypatch, tmp_path):
    """Varmistaa, että nameday.fetch_nameday_today ohjaa calendar_nameday:lle."""
    _set_fixed_today(monkeypatch)

    data = {"nimipäivät": {"marraskuu": {"11": "Panu"}}}
    f = tmp_path / "nimipaivat.json"
    f.write_text(json.dumps(data), encoding="utf-8")

    monkeypatch.setattr(caln, "_resolve_nameday_file", lambda: f)
    _clear_calendar_caches()

    out = nd.fetch_nameday_today()
    assert out == "Panu"


# --- pyhä- ja liputuspäivät ----------------------------------------


def test_fetch_holiday_today_with_dict(monkeypatch, tmp_path):
    """Dict-muotoinen JSON palauttaa odotetun rakenteen."""
    _set_fixed_today(monkeypatch)

    data = {"11-11": {"name": "Isänpäivä", "flag": True, "is_holiday": True}}
    f = tmp_path / "holidays.json"
    f.write_text(json.dumps(data), encoding="utf-8")

    monkeypatch.setattr(caln, "_resolve_first_existing", lambda _: f)
    _clear_calendar_caches()

    out = caln.fetch_holiday_today(_cache_buster=11)
    assert out["holiday"] == "Isänpäivä"
    assert out["is_flag_day"] is True
    assert out["is_holiday"] is True


def test_fetch_holiday_today_with_list(monkeypatch, tmp_path):
    """List-muotoinen JSON toimii myös."""
    _set_fixed_today(monkeypatch)

    data = [{"date": "2025-11-11", "name": "Testipäivä", "flag": False, "is_holiday": True}]
    f = tmp_path / "holidays.json"
    f.write_text(json.dumps(data), encoding="utf-8")

    monkeypatch.setattr(caln, "_resolve_first_existing", lambda _: f)
    _clear_calendar_caches()

    out = caln.fetch_holiday_today(_cache_buster=12)
    assert out["holiday"] == "Testipäivä"
    assert out["is_holiday"] is True


def test_fetch_holiday_today_missing_file(monkeypatch, tmp_path):
    """Jos tiedostoa ei ole, palauttaa oletusrakenteen."""
    _set_fixed_today(monkeypatch)

    f = tmp_path / "missing.json"
    monkeypatch.setattr(caln, "_resolve_first_existing", lambda _: f)
    _clear_calendar_caches()

    out = caln.fetch_holiday_today(_cache_buster=13)
    assert out == {"holiday": None, "is_flag_day": False, "is_holiday": False}
