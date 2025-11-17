# 🧩 REFACTORING.md – HomeDashboard

Tämä dokumentti pitää kasassa ne kohdat, joissa koodi vielä rikkoo meidän tavoitetta “A/B-taso mahdollisimman monessa paikassa”. Alla on uusin Radon-ajon yhteenveto (**2025-11-17**) ja siitä johdettu refaktorointijono.

Komento:

```bash
radon cc -s \src .
```

---

## 1. Uusin Radon-löydös (2025-11-17)

### 1.1 Aktiivinen refaktorointilista (C-taso, joita halutaan vielä keventää)

Nämä ovat ne, joita kannattaa vielä pilkkoa tai selkeyttää. Kaikki D-tason funktiot on jo saatu pois; jäljellä on vain C-tason kohtia.

- **src/api/calendar_nameday.py**
  - `_pick_today_name` – **C (20)**
  - `fetch_holiday_today` – **C (12)**

- **src/api/weather_fetch.py**
  - `_map_hourly_to_dashboard` – **C (14)**
    (aiemmin D-tasoa, nyt jo selvästi parempi, mutta yhä pitkä orkestrointifunktio)

- **src/api/weather_utils.py**
  - `safe_cast` – **C (19)**

- **src/api/wmo_icon_map.py**
  - `wmo_to_icon_key` – **C (13)**

- **src/api/wmo_map_loader.py**
  - `load_wmo_foreca_map` – **C (11)**

Näihin kannattaa kohdistaa seuraavat refaktorointikierrokset.

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

- Datasarjojen haku pilkottu: `_try_fetch_series_for_window`, `_build_24h_from_7d`, `_fallback_7d`
- UI-palaset: `build_window_pill`, `build_title_html`, `build_footer_html`
- Viewmodel figuurille: `get_btc_figure_vm`, `BtcFigureVM`, `_y_axis_range`
- Varsinainen figuuri: `build_btc_figure` – B

---

### 2.4 Sää (forecast → dashboard)

- **fetch_forecast/fetch_current/fetch_alerts**: A-tasoa
- **fetch_weather_points**: A-tasoa
- **_map_hourly_to_dashboard**: C (aktiivinen refaktorointikohde)
- **build_weather_view**: A

---

## 3. Seuraavat refaktorointikierrokset

### 3.1 Nimipäivät

- Pilko `_pick_today_name` kahteen apufunktioon (flat/nested).
- Pilko `fetch_holiday_today` päivämäärävalintaan ja datarakenteen erottamiseen.

Tavoite: B-tasolle.

---

### 3.2 Sää: `_map_hourly_to_dashboard`

- Erottele ajan muodostus (`_build_time_axis`).
- Erottele yksittäisen rivin muunnos (`_extract_point_fields`).
- Tee pääfunktiosta vain orkestroija.

Tavoite: B-taso.

---

### 3.3 `safe_cast`

- Pilko `_cast_to_bool`, `_cast_to_int`, `_cast_to_float`.
- Tee `safe_cast` pelkäksi dispatcheriksi.

---

### 3.4 WMO-mappaus

- `wmo_to_icon_key`: siirrä tunnistenumeroiden käsittely map/dict-rakenteeseen.
- `load_wmo_foreca_map`: erota tiedostonluku / validointi / transformaatio.

---

## 4. Seuranta

1. Aja Radon säännöllisesti:

   ```bash
   radon cc -s \src .
   ```

2. Jos funktio heikkenee tasolle C/D, lisää se kohtaan **1.1**.
3. Refaktoroinnin jälkeen päivitä dokumentti.

---

**Viimeisin päivitys:** 2025-11-17
**Päivittäjä:** ChatGPT
