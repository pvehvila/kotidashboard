import json
from datetime import datetime
from pathlib import Path

import src.ui.card_nameday_helpers as h


def test_find_pyhat_file_picks_existing(tmp_path, monkeypatch):
    # rakenna data/pyhat_fi.json hakemistorakenne
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    f = data_dir / "pyhat_fi.json"
    f.write_text("{}", encoding="utf-8")

    # tee niin, että helper “luulee” olevansa tuossa juurihakemistossa
    monkeypatch.setattr(h, "Path", Path)  # varmistus
    monkeypatch.chdir(tmp_path)

    found = h.find_pyhat_file()
    assert found == f


def test_get_flag_info_returns_name(tmp_path, monkeypatch):
    today = datetime(2025, 11, 11)
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    f = data_dir / "pyhat_fi.json"
    f.write_text(json.dumps({"2025-11-11": {"name": "Isänpäivä", "flag": True}}), encoding="utf-8")

    monkeypatch.chdir(tmp_path)

    name, debug = h.get_flag_info(today)
    assert name == "Isänpäivä"
    assert debug is None


def test_get_flag_info_missing_key_gives_debug(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    f = data_dir / "pyhat_fi.json"
    f.write_text("{}", encoding="utf-8")

    monkeypatch.chdir(tmp_path)

    name, debug = h.get_flag_info(datetime(2025, 1, 1))
    assert name is None
    assert debug is not None
    assert "2025-01-01" in debug


def test_get_background_image_ok(monkeypatch, tmp_path):
    img = tmp_path / "butterfly-bg.png"
    img.write_bytes(b"\x89PNG\r\n\x1a\n")  # riittää että tiedosto on olemassa

    def fake_asset_path(name):
        # palautetaan aina tämä luotu kuva
        return img

    monkeypatch.setattr(h, "asset_path", fake_asset_path)

    b64 = h.get_background_image()
    assert b64.startswith("data:image/png;base64,")
