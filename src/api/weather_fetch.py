from __future__ import annotations

from datetime import date, datetime, timedelta
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
def _build_time_axis(hourly_raw: dict[str, Any], tz_name: str) -> list[datetime]:
    """
    Parsii Open-Meteon "time"-listan datetime-olioiksi.

    Tällä hetkellä tz_name ei ole kriittinen (ajat ovat jo oikeassa aikavyöhykkeessä),
    mutta pidetään se rajapinnassa mahdollisia tulevia muutoksia varten.
    """
    raw_times: list[str] = hourly_raw.get("time", []) or []
    axis: list[datetime] = []

    for t in raw_times:
        try:
            dt = datetime.fromisoformat(t)
        except ValueError:
            # rikkinäinen aikaleima -> ohitetaan
            continue

        # jos aikaleima on naivi, sidotaan se dashboardin oletus-TZ:ään
        if dt.tzinfo is None and TZ is not None:
            dt = dt.replace(tzinfo=TZ)

        axis.append(dt)

    return axis


def _build_time_index(time_axis: list[datetime]) -> dict[datetime, int]:
    """Rakentaa nopean aikaleima → indeksi -hakemiston ilman poikkeuspohjaista logiikkaa."""
    return {ts: idx for idx, ts in enumerate(time_axis)}


def _extract_point_fields(
    temps: list[Any],
    pops: list[Any],
    wmos: list[Any],
    covers: list[Any],
    isday: list[Any],
    idx: int,
) -> tuple[float | None, int | None, int | None, int | None, bool | None]:
    """
    Lukee yksittäisen ennusterivin raakakentät ja muuntaa ne turvallisesti perus­tyyppeihin.
    """
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

    return temp, pop, wmo, ccov, is_day_flag


def _build_point(
    target_time: datetime,
    offset: int,
    temp: float | None,
    pop: int | None,
    wmo: int | None,
    ccov: int | None,
    is_day_flag: bool | None,
) -> dict[str, Any]:
    """
    Rakentaa dashboardin käyttämän piste-dictin yhden tunnin datasta.
    """
    # fallback: päätellään päivä/yö kellonajasta jos api ei kerro
    is_day = is_day_flag if is_day_flag is not None else (6 <= target_time.hour <= 20)

    return {
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


def _compute_day_minmax(
    temps: list[Any],
    time_axis: list[datetime],
    target_date: date,
) -> tuple[Any | None, Any | None]:
    """
    Laskee annetun päivän min/max-lämpötilan.
    Pidetään logiikka erillisenä, jotta _map_hourly_to_dashboard pysyy ohuena.
    """
    indices: list[int] = []
    for i, ts in enumerate(time_axis):
        if ts.date() == target_date:
            indices.append(i)

    values: list[Any] = []
    for i in indices:
        if i < len(temps):
            values.append(temps[i])

    if not values:
        return None, None

    return min(values), max(values)


def _map_hourly_to_dashboard(
    hourly: dict[str, Any],
    now: datetime,
    offsets: tuple[int, ...],
    tz_name: str,
) -> dict[str, Any]:
    """
    Muuntaa Open-Meteon hourly-datan dashboardin käyttämään muotoon.

    Vastuu on nyt:
      * rakentaa aika-akseli ja hakemisto (_build_time_axis, _build_time_index)
      * käydä läpi pyydetyt offsetit
      * koota pisteet _extract_point_fields- ja _build_point-apufunktioilla
      * pyytää päivän min/max-lämpötilat _compute_day_minmax-apufunktiolta
    """
    temps: list[Any] = hourly.get("temperature_2m", []) or []
    pops: list[Any] = hourly.get("precipitation_probability", []) or []
    wmos: list[Any] = hourly.get("weathercode", []) or []
    covers: list[Any] = hourly.get("cloudcover", []) or []
    isday: list[Any] = hourly.get("is_day", []) or []

    time_axis: list[datetime] = _build_time_axis(hourly, tz_name)
    time_index = _build_time_index(time_axis)

    points: list[dict[str, Any]] = []

    for offset in offsets:
        target_time = now + timedelta(hours=offset)
        idx = time_index.get(target_time)

        if idx is None:
            # kyseistä tuntia ei tullut api:sta
            continue

        temp, pop, wmo, ccov, is_day_flag = _extract_point_fields(
            temps=temps,
            pops=pops,
            wmos=wmos,
            covers=covers,
            isday=isday,
            idx=idx,
        )

        point = _build_point(
            target_time=target_time,
            offset=offset,
            temp=temp,
            pop=pop,
            wmo=wmo,
            ccov=ccov,
            is_day_flag=is_day_flag,
        )
        points.append(point)

    min_temp, max_temp = _compute_day_minmax(
        temps=temps,
        time_axis=time_axis,
        target_date=now.date(),
    )

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

    return _map_hourly_to_dashboard(
        hourly=hourly,
        now=now,
        offsets=offsets,
        tz_name=tz_name,
    )
