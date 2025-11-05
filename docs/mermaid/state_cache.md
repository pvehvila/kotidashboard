### 📁 **docs/mermaid/state_cache.md**

# Tilakaavio: Cache-tila

```mermaid
stateDiagram-v2
  [*] --> Empty
  Empty --> Fresh: set(key, data, ttl)
  Fresh --> Fresh: get(key) / hit
  Fresh --> Expiring: ttl < 10%
  Expiring --> Empty: ttl == 0
  Fresh --> Empty: invalidate(key)
