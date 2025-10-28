#!/usr/bin/env bash
# Päivittää Kotidashboardin GitHubista ja käynnistää palvelun uudelleen

set -euo pipefail

echo "=== Päivitetään Kotidashboard ==="
cd /home/admin/HomeDashboard

# Varmuuskopioidaan paikalliset muutokset tarvittaessa
if [ -n "$(git status --porcelain)" ]; then
    echo "Paikallisia muutoksia havaittu, commitoidaan väliaikaisesti..."
    git add .
    git commit -m "Väliaikainen commit ennen päivitystä" || true
fi

# Vedetään uusin versio
echo "--- Haetaan uusin versio GitHubista ---"
git pull --rebase

# Päivitetään virtuaaliympäristö ja riippuvuudet (jos muutoksia)
if [ -f venv/bin/activate ]; then
    source venv/bin/activate
    echo "--- Päivitetään pip ja requirements ---"
    pip install -U pip >/dev/null
    if [ -f requirements.txt ]; then
        pip install -r requirements.txt >/dev/null
    fi
    deactivate
else
    echo "Varoitus: virtuaaliympäristöä ei löytynyt (venv/), ohitetaan pip-asennus."
fi

# Käynnistetään palvelu uudelleen
if systemctl list-units --type=service | grep -q kotidashboard.service; then
    echo "--- Käynnistetään kotidashboard-palvelu uudelleen ---"
    sudo systemctl restart kotidashboard
    sudo systemctl status kotidashboard --no-pager | head -n 10
else
    echo "--- Palvelua ei löytynyt systemd:stä, käynnistetään manuaalisesti ---"
    pkill -f "streamlit run main.py" 2>/dev/null || true
    nohup /home/admin/HomeDashboard/venv/bin/streamlit run /home/admin/HomeDashboard/main.py \
        --server.port=8787 --server.address=0.0.0.0 >/home/admin/HomeDashboard/streamlit.out 2>&1 &
    echo "Käynnistetty taustalle (lokit: streamlit.out)."
fi

echo "✅ Päivitys valmis."
