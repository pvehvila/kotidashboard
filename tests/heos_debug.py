import json
import socket
from typing import Any

HEOS_HOST = "192.168.1.231"  # vaihda
HEOS_PORT = 1255
PID = 186388645  # vaihda samaan kuin HEOS_PLAYER_ID


def send(cmd: str) -> dict[str, Any]:
    with socket.create_connection((HEOS_HOST, HEOS_PORT), timeout=3.0) as s:
        s.sendall(f"heos://{cmd}\r\n".encode())
        s.settimeout(3.0)
        data = s.recv(65535).decode("utf-8", errors="replace")

    # HEOS voi palauttaa useita JSON-rivejä; tulostetaan kaikki ja palautetaan viimeinen validi
    last = {}
    print("\n--- RAW ---")
    print(data)
    print("--- PARSED ---")
    for line in data.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
            print(json.dumps(obj, indent=2, ensure_ascii=False))
            last = obj
        except json.JSONDecodeError:
            pass
    return last


print("Players:")
send("player/get_players")

print("\nPlay state before:")
send(f"player/get_play_state?pid={PID}")

print("\nNow playing:")
send(f"player/get_now_playing_media?pid={PID}")

print("\nTrying: player/play_pause")
send(f"player/play_pause?pid={PID}")

print("\nPlay state after play_pause:")
send(f"player/get_play_state?pid={PID}")

print("\nTrying: player/set_play_state play")
send(f"player/set_play_state?pid={PID}&state=play")

print("\nPlay state after set_play_state play:")
send(f"player/get_play_state?pid={PID}")

print("\nTrying: player/set_play_state pause")
send(f"player/set_play_state?pid={PID}&state=pause")

print("\nPlay state after pause:")
send(f"player/get_play_state?pid={PID}")

print("\nTrying: player/play_queue_item qid=1")
send(f"player/play_queue_item?pid={PID}&qid=1")
print("\nPlay state after play_queue_item:")
send(f"player/get_play_state?pid={PID}")
