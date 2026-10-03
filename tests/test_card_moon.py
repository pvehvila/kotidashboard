from __future__ import annotations

import importlib
from datetime import date

import pytest

moon_module = importlib.import_module("src.ui.card_moon")


@pytest.mark.parametrize(
    ("day", "name", "illumination"),
    [
        (date(2000, 1, 6), "Uusikuu", 0),
        (date(2000, 1, 14), "Ensimmäinen neljännes", 50),
        (date(2000, 1, 21), "Täysikuu", 100),
        (date(2000, 1, 29), "Viimeinen neljännes", 50),
    ],
)
def test_moon_phases(day, name, illumination):
    vm = moon_module.get_moon_view(day)

    assert vm["name"] == name
    assert abs(vm["illumination"] - illumination) <= 6
    assert vm["day"] == day


def test_moon_uses_current_finnish_day(monkeypatch):
    class FixedDatetime:
        @classmethod
        def now(cls, tz):
            assert tz == moon_module.TZ
            return original_datetime(2026, 10, 3, 0, 5, tzinfo=tz)

        def __new__(cls, *args, **kwargs):
            return original_datetime(*args, **kwargs)

    original_datetime = moon_module.datetime
    monkeypatch.setattr(moon_module, "datetime", FixedDatetime)

    assert moon_module.get_moon_view()["day"] == date(2026, 10, 3)


def test_card_moon_renders(monkeypatch):
    markdowns = []
    titles = []
    monkeypatch.setattr(moon_module.st, "markdown", lambda body, **kwargs: markdowns.append(body))
    monkeypatch.setattr(moon_module, "section_title", lambda title, **kwargs: titles.append(title))
    vm = {
        "day": date(2026, 10, 3),
        "name": "Viimeinen neljännes",
        "icon": "🌗",
        "phase": 0.75,
        "illumination": 50,
    }
    monkeypatch.setattr(moon_module, "get_moon_view", lambda: vm)

    moon_module.card_moon()

    assert titles == ["🌙 Kuun vaihe"]
    assert "moon-card" in markdowns[0]
    assert "3.10.2026" in markdowns[0]
    assert "Viimeinen neljännes" in markdowns[0]
    assert "50 %" in markdowns[0]
    assert "Valaistu osuus" not in markdowns[0]
    assert markdowns[0].index("50 %") < markdowns[0].rindex("Viimeinen neljännes")
    assert "<svg" in markdowns[0]
    assert "data:image/jpeg;base64," in markdowns[0]


@pytest.mark.parametrize(
    ("phase", "outer_sweep", "inner_sweep"),
    [(0.125, 1, 0), (0.375, 1, 1), (0.625, 0, 0), (0.875, 0, 1)],
)
def test_moon_shadow_curves_and_changes_side(phase, outer_sweep, inner_sweep):
    path = moon_module._moon_light_path(phase)

    assert f"A 90 90 0 0 {outer_sweep} 100 190" in path
    assert f"A 63.6396 90 0 0 {inner_sweep} 100 10" in path


@pytest.mark.parametrize("phase", [0.25, 0.75])
def test_quarter_moon_has_straight_terminator(phase):
    assert "L 100 10" in moon_module._moon_light_path(phase)
