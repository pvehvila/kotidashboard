![Kotidashboard banneri](docs/images/banner_kotidashboard.png)

# 🏠 Kotidashboard

> **Kotidashboard** on Streamlit-pohjainen kojelauta, joka näyttää keskeiset arjen tiedot yhdellä näytöllä.  
> Sovellus kerää reaaliaikaisia tietoja muun muassa säästä, sähkön hinnasta, Bitcoin-kurssista, nimipäivistä ja järjestelmän tilasta.  
> Toteutus toimii Raspberry Pi 5:llä ja päivittyy suoraan GitHubista yhdellä komennolla.

---

## ⚙️ Keskeiset teknologiat

| Osa | Teknologia |
|:----|:------------|
| Käyttöliittymä | [Streamlit](https://streamlit.io) |
| Datalähteet | Open-Meteo, Nord Pool, CoinGecko, Yle API |
| Kieli / ympäristö | Python 3.13, venv |
| Palvelin | Raspberry Pi 5 (8 GB) |
| Visualisointi | Plotly, Mermaid-kaaviot |
| Versionhallinta | Git / GitHub |

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

📘 README.md-linkit

Tämä osio kokoaa kaikki Kotidashboardin tekniset kaaviot ja dokumentaatiolinkit.
Jokainen linkki avaa vastaavan Mermaid-kaavion tiedoston docs/mermaid/-hakemistossa.

🧩 Lisäkaaviot

| Osa-alue                                                  | Kuvaus                                                        |
| :-------------------------------------------------------- | :------------------------------------------------------------ |
| [Arkkitehtuuri](docs/mermaid/architecture.md)             | Kokonaisarkkitehtuurin rakenne ja komponenttien vuorovaikutus |
| [Sääkortti](docs/mermaid/sequence_weather.md)             | Säädatan haku ja esittäminen dashboardilla                    |
| [Sähkön hinta](docs/mermaid/sequence_electricity.md)      | Pörssisähkön hintatietojen nouto ja visualisointi             |
| [Bitcoin](docs/mermaid/sequence_bitcoin.md)               | Bitcoinin hinnan haku CoinGeckosta ja sen päivityslogiikka    |
| [System-kortti](docs/mermaid/sequence_system.md)          | Järjestelmän tilakortin tiedonkeruu ja renderöinti            |
| [Cache-tila](docs/mermaid/state_cache.md)                 | Tietovälimuistin (cache) tila ja elinkaari                    |
| [Deployment (Raspberry Pi 5)](docs/mermaid/deployment.md) | Sovelluksen päivitys- ja käynnistysprosessi Pi:llä            |
