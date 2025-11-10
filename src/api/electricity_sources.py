from __future__ import annotations

import datetime as dt
from datetime import datetime

from src.api.http import http_get_json
from src.config import TZ


def fetch_from_sahkonhintatanaan(date_ymd: dt.date) -> list[dict]:
    """
    Hakee https://www.sahkonhintatanaan.fi/… v1-muodossa.
    Palauttaa sellaisenaan listan itemeitä, normalisointi tehdään muualla.
    """
    url = f"https://www.sahkonhintatanaan.fi/api/v1/prices/{date_ymd:%Y}/{date_ymd:%m-%d}.json"
    data = http_get_json(url)
    # data voi olla {"prices": [...]} tai suoraan lista
    if isinstance(data, dict):
        return data.get("prices", []) or []
    return data or []


def fetch_from_porssisahko_v1(date_ymd: dt.date) -> list[dict]:
    """
    VANHA tuntipohjainen haku, jos sitä joskus tarvitaan.
    (Voit poistaa tämän jos ei ole käytössä.)
    """
    url = f"https://api.porssisahko.net/v1/price.json?date={date_ymd:%Y-%m-%d}"
    data = http_get_json(url)
    if isinstance(data, dict):
        return data.get("prices", []) or []
    return data or []


def fetch_from_porssisahko_latest() -> list[dict]:
    """
    Hakee v2-rajapinnan 48 h varttidatan.
    Tämä on se sama, jota vanha koodi kutsui suoraan.
    """
    url = "https://api.porssisahko.net/v2/latest-prices.json"
    data = http_get_json(url)
    if isinstance(data, dict):
        return data.get("prices", []) or []
    return []


def filter_latest_to_day(items: list[dict], date_ymd: dt.date) -> dict[int, list[float]]:
    """
    Muuntaa v2:n varttidatasta “päivä → tunti → list[price]”.
    Tätä käytetään, kun halutaan tuntihinnat v2:sta.
    """
    per_hour: dict[int, list[float]] = {}

    for item in items:
        start = item.get("startDate")
        price = item.get("price")
        if not start or price is None:
            continue

        try:
            dt_utc = datetime.fromisoformat(str(start).replace("Z", "+00:00"))
            dt_local = dt_utc.astimezone(TZ)
        except Exception:
            continue

        if dt_local.date() != date_ymd:
            continue

        hour = dt_local.hour
        per_hour.setdefault(hour, []).append(float(price))

    return per_hour
