#!/bin/bash
set -e

echo "[update.sh] mennään hakemistoon ~/HomeDashboard"
cd /home/admin/HomeDashboard

echo "[update.sh] haetaan uusin koodi"
git pull --rebase origin main

# jos sulla on venv ~/HomeDashboard/venv niin aktivoidaan se
if [ -f "venv/bin/activate" ]; then
    echo "[update.sh] aktivoidaan venv"
    source venv/bin/activate
    # päivitä tarvittaessa riippuvuudet
    if [ -f "requirements.txt" ]; then
        echo "[update.sh] päivitetään pip-paketit"
        pip install -r requirements.txt
    fi
fi

# käynnistä palvelu uudestaan, jos sulla on se käytössä
if command -v sudo >/dev/null 2>&1; then
    echo "[update.sh] käynnistetään kotidashboard-palvelu uudestaan"
    sudo systemctl restart kotidashboard
else
    echo "[update.sh] sudo ei käytettävissä, jätetään palvelu käynnistämättä"
fi

echo "[update.sh] valmis"
