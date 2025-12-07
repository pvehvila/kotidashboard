# src/api/hue_motion.py
from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timezone

import requests

HUE_DEFAULT_TIMEOUT = 5


@dataclass
class HueDoorSensor:
    """Malli Hue-ovesta / liikesensorista.

    - is_open: True = ovi auki, False = ovi kiinni, None = ei kontaktitietoa
    - presence: True/False jos anturi on liiketunnistin (ei välttämättä ovikytkin)
    """

    id: str
    name: str
    is_open: bool | None
    presence: bool | None
    lastupdated: datetime | None


def _parse_lastupdated(value: str | None) -> datetime | None:
    """Parseeraa Hue:n lastupdated-kentän paikalliseen aikaan."""
    if not value or value in ("none", "1970-01-01T00:00:00"):
        return None

    try:
        dt = datetime.fromisoformat(value)  # usein ilman tz-infoa
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone()
    except Exception:
        return None


def fetch_hue_door_sensors(
    bridge_host: str | None = None,
    user: str | None = None,
    session: requests.Session | None = None,
) -> list[HueDoorSensor]:
    """Hakee Hue-sensorit ja suodattaa ovikontaktit + liikesensorit.

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

    sensors: list[HueDoorSensor] = []

    # Hue-sensorit: { "1": {...}, "2": {...}, ... }
    for sensor_id, info in raw.items():
        sensor_type = info.get("type")
        # Ovi- / liikesensorityypit, joita meille kannattaa katsoa
        if sensor_type not in (
            "ZLLMotion",
            "CLIPPresence",
            "ZLLPresence",
            "ZLLContact",
            "ZigbeeContact",
            "ZigbeeMotion",
        ):
            continue

        state = info.get("state") or {}
        presence_raw = state.get("presence")
        open_raw = state.get("open")

        presence: bool | None
        if presence_raw is None:
            presence = None
        else:
            presence = bool(presence_raw)

        is_open: bool | None
        if open_raw is None:
            is_open = None
        else:
            is_open = bool(open_raw)

        sensors.append(
            HueDoorSensor(
                id=str(sensor_id),
                name=info.get("name") or "",
                is_open=is_open,
                presence=presence,
                lastupdated=_parse_lastupdated(state.get("lastupdated")),
            )
        )

    return sensors
