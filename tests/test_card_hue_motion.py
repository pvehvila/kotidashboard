# tests/test_card_hue_motion.py

import importlib

from src.viewmodels.hue_motion import WANTED_NAMES, MotionRow


def _get_card_module():
    # Haetaan nimenomaan varsinainen card_hue_motion -moduuli
    return importlib.import_module("src.ui.card_hue_motion")


class DummyCol:
    """Simuloi yhtä Streamlit-kolumnia (context manager + markdown)."""

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def markdown(self, html, unsafe_allow_html=False):
        self.html = html


class DummySt:
    """Minimaalinen Streamlit-mock, jota kortti käyttää."""

    def __init__(self):
        self.session_state = {}
        self.markdowns: list[str] = []

    def columns(self, n, gap=None):
        # Palautetaan täsmälleen n kolumnia
        return [DummyCol() for _ in range(n)]

    def markdown(self, html, unsafe_allow_html=False):
        self.markdowns.append(html)

    def __getattr__(self, name):
        # Mahdolliset muut st.* -kutsut (joita emme erikseen testaa) → no-op
        return lambda *a, **k: None


def test_card_hue_motion_happy_path(monkeypatch):
    """Bridge toimii ja viewmodel palauttaa tavalliset rivit."""
    card_mod = _get_card_module()

    # Ei tarvita oikeaa section_title-logiikkaa
    monkeypatch.setattr(card_mod, "section_title", lambda *a, **k: None)

    dummy_st = DummySt()
    monkeypatch.setattr(card_mod, "st", dummy_st)

    rows = [
        MotionRow(
            name=n,
            status_label="Ovi kiinni",
            idle_for_str="1 min sitten",
            bg_role="closed",
        )
        for n in WANTED_NAMES
    ]
    monkeypatch.setattr(card_mod, "load_hue_motion_viewmodel", lambda: rows)

    card_mod.card_hue_motion()

    html = "".join(dummy_st.markdowns)
    # Otsikon alla pitäisi olla vihreä Hue Bridge -chip
    assert "Hue Bridge: OK" in html

    # Jokaisen oven kortin pitäisi näkyä HTML:ssä
    for name in WANTED_NAMES:
        assert name in html


def test_card_hue_motion_offline(monkeypatch):
    """Jos viewmodel heittää poikkeuksen → näytetään offline-chip."""
    card_mod = _get_card_module()
    monkeypatch.setattr(card_mod, "section_title", lambda *a, **k: None)

    dummy_st = DummySt()
    monkeypatch.setattr(card_mod, "st", dummy_st)

    def fail():
        raise RuntimeError("bridge unreachable")

    monkeypatch.setattr(card_mod, "load_hue_motion_viewmodel", fail)

    card_mod.card_hue_motion()

    html = "".join(dummy_st.markdowns)
    assert "Hue Bridge: OFFLINE" in html
    assert "bridge unreachable" in html

    # Placeholder-rivit renderöityvät kaikille WANTED_NAMES-arvoille
    for name in WANTED_NAMES:
        assert name in html


def test_card_hue_motion_renders_roles_and_icons(monkeypatch):
    """UI renderöi kortit eri roolien mukaan ja sisältää oikeat ikonit."""
    card_mod = _get_card_module()
    monkeypatch.setattr(card_mod, "section_title", lambda *a, **k: None)

    dummy_st = DummySt()
    monkeypatch.setattr(card_mod, "st", dummy_st)

    # HUOM: vain 3 riviä, koska kortti renderöi 3 kolumnia
    rows = [
        MotionRow(name="A", status_label="Ovi auki", idle_for_str="1 m", bg_role="open"),
        MotionRow(name="B", status_label="Ovi kiinni", idle_for_str="2 m", bg_role="closed"),
        MotionRow(name="C", status_label="Ei tietoa", idle_for_str="?", bg_role="stale"),
    ]
    monkeypatch.setattr(card_mod, "load_hue_motion_viewmodel", lambda: rows)

    card_mod.card_hue_motion()

    html = "".join(dummy_st.markdowns)

    # open → 🚪🔓
    assert "A" in html and "🚪🔓" in html
    # closed → 🚪🔒
    assert "B" in html and "🚪🔒" in html
    # stale → 🚪⏳
    assert "C" in html and "🚪⏳" in html


def test_icon_for_unknown_role():
    """Erillinen testi: unknown-rooli → 🚪❔."""
    card_mod = _get_card_module()
    row = MotionRow(
        name="X",
        status_label="Ei tietoa",
        idle_for_str="?",
        bg_role="unknown",
    )
    icon = card_mod._icon_for_row(row)
    assert icon == "🚪❔"
