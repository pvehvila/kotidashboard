import datetime as dt
import json

import src.api.calendar as cal
import src.api.calendar_nameday as caln
import src.api.nameday as nd

# ------------------------------------------------------------------
# Aputyökalut cachetuille funktioille
# ------------------------------------------------------------------


def _clear_calendar_caches():
    # streamlitin @st.cache_data -funktioilla on .clear()
    for fn in (cal.fetch_nameday_today, cal.fetch_holiday_today):
        try:
            fn.clear()
        except Exception:
            pass
    # ja samoin wrapperille, jos UI käyttää sitä
    for fn in (caln.fetch_nameday_today, caln.fetch_holiday_today):
        try:
            fn.clear()
        except Exception:
            pass


# ------------------------------------------------------------------
# calendar.py – nimipäivät
# ------------------------------------------------------------------


def test_fetch_nameday_today_from_nested(monkeypatch, tmp_path):
    _clear_calendar_caches()
    data = {"nimipäivät": {"marraskuu": {"11": "Panu"}}}
    f = tmp_path / "nimipaivat.json"
    f.write_text(json.dumps(data), encoding="utf-8")

    monkeypatch.setattr(cal, "_resolve_nameday_file", lambda: f)

    result = cal.fetch_nameday_today(_cache_buster=1)
    assert result == "Panu"


def test_fetch_nameday_today_file_missing(monkeypatch, tmp_path):
    _clear_calendar_caches()
    monkeypatch.setattr(cal, "_resolve_nameday_file", lambda: tmp_path / "missing.json")
    result = cal.fetch_nameday_today(_cache_buster=2)
    assert result == "—"


def test_fetch_nameday_today_handles_error(monkeypatch):
    _clear_calendar_caches()
    monkeypatch.setattr(cal, "_resolve_nameday_file", lambda: 1 / 0)
    out = cal.fetch_nameday_today(_cache_buster=3)
    assert out == "—"


# ------------------------------------------------------------------
# calendar.py – pyhät / liputuspäivät
# ------------------------------------------------------------------


def test_fetch_holiday_today_flag(monkeypatch, tmp_path):
    _clear_calendar_caches()
    today = dt.datetime.now(cal.TZ)
    data = {
        today.strftime("%Y-%m-%d"): {
            "name": "Liputuspäivä",
            "flag": True,
        }
    }
    f = tmp_path / "pyhat.json"
    f.write_text(json.dumps(data), encoding="utf-8")

    monkeypatch.setattr(cal, "_resolve_first_existing", lambda _: f)

    out = cal.fetch_holiday_today(_cache_buster=4)
    assert out["holiday"] == "Liputuspäivä"
    assert out["is_flag_day"] is True
    # is_holiday voi olla False, joten ei lukita sitä täysin
    assert "is_holiday" in out


def test_fetch_holiday_today_missing(monkeypatch, tmp_path):
    _clear_calendar_caches()
    f = tmp_path / "does_not_exist.json"
    monkeypatch.setattr(cal, "_resolve_first_existing", lambda _: f)

    out = cal.fetch_holiday_today(_cache_buster=5)
    assert out == {"holiday": None, "is_flag_day": False, "is_holiday": False}


# ------------------------------------------------------------------
# calendar_nameday.py – varmista, että wrapper vie samat funktiot
# ------------------------------------------------------------------


def test_calendar_nameday_wrapper_uses_same_impl(monkeypatch, tmp_path):
    _clear_calendar_caches()
    data = {"nimipäivät": {"marraskuu": {"11": "Panu"}}}
    f = tmp_path / "nimipaivat.json"
    f.write_text(json.dumps(data), encoding="utf-8")

    # patchataan alkuperäinen kalenteri
    monkeypatch.setattr(cal, "_resolve_nameday_file", lambda: f)

    # kutsutaan wrapperia
    result = caln.fetch_nameday_today(_cache_buster=10)
    assert result == "Panu"


# ------------------------------------------------------------------
# nameday.py – helpompi, ei tarvita enää oikeaa tiedostoa
# ------------------------------------------------------------------


def test_nameday_finds_nimipaivat_via_load_json(monkeypatch):
    """Tämä moduli saa pysyä omanaan, mutta luetaan data suoraan ilman tiedostopolkuja."""
    data = {"nimipäivät": {"marraskuu": {"11": "Panu"}}}

    # ohitetaan koko tiedostonhaku
    monkeypatch.setattr(nd, "_load_json", lambda: data)

    # stubataan päiväksi 11.11.
    monkeypatch.setattr(nd, "date", lambda: None)  # pitää olla olemassa mutta sitä ei käytetä

    # helpoin tapa: patchataan date.today-kutsu moduulin sisällä
    class _D(dt.date):
        @classmethod
        def today(cls):
            return cls(2025, 11, 11)

    monkeypatch.setattr(nd, "date", _D)

    out = nd.fetch_nameday_today()
    assert out == "Panu"
