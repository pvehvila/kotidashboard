from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any
from urllib.parse import quote

from src.api.http import http_get_json
from src.api.weather_mapping import wmo_to_foreca_code
from src.api.weather_utils import as_bool, as_float, as_int
from src.config import TZ


# --- uudet pienet hakufunktiot -------------------------------------------------
def fetch_forecast(lat: float, lon: float, tz_name: str) -> dict[str, Any]:
    """Hakee Open-Meteosta tuntiennusteen raakana."""
    url = (
        "https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}"
        "&hourly=temperature_2m,precipitation_probability,weathercode,cloudcover,is_day"
        f"&timezone={quote(tz_name)}"
    )
    return http_get_json(url)


def fetch_current(lat: float, lon: float, tz_name: str) -> dict[str, Any]:
    """
    Oma paikka nykytilalle.
    Jos haluat myöhemmin hakea esim. https://api.open-meteo.com/v1/forecast?current=...
    -endpointin, tee se tänne.
    Nyt palautetaan vain tyhjä dict, jotta rajapinta on olemassa.
    """
    return {}


def fetch_alerts(lat: float, lon: float, tz_name: str) -> dict[str, Any]:
    """
    Oma paikka säähälytyksille.
    Open-Meteolla on erillinen weather alerts -kysely, jonka voi myöhemmin lisätä tähän.
    """
    return {}


# --- apufunktiot dashboard-mapitukseen -----------------------------------------
def _map_hourly_to_dashboard(
    hourly: dict[str, Any],
    now: datetime,
    offsets: tuple[int, ...],
) -> dict[str, Any]:
    """
    Muuntaa Open-Meteon hourly-datan dashboardin käyttämään muotoon.

    Parametrit:
        hourly: Open-Meteon "hourly"-lohko.
        now: "nyt"-aikaleima (pyöristetty tuntiin).
        offsets: tunnit nyt-hetkestä (0, 3, 6, ...) joille pisteet lasketaan.
    """
    times: list[str] = hourly.get("time", []) or []
    temps: list[Any] = hourly.get("temperature_2m", []) or []
    pops: list[Any] = hourly.get("precipitation_probability", []) or []
    wmos: list[Any] = hourly.get("weathercode", []) or []
    covers: list[Any] = hourly.get("cloudcover", []) or []
    isday: list[Any] = hourly.get("is_day", []) or []

    points: list[dict[str, Any]] = []

    for offset in offsets:
        target_time = now + timedelta(hours=offset)
        ts = target_time.strftime("%Y-%m-%dT%H:00")

        try:
            idx = times.index(ts)
        except ValueError:
            # kyseistä tuntia ei tullut api:sta
            continue

        raw_temp = temps[idx] if idx < len(temps) else None
        raw_pop = pops[idx] if idx < len(pops) else None
        raw_wmo = wmos[idx] if idx < len(wmos) else None
        raw_ccov = covers[idx] if idx < len(covers) else None
        raw_isday = isday[idx] if idx < len(isday) else None

        temp = as_float(raw_temp)
        pop = as_int(raw_pop)
        wmo = as_int(raw_wmo)
        ccov = as_int(raw_ccov)
        is_day_flag = as_bool(raw_isday)

        # fallback: päätellään päivä/yö kellonajasta jos api ei kerro
        is_day = is_day_flag if is_day_flag is not None else (6 <= target_time.hour <= 20)

        points.append(
            {
                "label": "Nyt" if offset == 0 else f"+{offset} h",
                "hour": target_time.hour,
                "temp": temp,
                "pop": pop,
                "key": wmo_to_foreca_code(
                    wmo,
                    is_day=is_day,
                    pop=pop,
                    temp_c=temp,
                    cloudcover=ccov,
                ),
            }
        )

    # päivän min/max kuten ennen
    min_temp = max_temp = None
    try:
        day_str = now.strftime("%Y-%m-%d")
        idxs = [i for i, t in enumerate(times) if t.startswith(day_str)]
        vals = [temps[i] for i in idxs if i < len(temps)]
        if vals:
            min_temp, max_temp = min(vals), max(vals)
    except Exception:
        # ei kaadeta dashboardia tämän takia
        pass

    return {
        "points": points,
        "min_temp": min_temp,
        "max_temp": max_temp,
    }


# --- vanha dashboard-funktio, nyt vain valitsee lähteen ------------------------
def fetch_weather_points(
    lat: float,
    lon: float,
    tz_name: str,
    offsets: tuple[int, ...] = (0, 3, 6, 9, 12),
) -> dict[str, Any]:
    """
    Hakee tuntiennusteen ja palauttaa dashboardin käyttämän rakenteen.

    Päävastuu:
      * valita/hauttaa datalähteen (nyt: fetch_forecast)
      * antaa raakadatan _map_hourly_to_dashboard-apufunktiolle

    Paluuarvo on pidetty entisellään, jotta UI ei hajoa.
    """
    data = fetch_forecast(lat, lon, tz_name)
    hourly = data.get("hourly") or {}

    now = datetime.now(TZ).replace(minute=0, second=0, microsecond=0)

    return _map_hourly_to_dashboard(hourly=hourly, now=now, offsets=offsets)
