# Kotidashboardin ChatGPT-keskustelujen ja liitteiden auditointi

Päivitetty: **9.11.2026**. PR #4, haara `docs/chatgpt-project-migration-2026-11`.

**Tulos:** kaikki aiemman projektihakemiston 111 keskustelua löytyivät käyttäjän toimittamasta tietoviennistä. Viestihistorian aiempi viiden vuoron rajoitus on poistunut tämän viennin osalta. Liitteiden alkuperäiset tiedostosisällöt ovat edelleen osittain saatavilla, joten **projektin poistovalmius ei ole valmis**. Mitään ei poisteta, siirretä tai yhdistetä tällä auditoinnilla.

Tämä versio korvaa 8.11.2026 inventaarion saatavuusluvut ja yleisen P0-luokituksen. Aiemman tarkistuksen tekniset havainnot säilyvät lopun päivätyssä osassa siltä osin kuin uudet korjaukset eivät korvaa niitä.

## 1. Lähteet ja täsmällinen kattavuus

### Tietovienti

Käyttäjä tallensi ChatGPT:n koko tilin ZIP-viennin paikallisesti 9.11.2026. Paketti luettiin paikallisesti; raakakeskusteluja, kuvia, asetuksia, tunnuksia tai muita projektikeskusteluja ei viety GitHubiin.

- ZIP:n SHA-256: `cd2e08e3e980177f76506b84eaeab40ef1b12301bad4b9583ac5807bb98568d2`.
- Arkistossa on 2 314 tiedostomerkintää, joista kymmenen `conversations-000.json` … `conversations-009.json`. Näistä poimittiin vain aiemman Kotidashboard-luettelon tunnuksia vastaavat keskustelut.
- **111/111 eri keskustelutunnusta löytyi.** Vienti ei sisällä näissä keskusteluobjekteissa projektijäsenyyden tunnusta, joten se ei yksin tarjoa riippumatonta täydellistä projektihakemistoa. Projektirajaus perustuu 8.11.2026 työkalulla tehtyyn luetteloon, ei otsikon sanaosumaan.
- Nykyisissä keskusteluhaaroissa on **2 339 näkyvää käyttäjän/avustajan viestiä**, joista **1 166 käyttäjäviestiä**. Lisäksi neljässä keskustelussa on yhteensä **7 näkyvää sivuhaaran viestiä**. Kaikki näkyvät viestit: **2 346**. Mallin sisäisiä analyysikenttiä ei käytetty käyttäjän päätösten lähteenä.
- Nykyhaara rakennettiin `current_node`-solmusta vanhempien kautta juureen; **puuttuvia vanhempisolmuja ei löytynyt**. Seitsemän sivuhaaran viestiä erotettiin voimassa olevan haaran päätöksistä. Alkuperäistä palveluhistoriaa, jo poistettuja viestejä tai viennistä mahdollisesti pois jäänyttä sisältöä ei tällä todisteta täydelliseksi.
- Näkyvien viestien aikaväli on **27.9.2025–8.11.2026**; viimeinen viestiaika viennissä on 8.11.2026 klo 15.20 Suomen aikaa. Vienti ei sisällä sen jälkeisiä muutoksia. Myös aiemmin 20 000 merkkiin katkaistu UI-refaktorointikeskustelu on nyt saatavilla vientitekstinä.
- Liitemetadatassa on **738 esiintymää / 734 eri tiedostotunnusta**. Neljä tunnusta esiintyy kahdesti; samannimisiä eri tiedostotunnuksia ei yhdistetä.
- **255 kuvaliitettä** kohdistui ZIP:n tiedostoon täsmällisen tiedostotunnuksen perusteella: 250 PNG- ja 5 JPEG-kuvaa. Niiden tavut luettiin arkistosta ja ne katsottiin pienennettyinä yhteiskuvina. Tämä on visuaalinen yleiskatsaus, ei kaikkien pienien koodi-/lokitekstien tarkistus alkuperäiskoossa eikä kuvien tietojen ajantasaisuuden vahvistus.
- **483 muun liitteen alkuperäinen tiedostosisältö ei sisälly pakettiin kohdistettavana tiedostona.** Näistä **68 eri liitteestä** on ei-tyhjä tekstikatkelma `content_references.snippet`-kentässä. Katkelmaa ei merkitä alkuperäiseksi täydelliseksi tiedostoksi eikä tavutason varmuuskopioksi. Jäljelle jää **415 esiintymää vain metatietona/tyhjänä viitteenä**.
- Tekstiviitteitä on 272, joista 136 sisältää katkelman; ne viittaavat 118 eri liitetunnukseen. Toistuvat saman katkelman viitteet eivät lisää liitteiden määrää. Ei-tyhjiä katkelmia on 68 eri liitetunnukselle. Kaikki 118 viitetunnusta kohdistuvat liitemetadataan.
- Näkyvissä viesteissä on **54 sandbox-latausviitettä**, **34 eri keskustelu/polku-paria** ja **33 eri polkumerkkijonoa**. Alkuperäisten generoitujen tiedostojen sisältösamuutta repo-tiedostoihin ei vahvistettu. Pelkkä samannimisyys tai vanha latauslinkki ei todista säilymistä.
- Canvasien itsenäistä versiohistoriaa ei palautettu erillisenä aineistona. Keskustelussa mainittu canvasiin kirjoittaminen ei siksi todista, että kaikki canvas-versiot ovat mukana. Näkyvät Markdown-/koodilohkot ovat käytettävissä keskustelutekstinä.

### Keskusteluluettelo ja projektin lähdetiedostot

8.11.2026 `list_projects` tunnisti ChatGPT-projektin **Kotidashboard**, tunnus `g-p-68e77f35e33c8191ba7b0692012d3816`. Samanniminen paikallinen Codex-projekti on eri kohde.

`list_threads(mode=history, source=chatgpt, limit=50)` käytiin kursorihausta loppuun: 20 aktiivista sivua / 954 keskustelua ja arkistoidut erikseen yksi sivu / 14 keskustelua. Projektitunnuksella löytyi **111 aktiivista, 0 arkistoitua** Kotidashboard-keskustelua. Tämä luettelo on nyt kokonaan kohdistettu vientiin; jo poistettuja tai käyttöoikeuksiltaan näkymättömiä keskusteluja se ei kata.

Selaimen projektin **Sources → All** -näkymässä oli kaksi tiedostoa. Molemmat luettiin 8.11.2026:

| Lähde | Saatavuus ja sisältövertailu | Säilytys / siirto / poisto |
| --- | --- | --- |
| `PROJEKTIOHJEET.md`, 29.10.2026 | Esikatselu luettu. Repo, versio ja ajoalusta tarkistettava; integraatioasetukset erotettava koodista; toimivat kortit säilytettävä; tunnuksia ei tallenneta. Vastine `docs/PROJECT_CONTEXT.md` ja repon `AGENTS.md`. | Olennainen periaatesisältö dokumentoitu. Säilytä lähde kunnes dokumentaatio on katselmoitu ja yhdistetty erillisellä päätöksellä. |
| `PERUSTIEDOT.md`, 29.10.2026 | Esikatselu luettu. Tarkoitus, aiheet, työnjako ja puuttuvat prioriteetit; aiempi kartoitus ilmoitetaan osittaiseksi. Vastine `docs/PROJECT_CONTEXT.md`. | Mahdollinen myöhempi poistoehdokas, ei poistotoimenpidettä. |

### Repon vertailutilanne

Tarkistettu PR #4:n pää **`fc0e7f9b996ffb4c75841c1fa5512d4ba496a921`**, haara `docs/chatgpt-project-migration-2026-11`. PR oli avoin luonnos ja yhdistämätön. Rekursiivinen tiedostopuu palautui ilman katkaisua.

Tässä kierroksessa luettiin README, QUALITY, REFACTORING, CHANGELOG, PROJECT_CONTEXT, HISTORICAL_DECISIONS, AGENTS, `pyproject.toml` ja kohdennetusti pääohjelma, asetukset, sitaatti-, sähkö-, WMO-, HA- ja HEOS-koodi sekä päivitysskriptit. Sovellusta, testejä, käyttöjärjestelmää tai laitteiden ohjausta ei ajettu. Lähdekoodin tai dokumentin olemassaolo ei todista tuotantokäyttöä tai tuoretta testitulosta.

## 2. Päätösten ja vaatimusten vertailu

Alla oleva sisältö erottaa käyttäjän nimenomaisen toiveen, historiallisen onnistumiskuittauksen ja avustajan ehdotuksen. Vanhojen vastausten ”valmis”, ”testattu” ja ”tallennettu” eivät yksin todista nykyistä toteutusta tai Git-tallennusta.

| Aihe / lähdekeskustelu (nro alla) | Viennistä vahvistettu tieto | Repovertailu ja säilytettävä päätös |
| --- | --- | --- |
| Alkuperäinen käyttötarkoitus, 101/105 | Jatkuvasti näkyvä tablettikoonti: arjen tiedot, kello, aurinko, nimipäivät, sähkö ja sää. Lenovo M9:n hankinta ja Fully Kiosk -käyttö mainitaan käyttäjän viesteissä. Pystykuva, tumma teema ja näkyviin mahtuva sisältö ovat alkuperäisiä tavoitteita. | README kuvaa koontinäytön ja alustat. Historiallinen laite/selainhyväksymiskohde on **pystyasentoinen Lenovo M9 + Fully Kiosk**, ei oletus kaikista nykyisistä asiakaslaitteista. Vanhoja ostosehdotuksia ei muuteta toteutuneiksi hankinnoiksi. |
| Zen-sitaatit, 103 | Verkosta haettavat samanhenkiset zen-ajattelijat, vain rajatut tekijät, erillinen nimipäivä- ja zen-kortti sekä himmeä zen-tausta. Myöhemmin käyttäjä vahvisti Initial Scale -asetuksen auttaneen asettelua. | `src/api/quotes.py` hakee ZenQuotes/Quotable-lähteistä ja käyttää paikallista fallbackia; **verkkositaattien tekijälistasuodatusta ei ole**. `card_zen.py`:ssä on erillinen kortti/tausta. README:n ”satunnainen mietelause” ei säilytä alkuperäistä tekijärajausta. **Avoin tuotevalinta:** palautetaanko zen-tekijärajaus vai hyväksytäänkö nykyinen laajempi sisältö. Tässä auditissa ei muutettu koodia eikä väitetä myöhempää rajauksen peruuttamista. |
| Korttien järjestys, 104/108/65 | Nimipäivät + sitaatti ylimmäksi, sää ja sähkö omille riveille, sen jälkeen Bitcoin ja järjestelmätila. Myöhemmin lisättyjä kortteja ei ollut tässä vanhassa järjestyspäätöksessä. | Nykyinen `main.py` näyttää nimipäivät/zen, ovet, sään, EQE+sähkön, Bitcoin/tikkerit sekä järjestelmätila+siitepölyn. Vanha järjestys on historiallinen lähtökohta, ei käsky poistaa myöhempiä kortteja. Responsiivisuus ja tiivis tablettiasettelu on säilytettävä muutoksissa. |
| HEOS/Tidal, 91/67/9/8/30 | Toiston aloitus, pause/play, seuraava/edellinen sekä kappaletieto; standby-herätyksen onnistumisesta käyttäjän raportti. Isommat keskitetyt painikkeet, leveä teksti ja tasakorkeus. Kehitysympäristö ei saa käynnistää kotona toistoa vahingossa. | README/CHANGELOG ja `card_heos.py`/`heos_client.py` kattavat suuren osan toiminnosta. **Nykyinen `main.py` ei tuo tai kutsu `card_heos()`-funktiota**, vaikka se on re-exportattu `src/ui/__init__.py`:ssä. Siksi ”HEOS-koodi on repossa” ei tarkoita, että kortti on nykyisessä päänäkymässä. Dokumentoi poistamisen tai uudelleenkytkennän tarkoitus erikseen. Ei laitekoetta. |
| Sähkön data ja UI, 73/72/94/111 | 12 h eteenpäin, 48 varttipalkkia, snt/kWh, Pörssisähkö ensisijaisena, varalähde tarvittaessa. **Käyttäjä halusi jättää tuntikeskiarvon välistä.** Negatiiviset hinnat pitää näyttää; aiempi nollaminimi on vanhentunut. Nykyhinta otsikkoon, ei hinnan muutosprosenttia. | README, palvelukoodi ja aiempi kohdennettu tarkistus kattavat varttihaun. `prices_15min_vm.py` käyttää datan minimiä ja UI viewmodelin akselirajoja. Tuntidatan nelinkertaistus fallbackina on alempi tarkkuustaso, ei aitoa varttidataa: tämä ero säilytettävä dokumentaatiossa ja tulevissa testeissä. Yksikköregressiot ovat historiallisia, eivät tässä todettuja nykyvikoja. |
| Sähkötestit, 33/42/16 | Eri fallback-haarat, tyhjä/outo/vanha data, normalisoidun listan hintojen ei pidä kasvaa 100-kertaiseksi. | QUALITY ja olemassa olevat sähkötestit ovat vastineita, mutta tuoretta testiajoa ei tehty. Testausvaatimus säilyy; vanha ”kaikki testit vihreät” ei ole nykyinen hyväksyntä. |
| Nimipäivät ja palautus, 96/88/56/55/34 | Liputus/pyhäpäivä tärkeimpänä ylös, nimet sekä aurinkoikonit saman kortin sisään. Käyttäjä halusi palauttaa rikkoutuneen nimipäiväkortin menettämättä muita myöhempiä committeja. | `docs/CARD_NAMEDAY.md`, CHANGELOG 1.1.0 ja REFACTORING kattavat rakenteen. Historialliset commitit `6ec0fb1` (käyttäjän ilmoittama toimiva) ja `ef178bb` (käyttäjän ilmoittama rikkova) ovat **vianrajausviitteitä**, eivät tässä vahvistettuja nykyisen repon rollback-kohteita. Säilytä toimiva ulkoasu sekä flat/nested-data ja vanhat importtipinnat. |
| Sää ja WMO, 98/97/23/19 | Open-Meteon säädata → Forecan päivä/yö-ikonit; käyttäjä korjasi Excelin sarakkeet `Code figure`, `Päivä`, `Yö`. UI:hin aikaleimat, sateen todennäköisyydet ja aikavälin valinta. | `REFACTORING.md`, `data/WMO_Foreca-koodit.xlsx` ja `wmo_map_loader.py` ovat vastineita. Excelin alkuperäiset tiedostoliitteet puuttuvat: koko kartoituksen sisältösamuutta ei vahvisteta. Debug/trace pois normaalinäkymästä on myöhempi käyttäjän toive (93), ei velvoite säilyttää debug-paneelia tuotannossa. |
| Python ja kattavuus, 15/42 | 3.9-yhteensopivuutta ei tarvita; käynnistys-/konfiguraatiotason logger_config ja weather_debug voidaan jättää kattavuusraportista. | `pyproject.toml`: Python >=3.10, omit-listassa logger_config/weather_debug. Aiemmin tarkistettu CI-matriisi 3.10/3.11 vastaa tätä. README:n Python 3.13 -maininta kuvaa yhtä ympäristöä, ei tämän kierroksen laajaa yhteensopivuuskoetta. |
| Refaktorointi, R/W/N/E-ryhmät | Pienet muutokset ja API/laskenta/UI-erottelu, kellon ja cachejen hallinta testeissä. Nykyisen toiminnan ja yhteensopivuuden säilyttäminen korostuu käyttäjän viesteissä toistuvasti. | `REFACTORING.md` 7.12.2025 korvaa vanhempia marraskuun työjonoja; siinä hyväksytään rajattuja C-tason funktioita. Vanhan ehdotetun tiedostonimen puuttuminen ei yksin osoita puuttuvaa refaktorointia. Nykyisten testien numeerista kattavuutta ei päätellä vanhoista lokeista. |
| Windows/Pi-työnjako, 78/2 | Windows-kehitys → GitHub → Pi ja erilliset venvit; Pi:llä ei normaalisti luoda automaattisia sovelluscommitteja. Tammikuussa käyttäjä pyysi Pi:llä toimineen korjauksen vientiä Gitin kautta Windowsiin. | `PROJECT_CONTEXT.md` ja `HISTORICAL_DECISIONS.md` kattavat tavoitemallin. **Pi ei luo committeja** on normaali työnjako, ei aukoton historiaväite. Poikkeuskorjauksen pushin lopullista onnistumista ei todisteta viestistä ”Pi toimii”. |
| Home Assistant/EQE, 5/6/2/4 | HA rinnalle olemassa olevan dashboardin kanssa, Container/HACS-konteksti, ympäristökohtaiset osoitteet/entiteetit ja salaisuudet. Myöhempi käyttäjän raportti Pi:n toimivuudesta. | README:n ”kuten aiemmin” on puutteellinen asennusohje. Alla on koodiin perustuva salaisuukseton asetustaulukko. Alkuperäiset asetustiedostot ovat osin vain katkelmia/metatietoa; älä siirrä raakaa .env/secrets-sisältöä julkiseen repoon. EQE-ohjausten valtuutus jää aiemman auditin avoimeksi asiaksi. |
| Varmistus ja Linux/Windows, 6/1 | Rsync-varmistuksen itsensä sisään kopioituminen korjattiin keskustelussa; palautuskoetta ei vahvistettu. Jatkokeskustelussa Windows-osion luku- ja kirjoitusliitos selvitettiin. | Varmistuksen olemassaolo ei todista palautettavuutta. Windows/Linux-osuuden todellinen toteutustila on erillinen Computers & Linux -asia; viennistä ei seuraa uutta lupaa muuttaa liitoksia. Sekasisältöinen keskustelu 1 säilytetään/jaetaan sisältötasolla, ei poisteta kokonaisena auditin valmistuttua. |

### Päivitysskriptien tarkennus

Repossa on **kaksi eri skriptiä**:

| Tiedosto | Tarkistettu käyttäytyminen | Johtopäätös |
| --- | --- | --- |
| `update.sh` repojuuressa | `git pull --rebase origin main`, olemassa olevan venvin aktivointi, requirements.txt, systemd-restart. | `DeployToPi.ps1`:n kutsuma polku on repossa olemassa. Nykyinen polku ei siis ole puuttuva tiedosto. |
| `scripts/update.sh` | fetch/checkout/reset, `git clean -fdx -e streamlit.out`, venvin uudelleenluonti tarvittaessa, Linux-riippuvuudet ja fallback, useampi käynnistystapa/health-check. | Clean voi hävittää paikallisia Gitin ulkopuolisia asetuksia ja dataa. **Venv luodaan koodissa tarvittaessa uudelleen**, joten poistuminen ei yksin todista sen myöhempää puuttumista. Säilytettävät paikalliset asetukset ja varmistus on silti erotettava käyttöönotosta. |
| `scripts/DeployToPi.ps1` | Voi puskea nykyisen haaran, SSH-kutsu juuritason update.sh:hon; juuriskripti hakee mainin. | Muun haaran pushaus ei tarkoita sen käyttöönottoa Pi:llä. Käytössä oleva skripti on varmennettava Pi:ltä. |

**Korjaus aiempaan dokumentaatioon:** `HISTORICAL_DECISIONS.md` kohdan 4.1 polkuriskin perustelu on puutteellinen, koska juuritason tiedosto on olemassa. Viennissä on kuitenkin myös aito vanha käyttöönottoilmoitus puuttuvasta juuriskriptistä: se on **historiallinen ympäristövirhe**, ei nykyisen repon puuttuvan tiedoston todiste. Tätä muuta dokumenttia ei muutettu tässä auditointipäivityksessä.

### Salaisuukseton HA-asetuskartta

Lähde: `src/api/home_assistant.py::_get_secret` tarkistetussa commitissa. Järjestys on **secretsin suora HA_-avain → `[home_assistant]`-osion avain → ympäristömuuttuja**. Ei tyhjä arvo voittaa myöhemmät lähteet. Tämä kuvaa koodia, ei nykyisen palvelimen asetuksia.

| Suora secrets-/ympäristöavain | `[home_assistant]`-osion avain | Tarkoitus |
| --- | --- | --- |
| `HA_BASE_URL` | `base_url` | HA-palvelimen osoite; Windowsin localhost ei tarkoita Pi:n HA:ta. |
| `HA_TOKEN` | `token` | Pääsytunnus, säilytetään yksityisesti. Arvoa ei kirjata dokumentaatioon. |
| `HA_EQE_SOC_ENTITY` | `eqe_soc_entity` | Akun varaustila. Entiteetti tarkistetaan omasta HA:sta. |
| `HA_EQE_RANGE_ENTITY` | `eqe_range_entity` | Toimintamatka. |
| `HA_EQE_CHARGING_ENTITY` | `eqe_charging_entity` | Latauksen tilatieto. |
| `HA_EQE_LOCK_ENTITY` | `eqe_lock_entity` | Lukitusohjauksen kohde. |
| `HA_EQE_LOCK_STATUS_ENTITY` | `eqe_lock_status_entity` | Lukituksen palautetieto. |
| `HA_EQE_LOCK_CODE` | `eqe_lock_code` | Mahdollinen lukituskoodi; ei dokumentoitavaa arvoa. |
| `HA_EQE_PRECLIMATE_ENTITY` | `eqe_preclimate_entity` | Ilmastoinnin ohjauskohde. |
| `HA_EQE_PRECLIMATE_START_ENTITY` / `HA_EQE_PRECLIMATE_STOP_ENTITY` | `eqe_preclimate_start_entity` / `eqe_preclimate_stop_entity` | Erilliset käynnistys-/pysäytyskohteet. |
| `HA_EQE_CHARGING_POWER_ENTITY` | `eqe_charging_power_entity` | Latausteho. |
| `HA_EQE_CHARGING_SWITCH_ENTITY` | `eqe_charging_switch_entity` | Latauksen kytkentä. |
| `HA_EQE_LOCK_REFRESH_SERVICE` / `HA_EQE_LOCK_REFRESH_ENTITY` / `HA_EQE_LOCK_REFRESH_DATA` | `eqe_lock_refresh_service` / `eqe_lock_refresh_entity` / `eqe_lock_refresh_data` | Lukituksen tilan virkistys. |
| `HA_EQE_REFRESH_SERVICE` / `HA_EQE_REFRESH_ENTITY` / `HA_EQE_REFRESH_DATA` | `eqe_refresh_service` / `eqe_refresh_entity` / `eqe_refresh_data` | Yleinen tilan virkistys. |
| `HA_EQE_REFRESH_INTERVAL` | `eqe_refresh_interval` | Virkistysväli. |
| `HA_CACHE_TTL` | `cache_ttl` | Tilavälimuistin kesto. |
| `HA_EQE_LOCK_TIMEOUT` | Ei koodin osiokartoituksessa | Suora secrets-avain tai ympäristömuuttuja; ei oleteta samaa nimikäytäntöä kuin muilla. |

Vientitekstissä esiintyy todellisia tunnuksia. Niitä ei kopioitu tähän, lokiyhteenvetoon tai repoon. Katkelmia sisältävä vienti ei ole turvallinen julkinen lähdekoodipaketti. Mahdollinen edelleen käytössä olevien paljastuneiden tunnusten vaihto on erillinen käyttäjän toimenpide; tässä tunnuksia tai käyttöoikeuksia ei muutettu.

## 3. Säilytys-, siirto- ja poistokelpoisuus

- **S / P0:** säilytä; koko keskustelua/liitettä ei vielä todettu poistokelpoiseksi, esimerkiksi alkuperäinen tiedosto tai canvas puuttuu, historia on sekasisältöinen tai olennainen päätös on avoin.
- **M / P0:** siirtoehdokas nimettyyn toiseen projektiin; säilytä siihen asti. Keskustelun siirtoa ei suoritettu.
- **P1:** ehdollinen myöhempi poistoehdokas, jonka näkyvä sisältö on tässä rajauksessa dokumentoitu tai yleistä, eikä vienti näytä puuttuvaa liitettä. **Ei ole poistolupa:** käyttäjä arvioi viennin säilytyksen ja dokumentaation ennen erillistä poistopäätöstä. PR:n yhdistäminen ei kuulu tähän toimeksiantoon.

P1-kohteet ovat keskustelu **15** (3.9-testimatriisi; päätös ja kuva saatavilla, vastine CI/Python-määrityksissä), **32** (SemVer-kysymys; ei liitteitä, vastine CHANGELOGissa) ja **7** (julkisen IP:n yleinen selvitysohje; keskustelu ei sisällä vahvistettua osoitetta tai liitteitä). Viimeinen voidaan myös siirtää Computers & Linux -projektiin. Muissa kohteissa puuttuva lähde tai säilytettävä historiallinen konteksti jää ratkaisematta; tämä ei tarkoita kaikkien raakakeskustelujen pysyvää säilytystarvetta.

## 4. Kaikki 111 keskustelua: vientiin kohdistettu inventaario

Numerointi ja ensisijainen otsikko säilyttävät 8.11. projektihakemiston järjestyksen. **V/U/L/K/T** = nykyhaaran näkyvät viestit / käyttäjäviestit / kaikki liite-esiintymät / saatavilla olevat kuvat / liitteet joista tekstikatkelma. Kuvat ja katkelmat eivät ole päällekkäisiä saatavuusluokkia tässä aineistossa. Muut L−K−T-esiintymät ovat vain metatietoa. Vienti sisältää lisäksi edellä mainitut seitsemän sivuhaaran viestiä. Nolla liitettä tarkoittaa ”ei tämän vientikohteen metadatassa”, ei palveluntarjoajan takaamaa koko tilin täydellisyyttä.

Ryhmä: P käyttöönotto/HA, H Hue, E sähkö, N nimipäivät, W sää/WMO, HE HEOS, R refaktorointi/julkaisut, T testaus/Python, U UI/kaaviot, M muu projekti. Dokumenttivastineet ja uudet erot on koottu osioon 2 sekä lopun tekniseen tarkistukseen.

| Nro | Keskustelu | V/U/L/K/T | Ryhmä | Säilytys/siirto/poisto ja havainto |
| --- | --- | --- | --- | --- |
| 1 | [Kotidashboard – Windows/Linux](https://chatgpt.com/c/6ae211ad-2930-83ed-b27e-b34119890ee7) | 91/40/6/6/0 | P | S / P0. Koko vientihistoria sisältää myös projektien siivousta ja Windows/NTFS-asian. Sovelluksen siirtopäätökset dokumentoitu; käyttöjärjestelmäosuus Computers & Linux -siirtoehdokas. Sekasisältöä ei poisteta yhtenä kokonaisuutena. |
| 2 | [Raspberry Pi token virhe](https://chatgpt.com/c/697932d2-0bf4-8330-95e7-dd338f5e713c) | 56/28/5/3/0 | P | S / P0. Pi toimi käyttäjän mukaan; Pi → Git → Windows -poikkeus aiempaan kehitystyönjakoon. Nykyinen synkronointi vahvistamatta. |
| 3 | [Raspberry Pi palautus Windowsista](https://chatgpt.com/c/69793157-0fd0-8394-b82d-040fe42d2994) | 2/1/0/0/0 | P | S / P0. Windowsin toimivan version palautus Pi:lle; ei palautuksen onnistumiskuittausta. |
| 4 | [Raspberry Pi 5 ongelma](https://chatgpt.com/c/69791835-0894-8330-aef3-c4c3fcf52bdb) | 74/37/8/6/0 | H | S / P0. Hue 403/404; v1-fallback on ehdotus, ei vahvistettu korvaava päätös. |
| 5 | [Mercedes-Benz Me API](https://chatgpt.com/c/6977abf4-fd44-8393-81a7-fd38f1494857) | 116/58/13/9/0 | P | S / P0. EQE-entiteetit ja systemd-oikeudet; ajoasetukset eivät ole nykytilavarmennus. |
| 6 | [Raspberry Pi ja Home Assistant](https://chatgpt.com/c/6978446c-c3b0-838d-b987-42c295aff9b2) | 22/11/0/0/0 | P | S / P0. HA-kontti ja paikallinen HTTP 200; rsync-varmistuksen palautettavuus avoin. |
| 7 | [Raspberry Pi julkinen osoite](https://chatgpt.com/c/6960de36-8e50-832a-8503-05f454154b70) | 2/1/0/0/0 | M | P1. Ei vahvistettua julkista osoitetta. Computers & Linux -siirtoehdokas. |
| 8 | [HEOS-kortin grafiikka](https://chatgpt.com/c/694e5c26-fc38-8331-8eaf-85bf16598bc8) | 75/38/31/14/0 | HE | S / P0. Keskitetyt suuret painikkeet, leveä kappaleteksti ja tasakorkeus; nykyinen main.py ei kutsu HEOS-korttia, ks. osio 2. |
| 9 | [HEOS toisto ongelma](https://chatgpt.com/c/694e4504-0950-8332-bc41-f1cd940bd999) | 25/13/10/0/0 | HE | S / P0. Play/pause/standby käyttäjän onnistumiskuittauksin. Nykyisen päänäkymän puuttuva korttikutsu erotettava olemassa olevasta toteutuksesta. |
| 10 | [Codex environment variables selitys](https://chatgpt.com/c/693c084b-5594-8328-975f-dde0326d8733) | 12/6/2/1/0 | M | M / P0. Ympäristöasetukset ja refaktorointiprompti; ristiriitaisia vanhoja avainohjeita ei siirretä käyttöohjeeksi. |
| 11 | [Kompleksisuuden arviointi](https://chatgpt.com/c/6935ae2e-ba8c-832b-abdd-0d6994e821f3) | 32/16/13/0/0 | R | S / P0. 1.1.0-julkaisutekstit kahdella kielellä; vastine CHANGELOG-tiedostoissa. |
| 12 | [Testivirheet ja korjaukset](https://chatgpt.com/c/69352ddf-ca68-832b-a04e-8519bde2ead2) | 50/25/23/1/0 | N | S / P0. Nimipäiväkortin HTML-testien ja toteutuksen odotukset. |
| 13 | [Hue liiketunnistimien lisäys](https://chatgpt.com/c/6933edac-47f4-8331-b685-9c964ffac0fe) | 62/31/17/4/0 | H | S / P0. Hue-v2 ovet/liike, tilan päivitys ja Bandit/TLS-poikkeus; avoimet riskit säilyvät. |
| 14 | [Päivitetty changelog-tiedosto](https://chatgpt.com/c/691c9096-e8dc-832c-9eac-f3e26b329ab8) | 2/1/2/0/0 | R | S / P0. Refaktorointi- ja testimuutosten changelog-ehdotukset. |
| 15 | [Poista Python 3.9 testi](https://chatgpt.com/c/691c5868-0f18-832d-946a-1b57462f7f83) | 2/1/1/1/0 | T | P1. Käyttäjä ei tarvitse 3.9-tukea; CI 3.10/3.11 ja requires-python >=3.10 vastaavat. |
| 16 | [Testikattavuus ja analyysi](https://chatgpt.com/c/691c2e52-e248-8327-8c00-eb66c0ee4cb1) | 38/19/16/2/0 | T | S / P0. Testien tyypitys ja kattavuus; ei tuoretta laatutulosta. |
| 17 | [Bitcoin testien lisääminen](https://chatgpt.com/c/691c3538-da8c-8332-9588-92fd3eb9e464) | 18/9/5/1/0 | T | S / P0. Bitcoin UI-testin patch-kohde; ei uusi ominaisuuspäätös. |
| 18 | [Refaktorointitarpeet Radonilla](https://chatgpt.com/c/691c29ef-a894-832d-910f-fc4bc8f2dff3) | 12/6/1/0/0 | R | S / P0. REFACTORING.md-latausversio; binäärinen/tekstuaalinen samuus tarkistamatta. |
| 19 | [Refaktorointi ehdotukset](https://chatgpt.com/c/691c22d2-1d68-832e-83f0-b5aa1c356352) | 4/2/2/0/0 | W | S / P0. WMO-luku, validointi ja transformaatio erilleen. |
| 20 | [Refaktorointi safe_cast](https://chatgpt.com/c/691c21b4-b1a4-832f-aaf7-78592eded873) | 4/2/2/0/0 | W | S / P0. safe_cast dispatcheriksi; tyyppikohtaiset apurit. |
| 21 | [Refactoring update Radon 2025](https://chatgpt.com/c/691c2639-c978-832d-babd-9288f6148647) | 6/3/1/0/0 | R | S / P0. Refaktorointijonon päivitys ja canvas; canvas-versiota ei saatu. |
| 22 | [Refaktorointi nimipäivät](https://chatgpt.com/c/691c243f-7f34-832a-a965-204ee7adf7c3) | 2/1/1/0/0 | N | S / P0. Nimipäivien flat/nested sekä pyhäpäivälogiikan erottelu. |
| 23 | [Refaktorointi ja funktiot](https://chatgpt.com/c/691c1f03-d9bc-8333-b7b8-71606c4e529d) | 4/2/1/0/0 | W | S / P0. Sääaikajana, rivimuunnos, indeksi ja min/max erilleen. |
| 24 | [Sähkökortti ja Bitcoin-kortti](https://chatgpt.com/c/691b4a2d-9cb0-8325-995c-c10e51fe1e82) | 16/8/5/2/0 | R | S / P0. Sähkö/Bitcoin-regressiot ja refaktorointicanvas; canvas puuttuu. |
| 25 | [Refaktorointi weather_fetch.py](https://chatgpt.com/c/691b451d-c700-8329-8428-475f5372a353) | 4/2/1/0/0 | W | S / P0. Säädatan muunnoksen erottelu ja Windows-laatuketjun käynnistys. |
| 26 | [Refaktoroinnin tila](https://chatgpt.com/c/691b4337-e1e0-8329-85f1-3e384069c180) | 2/1/1/0/0 | R | S / P0. 17.11.2025 Radon-tilanne; myöhempi REFACTORING.md on eri päiväykseltä. |
| 27 | [New chat](https://chatgpt.com/c/691b4217-95c4-8326-ae43-fe96f0870fed) | 2/1/6/0/0 | N | S / P0. New chat käsittelee nimipäivätestejä: kellonaika vakioitava testeissä. |
| 28 | [Refaktorointi card_prices.py](https://chatgpt.com/c/691b4066-5cb4-8329-bacd-8a50662816bb) | 2/1/1/0/0 | E | S / P0. Laskenta viewmodeliin, UI:hin otsikko/värit/Plotly. |
| 29 | [Refaktorointi weather_fetch.py](https://chatgpt.com/c/691b3f17-f0d4-832f-8dc6-9ee1f2ea609f) | 2/1/1/0/0 | W | S / P0. Säähaun ja datamuunnoksen erottelu; ehdotuksen tarkka toteutus tarkistettava. |
| 30 | [HEOS virheilmoitus korjaus](https://chatgpt.com/c/691443a7-2ce4-8327-98d6-182a3e75d49c) | 2/1/1/0/1 | HE | S / P0. Käyttäjä ei halua etäkehitysympäristön käynnistävän kodin HEOS-toistoa. |
| 31 | [Siirrä git-repository VS Codessa](https://chatgpt.com/c/69144001-10f4-8325-a96c-4f5acde459c4) | 10/5/0/0/0 | M | M / P0. Reposiirto, puuttuva .git ja venv. Computers & Linux -siirtoehdokas. |
| 32 | [Versionhallinnan käytännöt](https://chatgpt.com/c/69142ab5-ad5c-832c-82d8-34816fbb3762) | 2/1/0/0/0 | R | P1. Vientiotikko on New chat; sisältö on SemVer-kysymys. Vastine CHANGELOGin versiointiperiaatteessa. |
| 33 | [Refaktorointi sähkön hinta](https://chatgpt.com/c/69139e66-ad5c-832c-8fc8-c77eac1619ed) | 45/23/22/3/0 | E | S / P0. Keskeytynyt refaktorointi; myöhempi REFACTORING ei todista vanhojen testivirheiden korjausta. |
| 34 | [Nimipäivälogiikan refaktorointi](https://chatgpt.com/c/69139a2e-8ae4-8331-b303-8e2aa80bf52e) | 10/5/11/1/2 | N | S / P0. Calendar-wrapperien yhteensopivuus ja testien oikeat patch-kohteet. |
| 35 | [Refaktorointi ja optimointi](https://chatgpt.com/c/69139865-d39c-8327-8c95-b0919636bdcd) | 6/3/1/0/0 | R | S / P0. Vanha refaktorointijono ja erillinen ladattava dokumentti. |
| 36 | [Refaktorointi ehdotus safe_cast](https://chatgpt.com/c/691392bc-7304-8330-be6c-14fb62e7b8e8) | 8/4/2/0/0 | W | S / P0. safe_cast ja vanhojen as_bool/as_int/as_float-nimien säilyttäminen. |
| 37 | [Refaktorointi wmo-mapit](https://chatgpt.com/c/69138f15-77d4-832e-8482-09ed3f6519fa) | 8/4/10/0/6 | W | S / P0. WMO-modulaarisuus; weather_mapping-yhteensopivuusrajapinta. |
| 38 | [Refaktorointi weather_fetch.py](https://chatgpt.com/c/69138d26-60ac-8332-a254-0fecdee86c23) | 6/3/3/1/0 | W | S / P0. Säätestin mock kohdistettava todelliseen HTTP-kutsuun. |
| 39 | [Refaktorointi jatkuu](https://chatgpt.com/c/69138a52-fc40-832e-849d-3ceb1a722ee6) | 6/3/8/2/0 | W | S / P0. Weather-viewmodelin vastuu ja uuden rajapinnan testitarve. |
| 40 | [Refaktorointi jatkaminen](https://chatgpt.com/c/691387cb-93b0-8332-848e-833fe98a978e) | 6/3/4/2/1 | N | S / P0. Nimipäivähelperit; debug-arvon None-käsittely testissä. |
| 41 | [Refaktorointi ja koodin yhdistäminen](https://chatgpt.com/c/691383f2-4278-832b-8926-aaec6f297a4d) | 6/3/5/2/0 | N | S / P0. Kalenterilogiikan yhdistäminen; historiallinen 80 testin tulos. |
| 42 | [Testikattavuus ja tulokset](https://chatgpt.com/c/69136afd-58dc-8325-9916-3948d5f3d3b0) | 16/8/3/1/1 | E | S / P0. Käyttäjän pyytämät coverage-omit logger_config/weather_debug löytyvät pyproject.toml:sta; sähköadapterien testivaatimukset säilyvät. |
| 43 | [Testitiedostojen rakentaminen](https://chatgpt.com/c/6913697b-f8c0-832c-9520-27fa682f442c) | 4/2/3/0/0 | T | S / P0. Utils-testit: builtins.print ja Streamlit-mock. |
| 44 | [HEOS-kortin testit](https://chatgpt.com/c/69136766-2b78-8333-bd1e-27f890b21627) | 8/4/3/1/0 | HE | S / P0. HEOS-kortin moduuli importlibillä; payload- ja painiketestit. |
| 45 | [Testi korttijärjestelmälle](https://chatgpt.com/c/6913662b-c588-8325-9151-f3f8c1db8021) | 6/3/1/0/0 | T | S / P0. Järjestelmäkortin moduuli- ja funktioimportin ero. |
| 46 | [Testit päivän zen kortille](https://chatgpt.com/c/691364f1-2afc-8329-8113-985cde94e757) | 6/3/4/1/0 | T | S / P0. Zen-cache eristettävä testeissä ja oikea moduuli tuotava. |
| 47 | [Testi epäonnistumisten korjaus](https://chatgpt.com/c/691363a6-f350-8332-ac1a-3920f269d836) | 4/2/6/0/0 | N | S / P0. Kalenterin cache ja UI-moduulin patchaus. |
| 48 | [Testifunktiot pytestilla](https://chatgpt.com/c/691362fc-3fe4-832b-b53a-005dd786ef6c) | 2/1/1/0/0 | T | S / P0. HTTP retry/JSON-testit ilman oikeita verkkokutsuja. |
| 49 | [Bitcoin testit ja kattavuus](https://chatgpt.com/c/691360d6-cba4-832f-91cc-17f663375936) | 6/3/5/1/0 | T | S / P0. Bitcoin-cache eristettävä; reload/mock-ehdotuksia. |
| 50 | [Testit sääfunktioille](https://chatgpt.com/c/69135f44-bd50-8330-a1b4-44aacce3d93a) | 2/1/8/0/0 | W | S / P0. Säätestien verkko, Excel-luku ja kellonaika mockataan. |
| 51 | [Testikattavuus ja raportti](https://chatgpt.com/c/69135945-d738-8329-9389-737ddc9c4f36) | 20/10/13/3/0 | T | S / P0. Sähköpalvelun testit ja tyyppirajaukset. |
| 52 | [Koodin refaktorointi](https://chatgpt.com/c/691356b2-1efc-8328-978a-cdb0d115c400) | 2/1/2/1/0 | E | S / P0. Sähkölähteet adaptereihin; palvelulle orkestrointi. |
| 53 | [Refaktoroinnin jatkaminen](https://chatgpt.com/c/6913551e-3d04-8332-80b8-6fe7c56097a9) | 2/1/2/1/0 | E | S / P0. Sähköparseri → normalisointi → 60/15 min laajennus. |
| 54 | [Refaktorointi ja Radon-tulokset](https://chatgpt.com/c/69135332-d398-8333-b5dc-a7c35b01bb1e) | 6/3/1/0/1 | R | S / P0. Radon-raportin ja refaktorointidokumentin ristiriidat. |
| 55 | [Merge commit without losing changes](https://chatgpt.com/c/6912f1fc-a084-832f-b718-6e33148a1aa6) | 52/26/33/8/3 | N | S / P0. Nimipäivä-API:n palautus ja yhteensopivuus; puuttuvia tiedostoliitteitä. |
| 56 | [Palauta rikottu koodi](https://chatgpt.com/c/6911bc93-7820-832e-8383-68ed6983994d) | 122/61/25/15/1 | N | S / P0. Liputus/pyhäpäivä ylimmäksi, auringot korttiin; CARD_NAMEDAY.md vastaa. |
| 57 | [Palaaminen toimivaan koodiin](https://chatgpt.com/c/6911ad83-6920-8328-9a57-4cde53d33f00) | 40/20/4/4/0 | N | S / P0. Rikkoutunut UI-palautus ja puuttuvat importit; ei nykyvikaväite. |
| 58 | [Refaktoroida dashboardin koodi](https://chatgpt.com/c/6910d2c1-0854-832b-89d0-fbb91b00c7f0) | 82/41/48/5/4 | N | S / P0. Säilytä nimipäivän tekstit ja auringon ikonit refaktoroinnissa. |
| 59 | [UML-skripti korjaus](https://chatgpt.com/c/6910f076-6334-8326-95f9-96c83ed20ba5) | 10/5/5/4/0 | U | S / P0. UML-generointi ja kaavion luettavuus; kuvat ovat historiallisia. |
| 60 | [Arvioi Radon-tuloksia](https://chatgpt.com/c/6910edaa-1f40-8333-ac59-9f49a7b1e8ea) | 6/3/1/0/1 | R | S / P0. Radon-tulosten perusteella rajattu jatkorefaktorointi. |
| 61 | [Refaktoroidaan bitcoin.py](https://chatgpt.com/c/6910eb2c-0458-8332-a3c0-2f822a57b8c5) | 4/2/2/1/0 | U | S / P0. Bitcoin HTTP/parsinta/pistemuunnos erilleen. |
| 62 | [Refaktorointi utils.py](https://chatgpt.com/c/6910e849-3e4c-832c-8b9c-f2e42c7c3575) | 6/3/1/0/0 | U | S / P0. Utils-vastuiden erotteluehdotus; tarkkaa nykyvastaavuutta ei vahvistettu. |
| 63 | [Refaktorointi sähkön hintakortti](https://chatgpt.com/c/6910e6aa-eb1c-8333-930b-9c671976fae6) | 2/1/1/0/0 | E | S / P0. 12 h / 15 min laskenta viewmodeliin ja yhteensopivuuswrapperit. |
| 64 | [Refaktorointi api.py-tiedostoon](https://chatgpt.com/c/691081d4-3ee8-8329-a8d7-5565bdd53e45) | 12/6/5/1/2 | E | S / P0. Sähkön data katosi refaktoroinnissa; käyttäjän onnistumiskuittaus. |
| 65 | [Refaktorointi ui.py:stä](https://chatgpt.com/c/69105622-4a48-832a-928c-f397f69a4ca1) | 24/12/12/9/0 | U | S / P0. UI-modulaarisuus ja regressiot. Aiemmin katkaistu viesti on nyt viennissä; alkuperäisten lähdeliitteiden saatavuus silti rajallinen. |
| 66 | [Merge ja salasanan suojaus](https://chatgpt.com/c/691050db-f10c-832e-b407-c3efa057da7c) | 9/5/5/0/2 | P | S / P0. HEOS-salaisuudet julkisen repon ulkopuolelle; .env/config-liitteet puuttuvat. |
| 67 | [Tidal kortti dashboardiin](https://chatgpt.com/c/690eeaa3-4998-8333-81a7-60278f493ef6) | 46/23/6/1/3 | HE | S / P0. HEOS-kortti ja kappaletiedon päivitys; kieli/DPR pois järjestelmäkortista. |
| 68 | [Julkaisun tarkistuslista](https://chatgpt.com/c/690b68e5-b1b0-832f-b5b4-25e5faefa7e9) | 65/33/31/6/5 | R | S / P0. Julkaisu ja kaksikielinen changelog; repo sisältää molemmat. |
| 69 | [Pylance virheet ratkaiseminen](https://chatgpt.com/c/690c6c7a-2654-8325-9fbd-e47d1266f77e) | 33/17/14/11/0 | U | S / P0. Polkuapu, tulkin valinta ja venv; historiallinen ympäristövika. |
| 70 | [Tasainen korttikorkeus](https://chatgpt.com/c/690b9582-b02c-8329-a0d7-2e7f3bdb1892) | 4/2/2/0/0 | U | S / P0. Nimipäivä- ja zen-korttien tasakorkeus. |
| 71 | [Zen rajapintojen lokitus](https://chatgpt.com/c/690b9451-2128-8330-921e-334724e88be2) | 2/1/0/0/0 | U | S / P0. Zen-lähteiden toiminnan lokitus; ei väitettä nykyisestä API-saatavuudesta. |
| 72 | [Lokihaun tarkistaminen api.py](https://chatgpt.com/c/690b8c7b-2980-832f-9a6a-d60ceac8c9fc) | 18/9/3/3/0 | E | S / P0. Sähkön 100-kertainen yksikkövirhe ja parseriapuri; kuvat historiallista näyttöä. |
| 73 | [Sähkönhinta 15 min](https://chatgpt.com/c/690b5749-7fb0-832f-8bc6-3dff34f96498) | 36/18/16/12/2 | E | S / P0. Aito 15 min data ja 48 palkkia / 12 h; tuntikeskiarvo haluttiin pois. Fallbackin tarkkuus eroaa aidosta varttidatasta. |
| 74 | [Korjaus Mermaid-tiedostoihin](https://chatgpt.com/c/690b4ce4-b750-8328-a182-9f1f1b99e7a8) | 6/3/11/3/0 | U | S / P0. Mermaid ilman ulompaa markdown-aitaa; renderöinnin korjaus kuitattu. |
| 75 | [Koodivirheen ratkaisu](https://chatgpt.com/c/6907b340-3a40-8329-845a-6aa41da09ad0) | 16/8/12/7/4 | W | S / P0. Pilvisyysarvon tyyppimuunnokset ja tulkki/riippuvuudet. |
| 76 | [Virheilmoitus ja ratkaisuvinkit](https://chatgpt.com/c/6907a62d-fde4-8331-a23f-1808e38dd78b) | 10/5/3/1/0 | U | S / P0. BTC-sarjafunktioiden importit; myöhempi toimivuus kuitattu. |
| 77 | [CSS latausongelma](https://chatgpt.com/c/6907a2b1-ae7c-8325-b593-16e748fcffb9) | 6/3/5/1/0 | U | S / P0. CSS:n merge-konfliktit ja tumma teema; toimivuus kuitattu. |
| 78 | [Synkkaus ja versionhallinta](https://chatgpt.com/c/69078f01-a154-832e-b9dc-07dd25bc96af) | 47/24/8/0/3 | P | S / P0. DeployToPi käyttää PiHost-nimeä; historiallinen systemd active -havainto. |
| 79 | [Korjaus git-merge-virheelle](https://chatgpt.com/c/69078c03-bb8c-832b-a1b1-41b2aaa7ee2a) | 2/1/0/0/0 | P | S / P0. Merge-konfliktimerkit Pythonissa; ei nykytilan vika. |
| 80 | [Python suoritusoikeuden korjaus](https://chatgpt.com/c/69078a3f-1504-8331-b3b6-7cb7f80a1b36) | 8/4/0/0/0 | P | S / P0. Venvin suoritusoikeus ja portin tuplainstanssit; suojausten poiskytkentä ei uusi suositus. |
| 81 | [Päivitys ja uudelleenkäynnistys](https://chatgpt.com/c/68fe481e-5d04-8326-9c1e-7caf83a85fce) | 18/9/0/0/0 | P | S / P0. Rebase-konflikti, päivitysskripti ja SSH-agentti. |
| 82 | [Git-merge konflikti python](https://chatgpt.com/c/69048893-1cf0-832c-82e5-0685f029a181) | 20/10/1/0/1 | P | S / P0. Venv/pyc/interpreter-ongelmat; ympäristökohtainen uudelleenluonti. |
| 83 | [Korjataan README.md linkit](https://chatgpt.com/c/69048346-2128-8330-85a8-996d1d7c1c20) | 15/7/1/1/0 | U | S / P0. README-banneri; vastine docs/images/banner_kotidashboard.png. |
| 84 | [Kotidashboardin kloonaus](https://chatgpt.com/c/6901d508-3720-8327-9ee3-161bf188517c) | 34/17/0/0/0 | P | S / P0. Kloonaus ja Git Sync -ehdotus; ei vahvistusta skriptin nykykäytöstä. |
| 85 | [Poista debug-tulosteet](https://chatgpt.com/c/68f7d902-643c-8327-a0c9-48c48e375897) | 8/4/4/1/1 | U | S / P0. UA-debuglaatikko pois dashboardista; käyttäjän onnistumiskuittaus. |
| 86 | [Refaktorointi Grokin avulla](https://chatgpt.com/c/68e760b4-c194-8332-bdf2-4b0b1e2c83dd) | 5/3/9/0/2 | U | S / P0. Sähköotsikko ja vanha ui.py; ladattava versio ei korvaa nykyistä moduulirakennetta. |
| 87 | [Kotiverkon optimointi](https://chatgpt.com/c/68f8edfd-e998-832a-b8b3-ff6596922377) | 48/23/7/5/0 | M | M / P0. Kotiverkon laitteet/osoitteet. Computers & Linux -siirtoehdokas. |
| 88 | [Auringon nousu ja lasku](https://chatgpt.com/c/68f7dbc7-2140-8328-ab0b-ca8f4ce6a777) | 6/3/1/0/0 | N | S / P0. Auringonnousu ja -lasku nimipäiväkorttiin; dokumentoitu CARD_NAMEDAY.md:ssä. |
| 89 | [Tallinnan aktiviteetit ehdotukset](https://chatgpt.com/c/68eca5d6-eafc-8330-8ddd-c08b846c4192) | 2/1/0/0/0 | M | M / P0. Matkailuaihe; Travel & Camping -siirtoehdokas, ei sovelluspäätöstä. |
| 90 | [Korjaus y-akselin tekstille](https://chatgpt.com/c/68f14502-a254-832f-bd0e-8e044dab80c1) | 44/22/17/15/0 | U | S / P0. Otsikosta poiketen selaimen/laiteversion tunnistus; historiallinen UA-rajoite. |
| 91 | [Denon ja Tidal ohjaus](https://chatgpt.com/c/68f0b355-c6f8-832b-9ada-95388b5383a8) | 2/1/0/0/0 | HE | S / P0. HEOS/Tidal-integraation alkuperäinen ehdotus; nykyinen toteutus erillinen. |
| 92 | [Sääkortin ennusteiden vaihto](https://chatgpt.com/c/68efb3e1-385c-8333-b7ea-d972243ef5bd) | 23/11/3/2/1 | U | S / P0. Bitcoin 24h/7d/30d-valinta ja valitun painikkeen korostus. |
| 93 | [Poista trace-tulosteet](https://chatgpt.com/c/68ed4943-701c-8332-836a-fedc87ae659b) | 6/3/5/0/0 | U | S / P0. Sääikonien debug/trace pois normaalinäkymästä; vanhojen apurien poisto vain ehdotus. |
| 94 | [Korjaus pörssisähkön kuvaajaan](https://chatgpt.com/c/68ef87eb-4598-8332-b1e2-733641005474) | 2/1/1/0/0 | E | S / P0. Negatiiviset sähköhinnat näkyviin; nykyinen viewmodel käyttää myös datan minimiä. |
| 95 | [PoE virransyöttö Raspberry Pi:lle](https://chatgpt.com/c/68ef7346-701c-8331-95e1-8c1e118070d8) | 32/16/3/3/0 | M | M / P0. PoE/virtalähdeaihe. Computers & Linux -siirtoehdokas; ei hankintapäätöksen vahvistusta. |
| 96 | [Tarkista nimipäivät-kortti](https://chatgpt.com/c/68e7c8b9-8a84-832c-88e8-3527de0d271c) | 54/27/18/6/7 | N | S / P0. Nimipäiväkortin statusrivi ylimmäksi; vastine CARD_NAMEDAY.md. |
| 97 | [Käännä WMO säätermitaulukko](https://chatgpt.com/c/68e7f312-6f08-8333-a4e9-537ae8fd4b6c) | 18/9/7/2/1 | W | S / P0. WMO Excelin päivä/yö-sarakkeet; data/WMO_Foreca-koodit.xlsx repossa. |
| 98 | [Vaihto sääikoneet Forecaan](https://chatgpt.com/c/68e7907e-c348-832f-9a80-814dd398725c) | 38/19/19/6/2 | W | S / P0. Foreca-ikonimappaus ja trace; vanhoja debug-ohjeita ei käyttöönoteta. |
| 99 | [Bitcoin skaalaus parannus](https://chatgpt.com/c/68e7862f-4e20-8332-81b9-125f1b962dd3) | 16/8/3/2/0 | E | S / P0. Vanha nollaan sidottu sähköasteikko on korvautunut negatiiviset hinnat sallivalla vaatimuksella. |
| 100 | [Otsikkotyyli yhtenäistäminen](https://chatgpt.com/c/68e78279-13d4-8329-bb64-50095912cc7c) | 10/5/7/1/1 | U | S / P0. Yhtenäiset otsikot ja yhteiset värit configiin. |
| 101 | [Kotidashboardin luominen](https://chatgpt.com/c/68d7f2ed-e070-832c-9f16-0169e4604001) | 64/32/10/5/0 | U | S / P0. Alkuperäinen jatkuvasti näkyvän tablettikoontinäytön tarkoitus on nyt luettavissa. Vanha HTML/JS-prototyyppi ei ole nykyisen Streamlit-repon palautuspaketti. |
| 102 | [Hyvä tabletti kotidashboardiin](https://chatgpt.com/c/68d986bb-4668-8330-883e-515684bfa1ea) | 30/15/0/0/0 | M | M / P0. Käyttäjän Lenovo M9 -tilaus löytyy historiasta; yleiset laite- ja palvelinvaihtoehdot Computers & Linux -siirtoehdokas. |
| 103 | [Päivittäinen sitaatti lisäys](https://chatgpt.com/c/68e612eb-fe6c-8330-aeaa-0c235141666a) | 60/30/16/9/2 | U | S / P0. Zen-tekijärajaus ja erillinen taustallinen kortti; tekijärajaus puuttuu nykyisestä verkkohakulogiikasta. Fully Initial Scale -onnistumiskuittaus säilytetään. |
| 104 | [Korttien järjestyksen muutos](https://chatgpt.com/c/68e663a5-39b8-8330-b29e-3badf18d2f52) | 12/6/2/1/0 | U | S / P0. Vanha järjestys: nimipäivät/zen → sää → sähkö → Bitcoin → järjestelmätila. Nykyinen main.py sisältää myöhempiä lisäkortteja. |
| 105 | [Testiskripti ohjeet](https://chatgpt.com/c/68e5538d-4878-8325-a486-561ab0c4a9b7) | 38/19/9/7/1 | E | S / P0. Lenovo M9 pystyssä ja Fully Kiosk; tumma responsiivinen yhden ruudun koonti. Historiallinen hyväksymisympäristö, ei nykytilan testitulos. |
| 106 | [Muutos kotidashboardiin](https://chatgpt.com/c/68e63b43-12b4-8327-b677-b91796e3aa15) | 18/9/4/3/0 | U | S / P0. Bitcoin EUR/ATH, välilyönti tuhaterottimena ja kuvaajan marginaalit. |
| 107 | [Fonttimuutokset dashboardille](https://chatgpt.com/c/68e645a8-44b8-8332-a5e2-4fff1650a7bb) | 48/24/20/13/2 | U | S / P0. Fontti/asettelu ja monistuvat sähkökortit; käyttäjän onnistumiskuittaus. |
| 108 | [Kotidashboardin sääkortti](https://chatgpt.com/c/68e5fa5b-9880-8329-8e14-d8f23be854d4) | 32/16/18/9/4 | E | S / P0. Sähköstä ylimääräiset kortit/keskiarvot pois; ei nykyisen hintabadgen poistopäätös. |
| 109 | [Muutos aikaskaalaan 7 päivään](https://chatgpt.com/c/68e66092-e4a8-8330-a96f-79e1be18683d) | 6/3/1/0/0 | U | S / P0. Bitcoin-historia 7 päivään ja päiväkohtaiset aikamerkit; myöhemmin 24h/7d/30d. |
| 110 | [Päivitysongelma Fully Kioskissa](https://chatgpt.com/c/68e68859-e824-832c-ab05-78102c22977e) | 14/7/4/2/1 | U | S / P0. Fully-näkymän marginaalit ja otsikkovälit; käyttäjän spacer-valinta. |
| 111 | [Pörssisähkön otsikkoidea](https://chatgpt.com/c/68e6b43f-0ddc-832a-88cc-a1e30847d458) | 10/5/1/0/0 | E | S / P0. Sähköotsikkoon nykyhinta ja seuraavat 12 h, ei muutosprosenttia; nykyinen 15 min otsikko on myöhempi. |

Vientitiedoston ja aiemman hakemiston otsikkoero: keskustelutunnuksen `69142ab5-ad5c-832c-82d8-34816fbb3762` otsikko on viennissä **New chat**, aiemmassa luettelossa **Versionhallinnan käytännöt**. Sama tunnus kohdistaa sen luotettavasti; otsikkoeroa ei tulkita puuttuvaksi keskusteluksi.

## 5. Liitteiden tunnistekohtainen saatavuus

Alla ovat kaikki **734 eri tiedostotunnusta**. Sarake **kpl** säilyttää neljän kahdesti esiintyvän tiedostotunnuksen esiintymät, joten summa on 738. Keskustelunumero kohdistaa liitteen osion 4 täydelliseen keskustelutunnukseen. Samannimisiä eri tunnuksia ei yhdistetä. Tarkka viestiin kohdistuva metatieto säilyy yksityisessä paikallisessa inventaariossa ja alkuperäisessä ZIP:ssä.

- **K:** alkuperäiseksi kohdistuva kuvatiedosto luettavissa ZIP:stä; visuaalinen yleiskatsaus tehty.
- **T:** ei erillistä alkuperäistä tiedostoa; keskustelun tekstiviitteessä katkelma, jonka täydellisyyttä ei todisteta.
- **M:** nimi/tunnus/MIME/koko saatavilla, sisältöä ei palautettu käyttökelpoisena tiedostona tai ei-tyhjänä tekstikatkelmana.
- Kaikki liitteet **S/P0**, lukuun ottamatta P1-keskustelun 15 kuvaa, jonka myöhempi poisto arvioidaan kyseisen kokonaisuuden kanssa. Kuvia, katkelmia tai salaisuuksia ei ole julkaistu; tämä taulukko on vain saatavuusmetatietoa. MAC-taulukot ja asetustiedostot ovat yksityisiä lähteitä, eivät julkiseen repoon siirrettävää raakadataa.

<details>
<summary>Avaa 734 liitetunnuksen inventaario</summary>

| Tiedostotunnus | Keskustelu nro | kpl | Alkuperäinen nimi | Saatavuus |
| --- | --- | --- | --- | --- |
| `file_00000000d4b462439d500eaf25c4e378` | 101 | 1 | `e35d8541-f0a1-476a-af9d-1b275de6dbe3.png` | K |
| `file_000000001cac61f4b03e685c446d3b2e` | 101 | 1 | `0db7a076-f949-4115-93ce-12fc65a9afbb.png` | K |
| `file_00000000c62c61f49ce3a5aa65e8c961` | 101 | 1 | `9d95e78c-33af-4c47-b885-9c68bbab430e.png` | K |
| `file_000000003a806246b2c976f732207cc5` | 101 | 1 | `835d9ac2-1301-4ba6-a9d2-0fb03008f755.png` | K |
| `file_0000000088306246aeee883b397a878f` | 101 | 1 | `532b5ba9-2150-4b09-9b93-e06eddda42be.png` | K |
| `file_000000004b4c62438e707ba929c677a5` | 101 | 1 | `nimipaivat_fi.json` | M |
| `file_00000000e62c62439167983cacc68301` | 101 | 1 | `dashboard_full.py` | M |
| `file_000000009d3c6243867248dec2a733e6` | 101 | 1 | `index.html` | M |
| `file_0000000010346243991261d4845427ec` | 101 | 1 | `app.js` | M |
| `file_0000000011cc6243b355200cc5c9731d` | 101 | 1 | `app.js` | M |
| `file_00000000cc60622f93b62eee5b7e40bb` | 105 | 1 | `f970ba08-66ba-4f91-96e1-81b3603d8da8.png` | K |
| `file_00000000750c62468bc254ccd833ed03` | 105 | 1 | `c2d051f4-f46a-451e-ae2d-f59025bc8286.png` | K |
| `file_00000000ad5061f4bd6fac9614b83023` | 105 | 1 | `app.py` | M |
| `file_00000000d13c61f5ad80a306d0393006` | 105 | 1 | `d8722347-3782-48d3-a0cf-f54893dccc47.png` | K |
| `file_00000000512c61f6a748041295b44cfe` | 105 | 1 | `nimipaivat_fi.json` | T |
| `file_00000000514861f4846599673c8b4e0f` | 105 | 1 | `333072fe-772e-4547-a461-36bc7e4ce103.png` | K |
| `file_00000000536861f4b98947251779fdb1` | 105 | 1 | `f47b11aa-f49e-4eca-aece-ed89a245b71f.png` | K |
| `file_0000000004ac620a81ed87d59e3fbebe` | 105 | 1 | `ccb4e5ea-1303-485b-aa1d-2a5ce499169c.png` | K |
| `file_00000000228861f6a401daf29e4857f3` | 105 | 1 | `bf3e0a91-f1c8-44ad-a431-7be14492afef.jpeg` | K |
| `file_000000000ad0620abe4bac1a15b020f0` | 108 | 1 | `2b1c89be-8dce-45c3-986d-153190d35df6.png` | K |
| `file_00000000bce86230b15e4c756f4a9ebf` | 108 | 1 | `app.py` | M |
| `file_000000000b30622fa4c237be1d80a93e` | 108 | 1 | `a9af0c05-ca52-4aac-b395-52b1cca01903.png` | K |
| `file_0000000076e0622f91355e0173c3e59d` | 108 | 1 | `app.py` | T |
| `file_0000000046e061fb8177a798583eb7f6` | 108 | 1 | `c79eddd1-e63a-4756-86cf-ed9e6918a6cb.png` | K |
| `file_00000000f14c620a80aea3037e82c022` | 108 | 1 | `app.py` | M |
| `file_00000000866c6243a2fb35de67ed26b1` | 108 | 1 | `app.py` | T |
| `file_00000000541c61f5a59b5d3fb227495d` | 108 | 1 | `26bf84c4-be7f-4246-8c80-0a59ed8d6f57.png` | K |
| `file_000000007dbc6246925fcf536b15c1cc` | 108 | 1 | `app.py` | T |
| `file_00000000870462439fa623ca7b0693a1` | 108 | 1 | `079339c7-27b3-4be7-9c71-c579188e314a.png` | K |
| `file_00000000103861fb92cd80e27f9edaf3` | 108 | 1 | `3218ddfd-c974-4461-a914-38d93fa37c81.png` | K |
| `file_00000000258c61f59ab43dbf4802dbe6` | 108 | 1 | `app.py` | T |
| `file_000000004e74622f8baf2b4d260615c1` | 108 | 1 | `e2ba7fcc-fb6f-403d-a342-5a899f8b02b8.png` | K |
| `file_00000000552c6243b030eaa6c093b774` | 108 | 1 | `app.py` | M |
| `file_00000000eee061fa814f27bc743058f6` | 108 | 1 | `fded87e0-236a-4655-9f97-9b488d43123c.png` | K |
| `file_000000004fdc623087633597032c60f9` | 108 | 1 | `app.py` | M |
| `file_00000000bc4c622fbe297175f21e4f3f` | 108 | 1 | `e651a841-e467-4559-b344-29c82c689055.png` | K |
| `file_00000000ced4622f803c42192cf008a5` | 108 | 1 | `app.py` | M |
| `file_000000006638620a8ef5ff1824ac56e4` | 103 | 1 | `2d313ed3-848c-4b60-a6bf-35cf32fa94c1.png` | K |
| `file_000000008734620aa33e219d05b037bf` | 103 | 1 | `app.py` | M |
| `file_0000000091bc6246adf25b438daccb4b` | 103 | 1 | `f16d06d7-f28e-4f23-8fa3-36281299e412.png` | K |
| `file_00000000bc6861f4818b9fd8dfba8d8f` | 103 | 1 | `69cae376-074b-4318-a085-7789309327f6.jpeg` | K |
| `file_00000000392861f595918924b6b59955` | 103 | 1 | `app.py` | T |
| `file_000000008674622f8100b8e01fd1a8aa` | 103 | 1 | `7731325c-256a-4db3-a32c-fb641ca65c3e.png` | K |
| `file_00000000430461f5aabf93890ba7210d` | 103 | 1 | `app.py` | M |
| `file_00000000e5f8620a935a9ea33ffed873` | 103 | 1 | `1f5ec357-4d91-419b-a9d4-a18a1b5d9791.png` | K |
| `file_000000004ae4620a87139fda9da4376a` | 103 | 1 | `9476f843-2510-49a5-a966-db97ea439d60.png` | K |
| `file_00000000105c620a92149e3f4db3261f` | 103 | 1 | `app.py` | T |
| `file_0000000054b8620ab644b3596c58362b` | 103 | 1 | `app.py` | M |
| `file_000000004124620aabbcc8cba8c70c01` | 103 | 1 | `app.py` | M |
| `file_00000000c578620a9e063f08f47f0ec0` | 103 | 1 | `6d826393-ca96-4478-833b-c7c40d880d97.png` | K |
| `file_000000001a74620a95267c3ea6bada6b` | 103 | 1 | `app.py` | M |
| `file_000000007c6c620aacafd4d362fc161b` | 103 | 1 | `c817de08-b280-4815-9c4a-aebd554ca1b3.png` | K |
| `file_00000000e7bc620aa7f20c5875c24bbf` | 103 | 1 | `92f33993-de3d-48a8-9d61-242d82ab3b3a.png` | K |
| `file_00000000e11862439e9d900f598b6f92` | 106 | 1 | `cbc28d31-fa97-4777-bd1d-f0ae3af55bfe.png` | K |
| `file_00000000931062439c3f15dce992f985` | 106 | 1 | `370c5bcc-7c67-48f6-853e-f2cc28dc8a40.png` | K |
| `file_0000000077f46243bf2b8b7bfa52fc3e` | 106 | 1 | `app.py` | M |
| `file_00000000e5286246b77920a6f978d953` | 106 | 1 | `b98dff80-b5f8-42bd-9ef6-2e9b45e6d026.png` | K |
| `file_000000000c786246bc2503443bc81d2d` | 107 | 1 | `ad29e404-4cc3-4410-af48-d30aff7cad2e.png` | K |
| `file_00000000dca461f48e41dbfa8fcab092` | 107 | 1 | `10dd5f08-e5f7-4e10-bcf0-2619f808ae6a.png` | K |
| `file_0000000074306243a6c3e930cdcde9cf` | 107 | 1 | `app.py` | T |
| `file_00000000b594624388effee4346eb014` | 107 | 1 | `app.py` | T |
| `file_0000000057006243947156854523568b` | 107 | 1 | `f197d484-3363-4314-aeba-662adb1ca7a7.png` | K |
| `file_0000000077b862439bfad71fd97ce25d` | 107 | 1 | `app.py` | M |
| `file_000000001d70620aa104c2f27bea1752` | 107 | 1 | `a0aede0b-cdf1-4b18-8422-c6f7ac66627e.png` | K |
| `file_000000000774620a9e510a454e91b829` | 107 | 1 | `d7394c95-b2a9-45c5-b43e-5ee5d336948a.png` | K |
| `file_00000000df6c62438378170c6a21ac86` | 107 | 1 | `app.py` | M |
| `file_000000001ef8624395b3bacefdff9880` | 107 | 1 | `96ad4cbd-d09e-43de-a9c2-d21461647d1c.png` | K |
| `file_00000000d0a062469972b1156528417d` | 107 | 1 | `af4d20c0-b721-4e4a-aeaf-c194552a1df8.png` | K |
| `file_00000000a37c620a9b6d7ccbf6a46c08` | 107 | 1 | `d29c442c-4030-4ca2-8a08-98a2abf58a6b.png` | K |
| `file_0000000037e86243991b057d670cf678` | 107 | 1 | `e50c2355-37a1-40ec-a771-eca25d64800b.png` | K |
| `file_00000000639462439f9d9881a5574470` | 107 | 1 | `fe5153ed-0d29-4844-bbc4-3f06bde155e5.png` | K |
| `file_00000000e3d461f484d7948fc4c116bb` | 107 | 1 | `app.py` | M |
| `file_00000000f5b86246bd2c71931e13f326` | 107 | 1 | `1154f033-b3bd-4507-b7ce-443ed3239ea6.png` | K |
| `file_000000002c0c624386aa9fa44fb4df30` | 107 | 1 | `app.py` | M |
| `file_00000000ae586246be74197dee58be4a` | 107 | 1 | `app.py` | M |
| `file_0000000098ec624385c381aedf4a5d78` | 107 | 1 | `0757c899-cb19-46c3-9df9-616c2dcb7327.png` | K |
| `file_00000000afa46243b655ed885e2ece75` | 107 | 1 | `575a7bcf-c9e0-4b81-8353-2afea7d4d3a8.png` | K |
| `file_00000000c4f861f7afe392ba94362605` | 109 | 1 | `app.py` | M |
| `file_000000000f4861fbba68708870b36b89` | 104 | 1 | `41b14964-18c5-4db3-874d-e68b9553e60e.png` | K |
| `file_00000000d54061f8913451abdab1e406` | 104 | 1 | `app.py` | M |
| `file_0000000000e061f7bc6327605b84cd58` | 110 | 1 | `app.py` | T |
| `file_00000000887c61f49ab3a302be2a43fd` | 110 | 1 | `style.css` | M |
| `file_00000000ef1861f59dff048a6a473292` | 110 | 1 | `70c65905-4a51-49df-a1aa-97fe4de66854.png` | K |
| `file_00000000ae1061f49c2b8bf9dfe4d56b` | 110 | 1 | `ad3af5d2-25c1-4520-98f7-bdb9f177f4af.png` | K |
| `file_00000000a684624394160120cbe8a2c0` | 111 | 1 | `app.py` | M |
| `file_00000000ef0461f589c4f012094b67e1` | 86 | 1 | `api.py` | T |
| `file_000000006110622fb4485e41ab815e88` | 86 | 1 | `config.py` | M |
| `file_00000000011c622f9b5db85df7772955` | 86 | 1 | `main.py` | M |
| `file_000000004e3861f590b0cc363a2d870d` | 86 | 1 | `ui.py` | T |
| `file_000000009ae461f5a1a8c6848890df19` | 86 | 1 | `utils.py` | M |
| `file_000000002fec61f5b8b9e791ce28d49d` | 86 | 1 | `config.py` | M |
| `file_00000000570c61f5ad3f0e18c3b89dea` | 86 | 1 | `main.py` | M |
| `file_000000005c7461f5bd2ecf4f5a5a7755` | 86 | 1 | `ui.py` | M |
| `file_0000000047a0622fbfb7114eaf5068d2` | 86 | 1 | `utils.py` | M |
| `file_000000003d7c620a8567fd08affaae97` | 100 | 1 | `a238aa1e-9873-4f1f-bd63-a8179967ad19.png` | K |
| `file_00000000f3ec6246a837b3a245546282` | 100 | 1 | `api.py` | M |
| `file_000000003c2c6246be0fbd2e9e3f563a` | 100 | 1 | `config.py` | M |
| `file_000000002c1462439e560861cb511932` | 100 | 1 | `main.py` | M |
| `file_00000000c3a061f4984600024830377b` | 100 | 1 | `ui.py` | T |
| `file_000000006eb06246a0cf76f48e66756f` | 100 | 1 | `utils.py` | M |
| `file_0000000003ec61f4a56096f7053ba699` | 100 | 1 | `weather_icons.py` | M |
| `file_0000000018a862468dd276d7452c3247` | 99 | 1 | `ui.py` | M |
| `file_00000000c9c4624697d2a907c0518b41` | 99 | 1 | `671242b0-781d-42ed-9f6b-f8adefbacd89.png` | K |
| `file_000000006314620a849fb9e929455349` | 99 | 1 | `4914513c-231b-4c44-85b5-d3678c09e397.png` | K |
| `file-Ba6XrDJVRUooTMAD4a35VY` | 98 | 1 | `saaikoinit.zip` | M |
| `file_00000000a05c61f4a9dff0c53c239a2c` | 98 | 1 | `08e4ee5b-baa3-46c7-a671-e0c869089cd3.png` | K |
| `file_000000000a046243b1b422bf46cb8946` | 98 | 1 | `weather_icons.py` | T |
| `file_00000000fddc6246ab07fcb624fb1cfb` | 98 | 1 | `api.py` | T |
| `file_00000000b7c862438105c4a4b930e75d` | 98 | 1 | `f408586c-cecb-43bd-9d8d-6db8ec86f94e.png` | K |
| `file_0000000037106246ba674ba37a77e9ca` | 98 | 1 | `a574561f-c3b2-4bd4-aaf3-d4fd55af9f82.png` | K |
| `file_00000000d6186243b6c980a0cec3568c` | 98 | 1 | `b6af54cb-8a4e-4cde-a4f8-82f25bf6ad35.png` | K |
| `file_000000008a9c62439bfe29094066c551` | 98 | 1 | `api.py` | M |
| `file_00000000e96c61f496d823e8870e0b5f` | 98 | 1 | `ui.py` | M |
| `file_000000003a7062439646d002bc080d79` | 98 | 1 | `weather_icons.py` | M |
| `file_000000002be861f89f9ce1fb7c34d861` | 98 | 1 | `api.py` | M |
| `file_00000000e18061fdbbfa637a38b5faf6` | 98 | 1 | `config.py` | M |
| `file_000000004cf862439e21940a851037ba` | 98 | 1 | `api.py` | M |
| `file_0000000013b0624391634204b1268a10` | 98 | 1 | `ui.py` | M |
| `file_0000000056c062439d785fdd6d7e6116` | 98 | 1 | `weather_icons.py` | M |
| `file_00000000bcf861faae2782d202476351` | 98 | 1 | `api.py` | M |
| `file_0000000084546246829e8fc8536646f9` | 98 | 1 | `ui.py` | M |
| `file_00000000ce2462468515168e0a5993a0` | 98 | 1 | `70b0ef36-4ee6-483b-bf65-bb1db00b31ac.png` | K |
| `file_0000000073c862439bb1e3f189c5a81f` | 98 | 1 | `d2f4246d-9fff-496e-83a2-3be1a7543f0f.png` | K |
| `file_000000004fac6246aaf714c03f3b98b3` | 96 | 1 | `fdbd3ad4-e66c-4bf0-9921-a6af1a8569e2.png` | K |
| `file_0000000064f86246ac968960b466d9e1` | 96 | 1 | `2fa23c55-3f0d-4e5d-a252-80ce5dd51c94.png` | K |
| `file_000000009c1c6209bff7625d77223afe` | 96 | 1 | `ui.py` | M |
| `file_00000000f21c61fa93b466dc2641d745` | 96 | 1 | `09eb74c6-9ad5-4488-9ffb-6b9ec0c4cb37.png` | K |
| `file_0000000018d062468ee6a22bdc6512ce` | 96 | 1 | `f85c17ce-3bf1-4ca9-9256-d927a6a03b7f.png` | K |
| `file_00000000712c620ab850b74e0102ad43` | 96 | 1 | `api.py` | T |
| `file_000000007bac6243bc8ba1fce933964f` | 96 | 1 | `nimipaivat_fi.json` | T |
| `file_000000008c40620abba4bfbb2a2c8a68` | 96 | 1 | `ui.py` | T |
| `file_00000000a70c6246b812a8e7da04a31e` | 96 | 1 | `style.css` | M |
| `file_0000000070dc6246a305ec8cd0f3a616` | 96 | 1 | `ui.py` | M |
| `file_00000000142861f6a11829ec8019c63a` | 96 | 1 | `8e77b4ae-d4d4-4e0d-a636-d32925844bf9.png` | K |
| `file_0000000059406246acfa46c5936398cd` | 96 | 1 | `api.py` | T |
| `file_000000005c0461f4a53d3a1c28db0885` | 96 | 1 | `config.py` | T |
| `file_00000000cfec62438f4d09402a1c45cf` | 96 | 1 | `main.py` | M |
| `file_000000004c3c61f4bda4be6227545b2b` | 96 | 1 | `ui.py` | T |
| `file_00000000ec94620a9c082c148266fa26` | 96 | 1 | `utils.py` | M |
| `file_000000001df4624682a1f2958c082ebd` | 96 | 1 | `ui.py` | T |
| `file_00000000e72861faa578da0321bfb0e8` | 96 | 1 | `bb790835-f933-40c8-858a-eec44b18e5d0.png` | K |
| `file-UjGHcfZ9ZGM7vj2uC2bXL1` | 97 | 1 | `WMO_Foreca-koodit.xlsx` | M |
| `file_0000000019a061f79d208c610d88c634` | 97 | 1 | `api.py` | T |
| `file-54rU1mNzvWc5FyHUXYDDPh` | 97 | 1 | `WMO_Foreca-koodit.xlsx` | M |
| `file_00000000022461f7874274589986d944` | 97 | 1 | `api.py` | M |
| `file_00000000ae3461f7bf4f88bb7c307726` | 97 | 1 | `ui.py` | M |
| `file_00000000a308620a9665918905e3fb1c` | 97 | 1 | `ff2161a1-c7d6-4f77-ace1-a86b2a2d49c9.png` | K |
| `file_00000000addc61f789b16391aabecf02` | 97 | 1 | `75f8c422-4a37-483e-9d71-012dc8c2f653.png` | K |
| `file_0000000055d061f69f8e2e7169133612` | 93 | 1 | `ui.py` | M |
| `file_00000000620c61f79718345e577438cf` | 93 | 1 | `api.py` | M |
| `file_000000002b6c61f7b2951d6d1c9fee26` | 93 | 1 | `main.py` | M |
| `file_00000000251861f7a6d08f130162cc45` | 93 | 1 | `ui.py` | M |
| `file_00000000b8e061f7909b4c6647b34811` | 93 | 1 | `utils.py` | M |
| `file_0000000051b461f5bcfcd11ddc2e4109` | 95 | 1 | `97191370-84e2-4cdf-8968-0760d4d4699b.png` | K |
| `file_000000002a4461f599504476fb2bac14` | 95 | 1 | `61656772-c990-4988-9712-8a98f625e68e.png` | K |
| `file_0000000096b061f5bb057736a589796e` | 95 | 1 | `6af4a14d-5ef0-434a-b181-92852171a277.png` | K |
| `file_00000000eeb0620a90641a393c510998` | 94 | 1 | `ui.py` | M |
| `file_00000000070861f687f88c730676aeb6` | 92 | 1 | `5c2a8951-ee9e-4ea4-bd60-49eb2a012ded.png` | K |
| `file_00000000fb5461f69e1b9d6e6511a19a` | 92 | 1 | `66923dbc-4592-4ffd-9f4e-dc39aa2c27b3.png` | K |
| `file_0000000024d861f69c2c6b08cee98b56` | 92 | 1 | `api.py` | T |
| `file_00000000463c61f48f03491ae97b0ede` | 90 | 1 | `31e55a5b-d66b-4543-b849-fbe9cf22e7ee.jpeg` | K |
| `file_00000000095062469dcf83ec5036319c` | 90 | 1 | `036ecec7-fc14-4185-b28c-a28241bafd05.png` | K |
| `file_00000000b3686243b09aac9fb111ca62` | 90 | 1 | `4b101cbd-8880-4f24-887c-a0cd6bc4ee67.png` | K |
| `file_0000000025f86246baa37c253b479893` | 90 | 1 | `58861317-0fc1-4743-a47f-2f1fbf1a4a8b.png` | K |
| `file_0000000086d06243af09435ffe0c60a0` | 90 | 1 | `f02774e0-124a-4fef-b740-e41515af24c7.png` | K |
| `file_00000000e828620a8a384b20cba9610c` | 90 | 1 | `9807ecb6-77fa-4133-b4e2-5cf4221fc36b.png` | K |
| `file_0000000006c46243bdb6cd2b7ac3428b` | 90 | 1 | `f8fad558-34f6-489f-9d0e-fca8c3c673e6.jpeg` | K |
| `file_0000000059806243be5b0c108f6d2526` | 90 | 1 | `ui.py` | M |
| `file_00000000d4786243ab20432e628949fc` | 90 | 1 | `b62b0780-acbf-4f2c-953b-43d5dcaa6d85.png` | K |
| `file_000000009760620aa5f2cf1f945175b6` | 90 | 1 | `9be1808e-60fa-4a87-bdf7-5e5e30d95e0d.png` | K |
| `file_00000000ef28620a8687e4000ef303f3` | 90 | 1 | `0f45d369-0645-494a-baa9-f1bdf6ba59f0.png` | K |
| `file_00000000c884620aaa03ce75d5bb3af9` | 90 | 1 | `72bade5a-711f-4b03-be39-dae343144b37.png` | K |
| `file_00000000a5e861f4bf158530a1a64b8d` | 90 | 1 | `c67d738d-f93a-46b9-82f8-7f80fc02ae1f.png` | K |
| `file_0000000015106246a3fb9ef3c91b2b78` | 90 | 1 | `a85fffd6-d616-40c0-b50e-c1b788f759ac.png` | K |
| `file_000000006bb0624683c0f6163e99077b` | 90 | 1 | `8438cc53-8407-457c-98b5-c4185a01edb9.png` | K |
| `file_00000000a12c620ab804c52d48574557` | 90 | 1 | `080769a4-4886-40ba-8b5e-a42b1faab18f.png` | K |
| `file_00000000623c620a804d5eec90dc3b65` | 90 | 1 | `ui.py` | M |
| `file_00000000e37c61fda23bc5272228f8a8` | 85 | 1 | `api.py` | M |
| `file_00000000cf58620a92e9dc34b611cd45` | 85 | 1 | `utils.py` | M |
| `file_000000004ab4620980b5be22d6aed03b` | 85 | 1 | `ui.py` | T |
| `file_00000000d78c62468c295798eaeba8d8` | 85 | 1 | `b615a842-ec02-40ad-bc39-8f77d70b0441.png` | K |
| `file_00000000632061f681713befbc9fd35b` | 88 | 1 | `ui.py` | M |
| `file_00000000776061f48fdb63edb9677904` | 87 | 1 | `e4be6963-9172-48eb-bc12-365cdcb82f43.png` | K |
| `file_000000007364620ab2eed137f9171a00` | 87 | 1 | `cd3797a8-7dfe-4369-aa87-7ab805b41288.png` | K |
| `file-3bWz9vAE13ACrfKVENVjJC` | 87 | 1 | `MAC-osoitteet.csv` | M |
| `file-9JArKL9Bt37YcsJG3VRMVA` | 87 | 1 | `MAC-osoitteet.xlsx` | M |
| `file_00000000019461f7846428d272f057d5` | 87 | 1 | `Screenshot 2025-10-22 163837.png` | K |
| `file_00000000612061f79c178b6570c365f5` | 87 | 1 | `Screenshot 2025-10-22 163851.png` | K |
| `file_00000000426861f7bb519b8d32110ff6` | 87 | 1 | `927070fa-d015-4b4b-a825-9147fca43220.png` | K |
| `file_00000000c9a061f5bb567efd41a0981d` | 83 | 1 | `f97c44b5-b864-49c7-acac-f61e5754d15e.png` | K |
| `file_0000000029d861f5a3e2a19a33e9bdfa` | 82 | 1 | `config.py` | T |
| `file-PoJvapguUDsPUWWcR4LEEW` | 78 | 1 | `GitSync.bat` | M |
| `file_0000000096947243b122e00f92679525` | 78 | 1 | `update.sh` | M |
| `file_00000000a8a471f4af3ae1750bd8c9ea` | 78 | 1 | `requirements-windows.txt` | T |
| `file_00000000df54720aa3676f424ec65fd2` | 78 | 1 | `update.sh` | T |
| `file-FNwTrabfXvs3iWrY8KeXiH` | 78 | 1 | `.editorconfig` | M |
| `file-DCCJF1QVvYi8M8LEQpduqw` | 78 | 1 | `.gitattributes` | M |
| `file-RLy6ReNuz7XbaZdLSCZ1TN` | 78 | 1 | `.gitignore` | M |
| `file_00000000992472469d8991e884eebefe` | 78 | 1 | `requirements-linux.txt` | T |
| `file_000000008e5871fb808af98faf1f4506` | 77 | 1 | `style.css` | M |
| `file_00000000fddc71f4be40d68915005276` | 77 | 1 | `config.py` | M |
| `file_000000007be4720e972e1f34345797d5` | 77 | 1 | `main.py` | M |
| `file_00000000b9a471f796c61a10a143cc8f` | 77 | 1 | `ui.py` | M |
| `file_00000000a72c71fbbb92715224685716` | 77 | 1 | `0e2ce21b-a01f-4eb6-96b2-4b3200b04de1.png` | K |
| `file_00000000fa3471f587cd1f98af82e939` | 76 | 1 | `061de28b-93af-4a2c-a854-fbfc35b8ff9c.png` | K |
| `file_000000007bb07208838bb32cca9228aa` | 76 | 1 | `api.py` | M |
| `file_00000000cb70720aaf940a3b6891c600` | 76 | 1 | `ui.py` | M |
| `file_0000000022b87246bc6ea889376f252e` | 75 | 1 | `api.py` | T |
| `file_00000000f10871f4a1ff166d3a6c3f96` | 75 | 1 | `3907e1a8-985a-4b1a-b69a-a7ee5b964c34.png` | K |
| `file_00000000a4e071f493d3fb05019b941c` | 75 | 1 | `b1ce7d3c-c804-435c-a72a-73abca8d87cd.png` | K |
| `file_00000000108872438f9c7afa22c0cafd` | 75 | 1 | `859797e8-402e-4a4e-b62a-20f92b269cb0.png` | K |
| `file_000000004d9471f4bb079c67c25189a9` | 75 | 1 | `api.py` | T |
| `file_0000000019e071f485a17f98720850d7` | 75 | 1 | `6d028021-0554-4d2c-89b8-71935276113d.png` | K |
| `file_00000000325c7246af01f7000e8febd3` | 75 | 1 | `api.py` | T |
| `file_000000003f00724390ed4b74f8c8603f` | 75 | 1 | `d330d0ea-0b33-4954-9e45-1965aa949eb5.png` | K |
| `file_0000000073607243a3942398e6afa6b9` | 75 | 1 | `api.py` | T |
| `file_00000000b9307246a5acc4751194c307` | 75 | 1 | `api.py` | M |
| `file_00000000db6071f48329c2be998e75c8` | 75 | 1 | `b1befb2d-131f-41bb-98b3-9ecaa67d9158.png` | K |
| `file_00000000942871f4b144ba88d1a76d6c` | 75 | 1 | `4f6cec9f-de2c-48f3-8851-318a67428cc7.png` | K |
| `file_0000000005a471f4b65b1bc1dc6b9767` | 74 | 1 | `b888deae-9d2a-424b-806d-97befde63db8.png` | K |
| `file_00000000c0207243b5c185d2280b5bfe` | 74 | 1 | `README.md` | M |
| `file_00000000264872439f6d873443d860c2` | 74 | 1 | `sequence_system.md` | M |
| `file_0000000077c871f4aea659c54a40d435` | 74 | 1 | `sequence_weather.md` | M |
| `file_00000000b31c7243ad66f2e50ccaca0d` | 74 | 1 | `state_cache.md` | M |
| `file_000000003d1c72439ad116a3b6eb1c81` | 74 | 1 | `architecture.md` | M |
| `file_0000000001c471f49a0a998456fc0040` | 74 | 1 | `deployment.md` | M |
| `file_0000000008547243aa6d18a5effd465b` | 74 | 1 | `sequence_bitcoin.md` | M |
| `file_000000006a5471f4a70c473b15986f1c` | 74 | 1 | `sequence_electricity.md` | M |
| `file_00000000285c7243beebacbbab9ec958` | 74 | 1 | `ac01a690-6401-449b-acd2-9bb4cd2118bb.png` | K |
| `file_000000004df071f4b0a062d42ee8ca89` | 74 | 1 | `ca471143-6fe3-4670-a530-1e36cefe8c2a.png` | K |
| `file_00000000c1bc71f4a731fc4c1ec307c3` | 73 | 1 | `aab1d3d1-b4be-4dda-8265-33d1becf0640.png` | K |
| `file_00000000c2c4720a8dae7c61a4e7513d` | 73 | 1 | `51623b29-917e-4302-8698-181dabb0ad73.png` | K |
| `file_0000000084e07243a6fd9c2d64192162` | 73 | 1 | `8abc25ab-dc11-442e-94a9-15bac00f47d5.png` | K |
| `file_00000000bc8472468227a26d05977269` | 73 | 1 | `83296ce5-86f8-405a-abd9-c65b3888d718.png` | K |
| `file_00000000060872439a5e882e84de48eb` | 73 | 1 | `api.py` | M |
| `file_00000000a298720ab2ef8ffe8345b19d` | 73 | 1 | `b065e1f3-6662-456d-b788-3ed693f57da3.png` | K |
| `file_000000008d087243880d0bc9f6094e1f` | 73 | 1 | `8a2fe89c-423c-4157-b10e-33dfa8715d19.png` | K |
| `file_00000000cabc71f4a75629e22f8d386e` | 73 | 1 | `0f96102c-28a4-4a3e-aa86-01484731087a.png` | K |
| `file_00000000d80c7246b5f1af69c7f6f435` | 73 | 1 | `ui.py` | M |
| `file_00000000477c7246a19dba1d6f56f47b` | 73 | 1 | `b9c29d7a-b80b-41a5-8050-36b5463b1788.png` | K |
| `file_00000000971071f4bf4a71258cd8a9b6` | 73 | 1 | `a2686423-42c8-4d2e-b5d0-82dad5b212e8.png` | K |
| `file_00000000165871f4873fc97e32aa62dd` | 73 | 1 | `ui.py` | T |
| `file_00000000c89c71f4bbfedeb87f5b9c74` | 73 | 1 | `api.py` | T |
| `file_000000005b1471f484b799cb73220b4e` | 73 | 1 | `2e7ec3d0-1345-4131-bf1f-bbb358d5d4dc.png` | K |
| `file_000000000f2072438e1d585127d23d8c` | 73 | 1 | `7bf5aff9-ab03-4e0a-945c-67cc37ff53d6.png` | K |
| `file_00000000a47871f49b3890ca5d9398b3` | 73 | 1 | `b08bb6ad-6a7f-42a7-92b5-405729d71b72.png` | K |
| `file_00000000c83c71f4ae8a0ceec0e219dd` | 68 | 1 | `api.py` | M |
| `file_0000000074007243b82ef6ede71c018b` | 68 | 1 | `config.py` | M |
| `file_00000000becc7243a015399b1511b990` | 68 | 1 | `logger_config.py` | M |
| `file_00000000e8a472438fd44f0f7e7718d4` | 68 | 1 | `ui.py` | M |
| `file_00000000073471f4aa36ec326906140b` | 68 | 1 | `utils.py` | M |
| `file_00000000efd471f4975e6fefabc6075f` | 68 | 1 | `weather_icons.py` | M |
| `file_000000003bb47243b441405c4a4c5b4f` | 68 | 1 | `paths.py` | M |
| `file_00000000f0d071f49a49ff1d2d466a57` | 68 | 1 | `main.py` | M |
| `file_00000000c8ac72439af5afa5b809603c` | 68 | 1 | `1794993f-3c98-4fbb-9633-816a76b22346.png` | K |
| `file_000000002eb471f4b7401ddcf3c38a2f` | 68 | 1 | `b76afd4d-f894-494f-a099-9469fa14ae6c.png` | K |
| `file_00000000de4c71f49e6227802711d782` | 68 | 1 | `59fe4d80-5d92-42a7-ac2f-d015668d8049.png` | K |
| `file_00000000954c72438cf601a495cc226e` | 68 | 1 | `main.py` | M |
| `file_0000000099107243a226e54e9b4b11ce` | 68 | 1 | `config.py` | M |
| `file_000000009b387243bb980e4b88ad1fea` | 68 | 1 | `ui.py` | M |
| `file_000000000f407243a247866e9bcaaa4e` | 68 | 1 | `README.md` | M |
| `file_00000000422871f498185787663b28b1` | 68 | 1 | `d730f36c-832f-4c69-8ba9-56aaccd5f7c8.png` | K |
| `file_0000000096207246b7a2239b6a152859` | 68 | 1 | `main.py` | T |
| `file_00000000da547246b565fb9d512e60a8` | 68 | 1 | `api.py` | M |
| `file_00000000437c7246bdafc2363348ad39` | 68 | 1 | `config.py` | T |
| `file_00000000348871f4af515ef86f138ab0` | 68 | 1 | `logger_config.py` | T |
| `file_00000000947071f4b65582602c4eb2c4` | 68 | 1 | `paths.py` | T |
| `file_000000001ea87246975f5bd4ae36c4aa` | 68 | 1 | `ui.py` | T |
| `file_000000001a1871f49bc14e051fcec8cb` | 68 | 1 | `utils.py` | M |
| `file_0000000018a47246a2761e5ed8887e6c` | 68 | 1 | `weather_icons.py` | M |
| `file_00000000b9dc724386826ebda61a1eae` | 68 | 1 | `main.py` | M |
| `file_00000000fc14724385abeb989cdf6fc5` | 68 | 1 | `logger_config.py` | M |
| `file_0000000009207243a68a6e083a4d8f66` | 68 | 1 | `config.py` | M |
| `file_00000000e16c7243947af9a1eaaa9b7e` | 68 | 1 | `ui.py` | M |
| `file_0000000057687243846cd4b578820979` | 68 | 1 | `main.py` | M |
| `file_000000000ba87243aca576688db75b59` | 68 | 1 | `2feafe05-4622-4abf-9935-483ae6a8713b.png` | K |
| `file_0000000088487243bd0a89f8f67093a7` | 68 | 1 | `5d5bdc2c-88c3-4f4f-9618-cc465728e044.png` | K |
| `file_0000000097b0720ab84e082fe1971b12` | 72 | 1 | `aaf5f6be-00b7-42cd-aae6-2678d79f9555.png` | K |
| `file_000000008888720a97bad03710856792` | 72 | 1 | `3de4ee25-7332-40dd-860f-7bd6e61133f3.png` | K |
| `file_0000000084ac720a8713403674173e14` | 72 | 1 | `0635062d-cdba-4c57-936b-397a612c6748.png` | K |
| `file_000000004340720aa798ce43f2d1c2fe` | 70 | 1 | `ui.py` | M |
| `file_000000005314720a845f61e0303474e7` | 70 | 1 | `style.css` | M |
| `file_0000000084d87246b5d08adfaf4411cc` | 69 | 1 | `339fee66-91c0-4ae0-83e1-ea63b76b101c.png` | K |
| `file_000000009b747246aa6df72901d909fd` | 69 | 1 | `3f79ce0d-eb71-4b97-8339-d9085266b762.png` | K |
| `file_000000007fac71f4bb3e4f4309d0cc2c` | 69 | 1 | `f9f93e55-61d4-44f2-9fc3-86bf09efc2d1.png` | K |
| `file_00000000280c7246a160c961e0554520` | 69 | 1 | `10a51311-72d9-4f25-bc14-c703d11a19ba.png` | K |
| `file_0000000049d07246acbcb2c0ebd7aa6b` | 69 | 1 | `api.py` | M |
| `file_00000000652471f49a01ce18a69aa7ee` | 69 | 1 | `bff40a16-127e-4fd1-8381-caecb9522f5d.png` | K |
| `file_0000000045d87246891614564607edb6` | 69 | 1 | `api.py` | M |
| `file_00000000d8f071f4b6d36dbb0e1ea70d` | 69 | 1 | `315b6c5c-732a-4f93-81a3-84a91bfefc99.png` | K |
| `file_000000009a6c7246a4536bba3bac2839` | 69 | 1 | `84bbdc14-7318-4fd8-bcf4-1344fd4a9ebd.png` | K |
| `file_00000000f6d071f4ab5624f9d89352cf` | 69 | 1 | `5da0e3a2-0b4b-4f09-889c-88cedbc62cca.png` | K |
| `file_0000000099d87246b873360feaf788ca` | 69 | 1 | `eea63360-c27a-4a9f-9181-6e1c5ab0ffc7.png` | K |
| `file_0000000094b07246bc9fc332023ba3c7` | 69 | 1 | `1fe4273b-b675-4e36-a393-1c0943c98bae.png` | K |
| `file_0000000006747246ab1d08df3abefefd` | 69 | 1 | `api.py` | M |
| `file_0000000069807246a86737ae029dea82` | 69 | 1 | `4ec4b97b-37e8-4764-96f4-d16907be1506.png` | K |
| `file_00000000f23c7243ae96371c60d2dba2` | 67 | 1 | `card_heos.py` | T |
| `file_000000004d10720aabcb807f1d7c0dab` | 67 | 1 | `main.py` | M |
| `file_00000000e4fc724392e69e03f74d8320` | 67 | 1 | `ui.py` | M |
| `file_00000000f25c720a87c86f0060cd3455` | 67 | 1 | `146b7e9f-b5a4-43ff-acfd-388416280cf2.png` | K |
| `file_000000001c6c720a82786d6dfd0edd40` | 67 | 1 | `ui.py` | T |
| `file_000000008f04720a866f12055ae7edc5` | 67 | 1 | `ui.py` | T |
| `file_0000000027647246b681703fa2f9c8d7` | 66 | 1 | `update.sh` | M |
| `file-Pdsnahv3eh4SRLxeZVXifj` | 66 | 1 | `DeployToPi.ps1` | M |
| `file-KcFB5myU9PCv8J7zQVJ4Cy` | 66 | 1 | `DeployToPi.ps1` | M |
| `file_000000000ae071f4bb4aa9f6033c7eeb` | 66 | 1 | `.env` | T |
| `file_0000000045cc7246adf9ce006160aa88` | 66 | 1 | `config.py` | T |
| `file_00000000fbac7246ae7b351b46fbdcc7` | 65 | 1 | `cf5d1a29-0880-4e3e-8b80-8a251cb946d9.png` | K |
| `file_000000009148724691772a65d8c01f27` | 65 | 1 | `3ed09b5b-6352-4624-9d25-4e0c5c93a316.png` | K |
| `file_00000000c0e47246a86f8f2f7bfae513` | 65 | 1 | `e6404728-7030-4b73-ab54-09cd3064058b.png` | K |
| `file_00000000cad4720a8645ff7abe172085` | 65 | 1 | `66abba8f-5351-464f-a8a5-34e297bb7462.png` | K |
| `file_00000000e98c71f49141dd57ce4b2196` | 65 | 1 | `80cd2c82-b47e-42a1-b778-dd80beb88cc3.png` | K |
| `file_0000000027a872469aa61912157da6e9` | 65 | 1 | `e3f4c818-d52c-454d-aa58-c88b55d38be6.png` | K |
| `file_00000000019c71f4a6bbf887940fe868` | 65 | 1 | `bf19fd13-529f-4204-abc9-168a29623b63.png` | K |
| `file_000000007d6471f4853d5549700108ba` | 65 | 1 | `4f8fa1a4-aa54-4b9a-b5f9-0d2c9d28f15d.png` | K |
| `file_00000000c41c72469cf11c3d4053709c` | 65 | 1 | `main.py` | M |
| `file_000000008cd87246953ad8c66944a8b5` | 65 | 1 | `ui.py` | M |
| `file_0000000094f071f4843c060f0f8dfba2` | 65 | 1 | `card_heos.py` | M |
| `file_0000000094807246b31dfe50d5c9571b` | 65 | 1 | `4bdea118-7bb8-48a2-9cfa-3661f53601a7.png` | K |
| `file_000000007d7871f48df3e3c6767ead9c` | 64 | 1 | `3942c05e-b5b4-4a0e-af92-2bfeb0168293.png` | K |
| `file_0000000019a87243b3b078c13108afb8` | 64 | 1 | `electricity.py` | T |
| `file_000000006ec87243ac7bbe7e332edba3` | 64 | 1 | `card_prices.py` | T |
| `file_0000000071dc7243bf3f0a2c207bbe14` | 64 | 1 | `electricity.py` | M |
| `file_0000000026647243a05045d9d9782bea` | 64 | 1 | `api.py` | M |
| `file_00000000a3487243a5ba67c405d8db17` | 58 | 1 | `main.py` | M |
| `file_0000000087fc71f48ff605f277dd397c` | 58 | 1 | `utils_sun.py` | M |
| `file_00000000b92c7243a3e291902dd9efcb` | 58 | 1 | `config.py` | M |
| `file_00000000f34871f49a29c708c25a0566` | 58 | 1 | `calendar_data.py` | M |
| `file_0000000058a471f4818f8f6ed53d4e3a` | 58 | 1 | `calendar_holiday.py` | M |
| `file_0000000072c47243a417bdb7df607bf0` | 58 | 1 | `calendar_nameday.py` | M |
| `file_00000000cfb471f4b83ebf835f3906c7` | 58 | 1 | `calendar.py` | M |
| `file_00000000972871f49c9f04f545fe2400` | 58 | 1 | `card_nameday.py` | M |
| `file_00000000550071f4b792a73ef4a8b754` | 58 | 1 | `calendar_old_working.py` | M |
| `file_000000006dc871f48218abaceddb33bb` | 58 | 1 | `card_nameday_old_working.py` | M |
| `file_000000009d2c7246bb5e4143995f66fd` | 58 | 1 | `electricity.py` | M |
| `file_000000005e18720aa508718044dd6864` | 58 | 1 | `utils.py` | M |
| `file_000000007950720abc363248ff40223e` | 58 | 1 | `utils_sun.py` | M |
| `file_000000004068720aae9b898e2284f4f1` | 58 | 1 | `card_nameday.py` | M |
| `file_0000000041d072469498a291959aefb2` | 58 | 1 | `card_bitcoin.py` | M |
| `file_00000000e61071f4b74efd4888f0cb6b` | 58 | 1 | `weather.py` | M |
| `file_00000000ff287243af8dd870840a7bd2` | 58 | 1 | `__init__.py` | T |
| `file_00000000f92872439a6f191a9fef9897` | 58 | 1 | `calendar.py` | T |
| `file_000000005b9072438faae905d3f670ac` | 58 | 1 | `09264293-61ca-46aa-9570-4077646adbb9.png` | K |
| `file_00000000f7e871f484225e54fe329977` | 58 | 1 | `card_nameday.py` | M |
| `file_00000000aaa8724394a38873f5c8a79b` | 58 | 1 | `utils_sun.py` | M |
| `file_00000000f53072438a4bd0346036f1fb` | 58 | 1 | `card_nameday_old_working.py` | M |
| `file_00000000d2ac7243808febda967284ff` | 58 | 1 | `calendar.py` | T |
| `file_000000006ac471f49d5a541b4cc464cc` | 58 | 1 | `card_nameday.py` | M |
| `file_0000000025e0720a820f9f5c263c1a48` | 58 | 1 | `725c9f04-df90-42c0-b64e-83d000f50ef0.png` | K |
| `file_00000000f440724692f6f4f9508f5256` | 58 | 1 | `card_nameday.py` | M |
| `file_000000003d2472469f97f4acf1d7ec0b` | 58 | 1 | `04d9e98f-c93f-4e85-9ae7-9fde7ec27953.png` | K |
| `file_000000007e6c71f49ba72db72038dc15` | 58 | 1 | `calendar.py` | M |
| `file_00000000302071f493ac33f9a4849650` | 58 | 1 | `calendar_data.py` | M |
| `file_00000000281871f4a1b4e5f212347070` | 58 | 1 | `calendar_holiday.py` | M |
| `file_00000000a7707243848471b478c143b2` | 58 | 1 | `calendar_nameday.py` | M |
| `file_0000000070e871f482ee74c472c7e624` | 58 | 1 | `card_nameday.py` | M |
| `file_000000003700720aaafe5050ca4a0de3` | 58 | 1 | `4a1178e4-8e1e-40db-b60e-f210ee8e9336.png` | K |
| `file_00000000cd24720a857635a0f215dd24` | 58 | 1 | `e939abb2-f28e-4a70-91ce-054fc0945f14.png` | K |
| `file_00000000ab0872469c697bf61d5ff87d` | 58 | 1 | `card_nameday.py` | M |
| `file_00000000737471f48f566793e670512d` | 58 | 1 | `calendar.py` | M |
| `file_00000000d74c7246bb8226eccea2b53f` | 58 | 1 | `calendar_data.py` | M |
| `file_00000000aa1872468ec13d7ca9e89254` | 58 | 1 | `calendar_holiday.py` | M |
| `file_000000006e0071f4b797398ab80b92fc` | 58 | 1 | `calendar_nameday.py` | M |
| `file_000000008c6c7243807b55cd042cb2a1` | 58 | 1 | `card_nameday.py` | M |
| `file_00000000520872439f0601c565ddd46f` | 58 | 1 | `calendar.py` | T |
| `file_000000007de871f4902c336991ca88d2` | 58 | 1 | `calendar_data.py` | M |
| `file_00000000dc8871f49fe1d81e91d05a55` | 58 | 1 | `calendar_holiday.py` | M |
| `file_00000000325471f4b0a0cb0eda637731` | 58 | 1 | `calendar_nameday.py` | M |
| `file_0000000032ac71f49502056153930acb` | 58 | 1 | `calendar_old_working.py` | M |
| `file_00000000d08471f4918b30c1eee8e21e` | 58 | 1 | `card_nameday_old_working.py` | M |
| `file_00000000d6ec720a815c76cc5f5b3d73` | 58 | 1 | `card_nameday_old_working.py` | M |
| `file_000000009c14720abfe79ad59fc1e507` | 58 | 1 | `card_nameday.py` | M |
| `file_000000004dec7243a7a2ac423cf14f92` | 63 | 1 | `card_prices.py` | M |
| `file_000000006a5871f4864e23814009e60d` | 62 | 1 | `utils.py` | M |
| `file_000000007da872439d3351f94aa4d875` | 61 | 1 | `bitcoin.py` | M |
| `file_0000000040a872438c0901bd752217ea` | 61 | 1 | `2aa09e62-40f3-49e4-8f14-597e0af651ee.png` | K |
| `file_000000004cec71f4bb59cc467115fd44` | 60 | 1 | `REFACTORING.md` | T |
| `file-XhPo6FUhRG8ZnNWGZKDu7o` | 59 | 1 | `Generate-UML.ps1` | M |
| `file_00000000759471f49af13df0ea7b2e60` | 59 | 1 | `f3663a31-f160-4c2a-9c47-5fbe5e4d773e.png` | K |
| `file_00000000903071f4ac6d488217f2de47` | 59 | 1 | `classes_HomeDashboard.png` | K |
| `file_0000000043d071f48a1e21b7017f3853` | 59 | 1 | `packages_HomeDashboard.png` | K |
| `file_00000000e03871f48fbcdc47290edd6a` | 59 | 1 | `packages_HomeDashboard.png` | K |
| `file_000000002a2c71f48ee4fbef9de0d242` | 57 | 1 | `9c85e542-f796-4439-a0f2-3b98dce2d679.png` | K |
| `file_00000000c70471f4bd196416ced67c28` | 57 | 1 | `b9e61eff-4cdc-45af-8f54-75f957e41022.png` | K |
| `file_0000000086e471f48e015d0fd18e6587` | 57 | 1 | `b9abb43f-3b44-4b55-b3d0-47b24d67bb89.png` | K |
| `file_000000008ad871f4823df01843de8d8c` | 57 | 1 | `bba81a10-1162-4157-8939-9e019d213335.png` | K |
| `file_000000008054720a8a7f8785c06d4054` | 56 | 1 | `b1fcd418-f0b7-47aa-ba1f-8eee0a7aef25.png` | K |
| `file_000000004c5871f4930ea4dae4f9b973` | 56 | 1 | `401ace54-ce02-4197-9876-48f6d77cbbbe.png` | K |
| `file_00000000e6187246a5fd2f6d24f851f5` | 56 | 1 | `0d0b5f0a-081b-45e1-bab6-5ff385bfbbc6.png` | K |
| `file_000000000ff472439c237b5e09623802` | 56 | 1 | `pyhat_fi.json` | M |
| `file_00000000d278724391ed8707d6b3561f` | 56 | 1 | `card_nameday.py` | M |
| `file_00000000d66c72438979d315861485fc` | 56 | 1 | `pyhat_fi.json` | M |
| `file_000000004d0471f4ba1d2d3444dcbace` | 56 | 1 | `00a5b879-2534-4ef6-89ee-0c1f1bc0f7d2.png` | K |
| `file_000000001be8720a83793dfaaa4bc769` | 56 | 1 | `5e4bc48b-f912-4518-81a2-e40dd9c7308f.png` | K |
| `file_000000009bd0724696f02a7ec6e85738` | 56 | 1 | `fd314749-072f-46a6-ad7b-5605a487aecd.png` | K |
| `file_0000000007d871f48454ce2126d7e66c` | 56 | 1 | `card_nameday.py` | M |
| `file_00000000145871f4b6a20d9f66257e4a` | 56 | 1 | `68b6afb0-9ca6-431f-929f-1c1abea203e6.png` | K |
| `file_00000000d418720a9ff74847f11fb019` | 56 | 1 | `main.py` | M |
| `file_0000000013ec720ab93deed032e7aad7` | 56 | 1 | `4c674371-61fd-454f-a66d-00298f38b49a.png` | K |
| `file_0000000065f071f4babeec40f1f59b96` | 56 | 1 | `card_nameday_old_working.py` | M |
| `file_000000004f0871f4bdeae8b656b7319d` | 56 | 1 | `dd626fbd-aae3-4000-9e6e-a77b2753b5f0.png` | K |
| `file_00000000503c720a81841769352fd18c` | 56 | 1 | `calendar_nameday.py` | M |
| `file_00000000b87471f49e8e31df60f6a485` | 56 | 1 | `c216645a-f8f1-4035-882d-0e15acf55fbc.png` | K |
| `file_0000000066147243b583f2ec5dc01d00` | 56 | 1 | `card_nameday.py` | M |
| `file_0000000058d872438bf73cfe3f000770` | 56 | 1 | `card_zen.py` | T |
| `file_00000000f6a871f4ac2784c04e49bb3f` | 56 | 1 | `28a48986-216e-47f0-af12-64f4b524b0e6.png` | K |
| `file_00000000bfb87243b93709015b0ed4e0` | 56 | 1 | `b10d12a0-43fc-44cd-bc9a-8c4d9228f3e2.png` | K |
| `file_0000000033647246a80b5c8640d8d8a7` | 56 | 1 | `014a6b75-de27-4892-a2ae-db0a084edc10.png` | K |
| `file_0000000099287246a5e4ed1eaf2f8e74` | 56 | 1 | `d5586690-0791-4eb3-b6be-907bc8940767.png` | K |
| `file_00000000eefc71f49c28665ad153fe87` | 56 | 1 | `48411e6f-088f-4234-931c-e4a6ab69fb8d.png` | K |
| `file_00000000e4e87246b4ae73d0fadd297b` | 56 | 1 | `card_nameday.py` | M |
| `file_00000000f4b871f4839e0d888b2d9312` | 55 | 1 | `CHANGELOG_EN.md` | M |
| `file_000000000d5071f4a6c9279cefa1a0a3` | 55 | 1 | `QUALITY.md` | T |
| `file_000000008e6871f4b5dd40feb5739dd0` | 55 | 1 | `README.md` | M |
| `file_00000000ee2871f4b0176798e03f8200` | 55 | 1 | `README_en.md` | M |
| `file_00000000f94071f4a1cc8ff92fd8b594` | 55 | 1 | `REFACTORING.md` | T |
| `file_00000000480c71f4aec08ac7b6cbb859` | 55 | 1 | `CHANGELOG.md` | M |
| `file_00000000583471f4be2fed2aab1240d1` | 55 | 1 | `9836fafa-7972-4942-837e-a7055efca488.png` | K |
| `file_00000000cda471f48ae84129bf0f3032` | 55 | 1 | `electricity_log.py` | M |
| `file_000000006f3471f4b8e3fe19207002b2` | 55 | 1 | `electricity_normalize.py` | M |
| `file_00000000d23471f4a1a65ea1619943c0` | 55 | 1 | `electricity_service.py` | M |
| `file_00000000507071f488030c449f2e33ca` | 55 | 1 | `electricity_sources.py` | M |
| `file_00000000501871f4a30e45381f02082c` | 55 | 1 | `electricity.py` | T |
| `file_000000000e0472469140b0425eeb2238` | 55 | 1 | `9d5c0fc2-072a-4104-a094-c15fd7adaed4.png` | K |
| `file_00000000b35871f48d4a13b2c077dd4e` | 55 | 1 | `344c0e7c-477d-497b-9f64-a2b992c57560.png` | K |
| `file_00000000276c71f4af5fd9fc6ef38bd5` | 55 | 1 | `9441aaff-52ef-4d48-953d-b5ab6c1c4c73.png` | K |
| `file_00000000bf2c72469bccd246a6f8f7c6` | 55 | 1 | `126bc909-7ae2-4d61-b06a-194a9464d9be.png` | K |
| `file_0000000078d471f4b8855308d107ad74` | 55 | 1 | `__init__.py` | M |
| `file_00000000cfd4720ab4dc8de4e20235f8` | 55 | 1 | `card_nameday.py` | M |
| `file_000000006cf871f48ef8e7b80e0190c8` | 55 | 1 | `__init__.py` | M |
| `file_00000000dad4724682e2712637697f32` | 55 | 1 | `main.py` | M |
| `file_000000006e4071f4a1c2a4410e60e135` | 55 | 1 | `5d823c34-4563-409e-a5ec-8ba423c30859.png` | K |
| `file_000000001abc72468c915ab297480737` | 55 | 1 | `main.py` | M |
| `file_0000000099dc7246b9107e9f4671f530` | 55 | 1 | `__init__.py` | M |
| `file_00000000246471f4a1620b694a85df94` | 55 | 1 | `card_nameday.py` | M |
| `file_000000004f10720aab7cfbffc72047fc` | 55 | 1 | `main.py` | M |
| `file_0000000079ac71f48861df503e27d69c` | 55 | 1 | `calendar_nameday.py` | M |
| `file_00000000f09471f4a428c37b7d181d8a` | 55 | 1 | `__init__.py` | M |
| `file_0000000074b071f49baa38760a1086b9` | 55 | 1 | `card_nameday.py` | M |
| `file_00000000d49071f4b9993db5ece0768b` | 55 | 1 | `29f9e6ef-57f1-446a-a49e-3a68cdae78e8.png` | K |
| `file_00000000273871f493181d2780bef489` | 55 | 1 | `card_nameday.py` | M |
| `file_00000000ef1871f4b2880120db49139f` | 55 | 1 | `856d4ed7-18cb-4849-bfa8-1c116ed3423c.png` | K |
| `file_00000000132471f48102ac870b8c098d` | 55 | 1 | `nimipaivat_fi.json` | M |
| `file_000000007dd071f49fd4b49f34c2efe1` | 55 | 1 | `pyhat_fi.json` | M |
| `file_000000006a4c71f4886c1b8951007287` | 54 | 1 | `REFACTORING.md` | T |
| `file_00000000b1d071f49979bb7dcab21447` | 53 | 1 | `electricity_normalize.py` | M |
| `file_00000000af98720aa8ed44239d2c9deb` | 53 | 1 | `aed5590f-166b-4bc4-8aa7-d2e43641600a.png` | K |
| `file_000000002088720ab43fe626e6d50d79` | 52 | 1 | `electricity_service.py` | M |
| `file_000000000b7471f4a509cf31958ad4ba` | 52 | 1 | `abf6c70a-ca80-4e31-a763-b61c0865cf35.png` | K |
| `file_00000000f55071f485190f532d8e3c96` | 51 | 1 | `test_electricity_normalize.py` | M |
| `file_00000000a774720ab956db8a38ec5284` | 51 | 1 | `199a6b6d-a5ae-4345-ad74-18b7bff45128.png` | K |
| `file_00000000a83c720ab0a92f7b7f64a1df` | 51 | 1 | `818b8727-a455-4d19-8e17-35ca50eec6e0.png` | K |
| `file_00000000c81471f4a42b9142bb92d258` | 51 | 1 | `abd26f4d-6537-44e1-a036-30e9135ccc2e.png` | K |
| `file_00000000102471f494e10c129ab82216` | 51 | 1 | `test_electricity_servie.py` | M |
| `file_00000000f2f4720abbd84d7a50fe1d5a` | 51 | 1 | `test_electricity_sources.py` | M |
| `file_00000000762c720aac8f2589c021fe81` | 51 | 1 | `electricity.py` | M |
| `file_0000000085b471f4b1b52a0fa5175c8f` | 51 | 1 | `electricity_adapters.py` | M |
| `file_00000000ac5c71f4923bd809776385d8` | 51 | 1 | `electricity_log.py` | M |
| `file_0000000057bc71f4aec0ed6d431184a3` | 51 | 1 | `electricity_normalize.py` | M |
| `file_000000004324720a99c7486b753cdde5` | 51 | 1 | `electricity_service.py` | M |
| `file_000000001aec71f4a95294c323c9ae86` | 51 | 1 | `electricity_sources.py` | M |
| `file_000000000298720abd92604987a7badf` | 51 | 1 | `card_prices.py` | M |
| `file_000000004a1871f483cc4eba86525dfe` | 50 | 1 | `weather.py` | M |
| `file_00000000c300720ab63a390174c0c346` | 50 | 1 | `weather_debug.py` | M |
| `file_000000004c6471f48a9e655643f8de5a` | 50 | 1 | `weather_fetch.py` | M |
| `file_00000000c0b4720a80a0b3dd8e2ac454` | 50 | 1 | `weather_mapping.py` | M |
| `file_0000000099ec71f48a5fddd7e986d66d` | 50 | 1 | `weather_utils.py` | M |
| `file_0000000093e4720aba7230caaf0ca478` | 50 | 1 | `card_weather.py` | M |
| `file-MguYK5YXFGLZ4vFTLvbAH2` | 50 | 1 | `WMO_weather_terms_fi.xlsx` | M |
| `file_000000006b4c720ab7dcd5c6b8143832` | 50 | 1 | `weather_icons.py` | M |
| `file_0000000073d8720ab2859e317d7408e7` | 49 | 1 | `card_bitcoin.py` | M |
| `file_000000002288720a923e7f22b964ed4a` | 49 | 1 | `card_bitcoin_parts.py` | M |
| `file_00000000b4b0720aa08c3c4277ca9584` | 49 | 1 | `bitcoin.py` | M |
| `file_00000000792871f483f4533a1238f248` | 49 | 1 | `test_bitcoin.py` | M |
| `file_0000000023a871f49e03812b3331d184` | 49 | 1 | `d42e2d66-bb36-4823-87e8-fe46c975ba09.png` | K |
| `file_00000000b43c720a9e481184429954c1` | 48 | 1 | `http.py` | M |
| `file_00000000173871f4b4b28b769f865614` | 47 | 1 | `calendar.py` | M |
| `file_00000000364c71f4b9b357422b66b548` | 47 | 1 | `calendar_nameday.py` | M |
| `file_000000001d1c71f48b795833b8d8f744` | 47 | 1 | `nameday.py` | M |
| `file_000000005b3471f486461c09641f11bc` | 47 | 1 | `card_nameday.py` | M |
| `file_0000000024c871f48805e610fa0a6092` | 47 | 1 | `nimipaivat_fi.json` | M |
| `file_00000000499871f4a9051ecd46f577cb` | 47 | 1 | `pyhat_fi.json` | M |
| `file_00000000e7b471f488164f7683632525` | 46 | 1 | `quotes.py` | M |
| `file_00000000e684720a8576dd8c974170c7` | 46 | 1 | `card_zen.py` | M |
| `file_00000000251871f4ac9426ee480583c5` | 46 | 1 | `99d19b7d-d5f9-4097-b31e-b925805368dd.png` | K |
| `file_00000000db24720aa1f21cad828cc262` | 46 | 1 | `test_card_zen.py` | M |
| `file_00000000a5dc71f4834e796bd1200840` | 45 | 1 | `card_system.py` | M |
| `file_000000005f1871f48167ff3677330a43` | 44 | 1 | `d476d6da-af4d-4b0f-b247-7724de629cdd.png` | K |
| `file_00000000ba1071f4994adba3311370cc` | 44 | 1 | `heos_client.py` | M |
| `file_00000000da5471f4bf6c3c0ba69080d4` | 44 | 1 | `card_heos.py` | M |
| `file_00000000b850720a8f5f085e67f83a16` | 43 | 1 | `paths.py` | M |
| `file_000000007854720a9437ea2668430bbf` | 43 | 1 | `utils.py` | M |
| `file_00000000e37471f4895f9ad309400f1c` | 43 | 1 | `common.py` | M |
| `file_0000000075d4720a822deeb0460ee9eb` | 42 | 1 | `electricity_adapters.py` | T |
| `file_00000000ae8471f4ad07dbe04a067731` | 42 | 1 | `17e4bc23-5dcf-467a-aae5-e20453e6c13f.png` | K |
| `file_00000000ccd0720aab8f6631a6445b6c` | 42 | 1 | `pyproject.toml` | M |
| `file_0000000038b87243b00e3896f486c12a` | 41 | 1 | `calendar.py` | M |
| `file_00000000c45871f4aaef12df5aad589c` | 41 | 1 | `nameday.py` | M |
| `file_0000000076787243bfe330a1fb436aa3` | 41 | 1 | `5455395c-7a06-4d3f-b10e-9e6f9e46e2a2.png` | K |
| `file_00000000b91071f4a75e569b1d889661` | 41 | 1 | `874a7569-ad1e-4b4f-a032-823db7353d4a.png` | K |
| `file_000000008af471f4a42594d23d23f3dc` | 41 | 1 | `test_calendar_nameday.py` | M |
| `file_0000000007e4724397918a2fa1dec204` | 40 | 1 | `8a01bf2a-a467-44f9-8490-eb5780afb560.png` | K |
| `file_00000000bb6471f4adf253c5e638859b` | 40 | 1 | `test_calendar_nameday.py` | T |
| `file_00000000611c7243ae49a6f560826758` | 40 | 1 | `card_nameday.py` | M |
| `file_000000009228724392ae1185a5a155bb` | 40 | 1 | `1579035d-2456-4433-af04-9f6fc69ed2a0.png` | K |
| `file_00000000e23071f493b5626d58bbeb09` | 39 | 1 | `test_weather_entrypoint.py` | M |
| `file_00000000c380724682bf5996ba95fdb5` | 39 | 1 | `test_weather_fetch.py` | M |
| `file_0000000082fc71f4aadf8830f457ebc5` | 39 | 1 | `test_weather_utils.py` | M |
| `file_00000000475471f4865e3b945a5bd0d9` | 39 | 1 | `test_weather_utils_mapping.py` | M |
| `file_00000000c1a471f494f1c16999c42293` | 39 | 1 | `f5c2ad79-eb7c-4d25-af5f-2be0f6d187ad.png` | K |
| `file_0000000053ec71f48c77506cd3ba6b1c` | 39 | 1 | `card_weather.py` | M |
| `file_00000000d09871f4855c43297d39dc8d` | 39 | 1 | `card_weather.py` | M |
| `file_00000000e1f4724380a0a4891b3ece2c` | 39 | 1 | `ba89344b-37b7-485a-9449-f508e6b24932.png` | K |
| `file_0000000027f871f4880425c87c28bc0e` | 38 | 1 | `weather_fetch.py` | M |
| `file_000000006ff871f492fc4c9317df6d6b` | 38 | 1 | `2159ba7a-5e61-406e-a20b-07c082fc0a54.png` | K |
| `file_0000000088bc71f4a20cf1ee95f66ffd` | 38 | 1 | `test_weather_fetch.py` | M |
| `file_00000000f25c724689bf68a1c8ba00aa` | 37 | 1 | `test_weather_entrypoint.py` | T |
| `file_0000000016787246b1ceb5dd3fb38793` | 37 | 1 | `test_weather_fetch.py` | T |
| `file_0000000037ec71f48dbc832982bdc27e` | 37 | 1 | `test_weather_utils.py` | T |
| `file_0000000073b471f4978f6c8cd4a3fd56` | 37 | 1 | `test_weather_utils_mapping.py` | T |
| `file_000000006d8c71f4ac737f3bc4886949` | 37 | 1 | `test_weather_viewmodel.py` | T |
| `file_0000000034a071f4abc6a750b6c4de76` | 37 | 1 | `test_wmo_foreca_code.py` | T |
| `file_00000000fbe471f49a0b864d6e27022a` | 37 | 1 | `weather_icons.py` | M |
| `file_000000004be07246aa666e781670a332` | 37 | 1 | `card_weather.py` | M |
| `file_00000000f8e872469865c3c706908dad` | 37 | 1 | `weather_mapping.py` | M |
| `file_000000000e6071f48bf8a271f7987a0a` | 37 | 1 | `test_weather_utils_mapping.py` | M |
| `file_00000000800c72469657b0a6ce1d6719` | 36 | 1 | `test_weather_utils.py` | M |
| `file_000000002ce871f4a302f928e986ddf0` | 36 | 1 | `weather_utils.py` | M |
| `file_00000000838471f4ba39fb6c0a023c81` | 35 | 1 | `REFACTORING.md` | M |
| `file_000000003e0c71f4a5bcec6ea9519183` | 34 | 1 | `card_nameday_helpers.py` | M |
| `file_00000000ad8871f490c575065717964d` | 34 | 1 | `card_nameday.py` | M |
| `file_000000008cac71f4ac57dc677bdaadac` | 34 | 1 | `calendar.py` | T |
| `file_000000005c4071f4a22d8551b5d41696` | 34 | 1 | `calendar_nameday.py` | M |
| `file_00000000155471f4b2073c348f074167` | 34 | 1 | `nameday.py` | T |
| `file_00000000c0a871f494d9ec1b11987f5d` | 34 | 1 | `b1c0cfc9-0e65-4e22-884c-c80eaeb880ce.png` | K |
| `file_000000005e6471f4aa8ec95de01a129c` | 34 | 1 | `calendar.py` | M |
| `file_000000002fa071f4af407e4bf42f6295` | 34 | 1 | `nameday.py` | M |
| `file_00000000082471f4a44ab4f2752c6b16` | 34 | 1 | `card_nameday.py` | M |
| `file_00000000995471f49fedb574c87eea25` | 34 | 1 | `test_calendar_nameday.py` | M |
| `file_00000000362471f49e68d281162089b7` | 34 | 1 | `test_card_nameday_helpers.py` | M |
| `file_0000000051e0724680da26192c90f853` | 33 | 1 | `eeb1c954-7f3b-4b05-89ac-5402f9bca410.png` | K |
| `file_00000000080472468253c99db784cf7b` | 33 | 1 | `4deacf00-0429-495d-853e-111c22e4b2f1.png` | K |
| `file_00000000a0147246b0a216818d8fc032` | 33 | 2 | `test_electricity_adapters.py` | M |
| `file_000000001e847246aa542f1d4875ad5c` | 33 | 2 | `test_electricity_normalize.py` | M |
| `file_00000000e7f87246aa65090b49505062` | 33 | 2 | `test_electricity_service.py` | M |
| `file_000000003b6071f48be3cdc42ebe6c8f` | 33 | 2 | `test_electricity_sources.py` | M |
| `file_00000000e4bc71f4976ad917ff863791` | 33 | 1 | `19635a3a-fa60-438f-add8-3522f222a906.png` | K |
| `file_0000000094e471f4967f734e1130e241` | 33 | 1 | `REFACTORING.md` | M |
| `file_000000008f1871f4a334e4c08b8d56b1` | 33 | 1 | `card_prices.py` | M |
| `file_00000000033871f4831009a625f3b70e` | 33 | 1 | `electricity.py` | M |
| `file_00000000b8607246b6f1c359b4ee5e6d` | 33 | 1 | `electricity_adapters.py` | M |
| `file_00000000060c72468c08f89b91f82c2c` | 33 | 1 | `electricity_normalize.py` | M |
| `file_00000000bd8871f49e3f31dc4345e62f` | 33 | 1 | `electricity_service.py` | M |
| `file_00000000731c7246b207107ced9c6a2e` | 33 | 1 | `electricity_sources.py` | M |
| `file_00000000227c71f49dd43e7f735f308f` | 33 | 1 | `electricity_viewmodel.py` | M |
| `file_0000000024dc71f4966dcd38382f3617` | 33 | 1 | `electricity_normalize.py` | M |
| `file_000000007f6471f4a041ae23839079d7` | 33 | 1 | `card_prices.py` | M |
| `file_00000000e6f471f4b6ba2bef13de68e8` | 33 | 1 | `electricity_service.py` | M |
| `file_000000005b1471f48245b47a32a50282` | 30 | 1 | `heos_client.py` | T |
| `file_000000003e4071f4a79720963546d7ef` | 29 | 1 | `weather_fetch.py` | M |
| `file_000000002e1871f4a3a8cf69e1ee5be7` | 28 | 1 | `card_prices.py` | M |
| `file_00000000a0c871f4acf23f628056d9d9` | 27 | 1 | `card_nameday.py` | M |
| `file_00000000569871f49cb0a4ba05558c11` | 27 | 1 | `calendar_nameday.py` | M |
| `file_000000005f8471f4b89cca93880bae88` | 27 | 1 | `calendar.py` | M |
| `file_00000000a37071f4a58f9c29c700f227` | 27 | 1 | `nameday.py` | M |
| `file_00000000373871f4b48ecadeeb292a34` | 27 | 1 | `test_calendar_nameday.py` | M |
| `file_000000002e0c71f48a5d59060e8e2f98` | 27 | 1 | `test_card_nameday_helpers.py` | M |
| `file_00000000ba4c71f4adebced43d62f1fe` | 26 | 1 | `REFACTORING.md` | M |
| `file_000000007bd871f48dde69207ec8d267` | 25 | 1 | `weather_fetch.py` | M |
| `file_00000000b408720a827b09cd6a344641` | 24 | 1 | `70129d68-c38e-4eef-bca3-7fddfe9485cf.png` | K |
| `file_000000009bc071f4804554476ceee6ab` | 24 | 1 | `card_bitcoin_parts.py` | M |
| `file_000000001be0720aa471feeb398da52e` | 24 | 1 | `card_prices.py` | M |
| `file_0000000012d871f48369450c814ad163` | 24 | 1 | `d23c7501-af8e-44ef-a43e-bab20bbe6a06.png` | K |
| `file_0000000041b871f4938b348700326d57` | 24 | 1 | `REFACTORING.md` | M |
| `file_00000000161071f49b8461790d3d7c31` | 23 | 1 | `weather_fetch.py` | M |
| `file_0000000081d872469feb40212e5310a6` | 20 | 1 | `weather_utils.py` | M |
| `file_00000000c9f471f4af38649ec12a3a2d` | 20 | 1 | `weather_utils.py` | M |
| `file_00000000639471f4afef8014c523578b` | 19 | 1 | `wmo_icon_map.py` | M |
| `file_00000000333c71f4b4ced46e4bab0ea0` | 19 | 1 | `wmo_map_loader.py` | M |
| `file_00000000065c7246828db4a397fa930c` | 22 | 1 | `calendar_nameday.py` | M |
| `file_0000000022f071f49daf7cf6f182d2b8` | 21 | 1 | `REFACTORING.md` | M |
| `file_000000007c507246b18a93ff805e0249` | 18 | 1 | `REFACTORING.md` | M |
| `file_00000000bd0471f4ae433b132a65faa9` | 16 | 1 | `afadfd1d-4a37-4d13-9bfb-17d655a65010.png` | K |
| `file_00000000bb3c7246a35395ba94a3bccd` | 16 | 1 | `heos_client.py` | M |
| `file_00000000a69072469c25091c7ca6924d` | 16 | 1 | `electricity_adapters.py` | M |
| `file_00000000f7f471f48c0ea6c4a09ca37b` | 16 | 1 | `electricity_log.py` | M |
| `file_0000000063407246aee37d9e8497db42` | 16 | 1 | `electricity_service.py` | M |
| `file_00000000a25071f48c22a52c30debc71` | 16 | 1 | `electricity_sources.py` | M |
| `file_00000000686472468e32b72c8a731d04` | 16 | 1 | `f8a455f9-cdcb-40f8-980b-cf5fec65a96b.png` | K |
| `file_00000000fbe8720ab0fc6f97a0b5700c` | 16 | 1 | `quotes.py` | M |
| `file_000000002770720aa3fe5c0921ac5113` | 16 | 1 | `test_wmo_foreca_code.py` | M |
| `file_000000001820720a83af87889185fa13` | 16 | 1 | `wmo_icon_map.py` | M |
| `file_00000000a280720a8306488740e1ad94` | 16 | 1 | `wmo_map_loader.py` | M |
| `file_000000006bd8720ab1b1f95e9f93dfc4` | 16 | 1 | `wmo_trace.py` | M |
| `file_000000009fd4720a8848350cdaa0efc6` | 16 | 1 | `weather_icons.py` | M |
| `file_000000006f387246b9a6312abcd6a321` | 16 | 1 | `card_nameday.py` | M |
| `file_00000000188071f488a9d668bd2c37d5` | 16 | 1 | `card_prices.py` | M |
| `file_000000009ec47246a1cb4c8bdc211626` | 16 | 1 | `card_weather.py` | M |
| `file_00000000458c724686c1e5941734f618` | 17 | 1 | `0140fad1-dc17-4e0a-95d8-eb5e0ea6e9f9.png` | K |
| `file_0000000088247246a00ea1fbdda07b58` | 17 | 1 | `test_bitcoin.py` | M |
| `file_000000001aa87246a7fbb7db9c774e9a` | 17 | 1 | `bitcoin.py` | M |
| `file_000000003adc7246acb4fb25f52961f2` | 17 | 1 | `card_bitcoin.py` | M |
| `file_00000000fa7c71f4a6b627090df70543` | 17 | 1 | `card_bitcoin_parts.py` | M |
| `file_00000000f510724683332acdb44dc176` | 15 | 1 | `1d8c0fe5-044e-43e0-90f3-115befd50673.png` | K |
| `file_0000000096307243a5d7ec7560aa2901` | 14 | 1 | `CHANGELOG.md` | M |
| `file_00000000414c71f49d37b94c7e783382` | 14 | 1 | `CHANGELOG_EN.md` | M |
| `file-CK4k7dvhcE8d6oo3q96dPk` | 13 | 1 | `DeployToPi.ps1` | M |
| `file-WZvbR7YF8tPRs9SqMmr8X7` | 13 | 1 | `GitSync.bat` | M |
| `file_000000009a8c7246b531e96f6dbec22a` | 13 | 1 | `update.sh` | M |
| `file_00000000b19871f4b1922be9acb8f4ef` | 13 | 1 | `style.css` | M |
| `file_00000000c71c7246b5a73784e84cc30b` | 13 | 1 | `main.py` | M |
| `file_00000000c498722f84c501816648343b` | 13 | 1 | `91a134b6-598d-4ad7-9afa-e01a55d3bdd7.png` | K |
| `file_00000000e9a8722f9abe43e48eecb4dc` | 13 | 1 | `main.py` | M |
| `file_000000005b1c72468649b818dc7d857c` | 13 | 1 | `card_heos.py` | M |
| `file_00000000dcac71f48e51fa40b3fc2341` | 13 | 1 | `card_hue_motion.py` | M |
| `file_0000000054ac71f4ba9ca987d44a48ea` | 13 | 1 | `card_system.py` | M |
| `file_00000000d71c722fbf52fc7f5bb59738` | 13 | 1 | `765031d5-a474-4766-ad12-f6de1ab7d9a5.jpeg` | K |
| `file_000000001db8722fae170b977275a554` | 13 | 1 | `main.py` | M |
| `file_00000000e94c722fa9dddf817cf8dbc8` | 13 | 1 | `__init__.py` | M |
| `file_00000000f84c722fbd974e43395deab0` | 13 | 1 | `card_hue_motion.py` | M |
| `file_00000000fe84722fb0f18b1c3280d74b` | 13 | 1 | `b3255734-4eae-4253-935e-04ad8443fc3d.png` | K |
| `file-Rcz3AeNxPUbN9UZ5piAEjs` | 13 | 1 | `ListHueObjects.ps1` | M |
| `file_00000000def871f493029d566ae53e90` | 13 | 1 | `607eec4a-ef1a-4c41-b7ba-dc28667717bb.png` | K |
| `file_00000000f02c722fbb3b51a0077a5350` | 12 | 1 | `test_card_heos.py` | M |
| `file_000000001234722f8160ec221fc5f56d` | 12 | 1 | `heos_client.py` | M |
| `file_0000000070e0722f9569804533414052` | 12 | 1 | `card_heos.py` | M |
| `file_00000000eff8720abf79b7f78c66125c` | 12 | 1 | `hue_contacts_v2.py` | M |
| `file_00000000f61871f4b5862a235b0a3e5b` | 12 | 1 | `card_hue_doors.py` | M |
| `file_00000000e32071f4956296184da14b5e` | 12 | 1 | `hue_contacts.py` | M |
| `file_000000000770722f8d650a20e842ae9e` | 12 | 1 | `test_card_nameday_ui.py` | M |
| `file_00000000ed98722f9863b50ce760c6f3` | 12 | 1 | `card_nameday.py` | M |
| `file_00000000048071f49aa03aab840811df` | 12 | 1 | `card_hue_motion.py` | M |
| `file_0000000009ac720a8b83c6d686d82944` | 12 | 1 | `hue_motion.py` | M |
| `file_00000000db14720a8ee2886559fc3025` | 12 | 1 | `calendar_nameday.py` | M |
| `file_000000007ee871f4b873d1f4deb6a424` | 12 | 1 | `calendar_nameday.py` | M |
| `file_0000000011e071f4a58dc2caddb2fb35` | 12 | 1 | `card_nameday.py` | M |
| `file_00000000147c71f48c684bd01aac92a6` | 12 | 1 | `card_nameday_helpers.py` | M |
| `file_000000003e2c722f84ab3b8698f60516` | 12 | 1 | `card_nameday_helpers.py` | M |
| `file_00000000dc9c71f4bd16c2b23c8e7a13` | 12 | 1 | `QUALITY.md` | M |
| `file_000000007148720a8681c787efcb23e9` | 12 | 1 | `README.md` | M |
| `file_00000000aff871f4ae0b76bedb2e09e8` | 12 | 1 | `README_en.md` | M |
| `file_000000000ab471f499ac74dbcadcdf17` | 12 | 1 | `REFACTORING.md` | M |
| `file_000000007b3071f4b2241a6ca4715434` | 12 | 1 | `CHANGELOG.md` | M |
| `file_0000000040e871f4b07e7482b516f073` | 12 | 1 | `CHANGELOG_EN.md` | M |
| `file_00000000fb48720abcc8819f333b8242` | 12 | 1 | `39d6e601-8cca-4b6e-9fe2-9812d5af99f7.png` | K |
| `file_000000004828720a92da24dd50ebf6e2` | 12 | 1 | `hue_motion.py` | M |
| `file_0000000072b8722fb248b67df3083aa9` | 11 | 1 | `REFACTORING.md` | M |
| `file_00000000cf10722fa1a01f6aa8d70072` | 11 | 1 | `README_en.md` | M |
| `file_000000005764722f8c4b4e436891cfd8` | 11 | 1 | `QUALITY.md` | M |
| `file_00000000b60c722f85ded9fd8c62af83` | 11 | 1 | `CHANGELOG_EN.md` | M |
| `file_000000006374722fb885acc9ee9211f8` | 11 | 1 | `README.md` | M |
| `file_000000008890722fa88455ba2a3185fd` | 11 | 1 | `CHANGELOG.md` | M |
| `file_000000002cb4722f868065feda1f3ab1` | 11 | 1 | `CHANGELOG.md` | M |
| `file_000000003470722f87f08722c3d7f9a3` | 11 | 1 | `README.md` | M |
| `file_000000009ee4722f875bcdda48b27375` | 11 | 1 | `QUALITY.md` | M |
| `file_00000000e2d4722f8ea7496381422625` | 11 | 1 | `CHANGELOG_EN.md` | M |
| `file_000000007ff8722fae6c0e779e9b4204` | 11 | 1 | `CHANGELOG.md` | M |
| `file_000000001828722fb9cbf9accef96892` | 11 | 1 | `REFACTORING.md` | M |
| `file_00000000f6e8722fab9f2a1a044394cb` | 11 | 1 | `README_en.md` | M |
| `file_00000000c31c72469b8b847b46bf24cc` | 10 | 1 | `f5bf046b-564c-4cbb-989d-b74deb900f04.png` | K |
| `file_00000000c82071f48683cc18db49357f` | 10 | 1 | `.env` | M |
| `file_000000001c88720abf398d06e63cb3e4` | 9 | 1 | `heos_client.py` | M |
| `file_00000000b7bc71f497141ee99a3bd129` | 9 | 1 | `card_heos.py` | M |
| `file_000000004cb4720a984fce271b24db32` | 9 | 1 | `card_heos.py` | M |
| `file_000000001ffc720a8d15e8c04d794d90` | 9 | 1 | `heos_client.py` | M |
| `file_000000004aa4720ab6cf1a15cf7e0f73` | 9 | 1 | `test_card_heos.py` | M |
| `file_00000000d350720ab8b57f2ff45b3c72` | 9 | 1 | `test_heos_client.py` | M |
| `file_0000000001c071f4a674115824bd14d7` | 9 | 1 | `heos_client.py` | M |
| `file_000000004bac71f4b4866548ec70d424` | 9 | 1 | `card_heos.py` | M |
| `file_00000000ccc071f48aee075447f20cf0` | 9 | 1 | `card_heos.py` | M |
| `file_000000002c0071f4bb19b52dff010f8b` | 9 | 1 | `heos_client.py` | M |
| `file_00000000a178720a93e5de031226ce99` | 8 | 1 | `heos_client.py` | M |
| `file_000000007a1071f4bd0cca1b8975a650` | 8 | 1 | `card_heos.py` | M |
| `file_00000000767471f4a77f7526b7abd772` | 8 | 1 | `test_card_heos.py` | M |
| `file_0000000055d071f484d4bf663850fffc` | 8 | 1 | `2b916a68-c9db-478d-8dbf-8f635e092ad5.png` | K |
| `file_000000005844720aa4b45fda20d49313` | 8 | 1 | `heos_client.py` | M |
| `file_0000000008f071f4a8d171e738f5da03` | 8 | 1 | `97c01031-3e67-4695-a1c6-d35d164f6f1f.png` | K |
| `file_00000000b06c720aac50fca5b41efb4e` | 8 | 1 | `1325f5b5-abd0-48b7-8b36-3da834beacf4.png` | K |
| `file_00000000839871f498675879aa299bb5` | 8 | 1 | `card_heos.py` | M |
| `file_0000000049207246b92f7ab2a9b63669` | 8 | 1 | `card_heos.py` | M |
| `file_00000000d64c71f48a96018e94cc0fa5` | 8 | 1 | `886cab02-c10e-44bc-8995-4730ecff192e.png` | K |
| `file_000000005c98720a9cb725eb77ee6347` | 8 | 1 | `fe63cd3b-1de0-4898-8e70-97985ab20c03.png` | K |
| `file_00000000546c71f493b66555f0769057` | 8 | 1 | `card_heos.py` | M |
| `file_000000006214720ab865ec300d8e0e09` | 8 | 1 | `card_system.py` | M |
| `file_00000000e3cc720a94d7c6960916005d` | 8 | 1 | `card_heos.py` | M |
| `file_000000003f9071f4bfe501f51edbabd3` | 8 | 1 | `8237df7e-77cf-4917-a961-88049fdef49f.png` | K |
| `file_00000000e76472468fc28f35388fd367` | 8 | 1 | `18227d3e-f64e-4185-ace5-ad4807781457.png` | K |
| `file_000000004c3871f481bfd75d53b9986b` | 8 | 1 | `card_heos.py` | M |
| `file_00000000b22071f4a26beb2b60e0a4fb` | 8 | 1 | `card_heos.py` | M |
| `file_0000000039f472469a078f7a89522421` | 8 | 1 | `card_hue_doors.py` | M |
| `file_000000001d0871f49754a6f6a58668e9` | 8 | 1 | `3220ee11-da9a-4543-a4ff-0008dd7dc313.png` | K |
| `file_0000000011107246bebb59bf7b7a6059` | 8 | 1 | `8907c7dd-1dfe-4798-9665-05371a6def73.png` | K |
| `file_00000000fd7471f482db54f813ed5ad9` | 8 | 1 | `992c8d42-fe32-4a2c-a5ac-92e5319a89de.png` | K |
| `file_00000000f4a071f48c1e3fbbb248a6c2` | 8 | 1 | `card_heos.py` | M |
| `file_00000000627471f4a0453a532e2bfc38` | 8 | 1 | `68f65500-bf46-43a7-8bb0-fc4a55df17db.png` | K |
| `file_00000000123071f4a949c596e36b71ef` | 8 | 1 | `card_heos.py` | M |
| `file_000000008d9071f48c1e878299f7ab45` | 8 | 1 | `style.css` | M |
| `file_00000000cb00720aa6b6da34c6ec81ed` | 8 | 1 | `fee468b7-14fa-44b1-97fe-2683ea92e2a8.png` | K |
| `file_000000008b3c71f4adb545b0e39cd3f5` | 8 | 1 | `card_heos.py` | M |
| `file_00000000911071f4ba307e534ffa2876` | 8 | 1 | `48d3733f-ee92-440b-b5c9-af86f3d7b588.png` | K |
| `file_0000000004487246b3941132ba5e1c9e` | 8 | 1 | `card_heos.py` | M |
| `file_000000009458720ab979260e4effe6c8` | 8 | 1 | `eb7d4462-6d4a-4df8-b91f-f9ff3f557a09.png` | K |
| `file_00000000f11471f591060259c5e358b4` | 5 | 1 | `9fd93189-fa67-4559-a61b-3e9b4b1c1616.png` | K |
| `file_000000007f90722f826652bd82d68d12` | 5 | 1 | `f63d83a2-6062-4f3f-b9f4-7da0c2bc7e8f.png` | K |
| `file-4wX6vSjy2Z21a6WnTVSgce` | 5 | 1 | `DeployToPi.ps1` | M |
| `file-1fCCcD1vpk3Zasjpjh9wA5` | 5 | 1 | `GitSync.bat` | M |
| `file_000000006b6871f59967e251211cd278` | 5 | 1 | `update.sh` | M |
| `file_0000000088f471f58be64afd5580cf4e` | 5 | 1 | `e1ffd184-7496-4e39-a267-a74fdb7e72d1.png` | K |
| `file_000000008e7871f4939b86b2e0c3a489` | 5 | 1 | `61034a03-a515-4f86-a342-00071113aeea.png` | K |
| `file_00000000c94c71f499f5e102e2f9b6f6` | 5 | 1 | `0cc083fa-dd32-4851-b26d-1b01ba1fb87a.png` | K |
| `file_00000000cb4871f497cc5f7fa9e026a8` | 5 | 1 | `5b5c34f3-f915-4772-b8ed-f35c73f8dc7a.png` | K |
| `file_00000000fa2471f48208779ffa8f1e61` | 5 | 1 | `69edf045-ad73-4d23-97e0-e262a7658fd7.png` | K |
| `file_000000001f6c71f4addc5a7bac279f9e` | 5 | 1 | `54c3f0eb-6751-4812-9f61-40cc8f37d434.png` | K |
| `file-7k89N42VRjWn5dzjseXNLN` | 5 | 1 | `d4f599f1-bf98-41ad-8af9-fa7a9ef0e851.lnk` | M |
| `file_0000000078d0720a8b8ed2eea86ff243` | 5 | 1 | `ab906721-5a05-4c5d-8f05-2a785e9803dc.png` | K |
| `file_000000001a187246866522d802738d87` | 4 | 1 | `c84580b0-efb1-4c3f-8fbf-f4541a79d99a.png` | K |
| `file_00000000d6a4720a915b30101365058e` | 4 | 1 | `09944c77-7ee1-4cc0-8a06-91c8c3ef0060.png` | K |
| `file_00000000fd60720aaeeef6ed9e386f7f` | 4 | 1 | `d334a382-960f-453b-864e-af317c358c26.png` | K |
| `file_00000000e064720a93244a60f16c2dbb` | 4 | 1 | `a8af75e7-3ab9-466a-974a-bef6cb26e1b6.png` | K |
| `file_00000000ef7871f4a0a738b15f66cc18` | 4 | 1 | `3119d91d-f322-42c4-b124-9382be046b12.png` | K |
| `file_00000000b7e8720a9be9cf378876ea65` | 4 | 1 | `home_assistant.py` | M |
| `file_00000000f7c471f49fc4b56021f14618` | 4 | 1 | `card_eqe.py` | M |
| `file_0000000044d471f49c81be8bf8dc7a42` | 4 | 1 | `7e67eac0-213d-42bf-958c-ee87fda466ff.png` | K |
| `file_000000005340720ab87b5b415d828a84` | 2 | 1 | `card_eqe.py` | M |
| `file_00000000ed5c720abb217ab74d23941d` | 2 | 1 | `39e000b6-f84a-432f-9b8d-c56b05e15787.png` | K |
| `file_00000000f5a471f4a5ed10f6d43e972b` | 2 | 1 | `17e7e968-f2e9-446b-b2dd-c8f5da163dc7.png` | K |
| `file_0000000008b471f4a1b0d072afc9580b` | 2 | 1 | `8701ff54-8d01-4b71-b46f-705a71fa130c.png` | K |
| `file_000000004bac724690683ea4f8f53d40` | 2 | 1 | `home_assistant.py` | M |
| `file_00000000b3a88211812c28ab3b56d561` | 1 | 1 | `image(20261028-094434).png` | K |
| `file_00000000bb9882108611e3d9be7cbacb` | 1 | 1 | `image(20261028-094519).png` | K |
| `file_000000001b7c81f5b8d88f75b010dba1` | 1 | 1 | `image(20261028-094754).png` | K |
| `file_00000000286481f4a92643286159d7ac` | 1 | 1 | `image(20261028-094240).png` | K |
| `file_00000000d74c821196541d06220bbf57` | 1 | 1 | `image(20261028-094906).png` | K |
| `file_00000000411c82109376e27ea958a31a` | 1 | 1 | `image(20261028-093636).png` | K |

</details>

### Generoidut lataukset

Nämä ovat 34 erillistä keskustelu/polku-paria. Kaikissa saatavuusluokka on **viite, ei vahvistettua alkuperäistä tiedostosisältöä / S-P0**. Polkujen samuus eri keskusteluissa ei todista samaa tiedostoa. Nimeltään samanlaiset nykyiset repo-dokumentit ovat käyttökelpoisia dokumenttivastineita, mutta eivät tavutason vertailutuloksia.

| Keskustelu nro | Viestissä havaittu sandbox-polku |
| --- | --- |
| 18 | `/mnt/data/REFACTORING.md` |
| 33 | `/mnt/data/REFACTORING.md` |
| 35 | `/mnt/data/REFACTORING_UPDATED.md` |
| 54 | `/mnt/data/REFACTORING_updated.md` |
| 56 | `/mnt/data/CARD_NAMEDAY.md` |
| 68 | `/mnt/data/CHANGELOG.md` |
| 68 | `/mnt/data/CHANGELOG_EN.md` |
| 68 | `/mnt/data/README_en.md` |
| 68 | `/mnt/data/README_fi.md` |
| 86 | `/mnt/data/ui.py` |
| 87 | `/mnt/data/MAC-analyysi.xlsx` |
| 97 | `/mnt/data/WMO_weather_terms_fi.xlsx` |
| 101 | `/mnt/data/kotidashboard_btc.zip` |
| 101 | `/mnt/data/kotidashboard_full_fixed.zip` |
| 101 | `/mnt/data/kotidashboard_full_py/dashboard_full.py` |
| 101 | `/mnt/data/kotidashboard_local_namedays.zip` |
| 101 | `/mnt/data/kotidashboard_local_proxy.zip` |
| 101 | `/mnt/data/kotidashboard_local_proxy_v2.zip` |
| 101 | `/mnt/data/kotidashboard_namedays_builder.zip` |
| 101 | `/mnt/data/kotidashboard_namedays_webcal.zip` |
| 101 | `/mnt/data/kotidashboard_no_sw.zip` |
| 101 | `/mnt/data/kotidashboard_no_sw_v2.zip` |
| 101 | `/mnt/data/kotidashboard_pwa.zip` |
| 101 | `/mnt/data/kotidashboard_pwa.zip` |
| 101 | `/mnt/data/kotidashboard_pwa_fix.zip` |
| 101 | `/mnt/data/kotidashboard_pwa_fix2.zip` |
| 101 | `/mnt/data/kotidashboard_rebuilt.zip` |
| 103 | `/mnt/data/Fully_Kiosk_Settings_A5.pdf` |
| 104 | `/mnt/data/app_reordered.py` |
| 104 | `/mnt/data/app_reordered_tight.py` |
| 104 | `/mnt/data/app_reordered_tight_margin.py` |
| 107 | `/mnt/data/app.backup.py` |
| 107 | `/mnt/data/app.before_fix.py` |
| 107 | `/mnt/data/app.py` |

## 6. Aiempi kohdennettu lähdekooditarkistus (8.11.2026)

Seuraava osuus säilyttää aiemman sähkö-/EQE- ja Hue-tarkistuksen. Se on staattinen kartoitus, ei ajonaikainen turvallisuus- tai toimivuuskoe. Uuden tietoviennin saatavuus- ja säilytysluvut ovat tämän dokumentin osioissa 1–5.

### Kohdennetut kokonaisuudet

| Aihe aiemmissa keskusteluissa | Repossa tarkistettu näyttö | Johtopäätös |
| --- | --- | --- |
| Hue Secure -ovikontaktit ja v2 API (2025-12) | `src/api/hue_contacts_v2.py`, `src/viewmodels/hue_contacts.py`, `src/ui/card_hue_doors.py` sekä niihin liittyvät testit | **Repossa.** Koodi yhdistää v2:n `device`- ja `contact`-resurssit, tunnistaa `contact`/ `no_contact` -tilat ja käyttää kolmea ovikorttia. Viewmodelin yli 3 tunnin stale-raja on toteutettu. |
| Sähköhintakortin 15 min -resoluutio (2025-11) | `src/ui/card_prices.py`, `src/api/prices_15min_vm.py` (UI:n importissa) | **Repossa osittain varmennettu.** UI näyttää seuraavat 12 tuntia 15 minuutin jaksoina. Historiallisen keskustelun fallbackin ja API-formaattien yksityiskohtia ei ole vielä verrattu viewmodelin toteutukseen. |
| EQE/Home Assistant -kortin mittaus ja ohjaus (2026-01) | `src/ui/card_eqe.py` viittaa `set_eqe_lock`, `set_eqe_preclimate`, `set_eqe_charging_enabled` -funktioihin | **Repossa kirjoittavia toimintoja.** Vanhan keskustelun maininta pelkästä ehdotetusta write-ohjauksesta on vanhentunut; tämänhetkinen koodi sisältää toimintoja, joiden käyttöoikeudet ja todellinen toimivuus on vielä testattava HA-ympäristössä. |
| Raspberry Pi:n systemd-ajo, Git-päivitys ja portti 8787 (2025-11) | `README.md`, `scripts/update.sh`, `scripts/DeployToPi.ps1` | **Dokumentoitu, mutta nykyympäristö tarkistettava.** Kaksi eri päivitysskriptiä on erotettava; ks. uuden inventointikierroksen korjaus. `scripts/update.sh`:n `git clean -fdx` on edelleen tarkistettava. |
| CRLF/LF-virhe Linuxin shell-skripteissä (2025-11) | `.gitattributes` | **Repossa.** LF-säännöt `.sh`-, `.py`- ja `.md`-tiedostoille; Windowsin PowerShell-skripteissä CRLF. |
| Sovelluksen arkkitehtuurikaaviot (2025-10) | `docs/mermaid/sequence_electricity.md`, README | **Tarkistettava.** Vanha sähkönhintasekvenssi kuvaa tuntidataan viittaavaa normalisointia, eikä sen ajantasaisuutta 15 min -viewmodeliin nähden ole varmistettu. |
| Git-repositorion siirto, hävinnyt `.git`-hakemisto ja Windowsin venv (2025-11) | `main`-haaran repo on nyt GitHubissa käytettävissä | **Historiallinen ympäristöongelma.** Ei nykyiseksi virheeksi ilman paikallisen koneen tarkistusta. |
| Pi:n paikallisen rsync-varmuuskopion rekursio (2026-01) | Ei tutkittu varmistusskriptiä tai palautusprosessia | **Tarkistettava.** Aiemmassa keskustelussa raportoitiin alkuperäisen varmistuksen täyttäneen levyä ja korjatun varmistuksen onnistuneen; todennettu palautettavuus puuttuu. |
| Windows–Ubuntu-kaksoiskäynnistys ja NTFS-kirjoitusliitos (2026-10) | Ei sovelluksen lähdekoodimuutos | **Muu projekti: Computers & Linux.** Isäntäjärjestelmän liitostilaa ei päätellä GitHubista. |

## Tarkistuksessa löytyneet konkreettiset ylläpitoriskit

1. **Hue:n yhteysturvallisuus:** `src/api/hue_contacts_v2.py` kutsuu Hue Bridgeä asetuksella `verify=False` ja vaimentaa TLS-varoitukset. Selvitä paikallisen varmenteen hallinta ennen muutoksia. Nykyistä toimivaa integraatiota ei saa rikkoa dokumentaatiotyön yhteydessä.
2. **Hue:n anturin kohdistus:** `src/viewmodels/hue_contacts.py` kohdistaa puuttuvan ovinimen tarvittaessa API:n palautusjärjestyksen perusteella seuraavaan vapaaseen anturiin. Jos laitteen nimeä ei tunnisteta, kortin ovinimi voi kohdistua väärään anturiin. Tämä on tarkistettava erillisillä testeillä.
3. **EQE:n ohjauskutsut:** `src/ui/card_eqe.py` sisältää säikeistettyjä, asynkronisesti vahvistettavia lukitus- ja esilämmitystoimintoja. Erota näkyvä ohjauksen tila todellisesta Home Assistantin kuittauksesta; älä oleta fyysisen toiminnon onnistumista pelkästä UI-vastauksesta.
4. **Päivitysskriptit:** `scripts/update.sh` tekee `git reset --hard` ja `git clean -fdx`. **Korjaus uudella inventointikierroksella:** repossa on myös juuritason `update.sh`, jota `scripts/DeployToPi.ps1` kutsuu. Polku ei tämän perusteella ole virhe. Skriptien erilaiset päivitysmenetelmät on dokumentoitava erikseen.
5. **Sekvenssidokumentaatio:** `docs/mermaid/sequence_electricity.md` ei ilmiselvästi kuvaa samaa nykyistä 15 minuutin toteutusta kuin `src/ui/card_prices.py`. Aseta lähdekoodi ja testit etusijalle, kunnes dokumentti päivitetään.


### Sähkö ja EQE: jatkotarkistuksen yksityiskohdat


Tässä osiossa tarkistettiin `main`-haaran lähdekoodia ja testien sisältöä. Testejä **ei ajettu**, eikä sovelluksen tai Home Assistantin ajonaikaista toimintaa tarkistettu.

### Sähkönhintakortti

- `src/api/electricity_service.py` hakee ensisijaisesti suoraa 15 minuutin pörssisähködataa. Jos sitä ei ole, `fetch_prices_for` hakee tuntihinnat ensisijaisesta lähteestä ja varalähteestä. Tuntidataa normalisoidaan tai laajennetaan neljäksi 15 minuutin jaksoksi. **Varalähdelogiikka on siis koodissa**, vaikka sitä ei aiemmin voitu vahvistaa pelkästä UI-kortista.
- `src/api/prices_15min_vm.py` hakee kuluvan ja seuraavan päivän hinnat ja pyrkii muodostamaan 48 varttijaksoa eli seuraavat 12 tuntia. Jos jaksolle ei ole dataa, se ohitetaan, joten näytössä voi olla vähemmän kuin 48 palkkia.
- `tests/test_prices_15min_vm.py` tarkistaa muun muassa täyden 48 jakson tapauksia, vuorokauden vaihtumisen ja alle minuutin aikaleimapoikkeaman. `tests/test_card_prices_ui.py` tarkistaa onnistuneen korttirenderöinnin ja poikkeustilanteen. Nämä ovat **olemassa olevia testejä**, eivät tässä tarkistuksessa suoritettuja testituloksia.
- `docs/mermaid/sequence_electricity.md` kuvaa aiempaa `fetch_electricity`-polkua ja tuntihintoihin liittyvää rajapintaa. Päivitä kaavio vastaamaan ketjua `card_prices -> prices_15min_vm -> electricity_service -> 15min adapteri / tuntidatan varalähde` sekä aikaleimojen ja puuttuvan datan käsittelyä.
- Avoin testauskohde: todellisen varttidatan ja tuntidatasta laajennetun varttiesityksen erottaminen. Tuntihinnasta johdettu neljä samanarvoista jaksoa ei ole itsenäistä toteutunutta varttihinnoittelua.

### EQE / Home Assistant

- `src/api/home_assistant.py` käyttää HA:n palvelukutsuihin Bearer-tokenia ja HTTP POST -pyyntöä. `set_eqe_lock`, `set_eqe_preclimate` ja `set_eqe_charging_enabled` muodostavat palvelun nykyisen konfiguraation perusteella; puuttuvista entiteettimäärityksistä nostetaan virhe.
- `src/ui/card_eqe.py` lukee komennot Streamlitin `st.query_params`-arvoista (`eqe_lock`, `eqe_preclimate`, `eqe_charge`). Tämä tarkoittaa, että ohjaustoiminto voidaan pyytää URL-parametrilla, mikä edellyttää erillistä käyttöoikeus-, vahvistus- ja toistokutsutarkastelua. HA-tokenin käyttö sisäisessä POST-kutsussa **ei yksin ole näyttöä siitä**, että sovelluksen käyttäjät ja URL-ohjaukset olisi valtuutettu turvallisesti.
- Lukitus- ja ilmastointitoimissa UI käynnistää taustasäikeen, näyttää välitilan ja yrittää varmistaa palautuneen tilan Home Assistantista. Latauksen kytkentä tekee myös kirjoittavan palvelukutsun ja käyttää tila-/päivityslogiikkaa. Kutsu on eri asia kuin auton todellinen toiminnon suorittaminen.
- `tests/test_home_assistant.py` sisältää lukituksen palvelukutsun ja lock/switch-domainin testit. `tests/test_card_eqe.py` sisältää query-parametripolkujen, konfiguraation puuttumisen, latauksen kytkennän ja lukitusvirheen testit. Nämä testit eivät sellaisenaan osoita erillisen URL-kutsujen valtuutus- tai CSRF-suojauksen toimivuutta.
- Tarkistettava: tuntemattomat `eqe_lock`-parametriarvot tulkitaan koodissa `unlock`-pyynnöksi, ja tuntemattomat `eqe_preclimate`-arvot `off`-pyynnöksi. Suositus on rajata sallitut arvot eksplisiittisesti ja torjua muut.
- Tarkistettava: `set_eqe_lock` voi sisällyttää HA:n HTTP-virhevastauksen raakatekstin poikkeusviestiin. Arvioi ennen tuotantokäyttöä, voiko viesti päätyä UI:hin tai lokeihin ja sisältää arkaluonteista tietoa.
- **Ei tehty:** autentikointi-/käyttöoikeuskoetta, autentikoimatonta selainkoetta, automaattisia testiajoja tai oikeita HA:n/ajoneuvon ohjauspyyntöjä.


## 7. Jäljellä olevat rajatut toimet

- [x] Kaikki aiemman hakemiston 111 keskustelua kohdistettu vientiin.
- [x] Nykyhaarat ja sivuhaarat erotettu; viennissä ei puuttuvia vanhempisolmuja.
- [x] Olennaiset uudet vaatimukset ja dokumentaation ristiriidat kirjattu; erityisesti zen-tekijärajaus ja HEOSin puuttuminen main.py:n näkymästä.
- [x] 738 liite-esiintymää yksilöity 734 tunnukseksi; 255 kuvatiedostoa saatavilla ja yleiskatsottu, 68 liitteen tekstikatkelmat erotettu alkuperäisistä.
- [x] Kaksi projektin Sources-tiedostoa luettu ja verrattu dokumentaatioon.
- [x] Kahden päivitysskriptin ero ja HA-asetusten etusijajärjestys kirjattu.
- [ ] Käyttäjän päätös zen-tekijärajauksen säilyttämisestä ja HEOS-kortin nykyisestä roolista. Tämä auditointi ei tilaa koodimuutosta.
- [ ] Puuttuvien alkuperäisten lähdeliitteiden ja canvasien erillinen arkistointi tai dokumentoitu päätös, ettei vanhoja versioita tarvita. 483 binääritiedoston puute ei ratkea uudella saman vientipaketin purkamisella; 68 katkelmaa ei korvaa alkuperäisiä.
- [ ] HISTORICAL_DECISIONS.md:n aiemman polkuväitteen sovitus tämän auditin korjaukseen ja README:n HEOS-kuvauksen täsmennys erillisessä dokumentaatiomuutoksessa.
- [ ] Pi:n nykyinen käyttöönotto, palautuksen toimivuus ja EQE-ohjausten valtuutus erillisessä teknisessä tarkistuksessa.
- [ ] Käyttäjän erillinen katselmointi ja päätökset PR:n yhdistämisestä, keskustelusiirroista tai poistoista.

**Tehty muutos:** vain tämä Markdown-auditointi PR #4:n nykyiseen haaraan. Ei keskustelu-/projekti-/liitepoistoja, arkistointia, keskustelusiirtoja, PR:n yhdistämistä, lähdekoodimuutoksia, testiajoja, palvelinmuutoksia tai laiteohjausta.

**Poistovalmius: EI KOKO PROJEKTILLE.** Viestihistorian aiempi saatavuuseste on poistunut tämän viennin osalta. Jäljellä ovat nimenomaisesti liitteiden/canvasien säilytysratkaisu, dokumentaation avoimet valinnat sekä käyttäjän erillinen hyväksyntä. Säilytä alkuperäinen yksityinen ZIP ja poimittu aineisto siihen asti.
