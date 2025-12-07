from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime, timezone

from src.api.hue_motion import HueDoorSensor, fetch_hue_door_sensors

WANTED_NAMES: tuple[str, ...] = ("Etuovi", "Terassin ovi", "Varaston ovi")


@dataclass
class MotionRow:
    """UI:lle valmis rivi yhdestä ovesta/liikesensorista."""

    name: str
    status_label: str  # "Ovi auki" / "Ovi kiinni" / "Liike havaittu" / "Ei liikettä" / "Ei tietoa"
    idle_for_str: str  # "5 min sitten" tms.
    bg_role: str  # "open" / "closed" / "stale" / "unknown"


def _format_idle(dt: datetime | None, now: datetime) -> tuple[str, bool]:
    """Palauttaa (teksti, onko_stale).

    stale = data selvästi vanhaa (esim. yli 3 h).
    """
    if dt is None:
        return "ei dataa", True

    delta = now - dt
    minutes = delta.total_seconds() / 60.0

    if minutes < 1.5:
        return "hetki sitten", False
    if minutes < 90:
        return f"{int(minutes)} min sitten", False

    hours = minutes / 60.0
    if hours < 48:
        return f"{int(hours)} h sitten", hours > 3

    days = int(hours // 24)
    return f"{days} pv sitten", True


def build_hue_motion_viewmodel(
    sensors: Iterable[HueDoorSensor],
    wanted_names: Iterable[str] = WANTED_NAMES,
) -> list[MotionRow]:
    """Rakentaa ovikohtaisen / liikesensori-kohtaisen viewmodelin."""

    by_name = {s.name: s for s in sensors}
    now = datetime.now(timezone.utc).astimezone()

    rows: list[MotionRow] = []

    for name in wanted_names:
        sensor = by_name.get(name)

        if not sensor:
            rows.append(
                MotionRow(
                    name=name,
                    status_label="Ei tietoa",
                    idle_for_str="ei dataa",
                    bg_role="unknown",
                )
            )
            continue

        idle_text, is_stale = _format_idle(sensor.lastupdated, now)

        # 1) Jos on oikea ovikontakti (open True/False), käytetään sitä.
        if sensor.is_open is True:
            status = "Ovi auki"
            bg_role = "open"
        elif sensor.is_open is False:
            status = "Ovi kiinni"
            bg_role = "closed"

        # 2) Muuten käytetään presenceä, jos sellainen on.
        elif sensor.presence is True:
            status = "Liike havaittu"
            # Käyttäydymme tässä kuin "ovi auki"
            bg_role = "open" if not is_stale else "stale"
        elif sensor.presence is False:
            status = "Ei liikettä"
            # Käyttäydymme tässä kuin "ovi kiinni"
            bg_role = "closed" if not is_stale else "stale"

        # 3) Ei kummankaan tietoa → fallback
        else:
            status = "Ei tietoa"
            bg_role = "stale" if is_stale else "unknown"

        rows.append(
            MotionRow(
                name=name,
                status_label=status,
                idle_for_str=idle_text,
                bg_role=bg_role,
            )
        )

    return rows


def load_hue_motion_viewmodel() -> list[MotionRow]:
    """Yhdistelmäfunktio: hakee API:sta ja rakentaa viewmodelin."""
    sensors = fetch_hue_door_sensors()
    return build_hue_motion_viewmodel(sensors)
