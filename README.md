Koodin päivittäminen:

-Kirjaudu ssh:lla Raspberryyn:
 "ssh admin@RaspberryPi5"

- Syötä salasana:
 "admin@raspberrypi5's password: xxxxxxxxx"

- Hae tuorein versio GitHub:ista ja käynnistä palveu uudelleen:
 "update-dash"

graph TD
  %% --- Kerrokset ---
  subgraph UI[UI-kerros]
    UI_Main[main.py<br/>- käynnistys, reititys]
    UI_UI[ui.py<br/>- kortit & layout]
    UI_Style[style.css / icons]
  end

  subgraph Domain[Logiikka & apurit]
    D_API[api.py<br/>- datan haku & muunnokset]
    D_Utils[utils.py<br/>- välineet: cache, logitus, virheilmoitukset]
    D_Config[config.py<br/>- asetukset & avaimet]
  end

  subgraph Sources[Ulkoiset datalähteet]
    S_Foreca[Foreca API<br/>sääennusteet]
    S_Coin[CoinGecko/Bitcoin]
    S_Elec[Pörssisähkö API]
    S_Nameday[Nimipäivät / Pyhät JSON]
  end

  subgraph System[Järjestelmä]
    Sys_FS[Paikalliset tiedostot<br/>/*.json, *.png]
    Sys_Scheduler[Streamlit runtime<br/>/ välimuisti]
  end

  %% --- Virrat ---
  UI_Main --> UI_UI
  UI_UI --> D_API
  UI_UI --> D_Utils
  UI_UI --> D_Config

  D_API --> S_Foreca
  D_API --> S_Coin
  D_API --> S_Elec
  D_API --> S_Nameday

  D_API --> Sys_FS
  D_Utils --> Sys_FS
  D_Utils --> Sys_Scheduler

  %% --- Paluusuunta ---
  S_Foreca --> D_API
  S_Coin --> D_API
  S_Elec --> D_API
  S_Nameday --> D_API
  D_API --> UI_UI

sequenceDiagram
  participant UI as ui.card_weather()
  participant API as api.fetch_weather()
  participant CFG as config
  participant F as Foreca API
  participant U as utils (cache/log)

  UI->>API: get weather(window=3h)
  API->>CFG: read FORECA_KEY, location
  API->>U: check cache("weather:3h")
  alt cache hit
    U-->>API: cached payload
  else cache miss
    API->>F: GET /forecast?loc=...&key=...
    F-->>API: 200 OK, JSON
    API->>U: cache set("weather:3h", ttl=5min)
  end
  API-->>UI: normalized dict (temps, icons, times)
  UI->>UI: render Plotly chart + icons

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

