# Nimipäiväkortti (`card_nameday`)

Tämä kortti näyttää:

1. **Liputus- / pyhäpäivän** (jos löytyy)
2. **Nimipäivät tänään** (päivä suomeksi + päivämäärä)
3. **Nimet isolla**
4. **Auringonnousu- ja laskuajan**
5. **Taustakuvan** (perhonen)

Kortti on rakennettu samaan korttityyliin kuin muut dashboardin kortit (sama 180px korkeus ja `section.card` -rakenne), joten se istuu riviin muiden kanssa.

---

## 1. Datalähteet

### 1.1 Nimipäivät
- Haetaan funktiolla:
  ```python
  from src.api.calendar_nameday import fetch_nameday_today
  ```
- Funktio palauttaa päivän nimipäivät merkkijonona (esim. `"Panu"`, `"Martin ja Martti"`).
- Jos funktio palauttaa tyhjää, kortti näyttää viivan `—`.

### 1.2 Liputus- ja pyhäpäivät
- Kortti **etsii ensin tiedostoa** `data/pyhat_fi.json`.
- Tiedostoa etsitään “ylöspäin” nykyisestä hakemistosta, joten kortti toimii vaikka appi ajetaan `C:\HomeDashboard\src` -kansiosta.
- Jos tiedosto löytyy ja sieltä löytyy tämän päivän avain, kortti näyttää liputuspillerin.

**JSON-muoto:**

```json
{
  "2025-11-11": {
    "name": "Testipäivä",
    "flag": true
  },
  "2025-12-06": {
    "name": "Itsenäisyyspäivä",
    "flag": true
  }
}
```

- avain: `YYYY-MM-DD`
- `name`: kortissa näytettävä teksti
- `flag`: jos `true`, kortti näyttää Suomen lipun

> Jos avainta ei löydy, kortti ei kaadu – se näyttää vain nimipäivät ja auringon.

---

## 2. Näyttöjärjestys

Kortti piirtää asiat **tässä järjestyksessä**:

1. (jos löytyy) **Liputuspäivä** – ylhäällä, harmaalla pillillä, vasemmassa laidassa. Lipun kuvana pieni SVG-Suomen lippu, jotta se näkyy tummaa taustaa vasten.
2. “**Nimipäivät tiistaina 11.11.**” – pieni harmaa teksti
3. **Nimet** – isolla, paksulla
4. **Aurinkopillerit** – kaksi pientä, mustahkoa pilleriä alalaitaan: 🌅 nousu ja 🌇 lasku

Tämä järjestys on tehty siksi, että dashboardin kortti leikkaa sisältöä alhaalta → tärkein pitää olla ylhäällä.

---

## 3. Taustakuva

- Kortti yrittää ladata jonkin näistä:
  - `assets/butterfly-bg.png`
  - `assets/butterfly-bg.webp`
  - `assets/butterfly-bg.jpg`
- Ensimmäinen löytynyt koodataan base64:ksi ja käytetään `background-image`nä.
- Taustan päälle laitetaan tumma gradientti, jotta teksti erottuu.

Jos mitään noista ei löydy, kortti käyttää vain tummaa gradienttia.

---

## 4. Auringonnousu ja -lasku

- Kortti käyttää:
  ```python
  from src.utils import fetch_sun_times, _sun_icon
  ```
- Kutsu on muotoa:
  ```python
  sunrise, sunset = fetch_sun_times(LAT, LON, TZ.key)
  ```
- Jos jompikumpi puuttuu → näytetään `—`
- Ikoni tulee `_sun_icon('rise')` ja `_sun_icon('set')` -funktioista (inline-SVG).

---

## 5. Mitä pitää muistaa jos refaktoroi

1. **Älä siirrä liputusta kortin loppuun** – se peittyy helposti. Pidä se nimien ylä- TAI alapuolella, mutta ennen aurinkoja.
2. **Älä poista JSON-fallbackia** – tämä on nyt ainoa varma reitti, koska projektissa ei tällä hetkellä ole `src.api.calendar_flagday` -moduulia.
3. **Älä vaihda päivämäärän muotoa** kortissa, mutta jos vaihdat JSONissa, vaihda myös koodissa tämä rivi:
   ```python
   key = today.strftime("%Y-%m-%d")
   ```
4. Jos projekti joskus siirtyy niin, että data ei ole enää `/data/pyhat_fi.json` vaan vaikka `/api/pyhat_fi.json`, riittää että päivittää yhden pienen apufunktion (`_find_pyhat()`).

---

## 6. Pieni snippet JSONin lisäämiseen

Jos haluat lisätä huomisen lipun nopeasti:

```json
{
  "2025-11-12": {
    "name": "Testipäivä 2",
    "flag": true
  }
}
```

Tallenna, käynnistä dashboard uudelleen → kortti näyttää sen.
