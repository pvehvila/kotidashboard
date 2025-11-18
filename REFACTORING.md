# 🧩 REFACTORING.md – HomeDashboard

Tämä dokumentti pitää kasassa ne kohdat, joissa koodi vielä rikkoo meidän tavoitetta “A/B-taso mahdollisimman monessa paikassa”. Alla on uusin Radon-ajon yhteenveto (**2025-11-18**) ja siitä johdettu refaktorointijono.

Komento:

```bash
radon cc -s \\src .
```

---

## 1. Uusin Radon-löydös (2025-11-18)

### 1.1 Aktiivinen refaktorointilista (C-taso, joita halutaan vielä keventää)

Kaikki vanhat D-tason funktiot on saatu pois ja suurin osa aiemmista C-tason kohteista on nyt A/B-tasolla (nimipäivät, säät, WMO-icon-key). Jäljellä olevat “oikeat” refaktorointikohteet:

- **src/api/weather_utils.py**
  - `safe_cast` – **C (11)**

- **src/api/wmo_map_loader.py**
  - `load_wmo_foreca_map` – **C (11)**

Näihin kohdistetaan seuraavat refaktorointikierrokset.

---

### 1.2 Hyväksytyt C:t (toleranssi)

Nämä ovat funktioita, joissa C-taso on toistaiseksi hyväksytty, kunhan koodi on selkeästi kommentoitu ja rajapinnat ovat siistit.

- **src/api/electricity_normalize.py**
  - `_parse_hour_from_item` – **C (12)**

- **src/api/weather_debug.py**
  - `card_weather_debug_matrix` – **C (13)**

- **src/api/prices_15min_vm.py**
  - `next_12h_15min` – **C (15)**
  - `build_prices_15min_vm` – **C (12)**

---

## 2. Mitä on jo tehty

### 2.1 Sähkön hinta – normalisointi ja palvelukerros

**Tavoite:** UI-kortti B/C-tasolle, normalisointi selkeästi kommentoiduksi C-tasoksi, palvelukerros ilman muunnoksia.

**Tehty:**

1. **Normalisointi 3 vaiheeseen** – `src/api/electricity_normalize.py`

   - Parserit: `_parse_cents_from_item`, `_parse_hour_from_item`, `_parse_ts_15min_from_item`
   - Normalisointi: `parse_hourly_to_map`, `normalize_hourly_map`
   - Laajennus: `expand_hourly_to_15min`, `normalize_prices_list`, `normalize_prices_list_15min`

2. **Palvelukerros ohueksi** – `src/api/electricity_service.py`

   Vain lähdevalinta + virheenkäsittely.

3. **Adapterit erilleen** – `src/api/electricity_adapters.py` & `src/api/electricity_sources.py`

---

### 2.2 Sähkön 15 min viewmodel + UI

- **Viewmodel:** `src/api/prices_15min_vm.py`
  - `current_price_15min` – B
  - `next_12h_15min` – C (hyväksytty, kunhan kommentit kunnossa)
  - `build_prices_15min_vm` – C (hyväksytty, kunhan kommentit kunnossa)

- **UI:** `src/ui/card_prices.py`
  - Wrapperit testien yhteensopivuuteen
  - `card_prices` – B

---

### 2.3 Bitcoin-kortti – datasarjat ja figuuri

- Datasarjojen haku pilkottu: `_try_fetch_series_for_window`, `_build_24h_from_7d`, `_fallback_7d`
- UI-palaset: `build_window_pill`, `build_title_html`, `build_footer_html`
- Viewmodel figuurille: `get_btc_figure_vm`, `BtcFigureVM`, `_y_axis_range`
- Varsinainen figuuri: `build_btc_figure` – B

---

### 2.4 Sää (forecast → dashboard)

- `fetch_forecast` / `fetch_current` / `fetch_alerts` – A-tasoa
- `fetch_weather_points` – A-tasoa
- `_map_hourly_to_dashboard` – **nyt B (8)**, aiempi C-tason orkestrointifunktio on pilkottu:
  - aikajanan rakennus → `_build_time_axis` (B)
  - indeksin rakennus → `_build_time_index` (A)
  - yksittäisen rivin muunnos → `_extract_point_fields` (B)
  - pisteen dict-rakenne → `_build_point` (A)

Refaktorointitavoite (C → B) saavutettu.

---

### 2.5 Nimipäivät

**Tavoite oli** purkaa monoliittinen nimipäivälogiikka erillisiksi vaiheiksi (datan lataus, arvon normalisointi, flat/nested-haut, pyhät).

Uusin Radon:

- **src/api/calendar_nameday.py**
  - `_normalize_nameday_value` – B (7)
  - `_pick_today_name_nested` – B (7)
  - `_parse_holiday_entry` – B (9)
  - `_pick_holiday_entry_for_today` – B (9)
  - `_pick_today_name_flat` – A (3)
  - `_pick_today_name` – A (3)
  - `fetch_nameday_today` – A (3)
  - `fetch_holiday_today` – A (5)
  - `_resolve_nameday_file`, `_resolve_first_existing`, `_load_nameday_data`, `_default_holiday_result` – A

**Refaktorointitavoite saavutettu:** Ei enää C-tason funktioita nimipäivämoduulissa.

---

### 2.6 WMO-mappaus

**Aiempi tavoite:** erottaa tiedostonluku, validointi ja transformaatio, sekä yksinkertaistaa WMO → ikonitunnus -logiikka.

Tilanne nyt:

- **src/api/wmo_icon_map.py**
  - `wmo_to_icon_key` – **A (4)**
    → Numerologinen käsittely siirretty selkeämpään map/dict-rakenteeseen; Radon-taso parantunut C → A.

- **src/api/wmo_map_loader.py**
  - `_read_wmo_mapping` – B (7)
  - `_scalar` – A (5)
  - `_prep` – A (3)
  - `load_wmo_foreca_map` – **C (11)**
    → Tämä on enää ainoa selkeä refaktorointikohde WMO-puolella.

---

## 3. Seuraavat refaktorointikierrokset

### 3.1 Nimipäivät

**Tila:** ✅ **Valmis Radonin näkökulmasta** (ei C/D-tason funktioita).

- Mahdolliset jatkokehitykset koskevat lähinnä domain-logiikan jalostamista (esim. konfiguroitavat nimipäivälähteet, fallback-strategiat), eivät kompleksisuuden purkua.

---

### 3.2 Sää: `_map_hourly_to_dashboard`

**Tila:** ✅ **Valmis** – funktio on nyt B (8) ja vastaa puhdasta orkestrointia.

- Aikajanan muodostus: `_build_time_axis`
- Indeksit ja pisteet: `_build_time_index`, `_extract_point_fields`, `_build_point`
- Päiväkohtaisten min/max-arvojen laskenta: `_compute_day_minmax` – B (6)

Ei uutta refaktorointitarvetta, kunhan rakenne pidetään ennallaan.

---

### 3.3 `safe_cast` (TODO)

**Tila:** 🔧 **Aktiivinen refaktorointikohde**

- **Moduuli:** `src/api/weather_utils.py`
  - `safe_cast` – C (11)
  - `_cast_to_bool` – B (7)
  - `_cast_to_float` – A (3)
  - `_cast_to_int` – A (3)

**Tavoite:**

- Pitää `safe_cast` mahdollisimman ohuena dispatcherina.
- Pitää yksityiset `_cast_*`-funktiot selkeästi ja eriyttää eri tyyppien haarat, jotta `safe_cast` ei ala taas paisua.

**Ehdotettu suunta:**

- Varmista, että
