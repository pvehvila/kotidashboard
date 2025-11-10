from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from src.api import try_fetch_prices_15min
from src.config import TZ


def _current_price_15min(
    prices_today: list[dict[str, Any]] | None,
    now_dt: datetime,
) -> float | None:
    """Palauttaa kuluvan 15 min slotin hinnan senteissä, jos löytyy."""
    if not prices_today:
        return None

    minute = (now_dt.minute // 15) * 15
    slot = now_dt.replace(minute=minute, second=0, microsecond=0)

    hit = next(
        (p for p in prices_today if isinstance(p.get("ts"), datetime) and p["ts"] == slot),
        None,
    )
    if not hit:
        return None

    cents_val = hit.get("cents")
    if not isinstance(cents_val, (int | float)):
        return None
    return float(cents_val)


def _next_12h_15min(
    prices_today: list[dict[str, Any]] | None,
    prices_tomorrow: list[dict[str, Any]] | None,
    now_dt: datetime,
) -> list[dict[str, Any]]:
    """Rakentaa seuraavat 12h / 15min slotit yhtenä listana."""
    if not prices_today and not prices_tomorrow:
        return []

    rows: list[dict[str, Any]] = []

    minute = (now_dt.minute // 15) * 15
    base = now_dt.replace(minute=minute, second=0, microsecond=0)

    # 12 h = 48 * 15 min
    for i in range(48):
        ts = base + timedelta(minutes=15 * i)

        # valitaan oikean päivän lista
        src = prices_today if ts.date() == now_dt.date() else prices_tomorrow
        if not src:
            continue

        # normaali täsmähaku
        hit = next(
            (p for p in src if isinstance(p.get("ts"), datetime) and p["ts"] == ts),
            None,
        )

        # joskus ts heittää < 60 s -> etsitään lähin
        if not hit:
            for p in src:
                ts_p = p.get("ts")
                if not isinstance(ts_p, datetime):
                    continue
                if abs((ts_p - ts).total_seconds()) < 60:
                    hit = p
                    break

        if not hit:
            continue

        cents_val = hit.get("cents")
        if not isinstance(cents_val, (int | float)):
            cents_val = 0.0

        rows.append(
            {
                "ts": ts,
                "label": ts.strftime("%H:%M"),
                "cents": float(cents_val),
                "is_now": i == 0,
            }
        )

    return rows


def build_electricity_12h_view(now_dt: datetime | None = None) -> dict[str, Any]:
    """
    Rakentaa sähkökortille valmiin viewmodelin:
      - current_cents: kuluvan slotin hinta
      - rows: seuraavat 12h / 15 min
      - fetched: True/False, onnistuiko haku ylipäätään
    """
    if now_dt is None:
        now_dt = datetime.now(TZ)

    today = now_dt.date()
    tomorrow = today + timedelta(days=1)

    prices_today = try_fetch_prices_15min(today)
    prices_tomorrow = try_fetch_prices_15min(tomorrow)

    rows = _next_12h_15min(prices_today, prices_tomorrow, now_dt)
    current_cents = _current_price_15min(prices_today, now_dt)

    return {
        "now_dt": now_dt,
        "current_cents": current_cents,
        "rows": rows,
        "fetched": bool(prices_today or prices_tomorrow),
    }
