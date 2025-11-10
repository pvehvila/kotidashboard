# weather_icons.py
import base64
from pathlib import Path

from src.paths import ASSETS, ROOT_DIR  # ← UUSI

SEARCH_DIRS = [
    ASSETS / "foreca",
    ROOT_DIR / "foreca",
]

# CWD ja moduulin oma kansio
SEARCH_DIRS += [
    Path.cwd() / "foreca",
    Path.cwd() / "assets" / "foreca",
    Path(__file__).parent / "foreca",
    Path(__file__).parent / "assets" / "foreca",
]

# Poistetaan duplikaatit säilyttäen järjestys
_seen = set()
SEARCH_DIRS = [p for p in SEARCH_DIRS if not (str(p) in _seen or _seen.add(str(p)))]


def _read_png_as_data_uri(path: Path) -> str:
    b64 = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{b64}"


# Cache: muistetaan löytyneet polut
_ICON_CACHE: dict[str, Path] = {}


def _find_icon_path(key: str) -> Path | None:
    # 1) cache
    p = _ICON_CACHE.get(key)
    if p and p.exists():
        return p
    # 2) etsi useista hakemistoista
    fname = f"{key}.png"
    for root in SEARCH_DIRS:
        p = root / fname
        if p.exists():
            _ICON_CACHE[key] = p
            return p
    # 3) fallback: yö→päivä tai päivä→yö
    alt = ("d" if key.startswith("n") else "n") + key[1:]
    fname_alt = f"{alt}.png"
    for root in SEARCH_DIRS:
        p = root / fname_alt
        if p.exists():
            _ICON_CACHE[key] = p
            return p
    # 4) yleinen d000
    for root in SEARCH_DIRS:
        p = root / "d000.png"
        if p.exists():
            _ICON_CACHE[key] = p
            return p
    return None


def render_foreca_icon(key: str, size: int = 48) -> str:
    """
    key = 'dxxx' tai 'nxxx'. Palauttaa <img>-HTML:n.
    """
    try:
        p = _find_icon_path(key)
        if not p:
            # näytä neutraali placeholder
            return (
                f'<span title="not found: {key}" '
                f'style="display:inline-block;width:{size}px;height:{size}px;'
                f"background:#eee;border-radius:8px;text-align:center;line-height:{size}px;"
                f'color:#888;">?</span>'
            )
        uri = _read_png_as_data_uri(p)
        return (
            f'<img src="{uri}" width="{size}" height="{size}" alt="{key}" '
            f'style="vertical-align:middle;" />'
        )
    except Exception:
        return (
            f'<span style="display:inline-block;width:{size}px;height:{size}px;'
            f"background:#eee;border-radius:8px;text-align:center;line-height:{size}px;"
            f'color:#888;">?</span>'
        )


# WX_SVGS = {
# "clear-day": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="48" height="48" fill="currentColor" stroke="currentColor"><circle cx="12" cy="12" r="5"/><g stroke-width="2"><line x1="12" y1="1" x2="12" y2="4"/><line x1="12" y1="20" x2="12" y2="23"/><line x1="1" y1="12" x2="4" y2="12"/><line x1="20" y1="12" x2="23" y2="12"/><line x1="4.2" y1="4.2" x2="6.3" y2="6.3"/><line x1="17.7" y1="17.7" x2="19.8" y2="19.8"/><line x1="4.2" y1="19.8" x2="6.3" y2="17.7"/><line x1="17.7" y1="6.3" x2="19.8" y2="4.2"/></g></svg>',
# "clear-night": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="48" height="48" fill="currentColor" stroke="currentColor"><path d="M16.5 2a8.5 8.5 0 1 0 5.5 14.7A9.5 9.5 0 0 1 16.5 2z"/></svg>',
# "partly-cloudy-day": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="48" height="48" fill="currentColor" stroke="currentColor"><circle cx="7" cy="7" r="3"/><path d="M5 16h10a3 3 0 0 0 0-6 4 4 0 0 0-7-2 3 3 0 0 0-3 5z"/></svg>',
# "partly-cloudy-night": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="48" height="48" fill="currentColor" stroke="currentColor"><path d="M9 3a5 5 0 1 0 7 7 6 6 0 0 1-7-7z"/><path d="M5 16h10a3 3 0 0 0 0-6 4 4 0 0 0-7-2 3 3 0 0 0-3 5z"/></svg>',
# "cloudy": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="48" height="48" fill="currentColor" stroke="currentColor"><path d="M6 18h11a4 4 0 0 0 0-8 6 6 0 0 0-11-2A4 4 0 0 0 6 18z"/></svg>',
# "rain": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="48" height="48" fill="currentColor" stroke="currentColor"><path d="M6 15h11a4 4 0 0 0 0-8 6 6 0 0 0-11-2A4 4 0 0 0 6 15z"/><path d="M8 19l-1 3M12 19l-1 3M16 19l-1 3" stroke-width="2"/></svg>',
# "rain-showers": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="48" height="48" fill="currentColor" stroke="currentColor"><path d="M6 14h11a4 4 0 0 0 0-8 6 6 0 0 0-11-2A4 4 0 0 0 6 14z"/><path d="M8 17l-1 3M12 17l-1 3M16 17l-1 3" stroke-width="2"/></svg>',
# "snow": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="48" height="48" fill="currentColor" stroke="currentColor"><path d="M6 15h11a4 4 0 0 0 0-8 6 6 0 0 0-11-2A4 4 0 0 0 6 15z"/><path d="M10 18l2 2 2-2-2-2-2 2z"/></svg>',
# "thunderstorm": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="48" height="48" fill="currentColor" stroke="currentColor"><path d="M6 14h11a4 4 0 0 0 0-8 6 6 0 0 0-11-2A4 4 0 0 0 6 14z"/><path d="M11 16l-2 4h3l-1 4 4-6h-3l1-2z"/></svg>',
# "fog": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="48" height="48" fill="currentColor" stroke="currentColor"><path d="M3 10h18M3 13h18M3 16h18" stroke-width="2"/></svg>',
# "freezing-rain": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="48" height="48" fill="currentColor" stroke="currentColor"><path d="M6 15h11a4 4 0 0 0 0-8 6 6 0 0 0-11-2A4 4 0 0 0 6 15z"/><path d="M10 17v3M14 17v3" stroke-width="2"/></svg>',
# "drizzle": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="48" height="48" fill="currentColor" stroke="currentColor"><path d="M6 15h11a4 4 0 0 0 0-8 6 6 0 0 0-11-2A4 4 0 0 0 6 15z"/><path d="M9 18h6" stroke-width="2"/></svg>',
# "na": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="48" height="48" fill="currentColor" stroke="currentColor"><text x="6" y="16">?</text></svg>',
# }
