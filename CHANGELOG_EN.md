# 📜 Changelog

This project follows the [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) format and uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
All notable changes are recorded here.

---

## [Unreleased]

### Added
- 🧪 New unit tests across multiple modules:
  - `fetch_nameday_today` now tested for both flat and nested JSON formats.
  - `fetch_holiday_today` covers dict-based, list-based, and error-path scenarios.
  - Added tests for `card_nameday` and `card_nameday_helpers`.
  - Comprehensive HEOS card tests (active track, empty state, playback controls).
  - Full test suites for Hue Motion and Hue Secure sensors (API → viewmodel → UI).

### Changed
- 📅 `calendar_nameday` now fully respects `NAMEDAY_PATHS`; silent fallback to defaults removed.
- 🧪 Tests now follow a consistent structure: frozen `datetime.now()` and bypassing Streamlit caching via `.__wrapped__`.
- 🎧 Simplified HEOS card logic; UI now models only the binary state: *playing / not playing*.
- 🚪 Hue Secure door card updated to use v2 API and a dedicated viewmodel.

### Fixed
- 📈 Nameday & holiday regressions corrected; tests no longer read unexpected real data.
- ⚡ Electricity price card (`card_prices`) restored and aligned with current viewmodel structure.
- 🧱 Updated `src/ui/__init__.py` to reflect current card set.
- 🟢 All HEOS, Hue Motion and Hue Doors tests now pass.

---

## [1.0.0] – 2025-11-06

### 🎉 Initial Public Release

**Kotidashboard** released as a public Streamlit-based home dashboard.

#### Added
- ⚡ Electricity price card (porssisahko.net / sahkonhintatanaan.fi)
- ☀️ Weather via Open-Meteo
- ₿ Bitcoin price with charts
- 📅 Finnish namedays and holidays
- 🧘 Zen card with quote and background image
- 🖥️ System card (CPU, RAM, disk usage)
- 🎧 HEOS / Tidal integration
- 💾 Logging to `logs/`
- 🎨 Dark theme and background images
- 🔄 Automatic refresh and caching

#### Structure & Technology
- Python 3.13, Streamlit, Plotly, Mermaid
- New folder structure (`src/`, `assets/`, `data/`, `scripts/` ...)
- Windows & Raspberry Pi 5 support
- MIT License

---

## [Unreleased]
### Upcoming Features
- 🌤️ Extended 3-day weather forecast
- 🏠 Personal electricity usage history
- 🪴 Home Assistant integration
- 🎨 Optional light/dark theme

---

© 2025 Pekko Vehviläinen — MIT License
