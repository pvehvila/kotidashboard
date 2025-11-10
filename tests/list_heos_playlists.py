from __future__ import annotations

import sys
from pathlib import Path

from src.config import HEOS_HOST, HEOS_PASSWORD, HEOS_USERNAME
from src.heos_client import HeosClient

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def list_sid(client: HeosClient, sid: int, title: str) -> None:
    print(f"\n== {title} (sid={sid}) ==")
    resp = client._send_cmd(f"browse/browse?sid={sid}")
    payload = resp.get("payload", [])
    if not payload:
        print("  (tyhjä)")
        return
    for item in payload:
        name = item.get("name")
        itype = item.get("type")
        cid = item.get("container_id")
        print(f"- name={name!r} type={itype} cid={cid}")


def main() -> None:
    client = HeosClient(
        HEOS_HOST,
        username=HEOS_USERNAME,
        password=HEOS_PASSWORD,
    )
    client.sign_in()

    # HEOSin oma playlist-palvelu
    list_sid(client, 1025, "HEOS Playlists")

    # HEOS Favorites – joskus Tidal-juttuja on täällä
    list_sid(client, 1028, "HEOS Favorites")


if __name__ == "__main__":
    main()
