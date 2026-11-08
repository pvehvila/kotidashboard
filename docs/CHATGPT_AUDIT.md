# ChatGPT-keskustelujen tekninen inventointi (osittainen)

Päivitetty: 2026-11-08  
Tila: **Keskusteluluettelo inventoitu, sisältö- ja liiteauditointi osittainen; ei poistovalmiutta.** Alla säilyvät aiemman kohdennetun tarkistuksen havainnot. Uusi 2026-11-08 inventointikierros täydentää ja tarvittaessa korjaa niitä: 111 keskustelua, 405 saatavilla ollutta vuoroa sekä kaksi projektin lähdetiedostoa. Vanhempien viestien ja tiedostoliitteiden kattavuutta ei ole vahvistettu.

## Käytetty luokittelu

- **Repossa:** keskustelun keskeinen toteutus löytyy lähdekoodista. Ei tarvetta säilyttää keskustelua toteutuksen ainoana lähteenä.
- **Dokumentoitu:** pysyvä historiallinen havainto kirjattu `HISTORICAL_DECISIONS.md`-tiedostoon.
- **Tarkistettava:** käyttäjän aiempaa päätöstä, ehdotusta tai historiallista ongelmaa ei voida vielä todentaa nykytilaksi.
- **Muu projekti:** aihe ei kuulu Kotidashboardin sovelluskoodiin.

## Kohdennetusti tarkistetut kokonaisuudet

| Aihe aiemmissa keskusteluissa | Repossa tarkistettu näyttö | Johtopäätös |
| --- | --- | --- |
| Hue Secure -ovikontaktit ja v2 API (2025-12) | `src/api/hue_contacts_v2.py`, `src/viewmodels/hue_contacts.py`, `src/ui/card_hue_doors.py` sekä niihin liittyvät testit | **Repossa.** Koodi yhdistää v2:n `device`- ja `contact`-resurssit, tunnistaa `contact`/ `no_contact` -tilat ja käyttää kolmea ovikorttia. Viewmodelin yli 3 tunnin stale-raja on toteutettu. |
| Sähköhintakortin 15 min -resoluutio (2025-11) | `src/ui/card_prices.py`, `src/api/prices_15min_vm.py` (UI:n importissa) | **Reposssa osittain varmennettu.** UI näyttää seuraavat 12 tuntia 15 minuutin jaksoina. Historiallisen keskustelun fallbackin ja API-formaattien yksityiskohtia ei ole vielä verrattu viewmodelin toteutukseen. |
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

## Seuraava inventointikierros

- [x] Inventoi työkalun koko aktiivinen ja arkistoitu keskusteluluettelo (111 projektikeskustelua); liiteinventaario ja sisältörajoitukset alla.
- [ ] Hanki puuttuvat vanhemmat viestit ja tiedostoliitteet; täydellinen sisältöauditointi on kesken.
- [ ] Vertaile `src/api/prices_15min_vm.py` ja sen testit aiemman sähkönhintapäätöksen fallback-vaatimuksiin.
- [ ] Tarkista EQE:n kirjoittavien ohjausfunktioiden suojaus, palautteet ja testit.
- [ ] Tarkista, mitkä keskustelut koskevat vain koneiden ja palveluiden ylläpitoa ja kuuluvat Computers & Linux -projektiin.
- [ ] Tarkista, että tärkeät päätökset löytyvät koodista, testeistä, dokumentaatiosta tai issueista.
- [ ] Älä arkistoi tai poista keskusteluja tämän osittaisen kartoituksen perusteella automaattisesti.


## Kohdennettu jatkotarkistus 2026-11-08: sähkö ja EQE

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

### Siirtopäätös

Näiden aiheiden **nykyinen koodillinen toteutus** on Gitissä ja voidaan dokumentoida ilman vanhojen raakakeskustelujen säilyttämistä ensisijaisena lähteenä. ChatGPT-projektin täydellinen poistovalmius on silti avoin, kunnes kaikkien keskustelujen ja liitteiden inventointi on tehty.


## Keskustelu- ja liiteinventaario 2026-11-08

### Menetelmä ja täsmällinen kattavuus

Kohde on ChatGPT-projekti **Kotidashboard**, projektitunnus
`g-p-68e77f35e33c8191ba7b0692012d3816`.
Samanniminen paikallinen Codex-projekti ei ole tämän inventaarion keskustelulähde.

- `list_projects` vahvisti projektin ja tunnuksen.
- `list_threads(mode=history, source=chatgpt, limit=50)`: kaikki 20 aktiivista sivua, yhteensä **954** keskustelua; arkistoidut erikseen, yksi sivu, **14** keskustelua. Molemmat kursorihausta loppuun. Projektitunnuksen perusteella **111 aktiivista ja 0 arkistoitua** Kotidashboard-keskustelua, 111 eri tunnusta. Koko työkalun palauttama projektikohtainen keskusteluluettelo on siis inventoitu. Tämä ei ole palveluntarjoajan täydellinen tietovienti eikä kata jo poistettuja tai tililtä näkymättömiä keskusteluja.
- Jokaiselle 111 keskustelulle tehtiin `read_thread(turnLimit=10, maxOutputCharsPerItem=20000)`. Saatiin **111 sivua ja 405 vuoroa**. Jokainen palautti `nextCursor=null` / `hasMore=false`. **58 keskustelua palautti tasan viisi vuoroa**, vaikka pyydettiin kymmenen. Tämän vuoksi sivutuksen loppuminen ei riitä vahvistamaan koko alkuperäisen historian saatavuutta. Esimerkiksi jatkokeskustelun Windows/Linux-osuus ei näy palautetuissa viidessä siirtotyön vuorossa. Taulukon vuoromäärä tarkoittaa tarkistettavaksi palautettua aineistoa, ei alkuperäisen keskustelun kokonaispituutta.
- Yksi vastaus katkaistiin 20 000 merkkiin: keskustelu **Refaktorointi ui.py:stä**, vastaustunnus `97a9f9c2-4032-4e7d-a42f-8da71017573d`. Työkalu hylkäsi suuremman merkkirajan. Muut palautetut viestit eivät ilmoittaneet vastaavaa katkaisua; pois jääneiden vanhempien viestien määrää ei tunneta.
- Palautetuissa käyttäjäviesteissä on **192 tiedostoliite- ja 74 kuvaliitemainintaa** (mainintojen määrät, ei todistettu määrä yksilöllisiä alkuperäisiä tiedostoja). Tiedostoliitteiden sisältö ei sisältynyt viesteihin.
- Työkalu palautti **73 paikallista kuvaesikatselua**, kaikki 73 tiedostoa olivat luettavissa. Näitä on **72 eri nimellä**; kaksi `packages_HomeDashboard.png`-esikatselua ovat eri liite-esiintymiä, eivät automaattisesti sama sisältö. Esikatselut katsottiin pienennettyinä yhteiskuvina: historiallisia UI-, virhe-, editori- ja kaaviokuvia. Tämä on visuaalinen yleiskatsaus, ei kaikkien pienikokoisten tekstien tai lähdekoodirivien täydellinen tarkistus. Esikatselujen määrä ei todista 74 kuvaliitemaininnan täydellistä yksi yhteen -kattavuutta.
- Avustajavastauksista löytyi **21 sandbox-latausviitettä / 13 erilaista polkumerkkijonoa**. Eri keskustelujen samannimiset polut eivät todista samaa tiedostoa. Ladattavien alkuperäisten sisältöjä ei saatu tällä lukutyökalulla; saatavuus jää vahvistamatta.
- Selaimessa projektin **Sources → All** näytti kaksi lähdetiedostoa, `PROJEKTIOHJEET.md` ja `PERUSTIEDOT.md`. Molemmat luettiin esikatselusta, päiväys 29.10.2026. Näkyvässä lähdeluettelossa ei ollut muita lähteitä. Tämä havainto ei korvaa puuttuvia keskusteluliitteitä.
- Repon vertailutilanne: PR #4:n pää `276ccd7ed49ce1e974bd7c45800f6e5b27210f16`, haara `docs/chatgpt-project-migration-2026-11`, pohja `main` / `913c888bd560dc49e02c54279ccb2369e2ccecb4`. Rekursiivinen tiedostopuu saatiin ilman katkaisua. PR oli avoin luonnos ja yhdistämätön.

**Kattavuuspäätelmä:** otsikkoinventaario on täydellinen käytettävissä olevan aktiivisen ja arkistoidun luettelon rajoissa. Sisältöauditointi on osittainen kaikissa niissä keskusteluissa, joiden vanhempaa historiaa tai liitteitä työkalu ei toimita. Alkuperäisen aineiston kokonaismäärää tai tarkistettua prosenttiosuutta ei voi rehellisesti laskea.

### Säilytys-, siirto- ja poistoluokat

- **S – säilytä:** tekninen lähde, avoin asia tai puuttuva historia/liite. Myöhemmin poistokelpoisuus voidaan arvioida vasta, kun puuttuva aineisto on tarkistettu ja pysyvä tieto säilytetty.
- **M – siirtoehdokas:** taulukossa nimetty kotiprojekti; säilytä siihen asti. Luokka on ehdotus, keskustelua ei siirretty.
- **P0 – ei nyt poistokelpoinen:** koskee kaikkia 111 keskustelua ja kaikkia tässä lueteltuja liite-esiintymiä. Se ei tarkoita, että kaikki raakakeskustelut tarvittaisiin pysyvästi. Tässä kierroksessa ei ole riittävää näyttöä yhdenkään *koko keskustelun* turvallisesta lopullisesta poistamisesta.
- **Dokumentoitu / repossa** kuvaa vain nimettyä havaintoa tai toteutusta. Se ei ole koko keskustelun tai sen kaikkien liitteiden poistohyväksyntä.

### Olennaisten päätösten vertailu dokumentaatioon

| Ryhmä | Keskusteluista saatava olennainen tieto | Vastine ja tämän kierroksen johtopäätös |
| --- | --- | --- |
| P – käyttöönotto, HA ja salaisuudet | Eri Windows/Pi-ympäristöt; HA-osoite ja entiteetit ympäristökohtaisia; salaisuudet eivät julkiseen Gitiin. Tammikuussa käyttäjä pyysi myös Pi:llä toimineen korjauksen vientiä Gitin kautta Windowsiin. | `docs/PROJECT_CONTEXT.md` ja `docs/HISTORICAL_DECISIONS.md` kattavat periaatteen. **Täydennys:** aiempi ehdoton ”Pi ei luo omia sovelluscommitteja” on tavoitetyönjako, ei aukoton historiallinen tosiasia. Pi → Git → Windows -korjaussiirto oli käyttäjän nimenomainen toive, mutta pushin valmistumista ei saatu vahvistettua. |
| H – Hue | v2 ovikontaktit/liike; virhetilat ja palvelun asetukset; v1-fallbackia ehdotettiin myöhemmässä 403-ongelmassa. | README ja aiempi auditointi kuvaavat v2-toteutusta. **Ei näyttöä hyväksytystä pysyvästä v1-siirtymästä.** Älä korvaa v2-kuvausta vanhalla vianrajausohjeella. TLS- ja ovikohdistusriskit ovat edelleen avoimia. |
| E – sähkö | Ensisijainen Pörssisähkö, varalla sahkonhintatanaan; 15 min esitys, seuraavat 12 h, snt/kWh, huominen ja negatiiviset hinnat. Vanha nollaan sidottu asteikko korvautui myöhemmällä negatiivisten hintojen vaatimuksella. | README ja aiemman auditin palvelukartoitus kattavat lähteet. `src/api/prices_15min_vm.py` laskee alarajan datan minimistä; `card_prices.py` käyttää viewmodelin rajoja. UI-otsikko on nyt ”15 min”, ei vanhan keskustelun ”Seuraavat 12 h”; horisontti säilyy. Vanha tuntihintaotsikko ei kumoa myöhempää varttitoteutusta. 100-kertainen hintavirhe on historiallinen raportti, ei tämän kierroksen vahvistama nykyvika. |
| N – nimipäivät | Säilytä flat/nested JSON -tuki ja yhteensopivuus; liputus/pyhäpäivä tärkeimpänä, nimet sekä auringonnousu/lasku kortissa. | `docs/CARD_NAMEDAY.md` dokumentoi järjestyksen, paikallisdatan ja auringot. `REFACTORING.md` ja CHANGELOG 1.1.0 kuvaavat rakenteen muutoksia. Vanhojen latausversioiden tai puuttuvien lähdeliitteiden täydellistä vastaavuutta ei vahvistettu. |
| W – sää ja WMO | Erota tiedostonluku, validointi, muunnos ja UI; päivä/yö-mappaus Excelistä; säilytä vanhat importtipinnat. | `REFACTORING.md` kuvaa erottelun. `src/api/wmo_map_loader.py` sisältää erillisen raakaluennan ja etsii myös `data/WMO_Foreca-koodit.xlsx`:ää; `weather_mapping.py` on repossa. Excelin koko sisältöä ei verrattu alkuperäisiin liitteisiin. |
| HE – HEOS | Play/pause/standby, payload-luku ja tabletilla keskitetty ohjaus sekä leveä kappaleteksti. Kehitysympäristö ei saa käynnistää kodin toistoa vahingossa. | README/CHANGELOG kuvaavat HEOSia ja 1.1.1-korjausta. `card_heos.py`:ssä payload/root-luku, napit vain painalluksesta ja leveä now-playing-alue; `heos_client.py`:ssä play/pause käyttää toistotilaa. **Täydennys:** offline-kehityksen hyväksymiskriteeri on olla lähettämättä toistokomentoja; nykykoodi voi silti lukea tilaa ja kirjautua. Väite täydestä verkkotoimettomuudesta ei ole todennettu. Laitteen standby-käyttäytyminen on yhä käytännössä testaamatta tässä työssä. |
| R – refaktorointi ja julkaisut | Pienet muutokset, API/UI-erottelu, ajantasainen Radon-jono ja kaksikieliset julkaisut. | `REFACTORING.md` on päivätty 7.12.2025 ja hyväksyy neljä rajattua C-tason funktiota; vanhemmat marraskuun jonot eivät sellaisenaan kuvaa nykytilaa. CHANGELOG/CHANGELOG_EN ovat repossa. Dokumenttien laatuprosentit ovat historiallisia väitteitä, eivät uusia testituloksia. |
| T – testaus ja Python | Ei 3.9-tukitarvetta; testien kellonaika, cache ja oikea patch-moduuli eristettävä; verkko mockataan. | `pyproject.toml`: Python >=3.10; `.github/workflows/ci.yml`: matriisi 3.10/3.11. Tämä vastaa 3.9-päätöstä. `QUALITY.md` kuvaa työkalut. Testitiedostojen olemassaolo ei todista, että kaikki vanhat virheet on korjattu. |
| U – UI, kaaviot ja vanhat prototyypit | Tasakorkeat kortit, valitun aikavälin korostus, EUR/ATH, hillitty debug, responsiivinen tablettinäkymä. Vanhoja app.py/dashboard_full.py-versioita ja kaaviolatauksia. | README, `docs/CARD_NAMEDAY.md`, `docs/mermaid/` ja `docs/Fully_Kiosk_Settings_A5.pdf` ovat dokumenttivastineita. Kaikkien vanhojen UI-yksityiskohtien ja kuvien samuutta nykyversioon ei ole todistettu. Vanhoja prototyyppejä ei pidä palauttaa nykyisen moduulirakenteen päälle. |
| M – muu projekti | Yleinen Git/venv-, verkko-, laite- tai matkailuaihe. | Projektirajaus vastaa `docs/PROJECT_CONTEXT.md`:tä. Taulukossa kohde-ehdotus. Yksityisiä osoitteita, verkon tunnisteita tai matkailun henkilökohtaisia tietoja ei kopioida tähän auditointiin. |

### Uudet dokumentaatiokorjaukset ja avoimet päätökset

1. **Julkaisuskriptin polkuhavainto korjattu.** Repossa on sekä `update.sh` että `scripts/update.sh`. `scripts/DeployToPi.ps1` kutsuu olemassa olevaa juuritason tiedostoa. Juuriskripti käyttää `git pull --rebase origin main` ja `requirements.txt`:tä; aiemmin tarkistettu scripts-versio käyttää reset/clean-menetelmää ja Linux-riippuvuuksia. Näiden sekoittaminen johti aiempaan virheelliseen polkuriskiväitteeseen. `HISTORICAL_DECISIONS.md`:n kohta 4.1 on luettava tämän korjauksen kanssa; tiedostoa ei muutettu tässä rajatussa päivityksessä. Käytössä oleva skripti pitää edelleen tarkistaa Pi:ltä. Lisäksi Windows-skripti voi puskea nykyhaaran mutta juuriskripti hakee aina mainin: muun haaran julkaisua ei pidä olettaa.
2. **HA-asetusten etusijajärjestys vahvistettu koodista:** `src/api/home_assistant.py::_get_secret` lukee ensin secretsin suoran avaimen, sitten `[home_assistant]`-osion ja viimeisenä ympäristömuuttujan. README:n ”kuten aiemmin” ei yksin ole täydellinen asennusohje. Tarvitaan erillinen salaisuukseton asetustaulukko ja ympäristökohtainen tarkistus ennen seuraavaa käyttöönottoa.
3. **Päätös, havainto ja ehdotus erotetaan.** Käyttäjän ”nyt toimii” on päivätty toimivuusraportti. Avustajan ”testattu / valmis / kirjoitettu canvasiin” ei yksin todista testiajoa, Git-commitia tai liitteen säilymistä. Vanhojen Codex-avaimia, TLS-ohituksia tai CORS/XSRF-poiskytkentää koskevien ohjeiden oikeellisuutta ei vahvisteta eikä niitä siirretä uusiksi käyttöohjeiksi.
4. **Fully Kiosk:** käyttäjä raportoi Initial Scale -asetuksen auttaneen; muistiinpanon PDF on repossa. Alkuperäisen sandbox-PDF:n ja repo-PDF:n tavutason samuutta ei vahvistettu, joten alkuperäistä ei vielä merkitä poistokelpoiseksi.
5. **Puuttuvat canvasit:** keskusteluissa mm. Refactoring / REFACTORING.md -canvasiin kirjoittaminen on mainittu, mutta canvasien sisältöä tai versiohistoriaa ei palautettu. Niiden kokonaismäärä on tuntematon. Repon samanniminen dokumentti ei yksin todista vastaavuutta.

### Kaikki 111 keskustelua

Tunnisteena on linkin koko keskustelutunnus; otsikot säilytetty työkalun antamassa muodossa.
**V/F/I/A** = palautetut vuorot / tiedostoliitemaininnat / kuvaliitemaininnat / saatavilla olevat kuvaesikatselut.
Nolla tarkoittaa ”ei palautetussa aineistossa”, ei todistetta ettei koko keskustelussa ole liitteitä.
Kaikkien rivien viestisaatavuus on edellä kuvattu rajattu näkymä; P0 koskee jokaista riviä.
Ryhmän kirjain viittaa edellisen vertailutaulukon dokumenttivastineeseen.

| Nro | Keskustelu | V/F/I/A | Ryhmä | Havainto ja säilytys/siirto |
| --- | --- | --- | --- | --- |
| 1 | [Kotidashboard – Windows/Linux](https://chatgpt.com/c/6ae211ad-2930-83ed-b27e-b34119890ee7) | 5/0/0/0 | P | S; P0. Siirtotyön lähtökeskustelu; aiempi Windows/Linux-osuus ei näy palautetuissa vuoroissa. |
| 2 | [Raspberry Pi token virhe](https://chatgpt.com/c/697932d2-0bf4-8330-95e7-dd338f5e713c) | 5/0/0/0 | P | S; P0. Pi toimi käyttäjän mukaan; Pi → Git → Windows -poikkeus aiempaan kehitystyönjakoon. Nykyinen synkronointi vahvistamatta. |
| 3 | [Raspberry Pi palautus Windowsista](https://chatgpt.com/c/69793157-0fd0-8394-b82d-040fe42d2994) | 1/0/0/0 | P | S; P0. Windowsin toimivan version palautus Pi:lle; ei palautuksen onnistumiskuittausta. |
| 4 | [Raspberry Pi 5 ongelma](https://chatgpt.com/c/69791835-0894-8330-aef3-c4c3fcf52bdb) | 5/0/2/2 | H | S; P0. Hue 403/404; v1-fallback on ehdotus, ei vahvistettu korvaava päätös. |
| 5 | [Mercedes-Benz Me API](https://chatgpt.com/c/6977abf4-fd44-8393-81a7-fd38f1494857) | 4/0/0/0 | P | S; P0. EQE-entiteetit ja systemd-oikeudet; ajoasetukset eivät ole nykytilavarmennus. |
| 6 | [Raspberry Pi ja Home Assistant](https://chatgpt.com/c/6978446c-c3b0-838d-b987-42c295aff9b2) | 5/0/0/0 | P | S; P0. HA-kontti ja paikallinen HTTP 200; rsync-varmistuksen palautettavuus avoin. |
| 7 | [Raspberry Pi julkinen osoite](https://chatgpt.com/c/6960de36-8e50-832a-8503-05f454154b70) | 1/0/0/0 | M | M; P0. Ei vahvistettua julkista osoitetta. Computers & Linux -siirtoehdokas. |
| 8 | [HEOS-kortin grafiikka](https://chatgpt.com/c/694e5c26-fc38-8331-8eaf-85bf16598bc8) | 5/1/2/2 | HE | S; P0. Tabletilla leveä now-playing-teksti ja keskitetyt painikkeet; käyttäjän hyväksyntä näkyy. |
| 9 | [HEOS toisto ongelma](https://chatgpt.com/c/694e4504-0950-8332-bc41-f1cd940bd999) | 5/6/0/0 | HE | S; P0. Play/pause ja standby; käyttäjän onnistumiskuittaukset eivät korvaa nykyistä laitekoetta. |
| 10 | [Codex environment variables selitys](https://chatgpt.com/c/693c084b-5594-8328-975f-dde0326d8733) | 5/1/1/1 | M | M; P0. Ympäristöasetukset ja refaktorointiprompti; ristiriitaisia vanhoja avainohjeita ei siirretä käyttöohjeeksi. |
| 11 | [Kompleksisuuden arviointi](https://chatgpt.com/c/6935ae2e-ba8c-832b-abdd-0d6994e821f3) | 5/1/0/0 | R | S; P0. 1.1.0-julkaisutekstit kahdella kielellä; vastine CHANGELOG-tiedostoissa. |
| 12 | [Testivirheet ja korjaukset](https://chatgpt.com/c/69352ddf-ca68-832b-a04e-8519bde2ead2) | 5/4/0/0 | N | S; P0. Nimipäiväkortin HTML-testien ja toteutuksen odotukset. |
| 13 | [Hue liiketunnistimien lisäys](https://chatgpt.com/c/6933edac-47f4-8331-b685-9c964ffac0fe) | 5/0/0/0 | H | S; P0. Hue-v2 ovet/liike, tilan päivitys ja Bandit/TLS-poikkeus; avoimet riskit säilyvät. |
| 14 | [Päivitetty changelog-tiedosto](https://chatgpt.com/c/691c9096-e8dc-832c-9eac-f3e26b329ab8) | 1/2/0/0 | R | S; P0. Refaktorointi- ja testimuutosten changelog-ehdotukset. |
| 15 | [Poista Python 3.9 testi](https://chatgpt.com/c/691c5868-0f18-832d-946a-1b57462f7f83) | 1/0/1/1 | T | S; P0. Käyttäjä ei tarvitse 3.9-tukea; CI 3.10/3.11 ja requires-python >=3.10 vastaavat. |
| 16 | [Testikattavuus ja analyysi](https://chatgpt.com/c/691c2e52-e248-8327-8c00-eb66c0ee4cb1) | 5/0/2/2 | T | S; P0. Testien tyypitys ja kattavuus; ei tuoretta laatutulosta. |
| 17 | [Bitcoin testien lisääminen](https://chatgpt.com/c/691c3538-da8c-8332-9588-92fd3eb9e464) | 5/0/0/0 | T | S; P0. Bitcoin UI-testin patch-kohde; ei uusi ominaisuuspäätös. |
| 18 | [Refaktorointitarpeet Radonilla](https://chatgpt.com/c/691c29ef-a894-832d-910f-fc4bc8f2dff3) | 5/0/0/0 | R | S; P0. REFACTORING.md-latausversio; binäärinen/tekstuaalinen samuus tarkistamatta. |
| 19 | [Refaktorointi ehdotukset](https://chatgpt.com/c/691c22d2-1d68-832e-83f0-b5aa1c356352) | 2/2/0/0 | W | S; P0. WMO-luku, validointi ja transformaatio erilleen. |
| 20 | [Refaktorointi safe_cast](https://chatgpt.com/c/691c21b4-b1a4-832f-aaf7-78592eded873) | 2/2/0/0 | W | S; P0. safe_cast dispatcheriksi; tyyppikohtaiset apurit. |
| 21 | [Refactoring update Radon 2025](https://chatgpt.com/c/691c2639-c978-832d-babd-9288f6148647) | 3/1/0/0 | R | S; P0. Refaktorointijonon päivitys ja canvas; canvas-versiota ei saatu. |
| 22 | [Refaktorointi nimipäivät](https://chatgpt.com/c/691c243f-7f34-832a-a965-204ee7adf7c3) | 1/1/0/0 | N | S; P0. Nimipäivien flat/nested sekä pyhäpäivälogiikan erottelu. |
| 23 | [Refaktorointi ja funktiot](https://chatgpt.com/c/691c1f03-d9bc-8333-b7b8-71606c4e529d) | 2/1/0/0 | W | S; P0. Sääaikajana, rivimuunnos, indeksi ja min/max erilleen. |
| 24 | [Sähkökortti ja Bitcoin-kortti](https://chatgpt.com/c/691b4a2d-9cb0-8325-995c-c10e51fe1e82) | 5/1/2/2 | R | S; P0. Sähkö/Bitcoin-regressiot ja refaktorointicanvas; canvas puuttuu. |
| 25 | [Refaktorointi weather_fetch.py](https://chatgpt.com/c/691b451d-c700-8329-8428-475f5372a353) | 2/1/0/0 | W | S; P0. Säädatan muunnoksen erottelu ja Windows-laatuketjun käynnistys. |
| 26 | [Refaktoroinnin tila](https://chatgpt.com/c/691b4337-e1e0-8329-85f1-3e384069c180) | 1/1/0/0 | R | S; P0. 17.11.2025 Radon-tilanne; myöhempi REFACTORING.md on eri päiväykseltä. |
| 27 | [New chat](https://chatgpt.com/c/691b4217-95c4-8326-ae43-fe96f0870fed) | 1/6/0/0 | N | S; P0. New chat käsittelee nimipäivätestejä: kellonaika vakioitava testeissä. |
| 28 | [Refaktorointi card_prices.py](https://chatgpt.com/c/691b4066-5cb4-8329-bacd-8a50662816bb) | 1/1/0/0 | E | S; P0. Laskenta viewmodeliin, UI:hin otsikko/värit/Plotly. |
| 29 | [Refaktorointi weather_fetch.py](https://chatgpt.com/c/691b3f17-f0d4-832f-8dc6-9ee1f2ea609f) | 1/1/0/0 | W | S; P0. Säähaun ja datamuunnoksen erottelu; ehdotuksen tarkka toteutus tarkistettava. |
| 30 | [HEOS virheilmoitus korjaus](https://chatgpt.com/c/691443a7-2ce4-8327-98d6-182a3e75d49c) | 1/1/0/0 | HE | S; P0. Käyttäjä ei halua etäkehitysympäristön käynnistävän kodin HEOS-toistoa. |
| 31 | [Siirrä git-repository VS Codessa](https://chatgpt.com/c/69144001-10f4-8325-a96c-4f5acde459c4) | 5/0/0/0 | M | M; P0. Reposiirto, puuttuva .git ja venv. Computers & Linux -siirtoehdokas. |
| 32 | [Versionhallinnan käytännöt](https://chatgpt.com/c/69142ab5-ad5c-832c-82d8-34816fbb3762) | 1/0/0/0 | R | S; P0. SemVer-ehdotus; CHANGELOG käyttää SemVeriä. Jokaisen commitin versionnostoa ei vaadita. |
| 33 | [Refaktorointi sähkön hinta](https://chatgpt.com/c/69139e66-ad5c-832c-8fc8-c77eac1619ed) | 5/1/0/0 | E | S; P0. Keskeytynyt refaktorointi; myöhempi REFACTORING ei todista vanhojen testivirheiden korjausta. |
| 34 | [Nimipäivälogiikan refaktorointi](https://chatgpt.com/c/69139a2e-8ae4-8331-b303-8e2aa80bf52e) | 5/10/1/1 | N | S; P0. Calendar-wrapperien yhteensopivuus ja testien oikeat patch-kohteet. |
| 35 | [Refaktorointi ja optimointi](https://chatgpt.com/c/69139865-d39c-8327-8c95-b0919636bdcd) | 3/1/0/0 | R | S; P0. Vanha refaktorointijono ja erillinen ladattava dokumentti. |
| 36 | [Refaktorointi ehdotus safe_cast](https://chatgpt.com/c/691392bc-7304-8330-be6c-14fb62e7b8e8) | 4/2/0/0 | W | S; P0. safe_cast ja vanhojen as_bool/as_int/as_float-nimien säilyttäminen. |
| 37 | [Refaktorointi wmo-mapit](https://chatgpt.com/c/69138f15-77d4-832e-8482-09ed3f6519fa) | 4/10/0/0 | W | S; P0. WMO-modulaarisuus; weather_mapping-yhteensopivuusrajapinta. |
| 38 | [Refaktorointi weather_fetch.py](https://chatgpt.com/c/69138d26-60ac-8332-a254-0fecdee86c23) | 3/2/1/1 | W | S; P0. Säätestin mock kohdistettava todelliseen HTTP-kutsuun. |
| 39 | [Refaktorointi jatkuu](https://chatgpt.com/c/69138a52-fc40-832e-849d-3ceb1a722ee6) | 3/6/2/2 | W | S; P0. Weather-viewmodelin vastuu ja uuden rajapinnan testitarve. |
| 40 | [Refaktorointi jatkaminen](https://chatgpt.com/c/691387cb-93b0-8332-848e-833fe98a978e) | 3/2/2/2 | N | S; P0. Nimipäivähelperit; debug-arvon None-käsittely testissä. |
| 41 | [Refaktorointi ja koodin yhdistäminen](https://chatgpt.com/c/691383f2-4278-832b-8926-aaec6f297a4d) | 3/3/2/2 | N | S; P0. Kalenterilogiikan yhdistäminen; historiallinen 80 testin tulos. |
| 42 | [Testikattavuus ja tulokset](https://chatgpt.com/c/69136afd-58dc-8325-9916-3948d5f3d3b0) | 5/1/1/1 | E | S; P0. Sähköadapterien tyhjä/outo/vanha data; Ruff-korjaukset. |
| 43 | [Testitiedostojen rakentaminen](https://chatgpt.com/c/6913697b-f8c0-832c-9520-27fa682f442c) | 2/3/0/0 | T | S; P0. Utils-testit: builtins.print ja Streamlit-mock. |
| 44 | [HEOS-kortin testit](https://chatgpt.com/c/69136766-2b78-8333-bd1e-27f890b21627) | 4/2/1/1 | HE | S; P0. HEOS-kortin moduuli importlibillä; payload- ja painiketestit. |
| 45 | [Testi korttijärjestelmälle](https://chatgpt.com/c/6913662b-c588-8325-9151-f3f8c1db8021) | 3/1/0/0 | T | S; P0. Järjestelmäkortin moduuli- ja funktioimportin ero. |
| 46 | [Testit päivän zen kortille](https://chatgpt.com/c/691364f1-2afc-8329-8113-985cde94e757) | 3/3/1/1 | T | S; P0. Zen-cache eristettävä testeissä ja oikea moduuli tuotava. |
| 47 | [Testi epäonnistumisten korjaus](https://chatgpt.com/c/691363a6-f350-8332-ac1a-3920f269d836) | 2/6/0/0 | N | S; P0. Kalenterin cache ja UI-moduulin patchaus. |
| 48 | [Testifunktiot pytestilla](https://chatgpt.com/c/691362fc-3fe4-832b-b53a-005dd786ef6c) | 1/1/0/0 | T | S; P0. HTTP retry/JSON-testit ilman oikeita verkkokutsuja. |
| 49 | [Bitcoin testit ja kattavuus](https://chatgpt.com/c/691360d6-cba4-832f-91cc-17f663375936) | 3/4/1/1 | T | S; P0. Bitcoin-cache eristettävä; reload/mock-ehdotuksia. |
| 50 | [Testit sääfunktioille](https://chatgpt.com/c/69135f44-bd50-8330-a1b4-44aacce3d93a) | 1/8/0/0 | W | S; P0. Säätestien verkko, Excel-luku ja kellonaika mockataan. |
| 51 | [Testikattavuus ja raportti](https://chatgpt.com/c/69135945-d738-8329-9389-737ddc9c4f36) | 5/2/2/2 | T | S; P0. Sähköpalvelun testit ja tyyppirajaukset. |
| 52 | [Koodin refaktorointi](https://chatgpt.com/c/691356b2-1efc-8328-978a-cdb0d115c400) | 1/1/1/1 | E | S; P0. Sähkölähteet adaptereihin; palvelulle orkestrointi. |
| 53 | [Refaktoroinnin jatkaminen](https://chatgpt.com/c/6913551e-3d04-8332-80b8-6fe7c56097a9) | 1/1/1/1 | E | S; P0. Sähköparseri → normalisointi → 60/15 min laajennus. |
| 54 | [Refaktorointi ja Radon-tulokset](https://chatgpt.com/c/69135332-d398-8333-b5dc-a7c35b01bb1e) | 3/1/0/0 | R | S; P0. Radon-raportin ja refaktorointidokumentin ristiriidat. |
| 55 | [Merge commit without losing changes](https://chatgpt.com/c/6912f1fc-a084-832f-b718-6e33148a1aa6) | 5/12/0/0 | N | S; P0. Nimipäivä-API:n palautus ja yhteensopivuus; puuttuvia tiedostoliitteitä. |
| 56 | [Palauta rikottu koodi](https://chatgpt.com/c/6911bc93-7820-832e-8383-68ed6983994d) | 5/0/1/1 | N | S; P0. Liputus/pyhäpäivä ylimmäksi, auringot korttiin; CARD_NAMEDAY.md vastaa. |
| 57 | [Palaaminen toimivaan koodiin](https://chatgpt.com/c/6911ad83-6920-8328-9a57-4cde53d33f00) | 5/0/2/2 | N | S; P0. Rikkoutunut UI-palautus ja puuttuvat importit; ei nykyvikaväite. |
| 58 | [Refaktoroida dashboardin koodi](https://chatgpt.com/c/6910d2c1-0854-832b-89d0-fbb91b00c7f0) | 5/0/2/2 | N | S; P0. Säilytä nimipäivän tekstit ja auringon ikonit refaktoroinnissa. |
| 59 | [UML-skripti korjaus](https://chatgpt.com/c/6910f076-6334-8326-95f9-96c83ed20ba5) | 5/0/4/4 | U | S; P0. UML-generointi ja kaavion luettavuus; kuvat ovat historiallisia. |
| 60 | [Arvioi Radon-tuloksia](https://chatgpt.com/c/6910edaa-1f40-8333-ac59-9f49a7b1e8ea) | 3/1/0/0 | R | S; P0. Radon-tulosten perusteella rajattu jatkorefaktorointi. |
| 61 | [Refaktoroidaan bitcoin.py](https://chatgpt.com/c/6910eb2c-0458-8332-a3c0-2f822a57b8c5) | 2/1/1/1 | U | S; P0. Bitcoin HTTP/parsinta/pistemuunnos erilleen. |
| 62 | [Refaktorointi utils.py](https://chatgpt.com/c/6910e849-3e4c-832c-8b9c-f2e42c7c3575) | 3/1/0/0 | U | S; P0. Utils-vastuiden erotteluehdotus; tarkkaa nykyvastaavuutta ei vahvistettu. |
| 63 | [Refaktorointi sähkön hintakortti](https://chatgpt.com/c/6910e6aa-eb1c-8333-930b-9c671976fae6) | 1/1/0/0 | E | S; P0. 12 h / 15 min laskenta viewmodeliin ja yhteensopivuuswrapperit. |
| 64 | [Refaktorointi api.py-tiedostoon](https://chatgpt.com/c/691081d4-3ee8-8329-a8d7-5565bdd53e45) | 5/3/1/1 | E | S; P0. Sähkön data katosi refaktoroinnissa; käyttäjän onnistumiskuittaus. |
| 65 | [Refaktorointi ui.py:stä](https://chatgpt.com/c/69105622-4a48-832a-928c-f397f69a4ca1) | 5/0/4/4 | U | S; P0. UI-modulaarisuus, ulkoasun regressiot ja julkaisuloki; yksi vastaus katkaistu. |
| 66 | [Merge ja salasanan suojaus](https://chatgpt.com/c/691050db-f10c-832e-b407-c3efa057da7c) | 5/3/0/0 | P | S; P0. HEOS-salaisuudet julkisen repon ulkopuolelle; .env/config-liitteet puuttuvat. |
| 67 | [Tidal kortti dashboardiin](https://chatgpt.com/c/690eeaa3-4998-8333-81a7-60278f493ef6) | 5/2/0/0 | HE | S; P0. HEOS-kortti ja kappaletiedon päivitys; kieli/DPR pois järjestelmäkortista. |
| 68 | [Julkaisun tarkistuslista](https://chatgpt.com/c/690b68e5-b1b0-832f-b5b4-25e5faefa7e9) | 5/0/0/0 | R | S; P0. Julkaisu ja kaksikielinen changelog; repo sisältää molemmat. |
| 69 | [Pylance virheet ratkaiseminen](https://chatgpt.com/c/690c6c7a-2654-8325-9fbd-e47d1266f77e) | 5/1/2/2 | U | S; P0. Polkuapu, tulkin valinta ja venv; historiallinen ympäristövika. |
| 70 | [Tasainen korttikorkeus](https://chatgpt.com/c/690b9582-b02c-8329-a0d7-2e7f3bdb1892) | 2/2/0/0 | U | S; P0. Nimipäivä- ja zen-korttien tasakorkeus. |
| 71 | [Zen rajapintojen lokitus](https://chatgpt.com/c/690b9451-2128-8330-921e-334724e88be2) | 1/0/0/0 | U | S; P0. Zen-lähteiden toiminnan lokitus; ei väitettä nykyisestä API-saatavuudesta. |
| 72 | [Lokihaun tarkistaminen api.py](https://chatgpt.com/c/690b8c7b-2980-832f-9a6a-d60ceac8c9fc) | 5/0/3/3 | E | S; P0. Sähkön 100-kertainen yksikkövirhe ja parseriapuri; kuvat historiallista näyttöä. |
| 73 | [Sähkönhinta 15 min](https://chatgpt.com/c/690b5749-7fb0-832f-8bc6-3dff34f96498) | 5/0/0/0 | E | S; P0. Pörssisähkö ensisijaiseksi, sahkonhintatanaan varalle; myöhempi toteutus varttidataa ensin. |
| 74 | [Korjaus Mermaid-tiedostoihin](https://chatgpt.com/c/690b4ce4-b750-8328-a182-9f1f1b99e7a8) | 3/8/3/2 | U | S; P0. Mermaid ilman ulompaa markdown-aitaa; renderöinnin korjaus kuitattu. |
| 75 | [Koodivirheen ratkaisu](https://chatgpt.com/c/6907b340-3a40-8329-845a-6aa41da09ad0) | 5/3/4/4 | W | S; P0. Pilvisyysarvon tyyppimuunnokset ja tulkki/riippuvuudet. |
| 76 | [Virheilmoitus ja ratkaisuvinkit](https://chatgpt.com/c/6907a62d-fde4-8331-a23f-1808e38dd78b) | 5/2/1/1 | U | S; P0. BTC-sarjafunktioiden importit; myöhempi toimivuus kuitattu. |
| 77 | [CSS latausongelma](https://chatgpt.com/c/6907a2b1-ae7c-8325-b593-16e748fcffb9) | 3/4/1/1 | U | S; P0. CSS:n merge-konfliktit ja tumma teema; toimivuus kuitattu. |
| 78 | [Synkkaus ja versionhallinta](https://chatgpt.com/c/69078f01-a154-832e-b9dc-07dd25bc96af) | 5/0/0/0 | P | S; P0. DeployToPi käyttää PiHost-nimeä; historiallinen systemd active -havainto. |
| 79 | [Korjaus git-merge-virheelle](https://chatgpt.com/c/69078c03-bb8c-832b-a1b1-41b2aaa7ee2a) | 1/0/0/0 | P | S; P0. Merge-konfliktimerkit Pythonissa; ei nykytilan vika. |
| 80 | [Python suoritusoikeuden korjaus](https://chatgpt.com/c/69078a3f-1504-8331-b3b6-7cb7f80a1b36) | 4/0/0/0 | P | S; P0. Venvin suoritusoikeus ja portin tuplainstanssit; suojausten poiskytkentä ei uusi suositus. |
| 81 | [Päivitys ja uudelleenkäynnistys](https://chatgpt.com/c/68fe481e-5d04-8326-9c1e-7caf83a85fce) | 5/0/0/0 | P | S; P0. Rebase-konflikti, päivitysskripti ja SSH-agentti. |
| 82 | [Git-merge konflikti python](https://chatgpt.com/c/69048893-1cf0-832c-82e5-0685f029a181) | 5/0/0/0 | P | S; P0. Venv/pyc/interpreter-ongelmat; ympäristökohtainen uudelleenluonti. |
| 83 | [Korjataan README.md linkit](https://chatgpt.com/c/69048346-2128-8330-85a8-996d1d7c1c20) | 5/0/0/0 | U | S; P0. README-banneri; vastine docs/images/banner_kotidashboard.png. |
| 84 | [Kotidashboardin kloonaus](https://chatgpt.com/c/6901d508-3720-8327-9ee3-161bf188517c) | 5/0/0/0 | P | S; P0. Kloonaus ja Git Sync -ehdotus; ei vahvistusta skriptin nykykäytöstä. |
| 85 | [Poista debug-tulosteet](https://chatgpt.com/c/68f7d902-643c-8327-a0c9-48c48e375897) | 4/3/1/1 | U | S; P0. UA-debuglaatikko pois dashboardista; käyttäjän onnistumiskuittaus. |
| 86 | [Refaktorointi Grokin avulla](https://chatgpt.com/c/68e760b4-c194-8332-bdf2-4b0b1e2c83dd) | 3/9/0/0 | U | S; P0. Sähköotsikko ja vanha ui.py; ladattava versio ei korvaa nykyistä moduulirakennetta. |
| 87 | [Kotiverkon optimointi](https://chatgpt.com/c/68f8edfd-e998-832a-b8b3-ff6596922377) | 5/0/1/1 | M | M; P0. Kotiverkon laitteet/osoitteet. Computers & Linux -siirtoehdokas. |
| 88 | [Auringon nousu ja lasku](https://chatgpt.com/c/68f7dbc7-2140-8328-ab0b-ca8f4ce6a777) | 3/1/0/0 | N | S; P0. Auringonnousu ja -lasku nimipäiväkorttiin; dokumentoitu CARD_NAMEDAY.md:ssä. |
| 89 | [Tallinnan aktiviteetit ehdotukset](https://chatgpt.com/c/68eca5d6-eafc-8330-8ddd-c08b846c4192) | 1/0/0/0 | M | M; P0. Matkailuaihe; Travel & Camping -siirtoehdokas, ei sovelluspäätöstä. |
| 90 | [Korjaus y-akselin tekstille](https://chatgpt.com/c/68f14502-a254-832f-bd0e-8e044dab80c1) | 5/0/1/1 | U | S; P0. Otsikosta poiketen selaimen/laiteversion tunnistus; historiallinen UA-rajoite. |
| 91 | [Denon ja Tidal ohjaus](https://chatgpt.com/c/68f0b355-c6f8-832b-9ada-95388b5383a8) | 1/0/0/0 | HE | S; P0. HEOS/Tidal-integraation alkuperäinen ehdotus; nykyinen toteutus erillinen. |
| 92 | [Sääkortin ennusteiden vaihto](https://chatgpt.com/c/68efb3e1-385c-8333-b7ea-d972243ef5bd) | 5/1/1/1 | U | S; P0. Bitcoin 24h/7d/30d-valinta ja valitun painikkeen korostus. |
| 93 | [Poista trace-tulosteet](https://chatgpt.com/c/68ed4943-701c-8332-836a-fedc87ae659b) | 3/5/0/0 | U | S; P0. Sääikonien debug/trace pois normaalinäkymästä; vanhojen apurien poisto vain ehdotus. |
| 94 | [Korjaus pörssisähkön kuvaajaan](https://chatgpt.com/c/68ef87eb-4598-8332-b1e2-733641005474) | 1/1/0/0 | E | S; P0. Negatiiviset sähköhinnat näkyviin; nykyinen viewmodel käyttää myös datan minimiä. |
| 95 | [PoE virransyöttö Raspberry Pi:lle](https://chatgpt.com/c/68ef7346-701c-8331-95e1-8c1e118070d8) | 5/0/0/0 | M | M; P0. PoE/virtalähdeaihe. Computers & Linux -siirtoehdokas; ei hankintapäätöksen vahvistusta. |
| 96 | [Tarkista nimipäivät-kortti](https://chatgpt.com/c/68e7c8b9-8a84-832c-88e8-3527de0d271c) | 5/2/0/0 | N | S; P0. Nimipäiväkortin statusrivi ylimmäksi; vastine CARD_NAMEDAY.md. |
| 97 | [Käännä WMO säätermitaulukko](https://chatgpt.com/c/68e7f312-6f08-8333-a4e9-537ae8fd4b6c) | 5/2/1/1 | W | S; P0. WMO Excelin päivä/yö-sarakkeet; data/WMO_Foreca-koodit.xlsx repossa. |
| 98 | [Vaihto sääikoneet Forecaan](https://chatgpt.com/c/68e7907e-c348-832f-9a80-814dd398725c) | 5/2/0/0 | W | S; P0. Foreca-ikonimappaus ja trace; vanhoja debug-ohjeita ei käyttöönoteta. |
| 99 | [Bitcoin skaalaus parannus](https://chatgpt.com/c/68e7862f-4e20-8332-81b9-125f1b962dd3) | 5/0/0/0 | E | S; P0. Vanha nollaan sidottu sähköasteikko on korvautunut negatiiviset hinnat sallivalla vaatimuksella. |
| 100 | [Otsikkotyyli yhtenäistäminen](https://chatgpt.com/c/68e78279-13d4-8329-bb64-50095912cc7c) | 5/6/1/1 | U | S; P0. Yhtenäiset otsikot ja yhteiset värit configiin. |
| 101 | [Kotidashboardin luominen](https://chatgpt.com/c/68d7f2ed-e070-832c-9f16-0169e4604001) | 5/4/1/1 | U | S; P0. Varhainen dashboard_full.py/HTML/JS-prototyyppi; ei nykyisen Streamlit-repon palautuspaketti. |
| 102 | [Hyvä tabletti kotidashboardiin](https://chatgpt.com/c/68d986bb-4668-8330-883e-515684bfa1ea) | 5/0/0/0 | M | M; P0. Palvelin/tablettivaihtoehdot. Computers & Linux -siirtoehdokas; ehdotukset eivät todista hankintaa. |
| 103 | [Päivittäinen sitaatti lisäys](https://chatgpt.com/c/68e612eb-fe6c-8330-aeaa-0c235141666a) | 5/0/2/2 | U | S; P0. Fully Kiosk Initial Scale ratkaisi käyttäjän mukaan asettelun; PDF-vastine repossa. |
| 104 | [Korttien järjestyksen muutos](https://chatgpt.com/c/68e663a5-39b8-8330-b29e-3badf18d2f52) | 5/0/1/1 | U | S; P0. Vanhoja app.py-asetteluversioita; latausvirheitä ja katkennut merkkijono. |
| 105 | [Testiskripti ohjeet](https://chatgpt.com/c/68e5538d-4878-8325-a486-561ab0c4a9b7) | 5/1/1/1 | E | S; P0. Huomisen hinnat ja nimipäivien JSON; vanhan app.py:n helper-virhe. |
| 106 | [Muutos kotidashboardiin](https://chatgpt.com/c/68e63b43-12b4-8327-b677-b91796e3aa15) | 5/0/1/1 | U | S; P0. Bitcoin EUR/ATH, välilyönti tuhaterottimena ja kuvaajan marginaalit. |
| 107 | [Fonttimuutokset dashboardille](https://chatgpt.com/c/68e645a8-44b8-8332-a5e2-4fff1650a7bb) | 5/1/1/1 | U | S; P0. Fontti/asettelu ja monistuvat sähkökortit; käyttäjän onnistumiskuittaus. |
| 108 | [Kotidashboardin sääkortti](https://chatgpt.com/c/68e5fa5b-9880-8329-8e14-d8f23be854d4) | 5/3/5/5 | E | S; P0. Sähköstä ylimääräiset kortit/keskiarvot pois; ei nykyisen hintabadgen poistopäätös. |
| 109 | [Muutos aikaskaalaan 7 päivään](https://chatgpt.com/c/68e66092-e4a8-8330-a96f-79e1be18683d) | 3/1/0/0 | U | S; P0. Bitcoin-historia 7 päivään ja päiväkohtaiset aikamerkit; myöhemmin 24h/7d/30d. |
| 110 | [Päivitysongelma Fully Kioskissa](https://chatgpt.com/c/68e68859-e824-832c-ab05-78102c22977e) | 5/0/1/1 | U | S; P0. Fully-näkymän marginaalit ja otsikkovälit; käyttäjän spacer-valinta. |
| 111 | [Pörssisähkön otsikkoidea](https://chatgpt.com/c/68e6b43f-0ddc-832a-88cc-a1e30847d458) | 5/1/0/0 | E | S; P0. Sähköotsikkoon nykyhinta ja seuraavat 12 h, ei muutosprosenttia; nykyinen 15 min otsikko on myöhempi. |

### Projektin kaksi lähdetiedostoa

| Lähde | Saatavuus ja vertailu | Säilytys / siirto / poisto |
| --- | --- | --- |
| PROJEKTIOHJEET.md, 29.10.2026 | Selaimen esikatselu luettu. Repo/versio/alusta tarkistettava, integraatiot erotettava koodista, toimivat kortit säilytettävä, tunnuksia ei tallenneta, projektien työnjako. Vastine: PROJECT_CONTEXT.md, AGENTS.md ja tämä auditointi. | Säilytä alkuperäinen toistaiseksi. Olennainen tekninen sisältö dokumentoitu; ei automaattista poistohyväksyntää. |
| PERUSTIEDOT.md, 29.10.2026 | Selaimen esikatselu luettu. Tarkoitus, aihealueet ja työnjako; toteaa myös aiemman kartoituksen osittaisuuden ja täydennettävät prioriteetit. Vastine: PROJECT_CONTEXT.md. Ei vahvistettuja uusia teknisiä prioriteetteja. | Säilytä kunnes siirto katselmoitu; mahdollinen myöhempi poistoehdokas sisällön säilymisen varmistamisen jälkeen. |

### Kuvien esiintymäkohtainen inventaario

Kaikki alla olevat 73 esikatselua olivat paikallisesti luettavissa ja katsottiin pienennetystä yhteiskuvasta. Kuvien yleinen sisältö vastasi keskustelujen UI-/virhe-/testi-/kaavioaiheita. Niistä ei päätelty uutta ajantasaista laitetilaa tai testitulosta. **S/P0 joka rivillä.** Tarkat pienet tekstit, alkuperäinen resoluutio ja mahdolliset tunnisteet on tarvittaessa tarkistettava alkuperäisistä ennen lopullista siirto-/poistoratkaisua. Kuvia tai niiden verkko-/henkilötietoja ei julkaistu repossa. Tiedostonimi ei ole sisällön yksilöivä tarkiste.

| Kuva | Keskustelu nro | Työkalun palauttama nimi | Saatavuus / käsittely |
| --- | --- | --- | --- |
| 1 | 4 | `d334a382-960f-453b-864e-af317c358c26.png` | Luettava esikatselu; yleiskatsaus; S/P0 |
| 2 | 4 | `3119d91d-f322-42c4-b124-9382be046b12.png` | Luettava esikatselu; yleiskatsaus; S/P0 |
| 3 | 8 | `8237df7e-77cf-4917-a961-88049fdef49f.png` | Luettava esikatselu; yleiskatsaus; S/P0 |
| 4 | 8 | `2b916a68-c9db-478d-8dbf-8f635e092ad5.png` | Luettava esikatselu; yleiskatsaus; S/P0 |
| 5 | 10 | `f5bf046b-564c-4cbb-989d-b74deb900f04.png` | Luettava esikatselu; yleiskatsaus; S/P0 |
| 6 | 15 | `1d8c0fe5-044e-43e0-90f3-115befd50673.png` | Luettava esikatselu; yleiskatsaus; S/P0 |
| 7 | 16 | `afadfd1d-4a37-4d13-9bfb-17d655a65010.png` | Luettava esikatselu; yleiskatsaus; S/P0 |
| 8 | 16 | `f8a455f9-cdcb-40f8-980b-cf5fec65a96b.png` | Luettava esikatselu; yleiskatsaus; S/P0 |
| 9 | 24 | `d23c7501-af8e-44ef-a43e-bab20bbe6a06.png` | Luettava esikatselu; yleiskatsaus; S/P0 |
| 10 | 24 | `70129d68-c38e-4eef-bca3-7fddfe9485cf.png` | Luettava esikatselu; yleiskatsaus; S/P0 |
| 11 | 34 | `b1c0cfc9-0e65-4e22-884c-c80eaeb880ce.png` | Luettava esikatselu; yleiskatsaus; S/P0 |
| 12 | 38 | `2159ba7a-5e61-406e-a20b-07c082fc0a54.png` | Luettava esikatselu; yleiskatsaus; S/P0 |
| 13 | 39 | `f5c2ad79-eb7c-4d25-af5f-2be0f6d187ad.png` | Luettava esikatselu; yleiskatsaus; S/P0 |
| 14 | 39 | `ba89344b-37b7-485a-9449-f508e6b24932.png` | Luettava esikatselu; yleiskatsaus; S/P0 |
| 15 | 40 | `8a01bf2a-a467-44f9-8490-eb5780afb560.png` | Luettava esikatselu; yleiskatsaus; S/P0 |
| 16 | 40 | `1579035d-2456-4433-af04-9f6fc69ed2a0.png` | Luettava esikatselu; yleiskatsaus; S/P0 |
| 17 | 41 | `874a7569-ad1e-4b4f-a032-823db7353d4a.png` | Luettava esikatselu; yleiskatsaus; S/P0 |
| 18 | 41 | `5455395c-7a06-4d3f-b10e-9e6f9e46e2a2.png` | Luettava esikatselu; yleiskatsaus; S/P0 |
| 19 | 42 | `17e4bc23-5dcf-467a-aae5-e20453e6c13f.png` | Luettava esikatselu; yleiskatsaus; S/P0 |
| 20 | 44 | `d476d6da-af4d-4b0f-b247-7724de629cdd.png` | Luettava esikatselu; yleiskatsaus; S/P0 |
| 21 | 46 | `99d19b7d-d5f9-4097-b31e-b925805368dd.png` | Luettava esikatselu; yleiskatsaus; S/P0 |
| 22 | 49 | `d42e2d66-bb36-4823-87e8-fe46c975ba09.png` | Luettava esikatselu; yleiskatsaus; S/P0 |
| 23 | 51 | `818b8727-a455-4d19-8e17-35ca50eec6e0.png` | Luettava esikatselu; yleiskatsaus; S/P0 |
| 24 | 51 | `abd26f4d-6537-44e1-a036-30e9135ccc2e.png` | Luettava esikatselu; yleiskatsaus; S/P0 |
| 25 | 52 | `abf6c70a-ca80-4e31-a763-b61c0865cf35.png` | Luettava esikatselu; yleiskatsaus; S/P0 |
| 26 | 53 | `aed5590f-166b-4bc4-8aa7-d2e43641600a.png` | Luettava esikatselu; yleiskatsaus; S/P0 |
| 27 | 56 | `014a6b75-de27-4892-a2ae-db0a084edc10.png` | Luettava esikatselu; yleiskatsaus; S/P0 |
| 28 | 57 | `bba81a10-1162-4157-8939-9e019d213335.png` | Luettava esikatselu; yleiskatsaus; S/P0 |
| 29 | 57 | `b9abb43f-3b44-4b55-b3d0-47b24d67bb89.png` | Luettava esikatselu; yleiskatsaus; S/P0 |
| 30 | 58 | `e939abb2-f28e-4a70-91ce-054fc0945f14.png` | Luettava esikatselu; yleiskatsaus; S/P0 |
| 31 | 58 | `4a1178e4-8e1e-40db-b60e-f210ee8e9336.png` | Luettava esikatselu; yleiskatsaus; S/P0 |
| 32 | 59 | `packages_HomeDashboard.png` | Luettava esikatselu; yleiskatsaus; S/P0 |
| 33 | 59 | `classes_HomeDashboard.png` | Luettava esikatselu; yleiskatsaus; S/P0 |
| 34 | 59 | `packages_HomeDashboard.png` | Luettava esikatselu; yleiskatsaus; S/P0 |
| 35 | 59 | `f3663a31-f160-4c2a-9c47-5fbe5e4d773e.png` | Luettava esikatselu; yleiskatsaus; S/P0 |
| 36 | 61 | `2aa09e62-40f3-49e4-8f14-597e0af651ee.png` | Luettava esikatselu; yleiskatsaus; S/P0 |
| 37 | 64 | `3942c05e-b5b4-4a0e-af92-2bfeb0168293.png` | Luettava esikatselu; yleiskatsaus; S/P0 |
| 38 | 65 | `80cd2c82-b47e-42a1-b778-dd80beb88cc3.png` | Luettava esikatselu; yleiskatsaus; S/P0 |
| 39 | 65 | `66abba8f-5351-464f-a8a5-34e297bb7462.png` | Luettava esikatselu; yleiskatsaus; S/P0 |
| 40 | 65 | `3ed09b5b-6352-4624-9d25-4e0c5c93a316.png` | Luettava esikatselu; yleiskatsaus; S/P0 |
| 41 | 65 | `4f8fa1a4-aa54-4b9a-b5f9-0d2c9d28f15d.png` | Luettava esikatselu; yleiskatsaus; S/P0 |
| 42 | 69 | `84bbdc14-7318-4fd8-bcf4-1344fd4a9ebd.png` | Luettava esikatselu; yleiskatsaus; S/P0 |
| 43 | 69 | `bff40a16-127e-4fd1-8381-caecb9522f5d.png` | Luettava esikatselu; yleiskatsaus; S/P0 |
| 44 | 72 | `aaf5f6be-00b7-42cd-aae6-2678d79f9555.png` | Luettava esikatselu; yleiskatsaus; S/P0 |
| 45 | 72 | `3de4ee25-7332-40dd-860f-7bd6e61133f3.png` | Luettava esikatselu; yleiskatsaus; S/P0 |
| 46 | 72 | `0635062d-cdba-4c57-936b-397a612c6748.png` | Luettava esikatselu; yleiskatsaus; S/P0 |
| 47 | 74 | `ca471143-6fe3-4670-a530-1e36cefe8c2a.png` | Luettava esikatselu; yleiskatsaus; S/P0 |
| 48 | 74 | `ac01a690-6401-449b-acd2-9bb4cd2118bb.png` | Luettava esikatselu; yleiskatsaus; S/P0 |
| 49 | 75 | `3907e1a8-985a-4b1a-b69a-a7ee5b964c34.png` | Luettava esikatselu; yleiskatsaus; S/P0 |
| 50 | 75 | `4f6cec9f-de2c-48f3-8851-318a67428cc7.png` | Luettava esikatselu; yleiskatsaus; S/P0 |
| 51 | 75 | `6d028021-0554-4d2c-89b8-71935276113d.png` | Luettava esikatselu; yleiskatsaus; S/P0 |
| 52 | 75 | `859797e8-402e-4a4e-b62a-20f92b269cb0.png` | Luettava esikatselu; yleiskatsaus; S/P0 |
| 53 | 76 | `061de28b-93af-4a2c-a854-fbfc35b8ff9c.png` | Luettava esikatselu; yleiskatsaus; S/P0 |
| 54 | 77 | `0e2ce21b-a01f-4eb6-96b2-4b3200b04de1.png` | Luettava esikatselu; yleiskatsaus; S/P0 |
| 55 | 85 | `b615a842-ec02-40ad-bc39-8f77d70b0441.png` | Luettava esikatselu; yleiskatsaus; S/P0 |
| 56 | 87 | `cd3797a8-7dfe-4369-aa87-7ab805b41288.png` | Luettava esikatselu; yleiskatsaus; S/P0 |
| 57 | 90 | `9807ecb6-77fa-4133-b4e2-5cf4221fc36b.png` | Luettava esikatselu; yleiskatsaus; S/P0 |
| 58 | 92 | `66923dbc-4592-4ffd-9f4e-dc39aa2c27b3.png` | Luettava esikatselu; yleiskatsaus; S/P0 |
| 59 | 97 | `75f8c422-4a37-483e-9d71-012dc8c2f653.png` | Luettava esikatselu; yleiskatsaus; S/P0 |
| 60 | 100 | `a238aa1e-9873-4f1f-bd63-a8179967ad19.png` | Luettava esikatselu; yleiskatsaus; S/P0 |
| 61 | 101 | `835d9ac2-1301-4ba6-a9d2-0fb03008f755.png` | Luettava esikatselu; yleiskatsaus; S/P0 |
| 62 | 103 | `69cae376-074b-4318-a085-7789309327f6.jpeg` | Luettava esikatselu; yleiskatsaus; S/P0 |
| 63 | 103 | `f16d06d7-f28e-4f23-8fa3-36281299e412.png` | Luettava esikatselu; yleiskatsaus; S/P0 |
| 64 | 104 | `41b14964-18c5-4db3-874d-e68b9553e60e.png` | Luettava esikatselu; yleiskatsaus; S/P0 |
| 65 | 105 | `ccb4e5ea-1303-485b-aa1d-2a5ce499169c.png` | Luettava esikatselu; yleiskatsaus; S/P0 |
| 66 | 106 | `cbc28d31-fa97-4777-bd1d-f0ae3af55bfe.png` | Luettava esikatselu; yleiskatsaus; S/P0 |
| 67 | 107 | `f197d484-3363-4314-aeba-662adb1ca7a7.png` | Luettava esikatselu; yleiskatsaus; S/P0 |
| 68 | 108 | `c79eddd1-e63a-4756-86cf-ed9e6918a6cb.png` | Luettava esikatselu; yleiskatsaus; S/P0 |
| 69 | 108 | `3218ddfd-c974-4461-a914-38d93fa37c81.png` | Luettava esikatselu; yleiskatsaus; S/P0 |
| 70 | 108 | `e651a841-e467-4559-b344-29c82c689055.png` | Luettava esikatselu; yleiskatsaus; S/P0 |
| 71 | 108 | `a9af0c05-ca52-4aac-b395-52b1cca01903.png` | Luettava esikatselu; yleiskatsaus; S/P0 |
| 72 | 108 | `26bf84c4-be7f-4246-8c80-0a59ed8d6f57.png` | Luettava esikatselu; yleiskatsaus; S/P0 |
| 73 | 110 | `ad3af5d2-25c1-4520-98f7-bdb9f177f4af.png` | Luettava esikatselu; yleiskatsaus; S/P0 |

### Muut liitteet, latausviitteet ja puuttuva aineisto

**192 tiedostoliitemainintaa:** esiintymien määrä on keskustelutaulukon F-sarakkeessa.
Alkuperäisiä nimiä, tiedostotunnuksia, sisältöjä tai tarkisteita ei palautettu; siksi nimiä ei arvata
keskustelun koodiesimerkeistä. Maininnat eivät välttämättä tarkoita 192 eri tiedostoa.
Saatavuus: metadata vain mainintana, sisältö ei saatavilla tällä työkalulla. Luokka **S/P0**.
Tähän sisältyy myös asetustiedostoihin viittaavaa aineistoa; sitä ei kopioida julkiseen repoon.

Sandbox-latausviitteet (vain viite havaittu; alkuperäistä ei ladattu eikä sisältövastaavuutta vahvistettu):

| Keskustelu nro | Havaittu latauspolku | Repovertailu ja luokka |
| --- | --- | --- |
| 18 | `/mnt/data/REFACTORING.md` | REFACTORING.md (eri päiväys/versio mahdollinen); S/P0 |
| 33 | `/mnt/data/REFACTORING.md` | REFACTORING.md (eri päiväys/versio mahdollinen); S/P0 |
| 35 | `/mnt/data/REFACTORING_UPDATED.md` | REFACTORING.md (eri päiväys/versio mahdollinen); S/P0 |
| 54 | `/mnt/data/REFACTORING_updated.md` | REFACTORING.md (eri päiväys/versio mahdollinen); S/P0 |
| 56 | `/mnt/data/CARD_NAMEDAY.md` | docs/CARD_NAMEDAY.md; S/P0 |
| 68 | `/mnt/data/CHANGELOG.md` | CHANGELOG.md; S/P0 |
| 68 | `/mnt/data/CHANGELOG_EN.md` | CHANGELOG_EN.md; S/P0 |
| 86 | `/mnt/data/ui.py` | Vanha prototyyppi/UI-versio; samaa sisältöä ei todistettu; S/P0 |
| 101 | `/mnt/data/kotidashboard_full_py/dashboard_full.py` | Vanha prototyyppi/UI-versio; samaa sisältöä ei todistettu; S/P0 |
| 101 | `/mnt/data/kotidashboard_full_fixed.zip` | Vanha prototyyppi/UI-versio; samaa sisältöä ei todistettu; S/P0 |
| 103 | `/mnt/data/Fully_Kiosk_Settings_A5.pdf` | docs/Fully_Kiosk_Settings_A5.pdf; S/P0 |
| 104 | `/mnt/data/app_reordered_tight_margin.py` | Vanha prototyyppi/UI-versio; samaa sisältöä ei todistettu; S/P0 |
| 104 | `/mnt/data/app_reordered_tight.py` | Vanha prototyyppi/UI-versio; samaa sisältöä ei todistettu; S/P0 |
| 107 | `/mnt/data/app.py` | Vanha prototyyppi/UI-versio; samaa sisältöä ei todistettu; S/P0 |

Kuvaliitemainintoja on 74, mutta esikatseluja 73. Esimerkiksi keskustelussa
**Korjaus Mermaid-tiedostoihin** on kolme kuvaliitemainintaa ja kaksi palautettua esikatselua.
Näiden lukumäärien erotus on **yksi esiintymä**, ei varma todistus vain yhdestä puuttuvasta alkuperäiskuvasta:
aineistojen yksilöivä kohdistus puuttuu. Kaikkien kuvien alkuperäisversioiden kattavuus on vahvistamatta.

### Jäljellä oleva työ ja poistovalmius

- [x] Käytettävissä oleva aktiivinen ja arkistoitu keskusteluluettelo loppuun asti.
- [x] Jokaiselle 111 keskustelulle tunnus, otsikko, palautetun aineiston määrä, aihevertailu ja säilytys-/siirtoehdotus.
- [x] Kahden näkyvän projektin lähdetiedoston sisältövertailu.
- [x] 73 kuvaesikatselun saatavuus ja visuaalinen yleiskatsaus sekä tiedosto-/latausviitteiden inventaario.
- [ ] Alkuperäiset täydet viestihistoriat, puuttuvat tiedostot, kuvien kattava kohdistus ja canvas-versiot.
- [ ] Puuttuvien aineistojen päätökset ja dokumenttien tarkka sisältövastaavuus.
- [ ] Salaisuukseton HA-asetustaulukko, kahden päivitysskriptin eron yhtenäinen dokumentointi sekä aiemman HISTORICAL_DECISIONS-polkuväitteen korjaus.
- [ ] Pi:n palautus/varmistus ja nykyinen HA/Hue/HEOS/EQE-ympäristö erillisessä teknisessä tarkistuksessa.
- [ ] Käyttäjän erilliset päätökset mahdollisista keskustelusiirroista, poistoista ja PR:n yhdistämisestä.

Tässä työssä muutettiin vain tätä Markdown-tiedostoa. Sovelluskoodia, laitteita, tilejä tai ajoasetuksia ei muutettu; testejä eikä käyttöönottoa ajettu. Keskusteluja, liitteitä tai projektia ei siirretty, arkistoitu tai poistettu. PR #4 jätetään avoimeksi luonnokseksi ja yhdistämättä.

**Projektin poistovalmius: EI VALMIS.** Täsmällinen jatkotarve on puuttuvan sisältöaineiston saaminen
esimerkiksi täydestä keskustelu-/liiteviennistä; pelkkää otsikkoluetteloa ei tarvitse inventoida uudelleen.
