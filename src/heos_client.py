# src/heos_client.py
from __future__ import annotations

import json
import socket
import time
import urllib.parse
from typing import Any, Dict, Optional, List


DEFAULT_PORT = 1255


class HeosClient:
    """Yksinkertainen HEOS-CLI asiakas Denon/Marantz -laitteille."""

    def __init__(
        self,
        host: str,
        port: int = DEFAULT_PORT,
        username: Optional[str] = None,
        password: Optional[str] = None,
        timeout: float = 3.0,
    ) -> None:
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.timeout = timeout

    # --- perus I/O ---

    def _send_cmd(self, cmd: str) -> Dict[str, Any]:
        # avataan lyhyt telnet-tyylinen yhteys jokaiselle komennolle,
        # streamlit-ympäristöön tämä on helpoin
        with socket.create_connection((self.host, self.port), self.timeout) as s:
            s.sendall(f"heos://{cmd}\r\n".encode("utf-8"))
            s.settimeout(self.timeout)
            data = s.recv(65535).decode("utf-8", errors="replace")

        # HEOS voi joskus lähettää useamman JSON-rivin, otetaan eka kunnollinen
        for line in data.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                return json.loads(line)
            except json.JSONDecodeError:
                continue
        return {}

    # --- yleiset ---

    def register_for_events(self) -> None:
        self._send_cmd("system/register_for_change_events?enable=on")

    def sign_in(self) -> None:
        if self.username and self.password:
            q = f"un={urllib.parse.quote(self.username)}&pw={urllib.parse.quote(self.password)}"
            self._send_cmd(f"system/sign_in?{q}")

    # --- Soittimet ---

    def get_players(self) -> List[Dict[str, Any]]:
        resp = self._send_cmd("player/get_players")
        return resp.get("payload", [])

    def get_now_playing(self, pid: int) -> Dict[str, Any]:
        return self._send_cmd(f"player/get_now_playing_media?pid={pid}")
    
    def get_volume(self, pid: int) -> int:
        resp = self._send_cmd(f"player/get_volume?pid={pid}")
        return int(resp.get("payload", {}).get("level", 0))

    def set_volume(self, pid: int, level: int) -> None:
        self._send_cmd(f"player/set_volume?pid={pid}&level={level}")

    def set_mute(self, pid: int, state: str) -> None:
        # state: on/off/toggle
        self._send_cmd(f"player/set_mute?pid={pid}&state={state}")


    def set_play_state(self, pid: int, state: str) -> dict:
        return self._send_cmd(f"player/set_play_state?pid={pid}&state={state}")

    def play_next(self, pid: int) -> dict:
        return self._send_cmd(f"player/play_next?pid={pid}")

    def play_previous(self, pid: int) -> dict:
        return self._send_cmd(f"player/play_previous?pid={pid}")

    # --- Tidal-selaus ---

    def _get_music_sources(self) -> List[Dict[str, Any]]:
        resp = self._send_cmd("browse/get_music_sources")
        return resp.get("payload", [])

    def _get_tidal_sid(self) -> Optional[int]:
        for src in self._get_music_sources():
            if src.get("name", "").lower() == "tidal":
                return int(src["sid"])
        return None

    def search_tidal_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Etsii Tidalista playlistin nimellä ja palauttaa ekana osuneen kontainerin."""
        sid = self._get_tidal_sid()
        if not sid:
            return None
        # HEOS: browse/search?sid=10&search=<text>&scid=1 ...
        q = urllib.parse.quote(name)
        resp = self._send_cmd(f"browse/search?sid={sid}&search={q}")
        items = resp.get("payload", [])
        # payloadissa voi olla eri tyyppejä, otetaan eka jossa on container_id
        for item in items:
            # playlist on yleensä "container"
            if item.get("type") in ("playlist", "container", "album"):
                return {"sid": sid, **item}
        return None

    def play_tidal_container(self, pid: int, container: Dict[str, Any]) -> None:
        sid = container["sid"]
        cid = container["container_id"]
        # aid=4 => replace and play
        self._send_cmd(
            f"browse/add_to_queue?pid={pid}&sid={sid}&cid={urllib.parse.quote(cid)}&aid=4"
        )
        # antaa hetkisen että soitto alkaa
        time.sleep(0.2)

    def search_heos_playlist_by_name(self, name: str) -> dict | None:
        # HEOSin oma Playlists-palvelu on yleensä sid=1025
        resp = self._send_cmd("browse/browse?sid=1025")
        for item in resp.get("payload", []):
            if item.get("name", "").lower() == name.lower():
                # tässä on nyt container_id
                item["sid"] = 1025
                return item
        return None

    def play_tidal_known_container(self, pid: int) -> bool:
        """
        Yrittää muutamaa yleistä Tidal-kontaineria HEOSin kautta.
        Palauttaa True jos jokin onnistui.
        """
        sid = self._get_tidal_sid()
        if not sid:
            return False

        # tunnettuja "virtuaalikansioita", joita kaikki laitteet eivät paljasta
        candidates = [
            "my_music",
            "my_collection",
            "playlists",
            "favorites",
        ]
        for cid in candidates:
            resp = self._send_cmd(
                f"browse/add_to_queue?pid={pid}&sid={sid}&cid={cid}&aid=4"
            )
            if resp.get("heos", {}).get("result") == "success":
                return True
        return False
