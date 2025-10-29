Koodin päivittäminen:

-Kirjaudu ssh:lla Raspberryyn:
 "ssh admin@RaspberryPi5"

- Syötä salasana:
 "admin@raspberrypi5's password: xxxxxxxxx"

- Hae tuorein versio GitHub:ista ja käynnistä palveu uudelleen:
 "update-dash"

## Arkkitehtuuri

```mermaid
graph TD
  UI[ui.py] --> API[api.py]
  UI --> UTIL[utils.py]
  API --> FORECA[Foreca API]
  API --> BTC[CoinGecko]
```

## Sekvenssi: Sääkortti

```mermaid
sequenceDiagram
  participant UI as ui_card_weather
  participant API as api_fetch_weather
  participant CFG as config
  participant F as foreca_api
  participant U as utils_cache

  UI->>API: get weather (window=3h)
  API->>CFG: read keys & location
  API->>U: cache get "weather:3h"
  alt cache hit
    U-->>API: cached payload
  else cache miss
    API->>F: GET /forecast?loc=...&key=...
    F-->>API: 200 OK (JSON)
    API->>U: cache set "weather:3h" (ttl 5m)
  end
  API-->>UI: normalized data
  UI->>UI: render chart
```

