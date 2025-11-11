# REFACTORING.md

Refaktorointisuunnitelma – HomeDashboard
Päivitetty: 2025-11-09
Lähde: Radon CC -raportti (src/…-tiedostot), tehty refaktorointi (bitcoin, utils, sähkökortti)

Tämän dokumentin tarkoitus on pitää näkyvissä ne tiedostot ja funktiot, joissa monimutkaisuus on vielä koholla, sekä kirjata, mitä on jo tehty. Tavoitteena on, että UI-kortit renderöivät ja API-/viewmodel-taso kokoaa datan.

---

## 0. Mitä juuri korjattiin (2025-11-11)

- `src/ui/card_nameday.py` lakkasi toimimasta, koska aiempi koodi oletti moduulin `src.api.calendar_nameday`.
  **Korjaus:** lisättiin uusi tiedosto `src/api/calendar_nameday.py`, joka vain re-exporttaa `fetch_nameday_today`-funktion `src/api/nameday.py`:stä.
- Nimipäivädata ei löytynyt, koska projekti käyttää juurihakemiston tiedostoja `data/nimipaivat_fi.json` ja `data/pyhat_fi.json` (eri rakenne kuin aiemmin).
  **Korjaus:** uusi `src/api/nameday.py` tunnistaa suomalaisen kuukausirakenteen (`"marraskuu" -> "11" -> "Panu"`).
- UI-korttien export-lista ei vastannut enää todellista tilannetta.
  **Korjaus:** `src/ui/__init__.py` päivitettiin uudelleen.
- Sähkökortti poistui refaktoroinnin yhteydessä.
  **Korjaus:** `src/ui/card_prices.py` palautettiin commitista `eda6fbbf`, koska se oli viimeinen varmuudella toimiva versio.

---

## 1. Nykytila Radonin mukaan

Radon-raportin perusteella valtaosa projektista on nyt tasolla **A** ja **B**:

- **Hyvin kevyet / valmiit:**
  - `src/heos_client.py` – kaikki metodit A (3–4)
  - `src/logger_config.py` – A (3)
  - `src/paths.py` – A (1)
  - `src/utils.py` (jäljelle jäänyt osa) – A (2)
  - `src/api/http.py` – A (3–4)
  - `src/api/quotes.py` – A (2–4)
  - `src/api/weather.py` – A (1)
  - `src/ui/common.py` – A (1–2)
  - `src/ui/card_bitcoin.py` – A (3)

Näihin ei tarvita lisärefaktorointia nyt.

---

## 2. Jo tehdyt refaktoroinnit

### 2.1 Utilsin pilkkominen
**Tavoite:** poistaa “kaatopaikka”-tiedosto.

- [x] Luotu `src/utils_colors.py` ja siirretty:
  - `_color_by_thresholds` – A (5)
  - `_color_for_value` – A (1)
- [x] Luotu `src/utils_sun.py` ja siirretty:
  - `fetch_sun_times` – A (5)
  - `_sun_icon` – A (2)
- [x] Luotu `src/utils_net.py` ja siirretty:
  - `get_ip` – A (2)
- [x] Alkuperäinen `src/utils.py` sisältää nyt vain oikeasti yleiskäyttöiset utilit.

**Tulos:** utils ei ole enää monitoimitiedosto, ja Radonin pisteet ovat A-tasoa → ei jatkotoimia.

---

### 2.2 Bitcoin-API:n siistiminen
**Ongelma havaittu:** `_coingecko_market_chart(...)` oli liian iso ja teki sekä HTTP-pyynnön että muunnoksen.

**Toteutettu ratkaisu:** pilkottu kolmeen vaiheeseen.
- [x] HTTP-pyyntö omaksi funktioksi (`_get_coingecko_market_chart` – A (1))
- [x] Raakadatan prices-listan poiminta omaksi funktioksi (`_extract_coingecko_prices` – B (6))
- [x] Datan muuntaminen dashboard-muotoon omaksi funktioksi (`_to_dashboard_from_ms` / `_to_dashboard_from_unix` – A (4))

**Tulos Radonissa:**
- `src/api/bitcoin.py`
  - `_extract_cryptocompare_prices` – B (9)
  - `_extract_coingecko_prices` – B (6)
  - `_btc_market_chart` – A (5)
  - loput A (1–4)

**Johtopäätös:** bitcoin on nyt hyväksyttävällä tasolla, eikä vaadi lisäpilkkomista.

---

### 2.3 Sähkön hintakortin eriyttäminen
**Aiempi ongelma:** `src/ui/card_prices.py` sisälsi sekä laskennan (seuraavat 12 h / 15 min) että UI:n.

**Toteutettu ratkaisu:**
- [x] Laskentalogiikka siirretty erilliseen moduuliin: `src/api/electricity_viewmodel.py`
  - siellä nyt mm. `_next_12h_15min - C (15)`
  - ja `_current_price_15min - B (7)`
  - sekä `build_electricity_12h_view - A (3)`
- [x] `src/ui/card_prices.py` jättää vain kortin piirtämisen valmiilla viewmodelilla.

**Tulos:** UI-tiedosto on kevyempi, ja monimutkaisuus “saa” nyt olla viewmodelissa, koska se tekee oikeaa työtä.

---

### 2.4 Sähkön hakujen pilkkominen
**Toteutettu:**
- [x] `src/api/electricity_sources.py` – kaikki yksittäiset lähdehaut A–B
- [x] `src/api/electricity_service.py` – koonti ja fallbackit
- [x] `src/api/electricity_normalize.py` – normalisointi ja 15 min -laajennus
- [x] `src/api/electricity_log.py` – lokitus

**Tulos Radonissa:**
- Lähdehaut: A (3–4)
- Palvelufunktiot: yksi C (13)
- Normalisointi: yksi C (13) ja yksi C (12)

---

## 3. Jäljellä olevat hotspotit

Nämä ovat ne, joissa Radon näyttää **C–D** ja jotka kannattaa seuraavaksi pilkkoa. Järjestys on tarkoituksella konkreettinen.

### 3.1 `src/ui/card_nameday.py` – **tärkein**
- Radon: `card_nameday - D (30)`
- Tämä on selvästi liian iso UI-funktio.
- **Tavoite:** kortti saa vain renderöidä, ei päättää monimutkaisia “tänään on sekä pyhä että nimipäivä” -tiloja.
- **Uusi huomio (2025-11-11):** kortti ei saa näyttää pyhä-/liputuspäivän debug-tekstiä jos päivälle ei ole merkintää → tämä on nyt toteutettu UI:ssa.

**Toimenpiteet:**
1. Tee sisäinen viewmodel-funktio, esim. `_nameday_viewmodel()` joka palauttaa kaiken kortin tarvitsemana datana.
2. Tee erillinen renderöintifunktio, esim. `_render_nameday_content(vm)` joka tekee HTML/Streamlitin.
3. Pidä `card_nameday(...)` vain koordinoivana.

**Valmis, kun:** `card_nameday` tippuu C- tai B-tasolle.

---

### 3.2 `src/api/electricity_normalize.py`
- Radon:
  - `normalize_prices_list_15min - C (13)`
  - `parse_hour_from_item - C (12)`
  - `normalize_prices_list - B (9)`

**Mitä täältä kannattaa erottaa:**
- syötteen rakenteen tunnistus (eri lähteet)
- 60→15 min -laajennus
- puuttuvien arvojen/fallbackien käsittely

Eli yksi funktio yksi vastuu. Nyt se tekee kolmea.

---

### 3.3 `src/api/electricity_service.py`
- Radon: `fetch_prices_for - C (13)`

**Toimenpide:**
- tee funktiosta pelkkä orkestrointi:
  - yritä 15 min (`try_fetch_prices_15min`)
  - jos epäonnistuu → tuntidata (`try_fetch_prices`)
  - normalisoi
- jätä yksityiskohdat jo olemassa oleville pienemmille funktioille

---

### 3.4 `src/api/calendar_nameday.py`
- Radon: `fetch_nameday_today - C (20)`
- Tämä on sama ketju kuin UI-puolella: päivämäärän ratkaisu, datalähteen valinta ja lopputuloksen muotoilu ovat yhdessä.

**Toimenpide:**
1. hae “raw” nimipäivädata tälle päivälle
2. muunna se dashboardin käyttämään muotoon
3. palauta valmis rakenne

→ API-taso pysyy lyhyenä, ja samalla UI-taso kevenee.

---

### 3.5 Viewmodelin jatkojalostus
`src/api/electricity_viewmodel.py` → `_next_12h_15min - C (15)`

**Toimenpide (valinnainen):**
- erottele “aikajakson muodostus” ja “UI:lle sopiva lista”
- näin viewmodel pysyy muutettavana ilman että CC nousee uudestaan

---

## 4. Hyväksytty monimutkaisuus

On muutama kohta, joissa C-luokka on hyväksyttävissä, koska ne käsittelevät luonnostaan monimutkaista dataa:

- `src/api/weather_fetch.py` → `fetch_weather_points - C (16)`
- `src/api/weather_mapping.py` → `wmo_to_icon_key - C (13)`
- `src/api/weather_utils.py` → `as_bool - C (14)`
- `src/api/calendar_holiday.py` → `fetch_holiday_today - C (13)`

**Periaate:** näitä ei tarvitse pilkkoa heti, ellei niihin lisätä uusia haaroja tai uusia datalähteitä.

---

## 5. Valmis / ei lisätoimia

Nämä tiedostot/funktiot ovat Radonin mukaan A–B ja ovat jo riittävän yksinkertaisia:

- `src/heos_client.py` (kaikki metodit A)
- `src/logger_config.py`
- `src/paths.py`
- `src/utils_*.py` (colors, sun, net)
- `src/api/http.py`
- `src/api/quotes.py`
- `src/api/bitcoin.py` (pilkottu)
- `src/ui/common.py`
- `src/ui/card_bitcoin.py`

---

## 6. Seurantalista

- [x] Utils jaettu domain-kohtaisiin tiedostoihin
- [x] Bitcoin-API pilkottu: HTTP → poiminta → muunto
- [x] Sähkön hintakortin laskenta siirretty omaan viewmodeliin
- [x] Sähkökortti palautettu vanhasta toimivasta commitista (2025-11-11)
- [x] Nimipäivä-API korjattu lukemaan `data/nimipaivat_fi.json`
- [ ] Nimipäiväkortin (`src/ui/card_nameday.py`) varsinainen pilkkominen pienempiin funktioihin
- [ ] Sähkön normalisoinnin (2 kpl C-luokan funktioita) pilkkominen
- [ ] Nimipäivä-API:n keventäminen (nyt toimii, mutta voisi olla 2-vaiheinen)

Kun yllä olevat kolme kohtaa on tehty, projektin näkyvimmät D- ja C-luokan funktiot poistuvat ja koodi on tasalaatuista.
