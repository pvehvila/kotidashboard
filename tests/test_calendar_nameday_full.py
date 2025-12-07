# tests/test_calendar_nameday_full.py

import datetime as dt
import json

from src.api import calendar_nameday as api


def _freeze_today(monkeypatch, when: dt.datetime) -> None:
    """Korvaa calendar_nameday.dt.datetime.now palauttamaan halutun päivän."""

    class FrozenDateTime(dt.datetime):
        @classmethod
        def now(cls, tz=None):  # type: ignore[override]
            if tz is not None:
                if when.tzinfo is None:
                    return when.replace(tzinfo=tz)
                return when.astimezone(tz)
            return when

    # calendar_nameday teki: import datetime as dt → dt.datetime
    monkeypatch.setattr(api.dt, "datetime", FrozenDateTime)


def test_fetch_nameday_today_happy(tmp_path, monkeypatch):
    p = tmp_path / "names.json"
    p.write_text(json.dumps({"11-11": ["Panu"]}), encoding="utf-8")

    # ohjataan nimipäiväpolku tähän väliaikaiseen tiedostoon
    monkeypatch.setattr(api, "NAMEDAY_PATHS", [str(p)])

    fake_today = dt.datetime(2024, 11, 11, 12, 0, tzinfo=api.TZ)
    _freeze_today(monkeypatch, fake_today)

    # käytetään dekoroinnin alla olevaa alkuperäistä funktiota
    out = api.fetch_nameday_today.__wrapped__(_cache_buster=1)  # type: ignore[attr-defined]
    assert out == "Panu"


def test_fetch_nameday_today_missing_file(tmp_path, monkeypatch):
    # osoitetaan ei-olemassa olevaan tiedostoon → funktio palauttaa "—"
    monkeypatch.setattr(api, "NAMEDAY_PATHS", [str(tmp_path / "missing.json")])

    fake_today = dt.datetime(2024, 11, 11, 12, 0, tzinfo=api.TZ)
    _freeze_today(monkeypatch, fake_today)

    out = api.fetch_nameday_today.__wrapped__(_cache_buster=2)  # type: ignore[attr-defined]
    assert out == "—"


def test_fetch_holiday_today_happy(tmp_path, monkeypatch):
    p = tmp_path / "hol.json"
    p.write_text(
        json.dumps({"11-11": {"name": "X", "flag": True}}),
        encoding="utf-8",
    )

    monkeypatch.setattr(api, "HOLIDAY_PATHS", [str(p)])

    fake_today = dt.datetime(2024, 11, 11, 12, 0, tzinfo=api.TZ)
    _freeze_today(monkeypatch, fake_today)

    out = api.fetch_holiday_today.__wrapped__(_cache_buster=3)  # type: ignore[attr-defined]
    assert out["holiday"] == "X"
    assert out["is_flag_day"] is True
    assert "is_holiday" in out


def test_fetch_holiday_today_missing_file(tmp_path, monkeypatch):
    monkeypatch.setattr(api, "HOLIDAY_PATHS", [str(tmp_path / "missing.json")])

    fake_today = dt.datetime(2024, 11, 11, 12, 0, tzinfo=api.TZ)
    _freeze_today(monkeypatch, fake_today)

    out = api.fetch_holiday_today.__wrapped__(_cache_buster=4)  # type: ignore[attr-defined]
    assert out == {
        "holiday": None,
        "is_flag_day": False,
        "is_holiday": False,
    }
