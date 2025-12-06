# src/api/hue_motion.py
from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timezone

import requests

HUE_DEFAULT_TIMEOUT = 5


@dataclass
class HueMotionSensor:
    """Yksinkertainen malli Hue-liikesensorista."""

    id: str
    name: str
    presence: bool
    lastupdated: datetime | None


def _parse_lastupdated(value: str | None) -> datetime | None:
    """Parseeraa Hue:n lastupdated-kentän paikalliseen aikaan.

    Hue palauttaa tyypillisesti UTC-aikaa muodossa 'YYYY-MM-DDTHH:MM:SS'.
    """
    if not value or value in ("none", "1970-01-01T00:00:00"):
        return None

    try:
        dt = datetime.fromisoformat(value)  # oletetaan UTC ilman tz:tä
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        # Muunnetaan koneen lokaaliaikavyöhykettä vastaavaksi
        return dt.astimezone()
    except Exception:
        # Jos jotain outoa, ei kaadeta koko korttia
        return None


def fetch_hue_motion_sensors(
    bridge_host: str | None = None,
    user: str | None = None,
    session: requests.Session | None = None,
) -> list[HueMotionSensor]:
    """Hakee kaikki Hue-sensorit ja suodattaa liikesensorit.

    bridge_host ja user voidaan syöttää parametrina tai lukea
    ympäristömuuttujista HUE_BRIDGE_HOST ja HUE_BRIDGE_USER.
    """
    bridge_host = bridge_host or os.environ.get("HUE_BRIDGE_HOST")
    user = user or os.environ.get("HUE_BRIDGE_USER")

    if not bridge_host or not user:
        raise RuntimeError("HUE_BRIDGE_HOST ja/tai HUE_BRIDGE_USER puuttuu ympäristöstä.")

    url = f"http://{bridge_host}/api/{user}/sensors"
    sess = session or requests

    resp = sess.get(url, timeout=HUE_DEFAULT_TIMEOUT)
    resp.raise_for_status()
    raw = resp.json()

    sensors: list[HueMotionSensor] = []

    # Hue-sensorit tulevat dictinä: { "1": {...}, "2": {...}, ... }
    for sensor_id, info in raw.items():
        if info.get("type") not in ("ZLLMotion", "CLIPPresence"):
            continue

        state = info.get("state") or {}
        presence = bool(state.get("presence"))
        lastupdated = _parse_lastupdated(state.get("lastupdated"))

        sensors.append(
            HueMotionSensor(
                id=str(sensor_id),
                name=info.get("name") or "",
                presence=presence,
                lastupdated=lastupdated,
            )
        )

    return sensors
