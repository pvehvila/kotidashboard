# Kotidashboard – aiemmista keskusteluista tarkistettavat kehitystiedot

Päivitetty: 2026-11-08  
Tarkoitus: säilyttää olennaiset *historialliset* toteutus- ja käyttöönottohavainnot ennen ChatGPT-projektin mahdollista poistamista. Tämä ei ole reaaliaikainen ympäristöinventaario.

## 1. Käyttöönoton malli (keskusteluissa vahvistettu)

- 2025-11-02: Raspberry Pi 5:n Kotidashboardia ajettiin `kotidashboard`-nimisenä systemd-palveluna portissa `8787`. Tuolloin käyttäjä raportoi palvelun toimivaksi. Nykyinen tila on tarkistettava Pi:ltä.
- Julkaisun tavoite: lähdekoodimuutokset tehdään kehitysympäristössä, viedään GitHubiin ja otetaan Pi:llä käyttöön. Pi ei luo omia sovelluscommitteja. Pi-kohtainen virtuaaliympäristö ja Linux-riippuvuudet pidetään erillään Windowsin ympäristöstä.
- Repositorion nykyisessä `scripts/update.sh`-tiedostossa Git-synkronointi toteutetaan `fetch` + `checkout` + `reset --hard origin/<haara>` -menettelyllä. Skripti asentaa riippuvuuksia `requirements-linux.txt`-listasta ja tarkistaa Streamlitin `/_stcore/health`-polun.
- 2025-10–11 keskusteluissa esiintynyt Pi:n polku oli `/home/admin/HomeDashboard`; nykyinen `scripts/update.sh` käyttää samaa polkua.
- Windows-julkaisuautomaatio on repossa `scripts/DeployToPi.ps1` (ei ole tässä siirtotyössä ajettu).

## 2. Merkittävät yhteensopivuuspäätökset

- 2025-11-02: Pi:llä nähtiin `bash\r`-virhe CRLF-rivinvaihdoista. Tämän vuoksi erityisesti `.sh`- ja `.py`-tiedostojen LF-rivinvaihdot ovat tärkeä reunaehto.
- Varmennettu repositorion `.gitattributes`-tiedostosta 2026-11-08: oletus `* text=auto eol=lf`; `*.sh`, `*.py`, `*.md` LF; Windowsin `*.ps1` ja `*.bat` CRLF.
- Windows- ja Linux-virtuaaliympäristöjä ei pidä jakaa. Yhteinen lähdekoodirepository ei tarkoita yhteisiä asennettuja Python-paketteja.

## 3. Integraatioiden historialliset havainnot – ei oleteta nykytilaksi

- **Home Assistant:** tammikuun 2026 keskusteluissa Pi oli HA-palvelin. Windows-dashboardin tuli käyttää palvelimen verkko-osoitetta, ei `localhost`-osoitetta; Pi:llä paikallinen HA-yhteys saattoi käyttää `localhost:8123`-osoitetta. Yhteysosoitteet on tarkistettava nykyisestä konfiguraatiosta, ei kopioitava keskusteluista suoraan.
- **EQE-kortti:** tammikuussa 2026 eräs aiemmin käytetty Home Assistant -entiteettinimi johti `Entity not found` -virheeseen. Kyse oli ympäristön entiteettikartoituksesta, ei varmennetusta nykyisestä sovellusviasta. Tarkista nykyiset entiteettinimet HA:sta ennen muutoksia. Älä tallenna pääsytokeneita Git-repoon.
- **Hue:** joulukuussa 2025 keskusteluissa Raspberry Pi:n systemd-palvelu vaati Hue-integraation ympäristömuuttujat palvelun `[Service]`-osioon; väärä konfiguraation sijainti aiheutti puuttuvia arvoja. Käyttäjä vahvisti tuolloin tunnistinten näkyneen eri asiakaslaitteilla. Nykyinen konfiguraatio on tarkistettava Pi:llä. Hue-avaimia ei saa dokumentoida.
- **HEOS:** sovellus sisältää HEOS/Tidal-toimintoja nykyisen `README.md`-kuvauksen mukaan. Keskusteluista ei tässä vaiheessa ole varmennettu erillistä uutta HEOS-arkkitehtuuripäätöstä.

## 4. Tarkistettavat ristiriidat ja riskit repossa

1. **Julkaisuskriptin polku:** `scripts/DeployToPi.ps1` kutsuu SSH:n kautta `~/HomeDashboard/update.sh`, mutta repositorion tiedosto löytyy polusta `scripts/update.sh`. Selvitä, onko Pi:llä myös erillinen juuritason skripti, ennen kuin luotat automaattiseen julkaisuun.
2. **Paikallisten tiedostojen poistuminen:** `scripts/update.sh` sisältää `git clean -fdx -e streamlit.out`. Se voi poistaa Gitin ulkopuolisia hakemistoja ja asetuksia sekä virtuaaliympäristön, vaikka saman skriptin myöhemmät vaiheet yrittävät käyttää virtuaaliympäristöä. Varmista vaikutus ja korjaa erillisessä koodimuutoksessa ennen seuraavaa käyttöönottoa.
3. **Systemd-määrityksen sijainti:** `README.md` viittaa `examples/kotidashboard.service`-tiedostoon, jota ei löytynyt tarkistetusta haarasta kyseisestä polusta. Todellinen palveluyksikkö ja sen varmuuskopio on tarkistettava.
4. **Testitulokset:** `QUALITY.md` kuvaa onnistuneen laatuketjun, mutta dokumentin väite ei korvaa tuoretta testiajoa.
5. **Vanha Git-konflikti:** lokakuun 2025 keskustelussa raportoitiin `api.py`- ja `utils.py`-tiedostojen rebase-konflikti. Älä käsittele sitä nykyisenä vikana ilman tuoretta Git-tilatarkistusta.

## 5. Jäljellä oleva ChatGPT-projektin purkutyö

- Kaikkien keskustelujen ja liitteiden kattavaa inventaariota ei ole tehty: aiemmat keskustelumuistiinpanot eivät ole sama kuin täydellinen keskusteluexport.
- Tarkista käyttöliittymä-, kortti- ja integraatiokohtaiset poikkeuspäätökset, joita nykyinen README/lähdekoodi ei sisällä.
- Kirjaa jokaisen avoimen asian omistaja, ratkaisu ja todentamistapa issueen tai PR:ään; poista vanhoja keskusteluja vasta tiedon säilymisen todentamisen jälkeen.
- Tämä tiedosto sisältää vain aiheeseen liittyvät tekniset yhteenvedot, ei ympäristön salaisuuksia eikä yksityisiä tunnisteita.
