from src.config import HEOS_HOST, HEOS_PASSWORD, HEOS_USERNAME
from src.heos_client import HeosClient

client = HeosClient(HEOS_HOST, username=HEOS_USERNAME, password=HEOS_PASSWORD)
client.sign_in()

sid = 10  # Tidal on hyvin usein 10, mutta ota listauksesta oikea
cid = "SE_LÖYTYNYT_CONTAINER_ID"  # vaihda tähän se, minkä näit
resp = client._send_cmd(f"browse/browse?sid={sid}&cid={cid}")
for item in resp.get("payload", []):
    print(item)
