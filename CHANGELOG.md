# 📜 Changelog

Kaikki merkittävät muutokset tähän projektiin dokumentoidaan tähän tiedostoon.
Tiedosto noudattaa [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) -periaatetta ja versiointi perustuu [Semantic Versioning](https://semver.org/spec/v2.0.0.html) -käytäntöön.

---

## [Unreleased]

### Lisätty
- 🧪 HEOS-kortille (`card_heos`) kattavat yksikkötestit:
  - Soivan kappaleen renderöinti (song / artist / album)
  - Tyhjätila (“Ei HEOS-toistoa käynnissä”)
  - Ohjauspainikkeet (⏮, ⏯, ⏭) ja niiden kutsumat `HeosClient`-metodit
- 🧪 Mock-Streamlit (`DummySt`) jossa on sarake- ja context manager -tuki, jotta Streamlitin käyttäytyminen voidaan simuloida luotettavasti

### Muutettu
- 🎧 `card_heos` käyttää nyt selkeää, yksinkertaista rajapintaa: `HeosClient.get_now_playing()` palauttaa litteän sanakirjan, ei sisäkkäisiä rakenteita
- 🎧 HEOS-kortin sisäinen koodi siivottu vastaamaan uusia testejä ja poistettu vanhentunut tila- ja mute-logiikka

### Korjattu
- 🟢 Kaikki HEOS-kortin testit menevät nyt läpi (3 aiempaa epäonnistunutta testiä korjattu)
- 📈 Testikattavuus nousi 72 % → **73 %**

### Muutettu
- 📅 Nimipäivälogiikka on siirretty erilliseen `src/api/calendar_nameday.py` -moduuliin ja pilkottu pienempiin apufunktioihin, jotta datan luku, päivämäärävalinta ja nimen poiminta ovat selkeästi erillään. `fetch_nameday_today()` toimii nyt ohuena julkisena rajapintana.
- 📅 `card_nameday()` on refaktoroitu käyttämään uutta `calendar_nameday`-rajapintaa ja viewmodel-kerrosta, jolloin kortin vastuualue rajoittuu nimipäivä- ja pyhäpäivädatan esittämiseen.
- ₿ Bitcoin-kortin (`card_bitcoin`) sisäinen logiikka on siivottu käyttämään erillistä viewmodelia, joka kapseloi hinnan, prosenttimuutoksen ja virheviestit korttia varten.

### Korjattu
- 📅 Nimipäivä- ja pyhäpäivähaun regressiot refaktoroinnin jälkeen: `calendar_nameday` palauttaa nyt odotetut nimet sekä “flat” että sisäkkäisistä JSON-rakenteista ja nimipäiväkortin testit (mm. `test_fetch_nameday_today_*`, `test_fetch_holiday_today_*` sekä wrapper-testit) menevät läpi.
- ⚡ Sähkön hintakortti (`card_prices()`) on palautettu toimivaan tilaan ja sovitettu nykyiseen kortti-/viewmodel-rakenteeseen, jotta spot-hinnat näkyvät taas oikein eikä UI riipu enää vanhoista apufunktioista.
- 🧱 `src/ui/__init__.py` on päivitetty vastaamaan nykyistä korttivalikoimaa, joten `main.py`-importit eivät enää kaadu UI-refaktorointien seurauksena.

### Lisätty
- 🧪 Uusia yksikkötestejä nimipäivämoduulille (`calendar_nameday`) ja nimipäiväkortille; testit kattavat sekä JSON-lista- että dict-muotoiset nimipäivä- ja pyhäpäivälähteet ja varmistavat vakauden refaktoroinnin jälkeen.
- 🧪 Yksikkötestit Bitcoin-kortille, mukaan lukien virhepolut (esimerkiksi tilanteet, joissa API palauttaa puuttuvan hinnan tai muuten virheellistä dataa).
- 📄 `docs/CARD_NAMEDAY.md` dokumentoimaan nimipäiväkortin datalähteen ja polut.

---

## [1.0.0] – 2025-11-06
### 🎉 Ensimmäinen julkinen julkaisu

**Kotidashboard** on Streamlit-pohjainen kotinäyttö, joka kokoaa arjen keskeiset tiedot yhteen näkymään.

#### Lisätyt ominaisuudet
- ⚡ Sähkön hinta (porssisahko.net / sahkonhintatanaan.fi)
- ☀️ Sää Open-Meteosta (lämpötila, sademäärä, pilvisyys, ikoni)
- ₿ Bitcoinin hinta CoinGeckosta
- 📅 Nimipäivät ja pyhät
- 🧘 Zen-kortti satunnaisella mietelmällä ja taustakuvalla
- 🖥️ Järjestelmäkortti (CPU, RAM, levytila)
- 💾 Lokitus tiedostoon `logs/homedashboard.log`
- 🎨 Mukautettu tumma teema ja taustakuvat `assets/`-kansiosta
- 🔄 Automaattinen päivitys ja välimuisti

#### Rakenne ja teknologia
- Uusi hakemistorakenne (`src/`, `assets/`, `data/`, `docs/`, `scripts/`, `logs/`)
- Python 3.13 + Streamlit + Plotly + Mermaid
- Käyttö Windowsissa ja Raspberry Pi 5:llä
- MIT-lisenssi

---

## [Unreleased]
### 🧩 Tulevat muutokset
- 🌤️ Laajennettu sääennuste (3 vrk)
- 🏠 Sähkönkulutuksen oman historian näyttö
- 🪴 Kotiautomaatiointegraatiot (Home Assistant)
- ⚙️ Käyttöliittymän teemat (light / dark switch)

---

© 2025 Pekko Vehviläinen  |  [MIT License](LICENSE)
