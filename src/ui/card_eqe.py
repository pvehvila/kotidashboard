from __future__ import annotations

import base64
import html
import threading
import time

import requests
import streamlit as st
from streamlit.components.v1 import html as st_html

from src.api.home_assistant import (
    HAConfigError,
    eqe_charging_switch_configured,
    eqe_lock_configured,
    eqe_preclimate_configured,
    fetch_eqe_charging_power,
    fetch_eqe_lock_state,
    fetch_eqe_status,
    refresh_eqe_charging_power,
    refresh_eqe_charging_state,
    refresh_eqe_lock_status,
    set_eqe_charging_enabled,
    set_eqe_lock,
    set_eqe_preclimate,
)
from src.paths import asset_path
from src.ui.common import section_title

_LOCK_JOB_LOCK = threading.Lock()
_LOCK_POLL_RETRIES = 10
_LOCK_JOB: dict[str, object] = {
    "status": "idle",  # idle | pending | polling | error
    "action": None,  # "lock" | "unlock"
    "error": None,
    "poll_remaining": 0,
}

_PRECLIMATE_JOB_LOCK = threading.Lock()
_PRECLIMATE_POLL_RETRIES = 10
_PRECLIMATE_JOB: dict[str, object] = {
    "status": "idle",  # idle | pending | polling | error
    "action": None,  # "on" | "off"
    "error": None,
    "poll_remaining": 0,
}


def _lock_job_snapshot() -> dict[str, object]:
    with _LOCK_JOB_LOCK:
        return dict(_LOCK_JOB)


def _reset_lock_job() -> None:
    with _LOCK_JOB_LOCK:
        _LOCK_JOB.update(
            status="idle",
            action=None,
            error=None,
            poll_remaining=0,
        )


def _finish_lock_job(
    status: str,
    error: str | None = None,
    poll_remaining: int | None = None,
) -> None:
    with _LOCK_JOB_LOCK:
        _LOCK_JOB.update(
            status=status,
            error=error,
        )
        if poll_remaining is not None:
            _LOCK_JOB["poll_remaining"] = poll_remaining


def _run_lock_job(action: str) -> None:
    try:
        set_eqe_lock(action == "lock")
        _finish_lock_job("polling", poll_remaining=_LOCK_POLL_RETRIES)
    except requests.Timeout:
        # HA voi jäädä odottamaan pilvipalvelun kuittausta; jatketaan pollingia.
        _finish_lock_job("polling", poll_remaining=_LOCK_POLL_RETRIES)
    except Exception as e:
        _finish_lock_job("error", error=str(e))


def _start_lock_job(action: str) -> bool:
    with _LOCK_JOB_LOCK:
        if _LOCK_JOB.get("status") in ("pending", "polling"):
            return False
        _LOCK_JOB.update(
            status="pending",
            action=action,
            error=None,
            poll_remaining=0,
        )
    threading.Thread(target=_run_lock_job, args=(action,), daemon=True).start()
    return True


def _preclimate_job_snapshot() -> dict[str, object]:
    with _PRECLIMATE_JOB_LOCK:
        return dict(_PRECLIMATE_JOB)


def _reset_preclimate_job() -> None:
    with _PRECLIMATE_JOB_LOCK:
        _PRECLIMATE_JOB.update(
            status="idle",
            action=None,
            error=None,
            poll_remaining=0,
        )


def _finish_preclimate_job(
    status: str,
    error: str | None = None,
    poll_remaining: int | None = None,
) -> None:
    with _PRECLIMATE_JOB_LOCK:
        _PRECLIMATE_JOB.update(
            status=status,
            error=error,
        )
        if poll_remaining is not None:
            _PRECLIMATE_JOB["poll_remaining"] = poll_remaining


def _run_preclimate_job(action: str) -> None:
    try:
        set_eqe_preclimate(action == "on")
        _finish_preclimate_job("polling", poll_remaining=_PRECLIMATE_POLL_RETRIES)
    except requests.Timeout:
        _finish_preclimate_job("polling", poll_remaining=_PRECLIMATE_POLL_RETRIES)
    except Exception as e:
        _finish_preclimate_job("error", error=str(e))


def _start_preclimate_job(action: str) -> bool:
    with _PRECLIMATE_JOB_LOCK:
        if _PRECLIMATE_JOB.get("status") in ("pending", "polling"):
            return False
        _PRECLIMATE_JOB.update(
            status="pending",
            action=action,
            error=None,
            poll_remaining=0,
        )
    threading.Thread(target=_run_preclimate_job, args=(action,), daemon=True).start()
    return True


def _coerce_int(value: object, default: int = 0) -> int:
    try:
        return int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default


def _get_eqe_background() -> str:
    """Palauttaa EQE-taustakuvan data-URLina, jos löytyy assets-hakemistosta."""
    name = "mercedes-benz-eqe-2023_00_original.jpg"
    p = asset_path(name)
    if not p.exists():
        return ""
    b64 = base64.b64encode(p.read_bytes()).decode("ascii")
    return f"data:image/jpeg;base64,{b64}"


def _get_mercedes_logo_svg_data() -> str:
    """Palauttaa Mercedes-logo-SVG data-URLina, jos löytyy assets-hakemistosta."""
    p = asset_path("Mercedes-Benz_Star.svg")
    if not p.exists():
        return ""
    b64 = base64.b64encode(p.read_bytes()).decode("ascii")
    return f"data:image/svg+xml;base64,{b64}"


def _fmt_value(
    value: float | None, unit: str | None, digits: int = 0, color: str | None = None
) -> str:
    if value is None:
        return "<span class='hint'>—</span>"
    if digits <= 0:
        num = f"{value:.0f}"
    else:
        num = f"{value:.{digits}f}"
    unit_html = f"<span class='eqe-unit'>{html.escape(unit)}</span>" if unit else ""
    text = f"{num}{unit_html}"
    if color:
        return f"<span style='color:{color};'>{text}</span>"
    return text


def _soc_color(value: float | None) -> str | None:
    if value is None:
        return None
    if value >= 80:
        return "#1E7F43"
    if value >= 60:
        return "#2ECC71"
    if value >= 40:
        return "#A3E4D7"
    if value >= 25:
        return "#F1C40F"
    if value >= 15:
        return "#E67E22"
    return "#C0392B"


def _range_color(value: float | None) -> str | None:
    if value is None:
        return None
    if value > 300:
        return "#1B4F72"
    if value >= 200:
        return "#2980B9"
    if value >= 120:
        return "#48C9B0"
    if value >= 70:
        return "#F4D03F"
    if value >= 30:
        return "#E67E22"
    return "#C0392B"


def _charging_chip(
    state: str | None,
    raw_state: str | None,
    soc_pct: float | None,
    power_kw: float | None,
    switch_on: bool | None,
) -> tuple[str, str]:
    if not state and not raw_state and power_kw is None and switch_on is None:
        return ("chip yellow", "Tuntematon")
    state_lower = (state or "").strip().lower()
    raw_lower = (raw_state or "").strip().lower()
    soc_full = soc_pct is not None and soc_pct >= 99
    power_active = power_kw is not None and power_kw > 0.1

    if soc_full or raw_lower in ("full", "fully_charged", "complete", "completed", "done", "ready"):
        return ("chip green", "Täynnä")
    if switch_on is False:
        return ("chip red", "Ei lataa")
    if power_active:
        return ("chip blue pulse", "Lataa")
    if switch_on is True:
        return ("chip blue", "Käynnistyy")
    if power_kw is not None:
        return ("chip red", "Ei lataa")
    if "lataa" in state_lower or raw_lower in ("charging", "charge", "on"):
        return ("chip blue pulse", "Lataa")
    if (
        "ei lataa" in state_lower
        or state_lower in ("idle", "off", "not_charging", "disconnected", "false")
        or raw_lower in ("idle", "off", "not_charging", "disconnected", "false")
    ):
        return ("chip red", "Ei lataa")
    if raw_lower in ("plugged_in", "connected"):
        return ("chip red", "Ei lataa")
    return ("chip red", "Ei lataa")


def _charging_plug_status(state: str | None, raw_state: str | None) -> str:
    state_lower = (state or "").strip().lower()
    raw_lower = (raw_state or "").strip().lower()
    if raw_lower in ("disconnected", "unplugged", "not_connected"):
        return "disconnected"
    if raw_lower in ("plugged_in", "connected", "charging", "charge", "on"):
        return "connected"
    if "lataa" in state_lower or state_lower in ("charging", "on"):
        return "connected"
    return "unknown"


def _charging_state_active(state: str | None, raw_state: str | None) -> bool:
    state_lower = (state or "").strip().lower()
    raw_lower = (raw_state or "").strip().lower()
    return "lataa" in state_lower or raw_lower in ("charging", "charge", "on")


def _wait_for_power_change(
    expected_on: bool,
    timeout_s: float = 5.0,
    interval_s: float = 1.0,
) -> tuple[float | None, str | None]:
    deadline = time.time() + timeout_s
    last_val: float | None = None
    last_unit: str | None = None
    while True:
        try:
            refresh_eqe_charging_power()
        except Exception:
            pass
        try:
            val, unit, _updated = fetch_eqe_charging_power()
            if val is not None:
                last_val = val
                last_unit = unit
                if expected_on and val > 0.1:
                    return last_val, last_unit
                if (not expected_on) and val <= 0.1:
                    return last_val, last_unit
        except Exception:
            pass
        if time.time() >= deadline:
            return last_val, last_unit
        time.sleep(interval_s)


def _maybe_force_charging_refresh(interval_s: float = 15.0) -> None:
    now = time.time()
    last_ts = st.session_state.get("eqe_charge_refresh_ts")
    if isinstance(last_ts, int | float) and now - float(last_ts) < interval_s:
        return
    try:
        refresh_eqe_charging_state()
    except Exception:
        pass
    try:
        refresh_eqe_charging_power()
    except Exception:
        pass
    st.session_state["eqe_charge_refresh_ts"] = now
    fetch_eqe_status.clear()


def _lock_chip(state: str | None) -> tuple[str, str]:
    if not state:
        return ("chip yellow", "Tuntematon")
    state_lower = state.lower()
    if "lukossa" in state_lower or state_lower in ("locked", "on", "true"):
        return ("chip green", state)
    if "lukitaan" in state_lower or state_lower in ("locking",):
        return ("chip yellow", "Lukitaan")
    if "avataan" in state_lower or state_lower in ("unlocking",):
        return ("chip yellow", "Avataan")
    if "auki" in state_lower or state_lower in ("unlocked", "off", "false"):
        return ("chip red", state)
    return ("chip yellow", state)


def _lock_is_locked(state: str | None) -> bool:
    if not state:
        return False
    state_lower = state.lower()
    return state_lower in ("locked", "lock", "on", "true", "closed", "lukossa")


def _preclimate_chip(state: str | None) -> tuple[str, str]:
    state_lower = (state or "").lower()
    if "käynnissä" in state_lower or state_lower in ("on", "active", "running", "true"):
        return ("chip green", "Käynnissä")
    return ("chip red", "Käynnistä")


def _preclimate_is_on(state: str | None) -> bool:
    if not state:
        return False
    state_lower = state.lower()
    return state_lower in ("on", "active", "running", "true", "käynnissä")


def card_eqe() -> None:
    """Render Mercedes EQE -kortti Home Assistant -datalla."""
    logo = _get_mercedes_logo_svg_data()
    if logo:
        title_html = (
            "<span style='display:inline-flex; align-items:center; gap:6px;'>"
            f"<img src='{logo}' alt='Mercedes' "
            "style='width:16px; height:16px; vertical-align:middle; filter:drop-shadow(0 1px 1px rgba(0,0,0,0.35));'/>"
            "Mercedes EQE</span>"
        )
    else:
        title_html = "Mercedes EQE"
    section_title(title_html, mt=10, mb=4)
    try:
        lock_job = _lock_job_snapshot()
        if lock_job.get("status") == "error":
            st.session_state["eqe_lock_msg"] = (
                "err",
                f"Lukituksen ohjaus epäonnistui: {lock_job.get('error')}",
            )
            _reset_lock_job()
        lock_job = _lock_job_snapshot()
        preclimate_job = _preclimate_job_snapshot()
        if preclimate_job.get("status") == "error":
            st.session_state["eqe_preclimate_msg"] = (
                "err",
                f"Ilmastoinnin ohjaus epäonnistui: {preclimate_job.get('error')}",
            )
            _reset_preclimate_job()
        preclimate_job = _preclimate_job_snapshot()

        lock_available = eqe_lock_configured()
        preclimate_available = eqe_preclimate_configured()
        charging_available = eqe_charging_switch_configured()
        lock_action_raw = st.query_params.get("eqe_lock")
        if isinstance(lock_action_raw, list):
            lock_action = (lock_action_raw[0] if lock_action_raw else "") or ""
        else:
            lock_action = lock_action_raw or ""
        lock_action = str(lock_action).lower()
        if lock_action:
            if not lock_available:
                st.session_state["eqe_lock_msg"] = (
                    "err",
                    "Lukitus ei ole käytössä (HA_EQE_LOCK_ENTITY puuttuu).",
                )
            else:
                action = "lock" if lock_action == "lock" else "unlock"
                _start_lock_job(action)
            try:
                del st.query_params["eqe_lock"]
            except Exception:
                st.query_params.clear()
            st.rerun()
        action_raw = st.query_params.get("eqe_preclimate")
        if isinstance(action_raw, list):
            action = (action_raw[0] if action_raw else "") or ""
        else:
            action = action_raw or ""
        action = str(action).lower()
        if action:
            if not preclimate_available:
                st.session_state["eqe_preclimate_msg"] = (
                    "err",
                    "Ilmastointi ei ole käytössä (HA_EQE_PRECLIMATE_ENTITY puuttuu).",
                )
            else:
                action_on = action == "on"
                _start_preclimate_job("on" if action_on else "off")
            try:
                del st.query_params["eqe_preclimate"]
            except Exception:
                st.query_params.clear()
            st.rerun()
        charge_action_raw = st.query_params.get("eqe_charge")
        if isinstance(charge_action_raw, list):
            charge_action = (charge_action_raw[0] if charge_action_raw else "") or ""
        else:
            charge_action = charge_action_raw or ""
        charge_action = str(charge_action).lower()
        charge_requested = bool(charge_action)
        if charge_requested:
            try:
                del st.query_params["eqe_charge"]
            except Exception:
                st.query_params.clear()
            if not charging_available:
                st.session_state["eqe_charge_msg"] = (
                    "err",
                    "Latauksen ohjaus ei ole käytössä (HA_EQE_CHARGING_SWITCH_ENTITY puuttuu).",
                )

        prev_polling = st.session_state.get("eqe_charging_polling", False)
        if prev_polling:
            _maybe_force_charging_refresh(interval_s=30.0)

        lock_job = _lock_job_snapshot()
        lock_pending_action = (
            lock_job.get("action") if lock_job.get("status") in ("pending", "polling") else None
        )
        is_polling = lock_job.get("status") == "polling"
        preclimate_job = _preclimate_job_snapshot()
        preclimate_pending_action = (
            preclimate_job.get("action")
            if preclimate_job.get("status") in ("pending", "polling")
            else None
        )
        preclimate_polling = preclimate_job.get("status") == "polling"
        lock_override = None
        if lock_pending_action:
            try:
                refresh_eqe_lock_status()
                time.sleep(1.5)
            except Exception:
                pass
            fetch_eqe_status.clear()
            try:
                lock_override = fetch_eqe_lock_state()
            except Exception:
                lock_override = None
        if preclimate_pending_action:
            fetch_eqe_status.clear()
        vm = fetch_eqe_status()
        charge_override = st.session_state.get("eqe_charge_override")
        charge_override_on = None
        charge_override_ts = None
        if isinstance(charge_override, dict):
            charge_override_on = charge_override.get("value")
            charge_override_ts = charge_override.get("ts")
        if lock_override:
            (
                vm.lock_state,
                vm.lock_state_raw,
                vm.lock_state_attr,
                vm.lock_state_source,
                vm.lock_state_updated,
            ) = lock_override
        if lock_pending_action:
            lock_state_lower = (vm.lock_state or "").lower()
            target_reached = (lock_pending_action == "lock" and "lukossa" in lock_state_lower) or (
                lock_pending_action == "unlock" and "auki" in lock_state_lower
            )
            if target_reached:
                _reset_lock_job()
                lock_pending_action = None
                is_polling = False
            elif is_polling:
                remaining = _coerce_int(lock_job.get("poll_remaining", 0), default=0)
                remaining = max(remaining - 1, 0)
                if remaining <= 0:
                    _reset_lock_job()
                    lock_pending_action = None
                    is_polling = False
                else:
                    with _LOCK_JOB_LOCK:
                        _LOCK_JOB["poll_remaining"] = remaining
        if preclimate_pending_action:
            preclimate_is_on = _preclimate_is_on(vm.preclimate_state)
            target_reached = (preclimate_pending_action == "on" and preclimate_is_on) or (
                preclimate_pending_action == "off" and not preclimate_is_on
            )
            if target_reached:
                _reset_preclimate_job()
                preclimate_pending_action = None
                preclimate_polling = False
            elif preclimate_polling:
                remaining = _coerce_int(preclimate_job.get("poll_remaining", 0), default=0)
                remaining = max(remaining - 1, 0)
                if remaining <= 0:
                    _reset_preclimate_job()
                    preclimate_pending_action = None
                    preclimate_polling = False
                else:
                    with _PRECLIMATE_JOB_LOCK:
                        _PRECLIMATE_JOB["poll_remaining"] = remaining
        soc_html = _fmt_value(
            vm.soc_pct,
            vm.soc_unit or "%",
            digits=0,
            color=_soc_color(vm.soc_pct),
        )
        range_html = _fmt_value(
            vm.range_km,
            vm.range_unit or "km",
            digits=0,
            color=_range_color(vm.range_km),
        )
        switch_on = vm.charging_switch_on
        if charge_override_on in (True, False):
            if (
                isinstance(charge_override_ts, int | float)
                and time.time() - float(charge_override_ts) <= 30
            ):
                if switch_on == charge_override_on:
                    st.session_state.pop("eqe_charge_override", None)
                else:
                    switch_on = charge_override_on
            else:
                st.session_state.pop("eqe_charge_override", None)
        power_probe = st.session_state.get("eqe_power_probe")
        if isinstance(power_probe, dict):
            expected_on = power_probe.get("expected_on")
            due_at = power_probe.get("due_at")
            if (
                isinstance(expected_on, bool)
                and isinstance(due_at, int | float)
                and time.time() >= float(due_at)
            ):
                power_val, power_unit = _wait_for_power_change(
                    expected_on=expected_on, timeout_s=10.0, interval_s=1.0
                )
                if power_val is not None:
                    st.session_state["eqe_power_override"] = {
                        "value": power_val,
                        "unit": power_unit,
                        "ts": time.time(),
                    }
                st.session_state.pop("eqe_power_probe", None)
        power_override = st.session_state.get("eqe_power_override")
        if isinstance(power_override, dict):
            override_val = power_override.get("value")
            override_unit = power_override.get("unit")
            override_ts = power_override.get("ts")
            if (
                override_val is None
                or not isinstance(override_ts, int | float)
                or time.time() - float(override_ts) > 30
            ):
                st.session_state.pop("eqe_power_override", None)
            else:
                try:
                    override_val_f = float(override_val)
                except (TypeError, ValueError):
                    st.session_state.pop("eqe_power_override", None)
                else:
                    if (
                        vm.charging_power_kw is not None
                        and abs(vm.charging_power_kw - override_val_f) <= 0.01
                    ):
                        st.session_state.pop("eqe_power_override", None)
                    else:
                        vm.charging_power_kw = override_val_f
                        if override_unit:
                            vm.charging_power_unit = str(override_unit)
        power_refresh = (
            switch_on is True
            or charge_override_on is True
            or _charging_state_active(vm.charging_state, vm.charging_state_raw)
        )
        if power_refresh:
            try:
                power_val, power_unit, power_updated = fetch_eqe_charging_power()
                if power_val is not None:
                    vm.charging_power_kw = power_val
                if power_unit:
                    vm.charging_power_unit = power_unit
                if power_updated and (vm.last_changed is None or power_updated > vm.last_changed):
                    vm.last_changed = power_updated
            except Exception:
                pass
        chip_class, chip_text = _charging_chip(
            vm.charging_state,
            vm.charging_state_raw,
            vm.soc_pct,
            vm.charging_power_kw,
            switch_on,
        )
        override_recent = (
            isinstance(charge_override_ts, int | float)
            and time.time() - float(charge_override_ts) <= 30
        )
        charging_polling = chip_text == "Lataa" or override_recent
        st.session_state["eqe_charging_polling"] = charging_polling
        if charge_requested and charging_available:
            desired_on = None
            if chip_text in ("Lataa", "Käynnistyy"):
                desired_on = False
            elif chip_text == "Ei lataa":
                desired_on = True
            if desired_on is None:
                st.session_state["eqe_charge_msg"] = (
                    "info",
                    f"Latausta ei muuteta (tila: {chip_text}).",
                )
            else:
                plug_status = _charging_plug_status(vm.charging_state, vm.charging_state_raw)
                if desired_on and plug_status == "disconnected":
                    st.session_state["eqe_charge_msg"] = (
                        "err",
                        "Kaapeli ei ole kiinni.",
                    )
                else:
                    try:
                        set_eqe_charging_enabled(desired_on)
                        try:
                            refresh_eqe_charging_power()
                        except Exception:
                            pass
                        st.session_state["eqe_power_probe"] = {
                            "expected_on": desired_on,
                            "due_at": time.time() + 10.0,
                        }
                        st.session_state["eqe_charge_override"] = {
                            "value": desired_on,
                            "ts": time.time(),
                        }
                        st.session_state["eqe_charge_msg"] = (
                            "info",
                            "Lataus kytketty päälle." if desired_on else "Lataus kytketty pois.",
                        )
                        fetch_eqe_status.clear()
                        st.rerun()
                    except Exception as e:
                        st.session_state["eqe_charge_msg"] = (
                            "err",
                            f"Latauksen ohjaus epäonnistui: {e}",
                        )
        if lock_available:
            if lock_pending_action == "lock":
                lock_class, lock_text = ("chip yellow pulse", "Lukitaan")
                lock_on = True
            elif lock_pending_action == "unlock":
                lock_class, lock_text = ("chip yellow pulse", "Avataan")
                lock_on = False
            else:
                lock_class, lock_text = _lock_chip(vm.lock_state)
                lock_on = _lock_is_locked(vm.lock_state)
        else:
            lock_class, lock_text = ("chip yellow", "Ei käytössä")
            lock_on = False
        if preclimate_available:
            if preclimate_pending_action == "on":
                preclimate_class, preclimate_text = ("chip yellow pulse", "Käynnistetään")
                preclimate_on = False
            else:
                preclimate_class, preclimate_text = _preclimate_chip(vm.preclimate_state)
                preclimate_on = _preclimate_is_on(vm.preclimate_state)
                if preclimate_on:
                    preclimate_class = f"{preclimate_class} pulse"
        else:
            preclimate_class, preclimate_text = ("chip yellow", "Ei käytössä")
            preclimate_on = False
        power_html = _fmt_value(vm.charging_power_kw, vm.charging_power_unit or "kW", digits=1)
        updated_label = vm.last_changed.strftime("%H:%M") if vm.last_changed else "—"

        bg = _get_eqe_background()
        overlay = "linear-gradient(90deg, rgba(11,15,20,0.70) 0%, rgba(11,15,20,0.10) 72%)"
        bg_layer = f"{overlay}, url('{bg}')" if bg else overlay

        if lock_available and not lock_pending_action:
            lock_action = "unlock" if lock_on else "lock"
            lock_html = (
                "<form method='get' style='margin:0; display:inline;'>"
                f"<button class='eqe-switch' type='submit' "
                f"name='eqe_lock' value='{lock_action}'>"
                f"<span class='{lock_class}'>{html.escape(lock_text)}</span>"
                "</button></form>"
            )
        else:
            lock_html = f"<span class='{lock_class}'>{html.escape(lock_text)}</span>"
        if preclimate_available and not preclimate_pending_action:
            preclimate_action = "off" if preclimate_on else "on"
            preclimate_html = (
                "<form method='get' style='margin:0; display:inline;'>"
                f"<button class='eqe-switch' type='submit' "
                f"name='eqe_preclimate' value='{preclimate_action}'>"
                f"<span class='{preclimate_class}'>{html.escape(preclimate_text)}</span>"
                "</button></form>"
            )
        else:
            preclimate_html = (
                f"<span class='{preclimate_class}'>{html.escape(preclimate_text)}</span>"
            )
        charge_html = (
            "<form method='get' style='margin:0; display:inline;'>"
            "<button class='eqe-switch' type='submit' name='eqe_charge' value='toggle'>"
            f"<span class='{chip_class}'>{html.escape(chip_text)}</span>"
            "</button></form>"
        )

        body = f"""
        <div class="eqe-grid">
          <div class="eqe-item">
            <div class="eqe-label">SoC</div>
            <div class="eqe-value">{soc_html}</div>
          </div>
          <div class="eqe-item">
            <div class="eqe-label">Range</div>
            <div class="eqe-value">{range_html}</div>
          </div>
          <div class="eqe-item">
            <div class="eqe-label">Lataus</div>
            <div class="eqe-value">{charge_html}</div>
          </div>
          <div class="eqe-item">
            <div class="eqe-label">Lukitus</div>
            <div class="eqe-value">{lock_html}</div>
          </div>
          <div class="eqe-item">
            <div class="eqe-label">Ilmastointi</div>
            <div class="eqe-value">{preclimate_html}</div>
          </div>
          <div class="eqe-item">
            <div class="eqe-label">Latausteho</div>
            <div class="eqe-value">{power_html}</div>
          </div>
        </div>
        """
        st.markdown(
            f"""
            <section class="card eqe-card" style="background-image:{bg_layer}; background-size:cover; background-position:center;">
              <div class="card-body">{body}</div>
            </section>
            """,
            unsafe_allow_html=True,
        )
        for msg_key in ("eqe_preclimate_msg", "eqe_lock_msg", "eqe_charge_msg"):
            msg = st.session_state.pop(msg_key, None)
            if msg:
                kind, text = msg
                if kind == "err":
                    st.error(text)
                elif kind == "info":
                    st.info(text)
        if lock_pending_action or preclimate_pending_action or charging_polling:
            st_html("<script>setTimeout(() => window.location.reload(), 10000);</script>", height=0)
        st.markdown(
            f"<div class='hint' style='margin-top:16px; margin-bottom:2px;'>Päivitetty: {html.escape(updated_label)}</div>",
            unsafe_allow_html=True,
        )

    except HAConfigError as e:
        st.markdown(
            f"""
            <section class="card" style="min-height:12dvh;">
              <div class="card-body"><span class="hint">{html.escape(str(e))}</span></div>
            </section>
            """,
            unsafe_allow_html=True,
        )
    except Exception as e:
        details = ""
        st.markdown(
            f"""
            <section class="card" style="min-height:12dvh;">
              <div class="card-body">
                <span class="hint">Virhe: {html.escape(str(e))}</span>
                {details}
              </div>
            </section>
            """,
            unsafe_allow_html=True,
        )
