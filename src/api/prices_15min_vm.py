# src/api/prices_15min_vm.py
from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any

from src.api import try_fetch_prices_15min
from src.config import PRICE_Y_STEP_SNT, TZ
from src.utils import _color_by_thresholds


def current_price_15min(
    prices_today: list[dict[str, datetime | float]] | None,
    now_dt: datetime,
) -> float | None:
    """Nykyinen 15 min hinta tai None, puhdas datalogiikka."""
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


def next_12h_15min(
    prices_today: list[dict[str, datetime | float]] | None,
    prices_tomorrow: list[dict[str, datetime | float]] | None,
    now_dt: datetime,
) -> list[dict[str, datetime | str | float | bool]]:
    """
    Rakenna seuraavien 12 tunnin (48 × 15 min) slotit.

    Palauttaa listan:
    {
        "ts": datetime,
        "label": "HH:MM",
        "cents": float,
        "is_now": bool,
    }
    """
    if not prices_today and not prices_tomorrow:
        return []

    rows: list[dict[str, datetime | str | float | bool]] = []
    minute = (now_dt.minute // 15) * 15
    base = now_dt.replace(minute=minute, second=0, microsecond=0)

    for i in range(48):
        ts = base + timedelta(minutes=15 * i)

        src = prices_today if ts.date() == now_dt.date() else prices_tomorrow
        if not src:
            continue

        hit = next(
            (p for p in src if isinstance(p.get("ts"), datetime) and p["ts"] == ts),
            None,
        )

        if not hit:
            # etsi lähellä; joskus ts voi heittää vähän
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


def build_prices_15min_vm(now_dt: datetime | None = None) -> dict[str, Any]:
    """
    Viewmodel sähkökortille.

    Palauttaa:
    {
      "now": datetime,
      "current_cents": float | None,
      "rows": [...],
      "values": list[float],
      "colors": list[str],
      "line_colors": list[str],
      "line_widths": list[float],
      "y_min": float,
      "y_max": float,
      "y_step": float,
    }
    """
    now_dt = now_dt or datetime.now(TZ)
    today: date = now_dt.date()
    tomorrow: date = today + timedelta(days=1)

    prices_today = try_fetch_prices_15min(today)
    prices_tomorrow = try_fetch_prices_15min(tomorrow)

    rows = next_12h_15min(prices_today, prices_tomorrow, now_dt=now_dt)

    # Nykyhinta
    current_cents = current_price_15min(prices_today, now_dt) if prices_today else None

    # Arvot ja värit
    values: list[float] = []
    for row in rows:
        val = row.get("cents")
        if isinstance(val, (int | float)):
            values.append(float(val))
        else:
            values.append(0.0)

    if values:
        colors = _color_by_thresholds(list(values))
    else:
        colors = []

    line_colors = [
        "rgba(255,255,255,0.9)" if row.get("is_now") else "rgba(0,0,0,0)" for row in rows
    ]
    line_widths = [1.5 if row.get("is_now") else 0 for row in rows]

    step = float(max(1, PRICE_Y_STEP_SNT))
    if values:
        y_min_src = min(values)
        y_max_src = max(values)
    else:
        y_min_src = 0.0
        y_max_src = step

    y_min = float((y_min_src // step) * step)
    y_max = float(((y_max_src + step - 1) // step) * step)
    if y_max <= y_min:
        y_max = y_min + step

    return {
        "now": now_dt,
        "current_cents": current_cents,
        "rows": rows,
        "values": values,
        "colors": colors,
        "line_colors": line_colors,
        "line_widths": line_widths,
        "y_min": y_min,
        "y_max": y_max,
        "y_step": step,
    }
