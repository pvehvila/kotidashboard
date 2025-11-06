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

## Asennus (Windows)

1. Asenna Python 3.10+ (tarkista että `py` toimii komentoriviltä).
2. Kloonaa repo:
   ```powershell
   git clone https://github.com/<oma-kayttaja>/kotidashboard.git
   cd kotidashboard
3. Luo virtuaaliympäristö:
   ```powershell
   py -m venv .venv
   .\.venv\Scripts\activate
5. Asenna riippuvuudet:
   ```powershell
   pip install --upgrade pip
   pip install -r requirements.txt
6. Käynnistä:
   ```powershell
   streamlit run main.py --server.address 0.0.0.0 --server.port 8787

Avaa selain ja mene osoitteeseen http://localhost:8787

 ---

## Asennus (Raspberry Pi 5)

1. Päivitä paketit:
   ```bash
   sudo apt update && sudo apt upgrade -y
   sudo apt install -y python3 python3-venv python3-pip git
2. Kloonaa repo:
   ```bash
   cd /home/admin
   git clone https://github.com/<oma-kayttaja>/kotidashboard.git
   cd kotidashboard
3. Luo virtuaaliympäristö:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
4. Asenna riippuvuudet:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
5. Kopioi asetukset:
   ```bash
   cp .env.example .env
   nano .env   # täytä arvot
6. Kokeile käynnistystä:
   ```bash 
   streamlit run main.py --server.address 0.0.0.0 --server.port 8787
7. (Valinnainen) systemd-palvelu:
   * kopioi repo mukana tuleva examples/kotidashboard.service → /etc/systemd/system/kotidashboard.service
   * ota käyttöön:
   ```bash 
    sudo systemctl daemon-reload
    sudo systemctl enable kotidashboard
    sudo systemctl start kotidashboard

---

## `requirements.txt` – esimerkkipohja

```text
streamlit>=1.37
requests>=2.32
pandas>=2.2
python-dotenv>=1.0
pytz>=2024.1
```
---
### Nopea testi

```bash
streamlit run main.py
```
Jos saat selaimeen dashboardin, asennus onnistui.

---

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
