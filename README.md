Koodin päivittäminen:

-Kirjaudu ssh:lla Raspberryyn:
 "ssh admin@RaspberryPi5"

- Syötä salasana:
 "admin@raspberrypi5's password: xxxxxxxxx"

- Hae tuorein versio GitHub:ista ja käynnistä palveu uudelleen:
 "update-dash"

```mermaid
graph TD
  subgraph UI
    UI_Main[main.py]
    UI_UI[ui.py]
    UI_Assets[styles & icons]
  end

  subgraph DOMAIN[Logic & Helpers]
    D_API[api.py]
    D_UTILS[utils.py]
    D_CFG[config.py]
  end

  subgraph SOURCES[External Sources]
    S_Foreca[Foreca API]
    S_Coin[CoinGecko / BTC]
    S_Elec[Electricity API]
    S_Nameday[Namedays / Holidays]
  end

  subgraph SYSTEM[System]
    Sys_FS[Local files]
    Sys_Runtime[Streamlit runtime / cache]
  end

  UI_Main --> UI_UI
  UI_UI --> D_API
  UI_UI --> D_UTILS
  UI_UI --> D_CFG

  D_API --> S_Foreca
  D_API --> S_Coin
  D_API --> S_Elec
  D_API --> S_Nameday
  D_API --> Sys_FS
  D_UTILS --> Sys_FS
  D_UTILS --> Sys_Runtime

  S_Foreca --> D_API
  S_Coin --> D_API
  S_Elec --> D_API
  S_Nameday --> D_API
  D_API --> UI_UI


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
  API-->>UI: normalized data (temps, icons, times)
  UI->>UI: render chart & icons


  graph LR
  subgraph UI[ui.py]
    C1[card_weather]
    C2[card_prices]
    C3[card_bitcoin]
    C4[card_nameday]
    C5[card_system]
    C6[card_zen]
  end

  subgraph API[api.py]
    W[fetch_weather]
    E[fetch_electricity]
    B[fetch_btc_eur]
    N[fetch_namedays]
    S[fetch_system]
  end

  C1 --> W
  C2 --> E
  C3 --> B
  C4 --> N
  C5 --> S
  C6 --> S
```
