from __future__ import annotations

import datetime as dt
from datetime import datetime, timedelta

from src.config import TZ

# varttidata: {"ts": datetime, "cents": float}
Price15 = dict[str, datetime | float]
# tuntidata: {"hour": int, "cents": float}
HourPrice = dict[str, float]


# ============================================================
# YLEISET APUFUNKTIOT
# ============================================================


def _parse_cents_from_item(item: dict) -> float | None:
    """
    Tukee sekä v2:n 'price' (snt/kWh) että vanhemman datan 'cents' / 'value' -tyyppisiä kenttiä.
    Palauttaa aina senteissä.
    """
    is_v2_like = "startDate" in item or "endDate" in item

    for key in (
        "cents",
        "cents_per_kwh",
        "price",
        "Price",
        "value",
        "Value",
        "EUR_per_kWh",
    ):
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


def _parse_hour_from_item(item: dict, idx: int, date_ymd: dt.date) -> int | None:
    """
    Yrittää löytää tunnin useasta eri kentästä.
    Jos mikään ei osu, palauttaa rivin indeksin (0–23) jos se on ok.
    """
    # 1) suorat kentät
    for key in ("hour", "Hour", "H"):
        if value := item.get(key):
            try:
                hour = int(value)
            except ValueError:
                break
            if 0 <= hour <= 23:
                return hour

    # 2) aikaleimamuodot
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
            except ValueError:
                continue

            # lisää / konvertoi aikavyöhyke
            if dt_obj.tzinfo is None:
                dt_obj = dt_obj.replace(tzinfo=TZ)
            else:
                dt_obj = dt_obj.astimezone(TZ)

            if dt_obj.date() == date_ymd:
                hour = dt_obj.hour
                if 0 <= hour <= 23:
                    return hour

    # 3) fallback: indeksistä
    return idx if 0 <= idx <= 23 else None


def _parse_ts_15min_from_item(item: dict, date_ymd: dt.date, idx: int) -> datetime:
    """
    Yhteinen tapa hakea varttidatan aikaleima.
    Jos mitään ei saada, käytetään: päivä klo 00:00 + idx*15min.
    """
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
            except Exception:
                break

            if dt_obj.tzinfo is None:
                dt_obj = dt_obj.replace(tzinfo=TZ)
            else:
                dt_obj = dt_obj.astimezone(TZ)

            return dt_obj

    # fallback
    base = datetime.combine(date_ymd, datetime.min.time()).replace(tzinfo=TZ)
    return base + timedelta(minutes=15 * idx)


# ============================================================
# VAIHE 1 — TUNTIEN PARSEROINTI
# ============================================================


def parse_hourly_to_map(items: list[dict], date_ymd: dt.date) -> dict[int, float]:
    """
    Lukee sekalaisen listan ja palauttaa puhtaan mapin: {hour: cents, ...}
    TÄMÄ tekee kaiken "arvaamisen".
    """
    out: dict[int, float] = {}

    for idx, item in enumerate(items or []):
        hour = _parse_hour_from_item(item, idx, date_ymd)
        cents = _parse_cents_from_item(item)

        if hour is None or cents is None:
            continue

        if not (0 <= hour <= 23):
            continue

        # älä ylikirjoita ensimmäistä onnistunutta arvoa
        if hour not in out:
            out[hour] = float(cents)

    return out


# ============================================================
# VAIHE 2 — NORMALISOINTI
# ============================================================


def normalize_hourly_map(hour_map: dict[int, float]) -> list[HourPrice]:
    """
    Muuntaa {hour: cents} -> [{"hour": h, "cents": x}, ...] järjestyksessä.
    Tämä on se muoto jota muu koodi yleensä käyttää.
    """
    return [{"hour": h, "cents": hour_map[h]} for h in sorted(hour_map.keys())]


def normalize_prices_list(items: list[dict], date_ymd: dt.date) -> list[HourPrice]:
    """
    Säilytetään vanha nimi taaksepäin yhteensopivuuden vuoksi.

    Uusi putki:
        raakadata -> parse_hourly_to_map(...) -> normalize_hourly_map(...)
    """
    hour_map = parse_hourly_to_map(items, date_ymd)
    return normalize_hourly_map(hour_map)


# ============================================================
# VAIHE 3 — 60min -> 15min LAAJENNUS
# ============================================================


def expand_hourly_to_15min(hourly: list[HourPrice], date_ymd: dt.date) -> list[Price15]:
    """
    Tuntidata -> neljä varttia / tunti.
    """
    out: list[Price15] = []

    for item in hourly:
        hour = int(item["hour"])
        cents = float(item["cents"])

        base = datetime.combine(date_ymd, datetime.min.time()).replace(tzinfo=TZ).replace(hour=hour)

        for q in range(4):
            ts = base + timedelta(minutes=15 * q)
            out.append({"ts": ts, "cents": cents})

    return out


# ============================================================
# 15min-DATA OMANA REITTINÄÄN
# ============================================================


def normalize_prices_list_15min(items: list[dict], date_ymd: dt.date) -> list[Price15]:
    """
    Muuttaa varttidatan -> [{"ts": ..., "cents": ...}, ...] ja ottaa vain pyydetyn päivän.
    """
    out_map: dict[datetime, float] = {}

    for idx, item in enumerate(items or []):
        ts = _parse_ts_15min_from_item(item, date_ymd, idx)

        # pyöristetään lähimpään varttiin alaspäin
        q = (ts.minute // 15) * 15
        ts = ts.replace(minute=q, second=0, microsecond=0)

        if ts.date() != date_ymd:
            continue

        cents = _parse_cents_from_item(item)
        if cents is None:
            continue

        if ts not in out_map:
            out_map[ts] = float(cents)

    return [{"ts": ts, "cents": out_map[ts]} for ts in sorted(out_map.keys())]
