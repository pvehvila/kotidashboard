# 🏠 Kotidashboard

> **Kotidashboard** on Streamlit-pohjainen kojelauta, joka kokoaa keskeiset arjen tiedot yhdelle näytölle.
> Se hakee reaaliaikaista dataa säästä, sähkön hinnasta, Bitcoinista, nimipäivistä, järjestelmän tilasta sekä älykotilaitteista.
> Sovellus toimii sekä **Windowsissa** että **Raspberry Pi 5**:llä ja päivittyy suoraan GitHubista yhdellä komennolla.

![Kotidashboard banneri](docs/images/banner_kotidashboard.png)

---

## ✨ Ominaisuudet

- ⚡ **Sähkön hinta** (Nord Pool / Pörssisähkö API, 60 min ja 15 min resoluutio)
- ☀️ **Sää Open-Meteosta** (lämpötila, tuuli, sade, pilvisyys, WMO-ikonit)
- ₿ **Bitcoinin kurssi** (CoinGecko, 24h/7d/30d)
- 📅 **Nimipäivät ja suomalaiset pyhäpäivät**
- 🧘 **Satunnainen mietelause** taustakuvalla
- 🎧 **HEOS / Tidal** – nykyinen kappale, ohjauspainikkeet, virheenkäsittely
- 🚪 **Hue Secure -ovi- ja liiketunnistimet** (v2 API)
- 🖥️ **Järjestelmän tila** (CPU, RAM, levytila, IP)
- 💾 **Lokitus** `logs/homedashboard.log` -tiedostoon
- 🔄 **Automaattinen päivitys ja välimuisti** (Streamlit cache)

---

## 📸 Kuvakaappaus

![Kuvakaappaus](docs/images/Kotidashboard.jpg)

---

## ⚙️ Teknologiat

| Osa-alue | Teknologia |
|---------|------------|
| Frontend | Streamlit |
| Data | Open-Meteo, Pörssisähkö API, CoinGecko, Yle API |
| Kieli | Python 3.13 |
| Laitteisto | Raspberry Pi 5 (8 GB), Windows |
| Visualisointi | Plotly, Mermaid |
| Laadunvalvonta | Ruff, Pytest, Coverage, Bandit, pre-commit |
| Versionhallinta | Git / GitHub |

---

## 📁 Hakemistorakenne

```text
HomeDashboard/
├── 📦 src/          # Sovelluskoodi (api/, ui/, viewmodels/, utils/...)
├── 🎨 assets/       # Tyylit, ikonit ja taustat
├── 📊 data/         # JSON- ja XLSX-data
├── 🧪 tests/        # Yksikkötestit
├── 📚 docs/         # Dokumentaatio
├── 🧰 scripts/      # Asennus- ja päivitysskriptit
├── 🪵 logs/         # Lokitiedostot
├── 🧩 .venv/        # Virtuaaliympäristö
└── 🚀 main.py       # Streamlit-sovelluksen entrypoint
```

---

## 📊 Paikallinen data

Dashboard käyttää seuraavia tiedostoja:

- `data/nimipaivat_fi.json` — nimipäivälista
- `data/pyhat_fi.json` — suomalaiset pyhä- ja liputuspäivät

Jos nämä puuttuvat, nimipäiväkortti näyttää vain päivämäärän.

---

## 🪟 Asennus (Windows)

```powershell
git clone https://github.com/<oma-kayttaja>/kotidashboard.git
cd kotidashboard

# Suositeltu tapa: käyttää projektin päivitysskriptiä (luo .venv automaattisesti)
.\scripts\Update-Dependencies.ps1

```

Vaihtoehtoisesti manuaalisesti:

```powershell
py -m venv .venv
.\.venv\Scripts\activate

pip install --upgrade pip
pip install -r requirements.txt

copy .env.example .env
# Muokkaa asetuksia

streamlit run main.py --server.address 0.0.0.0 --server.port 8787
```
Avaa selaimella: **http://localhost:8787**

---

## 🍓 Asennus (Raspberry Pi 5)

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-venv python3-pip git

git clone https://github.com/<oma-kayttaja>/kotidashboard.git
cd kotidashboard

python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

cp .env.example .env
nano .env

streamlit run main.py --server.address 0.0.0.0 --server.port 8787
```

### Systemd-palveluna

```bash
sudo cp examples/kotidashboard.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable kotidashboard
sudo systemctl start kotidashboard
```

---

## 🔧 Laadunvarmistus (CI / Development)

Dashboardissa käytetään:

- **Ruff** — linttaus ja automaattiformatointi
- **Pytest + Coverage** — yksikkötestit (kattavuus ~85 %)
- **Bandit** — tietoturvatarkistukset
- **pre-commit** — kaikkien tarkistusten automaattinen ajo

Asetukset löytyvät tiedostosta **QUALITY.md**.

---

## 🧾 Lisenssi

Sovellus on lisensoitu **MIT-lisenssillä** — katso `LICENSE`.

---

## 🙌 Kiitokset

Datalähteet:
- porssisahko.net
- sahkonhintatanaan.fi
- Open-Meteo
- CoinGecko
- Finnish Namedays API

Kehittäjä: **Pekko Vehviläinen**, 2025
