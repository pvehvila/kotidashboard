# 📜 Changelog

All notable changes to this project will be documented in this file.
This file follows the [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) format and adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- 🧪 Comprehensive unit tests for the HEOS card (`card_heos`):
  - Rendering of a currently playing track (song / artist / album)
  - Empty-state rendering (“No HEOS playback active”)
  - Button behaviour (⏮, ⏯, ⏭) with assertions that they call the corresponding `HeosClient` methods
- 🧪 A full mock Streamlit implementation (`DummySt`) including column layout and context manager support for stable UI testing

### Changed
- 🎧 Simplified the HEOS card logic to use a flat dictionary from `HeosClient.get_now_playing()`
- 🎧 Removed outdated mute/session-state logic and aligned UI structure with the new test suite

### Fixed
- 🟢 All HEOS-related tests pass (previous 3 failing tests resolved)
- 📈 Overall test coverage increased from 72% to **73%**

### Changed
- 📅 Moved the nameday logic into a dedicated `src/api/calendar_nameday.py` module and split it into smaller helper functions so data loading, date selection and name picking are clearly separated. `fetch_nameday_today()` now acts as a thin public wrapper.
- 📅 Refactored `card_nameday()` to use the new `calendar_nameday` API and a viewmodel layer, keeping the card focused purely on rendering the nameday/holiday data.
- ₿ Cleaned up the Bitcoin card (`card_bitcoin`) to use a dedicated viewmodel that encapsulates price, percentage change and error messages for the UI.

### Fixed
- 📅 Regressions in nameday and holiday lookups after the refactor: `calendar_nameday` now returns the expected names from both flat and nested JSON structures, and the tests (including `test_fetch_nameday_today_*`, `test_fetch_holiday_today_*` and wrapper tests) are passing again.
- ⚡ Restored the electricity price card (`card_prices()`) to a working state and aligned it with the current card/viewmodel structure so spot prices are displayed correctly and the UI no longer depends on legacy helper functions.
- 🧱 Updated `src/ui/__init__.py` to match the current set of cards, so `main.py` imports no longer fail after UI refactors.

### Added
- 🧪 New unit tests for the nameday module (`calendar_nameday`) and the nameday card, covering both list- and dict-shaped JSON data sources for namedays and holidays and guarding against regressions after refactoring.
- 🧪 Unit tests for the Bitcoin card, including error paths where the API returns missing or otherwise invalid data.
- 📄 `docs/CARD_NAMEDAY.md` to document how the nameday card picks its data sources.

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
