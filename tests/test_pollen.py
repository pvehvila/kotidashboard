from __future__ import annotations

from src.api.pollen import parse_pollen_text


def test_parse_pollen_text_extracts_riihimaki_relevant_levels():
    text = """
    Siitepölytiedote 3.5.2026.
    Uudellamaalla ja Hämeessä koivun siitepölyä on ilmassa runsaasti.
    Heinien siitepölyä esiintyy maan eteläosissa vähäisiä määriä.
    Pujon kukinnan odotetaan alkavan eteläisessä Suomessa lähipäivinä kohtalaisena.
    Pohjois-Suomessa koivua on ilmassa vähän.
    """

    vm = parse_pollen_text(text)

    assert vm.location == "Riihimäki"
    assert vm.updated == "3.5.2026"

    plants = {plant.key: plant for plant in vm.plants}
    assert plants["koivu"].level == "runsaasti"
    assert plants["heinät"].level == "vähän"
    assert plants["pujo"].level == "kohtalaisesti"
    assert "lähipäivinä" in plants["pujo"].forecast


def test_parse_pollen_text_uses_no_pollen_when_plant_is_missing():
    vm = parse_pollen_text("Siitepölytiedote. Uudellamaalla lepän siitepölyä on vähän.")

    plants = {plant.key: plant for plant in vm.plants}
    assert plants["koivu"].level == "ei havaittu"
    assert plants["heinät"].level == "ei havaittu"
    assert plants["pujo"].level == "ei havaittu"
    assert "Ei koivun" in vm.summary
