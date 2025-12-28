from __future__ import annotations

import json
import socket
import time
import urllib.parse
from typing import Any

DEFAULT_PORT = 1255


class HeosClient:
    """Yksinkertainen HEOS-CLI asiakas Denon/Marantz -laitteille."""

    def __init__(
        self,
        host: str,
        port: int = DEFAULT_PORT,
        username: str | None = None,
        password: str | None = None,
        timeout: float = 3.0,
    ) -> None:
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.timeout = timeout

    # --- perus I/O ---

    def _send_cmd(self, cmd: str) -> dict[str, Any]:
        # Avataan lyhyt telnet-tyylinen yhteys jokaiselle komennolle.
        with socket.create_connection((self.host, self.port), self.timeout) as s:
            s.sendall(f"heos://{cmd}\r\n".encode())
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

    def get_players(self) -> list[dict[str, Any]]:
        resp = self._send_cmd("player/get_players")
        return resp.get("payload", [])

    def get_now_playing(self, pid: int) -> dict[str, Any]:
        return self._send_cmd(f"player/get_now_playing_media?pid={pid}")

    def get_volume(self, pid: int) -> int:
        resp = self._send_cmd(f"player/get_volume?pid={pid}")
        return int(resp.get("payload", {}).get("level", 0))

    def set_volume(self, pid: int, level: int) -> None:
        self._send_cmd(f"player/set_volume?pid={pid}&level={level}")

    def set_mute(self, pid: int, state: str) -> None:
        # state: on/off/toggle
        self._send_cmd(f"player/set_mute?pid={pid}&state={state}")

    # --- Play state (robust play/pause) ---

    def get_play_state(self, pid: int) -> dict[str, Any]:
        return self._send_cmd(f"player/get_play_state?pid={pid}")

    def set_play_state(self, pid: int, state: str) -> dict[str, Any]:
        state = state.strip().lower()
        return self._send_cmd(f"player/set_play_state?pid={pid}&state={state}")

    def _extract_state(self, resp: dict[str, Any]) -> str | None:
        payload = resp.get("payload")
        if isinstance(payload, dict):
            state = payload.get("state")
            if state:
                return str(state).strip().lower()

        heos = resp.get("heos")
        if isinstance(heos, dict):
            msg = heos.get("message")
            # esim: "pid=1&state=play"
            if isinstance(msg, str) and "state=" in msg:
                for part in msg.split("&"):
                    if part.startswith("state="):
                        return part.split("=", 1)[1].strip("'\" ").lower()

        return None

    def _ensure_state(self, pid: int, target: str) -> tuple[dict[str, Any], str | None]:
        """
        Yritä asettaa tila ja varmistaa tila tarkistamalla uudelleen.
        Palauttaa (viimeisin_responssi, luettu_state).
        """
        target = target.strip().lower()

        # 1) ensisijainen yritys: set_play_state
        resp = self.set_play_state(pid, target)

        # pieni viive, jotta HEOS ehtii päivittää tilan
        time.sleep(0.15)

        st_resp = self.get_play_state(pid)
        st = self._extract_state(st_resp)

        # jos tavoite saavutettu, palauta
        if st == target:
            return resp, st

        return resp, st

    def pause(self, pid: int) -> dict[str, Any]:
        resp, _ = self._ensure_state(pid, "pause")
        return resp

    def play(self, pid: int) -> dict[str, Any]:
        """
        Käynnistä toisto luotettavasti myös STOP-tilasta:
        - pause -> set_play_state(play)
        - stop  -> play_queue_item(qid) jos qid löytyy now_playingistä
        """
        st = self._extract_state(self.get_play_state(pid))

        # jos paused, tavallinen play riittää
        if st == "pause":
            return self.set_play_state(pid, "play")

        # jos stop, käynnistä nykyinen queue-item (qid)
        if st == "stop" or st is None:
            # jos qid puuttuu, viimeinen fallback: play_next (jos queue on olemassa)
            return self.play_next(pid)

        # jos jo play, palautetaan pelkkä state-komento
        return {"heos": {"command": "noop", "result": "success", "message": "already playing"}}

    def play_pause(self, pid: int) -> dict[str, Any]:
        st_resp = self.get_play_state(pid)
        st = self._extract_state(st_resp)

        if st == "play":
            return self.set_play_state(pid, "pause")

        # pause/stop/None -> play
        return self.set_play_state(pid, "play")

    def play_next(self, pid: int) -> dict[str, Any]:
        return self._send_cmd(f"player/play_next?pid={pid}")

    def play_previous(self, pid: int) -> dict[str, Any]:
        return self._send_cmd(f"player/play_previous?pid={pid}")

    # --- Tidal-selaus ---

    def _get_music_sources(self) -> list[dict[str, Any]]:
        resp = self._send_cmd("browse/get_music_sources")
        return resp.get("payload", [])

    def _get_tidal_sid(self) -> int | None:
        for src in self._get_music_sources():
            if src.get("name", "").lower() == "tidal":
                return int(src["sid"])
        return None

    def search_tidal_by_name(self, name: str) -> dict[str, Any] | None:
        """Etsii Tidalista playlistin nimellä ja palauttaa ekana osuneen kontainerin."""
        sid = self._get_tidal_sid()
        if not sid:
            return None

        q = urllib.parse.quote(name)
        resp = self._send_cmd(f"browse/search?sid={sid}&search={q}")
        items = resp.get("payload", [])

        for item in items:
            if item.get("type") in ("playlist", "container", "album"):
                return {"sid": sid, **item}
        return None

    def play_tidal_container(self, pid: int, container: dict[str, Any]) -> None:
        sid = container["sid"]
        cid = container["container_id"]
        # aid=4 => replace and play
        self._send_cmd(
            f"browse/add_to_queue?pid={pid}&sid={sid}&cid={urllib.parse.quote(cid)}&aid=4"
        )
        time.sleep(0.2)

    def search_heos_playlist_by_name(self, name: str) -> dict[str, Any] | None:
        # HEOSin oma Playlists-palvelu on yleensä sid=1025
        resp = self._send_cmd("browse/browse?sid=1025")
        for item in resp.get("payload", []):
            if item.get("name", "").lower() == name.lower():
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

        candidates = [
            "my_music",
            "my_collection",
            "playlists",
            "favorites",
        ]
        for cid in candidates:
            resp = self._send_cmd(f"browse/add_to_queue?pid={pid}&sid={sid}&cid={cid}&aid=4")
            if resp.get("heos", {}).get("result") == "success":
                return True
        return False
