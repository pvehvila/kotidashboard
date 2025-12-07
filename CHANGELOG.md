# 📜 Changelog

Tämä tiedosto noudattaa [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) -formaattia ja [Semantic Versioning](https://semver.org/spec/v2.0.0.html) -versiointia.

Kaikki merkittävät muutokset dokumentoidaan tähän.

---

## [Unreleased]

### Lisätty
- 🧪 Uusia yksikkötestejä (nimipäivät, pyhäpäivät, HEOS, Hue Motion, Hue Secure):
  - `fetch_nameday_today` testaa sekä flat- että nested-rakenteet.
  - `fetch_holiday_today` testaa dict- ja listalähteet sekä virhepolut.
  - `card_nameday` ja `card_nameday_helpers` testattu peruspoluilla.
  - HEOS-kortille kattavat testit (soiva kappale, tyhjätila, ohjauspainikkeet).
  - Hue Motion- ja Hue Secure -sensorikortit testattu läpi API → viewmodel → UI -ketjun.

### Muutettu
- 📅 `calendar_nameday` kunnioittaa nyt `NAMEDAY_PATHS`-asetusta; ei enää hiljaista fallbackia oletuspolkuun.
- 🧪 Testit käyttävät yhtenäistä patternia: jäädytetty `datetime.now()` ja välimuistin ohitus `.__wrapped__`-attribuutilla.
- 🎧 HEOS-kortin logiikka yksinkertaistettu: UI käsittelee vain "soi / ei soi" -tilan.
- 🚪 Hue Secure -kortti käyttää v2 APIa ja selkeää viewmodel-kerrosta.

### Korjattu
- 📈 Regressiot nimipäivä- ja pyhäpäivähaussa korjattu; testit eivät enää käytä vahingossa oikeita datatiedostoja.
- ⚡ `card_prices()` palautettu toimivaksi ja päivitetty nykyiseen viewmodel-rakenteeseen.
- 🧱 `src/ui/__init__.py` päivitetty vastaamaan uusia kortteja.
- 🟢 HEOS-, Hue Motion- ja Hue Doors -korttien kaikki testit läpäisevät.

---

## [1.0.0] – 2025-11-06

### 🎉 Ensimmäinen julkinen julkaisu

**Kotidashboard** julkaistu ensimmäistä kertaa avoimena projektina.

#### Lisätty
- ⚡ Sähkön hinta (porssisahko.net / sahkonhintatanaan.fi)
- ☀️ Sää Open-Meteosta
- ₿ Bitcoinin hinta CoinGeckosta
- 📅 Nimipäivät ja pyhäpäivät
- 🧘 Zen-kortti taustakuvalla
- 🖥️ Järjestelmäkortti (CPU, RAM, levytila)
- 🎧 HEOS / Tidal -tuki
- 💾 Lokitus `logs/`-kansioon
- 🎨 Tumma teema + taustakuvat
- 🔄 Automaattinen päivitys ja välimuisti

#### Teknologia & rakenne
- Python 3.13, Streamlit, Plotly, Mermaid
- Uusi hakemistorakenne (`src/`, `assets/`, `data/`, `scripts/` ...)
- Raspberry Pi 5 & Windows -yhteensopivuus
- MIT-lisenssi

---

## [Unreleased]
### Tulevat suunnitelmat
- 🌤️ Laajennettu kolmen vuorokauden sääennuste
- 🏠 Oman sähkönkulutushistorian näyttö
- 🪴 Home Assistant -integraatio
- 🎨 Vaihdettava light/dark-teema

---

© 2025 Pekko Vehviläinen — MIT License
