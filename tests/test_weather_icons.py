# tests/test_weather_icons.py
from pathlib import Path

import src.weather_icons as wi


def _write_dummy_png(path: Path):
    # kirjaa yksinkertainen, kelvollinen PNG header
    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        b"\x00\x00\x00\rIHDR"
        b"\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x02\x00\x00\x00\x90wS\xde"
        b"\x00\x00\x00\nIDATx\xdac``\x00\x00\x00\x02\x00\x01"
        b"\x0d\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
    )


def test_find_icon_path_uses_direct_and_cache(monkeypatch, tmp_path):
    # clean cache
    wi._ICON_CACHE.clear()

    key = "d100"
    icon_path = tmp_path / "d100.png"
    _write_dummy_png(icon_path)

    # override SEARCH_DIRS
    monkeypatch.setattr(wi, "SEARCH_DIRS", [tmp_path])

    # direct hit
    p1 = wi._find_icon_path(key)
    assert p1 == icon_path

    # cached hit
    p2 = wi._find_icon_path(key)
    assert p2 == icon_path  # same path, from cache


def test_find_icon_path_uses_alt_key(monkeypatch, tmp_path):
    wi._ICON_CACHE.clear()

    key = "n200"
    alt_key = "d200"  # swapped by logic

    alt_path = tmp_path / f"{alt_key}.png"
    _write_dummy_png(alt_path)

    monkeypatch.setattr(wi, "SEARCH_DIRS", [tmp_path])

    p = wi._find_icon_path(key)
    assert p == alt_path


def test_find_icon_path_falls_back_to_d000(monkeypatch, tmp_path):
    wi._ICON_CACHE.clear()

    fallback = tmp_path / "d000.png"
    _write_dummy_png(fallback)

    monkeypatch.setattr(wi, "SEARCH_DIRS", [tmp_path])

    p = wi._find_icon_path("n999")
    assert p == fallback


def test_find_icon_path_returns_none_if_no_files(monkeypatch, tmp_path):
    wi._ICON_CACHE.clear()
    monkeypatch.setattr(wi, "SEARCH_DIRS", [tmp_path])

    p = wi._find_icon_path("d999")
    assert p is None


def test_render_foreca_icon_success(monkeypatch, tmp_path):
    key = "d123"
    icon_path = tmp_path / f"{key}.png"
    _write_dummy_png(icon_path)

    monkeypatch.setattr(wi, "SEARCH_DIRS", [tmp_path])
    wi._ICON_CACHE.clear()

    html = wi.render_foreca_icon(key)
    assert html.startswith("<img ")
    assert "data:image/png;base64," in html


def test_render_foreca_icon_fallback_placeholder(monkeypatch, tmp_path):
    monkeypatch.setattr(wi, "SEARCH_DIRS", [tmp_path])
    wi._ICON_CACHE.clear()

    html = wi.render_foreca_icon("d999")
    assert html.startswith("<span")
    assert "not found" in html or "?" in html
