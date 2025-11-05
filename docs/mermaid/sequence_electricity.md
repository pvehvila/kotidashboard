### 📁 **docs/mermaid/sequence_electricity.md**

# Sekvenssi: Sähkön hinta -kortti

```mermaid
sequenceDiagram
  participant UI as card_prices
  participant API as fetch_electricity
  participant CFG as config
  participant U as utils_cache
  participant EX as electricity_api

  UI->>API: get prices (today)
  API->>CFG: read API_URL, region
  API->>U: cache get "elec:today"
  alt hit
    U-->>API: cached payload
  else miss
    API->>EX: GET /spot?area=FI&date=YYYY-MM-DD
    EX-->>API: 200 OK (JSON)
    API->>U: cache set ttl=10m
  end
  API-->>UI: normalized list (time, EUR/MWh, c/kWh)
  UI->>UI: render bars, min/max, avg
