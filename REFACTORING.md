# 🧩 REFACTORING.md – HomeDashboard

### 📄 Yleiskuva
Tämä dokumentti seuraa refaktoroinnin etenemistä.
Tavoitteena on pitää koodi modulaarisena, helposti testattavana ja selkeästi jaettuna **API-logiikkaan**, **viewmodeleihin** ja **UI-renderöintiin**.

Refaktoroinnin tämänhetkinen tila: suurin osa moduuleista on jo A/B-tasoa Radonin mukaan, mutta muutama “solmukohta” tuottaa edelleen C–D -tason monimutkaisuutta. Nämä on listattu alla ja niille on kirjattu konkreettiset toimenpiteet.

---

### ✅ Valmiit ja hyväksytyt osiot

| Moduuli | Tila | Kommentti |
|----------|------|-----------|
| `src/ui` yleisesti | ✅ | Korttien ajatus selventynyt: UI renderöi vain, datan kokoaminen siirretty `api/`-kerrokseen. |
| `src/ui/card_system.py` | ✅ | Kevyt, CC A (2). |
| `src/logger_config.py`, `src/paths.py`, `src/api/http.py` | ✅ | Selkeät, CC A (1–3). |
| `src/api/bitcoin.py` | ✅ | HTTP-pyyntö, raakadata ja muunnos eroteltu. CC-arvot A–B. |
| `src/ui/card_bitcoin.py`, `src/ui/card_zen.py`, `src/ui/common.py` | ✅ | Hyväksyttävät A/B-tasot. |
| `src/utils.py` jaetut osat | ✅ | Pilkottu pieniin apufunktioihin; virheraportointi eriytetty. |
| HEOS-asiakas (`src/heos_client.py`) | ✅ | Lähes kaikki funktiot A-tasoa, ei vaadi jatkotoimia. |

---

### ⚙️ Keskeneräiset / työn alla

Alla ovat ne kohdat, jotka Radon nosti vielä esiin (C/D), ja mitä niille pitää tehdä.

#### 1. Nimipäivät

- **Nykytila**:
  - `src/api/calendar.py::fetch_nameday_today` – **D (23)**
  - `src/api/nameday.py::fetch_nameday_today` – **B (7)**
  - `src/ui/card_nameday.py` – **C (13)**

- **Toimenpiteet**:
  1. Pilko `fetch_nameday_today` kolmeen osaan:
     - `_load_nameday_data()` – vain tiedoston/lähteiden avaus
     - `_pick_today_name(data, today)` – logiikka, joka valitsee nimen myös sisäkkäisestä rakenteesta
     - `fetch_nameday_today()` – ohut julkinen funktio
  2. Siirrä datalähteiden hallinta selkeästi yhteen tiedostoon (esim. `calendar_nameday.py`), jotta UI käyttää vain public-funktiota. DONE
  3. Pilko `src/ui/card_nameday.py` siten, että:
     - datan haku → `get_nameday_vm()`
     - taustakuvan ja lipputiedon valinta → erilliset funktiot (`get_flag_info`, `get_background_image` ovat jo olemassa)
     - varsinainen Streamlit-renderöinti → `render_nameday_card(vm)`

**Tavoite**: D (23) → B (7–9), UI-kortti C → B. DONE

---

#### 2. Sähkön hinta

- **Nykytila**:
  - `src/api/electricity_normalize.py` – useita B/C-funktioita (`_parse_hour_from_item` C (12), `normalize_prices_list_15min` B (7))
  - `src/ui/card_prices.py::_next_12h_15min` – **C (15)**
  - `src/ui/card_prices.py::card_prices` – **C (13)**
  - `src/api/electricity_service.py` – A-tason funktioita, mutta orkestrointi on täällä

- **Toimenpiteet**:
  1. Jaottele normalisointi kolmeen vaiheeseen:
     - “parseri” (haetaan tunti, hinta, aikaleima)
     - “normalisointi” (tehdään listasta yhdenmukainen)
     - “laajennus 60 → 15 min” (nykyinen `expand_hourly_to_15min`)
  2. Siirrä kortin laskentalogiikka (`_current_price_15min`, `_next_12h_15min`) erilliseen viewmodel-tiedostoon (esim. `src/api/electricity_viewmodel.py`), jolloin UI-funktio `card_prices` vain renderöi.
  3. Varmista, että palvelukerros (`electricity_service`) kutsuu vain adaptereita (`electricity_sources`, `electricity_adapters`) eikä sisällä muunnoslogiikkaa.

**Tavoite**: UI-kortti B-tasolle, normalisointi selkeästi kommentoiduksi C-tasoksi (hyväksyttävä, koska domain on monimutkaisempi).

---

#### 3. Sää ja WMO-mappaus

- **Nykytila**:
  - `src/api/weather_fetch.py::fetch_weather_points` – **C (16)**
  - `src/api/weather_debug.py::card_weather_debug_matrix` – **C (13)** (jätettävissä dev-käyttöön)
  - `src/api/wmo_icon_map.py::wmo_to_icon_key` – **C (13)**
  - `src/api/wmo_map_loader.py::load_wmo_foreca_map` – **C (11)**

- **Toimenpiteet**:
  1. Pilko `fetch_weather_points` alafunktioiksi:
     - `_fetch_all_raw(lat, lon, tz_name)` – kutsuu forecast/current/alerts
     - `_merge_weather_payloads(raw)` – yhdistää eri vastaukset
     - `_to_points(raw, tz)` – muuntaa dashboardin muotoon
  2. Jaa WMO-mappaus kahteen tasoon:
     - “tiedoston/JSONin luku ja valmistelu”
     - “avain → koodi” -haku
     Näin `wmo_to_icon_key` ohenee.
  3. `weather_debug` voidaan jättää C-tasolle, mutta siihen kannattaa lisätä lyhyt docstring (“dev/käyttö”) ettei sitä yritetä optimoida jatkossa.

**Tavoite**: `fetch_weather_points` B-tasolle, WMO-lataus B:hen.

---

#### 4. UI-korttien kolmikerrosjako

Seuraavat funktiot olivat Radonin mukaan vielä C:
- `src/ui/card_prices.py::card_prices`
- `src/ui/card_nameday.py::card_nameday`
- `src/ui/card_bitcoin_parts.py::get_btc_series_for_window`
- `src/ui/card_bitcoin_parts.py::build_btc_figure`

**Toimenpiteet (sama malli kaikille):**

1. **viewmodel**: funktio, joka kerää ja muotoilee datan (ei Streamlitiä)
2. **builder**: funktio, joka muodostaa tekstit/HTML:n (voi palauttaa stringit)
3. **render**: varsinainen kortti, jossa on vain Streamlit-kutsut

Kun tämä on tehty, UI-puolen CC putoaa A/B-tasolle ja testaus helpottuu, koska viewmodelin voi testata ilman Streamlitiä.

---

### 📊 Hyväksytyt C-tasot

| Moduuli | Perustelu |
|----------|-----------|
| `src/api/electricity_normalize.py` (osittain) | Domain-logiikka monimutkaista, selkeämmin kommentoitu C-taso hyväksyttävä. |
| `src/api/weather_debug.py` | Vain kehityskäyttöön, ei refaktoroida enempää. |
| `src/api/wmo_trace.py` | Hyvin pieni, mutta liittyy diagnostiikkaan – nykyinen taso riittää. |

---

### 🔄 Seuraavat vaiheet

1. **Pilkko nimipäivälogiikka** kolmeen funktioon ja päivitä UI käyttämään uutta public-funktiota.
2. **Siirrä sähkö-kortin laskenta viewmodeliin** (`electricity_viewmodel.py`) ja ohennna `card_prices`.
3. **Pilkko `fetch_weather_points` ja WMO-lataus** alafunktioiksi.
4. **Aja Ruff ja Radon uudelleen** varmistaaksesi, että D-taso on poistunut eikä uusia E731/UP038-varoituksia tule.
5. **Päivitä README / kehittäjäohje** kertomaan UI → viewmodel → API -rakenteesta.

---

### 🏁 Yhteenveto

Refaktorointi on nyt noin **85 % valmis** Radonin näkökulmasta. Loppu 15 % on koottu muutamaan isompaan funktioon (nimipäivä, sähkön hinta, säämappaus). Kun ne pilkotaan ja Ruff-varoitukset korjataan, koodi on tasalaatuista ja testit eivät riko samoista kohdista toistuvasti.
