# tests/test_card_hue_doors.py

import importlib

from src.viewmodels.hue_contacts import WANTED_DOORS, DoorRow


def _get_card_module():
    return importlib.import_module("src.ui.card_hue_doors")


class DummyCol:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def markdown(self, html, unsafe_allow_html=False):
        self.html = html


class DummySt:
    def __init__(self):
        self.session_state = {}
        self.markdowns: list[str] = []

    def columns(self, n, gap=None):
        return [DummyCol() for _ in range(n)]

    def markdown(self, html, unsafe_allow_html=False):
        self.markdowns.append(html)

    def __getattr__(self, name):
        # esim. section_title kutsuu st.* → sallitaan no-op
        return lambda *a, **k: None


def test_card_hue_doors_happy_path(monkeypatch):
    card_mod = _get_card_module()
    monkeypatch.setattr(card_mod, "section_title", lambda *a, **k: None)

    dummy_st = DummySt()
    monkeypatch.setattr(card_mod, "st", dummy_st)

    rows = [
        DoorRow(
            name=n,
            status_label="Ovi kiinni",
            idle_for_str="1 min sitten",
            bg_role="closed",
        )
        for n in WANTED_DOORS
    ]
    monkeypatch.setattr(card_mod, "load_hue_contacts_viewmodel", lambda: rows)

    card_mod.card_hue_doors()

    html = "".join(dummy_st.markdowns)
    assert "Hue Secure: OK" in html
    for name in WANTED_DOORS:
        assert name in html


def test_card_hue_doors_config_error(monkeypatch):
    card_mod = _get_card_module()
    monkeypatch.setattr(card_mod, "section_title", lambda *a, **k: None)

    dummy_st = DummySt()
    monkeypatch.setattr(card_mod, "st", dummy_st)

    # käytetään moduulin omaa HueV2ConfigError-luokkaa
    def fail():
        raise card_mod.HueV2ConfigError("config missing")

    monkeypatch.setattr(card_mod, "load_hue_contacts_viewmodel", fail)

    card_mod.card_hue_doors()

    html = "".join(dummy_st.markdowns)
    assert "Hue Secure: OFFLINE" in html
    assert "config missing" in html
    # virhetilassa renderöidään placeholder-kortit
    for name in WANTED_DOORS:
        assert name in html
        assert "Hue Secure -konfiguraatio puuttuu" in html


def test_card_hue_doors_generic_error(monkeypatch):
    card_mod = _get_card_module()
    monkeypatch.setattr(card_mod, "section_title", lambda *a, **k: None)

    dummy_st = DummySt()
    monkeypatch.setattr(card_mod, "st", dummy_st)

    def fail():
        raise RuntimeError("bridge unreachable")

    monkeypatch.setattr(card_mod, "load_hue_contacts_viewmodel", fail)

    card_mod.card_hue_doors()

    html = "".join(dummy_st.markdowns)
    assert "Hue Secure: OFFLINE" in html
    assert "bridge unreachable" in html
    assert "Ei yhteyttä Hue Bridgeen" in html


def test_icon_for_unknown_role():
    card_mod = _get_card_module()
    row = DoorRow(
        name="X",
        status_label="Ei tietoa",
        idle_for_str="?",
        bg_role="unknown",
    )
    icon = card_mod._icon_for_row(row)
    assert icon == "🚪❔"
