# 📜 Changelog

This project follows the [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) format and uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
All notable changes are recorded here.

---

## [Unreleased]

### Added
- 🌿 Pollen card for Riihimäki with current levels and forecasts for birch, grasses and mugwort.
- 🌙 Moon card replaces the pollen card when all monitored plants have a current level of "not detected".
- 🌕 Large NASA Clementine surface image with a curved phase shadow; daily phase timing and illuminated percentage are approximate calculations.

### Documentation
- 📚 Finnish and English READMEs updated with pollen and Moon card behavior, image attribution and limitations.

---

## [1.2.0] – 2026-02-07
### ✨ EQE & crypto cards

### Added
- ₿ Compact Bitcoin ticker card.
- Ξ Compact Ethereum ticker card.

### Changed
- 🚗 Updated the EQE card.

---

## [1.1.1] – 2025-12-28
### 🛠️ HEOS card fix

### Fixed
- 🎧 Restored stable behavior for the HEOS card.

### Documentation
- 📚 Release documentation updated to reflect the fix.

---

## [1.1.0] – 2025-12-07
### 🚀 Vakaus- ja luotettavuuspäivitys

### Lisätty
- 🧪 Laajat uudet testipaketit (nimipäivät, pyhäpäivät, HEOS, Hue Motion, Hue Secure):
  - Testit flat- ja nested-rakenteisille nimipäivä- ja pyhäpäivälähteille.
  - HEOS-kortin täydet testit: soitto, tyhjätila, ohjauspainikkeet.
  - Hue Motion & Hue Secure -korttien koko API → viewmodel → UI -ketju testattu.
  - Bitcoin-kortin virhepolut kattavasti testattu.
  - Dummy Streamlit -mock parannettu (kolumnit, context manager -tuki).

### Muutettu
- 🧱 Kriittiset moduulit refaktoroitu A/B-kompleksisuustasolle (Radon):
  - Sähkön hinnan normalisointi 60 min → 15 min.
  - Säädatan muunnos dashboard-muotoon.
  - Nimipäivä- ja pyhäpäivälogiikan modernisointi.
  - Bitcoin-kortin viewmodel ja datasarjalogiikka.
  - Hue Secure / Motion -korttien rakenne (API v2, viewmodel-kerros).
- 📚 Dokumentaatio kokonaisuudessaan päivitetty (README, QUALITY, REFACTORING, CHANGELOG).
- 🎧 HEOS-kortin logiikka yksinkertaistettu: vain "soi / ei soi" -tila.

### Korjattu
- ⚡ Sähkön hintakortin regressiot korjattu ja kortti palautettu toimintaan.
- 🌤️ Sääkortin tunnin/dyyn datan yhdistämisen virheet korjattu.
- 🚪 Hue Secure -kortin stale-tila- ja aikaleimalogiikka korjattu.
- 📈 Testikattavuus nostettu 85–90 % tasolle.
- 🧱 `src/ui/__init__.py` päivitetty vastaamaan nykyistä korttikokoonpanoa.

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

© 2025 Pekko Vehviläinen — MIT License
