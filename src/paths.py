"""
paths.py – keskitetyt polut Kotidashboardille.

Tämän ideana on, että voit aina kirjoittaa:
    from src.paths import ASSETS, DATA, root_path, asset_path

…ja saat oikean polun riippumatta siitä, kutsutaanko sovellusta
projektin juuresta (streamlit run main.py) vai jostain muualta.
"""

from __future__ import annotations
from pathlib import Path

# 1) Selvitetään tiedoston sijainti
_THIS_FILE = Path(__file__).resolve()

# 2) Projektin juurihakemisto
#    src/paths.py -> src -> projektin juuri (= src:n parent)
ROOT_DIR = _THIS_FILE.parent.parent

# 3) Yleisimmät kansiot
SRC = ROOT_DIR / "src"
ASSETS = ROOT_DIR / "assets"
DATA = ROOT_DIR / "data"
DOCS = ROOT_DIR / "docs"
LOGS = ROOT_DIR / "logs"


def root_path(*parts: str) -> Path:
    """Palauttaa polun projektin juureen suhteessa."""
    return ROOT_DIR.joinpath(*parts)


def asset_path(*parts: str) -> Path:
    """Palauttaa polun assets-kansioon."""
    return ASSETS.joinpath(*parts)


def data_path(*parts: str) -> Path:
    """Palauttaa polun data-kansioon."""
    return DATA.joinpath(*parts)


def ensure_dirs() -> None:
    """Varmistaa, että tietyt hakemistot ovat olemassa (esim. logs/)."""
    LOGS.mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    # Pikku testi kehittäjälle
    print("ROOT_DIR:", ROOT_DIR)
    print("ASSETS:", ASSETS)
    print("DATA:", DATA)
    print("DOCS:", DOCS)
    print("LOGS:", LOGS)
