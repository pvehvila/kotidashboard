# ChatGPT-keskustelujen tekninen inventointi (osittainen)

Päivitetty: 2026-11-08  
Tila: **Osittainen**. Tämä kartoitus pohjautuu käytettävissä olleisiin aiempien keskustelujen yhteenvetoihin ja GitHubin `main`-haaran lähdekoodin kohdennettuun tarkistukseen. Kaikkien projektikeskustelujen täydellinen luettelo, viestit ja liitteet eivät olleet käytettävissä, joten tämä ei oikeuta projektin poistamiseen.

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
| Raspberry Pi:n systemd-ajo, Git-päivitys ja portti 8787 (2025-11) | `README.md`, `scripts/update.sh`, `scripts/DeployToPi.ps1` | **Dokumentoitu, mutta nykyympäristö tarkistettava.** Skriptien polkuero ja `git clean -fdx` ovat erillisiä korjaustarpeita. |
| CRLF/LF-virhe Linuxin shell-skripteissä (2025-11) | `.gitattributes` | **Repossa.** LF-säännöt `.sh`-, `.py`- ja `.md`-tiedostoille; Windowsin PowerShell-skripteissä CRLF. |
| Sovelluksen arkkitehtuurikaaviot (2025-10) | `docs/mermaid/sequence_electricity.md`, README | **Tarkistettava.** Vanha sähkönhintasekvenssi kuvaa tuntidataan viittaavaa normalisointia, eikä sen ajantasaisuutta 15 min -viewmodeliin nähden ole varmistettu. |
| Git-repositorion siirto, hävinnyt `.git`-hakemisto ja Windowsin venv (2025-11) | `main`-haaran repo on nyt GitHubissa käytettävissä | **Historiallinen ympäristöongelma.** Ei nykyiseksi virheeksi ilman paikallisen koneen tarkistusta. |
| Pi:n paikallisen rsync-varmuuskopion rekursio (2026-01) | Ei tutkittu varmistusskriptiä tai palautusprosessia | **Tarkistettava.** Aiemmassa keskustelussa raportoitiin alkuperäisen varmistuksen täyttäneen levyä ja korjatun varmistuksen onnistuneen; todennettu palautettavuus puuttuu. |
| Windows–Ubuntu-kaksoiskäynnistys ja NTFS-kirjoitusliitos (2026-10) | Ei sovelluksen lähdekoodimuutos | **Muu projekti: Computers & Linux.** Isäntäjärjestelmän liitostilaa ei päätellä GitHubista. |

## Tarkistuksessa löytyneet konkreettiset ylläpitoriskit

1. **Hue:n yhteysturvallisuus:** `src/api/hue_contacts_v2.py` kutsuu Hue Bridgeä asetuksella `verify=False` ja vaimentaa TLS-varoitukset. Selvitä paikallisen varmenteen hallinta ennen muutoksia. Nykyistä toimivaa integraatiota ei saa rikkoa dokumentaatiotyön yhteydessä.
2. **Hue:n anturin kohdistus:** `src/viewmodels/hue_contacts.py` kohdistaa puuttuvan ovinimen tarvittaessa API:n palautusjärjestyksen perusteella seuraavaan vapaaseen anturiin. Jos laitteen nimeä ei tunnisteta, kortin ovinimi voi kohdistua väärään anturiin. Tämä on tarkistettava erillisillä testeillä.
3. **EQE:n ohjauskutsut:** `src/ui/card_eqe.py` sisältää säikeistettyjä, asynkronisesti vahvistettavia lukitus- ja esilämmitystoimintoja. Erota näkyvä ohjauksen tila todellisesta Home Assistantin kuittauksesta; älä oleta fyysisen toiminnon onnistumista pelkästä UI-vastauksesta.
4. **Päivitysskriptit:** `scripts/update.sh` tekee `git reset --hard` ja `git clean -fdx`; `scripts/DeployToPi.ps1` kutsuu `~/HomeDashboard/update.sh`-polkua, mutta Gitissä skripti on `scripts/update.sh`. Tämä on tarkistettava ennen julkaisua.
5. **Sekvenssidokumentaatio:** `docs/mermaid/sequence_electricity.md` ei ilmiselvästi kuvaa samaa nykyistä 15 minuutin toteutusta kuin `src/ui/card_prices.py`. Aseta lähdekoodi ja testit etusijalle, kunnes dokumentti päivitetään.

## Seuraava inventointikierros

- [ ] Käy läpi Kotidashboardin kaikkien keskustelujen täydellinen otsikkoluettelo ja mahdolliset liitteet.
- [ ] Vertaile `src/api/prices_15min_vm.py` ja sen testit aiemman sähkönhintapäätöksen fallback-vaatimuksiin.
- [ ] Tarkista EQE:n kirjoittavien ohjausfunktioiden suojaus, palautteet ja testit.
- [ ] Tarkista, mitkä keskustelut koskevat vain koneiden ja palveluiden ylläpitoa ja kuuluvat Computers & Linux -projektiin.
- [ ] Tarkista, että tärkeät päätökset löytyvät koodista, testeistä, dokumentaatiosta tai issueista.
- [ ] Älä arkistoi tai poista keskusteluja tämän osittaisen kartoituksen perusteella automaattisesti.
