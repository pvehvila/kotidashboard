
---

### 📁 **docs/mermaid/sequence_system.md**

```markdown
# Sekvenssi: System-kortti

```mermaid
sequenceDiagram
  participant UI as card_system
  participant SYS as fetch_system
  participant U as utils

  UI->>SYS: get metrics
  SYS->>U: read cpu, mem, disk, net
  U-->>SYS: dict{cpu%, mem%, temp, ip, uptime}
  SYS-->>UI: normalized metrics
  UI->>UI: render tiles + thresholds
