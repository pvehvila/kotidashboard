import datetime as dt
import types

import pytest
import requests

import src.api.electricity_adapters as ea
from src.api import electricity_adapters as adapters

TODAY = dt.date(2025, 11, 11)


@pytest.mark.parametrize(
    "func_name,scenario,expected_type",
    [
        # --- get_hourly_from_porssisahko ---
        ("get_hourly_from_porssisahko", "empty_latest", type(None)),
        ("get_hourly_from_porssisahko", "no_data_for_day", type(None)),
        ("get_hourly_from_porssisahko", "one_hour_ok", list),
        # --- get_15min_from_porssisahko ---
        ("get_15min_from_porssisahko", "empty_latest", type(None)),
        ("get_15min_from_porssisahko", "no_15min_for_day", type(None)),
        ("get_15min_from_porssisahko", "fifteen_min_ok", list),
        # --- get_hourly_from_sahkonhintatanaan ---
        ("get_hourly_from_sahkonhintatanaan", "empty_raw", type(None)),
        ("get_hourly_from_sahkonhintatanaan", "normalized_ok", list),
    ],
)
def test_electricity_adapters_handle_weird_data(monkeypatch, func_name, scenario, expected_type):
    """
    Adaptereiden ei pitäisi kaatua, vaikka lähdepalvelu palauttaa tyhjää tai outoa dataa.
    Kelvollisessa tapauksessa niiden pitäisi palauttaa lista.
    """
    func = getattr(adapters, func_name)

    # 1) yhteiset no-op patchit
    # näissä funktioissa logitetaan ja raportoidaan virheitä – ei tarvita testeissä
    monkeypatch.setattr(adapters, "log_raw_prices", lambda *a, **k: None)
    monkeypatch.setattr(adapters, "report_error", lambda *a, **k: None)

    # 2) skenaarioiden mukaiset patchit
    if func_name == "get_hourly_from_porssisahko":
        # tämä funktio tekee:
        # latest = fetch_from_porssisahko_latest()
        # per_hour = filter_latest_to_day(latest, date)
        if scenario == "empty_latest":
            monkeypatch.setattr(adapters, "fetch_from_porssisahko_latest", lambda: None)
        elif scenario == "no_data_for_day":
            monkeypatch.setattr(adapters, "fetch_from_porssisahko_latest", lambda: {"some": "data"})
            monkeypatch.setattr(adapters, "filter_latest_to_day", lambda *_: {})
        elif scenario == "one_hour_ok":
            # palautetaan päivän data siten, että filter_latest_to_day saa tunnin 0 kaksi arvoa
            monkeypatch.setattr(adapters, "fetch_from_porssisahko_latest", lambda: {"raw": "ok"})
            monkeypatch.setattr(adapters, "filter_latest_to_day", lambda *_: {0: [5.0, 7.0]})
        result = func(TODAY)

    elif func_name == "get_15min_from_porssisahko":
        # tämä funktio tekee:
        # latest = fetch_from_porssisahko_latest()
        # out = normalize_prices_list_15min(latest, date)
        if scenario == "empty_latest":
            monkeypatch.setattr(adapters, "fetch_from_porssisahko_latest", lambda: None)
        elif scenario == "no_15min_for_day":
            monkeypatch.setattr(adapters, "fetch_from_porssisahko_latest", lambda: {"raw": "ok"})
            monkeypatch.setattr(adapters, "normalize_prices_list_15min", lambda *_: [])
        elif scenario == "fifteen_min_ok":
            monkeypatch.setattr(adapters, "fetch_from_porssisahko_latest", lambda: {"raw": "ok"})
            monkeypatch.setattr(
                adapters,
                "normalize_prices_list_15min",
                lambda *_: [
                    {"ts": dt.datetime(2025, 11, 11, 0, 0), "cents": 5.0},
                    {"ts": dt.datetime(2025, 11, 11, 0, 15), "cents": 5.1},
                ],
            )
        result = func(TODAY)

    else:  # get_hourly_from_sahkonhintatanaan
        # tämä funktio tekee:
        # raw = fetch_from_sahkonhintatanaan(date)
        # log_raw_prices(...)
        # prices = normalize_prices_list(raw, date)
        if scenario == "empty_raw":
            monkeypatch.setattr(adapters, "fetch_from_sahkonhintatanaan", lambda *_: [])
            monkeypatch.setattr(adapters, "normalize_prices_list", lambda *_: None)
        elif scenario == "normalized_ok":
            monkeypatch.setattr(adapters, "fetch_from_sahkonhintatanaan", lambda *_: [{"dummy": 1}])
            monkeypatch.setattr(
                adapters,
                "normalize_prices_list",
                lambda *_: [{"hour": 0, "cents": 6.0}],
            )
        result = func(TODAY)

    # 3) tarkistus
    assert isinstance(result, expected_type)


def _make_http_error(status_code: int) -> requests.HTTPError:
    err = requests.HTTPError("boom")
    err.response = types.SimpleNamespace(status_code=status_code)
    return err


def test_get_hourly_from_porssisahko_http_400_returns_none_and_no_report(monkeypatch):
    def fake_latest():
        raise _make_http_error(400)

    report_called = False

    def fake_report_error(msg, exc):
        nonlocal report_called
        report_called = True

    monkeypatch.setattr(ea, "fetch_from_porssisahko_latest", fake_latest)
    monkeypatch.setattr(ea, "report_error", fake_report_error)

    out = ea.get_hourly_from_porssisahko(dt.date(2023, 1, 1))
    assert out is None
    assert report_called is False


def test_get_hourly_from_porssisahko_http_500_reports_error(monkeypatch):
    def fake_latest():
        raise _make_http_error(500)

    calls: list[tuple[str, BaseException]] = []

    def fake_report_error(msg, exc):
        calls.append((msg, exc))

    monkeypatch.setattr(ea, "fetch_from_porssisahko_latest", fake_latest)
    monkeypatch.setattr(ea, "report_error", fake_report_error)

    out = ea.get_hourly_from_porssisahko(dt.date(2023, 1, 1))
    assert out is None
    assert len(calls) == 1
    assert "porssisahko" in calls[0][0]


def test_get_hourly_from_sahkonhintatanaan_http_404_returns_none_and_no_report(monkeypatch):
    def fake_fetch(_date):
        raise _make_http_error(404)

    report_called = False

    def fake_report_error(msg, exc):
        nonlocal report_called
        report_called = True

    monkeypatch.setattr(ea, "fetch_from_sahkonhintatanaan", fake_fetch)
    monkeypatch.setattr(ea, "report_error", fake_report_error)

    out = ea.get_hourly_from_sahkonhintatanaan(dt.date(2023, 1, 1))
    assert out is None
    assert report_called is False


def test_get_hourly_from_sahkonhintatanaan_http_500_reports_error(monkeypatch):
    def fake_fetch(_date):
        raise _make_http_error(500)

    calls: list[tuple[str, BaseException]] = []

    def fake_report_error(msg, exc):
        calls.append((msg, exc))

    monkeypatch.setattr(ea, "fetch_from_sahkonhintatanaan", fake_fetch)
    monkeypatch.setattr(ea, "report_error", fake_report_error)

    out = ea.get_hourly_from_sahkonhintatanaan(dt.date(2023, 1, 1))
    assert out is None
    assert len(calls) == 1
    assert "sahkonhintatanaan" in calls[0][0]


def test_get_15min_from_porssisahko_generic_exception_reports_error(monkeypatch):
    def fake_latest():
        raise ValueError("some parsing problem")

    calls: list[tuple[str, BaseException]] = []

    def fake_report_error(msg, exc):
        calls.append((msg, exc))

    monkeypatch.setattr(ea, "fetch_from_porssisahko_latest", fake_latest)
    monkeypatch.setattr(ea, "report_error", fake_report_error)

    out = ea.get_15min_from_porssisahko(dt.date(2023, 1, 1))
    assert out is None
    assert len(calls) == 1
    assert "v2 15min" in calls[0][0]
