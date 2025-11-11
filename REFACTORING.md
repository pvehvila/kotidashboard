# 🧩 REFACTORING.md – HomeDashboard

### 📄 Yleiskuva
Tämä dokumentti seuraa refaktoroinnin etenemistä.
Tavoitteena on pitää koodi modulaarisena, helposti testattavana ja selkeästi jaettuna **API-logiikkaan**, **viewmodeleihin** ja **UI-renderöintiin**.

### ✅ Valmiit ja hyväksytyt osiot

| Moduuli | Tila | Kommentti |
|----------|------|-----------|
| `src/ui` yleisesti | ✅ | Kortit on pilkottu: UI renderöi vain, datan kokoaminen siirretty `api/`-kerrokseen. |
| `src/ui/card_prices.py` | ✅ | Laskentalogiikka siirretty `api/electricity_viewmodel.py`. |
| `src/api/bitcoin.py` | ✅ | Funktiot eroteltu: HTTP-pyyntö / raakadata / muunnos. CC-arvot A–B. |
| `src/utils.py` | ✅ | Pilkottu kolmeen: `utils_colors.py`, `utils_sun.py`, `utils_net.py`. |
| `src/ui/card_system.py` | ✅ | Kevyt, CC A (2). |
| `src/logger_config.py`, `src/paths.py`, `src/api/http.py` | ✅ | Selkeät, CC A (1–3). |
| `src/ui/card_bitcoin.py`, `src/ui/card_zen.py`, `src/ui/common.py` | ✅ | Hyväksyttävät A/B-tasot. |

---

### ⚙️ Keskeneräiset / työn alla

| Moduuli | Nykyinen CC | Toimenpide |
|----------|-------------|-------------|
| `src/api/electricity_normalize.py` | C (13), B (9) | Pilko kolmeen vaiheeseen: 1) tunnin parserointi, 2) normalisointi, 3) 60→15 min laajennus. |
| `src/api/electricity_service.py` | C (13) | Siirrä lähdekutsut erillisiksi “adaptereiksi”, jätä tänne vain orchestrointi. |
| `src/api/calendar.py` & `src/api/nameday.py` | D (23) → B (7) | Yhdistä uudelleen: `calendar_nameday.py` on nyt oikea paikka; tee selkeä “fetch → transform → return”. |
| `src/ui/card_nameday.py` | C (13) | Olet jo parantanut D→C. Jatka vielä: taustakuvat ja pyhien haku erillisiksi funktioiksi. |
| `src/ui/card_weather.py` | B (10) | Pidä logiikka minimissä, siirrä laskenta `weather_viewmodel.py`-tyyppiseen tiedostoon. |
| `src/api/weather_fetch.py` | C (16) | Pilko useaan pieneen hakufunktioon (`fetch_forecast`, `fetch_current`, `fetch_alerts`). |
| `src/api/weather_mapping.py` | C (13) | Jaa “wmo-mapit” omiin tiedostoihinsa; CC laskee. |
| `src/api/weather_utils.py` | C (14) | `as_bool()` ja muut voisi yhdistää yhdeksi `safe_cast(value, type_)`-rakenteeksi. |

---

### 📊 Hyväksytyt C-tasot

| Moduuli | Perustelu |
|----------|-----------|
| `src/api/electricity_normalize.py` (osittain) | Domain-logiikka monimutkaista, selkeämmin kommentoitu C-taso hyväksyttävä. |
| `src/api/weather_mapping.py` (osittain) | Datamapping väistämättä monivaiheinen; refaktorointi ei toisi hyötyä. |
| `src/api/weather_debug.py` | Vain kehityskäyttöön, ei refaktoroida. |

---

### 🔄 Seuraavat vaiheet

1. **Synkronoi nimipäivämoduulit**: varmista, että `calendar_nameday.py` sisältää vain datalähteiden hallinnan ja `card_nameday.py` käyttää sen public-funktiota.
2. **Refaktoroi sähkönhinnan normalisointi ja palvelukerros** kolmeksi erilliseksi osaksi.
3. **Päivitä README / dokumentaatio** kuvaamaan uutta kerrosrakennetta (`api` / `viewmodel` / `ui`).
4. **Uusi Radon-ajo** näiden jälkeen – tavoitteena: ei yhtään D-luokkaa, korkeintaan muutama C.

---

### 🏁 Yhteenveto

Radon-analyysin ja tämän dokumentin välillä ei ole ristiriitaa — Radon on vain uudempi mittaus.
Päivitetty tila näyttää, että refaktorointi on 80–85 % valmis.
Loput kolme painopistettä (nimipäivä, sähkön hinta, sää) viedään loppuun ennen seuraavaa releasea.
