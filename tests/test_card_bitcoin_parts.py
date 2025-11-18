from __future__ import annotations

from datetime import datetime, timedelta

import pytest

import src.ui.card_bitcoin_parts as cbp


def _series_sample() -> list[tuple[datetime, float]]:
    now = datetime(2025, 1, 1, 12, 0, 0, tzinfo=cbp.TZ)
    return [
        (now - timedelta(hours=1), 60000.0),
        (now, 60500.0),
    ]


# ------------------------------------------------------------
# Data-puoli: 24h/7d/30d sarjojen rakennus
# ------------------------------------------------------------


def test_build_24h_from_7d_returns_24h_if_enough_points():
    now = datetime(2025, 1, 2, 12, 0, 0, tzinfo=cbp.TZ)
    s7 = [
        (now - timedelta(hours=23), 60000.0),
        (now - timedelta(hours=1), 60500.0),
    ]

    s24, degraded = cbp._build_24h_from_7d(now, s7)
    assert not degraded
    assert len(s24) == 2
    assert all(t >= now - timedelta(hours=24) for t, _ in s24)


def test_build_24h_from_7d_degrades_if_too_few_points():
    now = datetime(2025, 1, 2, 12, 0, 0, tzinfo=cbp.TZ)
    s7 = [(now - timedelta(days=3), 60000.0)]  # vain yksi piste

    s24, degraded = cbp._build_24h_from_7d(now, s7)
    assert degraded is True
    assert s24 == s7


def test_fallback_7d_raises_when_no_data(monkeypatch):
    monkeypatch.setattr(cbp, "fetch_btc_last_7d_eur", lambda: [])

    with pytest.raises(ValueError):
        cbp._fallback_7d("24h")


def test_get_btc_series_for_window_24h_direct(monkeypatch):
    s24 = _series_sample()

    monkeypatch.setattr(cbp, "fetch_btc_last_24h_eur", lambda: s24)
    monkeypatch.setattr(cbp, "fetch_btc_eur_range", lambda *a, **k: [])
    monkeypatch.setattr(cbp, "fetch_btc_last_7d_eur", lambda: [])

    series, degraded = cbp.get_btc_series_for_window("24h")
    assert series == s24
    assert degraded is False


def test_get_btc_series_for_window_24h_from_7d(monkeypatch):
    # 24 h ei palauta mitään → rakennetaan 7 d datasta
    s7 = _series_sample()

    monkeypatch.setattr(cbp, "fetch_btc_last_24h_eur", lambda: [])
    monkeypatch.setattr(cbp, "fetch_btc_eur_range", lambda *a, **k: [])
    monkeypatch.setattr(cbp, "fetch_btc_last_7d_eur", lambda: s7)

    series, degraded = cbp.get_btc_series_for_window("24h")
    # koska sample kattaa vain ~1 h → degrade True ja käytetään koko 7d-sarjaa
    assert series == s7
    assert degraded is True


def test_get_btc_series_for_window_30d_falls_back_to_7d(monkeypatch):
    s7 = _series_sample()

    monkeypatch.setattr(cbp, "fetch_btc_last_30d_eur", lambda: [])
    monkeypatch.setattr(cbp, "fetch_btc_last_7d_eur", lambda: s7)
    monkeypatch.setattr(cbp, "fetch_btc_last_24h_eur", lambda: [])
    monkeypatch.setattr(cbp, "fetch_btc_eur_range", lambda *a, **k: [])

    series, degraded = cbp.get_btc_series_for_window("30d")
    assert series == s7
    assert degraded is True


# ------------------------------------------------------------
# UI-palaset: pillit, otsikko, footer
# ------------------------------------------------------------


def test_build_window_pill_active_and_inactive():
    active_html = cbp.build_window_pill("7d", "7d", "7 d")
    inactive_html = cbp.build_window_pill("7d", "30d", "30 d")

    assert "bwin=7d" in active_html or "?bwin=7d" in active_html
    assert "background:#e7eaee" in active_html  # aktiivinen

    assert "bwin=30d" in inactive_html or "?bwin=30d" in inactive_html
    assert "background:rgba(255,255,255,0.10)" in inactive_html  # passiivinen


def test_build_title_html_includes_price_and_change_and_window():
    html = cbp.build_title_html(65000.0, 1.23, "24h")
    assert "Bitcoin" in html
    assert "65000" in html.replace(" ", "")
    assert "1.23%" in html
    assert "24 h" in html


def test_build_footer_html_ath_and_degraded_flags():
    html = cbp.build_footer_html(
        window="30d",
        degraded=True,
        ath_eur=69000.0,
        ath_date="2021-11-10T15:00:00Z",
    )
    # ATH-info
    assert "2021-11-10" in html
    assert "69000" in html.replace(" ", "")
    # degrade-viesti 30d → 7d
    assert "30 d data ei saatavilla" in html

    html_24 = cbp.build_footer_html(
        window="24h",
        degraded=True,
        ath_eur=None,
        ath_date=None,
    )
    assert "Viimeiset 24 h viipaloitu 7 d -datasta" in html_24


# ------------------------------------------------------------
# Viewmodel ja kuvaaja
# ------------------------------------------------------------


def test_get_btc_figure_vm_has_label_and_axis_range():
    series = _series_sample()
    vm = cbp.get_btc_figure_vm(series, window="7d", ath_eur=70000.0, ath_date=None)

    assert vm.xs and vm.ys
    assert vm.name == "BTC/EUR (7 d)"
    assert "%d.%m %H:%M" in vm.hovertemplate
    assert vm.y_min is not None and vm.y_max is not None
    assert vm.label_text is not None
    assert "€" in vm.label_text


def test_build_btc_figure_produces_plotly_figure():
    series = _series_sample()
    fig = cbp.build_btc_figure(
        series=series,
        window="7d",
        ath_eur=70000.0,
        ath_date="2021-11-10T15:00:00Z",
    )

    # Peruscheck: traceja ja anotaatioita on
    assert fig.data  # truthy → vähintään yksi trace
    assert "€" in fig.layout.yaxis.title.text
