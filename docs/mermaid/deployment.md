
---

### 📁 **docs/mermaid/deployment.md**

```markdown
# Deployment: Raspberry Pi 5 -ympäristö

```mermaid
graph LR
  subgraph LAN
    BrowserPC[PC / Phone / Lenovo M9]
    Streamlit[HomeDashboard (Streamlit)]
    Files[(Local JSON/PNG)]
    Dotenv[(config / env)]
  end

  subgraph Infra
    Pi[Raspberry Pi 5]
    ERX[Ubiquiti EdgeRouter X (PoE)]
    AP[Ubiquiti AC Lite AP]
  end

  BrowserPC <--HTTP--> Streamlit
  Streamlit --- Files
  Streamlit --- Dotenv
  Pi --- Streamlit
  ERX --- Pi
  ERX --- AP
  BrowserPC ~~~ AP
