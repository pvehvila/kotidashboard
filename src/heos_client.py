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
        with socket.create_connection((self.host, self.port), self.timeout) as s:
            s.sendall(f"heos://{cmd}\r\n".encode())
            s.settimeout(self.timeout)
            data = s.recv(65535).decode("utf-8", errors="replace")

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
        self._send_cmd(f"player/set_mute?pid={pid}&state={state}")

    def set_play_state(self, pid: int, state: str) -> dict[str, Any]:
        return self._send_cmd(f"player/set_play_state?pid={pid}&state={state}")

    def play_next(self, pid: int) -> dict[str, Any]:
        return self._send_cmd(f"player/play_next?pid={pid}")

    def play_previous(self, pid: int) -> dict[str, Any]:
        return self._send_cmd(f"player/play_previous?pid={pid}")

    def play_pause(self, pid: int) -> dict[str, Any]:
        """
        Toglaa play/pause nykyisen toistotilan perusteella.

        Wake-safe:
        - Jos now_playing ei anna tilaa luotettavasti (tyhjä/unknown), lähetetään ensin 'play'
          (tämä herättää Denonin standby-tilasta).
        - Jos tila kertoo selvästi että soi, lähetetään 'pause'.
        """
        now = self.get_now_playing(pid)
        payload = now.get("payload") or {}
        raw_state = (payload.get("state") or now.get("state") or "").strip().lower()

        playing_states = {"play", "playing"}
        paused_states = {"pause", "paused", "stop", "stopped"}

        if raw_state in playing_states:
            return self.set_play_state(pid, "pause")

        if raw_state in paused_states:
            # Jos on selvästi pausella/stopissa, käynnistetään toisto
            return self.set_play_state(pid, "play")

        # Tuntematon/tyhjä tila (tyypillinen standby-herätyksessä): herätä aina playllä
        resp = self.set_play_state(pid, "play")

        # Pieni viive auttaa, että seuraava painallus saa jo järkevän state/payloadin
        time.sleep(0.25)
        return resp

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

        self._send_cmd(
            f"browse/add_to_queue?pid={pid}&sid={sid}&cid={urllib.parse.quote(cid)}&aid=4"
        )
        time.sleep(0.2)
