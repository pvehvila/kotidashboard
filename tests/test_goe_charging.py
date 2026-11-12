import pytest

import src.api.home_assistant as ha


@pytest.mark.parametrize("enabled,option", [(True, "2"), (False, "1")])
def test_goe_force_state_service(monkeypatch, enabled, option):
    monkeypatch.setattr(
        ha,
        "_require_config",
        lambda: {
            "base_url": "http://ha",
            "token": "test",
            "charging_switch_entity": "select.goe_test_frc",
        },
    )
    calls = []
    monkeypatch.setattr(ha, "_call_service", lambda *args: calls.append(args))
    ha.set_eqe_charging_enabled(enabled)
    assert calls == [
        (
            "http://ha",
            "test",
            "select",
            "select_option",
            {"entity_id": "select.goe_test_frc", "option": option},
            None,
        )
    ]


@pytest.mark.parametrize(
    "raw,expected",
    [("0", None), ("1", False), ("2", True), ("unknown", None), ("unavailable", None)],
)
def test_goe_control_state(raw, expected):
    assert (
        ha._charging_control_state(
            {
                "entity_id": "select.goe_test_frc",
                "state": raw,
            }
        )
        is expected
    )


@pytest.mark.parametrize("enabled,service", [(True, "turn_on"), (False, "turn_off")])
def test_existing_switch_service(monkeypatch, enabled, service):
    monkeypatch.setattr(
        ha,
        "_require_config",
        lambda: {
            "base_url": "http://ha",
            "token": "test",
            "charging_switch_entity": "switch.charger",
        },
    )
    calls = []
    monkeypatch.setattr(ha, "_call_service", lambda *args: calls.append(args))
    ha.set_eqe_charging_enabled(enabled)
    assert calls[0][2:5] == ("switch", service, {"entity_id": "switch.charger"})


def test_unrelated_select_is_rejected(monkeypatch):
    monkeypatch.setattr(
        ha,
        "_require_config",
        lambda: {
            "charging_switch_entity": "select.unrelated",
        },
    )
    with pytest.raises(ha.HAConfigError, match="force state"):
        ha.set_eqe_charging_enabled(True)
