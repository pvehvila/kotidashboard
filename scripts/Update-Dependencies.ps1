# --- Update-Dependencies.ps1 ---

Write-Host "Updating pip..."
python -m pip install --upgrade pip

# Selvitetään projektin juurikansio (yksi taso ylöspäin tästä skriptistä)
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$Requirements = Join-Path $ProjectRoot "requirements.txt"

Write-Host "Installing/updating dependencies..."

if (Test-Path $Requirements) {
    python -m pip install -r $Requirements
} else {
    Write-Host "ERROR: requirements.txt not found at $Requirements" -ForegroundColor Red
}

# Kehitystyökalut
Write-Host "Installing development tools..."
python -m pip install ruff pytest pytest-cov

Write-Host "Dependencies updated successfully!" -ForegroundColor Green
