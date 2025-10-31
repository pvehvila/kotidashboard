---

## 🧭 Koodin päivittäminen (Raspberry Pi 5)

> Näillä ohjeilla voit päivittää Kotidashboardin uusimman version Raspberry Pi:lle.

1. Kirjaudu SSH:lla Raspberryyn:  
   ```bash
   ssh admin@RaspberryPi5

2. Syötä salasana:
 "admin@raspberrypi5's password: xxxxxxxxx"

3. Hae tuorein versio GitHub:ista ja käynnistä palveu uudelleen:
 "update-dash"


| Osa-alue                                                  | Kuvaus                                                        |
| :-------------------------------------------------------- | :------------------------------------------------------------ |
| [Arkkitehtuuri](docs/mermaid/architecture.md)             | Kokonaisarkkitehtuurin rakenne ja komponenttien vuorovaikutus |
| [Sääkortti](docs/mermaid/sequence_weather.md)             | Säädatan haku ja esittäminen dashboardilla                    |
| [Sähkön hinta](docs/mermaid/sequence_electricity.md)      | Pörssisähkön hintatietojen nouto ja visualisointi             |
| [Bitcoin](docs/mermaid/sequence_bitcoin.md)               | Bitcoinin hinnan haku CoinGeckosta ja sen päivityslogiikka    |
| [System-kortti](docs/mermaid/sequence_system.md)          | Järjestelmän tilakortin tiedonkeruu ja renderöinti            |
| [Cache-tila](docs/mermaid/state_cache.md)                 | Tietovälimuistin (cache) tila ja elinkaari                    |
| [Deployment (Raspberry Pi 5)](docs/mermaid/deployment.md) | Sovelluksen päivitys- ja käynnistysprosessi Pi:llä            |
