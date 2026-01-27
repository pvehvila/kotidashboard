from __future__ import annotations

import os
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
    last_changed: datetime | None


def _get_secret(name: str) -> str | None:
    """Hae asetus ympäristömuuttujasta tai Streamlit secretsista."""
    val = os.getenv(name)
    if val is not None and str(val).strip():
        return val

    try:
        if name in st.secrets:
            secret_val = st.secrets.get(name)
            if secret_val is not None and str(secret_val).strip():
                return str(secret_val)

        ha_section = st.secrets.get("home_assistant")
        if isinstance(ha_section, dict):
            key_map = {
                "HA_BASE_URL": "base_url",
                "HA_TOKEN": "token",
                "HA_EQE_SOC_ENTITY": "eqe_soc_entity",
                "HA_EQE_RANGE_ENTITY": "eqe_range_entity",
                "HA_EQE_CHARGING_ENTITY": "eqe_charging_entity",
                "HA_CACHE_TTL": "cache_ttl",
            }
            mapped = key_map.get(name)
            if mapped and mapped in ha_section:
                mapped_val = ha_section.get(mapped)
                if mapped_val is not None and str(mapped_val).strip():
                    return str(mapped_val)
    except Exception:
        return None

    return None


def _ha_cache_ttl() -> int:
    raw = _get_secret("HA_CACHE_TTL")
    if raw:
        try:
            return max(5, int(float(raw)))
        except ValueError:
            pass
    return CACHE_TTL_SHORT


def _require_config() -> dict[str, str]:
    base_url = _get_secret("HA_BASE_URL")
    token = _get_secret("HA_TOKEN")
    soc_entity = _get_secret("HA_EQE_SOC_ENTITY")
    range_entity = _get_secret("HA_EQE_RANGE_ENTITY")
    charging_entity = _get_secret("HA_EQE_CHARGING_ENTITY")

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
    }


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


@st.cache_data(ttl=_ha_cache_ttl())
def fetch_eqe_status(session: requests.Session | None = None) -> EqeStatus:
    cfg = _require_config()

    try:
        soc_state = _fetch_state(cfg["base_url"], cfg["token"], cfg["soc_entity"], session)
        range_state = _fetch_state(cfg["base_url"], cfg["token"], cfg["range_entity"], session)
        charging_state = _fetch_state(
            cfg["base_url"], cfg["token"], cfg["charging_entity"], session
        )
    except Exception as e:
        report_error("home_assistant_eqe: fetch", e)
        raise

    soc_val = _parse_float(soc_state.get("state"))
    range_val = _parse_float(range_state.get("state"))
    soc_unit = (soc_state.get("attributes") or {}).get("unit_of_measurement")
    range_unit = (range_state.get("attributes") or {}).get("unit_of_measurement")
    charging_val = _normalize_charging_state(charging_state.get("state"))

    timestamps = [
        _parse_ts(soc_state.get("last_changed") or soc_state.get("last_updated")),
        _parse_ts(range_state.get("last_changed") or range_state.get("last_updated")),
        _parse_ts(charging_state.get("last_changed") or charging_state.get("last_updated")),
    ]
    last_changed = max((ts for ts in timestamps if ts), default=None)

    return EqeStatus(
        soc_pct=soc_val,
        soc_unit=str(soc_unit) if soc_unit else None,
        range_km=range_val,
        range_unit=str(range_unit) if range_unit else None,
        charging_state=charging_val,
        last_changed=last_changed,
    )
