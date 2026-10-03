# 📜 Changelog

Tämä tiedosto noudattaa [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) -formaattia ja [Semantic Versioning](https://semver.org/spec/v2.0.0.html) -versiointia.

Kaikki merkittävät muutokset dokumentoidaan tähän.

---

## [Unreleased]

### Lisätty
- 🌿 Riihimäen siitepölykortti: koivun, heinien ja pujon nykytila sekä ennuste.
- 🌙 Kuukortti korvaa siitepölykortin, kun kaikkien seurattujen kasvien nykytila on "ei havaittu".
- 🌕 Suuri NASAn Clementine-pintakuva ja kuun vaihetta seuraava kaareva varjoraja; päivittäinen vaihe ja valaistu osuus ovat laskennallisia arvioita.

### Dokumentaatio
- 📚 Suomen- ja englanninkieliset README-tiedostot päivitetty siitepöly- ja kuukorttien toiminnalla sekä kuukuvan lähteellä ja rajauksilla.

---

## [1.2.0] – 2026-02-07
### ✨ EQE & kryptokortit

### Lisätty
- ₿ Bitcoin-tikkerikortti (kompakti).
- Ξ Ethereum-tikkerikortti (kompakti).

### Muutettu
- 🚗 EQE-korttia päivitetty.

---

## [1.1.1] – 2025-12-28
### 🛠️ HEOS-kortin korjaus

### Korjattu
- 🎧 HEOS-kortin toiminta palautettu vakaaksi.

### Dokumentaatio
- 📚 Julkaisudokumentaatio päivitetty vastaamaan korjausta.

---

## [1.1.0] – 2025-12-07
### 🚀 Vakaus- ja luotettavuuspäivitys

Tämä julkaisu keskittyy vakauteen, testikattavuuteen, refaktorointiin ja sisäisen arkkitehtuurin selkeyttämiseen.

### Lisätty
- 🧪 Laaja uusi testikattaus:
  - Nimipäivä- ja pyhäpäivälogiikka (flat + nested JSON).
  - `card_nameday` ja `card_nameday_helpers` peruspolut.
  - HEOS-kortti: soitto, tyhjätila, ohjauspainikkeet.
  - Hue Motion & Hue Secure -sensorit: API → viewmodel → UI.
  - Bitcoin-kortin virhepolut.
  - Parannettu Dummy Streamlit -mock (kolumnit, context manager -tuki).

### Muutettu
- 🧱 Suuret refaktoroinnit:
  - Sähkönhinnan normalisointi (60 min ja 15 min).
  - Säädatan muunnos dashboard-muotoon.
  - Nimipäivä- ja pyhäpäivälogiikan erottelu ja selkeytys.
  - Bitcoin-kortin uusi viewmodel.
  - Hue Secure / Motion uudelleenviety v2 API -rakenteeseen.
- 📅 `calendar_nameday` kunnioittaa nyt täysin `NAMEDAY_PATHS`-asetusta.
- 🎧 HEOS-kortin logiikka yksinkertaistettu (vain "soi / ei soi").
- 📚 Dokumentaatio päivitetty: README, README_en, QUALITY, REFACTORING, CHANGELOG.

### Korjattu
- ⚡ Sähkön hintakortin regressiot korjattu.
- 🌤️ Sääkortin data-yhdistyslogiikan virheitä korjattu.
- 🚪 Hue Secure -kortin stale-tilan ja aikaleimojen käsittely korjattu.
- 🧱 `src/ui/__init__.py` päivitetty vastaamaan nykyisiä kortteja.
- 🟢 Kaikki HEOS-, Hue Motion- ja Hue Doors -korttien testit läpäisevät.
- 📈 Testikattavuus nostettu 85–90 % tasolle.

---

## [1.0.0] – 2025-11-06
### 🎉 Ensimmäinen julkinen julkaisu

**Kotidashboard** julkaistu ensimmäistä kertaa avoimena projektina.

### Lisätty
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

### Teknologia & rakenne
- Python 3.13, Streamlit, Plotly, Mermaid
- Uusi hakemistorakenne (`src/`, `assets/`, `data/`, `scripts/` ...)
- Raspberry Pi 5 & Windows -yhteensopivuus
- MIT-lisenssi

---

© 2025 Pekko Vehviläinen — MIT License
