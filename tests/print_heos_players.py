# tests/print_heos_players.py
from __future__ import annotations

import sys
from pathlib import Path

from src.config import (
    HEOS_HOST,
    HEOS_PASSWORD,
    HEOS_USERNAME,
)
from src.heos_client import HeosClient

# lisää projektin juurikansio (C:\HomeDashboard) polulle
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> None:
    client = HeosClient(
        HEOS_HOST,
        username=HEOS_USERNAME,
        password=HEOS_PASSWORD,
    )
    # ei haittaa jos on jo kirjautuneena
    client.sign_in()
    players = client.get_players()
    if not players:
        print("Ei yhtään HEOS-soitinta löytynyt.")
    for p in players:
        print(
            f"pid={p.get('pid')} "
            f"name={p.get('name')} "
            f"model={p.get('model')} "
            f"ip={p.get('ip')}"
        )


if __name__ == "__main__":
    main()
