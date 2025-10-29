
---

### 📁 **docs/mermaid/sequence_weather.md**

```markdown
# Sekvenssi: Sääkortti

```mermaid
sequenceDiagram
  participant UI as card_weather
  participant API as fetch_weather
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
    API->>U: cache set ttl=5m
  end
  API-->>UI: normalized data
  UI->>UI: render chart & icons
