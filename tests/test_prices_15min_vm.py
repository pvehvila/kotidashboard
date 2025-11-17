import datetime as dt

import pytest

import src.api.prices_15min_vm as vm


def _slot(base: dt.datetime, minutes: int) -> dt.datetime:
    """Apufunktio: base + minutes, sekunnit nollaan."""
    return (base + dt.timedelta(minutes=minutes)).replace(second=0, microsecond=0)


# ---------------------------------------------------------------------------
# current_price_15min
# ---------------------------------------------------------------------------


def test_current_price_15min_returns_exact_slot_value():
    now = dt.datetime(2025, 1, 1, 10, 7)  # pyöristyy alas 10:00
    slot_10 = now.replace(minute=0, second=0, microsecond=0)
    slot_10_15 = now.replace(minute=15, second=0, microsecond=0)

    prices_today = [
        {"ts": slot_10, "cents": 5.0},
        {"ts": slot_10_15, "cents": 10.0},
    ]

    out = vm.current_price_15min(prices_today, now_dt=now)
    assert out == pytest.approx(5.0)


def test_current_price_15min_returns_none_when_no_matching_slot():
    now = dt.datetime(2025, 1, 1, 10, 7)
    # ts on väärä, ei pyöristettyyn aikaan
    prices_today = [
        {"ts": now.replace(minute=5, second=0, microsecond=0), "cents": 99.0},
    ]

    out = vm.current_price_15min(prices_today, now_dt=now)
    assert out is None


# ---------------------------------------------------------------------------
# next_12h_15min
# ---------------------------------------------------------------------------


def test_next_12h_15min_builds_48_points_across_today_and_tomorrow():
    # Aloitetaan 21:30 -> 12 h eteenpäin menee seuraavan päivän aamupuolelle
    now = dt.datetime(2025, 1, 1, 21, 30, 0)
    today = now.date()
    tomorrow = today + dt.timedelta(days=1)

    # Luodaan täysi 24 h 15 min -ruudukko molemmille päiville
    def build_day_prices(day: dt.date, start_hour=0) -> list[dict]:
        out = []
        base = dt.datetime(day.year, day.month, day.day, start_hour, 0, 0)
        for i in range(96):  # 96 * 15 min = 24 h
            ts = base + dt.timedelta(minutes=15 * i)
            out.append({"ts": ts, "cents": float(i)})
        return out

    prices_today = build_day_prices(today, start_hour=0)
    prices_tomorrow = build_day_prices(tomorrow, start_hour=0)

    rows = vm.next_12h_15min(
        prices_today=prices_today,
        prices_tomorrow=prices_tomorrow,
        now_dt=now,
    )

    # 12 h / 15 min = 48 slottia
    assert len(rows) == 48

    # Ensimmäinen ts on pyöristetty "nyt"
    assert rows[0]["ts"] == now
    assert rows[0]["is_now"] is True
    assert all((r["is_now"] is False) for r in rows[1:])

    # Ts-muuttujat nousevassa järjestyksessä
    ts_list = [r["ts"] for r in rows]
    assert ts_list == sorted(ts_list)

    # Mukana sekä tämän päivän että huomisen päiväyksiä
    # (otetaan vain ne rivit, joissa ts on datetime)
    dates = {r["ts"].date() for r in rows if isinstance(r["ts"], dt.datetime)}
    assert today in dates
    assert tomorrow in dates


def test_next_12h_15min_uses_fuzzy_matching_for_nearby_timestamps():
    # Testataan että < 60 s heitto ts:ssä kelpaa
    now = dt.datetime(2025, 1, 2, 12, 0, 0)
    # tallennetaan ts + 30 s, mutta haetaan tasaminuutille pyöristettynä
    stored_ts = now + dt.timedelta(seconds=30)

    prices_today = [{"ts": stored_ts, "cents": 42.0}]
    prices_tomorrow = None

    rows = vm.next_12h_15min(
        prices_today=prices_today,
        prices_tomorrow=prices_tomorrow,
        now_dt=now,
    )

    # Ensimmäisen rivin cents tulee löydetystä slotista
    assert rows
    assert rows[0]["cents"] == pytest.approx(42.0)


# ---------------------------------------------------------------------------
# build_prices_15min_vm – integraatiotyyppinen testi mockatulla datalla
# ---------------------------------------------------------------------------


def test_build_prices_15min_vm_aggregates_today_and_tomorrow(monkeypatch):
    # Kiinteä "nyt", klo 05:00
    now = dt.datetime(2025, 1, 3, 5, 0, 0)
    today = now.date()
    tomorrow = today + dt.timedelta(days=1)

    # Rakennetaan tänään 05:00–06:45 (8 slottia)
    today_slots = []
    base_today = now
    for i in range(8):
        ts = _slot(base_today, 15 * i)
        today_slots.append({"ts": ts, "cents": 5.0 + i})

    # Huomenna jatkuu 7 slottia lisää
    tomorrow_slots = []
    base_tomorrow = dt.datetime(tomorrow.year, tomorrow.month, tomorrow.day, 7, 0, 0)
    for i in range(7):
        ts = _slot(base_tomorrow, 15 * i)
        tomorrow_slots.append({"ts": ts, "cents": 20.0 + i})

    def fake_try_fetch_prices_15min(day: dt.date):
        if day == today:
            return today_slots
        if day == tomorrow:
            return tomorrow_slots
        return None

    monkeypatch.setattr(vm, "try_fetch_prices_15min", fake_try_fetch_prices_15min)

    out = vm.build_prices_15min_vm(now_dt=now)

    # Perusrakenne
    assert out["now"] == now
    rows = out["rows"]
    assert isinstance(rows, list)
    assert rows, "rows ei saa olla tyhjä kun dataa on tarjolla"

    # Nykyisen slotin hinta tulee oikein
    assert out["current_cents"] == pytest.approx(5.0)

    values = out["values"]
    assert len(values) == len(rows)
    assert all(isinstance(v, float) for v in values)

    # Värit, viivat ym. ovat samannumeroisia kuin rivit
    assert len(out["colors"]) == len(rows)
    assert len(out["line_colors"]) == len(rows)
    assert len(out["line_widths"]) == len(rows)

    # y-akselin range kattaa arvot
    y_min = out["y_min"]
    y_max = out["y_max"]
    assert y_min <= min(values)
    assert y_max >= max(values)
    assert out["y_step"] > 0
