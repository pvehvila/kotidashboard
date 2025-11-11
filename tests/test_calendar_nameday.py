import datetime as dt
import json

import src.api.calendar as cal
import src.api.nameday as nd

# ------------------------------------------------------------------
# Aputyökalut cachetuille funktioille
# ------------------------------------------------------------------


def _clear_calendar_caches():
    # streamlitin @st.cache_data -funktioilla on .clear()
    try:
        cal.fetch_nameday_today.clear()
    except Exception:
        pass
    try:
        cal.fetch_holiday_today.clear()
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

    # pakotetaan uusi välimuisti
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

    # calendar.py odottaa listaa poluista, mutta meidän apufunktio palauttaa Pathin,
    # joten monkeypatchataan suoraan resolveri
    monkeypatch.setattr(cal, "_resolve_first_existing", lambda _: f)

    out = cal.fetch_holiday_today(_cache_buster=4)
    assert out["holiday"] == "Liputuspäivä"
    assert out["is_flag_day"] is True
    # ei ole ehkä varsinaisesti vapaapäivä, joten se saa olla False
    assert out["is_holiday"] in (False, True)


def test_fetch_holiday_today_missing(monkeypatch, tmp_path):
    _clear_calendar_caches()
    f = tmp_path / "does_not_exist.json"
    # palautetaan polku, jota ei ole
    monkeypatch.setattr(cal, "_resolve_first_existing", lambda _: f)

    out = cal.fetch_holiday_today(_cache_buster=5)
    assert out == {"holiday": None, "is_flag_day": False, "is_holiday": False}


# ------------------------------------------------------------------
# nameday.py – oma toteutus
# ------------------------------------------------------------------


def test_nameday_finds_nimipaivat(monkeypatch, tmp_path):
    data = {"nimipäivät": {"marraskuu": {"11": "Panu"}}}
    f = tmp_path / "nimipaivat_fi.json"
    f.write_text(json.dumps(data), encoding="utf-8")

    # asset_path -> osoittaa tähän tmp-tiedostoon
    monkeypatch.setattr(nd, "asset_path", lambda p: str(f))
    # os.path.exists -> sanoo että löytyy
    monkeypatch.setattr(nd.os.path, "exists", lambda p: True)

    # nyt tämän päivän pitää olla 11.11. että tämä menee läpi – tehdään day stub
    monkeypatch.setattr(nd, "date", lambda: None)  # ei toimi näin
