# src/api/hue_contacts_v2.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

import requests
import streamlit as st
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class HueV2ConfigError(RuntimeError):
    """Heitetään, jos v2-API:n konfiguraatio puuttuu."""


@dataclass
class HueContactSensor:
    """Hue Secure -ovikontakti v2-API:sta."""

    id: str  # device.id (UUID)
    name: str  # device.metadata.name (esim. "Etuovi")
    is_open: bool | None  # True = ovi auki, False = kiinni, None = ei tietoa
    last_changed: datetime | None


def _resolve_v2_config() -> tuple[str, str]:
    host = None
    key = None
    try:
        hue = st.secrets["hue"]
        host = str(hue["bridge_host"]).strip()
        key = str(hue["v2_app_key"]).strip().strip('"').strip("'")
    except Exception:
        pass

    if not host or not key:
        raise HueV2ConfigError(
            "Hue-konfiguraatio puuttuu secrets.toml-tiedostosta: [hue] bridge_host / v2_app_key"
        )

    return host, key


def _hue_v2_get(path: str) -> dict:
    bridge_host, app_key = _resolve_v2_config()
    url = f"https://{bridge_host}{path}"
    headers = {"hue-application-key": app_key}
    resp = requests.get(url, headers=headers, timeout=5, verify=False)  # nosec B501
    resp.raise_for_status()
    return resp.json()


def _hue_cfg() -> tuple[str, str]:
    try:
        return _resolve_v2_config()
    except Exception as err:
        raise HueV2ConfigError(
            "Hue-konfiguraatio puuttuu secrets.toml-tiedostosta: [hue] bridge_host / v2_app_key"
        ) from err


def _parse_iso8601(ts: str | None) -> datetime | None:
    """Parseeraa esim. '2023-09-19T17:59:26.966Z' → datetime."""
    if not ts:
        return None
    try:
        # vaihdetaan Z → +00:00, jotta fromisoformat ymmärtää
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        return None


def fetch_hue_contact_sensors() -> list[HueContactSensor]:
    """Hakee Hue Secure -ovikontaktit v2-API:n kautta.

    Käyttää /clip/v2/resource/device ja /clip/v2/resource/contact -resursseja.
    """
    # 1) Kaikki laitteet
    device_payload = _hue_v2_get("/clip/v2/resource/device")
    devices = device_payload.get("data", []) or []

    # 2) Kaikki contact-resurssit (pelkät tilat)
    contact_payload = _hue_v2_get("/clip/v2/resource/contact")
    contacts = contact_payload.get("data", []) or []

    contacts_by_id: dict[str, dict[str, Any]] = {c["id"]: c for c in contacts}

    result: list[HueContactSensor] = []

    for dev in devices:
        services = dev.get("services", []) or []
        metadata = dev.get("metadata", {}) or {}
        name = metadata.get("name", "")

        # Onko laitteella contact-palvelua?
        contact_id: str | None = None
        for svc in services:
            if svc.get("rtype") == "contact":
                contact_id = svc.get("rid")
                break

        if not contact_id:
            # ei ovikontaktia, hypätään yli
            continue

        contact_res = contacts_by_id.get(contact_id)
        if not contact_res:
            continue

        report = contact_res.get("contact_report", {}) or {}
        state_str: str | None = report.get("state")
        changed_str: str | None = report.get("changed")

        if state_str == "contact":
            # magneetti kiinni → ovi kiinni
            is_open = False
        elif state_str == "no_contact":
            # magneetti irti → ovi auki
            is_open = True
        else:
            is_open = None

        last_changed = _parse_iso8601(changed_str)

        result.append(
            HueContactSensor(
                id=dev.get("id", ""),
                name=name,
                is_open=is_open,
                last_changed=last_changed,
            )
        )

    return result
