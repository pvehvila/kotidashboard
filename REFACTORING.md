# Refaktorointisuunnitelma

Tämä dokumentti kuvaa HomeDashboard-projektin tämänhetkisen koodin rakenteesta nousseet selkeät refaktorointikohteet. Lähteenä on käytetty rivimääräanalyysia (project_metrics.ps1) sekä radon-kompleksisuusraporttia.

Tavoitteet:
- pienentää yksittäisten moduulien (erityisesti `api/` ja `ui/`) kokoa
- erottaa domain-logiikka (API-haku, normalisointi) käyttöliittymästä
- helpottaa testausta pilkkomalla pitkät funktiot erillisiin, puhtaisiin apufunktioihin

---

## 1. `src/api/weather.py` (540 riviä)

**Ongelma:** sama tiedosto sisältää sekä säädatan haun, WMO/Foreca-mäppäyksen että debug-näkymän.

**Toimenpiteet:**

- [ ] Luo uusi tiedosto `src/api/weather_fetch.py` ja siirrä sinne:
  - `fetch_weather_points(...)`
  - muut ulkoiset rajapintakutsut
- [ ] Luo uusi tiedosto `src/api/weather_mapping.py` ja siirrä sinne:
  - `_load_wmo_foreca_map(...)`
  - `_read_wmo_mapping(...)`
  - `wmo_to_icon_key(...)`
  - `wmo_to_foreca_code(...)`
- [ ] Luo tarvittaessa `src/api/weather_utils.py` ja siirrä sinne pienet muunnosfunktiot:
  - `_as_bool(...)`
  - `_as_float(...)`
  - `_as_int(...)`
- [ ] Siirrä `card_weather_debug_matrix(...)` joko erilliseen `weather_debug.py` -tiedostoon tai jätä vain kehityskäyttöön.

**Valmis, kun:** varsinainen `weather.py` sisältää enää “orkestroivan” tason, ja yksittäiset osat ovat alle ~150 riviä kukin.

---

## 2. `src/api/electricity.py` (386 riviä)

**Ongelma:** sama tiedosto hoitaa lähdekohtaiset haut, normalisoinnin (tunti → 15 min) ja lokituksen.

**Toimenpiteet:**

- [ ] Luo `src/api/electricity_sources.py` ja siirrä sinne:
  - `_fetch_from_porssisahko(...)`
  - `_fetch_15min_from_porssisahko_v2(...)`
  - `_fetch_from_sahkonhintatanaan(...)`
- [ ] Luo `src/api/electricity_normalize.py` ja siirrä sinne:
  - `_normalize_prices_list_15min(...)` **(C 13)**
  - `_normalize_prices_list(...)`
  - `_expand_hourly_to_15min(...)`
  - `_parse_hour_from_item(...)` **(C 12)**
  - `_parse_cents_from_item(...)`
- [ ] Luo `src/api/electricity_service.py` ja siirrä “public”-funktiot:
  - `try_fetch_prices_15min(...)`
  - `try_fetch_prices(...)`
  - `fetch_prices_for(...)`
- [ ] Siirrä `_log_raw_prices(...)` erilliseen debug/logi -tiedostoon.

**Valmis, kun:** yksittäinen tiedosto ei sisällä sekä API-kutsua että 15 min -normalisointia samassa.

---

## 3. `src/ui/card_bitcoin.py` (281 riviä) – **radon: D (27)**

**Ongelma:** kortti tekee liikaa: hakee dataa, muotoilee ja piirtää UI:n.

**Toimenpiteet:**

- [ ] Jätä `card_bitcoin(...)` vain Streamlit-/UI-rakenteelle.
- [ ] Siirrä datan muotoilu erilliseen tiedostoon, esim. `src/ui/card_bitcoin_parts.py`:
  - hinnan formatointi
  - prosenttimuutokset
  - mahdollinen historiadata, jos sitä näytetään
- [ ] Varmista, että varsinainen datan haku pysyy `src/api/bitcoin.py`:ssä.

**Valmis, kun:** varsinainen korttifunktio on noin 50–80 riviä ja kutsuu selkeitä apufunktioita.

---

## 4. Nimipäiväketju: `src/api/calendar.py` ja `src/ui/card_nameday.py`

**Havainnot:**
- `fetch_nameday_today` → **D (23)**
- `card_nameday` → **D (29)**

**Toimenpiteet:**

- [ ] Jaa `src/api/calendar.py` kahteen tai kolmeen tiedostoon:
  - `calendar_data.py` → tiedoston resolvoinnit, `_resolve_nameday_file(...)`, `_resolve_first_existing(...)`, `_load_json(...)`
  - `calendar_nameday.py` → `fetch_nameday_today(...)`
  - `calendar_holiday.py` → `fetch_holiday_today(...)`
- [ ] Jaa `src/ui/card_nameday.py` kahteen funktioon:
  - `card_nameday(...)` → UI-rakenne
  - `_render_nameday_block(...)` → datan esitys

**Valmis, kun:** kumpikaan funktio ei ole D-tason monimutkaisuutta.

---

## 5. `src/ui/card_prices.py` (199 riviä)

**Ongelma:** kortti sisältää sekä laskentaa (seuraavat 12h / 15 min) että UI:n.

**Toimenpiteet:**

- [ ] Siirrä laskentalogiikka, kuten `_next_12h_15min(...)` **(C 15)**, erilliseen moduuliin esim. `src/api/electricity_viewmodel.py`
- [ ] Jätä tähän tiedostoon vain kortin piirtäminen.

**Valmis, kun:** kortti saa valmiin “viewmodelin” ja ainoastaan renderöi sen.

---

## 6. `src/utils.py` (184 riviä)

**Ongelma:** yleinen “kaatopaikka”.

**Toimenpiteet:**

- [ ] Luo `src/utils_colors.py` ja siirrä:
  - `_color_by_thresholds(...)`
  - `_color_for_value(...)`
- [ ] Luo `src/utils_sun.py` ja siirrä:
  - `fetch_sun_times(...)`
  - `_sun_icon(...)`
- [ ] Luo `src/utils_net.py` ja siirrä:
  - `get_ip(...)`

**Valmis, kun:** alkuperäinen `utils.py` sisältää vain oikeasti yleiskäyttöiset utilit.

---

## 7. `src/api/bitcoin.py`

**Havainto:** `_coingecko_market_chart(...)` → **C (15)**

**Toimenpiteet:**

- [ ] Pilko kolmeen osaan:
  1. HTTP-pyyntö
  2. raakadatasta `prices`-listan poiminta
  3. datan muuntaminen dashboardin käyttämään muotoon

**Valmis, kun:** yksikään funktio ei tee sekä pyyntöä että muunnosta.

---

## 8. Yleinen sääntö jatkoon

- [ ] Aja `.\project_metrics.ps1` aina ison refaktoroinnin jälkeen.
- [ ] Jos radon cc näyttää **C** tai **D**, pilko funktio.
- [ ] Pidä `api/`-kansio niin, että:
  - ulkoiset haut = oma tiedosto
  - normalisointi/mapping = oma tiedosto
  - debug/testi = oma tiedosto

---

## Seuranta

- [ ] 1: `api/weather.py` pilkottu
- [ ] 2: `api/electricity.py` pilkottu
- [ ] 3: `ui/card_bitcoin.py` kevennetty
- [ ] 4: kalenteri/nimipäiväketju eroteltu
- [ ] 5: hintakortin laskentalogiikka siirretty
- [ ] 6: utils jaettu domainin mukaan
- [ ] 7: bitcoin-haku jaettu kolmeen vaiheeseen
