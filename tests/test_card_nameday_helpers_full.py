import base64
import json
from datetime import datetime
from pathlib import Path

import src.ui.card_nameday_helpers as h

# ----------------------------
# get_background_image()
# ----------------------------


def test_background_image_png(tmp_path, monkeypatch):
    # Luo feikkikuva
    p = tmp_path / "butterfly-bg.png"
    p.write_bytes(b"\x89PNGtest")

    # patchaa asset_path palauttamaan tämän tiedoston
    monkeypatch.setattr(
        h, "asset_path", lambda name: p if name == "butterfly-bg.png" else Path("/nope")
    )

    out = h.get_background_image()
    assert out.startswith("data:image/png;base64,")
    assert base64.b64encode(b"\x89PNGtest").decode("ascii") in out


def test_background_image_missing(monkeypatch):
    # Kaikki asset_path-polut palauttavat olemattoman tiedoston
    monkeypatch.setattr(h, "asset_path", lambda name: Path("/definitely_missing"))

    out = h.get_background_image()
    assert out == ""


# ----------------------------
# find_pyhat_file()
# ----------------------------


def test_find_pyhat_file_cwd(tmp_path, monkeypatch):
    # Luo data/pyhat_fi.json nykyiseen hakemistoon
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    target = data_dir / "pyhat_fi.json"
    target.write_text("{}", encoding="utf-8")

    # patchaa CWD
    monkeypatch.chdir(tmp_path)

    found = h.find_pyhat_file()
    assert found == target


def test_find_pyhat_file_none(monkeypatch):
    # Estä sekä cwd että __file__ polut
    monkeypatch.setattr(Path, "cwd", lambda: Path("/nope/nope"))
    monkeypatch.setattr(h, "__file__", "/nope/nope/helpers.py")

    out = h.find_pyhat_file()
    assert out is None


# ----------------------------
# get_flag_info()
# ----------------------------


def test_flag_info_flag_true(tmp_path, monkeypatch):
    p = tmp_path / "data" / "pyhat_fi.json"
    p.parent.mkdir(parents=True)
    p.write_text(json.dumps({"2024-11-11": {"flag": True, "name": "Itsenäisyyspäivä"}}))

    # patchaa find_pyhat_file palauttamaan tämän
    monkeypatch.setattr(h, "find_pyhat_file", lambda: p)

    txt, dbg = h.get_flag_info(datetime(2024, 11, 11))
    assert txt == "Itsenäisyyspäivä"
    assert dbg is None


def test_flag_info_json_read_fails(tmp_path, monkeypatch):
    # Luo tiedosto mutta tee siitä lukukelvoton
    p = tmp_path / "data" / "pyhat_fi.json"
    p.parent.mkdir(parents=True)
    p.write_text("{NOT JSON")

    monkeypatch.setattr(h, "find_pyhat_file", lambda: p)

    txt, dbg = h.get_flag_info(datetime(2024, 11, 11))
    assert txt is None
    assert "ei voitu lukea" in dbg.lower()


def test_flag_info_missing_file(monkeypatch):
    monkeypatch.setattr(h, "find_pyhat_file", lambda: None)

    txt, dbg = h.get_flag_info(datetime(2024, 11, 11))
    assert txt is None
    assert "ei löytynyt" in dbg.lower()


def test_flag_info_missing_key(tmp_path, monkeypatch):
    p = tmp_path / "data" / "pyhat_fi.json"
    p.parent.mkdir(parents=True)
    p.write_text(json.dumps({"2024-01-01": {"flag": False, "name": "Uudenvuodenpäivä"}}))

    monkeypatch.setattr(h, "find_pyhat_file", lambda: p)

    txt, dbg = h.get_flag_info(datetime(2024, 11, 11))
    assert txt is None
    assert "avainta" in dbg.lower() or "avaimet" in dbg.lower()
