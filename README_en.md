![Kotidashboard banner](docs/images/banner_kotidashboard.png)

# 🏠 Kotidashboard

> **Kotidashboard** is a Streamlit-based home dashboard that gathers essential daily information into one screen.
> It fetches real-time data such as weather, electricity prices, Bitcoin rates, namedays, and system status.
> Runs on both **Windows** and **Raspberry Pi 5**, updating directly from GitHub with a single command.

---

## ✨ Features

- ⚡ Electricity prices (Nord Pool / Finnish Pörssisähkö API)
- ☀️ Weather from Open-Meteo (temperature, precipitation, cloud cover, icon)
- ₿ Bitcoin price from CoinGecko
- 📅 Finnish namedays and holidays
- 🧘 Random Zen quote with background image
- 🖥️ System status (CPU, RAM, disk space)
- 💾 Logging to `logs/homedashboard.log`
- 🔄 Automatic refresh and caching

---

## 📸 Screenshot

![Screenshot](docs/images/Kotidashboard.png)

---

## ⚙️ Core Technologies

| Component | Technology |
|:-----------|:-----------|
| Frontend | [Streamlit](https://streamlit.io) |
| Data sources | Open-Meteo, Pörssisähkö API, CoinGecko, Yle API |
| Language / Env | Python 3.13 + venv |
| Server | Raspberry Pi 5 (8 GB) |
| Visualization | Plotly, Mermaid |
| Version control | Git / GitHub |

---

## 📁 Folder Structure

```text
HomeDashboard/
├── 📦 src/          # Application code (api.py, ui.py, utils.py, config.py, ...)
├── 🎨 assets/       # Styles, icons and background images
├── 📊 data/         # JSON and XLSX data
├── 📚 docs/         # Documentation and diagrams
├── 🧰 scripts/      # Installation and update scripts
├── 🧪 tests/        # Unit tests
├── 🪵 logs/         # Log files
├── 🧩 .venv/        # Virtual environment
├── 🚀 main.py       # Streamlit entrypoint
└── 📘 README.md
```

## 📊 Local data

The dashboard expects some JSON data in the project root under `data/`:

- `data/nimipaivat_fi.json` – Finnish namedays, month-based structure (e.g. "marraskuu" → "11" → "Panu").
- `data/pyhat_fi.json` – Finnish holidays and flag days. The nameday card uses this to render the badge only on those days.

If these files are missing, the nameday card will fall back to showing just the date header.

---

## 🪟 Installation (Windows)

1. Install Python 3.10+ and make sure `py` works in PowerShell.
2. Clone the repository:
   ```powershell
   git clone https://github.com/<your-username>/kotidashboard.git
   cd kotidashboard
   ```
3. Create virtual environment:
   ```powershell
   py -m venv .venv
   .\.venv\Scripts\activate
   ```
4. Install dependencies:
   ```powershell
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
5. Copy environment example and edit:
   ```powershell
   copy .env.example .env
   # Fill in your location, API keys, etc.
   ```
6. Run the dashboard:
   ```powershell
   streamlit run main.py --server.address 0.0.0.0 --server.port 8787
   ```
7. Open browser at **http://localhost:8787**

---

## 🍓 Installation (Raspberry Pi 5)

1. Update packages:
   ```bash
   sudo apt update && sudo apt upgrade -y
   sudo apt install -y python3 python3-venv python3-pip git
   ```
2. Clone the repo:
   ```bash
   cd /home/admin
   git clone https://github.com/<your-username>/kotidashboard.git
   cd kotidashboard
   ```
3. Create virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
4. Install dependencies:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
5. Copy environment file:
   ```bash
   cp .env.example .env
   nano .env   # fill in your values
   ```
6. Test the dashboard:
   ```bash
   streamlit run main.py --server.address 0.0.0.0 --server.port 8787
   ```
7. (Optional) Run as systemd service:
   ```bash
   sudo cp examples/kotidashboard.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable kotidashboard
   sudo systemctl start kotidashboard
   ```

---

## 🧾 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 🙌 Credits

Data sources:
- [porssisahko.net](https://api.porssisahko.net)
- [sahkonhintatanaan.fi](https://www.sahkonhintatanaan.fi)
- [Open-Meteo](https://open-meteo.com/)
- [CoinGecko](https://www.coingecko.com/)
- [Finnish Namedays API](https://fi.fi/)

Developed by **Pekko Vehviläinen**, 2025
