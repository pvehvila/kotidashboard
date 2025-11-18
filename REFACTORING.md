# 🧩 REFACTORING.md – HomeDashboard

Tämä dokumentti pitää kasassa ne kohdat, joissa koodi vielä rikkoo meidän tavoitetta “A/B-taso mahdollisimman monessa paikassa”. Alla on uusin Radon-ajon yhteenveto (**2025-11-18**) ja siitä johdettu refaktorointijono.

Komento:

```bash
radon cc -s \src .
```

---

## 1. Uusin Radon-löydös (2025-11-18)

### 1.1 Aktiivinen refaktorointilista (C-taso, joita halutaan vielä keventää)

Kaikki vanhat D-tason funktiot on saatu pois ja suurin osa aiemmista C-tason kohteista on nyt A/B-tasolla (nimipäivät, säät, WMO-icon-key, WMO-map loader, `safe_cast`).
**Uusimman Radon-ajon perusteella ei ole enää pakollisia refaktorointikohteita:** kaikki jäljellä olevat C-tason funktiot on siirretty kohtaan 1.2 “Hyväksytyt C:t”.

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
  - `next_12h_15min` – C
  - `build_prices_15min_vm` – C

- **UI:** `src/ui/card_prices.py`
  - Wrapperit testien yhteensopivuuteen
  - `card_prices` – B

---

### 2.3 Bitcoin-kortti – datasarjat ja figuuri

- Datasarjojen haku pilkottu:
  - `_try_fetch_series_for_window`
  - `_build_24h_from_7d`
  - `_fallback_7d`
- UI-palaset:
  - `build_window_pill`
  - `build_title_html`
  - `build_footer_html`
- Viewmodel:
  - `get_btc_figure_vm`, `BtcFigureVM`, `_y_axis_range`
- Figuuri:
  - `build_btc_figure` – B

---

### 2.4 Sää (forecast → dashboard)

- `fetch_forecast` / `fetch_current` / `fetch_alerts` – A
- `fetch_weather_points` – A
- `_map_hourly_to_dashboard` – **B (8)**

Pilkkoutunut:

- `_build_time_axis` – B
- `_build_time_index` – A
- `_extract_point_fields` – B
- `_build_point` – A
- `_compute_day_minmax` – B

**Tavoite saavutettu.**

---

### 2.5 Nimipäivät

Kaikki C- ja D-tason funktiot poistettu.

Keskeiset funktiot:

- `_normalize_nameday_value` – B
- `_pick_today_name_nested` – B
- `_parse_holiday_entry` – B
- `_pick_holiday_entry_for_today` – B
- `_pick_today_name_flat` – A
- `_pick_today_name` – A
- `fetch_nameday_today` – A
- `fetch_holiday_today` – A

**Moduuli valmis.**

---

### 2.6 WMO-mappaus

- `wmo_to_icon_key` – **A (4)**
- `read_raw_wmo_mapping` – B
- `_scalar` – A
- `_normalize_cell` – A
- `build_wmo_foreca_maps` – B
- `load_wmo_foreca_map` – A

**Tavoite: tiedostonluku → validointi → transformaatio – saavutettu.**

---

### 2.7 `safe_cast` ja `weather_utils`

- `_cast_to_bool` – B
- `_normalize_scalar` – B
- `cloud_icon_from_cover` – B
- `safe_cast` – B
- `_cast_to_float` – A
- `_cast_to_int` – A
- `as_bool`, `as_int`, `as_float` – A

**Tavoite saavutettu:** safe_cast on ohut dispatcher.

---

## 3. Seuraavat refaktorointikierrokset

### 3.1 Nimipäivät

**Valmis.** Mahdolliset jatkokehitykset eivät koske kompleksisuutta.

---

### 3.2 Sää: `_map_hourly_to_dashboard`

**Valmis**, kunhan ei laajene.

---

### 3.3 `safe_cast` ja apurit

**Valmis.** Mahdollinen jatko: docstringit ja tyypit.

---

### 3.4 Hyväksytyt C-tason funktiot (ei kiireellisiä)

1. `_parse_hour_from_item` – C
2. `card_weather_debug_matrix` – C
3. `next_12h_15min` – C
4. `build_prices_15min_vm` – C

Voidaan pilkkoa myöhemmin, jos logiikka kasvaa.

---

**Nykytila:**
Refaktorointitarve on Radon-mielessä **erittäin hyvä**, lähes kaikki logiikka A/B-tasoilla.
