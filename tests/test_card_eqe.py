from __future__ import annotations

import importlib
from datetime import datetime, timezone

from src.api.home_assistant import EqeStatus, HAConfigError


def _get_card_module():
    return importlib.import_module("src.ui.card_eqe")


class DummySt:
    def __init__(self):
        self.session_state = {}
        self.query_params = {}
        self.markdown_calls = []
        self.error_calls = []
        self.info_calls = []
        self.rerun_called = False

    def markdown(self, html, unsafe_allow_html=False):
        self.markdown_calls.append((html, unsafe_allow_html))

    def error(self, text):
        self.error_calls.append(text)

    def info(self, text):
        self.info_calls.append(text)

    def rerun(self):
        self.rerun_called = True


def _make_status(now: datetime, **overrides) -> EqeStatus:
    status = EqeStatus(
        soc_pct=80.0,
        soc_unit="%",
        range_km=250.0,
        range_unit="km",
        charging_state="charging",
        charging_state_raw="charging",
        lock_state="Lukossa",
        lock_state_raw="locked",
        lock_state_attr="2",
        lock_state_source="doorlockstatusvehicle",
        lock_state_updated=now,
        preclimate_state="on",
        charging_power_kw=1.0,
        charging_power_unit="kW",
        charging_switch_on=True,
        last_changed=now,
    )
    for key, value in overrides.items():
        setattr(status, key, value)
    return status


class FakeFetch:
    def __init__(self, value):
        self.value = value

    def __call__(self):
        return self.value

    def clear(self):
        pass


def test_card_eqe_renders_basic(monkeypatch):
    card_mod = _get_card_module()
    dummy = DummySt()
    monkeypatch.setattr(card_mod, "st", dummy)
    monkeypatch.setattr(card_mod, "section_title", lambda *a, **k: None)

    html_calls = []
    monkeypatch.setattr(card_mod, "st_html", lambda html, height=0: html_calls.append(html))
    monkeypatch.setattr(card_mod, "_get_eqe_background", lambda: "")
    monkeypatch.setattr(card_mod, "_get_mercedes_logo_svg_data", lambda: "")

    monkeypatch.setattr(card_mod, "eqe_lock_configured", lambda: True)
    monkeypatch.setattr(card_mod, "eqe_preclimate_configured", lambda: True)
    monkeypatch.setattr(card_mod, "eqe_charging_switch_configured", lambda: True)

    now = datetime(2024, 1, 1, tzinfo=timezone.utc)
    status = _make_status(now)
    monkeypatch.setattr(card_mod, "fetch_eqe_status", FakeFetch(status))

    called = {}

    def fake_fetch_power():
        called["power"] = True
        return 2.5, "kW", now

    monkeypatch.setattr(card_mod, "fetch_eqe_charging_power", fake_fetch_power)

    card_mod.card_eqe()

    assert called.get("power") is True
    assert any("eqe-card" in html for html, _ in dummy.markdown_calls)
    assert html_calls


def test_card_eqe_handles_config_error(monkeypatch):
    card_mod = _get_card_module()
    dummy = DummySt()
    monkeypatch.setattr(card_mod, "st", dummy)
    monkeypatch.setattr(card_mod, "section_title", lambda *a, **k: None)

    def fake_fetch_status():
        raise HAConfigError("missing config")

    monkeypatch.setattr(card_mod, "fetch_eqe_status", fake_fetch_status)

    card_mod.card_eqe()

    assert any("missing config" in html for html, _ in dummy.markdown_calls)


def test_card_eqe_lock_query_param_not_configured(monkeypatch):
    card_mod = _get_card_module()
    dummy = DummySt()
    dummy.query_params = {"eqe_lock": "lock"}
    monkeypatch.setattr(card_mod, "st", dummy)
    monkeypatch.setattr(card_mod, "section_title", lambda *a, **k: None)
    monkeypatch.setattr(card_mod, "st_html", lambda *a, **k: None)
    monkeypatch.setattr(card_mod, "_get_eqe_background", lambda: "")
    monkeypatch.setattr(card_mod, "_get_mercedes_logo_svg_data", lambda: "")

    monkeypatch.setattr(card_mod, "eqe_lock_configured", lambda: False)
    monkeypatch.setattr(card_mod, "eqe_preclimate_configured", lambda: False)
    monkeypatch.setattr(card_mod, "eqe_charging_switch_configured", lambda: False)

    now = datetime(2024, 1, 1, tzinfo=timezone.utc)
    monkeypatch.setattr(card_mod, "fetch_eqe_status", FakeFetch(_make_status(now)))
    monkeypatch.setattr(card_mod, "fetch_eqe_charging_power", lambda: (None, None, None))

    card_mod.card_eqe()

    assert dummy.rerun_called is True
    assert any("Lukitus" in msg for msg in dummy.error_calls)


def test_card_eqe_lock_query_param_starts_job(monkeypatch):
    card_mod = _get_card_module()
    dummy = DummySt()
    dummy.query_params = {"eqe_lock": "unlock"}
    monkeypatch.setattr(card_mod, "st", dummy)
    monkeypatch.setattr(card_mod, "section_title", lambda *a, **k: None)
    monkeypatch.setattr(card_mod, "st_html", lambda *a, **k: None)
    monkeypatch.setattr(card_mod, "_get_eqe_background", lambda: "")
    monkeypatch.setattr(card_mod, "_get_mercedes_logo_svg_data", lambda: "")

    monkeypatch.setattr(card_mod, "eqe_lock_configured", lambda: True)
    monkeypatch.setattr(card_mod, "eqe_preclimate_configured", lambda: False)
    monkeypatch.setattr(card_mod, "eqe_charging_switch_configured", lambda: False)

    now = datetime(2024, 1, 1, tzinfo=timezone.utc)
    monkeypatch.setattr(card_mod, "fetch_eqe_status", FakeFetch(_make_status(now)))
    monkeypatch.setattr(card_mod, "fetch_eqe_charging_power", lambda: (None, None, None))

    called = {}
    monkeypatch.setattr(
        card_mod, "_start_lock_job", lambda action: called.setdefault("action", action)
    )

    card_mod.card_eqe()

    assert dummy.rerun_called is True
    assert called.get("action") == "unlock"


def test_card_eqe_preclimate_query_param_starts_job(monkeypatch):
    card_mod = _get_card_module()
    dummy = DummySt()
    dummy.query_params = {"eqe_preclimate": "on"}
    monkeypatch.setattr(card_mod, "st", dummy)
    monkeypatch.setattr(card_mod, "section_title", lambda *a, **k: None)
    monkeypatch.setattr(card_mod, "st_html", lambda *a, **k: None)
    monkeypatch.setattr(card_mod, "_get_eqe_background", lambda: "")
    monkeypatch.setattr(card_mod, "_get_mercedes_logo_svg_data", lambda: "")

    monkeypatch.setattr(card_mod, "eqe_lock_configured", lambda: False)
    monkeypatch.setattr(card_mod, "eqe_preclimate_configured", lambda: True)
    monkeypatch.setattr(card_mod, "eqe_charging_switch_configured", lambda: False)

    now = datetime(2024, 1, 1, tzinfo=timezone.utc)
    monkeypatch.setattr(card_mod, "fetch_eqe_status", FakeFetch(_make_status(now)))
    monkeypatch.setattr(card_mod, "fetch_eqe_charging_power", lambda: (None, None, None))

    called = {}
    monkeypatch.setattr(
        card_mod, "_start_preclimate_job", lambda action: called.setdefault("action", action)
    )

    card_mod.card_eqe()

    assert dummy.rerun_called is True
    assert called.get("action") == "on"


def test_card_eqe_charge_query_param_not_configured(monkeypatch):
    card_mod = _get_card_module()
    dummy = DummySt()
    dummy.query_params = {"eqe_charge": "toggle"}
    monkeypatch.setattr(card_mod, "st", dummy)
    monkeypatch.setattr(card_mod, "section_title", lambda *a, **k: None)
    monkeypatch.setattr(card_mod, "st_html", lambda *a, **k: None)
    monkeypatch.setattr(card_mod, "_get_eqe_background", lambda: "")
    monkeypatch.setattr(card_mod, "_get_mercedes_logo_svg_data", lambda: "")

    monkeypatch.setattr(card_mod, "eqe_lock_configured", lambda: False)
    monkeypatch.setattr(card_mod, "eqe_preclimate_configured", lambda: False)
    monkeypatch.setattr(card_mod, "eqe_charging_switch_configured", lambda: False)

    now = datetime(2024, 1, 1, tzinfo=timezone.utc)
    monkeypatch.setattr(card_mod, "fetch_eqe_status", FakeFetch(_make_status(now)))
    monkeypatch.setattr(card_mod, "fetch_eqe_charging_power", lambda: (None, None, None))

    card_mod.card_eqe()

    assert dummy.rerun_called is False
    assert any("Latauksen ohjaus" in msg for msg in dummy.error_calls)


def test_card_eqe_charge_query_param_success(monkeypatch):
    card_mod = _get_card_module()
    dummy = DummySt()
    dummy.query_params = {"eqe_charge": "toggle"}
    monkeypatch.setattr(card_mod, "st", dummy)
    monkeypatch.setattr(card_mod, "section_title", lambda *a, **k: None)
    monkeypatch.setattr(card_mod, "st_html", lambda *a, **k: None)
    monkeypatch.setattr(card_mod, "_get_eqe_background", lambda: "")
    monkeypatch.setattr(card_mod, "_get_mercedes_logo_svg_data", lambda: "")

    monkeypatch.setattr(card_mod, "eqe_lock_configured", lambda: False)
    monkeypatch.setattr(card_mod, "eqe_preclimate_configured", lambda: False)
    monkeypatch.setattr(card_mod, "eqe_charging_switch_configured", lambda: True)

    now = datetime(2024, 1, 1, tzinfo=timezone.utc)
    status = _make_status(
        now,
        charging_state="idle",
        charging_state_raw="connected",
        charging_power_kw=0.0,
        charging_switch_on=False,
    )
    monkeypatch.setattr(card_mod, "fetch_eqe_status", FakeFetch(status))
    monkeypatch.setattr(card_mod, "fetch_eqe_charging_power", lambda: (None, None, None))

    called = {}

    def fake_set_enabled(enabled: bool):
        called["enabled"] = enabled

    monkeypatch.setattr(card_mod, "set_eqe_charging_enabled", fake_set_enabled)
    monkeypatch.setattr(card_mod, "refresh_eqe_charging_power", lambda: None)

    card_mod.card_eqe()

    assert called.get("enabled") is True
    assert dummy.rerun_called is True
    assert any("Lataus kytketty päälle" in msg for msg in dummy.info_calls)


def test_card_eqe_charging_polling_triggers_refresh(monkeypatch):
    card_mod = _get_card_module()
    dummy = DummySt()
    monkeypatch.setattr(card_mod, "st", dummy)
    monkeypatch.setattr(card_mod, "section_title", lambda *a, **k: None)

    html_calls: list[str] = []
    monkeypatch.setattr(card_mod, "st_html", lambda html, height=0: html_calls.append(html))
    monkeypatch.setattr(card_mod, "_get_eqe_background", lambda: "")
    monkeypatch.setattr(card_mod, "_get_mercedes_logo_svg_data", lambda: "")

    monkeypatch.setattr(card_mod, "eqe_lock_configured", lambda: False)
    monkeypatch.setattr(card_mod, "eqe_preclimate_configured", lambda: False)
    monkeypatch.setattr(card_mod, "eqe_charging_switch_configured", lambda: True)

    now = datetime(2024, 1, 1, tzinfo=timezone.utc)
    status = _make_status(
        now,
        charging_state="charging",
        charging_state_raw="charging",
        charging_power_kw=2.0,
        charging_switch_on=True,
    )
    monkeypatch.setattr(card_mod, "fetch_eqe_status", FakeFetch(status))
    monkeypatch.setattr(card_mod, "fetch_eqe_charging_power", lambda: (2.0, "kW", now))

    card_mod.card_eqe()

    assert dummy.session_state.get("eqe_charging_polling") is True
    assert any("window.location.reload" in html for html in html_calls)


def test_card_eqe_lock_job_error_surface(monkeypatch):
    card_mod = _get_card_module()
    dummy = DummySt()
    monkeypatch.setattr(card_mod, "st", dummy)
    monkeypatch.setattr(card_mod, "section_title", lambda *a, **k: None)
    monkeypatch.setattr(card_mod, "st_html", lambda *a, **k: None)
    monkeypatch.setattr(card_mod, "_get_eqe_background", lambda: "")
    monkeypatch.setattr(card_mod, "_get_mercedes_logo_svg_data", lambda: "")

    monkeypatch.setattr(card_mod, "eqe_lock_configured", lambda: False)
    monkeypatch.setattr(card_mod, "eqe_preclimate_configured", lambda: False)
    monkeypatch.setattr(card_mod, "eqe_charging_switch_configured", lambda: False)

    snapshots = iter(
        [
            {"status": "error", "error": "boom"},
            {"status": "idle"},
            {"status": "idle"},
        ]
    )
    monkeypatch.setattr(card_mod, "_lock_job_snapshot", lambda: next(snapshots))
    monkeypatch.setattr(card_mod, "_reset_lock_job", lambda: None)

    now = datetime(2024, 1, 1, tzinfo=timezone.utc)
    monkeypatch.setattr(card_mod, "fetch_eqe_status", FakeFetch(_make_status(now)))
    monkeypatch.setattr(card_mod, "fetch_eqe_charging_power", lambda: (None, None, None))

    card_mod.card_eqe()

    assert any("Lukituksen ohjaus" in msg for msg in dummy.error_calls)


def test_card_eqe_helper_functions():
    card_mod = _get_card_module()

    cls, text = card_mod._charging_chip(
        state="charging",
        raw_state="charging",
        soc_pct=50.0,
        power_kw=2.0,
        switch_on=None,
    )
    assert "Lataa" in text
    assert "pulse" in cls

    cls, text = card_mod._charging_chip(
        state=None,
        raw_state=None,
        soc_pct=99.0,
        power_kw=0.0,
        switch_on=None,
    )
    assert text == "Täynnä"

    plug = card_mod._charging_plug_status("charging", "connected")
    assert plug == "connected"

    lock_cls, lock_text = card_mod._lock_chip("locked")
    assert lock_text
    assert "chip" in lock_cls

    pre_cls, pre_text = card_mod._preclimate_chip("on")
    assert pre_text
    assert "chip" in pre_cls

    assert card_mod._soc_color(85.0) is not None
    assert card_mod._range_color(250.0) is not None
