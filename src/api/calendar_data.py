# src/api/calendar_data.py
from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from src.config import HOLIDAY_PATHS, NAMEDAY_FILE, NAMEDAY_PATHS


def resolve_nameday_file() -> Path:
    """
    Palauttaa ensimmäisen olemassa olevan nimipäivätiedoston.
    Fallback on NAMEDAY_FILE.
    """
    for raw in NAMEDAY_PATHS:
        try:
            p = Path(raw)
            if p.exists():
                return p
        except Exception:
            continue
    return Path(NAMEDAY_FILE)


def resolve_first_existing(paths: Iterable[str | Path]) -> Path | None:
    """Palauttaa ensimmäisen olemassa olevan polun listasta."""
    for raw in paths:
        p = Path(raw)
        if p.exists():
            return p
    return None


def resolve_holiday_file() -> Path | None:
    """
    Palauttaa ensimmäisen olemassa olevan pyhä-/liputuspäivä -tiedoston
    HOLIDAY_PATHS -listasta.
    """
    return resolve_first_existing(HOLIDAY_PATHS)


def load_json(path: Path) -> Any:
    """Lataa tiedoston JSON-muotoon utf-8:lla."""
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)
