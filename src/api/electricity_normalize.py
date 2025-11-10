from __future__ import annotations

import datetime as dt
from datetime import datetime, timedelta

from src.config import TZ

Price15 = dict[str, datetime | float]  # {"ts": datetime, "cents": float}


# ----------------- peruskenttien purku -----------------


def parse_cents_from_item(item: dict) -> float | None:
    """
    Tukee sekä v2:n 'price' (snt/kWh) että vanhemman datan 'cents' / 'value' -tyyppisiä kenttiä.
    """
    is_v2_like = "startDate" in item or "endDate" in item

    for key in ("cents", "cents_per_kwh", "price", "Price", "value", "Value", "EUR_per_kWh"):
        if value := item.get(key):
            try:
                price = float(value)
            except ValueError:
                continue

            if is_v2_like:
                # v2 antaa jo oikeassa muodossa
                return price

            # vanha data saattoi antaa euroina
            return price if price >= 1.0 else price * 100.0

    return None


def parse_hour_from_item(item: dict, idx: int, date_ymd: dt.date) -> int | None:
    # suorat tuntikentät
    for key in ("hour", "Hour", "H"):
        if value := item.get(key):
            try:
                hour = int(value)
                if 0 <= hour <= 23:
                    return hour
            except ValueError:
                pass

    # aikaleimamuodot
    for key in (
        "time",
        "Time",
        "timestamp",
        "Timestamp",
        "datetime",
        "DateTime",
        "start",
        "Start",
        "startDate",
    ):
        if value := item.get(key):
            try:
                ts = str(value).replace("Z", "+00:00")
                dt_obj = datetime.fromisoformat(ts)
                if dt_obj.tzinfo is None:
                    dt_obj = dt_obj.replace(tzinfo=TZ)
                else:
                    dt_obj = dt_obj.astimezone(TZ)
                if dt_obj.date() == date_ymd and 0 <= dt_obj.hour <= 23:
                    return dt_obj.hour
            except ValueError:
                continue

    # fallback: rivin indeksi
    return idx if 0 <= idx <= 23 else None


# ----------------- normalisoinnit -----------------


def normalize_prices_list(items: list[dict], date_ymd: dt.date) -> list[dict[str, float]]:
    """
    Muuntaa sekalaisen listan → [{"hour": h, "cents": x}, ...]
    """
    out_map: dict[int, float] = {}
    for idx, item in enumerate(items or []):
        try:
            hour = parse_hour_from_item(item, idx, date_ymd)
            cents = parse_cents_from_item(item)
            if hour is not None and cents is not None and 0 <= hour <= 23 and hour not in out_map:
                out_map[hour] = float(cents)
        except Exception:
            continue
    return [{"hour": h, "cents": out_map[h]} for h in sorted(out_map.keys())]


def normalize_prices_list_15min(items: list[dict], date_ymd: dt.date) -> list[Price15]:
    """
    Muuttaa varttidatan → [{"ts": ..., "cents": ...}, ...] ja ottaa vain pyydetyn päivän.
    """
    out_map: dict[datetime, float] = {}

    for idx, item in enumerate(items or []):
        ts: datetime | None = None

        # löydä kellonaika jostain järkevästä kentästä
        for key in (
            "time",
            "Time",
            "timestamp",
            "Timestamp",
            "datetime",
            "DateTime",
            "start",
            "Start",
            "startDate",
            "endDate",
        ):
            if key in item and item[key]:
                try:
                    tmp = str(item[key]).replace("Z", "+00:00")
                    dt_obj = datetime.fromisoformat(tmp)
                    if dt_obj.tzinfo is None:
                        dt_obj = dt_obj.replace(tzinfo=TZ)
                    else:
                        dt_obj = dt_obj.astimezone(TZ)
                    ts = dt_obj
                except Exception:
                    ts = None
                break

        if ts is None:
            # fallback: klo 00:00 + idx * 15 min
            base = datetime.combine(date_ymd, datetime.min.time()).replace(tzinfo=TZ)
            ts = base + timedelta(minutes=15 * idx)

        # pyöristetään varttiin
        q = (ts.minute // 15) * 15
        ts = ts.replace(minute=q, second=0, microsecond=0)

        if ts.date() != date_ymd:
            continue

        cents = parse_cents_from_item(item)
        if cents is None:
            continue

        if ts not in out_map:
            out_map[ts] = float(cents)

    return [{"ts": ts, "cents": out_map[ts]} for ts in sorted(out_map.keys())]


def expand_hourly_to_15min(hourly: list[dict[str, float]], date_ymd: dt.date) -> list[Price15]:
    """
    Tuntidata → neljä varttia / tunti.
    """
    out: list[Price15] = []

    for item in hourly:
        hour = int(item["hour"])
        cents = float(item["cents"])

        base = datetime.combine(date_ymd, datetime.min.time()).replace(tzinfo=TZ) + timedelta(
            hours=hour
        )

        for q in range(4):
            ts = base + timedelta(minutes=15 * q)
            out.append({"ts": ts, "cents": cents})

    return out
