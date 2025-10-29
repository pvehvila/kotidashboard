
---

### 📁 **docs/mermaid/sequence_bitcoin.md**

```markdown
# Sekvenssi: Bitcoin-kortti

```mermaid
sequenceDiagram
  participant UI as card_bitcoin
  participant API as fetch_btc_eur
  participant U as utils_cache
  participant CG as coingecko_api

  UI->>API: get price(window=7d)
  API->>U: cache get "btc:7d"
  alt hit
    U-->>API: cached data
  else miss
    API->>CG: GET /market_chart?vs_currency=eur&days=7
    CG-->>API: 200 OK (prices[timestamp,eur])
    API->>U: cache set ttl=2m
  end
  API-->>UI: current EUR, change_24h, series
  UI->>UI: draw line + active pill (24h/7d/30d)
