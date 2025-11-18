# tests/test_heos_client.py

import json
from typing import Any

import pytest

from src.heos_client import HeosClient


class FakeSocket:
    """Yksinkertainen feikki-socket, jota _send_cmd käyttää."""

    def __init__(self, data: str) -> None:
        self._data = data
        self.sent: list[bytes] = []
        self.timeouts: list[float] = []

    def sendall(self, data: bytes) -> None:
        self.sent.append(data)

    def settimeout(self, timeout: float) -> None:
        self.timeouts.append(timeout)

    def recv(self, bufsize: int) -> bytes:  # pragma: no cover - ei haaraeroja testissä
        return self._data.encode("utf-8")

    def __enter__(self) -> "FakeSocket":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # pragma: no cover - ei logiikkaa
        pass


def _patch_socket(monkeypatch: pytest.MonkeyPatch, data: str, sock_holder: dict[str, Any]) -> None:
    """Apu: korvaa socket.create_connection ja palauttaa FakeSocketin."""

    def fake_create_connection(address, timeout=None):
        sock = FakeSocket(data)
        sock_holder["sock"] = sock
        return sock

    monkeypatch.setattr("src.heos_client.socket.create_connection", fake_create_connection)


# --- _send_cmd ---


def test_send_cmd_sends_heos_prefix_and_parses_first_valid_json(monkeypatch):
    # ensimmäinen JSON-kelpoinen rivi otetaan, muut ohitetaan
    payload = {"heos": {"result": "success"}, "payload": [{"foo": "bar"}]}
    raw_data = "\nnot-json\n" + json.dumps(payload) + "\n" + json.dumps({"ignored": True})

    holder: dict[str, Any] = {}
    _patch_socket(monkeypatch, raw_data, holder)

    client = HeosClient(host="example.local")
    result = client._send_cmd("player/get_players")  # noqa: SLF001

    # palauttaa oikean JSON-rivin
    assert result == payload

    # lähetetty komento on oikeassa muodossa
    sent = holder["sock"].sent[0].decode("utf-8")
    assert sent == "heos://player/get_players\r\n"


def test_send_cmd_returns_empty_dict_when_no_valid_json(monkeypatch):
    raw_data = "not-json\nstill-not-json\n"
    holder: dict[str, Any] = {}
    _patch_socket(monkeypatch, raw_data, holder)

    client = HeosClient(host="example.local")
    result = client._send_cmd("system/ping")  # noqa: SLF001

    assert result == {}


# --- yleiset komennot ---


def test_register_for_events_uses_correct_command(monkeypatch):
    called = {}

    def fake_send(cmd: str):
        called["cmd"] = cmd
        return {}

    client = HeosClient(host="example.local")
    monkeypatch.setattr(client, "_send_cmd", fake_send)  # noqa: SLF001

    client.register_for_events()
    assert called["cmd"] == "system/register_for_change_events?enable=on"


def test_sign_in_calls_send_cmd_when_credentials_present(monkeypatch):
    called = {}

    def fake_send(cmd: str):
        called["cmd"] = cmd
        return {}

    client = HeosClient(
        host="example.local",
        username="user@example.com",
        password="päss word",
    )
    monkeypatch.setattr(client, "_send_cmd", fake_send)  # noqa: SLF001

    client.sign_in()
    # tarkistetaan että käyttäjä ja salasana on URL-koodattu
    assert called["cmd"].startswith("system/sign_in?")
    assert "un=user%40example.com" in called["cmd"]
    assert "pw=p%C3%A4ss%20word" in called["cmd"]


def test_sign_in_does_nothing_without_credentials(monkeypatch):
    def fake_send(cmd: str):  # pragma: no cover - ei pitäisi koskaan kutsua
        raise AssertionError("Should not be called")

    client = HeosClient(host="example.local")
    monkeypatch.setattr(client, "_send_cmd", fake_send)  # noqa: SLF001

    # ei pitäisi herättää poikkeusta
    client.sign_in()


# --- Soittimet ---


def test_get_players_returns_payload(monkeypatch):
    def fake_send(cmd: str):
        assert cmd == "player/get_players"
        return {"payload": [{"pid": 1}, {"pid": 2}]}

    client = HeosClient(host="example.local")
    monkeypatch.setattr(client, "_send_cmd", fake_send)  # noqa: SLF001

    players = client.get_players()
    assert players == [{"pid": 1}, {"pid": 2}]


def test_get_now_playing_delegates_to_send_cmd(monkeypatch):
    def fake_send(cmd: str):
        assert cmd == "player/get_now_playing_media?pid=123"
        return {"payload": {"something": "value"}}

    client = HeosClient(host="example.local")
    monkeypatch.setattr(client, "_send_cmd", fake_send)  # noqa: SLF001

    now = client.get_now_playing(123)
    assert now == {"payload": {"something": "value"}}


def test_get_volume_parses_int_from_payload(monkeypatch):
    def fake_send(cmd: str):
        assert cmd == "player/get_volume?pid=5"
        return {"payload": {"level": "15"}}

    client = HeosClient(host="example.local")
    monkeypatch.setattr(client, "_send_cmd", fake_send)  # noqa: SLF001

    vol = client.get_volume(5)
    assert vol == 15


def test_set_volume_sends_correct_command(monkeypatch):
    called = {}

    def fake_send(cmd: str):
        called["cmd"] = cmd
        return {}

    client = HeosClient(host="example.local")
    monkeypatch.setattr(client, "_send_cmd", fake_send)  # noqa: SLF001

    client.set_volume(pid=7, level=33)
    assert called["cmd"] == "player/set_volume?pid=7&level=33"


def test_set_mute_sends_correct_command(monkeypatch):
    called = {}

    def fake_send(cmd: str):
        called["cmd"] = cmd
        return {}

    client = HeosClient(host="example.local")
    monkeypatch.setattr(client, "_send_cmd", fake_send)  # noqa: SLF001

    client.set_mute(pid=7, state="toggle")
    assert called["cmd"] == "player/set_mute?pid=7&state=toggle"


def test_play_state_and_next_previous_return_response(monkeypatch):
    def fake_send(cmd: str):
        return {"heos": {"result": cmd}}

    client = HeosClient(host="example.local")
    monkeypatch.setattr(client, "_send_cmd", fake_send)  # noqa: SLF001

    assert (
        client.set_play_state(1, "play")["heos"]["result"]
        == "player/set_play_state?pid=1&state=play"
    )
    assert client.play_next(1)["heos"]["result"] == "player/play_next?pid=1"
    assert client.play_previous(1)["heos"]["result"] == "player/play_previous?pid=1"


# --- Tidal-selaus ja playlistit ---


def test_get_tidal_sid_finds_tidal_case_insensitive(monkeypatch):
    def fake_send(cmd: str):
        assert cmd == "browse/get_music_sources"
        return {
            "payload": [
                {"name": "Spotify", "sid": 1},
                {"name": "TIDAL", "sid": 10},
            ]
        }

    client = HeosClient(host="example.local")
    monkeypatch.setattr(client, "_send_cmd", fake_send)  # noqa: SLF001

    sid = client._get_tidal_sid()  # noqa: SLF001
    assert sid == 10


def test_get_tidal_sid_returns_none_if_not_found(monkeypatch):
    def fake_send(cmd: str):
        return {"payload": [{"name": "Spotify", "sid": 1}]}

    client = HeosClient(host="example.local")
    monkeypatch.setattr(client, "_send_cmd", fake_send)  # noqa: SLF001

    sid = client._get_tidal_sid()  # noqa: SLF001
    assert sid is None


def test_search_tidal_by_name_builds_correct_command_and_picks_playlist(monkeypatch):
    def fake_get_sid():
        return 10

    def fake_send(cmd: str):
        # varmista että hakusana on URL-koodattu
        assert cmd.startswith("browse/search?sid=10&search=my%20list")
        return {
            "payload": [
                {"type": "track", "title": "foo"},
                {"type": "playlist", "name": "My List", "container_id": "abc123"},
            ]
        }

    client = HeosClient(host="example.local")
    monkeypatch.setattr(client, "_get_tidal_sid", fake_get_sid)  # noqa: SLF001
    monkeypatch.setattr(client, "_send_cmd", fake_send)  # noqa: SLF001

    container = client.search_tidal_by_name("my list")
    assert container is not None
    assert container["sid"] == 10
    assert container["container_id"] == "abc123"
    assert container["type"] == "playlist"


def test_search_tidal_by_name_returns_none_if_no_sid(monkeypatch):
    def fake_get_sid():
        return None

    def fake_send(cmd: str):  # pragma: no cover - ei pitäisi kutsua
        raise AssertionError("Should not be called")

    client = HeosClient(host="example.local")
    monkeypatch.setattr(client, "_get_tidal_sid", fake_get_sid)  # noqa: SLF001
    monkeypatch.setattr(client, "_send_cmd", fake_send)  # noqa: SLF001

    assert client.search_tidal_by_name("anything") is None


def test_play_tidal_container_sends_add_to_queue_and_waits(monkeypatch):
    called = {}

    def fake_send(cmd: str):
        called["cmd"] = cmd
        return {}

    def fake_sleep(seconds: float):
        called["sleep"] = seconds

    client = HeosClient(host="example.local")
    monkeypatch.setattr(client, "_send_cmd", fake_send)  # noqa: SLF001
    monkeypatch.setattr("src.heos_client.time.sleep", fake_sleep)

    client.play_tidal_container(pid=1, container={"sid": 10, "container_id": "my id"})

    # container_id pitää olla URL-koodattu
    assert called["cmd"] == "browse/add_to_queue?pid=1&sid=10&cid=my%20id&aid=4"
    assert called["sleep"] >= 0.0  # tarkistetaan että sleepiä ylipäätään kutsuttiin


def test_search_heos_playlist_by_name_adds_sid_and_matches_case_insensitive(monkeypatch):
    def fake_send(cmd: str):
        assert cmd == "browse/browse?sid=1025"
        return {
            "payload": [
                {"name": "Other playlist", "container_id": "1"},
                {"name": "My FAVORITE", "container_id": "2"},
            ]
        }

    client = HeosClient(host="example.local")
    monkeypatch.setattr(client, "_send_cmd", fake_send)  # noqa: SLF001

    item = client.search_heos_playlist_by_name("my favorite")
    assert item is not None
    assert item["container_id"] == "2"
    assert item["sid"] == 1025


def test_play_tidal_known_container_returns_true_on_first_success(monkeypatch):
    def fake_get_sid():
        return 10

    called_cmds = []

    def fake_send(cmd: str):
        called_cmds.append(cmd)
        # oletetaan että ensimmäinen candidate onnistuu
        return {"heos": {"result": "success"}}

    client = HeosClient(host="example.local")
    monkeypatch.setattr(client, "_get_tidal_sid", fake_get_sid)  # noqa: SLF001
    monkeypatch.setattr(client, "_send_cmd", fake_send)  # noqa: SLF001

    result = client.play_tidal_known_container(pid=3)
    assert result is True
    # vain yksi yritys, koska heti success
    assert len(called_cmds) == 1
    assert called_cmds[0].startswith("browse/add_to_queue?pid=3&sid=10&cid=")


def test_play_tidal_known_container_returns_false_if_all_fail(monkeypatch):
    def fake_get_sid():
        return 10

    called_cmds = []

    def fake_send(cmd: str):
        called_cmds.append(cmd)
        return {"heos": {"result": "fail"}}

    client = HeosClient(host="example.local")
    monkeypatch.setattr(client, "_get_tidal_sid", fake_get_sid)  # noqa: SLF001
