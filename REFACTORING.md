# 🧩 REFACTORING.md – HomeDashboard

Tämä dokumentti pitää kasassa ne kohdat, joissa koodi vielä rikkoo meidän tavoitetta “A/B-taso mahdollisimman monessa paikassa”. Alla on uusin Radon-ajon yhteenveto (**2025-11-17**) ja siitä johdettu refaktorointijono.

---

## 1. Uusin Radon-löydös (2025-11-17)

**Lähde:** `pytest --cov=src --cov-report=term-missing` jälkeen ajettu `radon cc`

### 1.1 Aktiivinen refaktorointilista (C/D-taso)

Nämä ovat ne, joita kannattaa vielä pilkkoa tai selkeyttää. D-taso on “punainen”, C-taso “oranssi”.

- `src/api/calendar_nameday.py`
  - `_pick_today_name` – **C (20)**
  - `fetch_holiday_today` – **C (12)**
- `src/api/weather_fetch.py`
  - `_map_hourly_to_dashboard` – **D (22)**
- `src/api/weather_utils.py`
  - `safe_cast` – **C (19)**  ← util-funktio, voi myös jäädä C-tasolle, jos hyvin kommentoitu
- `src/api/wmo_icon_map.py`
  - `wmo_to_icon_key` – **C (13)**
- `src/api/wmo_map_loader.py`
  - `load_wmo_foreca_map` – **C (11)**
- `src/ui/card_bitcoin_parts.py`
  - `get_btc_series_for_window` – **C (16)**
  - `build_btc_figure` – **C (11)**
- `src/ui/card_prices.py`
  - `_next_12h_15min` – **C (15)**
  - `card_prices` – **C (13)**

Näistä _map_hourly_to_dashboard on selkeä “järjesteltävä uudelleen” -kandidaatti (D), muut ovat vielä realistisia C-tason funktioita, mutta niitä voidaan pilkkoa, jos niihin tulee muutenkin muutoksia.

### 1.2 Hyväksytyt C:t ja B:t (toleranssi)

Nämä ovat funktioita, joissa C/B-taso on hyväksytty, kunhan koodi on selkeästi kommentoitu ja rajapinnat siistit.

- `src/api/electricity_normalize.py`
  - `_parse_hour_from_item` – **C (12)**
    → parseri monelle eri datalähteelle, hyväksytään C kunhan logiikka on dokumentoitu.
- `src/api/weather_debug.py`
  - `card_weather_debug_matrix` – **C (13)**
    → debug-kortti, saa olla monimutkaisempi.
- `src/utils.py`
  - `_cloud_icon_from_cover` – **B (7)**
- `src/api/bitcoin.py`
  - `_extract_cryptocompare_prices` – **B (9)**
  - `fetch_btc_ath_eur` – **B (7)**
- `src/api/electricity_adapters.py`
  - `get_hourly_from_porssisahko` – **B (9)**
- `src/api/electricity_sources.py`
  - `filter_latest_to_day` – **B (6)**
- `src/api/weather_utils.py`
  - `cloud_icon_from_cover` – **B (7)**
- `src/api/wmo_map_loader.py`
  - `_read_wmo_mapping` – **B (7)**
- `src/ui/card_heos.py`
  - `card_heos` – **B (10)**
- `src/ui/card_weather.py`
  - `card_weather` – **B (9)**
- `src/ui/card_zen.py`
  - `card_zen` – **B (8)**
- `src/ui/card_nameday.py`
  - `_get_sun_times` – **B (7)**
- `src/ui/card_nameday_helpers.py`
  - `get_flag_info` – **B (6)**
- `src/ui/card_prices.py`
  - `_current_price_15min` – **B (7)**

Näihin ei tarvitse tehdä erillistä refaktorointikierrosta, ellei funktiota muutenkin jouduta avaamaan.

---

## 2. Mitä on jo tehty

### 2.1 Sähkön hinta

**Tavoite** oli: *UI-kortti B/C-tasolle, normalisointi selkeästi kommentoiduksi C-tasoksi, palvelukerros ilman muunnoksia.*

Tehty:

1. **Normalisointi 3 vaiheeseen** (`src/api/electricity_normalize.py`):

   - Parserit:
     - `_parse_cents_from_item`
     - `_parse_hour_from_item`
     - `_parse_ts_15min_from_item`
   - Normalisointi:
     - `parse_hourly_to_map`
     - `normalize_hourly_map`
   - Laajennus:
     - `expand_hourly_to_15min`
     - `normalize_prices_list`
     - `normalize_prices_list_15min`

   → Parseri `_parse_hour_from_item` on **C (12)**, mutta hyväksytään C-tasolla, koska tukee useita eri lähteitä. Muut liittyvät funktiot ovat A/B-tasoa.

2. **Palvelukerros ohueksi**: `src/api/electricity_service.py`

   - `try_fetch_prices_15min`, `try_fetch_prices`, `fetch_prices_for` tekevät vain:
     - lähdevalinnan
     - kutsun adaptereille
     - virheenkäsittelyn
   → kaikki A-tasoa, ei sisällä enää muunnoslogiikkaa.

3. **Adapterit erilleen**: `src/api/electricity_adapters.py` ja `src/api/electricity_sources.py`

   - Adapterit puhuvat kunkin palvelun API:a ja palauttavat raakadatasta normalisoitavan listan.
   - `get_hourly_from_porssisahko` on **B (9)**, mikä on hyväksyttävä taso monimutkaiselle HTTP/API-koodille, kunhan se pysyy erillään UI:sta.

4. **UI ja viewmodel** (sähkö)

   - Kortin laskenta on siirretty viewmodeliin (tunnit, 15 min -pisteet, nykyinen hinta, seuraavat 12 h jne.).
   - `src/ui/card_prices.py`:
     - `_current_price_15min` – **B (7)**
     - `_next_12h_15min` – **C (15)**
     - `card_prices` – **C (13)**

   → UI saa olla C, kunhan varsinainen data-/domain-logiikka on viewmodelissa. Seuraava kierros voi halutessa vielä keventää `_next_12h_15min`- ja `card_prices`-funktioita (ks. kohta 3.3).

### 2.2 Sää (forecast → dashboard)

1. **Datankeruun erottaminen**: `src/api/weather_fetch.py`

   - `fetch_forecast`, `fetch_current`, `fetch_alerts` – A-tasoa.
   - `fetch_weather_points` – **A (2)**: pääfunktio, joka kokoaa dashboardille sopivan rakenteen.

2. **Mapitus omaan apufunktioon**

   - `_map_hourly_to_dashboard` tekee nyt varsinaisen tunnittaisen payloadin muunnoksen → tämä on kasvanut **D (22)** tasolle, joten se on seuraava refaktorointikohde (ks. kohta 3.2).

3. **Viewmodel säälle**: `src/api/weather_viewmodel.py`

   - `build_weather_view` – **A (2)**, selkeä rajapinta UI:lle.

---

## 3. Mitä pitää vielä korjata Radonin perusteella

### 3.1 `src/api/calendar_nameday.py`

Radon:

- `_pick_today_name` – **C (20)**
- `fetch_holiday_today` – **C (12)**

Tavoite:

- pitää yksi paikka, joka ymmärtää eri nimipäiväformaattien rakenteet (flat vs nested),
- tehdä juhlapäivien logiikasta luettava ja testattava.

Ehdotus:

1. Pilko `_pick_today_name` vähintään kahteen apufunktioon:
   - esim. `_pick_flat_nameday(data, today)`,
   - `_pick_nested_nameday(data, today)`,
   - ja pieni funktio, joka yhdistää nämä ja palauttaa stringin (tai `None`).

2. `fetch_holiday_today`:
   - irrota päivämäärän valinta (“tänään vai fallback eiliselle tms.”) omaan funktioon,
   - ja pidä varsinaisen datarakenteen käsittely omassa apufunktiossa, joka ottaa sisään jo valitun päivän.

Tavoitetaso: **B** molemmille tai selkeästi rajattu **C**, jossa pääfunktio delegoi apufunktioille.

---

### 3.2 `src/api/weather_fetch.py::_map_hourly_to_dashboard` – D (22)

Tämä on tämän hetken selkein “liikaa yhdessä paikassa” -funktio.

Ehdotus:

1. Pura ajoitus- ja data-logiikka erilleen:
   - `*_build_time_axis(hourly_raw, tz_name)` → tuottaa listan `datetime`-pisteitä.
   - `*_build_point(row) / *_extract_point_fields(row)` → lukee yksittäiset arvot (lämpötila, tuuli, symboli jne.).

2. Pidä `_map_hourly_to_dashboard` vain “orkestrointina”:
   - looppi, joka käy läpi tuntirivit,
   - kutsuu apufunktioita,
   - kokoaa listan `{"ts": ..., "value": ...}`-tyyppisiä dicttejä.

Tavoitetaso: saada `_map_hourly_to_dashboard` B-tasolle, apufunktiot A/B.

---

### 3.3 `src/ui/card_prices.py` ja `src/ui/card_bitcoin_parts.py`

**Sähkökortti:**

- `_next_12h_15min` – **C (15)**
- `card_prices` – **C (13)**

Ehdotus:

1. Siirrä jäljellä oleva “liiketoimintalogiikka” viewmodeliin (esim. valmiit sarjat ja tekstit).
2. Jätä UI:hin vain:
   - otsikon ja väri-informaation valinta valmiista viewmodel-kentistä,
   - Plotlyn konfigurointi (layout, akselit, hover).

Samalla kannattaa varmistaa, että testit eivät enää importtaa `_next_12h_15min` suoraan UI:sta, vaan vastaavasta viewmodel-funktiosta.

**Bitcoin-kortti:**

- `get_btc_series_for_window` – **C (16)**
- `build_btc_figure` – **C (11)**

Ehdotus:

1. Pilko `get_btc_series_for_window`:
   - yksi funktio, joka valitsee ikkunan (päivä, viikko, kk),
   - toinen, joka tekee downsamplauksen / filtteröinnin.
2. `build_btc_figure`:
   - siirrä mahdollinen datan muotoilu viewmodel-tyyppiseen funktioon (esim. `get_btc_figure_vm(window)`),
   - jätä tähän vain Plotlyn figuurin rakentaminen.

---

### 3.4 `src/api/wmo_icon_map.py` ja `src/api/wmo_map_loader.py`

Radon:

- `wmo_to_icon_key` – **C (13)**
- `load_wmo_foreca_map` – **C (11)**

Ehdotus:

1. `wmo_to_icon_key`:
   - siirrä iso “if/elif/lookup”-logiikka erilliseen rakenteeseen (dict/map),
   - pidä funktio itsessään vain “haku + fallback”.

2. `load_wmo_foreca_map`:
   - erottele tiedostonluku, validointi ja transformaatio:
     - `_load_raw_mapping(path)`,
     - `_validate_mapping(raw)`,
     - `_normalize_mapping(raw)`.

Tavoite: saada molemmat **B-tasolle** tai hyväksyttävä, hyvin dokumentoitu **C**.

---

### 3.5 `src/api/weather_utils.py::safe_cast` – C (19)

`safe_cast` on util-funktio, joka tekee aika monta eri haaraa (bool/int/float/string).

Ehdotus:

1. Pilko tyyppikohtaisiin apufunktioihin, esim.:
   - `_cast_to_bool(value)`,
   - `_cast_to_int(value)`,
   - `_cast_to_float(value)`,

2. Pidä `safe_cast`-pääfunktio lyhyenä “dispatcina”, joka päättää mihin alafunktioon mennään.

Jos haluat pitää sen yhtenä funktionsa (C-taso on utilille ok), lisää reilusti kommentteja sekä doctest-tyyppisiä esimerkkejä, jotta logiikka on helposti tarkistettavissa.

---

## 4. Seuranta

Pidä tästä dokumentista kiinni näin:

1. Aja Radon säännöllisesti (sama komento kuin yllä).
2. Jos joku funktio putoaa B → C tai C → D, lisää se listaan kohtaan **1.1**.
3. Kun olet pilkkonut sen:
   - päivitä tämän dokumentin päivämäärä,
   - siirrä funktio kohtaan **1.2** tai poista listalta kokonaan, jos se meni A/B:hen.
4. Kun teet isomman refaktorointikierroksen (esim. nimipäivät, sää, bitcoin-kortti), lisää lyhyt kuvaus kohtaan **2. Mitä on jo tehty**, jotta kokonaiskuva säilyy.

---

**Viimeisin päivitys:** 2025-11-17
**Päivittäjä:** ChatGPT (päivitetty suoraan käyttäjän toimittamasta Radon-listasta)
