from datetime import datetime, timedelta, timezone

from src.api.hue_motion import HueDoorSensor
from src.viewmodels.hue_motion import (
    _format_idle,
    build_hue_motion_viewmodel,
    load_hue_motion_viewmodel,
)


def _dt(minutes_ago: float) -> datetime:
    """Helper: palauttaa UTC-aikaleiman x minuuttia sitten."""
    return datetime.now(timezone.utc) - timedelta(minutes=minutes_ago)


# ----------------------------
# _format_idle -moduulitesti
# ----------------------------


def test_format_idle_none():
    txt, stale = _format_idle(None, datetime.now())
    assert txt == "ei dataa"
    assert stale is True


def test_format_idle_recent_seconds():
    now = datetime.now()
    txt, stale = _format_idle(now - timedelta(seconds=30), now)
    assert txt == "hetki sitten"
    assert stale is False


def test_format_idle_minutes():
    now = datetime.now()
    txt, stale = _format_idle(now - timedelta(minutes=15), now)
    assert txt == "15 min sitten"
    assert stale is False


def test_format_idle_hours_normal():
    now = datetime.now()
    txt, stale = _format_idle(now - timedelta(hours=2), now)
    assert txt == "2 h sitten"
    # stale = True if yli 3h
    assert stale is False


def test_format_idle_hours_stale():
    now = datetime.now()
    txt, stale = _format_idle(now - timedelta(hours=5), now)
    assert txt == "5 h sitten"
    assert stale is True


def test_format_idle_days():
    now = datetime.now()
    txt, stale = _format_idle(now - timedelta(days=3), now)
    assert txt == "3 pv sitten"
    assert stale is True


# ---------------------------------------
# build_hue_motion_viewmodel - logiikkatesti
# ---------------------------------------


def test_viewmodel_missing_sensor():
    rows = build_hue_motion_viewmodel(sensors=[], wanted_names=["Ovi 1"])
    assert len(rows) == 1
    r = rows[0]
    assert r.name == "Ovi 1"
    assert r.status_label == "Ei tietoa"
    assert r.bg_role == "unknown"
    assert r.idle_for_str == "ei dataa"


def test_viewmodel_door_open():
    s = HueDoorSensor(
        id="sensor-1",
        name="Ovi",
        is_open=True,
        presence=None,
        lastupdated=_dt(0.5),
    )
    rows = build_hue_motion_viewmodel([s], wanted_names=["Ovi"])
    row = rows[0]
    assert row.status_label == "Ovi auki"
    assert row.bg_role == "open"


def test_viewmodel_door_closed():
    s = HueDoorSensor(
        id="sensor-2",
        name="Ovi",
        is_open=False,
        presence=None,
        lastupdated=_dt(1),
    )
    rows = build_hue_motion_viewmodel([s], wanted_names=["Ovi"])
    row = rows[0]
    assert row.status_label == "Ovi kiinni"
    assert row.bg_role == "closed"


def test_viewmodel_presence_detected():
    s = HueDoorSensor(
        id="sensor-3",
        name="Sens",
        is_open=None,
        presence=True,
        lastupdated=_dt(2),
    )
    rows = build_hue_motion_viewmodel([s], wanted_names=["Sens"])
    row = rows[0]
    assert row.status_label == "Liike havaittu"
    assert row.bg_role in ("open", "stale")


def test_viewmodel_presence_no_motion():
    s = HueDoorSensor(
        id="sensor-4",
        name="Sens",
        is_open=None,
        presence=False,
        lastupdated=_dt(2),
    )
    rows = build_hue_motion_viewmodel([s], wanted_names=["Sens"])
    row = rows[0]
    assert row.status_label == "Ei liikettä"
    assert row.bg_role in ("closed", "stale")


def test_viewmodel_presence_stale():
    s = HueDoorSensor(
        id="sensor-5",
        name="Sens",
        is_open=None,
        presence=True,
        lastupdated=_dt(4000),  # stale threshold ylittää
    )
    rows = build_hue_motion_viewmodel([s], wanted_names=["Sens"])
    row = rows[0]
    assert row.bg_role == "stale"


def test_viewmodel_no_open_no_presence_fallback():
    s = HueDoorSensor(
        id="sensor-6",
        name="Sens",
        is_open=None,
        presence=None,
        lastupdated=_dt(1),
    )
    rows = build_hue_motion_viewmodel([s], wanted_names=["Sens"])
    row = rows[0]
    assert row.status_label == "Ei tietoa"


def test_viewmodel_lastupdated_none():
    s = HueDoorSensor(
        id="sensor-7",
        name="Sens",
        is_open=False,
        presence=None,
        lastupdated=None,
    )
    rows = build_hue_motion_viewmodel([s], wanted_names=["Sens"])
    row = rows[0]
    assert "ei dataa" in row.idle_for_str


def test_load_hue_motion_viewmodel(monkeypatch):
    fake = [
        HueDoorSensor(
            id="sensor-8",
            name="Etuovi",
            is_open=True,
            presence=None,
            lastupdated=_dt(0.3),
        )
    ]

    def fake_fetch():
        return fake

    monkeypatch.setattr(
        "src.viewmodels.hue_motion.fetch_hue_door_sensors",
        fake_fetch,
    )

    rows = load_hue_motion_viewmodel()
    assert any(r.name == "Etuovi" and r.status_label == "Ovi auki" for r in rows)
