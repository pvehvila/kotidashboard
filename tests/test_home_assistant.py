from __future__ import annotations

from datetime import datetime

import pytest

import src.api.home_assistant as ha


def test_get_secret_prefers_top_level(monkeypatch):
    monkeypatch.setattr(
        ha.st,
        "secrets",
        {"HA_TOKEN": "tok", "home_assistant": {"token": "nested"}},
        raising=False,
    )
    assert ha._get_secret("HA_TOKEN") == "tok"


def test_get_secret_from_section(monkeypatch):
    monkeypatch.setattr(
        ha.st,
        "secrets",
        {"home_assistant": {"token": "tok2", "base_url": "http://ha"}},
        raising=False,
    )
    assert ha._get_secret("HA_TOKEN") == "tok2"


def test_get_secret_env_fallback(monkeypatch):
    monkeypatch.setattr(ha.st, "secrets", {}, raising=False)
    monkeypatch.setenv("HA_TOKEN", "envtok")
    assert ha._get_secret("HA_TOKEN") == "envtok"


def test_require_config_missing_token(monkeypatch):
    monkeypatch.setattr(ha, "_get_secret", lambda name: None)
    with pytest.raises(RuntimeError):
        ha._require_config()


def test_require_config_missing_base_url(monkeypatch):
    vals = {
        "HA_BASE_URL": None,
        "HA_TOKEN": "token",
        "HA_EQE_SOC_ENTITY": "sensor.soc",
        "HA_EQE_RANGE_ENTITY": "sensor.range",
        "HA_EQE_CHARGING_ENTITY": "sensor.charge",
    }
    monkeypatch.setattr(ha, "_get_secret", lambda name: vals.get(name))
    with pytest.raises(ha.HAConfigError):
        ha._require_config()


def test_require_config_ok(monkeypatch):
    vals = {
        "HA_BASE_URL": "http://ha",
        "HA_TOKEN": "token",
        "HA_EQE_SOC_ENTITY": "sensor.soc",
        "HA_EQE_RANGE_ENTITY": "sensor.range",
        "HA_EQE_CHARGING_ENTITY": "sensor.charge",
        "HA_EQE_LOCK_ENTITY": "lock.eqe",
    }
    monkeypatch.setattr(ha, "_get_secret", lambda name: vals.get(name))
    cfg = ha._require_config()
    assert cfg["base_url"] == "http://ha"
    assert cfg["charging_entity"] == "sensor.charge"


def test_parse_float_variants():
    assert ha._parse_float("12,5") == 12.5
    assert ha._parse_float("x 3.7 kW") == 3.7
    assert ha._parse_float("unknown") is None
    assert ha._parse_float(4) == 4.0


def test_parse_ts_valid():
    dt = ha._parse_ts("2024-01-01T00:00:00Z")
    assert isinstance(dt, datetime)
    assert dt.tzinfo is not None


def test_normalize_states():
    assert ha._normalize_charging_state("charging") == "Lataa"
    assert ha._normalize_charging_state("idle") == "Ei lataa"
    assert ha._normalize_charging_state("unknown") is None
    assert ha._normalize_switch_state("on") is True
    assert ha._normalize_switch_state("off") is False
    assert ha._normalize_switch_state("unknown") is None


def test_normalize_lock_state_variants():
    assert ha._normalize_lock_state("2") == "Lukossa"
    assert ha._normalize_lock_state("0") == "Auki"
    assert ha._normalize_lock_state("locking") == "Lukitaan"


def test_extract_power_value_fallback_to_attrs():
    state = {"state": "0", "attributes": {"power": "5.5", "power_unit": "kW"}}
    val, unit = ha._extract_power_value(state)
    assert val == 5.5
    assert unit == "kW"


def test_extract_lock_state_prefers_vehicle_value():
    state = {"state": "unlocked", "attributes": {"doorlockstatusvehicle": "2"}}
    lock_val, raw, attr, source = ha._extract_lock_state(state)
    assert lock_val == "Lukossa"
    assert source == "doorlockstatusvehicle"
    assert raw == "unlocked"
    assert attr == "2"


def test_set_eqe_lock_uses_lock_domain_and_code(monkeypatch):
    cfg = {
        "base_url": "http://ha",
        "token": "token",
        "soc_entity": "sensor.soc",
        "range_entity": "sensor.range",
        "charging_entity": "sensor.charge",
        "lock_entity": "lock.eqe",
        "lock_status_entity": None,
        "preclimate_entity": None,
        "preclimate_start_entity": None,
        "preclimate_stop_entity": None,
        "charging_power_entity": None,
        "charging_switch_entity": None,
    }
    monkeypatch.setattr(ha, "_require_config", lambda: cfg)
    monkeypatch.setattr(
        ha,
        "_get_secret",
        lambda name: "1234" if name == "HA_EQE_LOCK_CODE" else None,
    )
    called = {}

    def fake_call_service(base_url, token, domain, service, data, session=None, timeout_s=None):
        called["domain"] = domain
        called["service"] = service
        called["data"] = data
        return {"ok": True}

    monkeypatch.setattr(ha, "_call_service", fake_call_service)

    ha.set_eqe_lock(True)

    assert called["domain"] == "lock"
    assert called["service"] == "lock"
    assert called["data"]["code"] == "1234"


def test_set_eqe_lock_switch_domain(monkeypatch):
    cfg = {
        "base_url": "http://ha",
        "token": "token",
        "soc_entity": "sensor.soc",
        "range_entity": "sensor.range",
        "charging_entity": "sensor.charge",
        "lock_entity": "switch.eqe",
        "lock_status_entity": None,
        "preclimate_entity": None,
        "preclimate_start_entity": None,
        "preclimate_stop_entity": None,
        "charging_power_entity": None,
        "charging_switch_entity": None,
    }
    monkeypatch.setattr(ha, "_require_config", lambda: cfg)
    monkeypatch.setattr(ha, "_get_secret", lambda name: None)
    called = {}

    def fake_call_service(base_url, token, domain, service, data, session=None, timeout_s=None):
        called["domain"] = domain
        called["service"] = service
        called["data"] = data
        return {"ok": True}

    monkeypatch.setattr(ha, "_call_service", fake_call_service)

    ha.set_eqe_lock(False)

    assert called["domain"] == "switch"
    assert called["service"] == "turn_off"


def test_refresh_eqe_lock_status_with_service(monkeypatch):
    cfg = {
        "base_url": "http://ha",
        "token": "token",
        "soc_entity": "sensor.soc",
        "range_entity": "sensor.range",
        "charging_entity": "sensor.charge",
        "lock_entity": "lock.eqe",
        "lock_status_entity": None,
        "preclimate_entity": None,
        "preclimate_start_entity": None,
        "preclimate_stop_entity": None,
        "charging_power_entity": None,
        "charging_switch_entity": None,
    }
    monkeypatch.setattr(ha, "_require_config", lambda: cfg)

    def fake_get_secret(name):
        data = {
            "HA_EQE_LOCK_REFRESH_SERVICE": "homeassistant.update_entity",
            "HA_EQE_LOCK_REFRESH_ENTITY": "lock.refresh",
        }
        return data.get(name)

    monkeypatch.setattr(ha, "_get_secret", fake_get_secret)
    called = {}

    def fake_call_service(base_url, token, domain, service, data, session=None, timeout_s=None):
        called["domain"] = domain
        called["service"] = service
        called["data"] = data
        return {"ok": True}

    monkeypatch.setattr(ha, "_call_service", fake_call_service)

    ha.refresh_eqe_lock_status()

    assert called["domain"] == "homeassistant"
    assert called["service"] == "update_entity"
    assert called["data"]["entity_id"] == "lock.refresh"


def test_fetch_eqe_charging_power(monkeypatch):
    cfg = {
        "base_url": "http://ha",
        "token": "token",
        "charging_power_entity": "sensor.power",
    }
    monkeypatch.setattr(ha, "_require_config", lambda: cfg)

    def fake_fetch_state(base_url, token, entity_id, session=None):
        return {
            "state": "1.5",
            "attributes": {"unit_of_measurement": "kW"},
            "last_changed": "2024-01-01T00:00:00Z",
        }

    monkeypatch.setattr(ha, "_fetch_state", fake_fetch_state)

    val, unit, updated = ha.fetch_eqe_charging_power()

    assert val == 1.5
    assert unit == "kW"
    assert updated is not None


def test_fetch_eqe_lock_state(monkeypatch):
    cfg = {
        "base_url": "http://ha",
        "token": "token",
        "lock_entity": "lock.eqe",
        "lock_status_entity": None,
    }
    monkeypatch.setattr(ha, "_require_config", lambda: cfg)

    def fake_fetch_state(base_url, token, entity_id, session=None):
        return {
            "state": "unlocked",
            "attributes": {"doorlockstatusvehicle": "2"},
            "last_changed": "2024-01-01T00:00:00Z",
        }

    monkeypatch.setattr(ha, "_fetch_state", fake_fetch_state)

    val, raw, attr, source, updated = ha.fetch_eqe_lock_state()

    assert val == "Lukossa"
    assert raw == "unlocked"
    assert attr == "2"
    assert source == "doorlockstatusvehicle"
    assert updated is not None


def test_fetch_eqe_status_basic(monkeypatch):
    cfg = {
        "base_url": "http://ha",
        "token": "token",
        "soc_entity": "sensor.soc",
        "range_entity": "sensor.range",
        "charging_entity": "sensor.charge",
        "lock_entity": "lock.eqe",
        "lock_status_entity": None,
        "preclimate_entity": "switch.preclimate",
        "preclimate_start_entity": None,
        "preclimate_stop_entity": None,
        "charging_power_entity": "sensor.power",
        "charging_switch_entity": "switch.charge",
    }
    monkeypatch.setattr(ha, "_require_config", lambda: cfg)

    def fake_fetch_state(base_url, token, entity_id, session=None):
        if entity_id == cfg["soc_entity"]:
            return {
                "state": "85",
                "attributes": {"unit_of_measurement": "%"},
                "last_changed": "2024-01-01T08:00:00Z",
            }
        if entity_id == cfg["range_entity"]:
            return {
                "state": "240",
                "attributes": {"unit_of_measurement": "km"},
                "last_changed": "2024-01-01T08:05:00Z",
            }
        if entity_id == cfg["charging_entity"]:
            return {
                "state": "charging",
                "last_changed": "2024-01-01T08:10:00Z",
            }
        if entity_id == cfg["lock_entity"]:
            return {
                "state": "unlocked",
                "attributes": {"doorlockstatusvehicle": "2"},
                "last_changed": "2024-01-01T08:02:00Z",
            }
        if entity_id == cfg["preclimate_entity"]:
            return {
                "state": "on",
                "last_changed": "2024-01-01T08:03:00Z",
            }
        if entity_id == cfg["charging_power_entity"]:
            return {
                "state": "2.5",
                "attributes": {"unit_of_measurement": "kW"},
                "last_changed": "2024-01-01T08:15:00Z",
            }
        if entity_id == cfg["charging_switch_entity"]:
            return {
                "state": "on",
                "last_changed": "2024-01-01T08:12:00Z",
            }
        return {}

    monkeypatch.setattr(ha, "_fetch_state", fake_fetch_state)
    if hasattr(ha.fetch_eqe_status, "clear"):
        ha.fetch_eqe_status.clear()

    status = ha.fetch_eqe_status()

    assert status.soc_pct == 85.0
    assert status.charging_state == "Lataa"
    assert status.lock_state == "Lukossa"
    assert status.charging_switch_on is True
    assert status.lock_state_source == "doorlockstatusvehicle"
    assert status.last_changed is not None
