"""
check_imports.py – tarkistaa, että kaikki tuonnit käyttävät src.-etuliitettä
Käyttö:
    python check_imports.py
"""

from __future__ import annotations
import os
import re
from pathlib import Path

# Hakemistot, joita ei tarkisteta
EXCLUDE_DIRS = {"venv", ".venv", "__pycache__", ".github", "tests"}

# Regex pattern: from api / from ui / import utils ...
PATTERN = re.compile(r"^\s*(from|import)\s+(api|ui|utils|config|logger_config|weather_icons)\b")

BASE_DIR = Path(__file__).resolve().parent
violations: list[tuple[str, int, str]] = []

for py_file in BASE_DIR.rglob("*.py"):
    if any(part in EXCLUDE_DIRS for part in py_file.parts):
        continue
    with open(py_file, "r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, start=1):
            if PATTERN.search(line):
                violations.append((str(py_file.relative_to(BASE_DIR)), lineno, line.strip()))

if not violations:
    print("✅ Kaikki tuonnit näyttävät käyttävän src.-etuliitettä.")
else:
    print("⚠️  Seuraavat rivit näyttävät viittaavan vanhaan tuontiin:\n")
    for file, lineno, line in violations:
        print(f"{file}:{lineno}: {line}")
    print("\nKorjaa muodosta esim. 'from api' → 'from src.api'")
