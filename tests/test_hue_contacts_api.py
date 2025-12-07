# tests/test_hue_contacts_api.py

from datetime import datetime, timezone

import pytest

from src.api.hue_contacts_v2 import (
    HueContactSensor,
    HueV2ConfigError,
    _hue_v2_get,
    _parse_iso8601,
    fetch_hue_contact_sensors,
)


class DummyResp:
    def __init__(self, payload, status=200):
        self._payload = payload
        self._status = status

    def raise_for_status(self):
        if self._status != 200:
            raise RuntimeError("http error")

    def json(self):
        return self._payload


def test_require_v2_config_missing(monkeypatch):
    # patchataan moduulin globaalit, ei ympäristömuuttujia
    monkeypatch.setattr("src.api.hue_contacts_v2.HUE_BRIDGE_HOST", None)
    monkeypatch.setattr("src.api.hue_contacts_v2.HUE_V2_APP_KEY", None)

    with pytest.raises(HueV2ConfigError):
        _hue_v2_get("/clip/v2/resource/device")


def test_hue_v2_get_builds_url_and_headers(monkeypatch):
    called = {}

    def fake_get(url, headers, timeout, verify):
        called["url"] = url
        called["headers"] = headers
        called["timeout"] = timeout
        called["verify"] = verify
        return DummyResp({"data": []})

    monkeypatch.setattr("src.api.hue_contacts_v2.HUE_BRIDGE_HOST", "bridge")
    monkeypatch.setattr("src.api.hue_contacts_v2.HUE_V2_APP_KEY", "app-key")
    monkeypatch.setattr("src.api.hue_contacts_v2.requests.get", fake_get)

    data = _hue_v2_get("/clip/v2/resource/device")

    assert data == {"data": []}
    assert called["url"] == "https://bridge/clip/v2/resource/device"
    assert called["headers"]["hue-application-key"] == "app-key"
    assert called["timeout"] == 5
    assert called["verify"] is False


def test_parse_iso8601_none_and_invalid():
    assert _parse_iso8601(None) is None
    assert _parse_iso8601("") is None
    assert _parse_iso8601("not-a-timestamp") is None


def test_parse_iso8601_valid_z_suffix():
    dt = _parse_iso8601("2023-09-19T17:59:26.966Z")
    assert isinstance(dt, datetime)
    assert dt.tzinfo is not None
    # pitäisi olla UTC
    assert dt.tzinfo.utcoffset(dt) == timezone.utc.utcoffset(dt)


def test_fetch_hue_contact_sensors_basic(monkeypatch):
    # Patchataan v2-get niin, että se palauttaa eri payloadit polusta riippuen
    def fake_v2_get(path: str):
        if path == "/clip/v2/resource/device":
            return {
                "data": [
                    {
                        "id": "dev-1",
                        "metadata": {"name": "Etuovi"},
                        "services": [
                            {"rtype": "contact", "rid": "contact-1"},
                        ],
                    },
                    {
                        "id": "dev-2",
                        "metadata": {"name": "Muu laite"},
                        "services": [
                            {"rtype": "temperature", "rid": "temp-1"},
                        ],
                    },
                ]
            }
        if path == "/clip/v2/resource/contact":
            return {
                "data": [
                    {
                        "id": "contact-1",
                        "contact_report": {
                            "state": "no_contact",
                            "changed": "2023-09-19T17:59:26.966Z",
                        },
                    },
                    {
                        "id": "contact-ignored",
                        "contact_report": {
                            "state": "contact",
                            "changed": "2023-09-19T17:00:00.000Z",
                        },
                    },
                ]
            }
        raise AssertionError(f"unexpected path {path}")

    monkeypatch.setattr("src.api.hue_contacts_v2._hue_v2_get", fake_v2_get)
    # varmista, että konfiguraatio näyttää olevan kunnossa
    monkeypatch.setattr("src.api.hue_contacts_v2.HUE_BRIDGE_HOST", "bridge")
    monkeypatch.setattr("src.api.hue_contacts_v2.HUE_V2_APP_KEY", "key")

    sensors = fetch_hue_contact_sensors()
    assert len(sensors) == 1

    s = sensors[0]
    assert isinstance(s, HueContactSensor)
    assert s.id == "dev-1"
    assert s.name == "Etuovi"
    # no_contact → ovi auki
    assert s.is_open is True
    assert isinstance(s.last_changed, datetime)


def test_fetch_hue_contact_sensors_unknown_state(monkeypatch):
    def fake_v2_get(path: str):
        if path == "/clip/v2/resource/device":
            return {
                "data": [
                    {
                        "id": "dev-1",
                        "metadata": {"name": "Etuovi"},
                        "services": [{"rtype": "contact", "rid": "contact-1"}],
                    }
                ]
            }
        if path == "/clip/v2/resource/contact":
            return {
                "data": [
                    {
                        "id": "contact-1",
                        "contact_report": {
                            "state": "weird",
                            "changed": None,
                        },
                    }
                ]
            }
        raise AssertionError

    monkeypatch.setattr("src.api.hue_contacts_v2._hue_v2_get", fake_v2_get)
    monkeypatch.setattr("src.api.hue_contacts_v2.HUE_BRIDGE_HOST", "bridge")
    monkeypatch.setattr("src.api.hue_contacts_v2.HUE_V2_APP_KEY", "key")

    sensors = fetch_hue_contact_sensors()
    assert len(sensors) == 1
    s = sensors[0]
    # tuntematon state → is_open = None
    assert s.is_open is None
    assert s.last_changed is None
