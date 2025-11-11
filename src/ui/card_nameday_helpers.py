from __future__ import annotations

import base64
import json
from datetime import datetime
from pathlib import Path

from src.paths import asset_path


def get_background_image() -> str:
    """Palauttaa ensimmäisen löytyvän butterfly-bg-kuvan base64-muodossa."""
    for name in ("butterfly-bg.png", "butterfly-bg.webp", "butterfly-bg.jpg"):
        p = asset_path(name)
        if p.exists():
            b64 = base64.b64encode(p.read_bytes()).decode("ascii")
            ext = p.suffix.lstrip(".").lower()
            mime = {"png": "image/png", "webp": "image/webp", "jpg": "image/jpeg"}[ext]
            return f"data:{mime};base64,{b64}"
    return ""


def find_pyhat_file() -> Path | None:
    """Etsii data/pyhat_fi.json tiedoston ylöspäin hakemistorakenteesta."""
    cwd = Path.cwd().resolve()
    for parent in (cwd, *cwd.parents):
        cand = parent / "data" / "pyhat_fi.json"
        if cand.exists():
            return cand
    here = Path(__file__).resolve()
    for parent in (here.parent, *here.parents):
        cand = parent / "data" / "pyhat_fi.json"
        if cand.exists():
            return cand
    return None


def get_flag_info(today: datetime) -> tuple[str | None, str | None]:
    """Palauttaa (liputuspäivän nimi, debug-viesti)."""
    key = today.strftime("%Y-%m-%d")
    path = find_pyhat_file()
    if path is None:
        return None, "data/pyhat_fi.json ei löytynyt mistään yläkansiosta"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        return None, f"pyhat_fi.json löytyi ({path}), mutta sitä ei voitu lukea: {e}"
    info = data.get(key)
    if info and info.get("flag"):
        return info.get("name") or "Liputuspäivä", None
    some_keys = ", ".join(list(data.keys())[:8])
    return None, f"Avainta {key} ei ollut. Avaimet: {some_keys}"
