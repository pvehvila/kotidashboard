# tests/test_paths.py

from pathlib import Path

import src.paths as paths


def test_root_constants_are_paths():
    assert isinstance(paths.ROOT_DIR, Path)
    assert isinstance(paths.ASSETS, Path)
    assert isinstance(paths.DATA, Path)
    assert isinstance(paths.DOCS, Path)
    assert isinstance(paths.LOGS, Path)


def test_root_path_joins_correctly():
    p = paths.root_path("foo", "bar.txt")
    # sen pitää olla ROOT_DIRin alla
    assert str(paths.ROOT_DIR) in str(p)
    assert str(p).endswith("foo\\bar.txt") or str(p).endswith("foo/bar.txt")


def test_asset_path_joins_correctly():
    p = paths.asset_path("img", "logo.png")
    assert str(paths.ASSETS) in str(p)
    assert p.name == "logo.png"


def test_data_path_joins_correctly():
    p = paths.data_path("mydata.json")
    assert str(paths.DATA) in str(p)
    assert p.name == "mydata.json"


def test_ensure_dirs_creates_logs(monkeypatch, tmp_path):
    # ohjataan LOGS väliaikaiseen kansioon
    fake_logs = tmp_path / "logs"
    monkeypatch.setattr(paths, "LOGS", fake_logs)
    paths.ensure_dirs()
    assert fake_logs.exists()
    assert fake_logs.is_dir()
