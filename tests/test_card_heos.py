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

    # feikataan HeosClient nykyisen card_heos-logiikan mukaan:
    # get_now_playing palauttaa suoraan dictin, jossa on song/artist/album
    class FakeClient(HeosClient):
        def __init__(self, *a, **k):
            pass

        def sign_in(self):
            pass

        def get_now_playing(self, pid):
            return {
                "song": "Track",
                "artist": "Artist",
                "album": "Album",
            }

    monkeypatch.setattr(card_mod, "HeosClient", FakeClient)

    # feikki-Streamlit
    class DummySt:
        session_state: dict = {}

        # Context manager -tuki, koska kortti tekee: with col_prev / col_play / col_next
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def columns(self, *args, **kwargs):
            # Kortti pyytää 5 kolumnia (esim. [1,1,1,1,1])
            return [self, self, self, self, self]

        def button(self, *a, **k):
            # Tässä testissä ei paineta mitään nappia
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

    # ei kappaletta -> get_now_playing palauttaa tyhjän dictin
    class FakeClient(HeosClient):
        def __init__(self, *a, **k):
            pass

        def sign_in(self):
            pass

        def get_now_playing(self, pid):
            return {}

    monkeypatch.setattr(card_mod, "HeosClient", FakeClient)

    class DummySt:
        session_state: dict = {}

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def columns(self, *args, **kwargs):
            return [self, self, self, self, self]

        def button(self, *a, **k):
            return False

        def markdown(self, html, unsafe_allow_html=False):
            self.html = html

    dummy_st = DummySt()
    monkeypatch.setattr(card_mod, "st", dummy_st)

    card_mod.card_heos()

    html = dummy_st.html
    assert "Ei HEOS-toistoa käynnissä." in html
    assert "Track" not in html
    assert "Artist" not in html
    assert "Album" not in html


def test_card_heos_buttons_call_client(monkeypatch):
    """Varmistetaan, että ohjauspainikkeet kutsuvat HEOS-asiakkaan metodeja."""
    card_mod = _get_card_module()
    monkeypatch.setattr(card_mod, "section_title", lambda *a, **k: None)

    calls: list[str] = []

    class FakeClient(HeosClient):
        def __init__(self, *a, **k):
            pass

        def sign_in(self):
            calls.append("sign_in")

        def get_now_playing(self, pid):
            # ei väliä tämän testin kannalta, tyhjä dictriittää
            return {}

        def play_previous(self, pid):
            calls.append("prev")

        def play_pause(self, pid):
            calls.append("play_pause")

        def play_next(self, pid):
            calls.append("next")

    monkeypatch.setattr(card_mod, "HeosClient", FakeClient)

    class DummySt:
        def __init__(self):
            self.session_state = {}
            self.html = ""

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def columns(self, *args, **kwargs):
            return [self, self, self, self, self]

        def button(self, label, **k):
            # Palautetaan True kaikille kolmelle ohjauspainikkeelle,
            # jotta kaikki metodit kutsutaan kerran.
            if label in ("⏮", "⏯", "⏭"):
                return True
            return False

        def markdown(self, html, unsafe_allow_html=False):
            self.html = html

    dummy_st = DummySt()
    monkeypatch.setattr(card_mod, "st", dummy_st)

    card_mod.card_heos()

    # sign_in kutsutaan kerran kortin alussa
    assert "sign_in" in calls
    # kaikki kolme ohjausmetodia kutsuttu
    assert "prev" in calls
    assert "play_pause" in calls
    assert "next" in calls
