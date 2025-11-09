from __future__ import annotations
from src.heos_client import HeosClient
from src.config import HEOS_HOST, HEOS_USERNAME, HEOS_PASSWORD
import sys
from pathlib import Path

# lisää projektin juurikansio polulle
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> None:
    client = HeosClient(
        HEOS_HOST,
        username=HEOS_USERNAME,
        password=HEOS_PASSWORD,
    )
    client.sign_in()

    # 1) hae musiikkilähteet
    sources = client._get_music_sources()
    tidal_sid = None
    print("== MUSIC SOURCES ==")
    for src in sources:
        print(f"- {src.get('name')} (sid={src.get('sid')})")
        if src.get("name", "").lower() == "tidal":
            tidal_sid = src.get("sid")

    if not tidal_sid:
        print("\nTidal-lähdettä ei löytynyt HEOSista.")
        return

    print(f"\nTidal SID = {tidal_sid}")
    print("\n== TIDAL TOP LEVEL ==")
    top = client._send_cmd(f"browse/browse?sid={tidal_sid}")
    payload = top.get("payload", [])
    for item in payload:
        name = item.get("name")
        itype = item.get("type")
        cid = item.get("container_id")
        print(f"[TOP] name={name!r} type={itype} cid={cid}")

    print(
        "\nValitse tuosta se kansio, jonka sisälle haluat mennä (esim. 'My Playlists'), "
        "niin lisätään sen cid sitten configiin."
    )


if __name__ == "__main__":
    main()
