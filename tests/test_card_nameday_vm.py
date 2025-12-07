# tests/test_card_nameday_vm.py
import datetime as dt
import importlib


def _get_card_module():
    # varmistetaan, että haetaan varsinainen src/ui/card_nameday.py
    return importlib.import_module("src.ui.card_nameday")


class DummySt:
    def __init__(self):
        self.markdowns: list[str] = []

    def markdown(self, html, unsafe_allow_html=False):  # noqa: ARG002
        self.markdowns.append(html)


def _freeze_today(card_mod, monkeypatch, when: dt.datetime) -> None:
    """Korvaa card_nameday.datetime.now palauttamaan halutun päivän."""

    class FrozenDateTime(dt.datetime):
        @classmethod
        def now(cls, tz=None):  # type: ignore[override]
            if tz is not None:
                if when.tzinfo is None:
                    return when.replace(tzinfo=tz)
                return when.astimezone(tz)
            return when

    # card_nameday teki: from datetime import datetime
    # → module-level nimi 'datetime' viittaa luokkaan
    monkeypatch.setattr(card_mod, "datetime", FrozenDateTime)


def test_get_nameday_vm_basic(monkeypatch):
    card_mod = _get_card_module()

    # datalähteet stubiksi
    monkeypatch.setattr(card_mod, "fetch_nameday_today", lambda: "Mauno")
    monkeypatch.setattr(card_mod, "_get_sun_times", lambda: ("08:00", "16:00"))
    monkeypatch.setattr(card_mod, "get_flag_info", lambda today: ("Isänpäivä", "dbg"))  # noqa: ARG005
    monkeypatch.setattr(
        card_mod,
        "fetch_holiday_today",
        lambda _cache_buster=None: {
            "holiday": "Isänpäivä",
            "is_flag_day": True,
            "is_holiday": True,
        },
    )
    monkeypatch.setattr(card_mod, "get_background_image", lambda: "bg-url")

    fake_today = dt.datetime(2024, 11, 11, 9, 0, tzinfo=card_mod.TZ)
    _freeze_today(card_mod, monkeypatch, fake_today)

    vm = card_mod.get_nameday_vm()

    assert vm["names"] == "Mauno"
    assert vm["sunrise"] == "08:00"
    assert vm["sunset"] == "16:00"
    assert vm["flag_txt"] == "Isänpäivä"
    assert vm["holiday_info"]["holiday"] == "Isänpäivä"
    assert vm["background"] == "bg-url"

    # Päivämerkkijono: pitää sisältää päivän ja kuukauden
    assert "11" in vm["day_str"]
    assert vm["day_str"].endswith(".11.")


def test_render_nameday_card_renders_html(monkeypatch):
    card_mod = _get_card_module()

    dummy_st = DummySt()
    monkeypatch.setattr(card_mod, "st", dummy_st)

    vm = {
        "today": dt.datetime(2024, 11, 11, 9, 0),
        "names": "Mauno",
        "weekday_label": "maanantaina",
        "day_str": "11.11.",
        "sunrise": "08:00",
        "sunset": "16:00",
        "flag_txt": "Isänpäivä",
        "flag_debug": None,
        "background": "bg-url",
        "holiday_info": {
            "holiday": "Isänpäivä",
            "is_flag_day": True,
            "is_holiday": True,
        },
    }

    card_mod.render_nameday_card(vm)

    html = "".join(dummy_st.markdowns)
    assert "Mauno" in html
    assert "Nimipäivät" in html
    assert "Isänpäivä" in html
    assert "08:00" in html
    assert "16:00" in html
