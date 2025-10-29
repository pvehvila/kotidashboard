# Arkkitehtuuri

```mermaid
graph TD
  subgraph UI
    UI_Main[main.py]
    UI_UI[ui.py]
    UI_Assets[styles & icons]
  end

  subgraph DOMAIN[Logiikka ja apurit]
    D_API[api.py]
    D_UTILS[utils.py]
    D_CFG[config.py]
  end

  subgraph SOURCES[Ulkoiset datalähteet]
    S_Foreca[Foreca API]
    S_Coin[CoinGecko / BTC]
    S_Elec[Pörssisähkö API]
    S_Nameday[Nimipäivät / Pyhät JSON]
  end

  subgraph SYSTEM[Järjestelmä]
    Sys_FS[Paikalliset tiedostot]
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
