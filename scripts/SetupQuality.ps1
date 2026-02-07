<#
.SYNOPSIS
Asentaa ja ottaa käyttöön Python-laadunvarmistustyökalut:
- ruff
- pytest + pytest-cov
- bandit
- pre-commit

Käyttö:
PS C:\HomeDashboard> .\scripts\SetupQuality.ps1
#>

param(
    [string]$PythonExe = "python",
    [switch]$UseVenv
)

Write-Host "[SetupQuality] Aloitetaan laadunvarmistustyökalujen asennus..." -ForegroundColor Cyan

# 1) Siirrytään skriptin sijaintiin ja projektin juureen
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir
Set-Location ..

Write-Host "[SetupQuality] Projektin juuri: $(Get-Location)" -ForegroundColor DarkCyan

# 2) Jos halutaan käyttää venviä, aktivoidaan / luodaan se
if ($UseVenv) {
    if (-not (Test-Path ".\.venv")) {
        Write-Host "[SetupQuality] .venv puuttuu, luodaan..." -ForegroundColor Yellow
        & $PythonExe -m venv .venv
    }
    Write-Host "[SetupQuality] Aktivoidaan .venv..." -ForegroundColor Yellow
    # Tämä toimii PowerShellissä
    . .\.venv\Scripts\Activate.ps1
}

# 3) Päivitetään pip
Write-Host "[SetupQuality] Päivitetään pip..." -ForegroundColor DarkCyan
& $PythonExe -m pip install --upgrade pip

# 4) Asennetaan peruslaadunvalvonta
Write-Host "[SetupQuality] Asennetaan ruff, pytest, pytest-cov, bandit, pre-commit..." -ForegroundColor DarkCyan
& $PythonExe -m pip install ruff pytest pytest-cov bandit pre-commit

# 5) pre-commit-konfiguraatio tarkistus
$preCommitFile = ".pre-commit-config.yaml"
if (-not (Test-Path $preCommitFile)) {
    Write-Host "[SetupQuality] .pre-commit-config.yaml puuttuu. Luo ensin tiedosto projektin juureen." -ForegroundColor Yellow
    Write-Host "Voit käyttää esimerkiksi tätä pohjaa:"
    Write-Host @"
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.7.0
    hooks:
      - id: ruff
      - id: ruff-format

  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: ["-r", "src"]

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: end-of-file-fixer
      - id: trailing-whitespace
      - id: check-yaml
      - id: check-toml
"@
} else {
    # 6) Asennetaan hookit
    Write-Host "[SetupQuality] Asennetaan pre-commit hookit..." -ForegroundColor DarkCyan
    pre-commit install
    Write-Host "[SetupQuality] Ajetaan hookit koko repoille..." -ForegroundColor DarkCyan
    pre-commit run --all-files
}

Write-Host "[SetupQuality] Valmis." -ForegroundColor Green
