from __future__ import annotations

import json
import re
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import requests

from src.config import HTTP_TIMEOUT_S, POLLEN_CACHE_FILE, POLLEN_CACHE_TTL_S

POLLEN_SOURCE_URL = "https://siirto.siitepoly.fi/media/sptied.txt"
POLLEN_SOURCE_NAME = "Turun yliopiston siitepölytiedotus"

PLANTS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("koivu", ("koivu", "koivun", "koivua")),
    ("heinät", ("heinä", "heinät", "heinien", "heinää", "heinäpöly")),
    ("pujo", ("pujo", "pujon", "pujoa")),
)

LEVELS = ("ei havaittu", "vähän", "kohtalaisesti", "runsaasti")

_FORECAST_RE = re.compile(
    r"\b(ennuste|ennustetaan|odotetaan|lähipäiv|jatkuu|voimistuu|runsastuu|"
    r"vähenee|alkaa|leviää|kulkeutuu|kulkeutua|tulevina)\b",
    re.IGNORECASE,
)
_REGION_RE = re.compile(
    r"\b(riihimä\w*|häme\w*|kanta-häme\w*|uusimaa|uudellama\w*|etelä-suom\w*|"
    r"eteläisessä suomessa|"
    r"maan eteläos\w*|etelärannik\w*|suomen eteläos\w*)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class PollenPlant:
    key: str
    name: str
    level: str
    forecast_level: str
    forecast: str


@dataclass(frozen=True)
class PollenView:
    location: str
    source: str
    updated: str | None
    plants: list[PollenPlant]
    summary: str


def fetch_pollen_view() -> dict[str, Any]:
    text = _fetch_pollen_text()
    view = parse_pollen_text(text)
    return {
        "location": view.location,
        "source": view.source,
        "updated": view.updated,
        "plants": [asdict(plant) for plant in view.plants],
        "summary": view.summary,
    }


def parse_pollen_text(text: str) -> PollenView:
    normalized = _normalize_text(text)
    current_text, forecast_text = _extract_text_sections(normalized)
    current_sentences = _section_sentences(current_text or normalized)
    forecast_sentences = _section_sentences(forecast_text or normalized)
    current_map = _station_levels(normalized, "TILANNE", "Helsinki")
    forecast_map = _station_levels(normalized, "ENNUSTE", "Helsinki")

    plants = [
        _build_plant(
            key,
            _display_name(key),
            aliases,
            current_sentences,
            forecast_sentences,
            current_map,
            forecast_map,
        )
        for key, aliases in PLANTS
    ]

    return PollenView(
        location="Riihimäki",
        source=POLLEN_SOURCE_NAME,
        updated=_extract_updated(normalized),
        plants=plants,
        summary=_build_summary(plants),
    )


def _fetch_pollen_text() -> str:
    cached = _read_cache(POLLEN_CACHE_FILE)
    now = time.time()
    if cached and now - float(cached.get("fetched_at", 0)) < POLLEN_CACHE_TTL_S:
        text = str(cached.get("text", ""))
        if text:
            return text

    headers = {"User-Agent": "HomeDashboard/1.0"}
    resp = requests.get(POLLEN_SOURCE_URL, timeout=HTTP_TIMEOUT_S, headers=headers)
    resp.raise_for_status()
    text = resp.content.decode("utf-8-sig", errors="replace")
    _write_cache(POLLEN_CACHE_FILE, {"fetched_at": now, "text": text})
    return text


def _read_cache(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _write_cache(path: Path, payload: dict[str, Any]) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    except OSError:
        return


def _normalize_text(text: str) -> str:
    clean = text.replace("\ufeff", "").replace("\r\n", "\n").replace("\r", "\n")
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in clean.splitlines()]
    return "\n".join(line for line in lines if line).strip()


def _split_sentences(text: str) -> list[str]:
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+", text) if part.strip()]


def _relevant_sentences(sentences: list[str]) -> list[str]:
    return [sentence for sentence in sentences if _REGION_RE.search(sentence)]


def _extract_text_sections(text: str) -> tuple[str, str]:
    _, _, body = text.partition("(TEKSTIT)")
    source = body or text

    current_match = re.search(
        r"\bTILANNE\b(?P<section>.*?)(?=\bENNUSTE\b)",
        source,
        flags=re.IGNORECASE | re.DOTALL,
    )
    forecast_match = re.search(
        r"\bENNUSTE\b(?P<section>.*?)(?=\(END\)|©|\Z)",
        source,
        flags=re.IGNORECASE | re.DOTALL,
    )

    current = current_match.group("section").strip() if current_match else ""
    forecast = forecast_match.group("section").strip() if forecast_match else ""
    return current, forecast


def _section_sentences(section: str) -> list[str]:
    sentences = _split_sentences(section)
    relevant = _relevant_sentences(sentences)
    return relevant or sentences


def _station_levels(text: str, heading: str, station: str) -> dict[str, str]:
    section = _map_section(text, heading)
    if not section:
        return {}

    station_re = re.compile(rf"^{re.escape(station)}\s+(?P<codes>[A-ZÅÄÖ,\s]+)$", re.IGNORECASE)
    for raw_line in section.splitlines():
        line = raw_line.strip()
        match = station_re.match(line)
        if not match:
            continue
        return _levels_from_codes(match.group("codes"))
    return {}


def _map_section(text: str, heading: str) -> str:
    pattern = rf"\b{re.escape(heading)}\b\s+\d{{1,2}}\.\d{{1,2}}\.\d{{4}}(?:\s+-\s+\d{{1,2}}\.\d{{1,2}}\.\d{{4}})?(?P<section>.*?)(?=\b(?:TILANNE|ENNUSTE)\b|\bTunnukset\b|\(TEKSTIT\)|\Z)"
    match = re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)
    if match:
        return match.group("section")
    return ""


def _levels_from_codes(codes: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for match in re.finditer(r"([LCKHPT])\1{0,2}", codes.upper()):
        code = match.group(0)
        key = _plant_key_for_code(code[0])
        if key:
            result[key] = _level_from_code(code)
    return result


def _plant_key_for_code(code: str) -> str | None:
    return {
        "K": "koivu",
        "H": "heinät",
        "P": "pujo",
    }.get(code)


def _level_from_code(code: str) -> str:
    length = len(code)
    if length >= 3:
        return "runsaasti"
    if length == 2:
        return "kohtalaisesti"
    return "vähän"


def _display_name(key: str) -> str:
    if key == "koivu":
        return "Koivu"
    if key == "heinät":
        return "Heinät"
    return "Pujo"


def _build_plant(
    key: str,
    name: str,
    aliases: tuple[str, ...],
    current_sentences: list[str],
    forecast_sentences: list[str],
    current_map: dict[str, str],
    forecast_map: dict[str, str],
) -> PollenPlant:
    current_plant_sentences = [
        sentence for sentence in current_sentences if _has_any(sentence, aliases)
    ]
    forecast_plant_sentences = [
        sentence for sentence in forecast_sentences if _has_any(sentence, aliases)
    ]
    current_sentence = _first_current_sentence(current_plant_sentences)
    forecast_sentence = _first_forecast_sentence(forecast_plant_sentences)

    level = current_map.get(key) or _level_from_sentence(current_sentence)
    forecast_level = forecast_map.get(key) or _level_from_sentence(forecast_sentence)
    forecast = forecast_sentence or "Ei erillistä ennustetta Riihimäen alueelle."

    return PollenPlant(
        key=key,
        name=name,
        level=level,
        forecast_level=forecast_level,
        forecast=forecast,
    )


def _has_any(sentence: str, words: tuple[str, ...]) -> bool:
    lower = sentence.lower()
    return any(word in lower for word in words)


def _first_current_sentence(sentences: list[str]) -> str:
    for sentence in sentences:
        if not _FORECAST_RE.search(sentence):
            return sentence
    return sentences[0] if sentences else ""


def _first_forecast_sentence(sentences: list[str]) -> str:
    return sentences[0] if sentences else ""


def _level_from_sentence(sentence: str) -> str:
    lower = sentence.lower()
    if not lower:
        return "ei havaittu"
    if re.search(r"\b(ei|eivät)\b.*\b(esiinny|havaittu|ole|ilmassa)\b", lower):
        return "ei havaittu"
    if "runsa" in lower or "erittäin" in lower:
        return "runsaasti"
    if "kohtal" in lower:
        return "kohtalaisesti"
    if any(token in lower for token in ("vähä", "vähän", "matala", "pieni", "pieninä")):
        return "vähän"
    return "ei havaittu"


def _extract_updated(text: str) -> str | None:
    match = re.search(r"\b(\d{1,2}\.\d{1,2}\.\d{4})\b", text)
    if match:
        return match.group(1)
    return None


def _build_summary(plants: list[PollenPlant]) -> str:
    active = [plant.name for plant in plants if plant.level in LEVELS[1:]]
    if not active:
        return "Ei koivun, heinien tai pujon siitepölyä lähialueen tiedotteessa."
    return "Ilmassa: " + ", ".join(active)
