import importlib
import types

# Yritetään ensin pakettirakennetta
try:
    card_mod = importlib.import_module("src.ui.card_system")
except ModuleNotFoundError:
    # ja jos projekti onkin "kortti samassa kansiossa" -mallilla
    card_mod = importlib.import_module("card_system")


def test_card_system_renders_html(monkeypatch):
    """Perustesti: varmistaa että kortin HTML generoituu ja kutsut tehdään."""
    assert isinstance(card_mod, types.ModuleType)

    called = {}

    def fake_section_title(title, mt=None, mb=None):
        called["title"] = title

    def fake_st_html(html, height=None, scrolling=None):
        called["html"] = html
        called["height"] = height
        called["scrolling"] = scrolling

    # patchataan NIMET MODUULISTA, ei funktiosta
    monkeypatch.setattr(card_mod, "section_title", fake_section_title)
    monkeypatch.setattr(card_mod, "st_html", fake_st_html)
    monkeypatch.setattr(card_mod, "get_ip", lambda: "1.2.3.4")

    # kutsu itse korttia
    card_mod.card_system()

    # tarkistukset
    assert "Järjestelmätila" in called["title"]
    html = called["html"]
    assert "IP:" in html
    assert "Päivitetty:" in html
    assert "Fully Kiosk Browser" in html
    assert called["height"] == 200
    assert called["scrolling"] is False


def test_card_system_handles_exception(monkeypatch):
    """Jos get_ip kaatuu, kortti ei saa pysähtyä virheeseen."""

    # kaadetaan get_ip
    monkeypatch.setattr(
        card_mod,
        "get_ip",
        lambda: (_ for _ in ()).throw(RuntimeError("no net")),
    )

    # nämä voi olla stubbeja
    monkeypatch.setattr(card_mod, "section_title", lambda *a, **k: None)

    captured = {}

    # card_system käyttää streamlitin st.markdownia virhetilassa
    monkeypatch.setattr(
        card_mod.st,
        "markdown",
        lambda text, unsafe_allow_html: captured.setdefault("text", text),
    )

    card_mod.card_system()

    assert "Virhe" in captured["text"]
