# src/viewmodels/hue_contacts.py
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime, timezone

from src.api.hue_contacts_v2 import HueContactSensor, fetch_hue_contact_sensors

# Ovien näyttönimet dashboardilla (sama järjestys kuin korteissa)
WANTED_DOORS: tuple[str, ...] = ("Etuovi", "Terassin ovi", "Varaston ovi")


@dataclass
class DoorRow:
    """UI:lle valmis rivi yhdestä ovesta."""

    name: str
    status_label: str  # "Ovi auki" / "Ovi kiinni" / "Ei tietoa"
    idle_for_str: str  # "5 min sitten" tms.
    bg_role: str  # "open" / "closed" / "stale" / "unknown"


def _format_idle(changed: datetime | None, now: datetime) -> tuple[str, bool]:
    """Palauttaa (tekstikuvaus, onko_data_vanhentunutta)."""
    if changed is None:
        return "ei dataa", True

    delta = now - changed
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


def build_hue_contacts_viewmodel(
    sensors: Iterable[HueContactSensor],
    wanted_names: Iterable[str] = WANTED_DOORS,
) -> list[DoorRow]:
    """Rakentaa ovikontakteista viewmodel-rivit dashboardille.

    Logiikka:
    - yritetään ensin matchata ovet device.name-nimellä
    - ovet, joille ei löytynyt nimellä sensoria, saavat loput vapaana olevat sensorit
      siinä järjestyksessä kun API ne palauttaa
    """

    sensors_list = list(sensors)
    by_name = {s.name: s for s in sensors_list}
    unused_sensors: list[HueContactSensor] = sensors_list.copy()

    now = datetime.now(timezone.utc).astimezone()
    rows: list[DoorRow] = []

    for door_name in wanted_names:
        sensor: HueContactSensor | None = None

        # 1) Yritä löytää nimellä
        named = by_name.get(door_name)
        if named is not None:
            sensor = named
            if named in unused_sensors:
                unused_sensors.remove(named)
        # 2) Muuten ota seuraava vapaa sensori listasta, jos sellainen on
        elif unused_sensors:
            sensor = unused_sensors.pop(0)

        if not sensor:
            rows.append(
                DoorRow(
                    name=door_name,
                    status_label="Ei tietoa",
                    idle_for_str="ei dataa",
                    bg_role="unknown",
                )
            )
            continue

        idle_text, is_stale = _format_idle(sensor.last_changed, now)

        if sensor.is_open is True:
            status = "Ovi auki"
            bg = "open"
        elif sensor.is_open is False:
            status = "Ovi kiinni"
            bg = "closed"
        else:
            status = "Ei tietoa"
            bg = "unknown"

        if is_stale and bg in ("open", "closed"):
            bg = "stale"

        rows.append(
            DoorRow(
                name=door_name,
                status_label=status,
                idle_for_str=idle_text,
                bg_role=bg,
            )
        )

    return rows


def load_hue_contacts_viewmodel() -> list[DoorRow]:
    """Yhdistelmäfunktio: hakee v2-API:sta ja rakentaa viewmodelin."""
    sensors = fetch_hue_contact_sensors()
    return build_hue_contacts_viewmodel(sensors)
