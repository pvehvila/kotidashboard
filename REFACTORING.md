# 🧩 REFACTORING.md – HomeDashboard

Tämä dokumentti kokoaa kaikki koodin rakenteeseen ja monimutkaisuuteen liittyvät refaktorointitarpeet. Dokumentti perustuu **uusimpaan Radon-analyysiin (2025-12-07)** sekä projektissa tehtyihin refaktorointeihin.

Päätavoitteena on pitää sovelluksen logiikka selkeänä, ylläpidettävänä ja mahdollisimman matalan kompleksisuuden tasolla (A/B). Jäljellä olevat C-tason funktiot ovat rajattuja, perusteltuja ja tällä hetkellä hyväksyttäviä.

---

## 1. Radon-yhteenveto (2025-12-07)

Uusin Radon-ajon tulos osoittaa, että **valtaosa koko projektista on A- ja B-tasolla**. Jäljellä olevat C-tason funktiot ovat luonteeltaan sellaisia, että niiden monimutkaisuuden vähentäminen ei tuo merkittävää hyötyä ilman laajempia muutoksia.

**Nykyisessä tilanteessa ei ole pakollista refaktorointitarvetta.**

---

## 2. Hyväksytyt C-tason funktiot

Seuraavat funktiot ovat C-tasolla, mutta ne ovat joko datan aggregointia, debug-käyttöön tarkoitettuja tai viewmodel-laskentaa, jonka monimutkaisuus on rajattua.

### 2.1 `src/api/electricity_normalize.py`
- `_parse_hour_from_item` – **C (12)**
  - Parsintalogiiikka on jo selkeästi rajattu. Pilkkominen edelleen ei toisi merkittävää hyötyä ilman laajempaa rakennemuutosta.

### 2.2 `src/api/weather_debug.py`
- `card_weather_debug_matrix` – **C (13)**
  - Debug-käyttöön tarkoitettu laaja matriisivisualisaatio. Ei vaikuta tuotantokoodin laatuun.

### 2.3 `src/api/prices_15min_vm.py`
- `next_12h_15min` – **C (15)**
- `build_prices_15min_vm` – **C (12)**
  - Viewmodelien rakentaminen vaatii useita vaiheita. Logiikka on testattu ja selkeästi rajattu.

---

## 3. Valmiit refaktorointikokonaisuudet

Merkittävimmät refaktoroinnit on jo toteutettu kaikilla osa-alueilla, joissa kompleksisuus aiemmin nousi liian korkeaksi.

### 3.1 Sähkönhintalogiikka
- Normalisointi ja parsinta erotettu omiin kerroksiinsa
- Selkeä kolmiportainen rakenne:
  1. **Parserit** (cents, hour, timestamp)
  2. **Normalisointi** (maps, lists)
  3. **Laajennus 60 → 15 min**
- Palvelukerros ohennettu ⇒ tekee vain lähdevalinnan ja virheenkäsittelyn

### 3.2 15 min sähkön hinta – viewmodelit
- `current_price_15min` B-tasolla
- Kaksi C-tason funktiota erotettu omiksi kokonaisuuksikseen ja selkeästi kommentoitu

### 3.3 Sää (Open-Meteo) → Dashboard
- `_map_hourly_to_dashboard` nyt **B (8)**
- Aikajanan rakentaminen, datan poiminta ja min/max-laskenta eriytetty omiin funktioihin
- Kokonaisuus on hyvin testattu ja ylläpidettävä

### 3.4 Nimipäivät ja pyhäpäivät
- Moduuli pilkottu kokonaan A/B-tasolle
- Rakenteet (flat / nested) normalisoidaan omissa apufunktioissa
- Testikattavuus yli 80 %

### 3.5 WMO-säätunnukset
- Kolmivaiheinen rakenne: tiedostonluku → validointi → transformaatio
- Kaikki funktiot A/B-tasolla

### 3.6 `safe_cast` ja `weather_utils`
- safe_cast toimii nyt ohuena dispatcherina
- Tyyppikohtainen logiikka omissa apufunktioissa
- Kokonaisuus on selkeä ja testattu

### 3.7 HEOS-, Hue Motion- ja Hue Doors -kortit
- API-rajapinnat kapseloitu
- Viewmodel-kerrokset erottavat datan muunnoksen UI-renderöinnistä
- Korkea testikattavuus (88–100 %)

---

## 4. Mahdolliset tulevat refaktorointikierrokset (ei kiireellisiä)

Näitä kannattaa harkita vasta, jos uudet ominaisuudet kasvattavat monimutkaisuutta.

### 4.1 15 min sähkönhintalogiikka
- `next_12h_15min` ja `build_prices_15min_vm` voidaan pilkkoa edelleen, jos logiikka laajenee.

### 4.2 Debug-näkymät
- `card_weather_debug_matrix` voidaan modularisoida, jos debug-paneeli laajenee.

### 4.3 Parsintafunktiot
- `_parse_hour_from_item` voidaan jakaa kahteen vaiheeseen (avaimen tulkinta / arvon muunnos), jos tarpeen.

---

## 5. Yhteenveto

Kokonaisuutena refaktoroinnin tila on **erittäin hyvä**:

- Suurin osa koodista on A/B-tasoilla
- Kaikki kriittiset osuudet ovat selkeitä, testattuja ja ylläpidettäviä
- Jäljellä olevat C-tason funktiot ovat hyväksyttävässä kunnossa
- Ei tarvetta välittömille muutoksille

Dokumentti päivitetään seuraavan kerran, kun uudet ominaisuudet tai Radon-tulokset antavat siihen aihetta.
