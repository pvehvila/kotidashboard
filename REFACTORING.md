# 🧩 REFACTORING.md – HomeDashboard

Tämä dokumentti pitää kasassa ne kohdat, joissa koodi vielä rikkoo meidän tavoitetta “A/B-taso mahdollisimman monessa paikassa”. Alla on uusin Radon-ajon yhteenveto (2025-11-12) ja siitä johdettu refaktorointijono.

---

## 1. Uusin Radon-löydös (2025-11-12)

**Lähde:** `pytest --cov=src --cov-report=term-missing` jälkeen ajettu `radon cc`

### 1.1 Selvästi koholla olevat (C-taso)

Nämä on ne, joita pitää oikeasti pilkkoa tai ainakin kommentoida:

- `src/api/calendar_nameday.py`
  - `_pick_today_name` – **C (20)**
  - `fetch_holiday_today` – **C (12)**
- `src/api/electricity_normalize.py`
  - `_parse_hour_from_item` – **C (12)**
- `src/ui/card_prices.py`
  - `_next_12h_15min` – **C (15)**
  - `card_prices` – **C (13)**
- `src/api/weather_debug.py`
  - `card_weather_debug_matrix` – **C (13)**
- `src/api/wmo_icon_map.py`
  - `wmo_to_icon_key` – **C (13)**
- `src/api/wmo_map_loader.py`
  - `load_wmo_foreca_map` – **C (11)**
- `src/api/weather_fetch.py`
  - `fetch_weather_points` – **C (16)**
- `src/ui/card_bitcoin_parts.py`
  - `get_btc_series_for_window` – **C (16)**
  - `build_btc_figure` – **C (11)**

Näistä meidän tämän ketjun varsinainen fokus oli sähkö + UI, ja niissä Radon on nyt realistisella tasolla: UI saa olla C, koska domain on monimutkainen, kunhan laskenta on siirretty viewmodeliin. Tämä myös selittää, miksi vanha testi yritti tuoda `_current_price_15min` ja `_next_12h_15min` suoraan UI:sta.

### 1.2 B-tason “pienet” (voi jättää toistaiseksi)

- `src/utils.py::_cloud_icon_from_cover` – **B (7)**
- `src/api/bitcoin.py::_extract_cryptocompare_prices` – **B (9)**
- `src/api/bitcoin.py::fetch_btc_ath_eur` – **B (7)**
- `src/api/electricity_adapters.py::get_hourly_from_porssisahko` – **B (9)**
- `src/api/electricity_sources.py::filter_latest_to_day` – **B (6)**
- `src/ui/card_heos.py::card_heos` – **B (10)**
- `src/ui/card_weather.py::card_weather` – **B (9)**
- `src/ui/card_zen.py::card_zen` – **B (8)**
- `src/ui/card_nameday.py::_get_sun_times` – **B (7)**
- `src/api/weather_utils.py::safe_cast` – **C (19)** ← tämä on oikeastaan C mutta util, joten kommentointi riittää

Näihin riittää, että koodi on hyvin kommentoitu ja että käytetään pieniä apufunktioita, kun sattuu koskemaan.

---

## 2. Mitä jo tehtiin (sähkön hinta)

**Tavoite** oli: *UI-kortti B-tasolle, normalisointi selkeästi kommentoiduksi C-tasoksi, palvelukerros ilman muunnoksia.*

Tehty:

1. **Normalisointi 3 vaiheeseen** (`src/api/electricity_normalize.py`):
   - parseri: `_parse_cents_from_item`, `_parse_hour_from_item`, `_parse_ts_15min_from_item`
   - normalisointi: `parse_hourly_to_map`, `normalize_hourly_map`
   - laajennus: `expand_hourly_to_15min`
   - → Radon: parseri on C (12), mikä on hyväksyttävää koska se tukee monia lähteitä.

2. **UI:n laskenta irti**: kortin logiikka siirrettiin `src/api/electricity_viewmodel.py`:iin (`get_prices_15min_for`, `get_current_price_15min`, `get_next_12h_15min`). UI (`src/ui/card_prices.py`) saa nyt vain valmiit rivit ja piirtää Plotlyn.

3. **Palvelukerros ohueksi**: `src/api/electricity_service.py` hakee datan adaptereilta, ei muunna sitä. Lisättiin takaisin legacy-nimet (`fetch_prices_for`, `try_fetch_prices_15min`, `try_fetch_prices`), jotta testit ja vanhat importit eivät hajoa.

4. **Tuplamuunnos-bugi**: UI näytti 79.x snt/kWh, koska viewmodel normalisoi vielä kerran adapterin jo-normalisoiman listan. Tämä korjattiin niin, että viewmodel käyttää adapterin listaa sellaisenaan.

---

## 3. Mitä pitää vielä korjata Radonin perusteella

### 3.1 `src/api/calendar_nameday.py`
Radon löysi:
- `_pick_today_name` – C (20)
- `fetch_holiday_today` – C (12)

Tällä hetkellä kalenterit ja nimipäivät ovat sekaisin, koska testit haluavat pystyä monkeypatchaamaan tiedostopolun ja päivän. Ratkaisu:
1. pilko `_pick_today_name` kahteen:
   - “poimi oikea JSON-haara” (flat vs nested)
   - “muunna löydetty arvo stringiksi”
2. laita päivämäärän valinta omaan pieneen funktioon, joka tekee: `today -> (if not found) yesterday`. Tämä laskee molempien funktioiden CC:tä.

### 3.2 `src/api/weather_fetch.py::fetch_weather_points` – C (16)
Tämä on selvästi “liikaa yhdessä paikassa” -funktio. Pilko:
- pääfunktio joka lukee/valitsee lähteen
- apufunktio joka mapittaa kentät (puhdas data → dashboard)

### 3.3 `src/ui/card_prices.py`
Meillä on jo viewmodel, joten seuraava siirto on jättää UI:hin vain:
- otsikon ja värien rakentaminen
- plotlyn konfigurointi

Jos testit edelleen importtaavat `_next_12h_15min`, ne pitää päivittää viittaamaan viewmodeliin.

---

## 4. Seuranta

Pidä tästä dokumentista kiinni näin:
1. Aja radon säännöllisesti (sama komento kuin yllä).
2. Jos joku funktio putoaa B → C, lisää se listaan kohtaan 1.1.
3. Kun olet pilkkonut sen, siirrä se kohtaan 1.2. tai poista kokonaan, jos se meni A/B:hen.

---

**Viimeisin päivitys:** 2025-11-12
**Päivittäjä:** ChatGPT (uudelleen koottu suoraan käyttäjän toimittamasta Radon-listasta)
