# src/viewmodels/hue_motion.py
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime

from src.api.hue_motion import HueMotionSensor, fetch_hue_motion_sensors

WANTED_NAMES = ("Etuovi", "Terassin ovi", "Varaston ovi")


@dataclass
class MotionRow:
    """Rivi UI-kortille yhdestä ovesta."""

    name: str
    active: bool
    last_updated_str: str  # esim. "09:32" tai "—"


def _format_time(dt: datetime | None) -> str:
    if dt is None:
        return "—"
    # Näyttää vain kellonajan (lokaalissa ajassa)
    return dt.strftime("%H:%M")


def build_hue_motion_viewmodel(
    sensors: Iterable[HueMotionSensor],
    wanted_names: Iterable[str] = WANTED_NAMES,
) -> list[MotionRow]:
    """Rakentaa viewmodelin haluttujen nimien perusteella."""
    by_name = {s.name: s for s in sensors}
    rows: list[MotionRow] = []

    for name in wanted_names:
        sensor = by_name.get(name)
        if not sensor:
            rows.append(
                MotionRow(
                    name=name,
                    active=False,
                    last_updated_str="—",
                )
            )
        else:
            rows.append(
                MotionRow(
                    name=name,
                    active=sensor.presence,
                    last_updated_str=_format_time(sensor.lastupdated),
                )
            )

    return rows


def load_hue_motion_viewmodel() -> list[MotionRow]:
    """Yhdistelmäfunktio: hakee API:sta ja rakentaa viewmodelin."""
    sensors = fetch_hue_motion_sensors()
    return build_hue_motion_viewmodel(sensors)
