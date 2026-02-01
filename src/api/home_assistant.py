from __future__ import annotations

import json
import os
import re
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import requests
import streamlit as st

from src.config import CACHE_TTL_SHORT, HTTP_TIMEOUT_S, TZ
from src.utils import report_error


class HAConfigError(RuntimeError):
    """Heitetään, jos Home Assistant -konfiguraatio puuttuu."""


@dataclass
class EqeStatus:
    soc_pct: float | None
    soc_unit: str | None
    range_km: float | None
    range_unit: str | None
    charging_state: str | None
    charging_state_raw: str | None
    lock_state: str | None
    lock_state_raw: str | None
    lock_state_attr: str | None
    lock_state_source: str | None
    lock_state_updated: datetime | None
    preclimate_state: str | None
    charging_power_kw: float | None
    charging_power_unit: str | None
    last_changed: datetime | None


def _get_secret(name: str) -> str | None:
    """Hae asetus Streamlit secretsista tai ympäristömuuttujasta."""
    try:
        if name in st.secrets:
            secret_val = st.secrets.get(name)
            if secret_val is not None and str(secret_val).strip():
                return str(secret_val).strip()

        ha_section = st.secrets.get("home_assistant")
        if isinstance(ha_section, Mapping):
            key_map = {
                "HA_BASE_URL": "base_url",
                "HA_TOKEN": "token",
                "HA_EQE_SOC_ENTITY": "eqe_soc_entity",
                "HA_EQE_RANGE_ENTITY": "eqe_range_entity",
                "HA_EQE_CHARGING_ENTITY": "eqe_charging_entity",
                "HA_EQE_LOCK_ENTITY": "eqe_lock_entity",
                "HA_EQE_LOCK_STATUS_ENTITY": "eqe_lock_status_entity",
                "HA_EQE_LOCK_CODE": "eqe_lock_code",
                "HA_EQE_LOCK_REFRESH_SERVICE": "eqe_lock_refresh_service",
                "HA_EQE_LOCK_REFRESH_ENTITY": "eqe_lock_refresh_entity",
                "HA_EQE_LOCK_REFRESH_DATA": "eqe_lock_refresh_data",
                "HA_EQE_PRECLIMATE_ENTITY": "eqe_preclimate_entity",
                "HA_EQE_PRECLIMATE_START_ENTITY": "eqe_preclimate_start_entity",
                "HA_EQE_PRECLIMATE_STOP_ENTITY": "eqe_preclimate_stop_entity",
                "HA_EQE_CHARGING_POWER_ENTITY": "eqe_charging_power_entity",
                "HA_CACHE_TTL": "cache_ttl",
            }
            mapped = key_map.get(name)
            if mapped:
                mapped_val = ha_section.get(mapped)
                if mapped_val is not None and str(mapped_val).strip():
                    return str(mapped_val).strip()
    except Exception:
        pass

    # env fallback (last)
    val = os.getenv(name)
    if val is not None and str(val).strip():
        return val.strip()

    return None


def _ha_cache_ttl() -> int:
    raw = _get_secret("HA_CACHE_TTL")
    if raw:
        try:
            return max(5, int(float(raw)))
        except ValueError:
            pass
    return CACHE_TTL_SHORT


def _ha_lock_timeout_s() -> float:
    raw = _get_secret("HA_EQE_LOCK_TIMEOUT")
    if raw:
        try:
            return max(5.0, float(raw))
        except ValueError:
            pass
    return max(HTTP_TIMEOUT_S, 20.0)


def _require_config() -> dict[str, str]:
    base_url = _get_secret("HA_BASE_URL")
    token = _get_secret("HA_TOKEN")
    if not token:
        raise RuntimeError("Home Assistant token puuttuu secrets.toml-tiedostosta")
    token = token.strip().strip('"').strip("'")

    soc_entity = _get_secret("HA_EQE_SOC_ENTITY")
    range_entity = _get_secret("HA_EQE_RANGE_ENTITY")
    charging_entity = _get_secret("HA_EQE_CHARGING_ENTITY")
    lock_entity = _get_secret("HA_EQE_LOCK_ENTITY")
    lock_status_entity = _get_secret("HA_EQE_LOCK_STATUS_ENTITY")
    preclimate_entity = _get_secret("HA_EQE_PRECLIMATE_ENTITY")
    preclimate_start_entity = _get_secret("HA_EQE_PRECLIMATE_START_ENTITY")
    preclimate_stop_entity = _get_secret("HA_EQE_PRECLIMATE_STOP_ENTITY")
    charging_power_entity = _get_secret("HA_EQE_CHARGING_POWER_ENTITY")

    missing = [
        name
        for name, value in (
            ("HA_BASE_URL", base_url),
            ("HA_TOKEN", token),
            ("HA_EQE_SOC_ENTITY", soc_entity),
            ("HA_EQE_RANGE_ENTITY", range_entity),
            ("HA_EQE_CHARGING_ENTITY", charging_entity),
        )
        if not value
    ]
    if missing:
        raise HAConfigError(f"Home Assistant -asetukset puuttuvat: {', '.join(missing)}")

    return {
        "base_url": str(base_url).rstrip("/"),
        "token": str(token),
        "soc_entity": str(soc_entity),
        "range_entity": str(range_entity),
        "charging_entity": str(charging_entity),
        "lock_entity": str(lock_entity) if lock_entity else None,
        "lock_status_entity": str(lock_status_entity) if lock_status_entity else None,
        "preclimate_entity": str(preclimate_entity) if preclimate_entity else None,
        "preclimate_start_entity": (
            str(preclimate_start_entity) if preclimate_start_entity else None
        ),
        "preclimate_stop_entity": str(preclimate_stop_entity) if preclimate_stop_entity else None,
        "charging_power_entity": str(charging_power_entity) if charging_power_entity else None,
    }


def eqe_preclimate_configured() -> bool:
    """Palauttaa True, jos EQE-ilmastoinnin entity on määritetty."""
    return bool(
        _get_secret("HA_EQE_PRECLIMATE_ENTITY")
        or _get_secret("HA_EQE_PRECLIMATE_START_ENTITY")
        or _get_secret("HA_EQE_PRECLIMATE_STOP_ENTITY")
    )


def eqe_lock_configured() -> bool:
    """Palauttaa True, jos EQE-lukituksen entity on määritetty."""
    return bool(_get_secret("HA_EQE_LOCK_ENTITY"))


def _parse_float(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, int | float):
        return float(value)
    if isinstance(value, str):
        text = value.strip()
        if not text or text in ("unknown", "unavailable"):
            return None
        try:
            return float(text.replace(",", "."))
        except ValueError:
            match = re.search(r"[-+]?\d+(?:[.,]\d+)?", text)
            if match:
                try:
                    return float(match.group(0).replace(",", "."))
                except ValueError:
                    return None
            return None
    return None


def _parse_ts(raw: str | None) -> datetime | None:
    if not raw:
        return None
    try:
        dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        return dt.astimezone(TZ)
    except ValueError:
        return None


def _fetch_state(
    base_url: str, token: str, entity_id: str, session: requests.Session | None = None
) -> dict[str, Any]:
    url = f"{base_url}/api/states/{entity_id}"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    sess = session or requests
    resp = sess.get(url, headers=headers, timeout=HTTP_TIMEOUT_S)
    resp.raise_for_status()
    data = resp.json()
    return data if isinstance(data, dict) else {}


def _call_service(
    base_url: str,
    token: str,
    domain: str,
    service: str,
    data: dict[str, Any],
    session: requests.Session | None = None,
    timeout_s: float | None = None,
) -> Any:
    url = f"{base_url}/api/services/{domain}/{service}"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    sess = session or requests
    timeout = HTTP_TIMEOUT_S if timeout_s is None else timeout_s
    resp = sess.post(url, headers=headers, json=data, timeout=timeout)
    resp.raise_for_status()
    return resp.json()


def set_eqe_preclimate(enabled: bool, session: requests.Session | None = None) -> Any:
    cfg = _require_config()
    start_entity = cfg.get("preclimate_start_entity")
    stop_entity = cfg.get("preclimate_stop_entity")
    if start_entity or stop_entity:
        entity_id = start_entity if enabled else stop_entity
        if not entity_id:
            missing = (
                "HA_EQE_PRECLIMATE_START_ENTITY" if enabled else "HA_EQE_PRECLIMATE_STOP_ENTITY"
            )
            raise HAConfigError(f"{missing} puuttuu")
        domain = entity_id.split(".", 1)[0] if "." in entity_id else "button"
        service = "press"
        return _call_service(
            cfg["base_url"],
            cfg["token"],
            domain,
            service,
            {"entity_id": entity_id},
            session,
        )

    entity_id = cfg.get("preclimate_entity")
    if not entity_id:
        raise HAConfigError("HA_EQE_PRECLIMATE_ENTITY puuttuu")
    domain = entity_id.split(".", 1)[0] if "." in entity_id else "homeassistant"
    service = "turn_on" if enabled else "turn_off"
    return _call_service(
        cfg["base_url"],
        cfg["token"],
        domain,
        service,
        {"entity_id": entity_id},
        session,
    )


def set_eqe_lock(locked: bool, session: requests.Session | None = None) -> Any:
    cfg = _require_config()
    entity_id = cfg.get("lock_entity")
    if not entity_id:
        raise HAConfigError("HA_EQE_LOCK_ENTITY puuttuu")
    domain = entity_id.split(".", 1)[0] if "." in entity_id else "lock"
    if domain in ("switch", "input_boolean"):
        service = "turn_on" if locked else "turn_off"
    else:
        service = "lock" if locked else "unlock"
    data = {"entity_id": entity_id}
    lock_code = _get_secret("HA_EQE_LOCK_CODE")
    if lock_code:
        cleaned = lock_code.strip().strip('"').strip("'")
        if cleaned:
            data["code"] = cleaned
    try:
        return _call_service(
            cfg["base_url"],
            cfg["token"],
            domain,
            service,
            data,
            session,
            timeout_s=_ha_lock_timeout_s(),
        )
    except requests.HTTPError as e:
        detail = ""
        if e.response is not None:
            detail = (e.response.text or "").strip()
        if detail:
            raise RuntimeError(f"{e} | {detail}") from e
        raise


def refresh_eqe_lock_status(session: requests.Session | None = None) -> Any:
    cfg = _require_config()
    entity_id = cfg.get("lock_status_entity") or cfg.get("lock_entity")
    if not entity_id:
        raise HAConfigError("HA_EQE_LOCK_ENTITY puuttuu")
    refresh_service = _get_secret("HA_EQE_LOCK_REFRESH_SERVICE")
    refresh_entity = _get_secret("HA_EQE_LOCK_REFRESH_ENTITY")
    refresh_data_raw = _get_secret("HA_EQE_LOCK_REFRESH_DATA")
    if refresh_service:
        if "." in refresh_service:
            domain, service = refresh_service.split(".", 1)
        else:
            domain, service = "homeassistant", refresh_service
        data: dict[str, Any] = {}
        extra: dict[str, Any] = {}
        if refresh_data_raw:
            try:
                parsed = json.loads(refresh_data_raw)
                if isinstance(parsed, dict):
                    extra = parsed
            except json.JSONDecodeError:
                extra = {}
        if refresh_entity:
            data["entity_id"] = refresh_entity
        elif "entry_id" not in extra:
            data["entity_id"] = entity_id
        if extra:
            data.update(extra)
        return _call_service(
            cfg["base_url"],
            cfg["token"],
            domain,
            service,
            data,
            session,
            timeout_s=_ha_lock_timeout_s(),
        )
    return _call_service(
        cfg["base_url"],
        cfg["token"],
        "homeassistant",
        "update_entity",
        {"entity_id": entity_id},
        session,
        timeout_s=_ha_lock_timeout_s(),
    )


def fetch_eqe_lock_state(
    session: requests.Session | None = None,
) -> tuple[str | None, str | None, str | None, str | None, datetime | None]:
    cfg = _require_config()
    lock_state_entity = cfg.get("lock_status_entity") or cfg.get("lock_entity")
    if not lock_state_entity:
        raise HAConfigError("HA_EQE_LOCK_ENTITY puuttuu")
    state = _fetch_state(cfg["base_url"], cfg["token"], lock_state_entity, session)
    lock_val, lock_raw, lock_attr, lock_source = _extract_lock_state(state)
    lock_updated = _parse_ts(state.get("last_changed") or state.get("last_updated"))
    return lock_val, lock_raw, lock_attr, lock_source, lock_updated


def _normalize_charging_state(state: str | None) -> str | None:
    if not state:
        return None
    if state in ("unknown", "unavailable"):
        return None
    raw = state.strip()
    lower = raw.lower()
    if lower in ("on", "charging", "charge", "true", "plugged_in"):
        return "Lataa"
    if lower in ("off", "idle", "not_charging", "false", "disconnected"):
        return "Ei lataa"
    return raw


def _coerce_lock_value(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, int | float):
        return str(int(value))
    if isinstance(value, str):
        text = value.strip()
        return text or None
    return None


def _normalize_lock_state(state: str | None) -> str | None:
    if not state:
        return None
    if state in ("unknown", "unavailable"):
        return None
    raw = state.strip()
    if raw.isdigit():
        if raw == "2":
            return "Lukossa"
        if raw in ("0", "1"):
            return "Auki"
    lower = raw.lower()
    if lower in ("locking",):
        return "Lukitaan"
    if lower in ("unlocking",):
        return "Avataan"
    if lower in ("locked", "lock", "on", "true", "closed"):
        return "Lukossa"
    if lower in ("unlocked", "unlock", "off", "false", "open"):
        return "Auki"
    return raw


def _extract_lock_state(
    state: dict[str, Any],
) -> tuple[str | None, str | None, str | None, str | None]:
    raw = _coerce_lock_value(state.get("state"))
    attrs = state.get("attributes") or {}
    vehicle_value = _coerce_lock_value(attrs.get("doorlockstatusvehicle"))
    overall_value = _coerce_lock_value(
        attrs.get("doorStatusOverall") or attrs.get("doorstatusoverall")
    )
    if vehicle_value:
        candidate = vehicle_value
        source = "doorlockstatusvehicle"
    elif raw:
        candidate = raw
        source = "state"
    else:
        candidate = overall_value
        source = "doorStatusOverall" if overall_value else None
    return _normalize_lock_state(candidate), raw, vehicle_value or overall_value, source


def _normalize_preclimate_state(state: str | None) -> str:
    if not state or state in ("unknown", "unavailable"):
        return "Käynnistä"
    raw = state.strip()
    lower = raw.lower()
    if lower in ("on", "active", "running", "true"):
        return "Käynnissä"
    if lower in ("off", "idle", "false"):
        return "Käynnistä"
    return raw


@st.cache_data(ttl=_ha_cache_ttl())
def fetch_eqe_status(session: requests.Session | None = None) -> EqeStatus:
    cfg = _require_config()

    try:
        soc_state = _fetch_state(cfg["base_url"], cfg["token"], cfg["soc_entity"], session)
        range_state = _fetch_state(cfg["base_url"], cfg["token"], cfg["range_entity"], session)
        charging_state = _fetch_state(
            cfg["base_url"], cfg["token"], cfg["charging_entity"], session
        )
        lock_state_entity = cfg.get("lock_status_entity") or cfg.get("lock_entity")
        lock_state = (
            _fetch_state(cfg["base_url"], cfg["token"], lock_state_entity, session)
            if lock_state_entity
            else {}
        )
        preclimate_state = (
            _fetch_state(cfg["base_url"], cfg["token"], cfg["preclimate_entity"], session)
            if cfg.get("preclimate_entity")
            else {}
        )
        charging_power_state = (
            _fetch_state(cfg["base_url"], cfg["token"], cfg["charging_power_entity"], session)
            if cfg.get("charging_power_entity")
            else {}
        )
    except Exception as e:
        report_error("home_assistant_eqe: fetch", e)
        raise

    soc_val = _parse_float(soc_state.get("state"))
    range_val = _parse_float(range_state.get("state"))
    soc_unit = (soc_state.get("attributes") or {}).get("unit_of_measurement")
    range_unit = (range_state.get("attributes") or {}).get("unit_of_measurement")
    charging_state_raw = charging_state.get("state")
    charging_val = _normalize_charging_state(charging_state_raw)
    lock_val, lock_raw, lock_attr, lock_source = _extract_lock_state(lock_state)
    lock_updated = _parse_ts(lock_state.get("last_changed") or lock_state.get("last_updated"))
    preclimate_val = _normalize_preclimate_state(preclimate_state.get("state"))
    charging_power_val = _parse_float(charging_power_state.get("state"))
    charging_power_unit = (charging_power_state.get("attributes") or {}).get("unit_of_measurement")

    timestamps = [
        _parse_ts(soc_state.get("last_changed") or soc_state.get("last_updated")),
        _parse_ts(range_state.get("last_changed") or range_state.get("last_updated")),
        _parse_ts(charging_state.get("last_changed") or charging_state.get("last_updated")),
        _parse_ts(lock_state.get("last_changed") or lock_state.get("last_updated")),
        _parse_ts(preclimate_state.get("last_changed") or preclimate_state.get("last_updated")),
        _parse_ts(
            charging_power_state.get("last_changed") or charging_power_state.get("last_updated")
        ),
    ]
    last_changed = max((ts for ts in timestamps if ts), default=None)
    return EqeStatus(
        soc_pct=soc_val,
        soc_unit=str(soc_unit) if soc_unit else None,
        range_km=range_val,
        range_unit=str(range_unit) if range_unit else None,
        charging_state=charging_val,
        charging_state_raw=str(charging_state_raw) if charging_state_raw is not None else None,
        lock_state=lock_val,
        lock_state_raw=lock_raw,
        lock_state_attr=lock_attr,
        lock_state_source=lock_source,
        lock_state_updated=lock_updated,
        preclimate_state=preclimate_val,
        charging_power_kw=charging_power_val,
        charging_power_unit=str(charging_power_unit) if charging_power_unit else None,
        last_changed=last_changed,
    )
