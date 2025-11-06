# 📜 Changelog

Kaikki merkittävät muutokset tähän projektiin dokumentoidaan tähän tiedostoon.  
Tiedosto noudattaa [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) -periaatetta ja versiointi perustuu [Semantic Versioning](https://semver.org/spec/v2.0.0.html) -käytäntöön.

---

## [1.0.0] – 2025-11-06
### 🎉 Ensimmäinen julkinen julkaisu

**Kotidashboard** on Streamlit-pohjainen kotinäyttö, joka kokoaa arjen keskeiset tiedot yhteen näkymään.

#### Lisätyt ominaisuudet
- ⚡ Sähkön hinta (porssisahko.net / sahkonhintatanaan.fi)
- ☀️ Sää Open-Meteosta (lämpötila, sademäärä, pilvisyys, ikoni)
- ₿ Bitcoinin hinta CoinGeckosta
- 📅 Nimipäivät ja pyhät
- 🧘 Zen-kortti satunnaisella mietelmällä ja taustakuvalla
- 🖥️ Järjestelmäkortti (CPU, RAM, levytila)
- 💾 Lokitus tiedostoon `logs/homedashboard.log`
- 🎨 Mukautettu tumma teema ja taustakuvat `assets/`-kansiosta
- 🔄 Automaattinen päivitys ja välimuisti

#### Rakenne ja teknologia
- Uusi hakemistorakenne (`src/`, `assets/`, `data/`, `docs/`, `scripts/`, `logs/`)
- Python 3.13 + Streamlit + Plotly + Mermaid
- Käyttö Windowsissa ja Raspberry Pi 5:llä
- MIT-lisenssi

---

## [Unreleased]
### 🧩 Tulevat muutokset
- 🌤️ Laajennettu sääennuste (3 vrk)
- 🏠 Sähkönkulutuksen oman historian näyttö
- 🪴 Kotiautomaatiointegraatiot (Home Assistant)
- ⚙️ Käyttöliittymän teemat (light / dark switch)

---

© 2025 Pekko Vehviläinen  |  [MIT License](LICENSE)
