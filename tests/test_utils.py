# tests/test_utils.py

import builtins
import json
from types import SimpleNamespace

import src.utils as utils


def test_color_by_thresholds_basic():
    # asetetaan tunnetut kynnykset
    low = 5.0
    high = 10.0
    vals = [None, 1.0, 7.0, 13.0]
    out = utils._color_by_thresholds(vals, low_thr=low, high_thr=high)
    # 4 arvoa → 4 väriä
    assert len(out) == 4
    # None → harmaa
    assert "128,128,128" in out[0]
    # 1.0 < low → vihreä
    assert "60,180,75" in out[1]
    # 7.0 väliin → keltainen
    assert "255,225,25" in out[2]
    # 13.0 > high → punainen
    assert "230,25,75" in out[3]


def test_color_for_value_delegates():
    c = utils._color_for_value(3.0, low_thr=1.0, high_thr=2.0)
    assert isinstance(c, str)
    assert c.startswith("rgba(")


def test_cloud_icon_from_cover_day_and_night():
    # tehdään eri kattavuuksilla
    day_clear = utils._cloud_icon_from_cover(0, True)
    night_cloudy = utils._cloud_icon_from_cover(100, False)
    assert day_clear.startswith("d")
    assert night_cloudy.startswith("n")
    # oletusarvo cover=None → 100%
    night_default = utils._cloud_icon_from_cover(None, False)
    assert night_default == night_cloudy


def test_get_ip_happy(monkeypatch):
    monkeypatch.setattr(utils.socket, "gethostbyname", lambda host: "192.0.2.123")
    ip = utils.get_ip()
    assert ip == "192.0.2.123"


def test_get_ip_failure_falls_back(monkeypatch):
    # korvataan report_error ettei tulosteta
    monkeypatch.setattr(utils, "report_error", lambda *a, **k: None)

    def bad(*a, **k):
        raise OSError("no network")

    monkeypatch.setattr(utils.socket, "gethostbyname", bad)
    ip = utils.get_ip()
    assert ip == "localhost"


def test_fetch_sun_times_success(monkeypatch):
    # korvataan urlopen ettei oikeaa HTTP:tä tehdä
    class FakeResponse:
        def __init__(self, payload: dict):
            self._payload = json.dumps(payload).encode("utf-8")

        def read(self):
            return self._payload

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

    payload = {
        "daily": {
            "sunrise": ["2025-11-11T07:54"],
            "sunset": ["2025-11-11T16:05"],
        }
    }

    def fake_urlopen(url, timeout=6):
        return FakeResponse(payload)

    monkeypatch.setattr(utils.urllib.request, "urlopen", fake_urlopen)

    sunrise, sunset = utils.fetch_sun_times(60.0, 25.0, "Europe/Helsinki")
    assert sunrise == "07:54"
    assert sunset == "16:05"


def test_fetch_sun_times_error_returns_none(monkeypatch):
    # pakotetaan poikkeus
    def fake_urlopen(*a, **k):
        raise TimeoutError("boom")

    monkeypatch.setattr(utils.urllib.request, "urlopen", fake_urlopen)

    sunrise, sunset = utils.fetch_sun_times(0.0, 0.0, "UTC")
    assert sunrise is None
    assert sunset is None


def test_report_error_prints_and_caption(monkeypatch):
    printed = {}

    def fake_print(msg):
        printed["msg"] = msg

    # korvataan globaali print
    monkeypatch.setattr(builtins, "print", fake_print)

    # streamlit-mock
    fake_st = SimpleNamespace()
    fake_st.caption = lambda *a, **k: None

    # varmistetaan että utils.report_error luulee olevansa dev-tilassa
    monkeypatch.setattr(utils, "DEV", True)
    monkeypatch.setattr(utils, "st", fake_st)

    utils.report_error("CTX", RuntimeError("r"))

    assert "[ERR] CTX: RuntimeError: r" in printed["msg"]
