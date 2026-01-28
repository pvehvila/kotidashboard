from datetime import datetime

import pytest
from requests import Session

from src.api.hue_motion import (
    _parse_lastupdated,
    fetch_hue_door_sensors,
)


def test_parse_lastupdated_none():
    assert _parse_lastupdated(None) is None
    assert _parse_lastupdated("none") is None
    assert _parse_lastupdated("1970-01-01T00:00:00") is None


def test_parse_lastupdated_valid_without_tz():
    dt = _parse_lastupdated("2024-06-01T10:00:00")
    assert isinstance(dt, datetime)
    assert dt.tzinfo is not None  # Converted to local tz


def test_parse_lastupdated_invalid():
    assert _parse_lastupdated("not-a-time") is None


class DummyResp:
    """Simulates requests.Response for JSON return."""

    def __init__(self, payload, status=200):
        self._payload = payload
        self._status = status

    def raise_for_status(self):
        if self._status != 200:
            raise RuntimeError("HTTP error")

    def json(self):
        return self._payload


class DummySession(Session):
    """Simulates requests.Session with get()."""

    def __init__(self, payload):
        super().__init__()
        self.payload = payload
        self.called_urls: list[tuple[str, float | None]] = []

    def get(self, url, timeout=None, **kwargs):  # type: ignore[override]
        self.called_urls.append((url, timeout))
        return DummyResp(self.payload)


def test_fetch_hue_sensors_basic(monkeypatch):
    raw = {
        "1": {
            "name": "Etuovi",
            "type": "ZLLContact",
            "state": {"open": True, "lastupdated": "2024-01-01T10:00:00"},
        },
        "2": {
            "name": "Motion1",
            "type": "ZLLMotion",
            "state": {"presence": True, "lastupdated": "2024-01-01T11:00:00"},
        },
        # ignored type
        "3": {"name": "Temp", "type": "ZLLTemperature", "state": {}},
    }

    sess = DummySession(raw)

    monkeypatch.setattr(
        "src.api.hue_motion.st.secrets",
        {"hue": {"bridge_host": "host", "bridge_user": "user"}},
        raising=False,
    )

    sensors = fetch_hue_door_sensors(session=sess)

    assert len(sensors) == 2
    names = {s.name for s in sensors}
    assert {"Etuovi", "Motion1"} <= names


def test_fetch_hue_sensors_missing_env(monkeypatch):
    monkeypatch.setattr("src.api.hue_motion.st.secrets", {}, raising=False)

    with pytest.raises(RuntimeError):
        fetch_hue_door_sensors(session=DummySession({}))


def test_fetch_hue_sensors_http_error(monkeypatch):
    class BadResp:
        def raise_for_status(self):
            raise RuntimeError("fail")

        def json(self):
            return {}

    class BadSession(Session):
        """Session, joka simuloi HTTP-virheen."""

        def get(self, *args, **kwargs):  # type: ignore[override]
            return BadResp()

    monkeypatch.setattr(
        "src.api.hue_motion.st.secrets",
        {"hue": {"bridge_host": "host", "bridge_user": "user"}},
        raising=False,
    )

    with pytest.raises(RuntimeError):
        fetch_hue_door_sensors(session=BadSession())
