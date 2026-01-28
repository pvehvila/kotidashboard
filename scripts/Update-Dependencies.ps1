# --- Update-Dependencies.ps1 ---

$ErrorActionPreference = "Stop"

Write-Host "Ensuring virtual environment..."
$ProjectRoot  = Split-Path -Parent $PSScriptRoot
$VenvDir      = Join-Path $ProjectRoot ".venv"
$VenvPython   = Join-Path $VenvDir "Scripts\python.exe"

if (!(Test-Path $VenvPython)) {
    Write-Host "Creating .venv..."
    python -m venv $VenvDir
    if ($LASTEXITCODE -ne 0) { throw "venv creation failed (exit $LASTEXITCODE)" }
}

Write-Host "Updating pip..."
& $VenvPython -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw "pip upgrade failed (exit $LASTEXITCODE)" }

$Requirements = Join-Path $ProjectRoot "requirements.txt"

Write-Host "Installing/updating dependencies..."
if (!(Test-Path $Requirements)) {
    throw "requirements.txt not found at $Requirements"
}

& $VenvPython -m pip install -r $Requirements
if ($LASTEXITCODE -ne 0) { throw "pip install -r requirements.txt failed (exit $LASTEXITCODE)" }

Write-Host "Installing development tools..."
& $VenvPython -m pip install ruff pytest pytest-cov bandit
if ($LASTEXITCODE -ne 0) { throw "pip install dev tools failed (exit $LASTEXITCODE)" }

Write-Host "Dependencies updated successfully!" -ForegroundColor Green
