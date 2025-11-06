# 📜 Changelog

All notable changes to this project will be documented in this file.  
This file follows the [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) format and adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] – 2025-11-06
### 🎉 Initial Public Release

**Kotidashboard** is a Streamlit-based home dashboard that brings together essential daily information in one view.

#### Added
- ⚡ Electricity prices (porssisahko.net / sahkonhintatanaan.fi)
- ☀️ Weather from Open-Meteo (temperature, precipitation, cloud cover, icon)
- ₿ Bitcoin price from CoinGecko
- 📅 Finnish namedays and holidays
- 🧘 Zen card with random quote and background image
- 🖥️ System card (CPU, RAM, disk usage)
- 💾 Logging to `logs/homedashboard.log`
- 🎨 Custom dark theme and background images from `assets/`
- 🔄 Automatic refresh and caching

#### Structure and Technology
- New folder structure (`src/`, `assets/`, `data/`, `docs/`, `scripts/`, `logs/`)
- Python 3.13 + Streamlit + Plotly + Mermaid
- Runs on Windows and Raspberry Pi 5
- Licensed under MIT

---

## [Unreleased]
### 🧩 Upcoming Features
- 🌤️ Extended 3-day weather forecast
- 🏠 Personal electricity consumption tracking
- 🪴 Home automation integrations (Home Assistant)
- ⚙️ Light/Dark theme switch

---

© 2025 Pekko Vehviläinen  |  [MIT License](LICENSE)
