
---

### 📁 **docs/mermaid/deployment.md**

# Deployment: Raspberry Pi 5 -ympäristö

```mermaid
graph LR
  subgraph LAN
    client["PC / phone / Lenovo M9"]
    app["HomeDashboard Streamlit"]
    files["Local JSON & PNG"]
    env["Config / env"]
  end

  subgraph Infra
    pi["Raspberry Pi 5"]
    router["Ubiquiti EdgeRouter X (PoE)"]
    ap["Ubiquiti AC Lite AP"]
  end

  client <-- HTTP --> app
  app --- files
  app --- env
  pi --- app
  router --- pi
  router --- ap
  client ~~~ ap
