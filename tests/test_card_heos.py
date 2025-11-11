# tests/test_card_heos.py

import importlib

from src.heos_client import HeosClient


def _get_card_module():
    # haetaan nimenomaan varsinainen tiedosto src/ui/card_heos.py,
    # ei src.ui -paketin attribuuttia
    return importlib.import_module("src.ui.card_heos")


def test_card_heos_renders_now_playing(monkeypatch):
    card_mod = _get_card_module()

    # ei tarvita oikeaa section_titlea
    monkeypatch.setattr(card_mod, "section_title", lambda *a, **k: None)

    # feikataan HeosClient
    class FakeClient(HeosClient):
        def __init__(self, *a, **k):
            pass

        def sign_in(self):
            pass

        def get_now_playing(self, pid):
            return {
                "payload": {
                    "song": "Track",
                    "artist": "Artist",
                    "album": "Album",
                }
            }

    monkeypatch.setattr(card_mod, "HeosClient", FakeClient)

    # feikki-Streamlit
    class DummySt:
        session_state: dict = {}

        def columns(self, n):
            return [self, self, self]

        def button(self, *a, **k):
            return False

        def markdown(self, html, unsafe_allow_html=False):
            self.html = html

    dummy_st = DummySt()
    monkeypatch.setattr(card_mod, "st", dummy_st)

    # kutsu korttia
    card_mod.card_heos()

    html = dummy_st.html
    assert "Track" in html
    assert "Artist" in html
    assert "Album" in html
    assert "Ei HEOS-toistoa" not in html


def test_card_heos_renders_empty(monkeypatch):
    card_mod = _get_card_module()
    monkeypatch.setattr(card_mod, "section_title", lambda *a, **k: None)

    class FakeClient(HeosClient):
        def __init__(self, *a, **k):
            pass

        def sign_in(self):
            pass

        def get_now_playing(self, pid):
            # ei kappaletta
            return {"payload": {}}

    monkeypatch.setattr(card_mod, "HeosClient", FakeClient)

    class DummySt:
        session_state: dict = {}

        def columns(self, n):
            return [self, self, self]

        def button(self, *a, **k):
            return False

        def markdown(self, html, unsafe_allow_html=False):
            self.html = html

    dummy_st = DummySt()
    monkeypatch.setattr(card_mod, "st", dummy_st)

    card_mod.card_heos()

    html = dummy_st.html
    assert "Ei HEOS-toistoa" in html


def test_pause_and_resume(monkeypatch):
    card_mod = _get_card_module()
    monkeypatch.setattr(card_mod, "section_title", lambda *a, **k: None)

    calls = {}

    class FakeClient(HeosClient):
        def __init__(self, *a, **k):
            pass

        def sign_in(self):
            pass

        def get_volume(self, pid):
            return 15

        def set_mute(self, pid, state):
            calls.setdefault("mute", []).append(state)

        def set_volume(self, pid, level):
            calls["volume"] = level

        def get_now_playing(self, pid):
            return {"payload": {}}

    monkeypatch.setattr(card_mod, "HeosClient", FakeClient)

    class DummySt:
        def __init__(self):
            self.session_state = {}

        def columns(self, n):
            return [self, self, self]

        def button(self, label, **k):
            # kortti tekee 3 nappia, haluamme että ⏯️ = True
            return label == "⏯️"

        def markdown(self, html, unsafe_allow_html=False):
            self.html = html

    dummy_st = DummySt()
    monkeypatch.setattr(card_mod, "st", dummy_st)

    # 1. painallus -> mute on
    card_mod.card_heos()
    assert calls["mute"] == ["on"]
    assert dummy_st.session_state["heos_paused"] is True
    assert dummy_st.session_state["heos_prev_volume"] == 15

    # 2. painallus -> mute off + volume back
    dummy_st.session_state["heos_paused"] = True
    dummy_st.session_state["heos_prev_volume"] = 42
    card_mod.card_heos()
    assert calls["mute"] == ["on", "off"]
    assert calls["volume"] == 42
