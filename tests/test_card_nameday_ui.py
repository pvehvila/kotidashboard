import importlib

from src.ui.card_nameday import card_nameday

# moduuli ja funktio erikseen
card_nameday_module = importlib.import_module("src.ui.card_nameday")


def test_card_nameday_renders_happy_path(monkeypatch):
    # Käytetään valmista viewmodelia, eikä sotketa syvempiä riippuvuuksia.
    vm = {
        "today": None,
        "names": "Maija",
        "weekday_label": "maanantaina",
        "day_str": "1.1.",
        "sunrise": "08:00",
        "sunset": "16:00",
        "flag_txt": "Itsenäisyyspäivä",
        "flag_debug": "",
        "background": "https://example.test/bg.jpg",
        "holiday_info": None,
    }

    monkeypatch.setattr(card_nameday_module, "get_nameday_vm", lambda: vm)

    captured: dict[str, str] = {}

    def fake_markdown(html: str, unsafe_allow_html: bool = False) -> None:
        captured["html"] = html
        captured["unsafe"] = "true" if unsafe_allow_html else "false"

    monkeypatch.setattr(card_nameday_module.st, "markdown", fake_markdown)

    # act
    card_nameday()  # HUOM: funktio, ei moduuli

    # assert
    html = captured["html"]

    # otsikkotekstin muoto on yksi kokonaisrivi -> "Nimipäivät maanantaina 1.1."
    assert "Nimipäivät maanantaina 1.1." in html

    # nimet
    assert "Maija" in html

    # liputuspäiväteksti
    assert "Itsenäisyyspäivä" in html

    # aurinkoajat
    assert "08:00" in html
    assert "16:00" in html

    # taustakuva on mukana osana background-image-riviä
    assert "background-image" in html
    assert "https://example.test/bg.jpg" in html

    # kortin pitää sallia HTML
    assert captured["unsafe"] == "true"
