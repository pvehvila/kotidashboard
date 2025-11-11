# tests/test_card_prices_helpers.py
import datetime as dt

from src.config import TZ
from src.ui.card_prices import _current_price_15min, _next_12h_15min


def test_current_price_15min_matches_exact_slot():
    now = dt.datetime(2025, 11, 11, 10, 23, tzinfo=TZ)
    slot = now.replace(minute=15, second=0, microsecond=0)

    prices_today = [
        {"ts": slot, "cents": 7.5},
    ]

    val = _current_price_15min(prices_today, now)
    assert val == 7.5


def test_next_12h_15min_builds_rows_from_today_and_tomorrow():
    now = dt.datetime(2025, 11, 11, 23, 50, tzinfo=TZ)

    today_slot = now.replace(minute=45, second=0, microsecond=0)
    tomorrow_slot = (today_slot + dt.timedelta(minutes=15)).replace(tzinfo=TZ)

    prices_today = [{"ts": today_slot, "cents": 5.0}]
    prices_tomorrow = [{"ts": tomorrow_slot, "cents": 6.0}]

    rows = _next_12h_15min(prices_today, prices_tomorrow, now)
    # ainakin ensimmäiset kaksi pitäisi löytyä
    assert any(r["cents"] == 5.0 for r in rows)
    assert any(r["cents"] == 6.0 for r in rows)
