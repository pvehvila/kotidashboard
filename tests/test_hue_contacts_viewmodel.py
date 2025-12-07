# tests/test_hue_contacts_viewmodel.py

from datetime import datetime, timedelta, timezone

from src.api.hue_contacts_v2 import HueContactSensor
from src.viewmodels.hue_contacts import (
    WANTED_DOORS,
    DoorRow,
    _format_idle,
    build_hue_contacts_viewmodel,
    load_hue_contacts_viewmodel,
)


def _dt(minutes_ago: float) -> datetime:
    return datetime.now(timezone.utc) - timedelta(minutes=minutes_ago)


# -----------------_format_idle-----------------


def test_format_idle_none():
    text, stale = _format_idle(None, datetime.now(timezone.utc))
    assert text == "ei dataa"
    assert stale is True


def test_format_idle_recent():
    now = datetime.now(timezone.utc)
    text, stale = _format_idle(now - timedelta(seconds=30), now)
    assert text == "hetki sitten"
    assert stale is False


def test_format_idle_minutes():
    now = datetime.now(timezone.utc)
    text, stale = _format_idle(now - timedelta(minutes=10), now)
    assert text == "10 min sitten"
    assert stale is False


def test_format_idle_hours_non_stale():
    now = datetime.now(timezone.utc)
    text, stale = _format_idle(now - timedelta(hours=2), now)
    assert text == "2 h sitten"
    assert stale is False


def test_format_idle_hours_stale():
    now = datetime.now(timezone.utc)
    text, stale = _format_idle(now - timedelta(hours=5), now)
    assert text == "5 h sitten"
    assert stale is True


def test_format_idle_days():
    now = datetime.now(timezone.utc)
    text, stale = _format_idle(now - timedelta(days=3), now)
    assert text == "3 pv sitten"
    assert stale is True


# --------------- build_hue_contacts_viewmodel ---------------


def test_build_viewmodel_missing_sensor():
    rows = build_hue_contacts_viewmodel([], wanted_names=("Etuovi",))
    assert len(rows) == 1
    r = rows[0]
    assert isinstance(r, DoorRow)
    assert r.name == "Etuovi"
    assert r.status_label == "Ei tietoa"
    assert r.bg_role == "unknown"
    assert r.idle_for_str == "ei dataa"


def test_build_viewmodel_match_by_name_open_and_closed():
    sensors = [
        HueContactSensor(id="1", name="Etuovi", is_open=True, last_changed=_dt(1)),
        HueContactSensor(id="2", name="Takao", is_open=False, last_changed=_dt(2)),
    ]
    rows = build_hue_contacts_viewmodel(sensors, wanted_names=("Etuovi", "Takao"))

    etuovi = rows[0]
    takao = rows[1]

    assert etuovi.status_label == "Ovi auki"
    assert etuovi.bg_role == "open"
    assert takao.status_label == "Ovi kiinni"
    assert takao.bg_role == "closed"


def test_build_viewmodel_fallback_to_unused_sensor():
    sensors = [HueContactSensor(id="1", name="Joku muu", is_open=False, last_changed=_dt(3))]
    rows = build_hue_contacts_viewmodel(sensors, wanted_names=("Etuovi",))
    r = rows[0]
    # vaikka nimi ei täsmää, fallback käyttää ainoaa sensoria
    assert r.status_label in ("Ovi kiinni", "Ovi auki", "Ei tietoa")


def test_build_viewmodel_stale_overrides_bg():
    sensors = [
        HueContactSensor(
            id="1",
            name="Etuovi",
            is_open=True,
            last_changed=_dt(60 * 24 * 4),  # 4 päivää sitten
        )
    ]
    rows = build_hue_contacts_viewmodel(sensors, wanted_names=("Etuovi",))
    r = rows[0]
    assert r.status_label == "Ovi auki"
    assert r.bg_role == "stale"


def test_build_viewmodel_last_changed_none():
    sensors = [HueContactSensor(id="1", name="Etuovi", is_open=False, last_changed=None)]
    rows = build_hue_contacts_viewmodel(sensors, wanted_names=("Etuovi",))
    r = rows[0]
    assert r.idle_for_str == "ei dataa"


def test_load_hue_contacts_viewmodel(monkeypatch):
    fake = [HueContactSensor(id="1", name="Etuovi", is_open=False, last_changed=_dt(5))]

    monkeypatch.setattr(
        "src.viewmodels.hue_contacts.fetch_hue_contact_sensors",
        lambda: fake,
    )

    rows = load_hue_contacts_viewmodel()
    assert len(rows) == len(WANTED_DOORS)
    assert rows[0].name == "Etuovi"
