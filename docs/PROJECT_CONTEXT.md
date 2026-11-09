# Kotidashboard – projektikonteksti ja siirtotarkistus

Päivitetty: 2026-11-08  
Tila: **osittainen siirto ChatGPT-projektista; ei vielä poistovalmiutta**

## Tarkoitus ja rajaus

Kotidashboard on Pythonilla ja Streamlitillä rakennettu kodin tietokoontinäyttö. Sovelluksen lähdekoodi, tekniset päätökset, testit ja dokumentaatio ylläpidetään tässä Git-repositoriossa. ChatGPT-keskustelut eivät ole ensisijainen dokumentaatiolähde.

Projektin sisältöön kuuluvat tietokortit (esimerkiksi sää, sähkö, Bitcoin, nimipäivät, siitepöly ja kuun vaihe), älykoti-integraatiot (esimerkiksi Home Assistant, HEOS ja Hue), käyttöliittymä, virheenkäsittely, testaus ja refaktorointi. Ajantasainen ominaisuusluettelo ja riippuvuudet on tarkistettava `README.md`- ja lähdekooditiedostoista.

**Rajaus:** yleinen käyttöjärjestelmien, Windows–Ubuntu-kaksoiskäynnistyksen ja laitteiston ylläpito kuuluu erilliseen Computers & Linux -kokonaisuuteen; kodin muut käytännön tarpeet Home & Living -kokonaisuuteen.

## Lähteet ja varmuustasot

- **Tarkistettu repositoriosta 2026-11-08:** `README.md` kuvaa Streamlit-käytön, kortit ja integraatiot. `AGENTS.md` sisältää koodausagentin rajatut ohjeet. `QUALITY.md` kuvaa Ruff-, Pytest-, Bandit- ja pre-commit-käytännöt. `scripts/update.sh` sisältää Raspberry Pi -päivitysmenettelyn.
- **Aiemmissa keskusteluissa raportoitu, ei nyt ajoalustalta varmennettu:** Raspberry Pi 5 -ajoympäristö, systemd-palvelu `kotidashboard`, portti `8787`, Windowsin ja Raspberry Pi:n Git-työnjako sekä Ubuntu/Windows-kaksoiskäynnistys.
- **Ei vielä läpikäyty:** ChatGPT-projektin kaikkia keskusteluja ja liitteitä; niiden kaikkia päätöksiä ei voi merkitä siirretyiksi tämän dokumentin perusteella.

## Työskentelyohjeet

1. Tarkista ensin oikea repository, haara, ajoalusta ja työpuun tila.
2. Erota sovelluksen lähdekoodimuutokset Home Assistantin, HEOSin, Huen ja käyttöjärjestelmän asetuksista.
3. Tee pienet, rajatut muutokset ja testaa vaikutus olemassa oleviin toimiviin kortteihin ja integraatioihin.
4. Älä tallenna API-avaimia, salasanoja, tunnisteita, paikallisia `.env`- tai secrets-tiedostoja eikä lokien arkaluonteisia sisältöjä Git-repositorioon.
5. Käytä Windowsissa ja Linuxissa erillisiä Python-virtuaaliympäristöjä. Älä käytä Windowsin virtuaaliympäristöä Linuxissa.
6. Säilytä sovelluksen toteutuspäätökset Gitissä: dokumentaatiomuutokset ja pull requestit ovat ensisijaiset jäljet.

## Ajo- ja julkaisukonteksti

- Sovelluksen käynnistyspiste on `main.py`; tämänhetkinen ajotapa ja vaaditut paketit tarkistetaan repositoriosta.
- Raspberry Pi:n käyttöönottoa on aiemmin käsitelty systemd-palveluna. `scripts/update.sh` sisältää Git-päivityksen, riippuvuuksien asennuksen, palvelun käynnistyksen ja terveystarkistuksen.
- **Tarkistettava ennen seuraavaa Pi-päivitystä:** `scripts/update.sh` suorittaa `git reset --hard` ja `git clean -fdx -e streamlit.out`. Jälkimmäinen voi poistaa myös huomioimattomia paikallisia asetuksia ja virtuaaliympäristön. Varmista salaisuuksien säilytys ja käyttöönoton palautettavuus ennen skriptin ajamista. Tässä siirrossa skriptiä ei ole muutettu tai ajettu.
- Windowsin ja Ubuntun yhteiskäyttöön liittyvät NTFS-liitokset ovat käyttöjärjestelmätason toimenpiteitä. Niiden turvallisuutta ei voida päätellä pelkästä repositorion tilasta.

## Siirron hyväksymiskriteerit ennen ChatGPT-projektin poistoa

- [x] Oikea Git-repository tunnistettu: `pvehvila/kotidashboard`.
- [x] Repo-dokumentaation perusrunko tarkistettu (`README.md`, `AGENTS.md`, `QUALITY.md`).
- [x] Projektin yleiset rajaukset ja toimintaperiaatteet kirjattu tähän.
- [ ] Kaikki ChatGPT-projektin keskustelut ja liitteet inventoitu; jokainen merkitty luokkaan: säilytä/siirrä tieto / jo repossa / muu aihe / tarpeeton.
- [ ] Keskusteluissa tehdyt vielä puuttuvat, olennaiset arkkitehtuuri- ja integraatiopäätökset siirretty lähdekoodin tai docs-tiedostojen yhteyteen.
- [ ] Nykyisen Raspberry Pi:n ja Windowsin käyttöönotto- sekä palautumismenettely tarkistettu käytännössä.
- [ ] Keskustelujen mahdolliset salaisuudet jätetty Gitin ulkopuolelle.
- [ ] Dokumentaatiomuutos katselmoitu, testattu tarpeen mukaan ja yhdistetty `main`-haaraan.
- [ ] Käyttäjä varmistanut tietojen säilymisen ennen keskustelujen ja ChatGPT-projektin lopullista poistamista.

## ChatGPT-projektin purkukäytäntö

1. Tarkista keskustelujen ja liitteiden sisältö; älä päättele otsikosta yksin, että kaikki olennainen on tallessa.
2. Siirrä pysyvät tekniset tiedot Git-repoon, mutta älä kopioi raakakeskusteluja sellaisenaan.
3. Tarvittaessa siirrä käyttöjärjestelmä-/laiteaiheiset keskustelut Computers & Linux -projektiin.
4. Varmista repo-dokumentaation kattavuus ennen pysyviä poistoja.
5. ChatGPT-projektin poisto on viimeinen, erikseen tarkistettava toimenpide. Se ei ole sama asia kuin yksittäisten keskustelujen arkistointi.

## Ylläpito

Päivitä tätä tiedostoa vain vahvistetuilla muutoksilla. Erota toteutettu päätös, havainto ja ehdotus toisistaan. Kirjaa pysyvien muutosten yhteyteen päivämäärä ja peruste.
