#!/usr/bin/env bash
# Kotidashboard – turvallinen deploy Raspberry Pi:lle (ei paikallisia committeja)
set -euo pipefail

# --- SÄÄDETTÄVÄT ---
REPO_DIR="/home/admin/HomeDashboard"
BRANCH="main"                   # tai "release"
SERVICE_NAME="kotidashboard"    # systemd-yksikön nimi
PORT="8787"
REQ_LINUX="$REPO_DIR/requirements-linux.txt"
# --------------------

PYTHON_BIN="$REPO_DIR/venv/bin/python3"

say() { printf "\033[1m%s\033[0m\n" "$*"; }

say "=== Kotidashboard: deploy origin/$BRANCH -> Pi ==="
cd "$REPO_DIR"

# 1) Puhdas työpuu: aina täsmälleen origin/$BRANCH
git fetch --prune
git checkout "$BRANCH"
git reset --hard "origin/$BRANCH"
# Puhdista generoidut roskat, mutta säästä loki
git clean -fdx -e streamlit.out

# 2) Venv vain tälle koneelle
if [ ! -x "$PYTHON_BIN" ]; then
  say "--- Luodaan venv ---"
  python3 -m venv "$REPO_DIR/venv"
fi

# 3) Riippuvuudet
set +u; source "$REPO_DIR/venv/bin/activate"; set -u
python -m pip install -U pip wheel setuptools >/dev/null

say "--- Asennetaan riippuvuudet ---"
if [ -f "$REQ_LINUX" ]; then
  python -m pip install -r "$REQ_LINUX" >/dev/null
elif [ -f "$REPO_DIR/requirements.txt" ]; then
  echo "Varoitus: requirements-linux.txt puuttuu, käytetään requirements.txt"
  python -m pip install -r "$REPO_DIR/requirements.txt" >/dev/null
else
  echo "Huom: riippuvuuslistaa ei löytynyt (requirements-*.txt)."
fi
deactivate

# 4) Käynnistys: yritä ensin systemd (root), sitten systemd --user, muuten manuaali
say "--- Käynnistys ---"
if sudo systemctl status "$SERVICE_NAME" >/dev/null 2>&1; then
  say "-> systemd (root) mode"
  sudo systemctl stop "$SERVICE_NAME" || true
  sudo systemctl start "$SERVICE_NAME"
  sudo systemctl status "$SERVICE_NAME" --no-pager | head -n 12 || true
elif systemctl --user status "$SERVICE_NAME" >/dev/null 2>&1; then
  say "-> systemd --user mode"
  systemctl --user stop "$SERVICE_NAME" || true
  systemctl --user start "$SERVICE_NAME"
  systemctl --user status "$SERVICE_NAME" --no-pager | head -n 12 || true
else
  say "-> manuaalikäynnistys"
  pkill -f "streamlit run .*main.py" 2>/dev/null || true
  nohup "$REPO_DIR/venv/bin/streamlit" run "$REPO_DIR/main.py" \
    --server.address=0.0.0.0 --server.port="$PORT" \
    > "$REPO_DIR/streamlit.out" 2>&1 &
  echo "Käynnistetty taustalle. Lokit: $REPO_DIR/streamlit.out"
fi

# 5) Health-check
sleep 2
if command -v curl >/dev/null 2>&1; then
  if curl -sf "http://127.0.0.1:${PORT}/_stcore/health" >/dev/null; then
    echo "✅ Health OK"
  else
    echo "⚠️ Health-check epäonnistui (katso streamlit.out)."
  fi
fi

echo "✅ Deploy valmis."
