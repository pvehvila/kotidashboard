# tests/test_card_nameday_helpers.py
import datetime as dt
import json

from src.ui import card_nameday_helpers as h


def test_get_flag_info_ok(tmp_path, monkeypatch):
    p = tmp_path / "data" / "pyhat_fi.json"
    p.parent.mkdir(parents=True)
    p.write_text(
        json.dumps({"2024-11-11": {"flag": True, "name": "Testi"}}),
        encoding="utf-8",
    )

    # ohitetaan tiedostonhaku → käytetään tätä väliaikaista polkua
    monkeypatch.setattr("src.ui.card_nameday_helpers.find_pyhat_file", lambda: p)

    txt, dbg = h.get_flag_info(dt.datetime(2024, 11, 11))

    assert txt == "Testi"
    assert dbg is None


def test_get_flag_info_missing(tmp_path, monkeypatch):
    p = tmp_path / "data" / "pyhat_fi.json"
    p.parent.mkdir(parents=True)
    p.write_text(json.dumps({}), encoding="utf-8")

    monkeypatch.setattr("src.ui.card_nameday_helpers.find_pyhat_file", lambda: p)

    txt, dbg = h.get_flag_info(dt.datetime(2024, 11, 11))

    assert txt is None
    assert "Avainta 2024-11-11 ei ollut" in dbg
