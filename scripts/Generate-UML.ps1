param(
    [string]$Name = "HomeDashboard"
)

# 1) Projektin juuri skriptin sijainnista
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjRoot  = Resolve-Path (Join-Path $ScriptDir "..")
Set-Location $ProjRoot

# 2) UML-ulostulokansio
$OutDir = Join-Path $ProjRoot "docs\uml"
if (-not (Test-Path $OutDir)) {
    New-Item -ItemType Directory -Path $OutDir | Out-Null
}

# 3) pyreverse polku
$pyreverse = $null
$venvPyreverse = Join-Path $ProjRoot ".venv\Scripts\pyreverse.exe"
if (Test-Path $venvPyreverse) {
    $pyreverse = $venvPyreverse
} else {
    $pyreverse = "pyreverse"
}

# 4) Analysoitavat kansiot → vain arkkitehtuuritaso
$Targets = @(
    "src/api",
    "src/ui",
    "src/utils.py",       # jos utils on vielä yhtenä tiedostona
    "src/utils_colors.py",
    "src/utils_sun.py",
    "src/utils_net.py"
)

Write-Host "Projektin juuri: $ProjRoot"
Write-Host "Käytettävä pyreverse: $pyreverse"
Write-Host "Analysoidaan: $($Targets -join ', ')"
Write-Host ""

try {
    # 5) Aja pyreverse niille
    & $pyreverse -o dot -p $Name $Targets
} catch {
    Write-Error "pyreverse ei löytynyt. Asenna: .\.venv\Scripts\python.exe -m pip install pylint"
    exit 1
}

# 6) Siirrä .dot -tiedostot
$classesDot  = "classes_$Name.dot"
$packagesDot = "packages_$Name.dot"

if (Test-Path $classesDot) {
    Move-Item $classesDot $OutDir -Force
}
if (Test-Path $packagesDot) {
    Move-Item $packagesDot $OutDir -Force
}

# 7) Muunna png:ksi (Graphviz)
$dotCmd = "dot"
$classesPng  = Join-Path $OutDir "classes_$Name.png"
$packagesPng = Join-Path $OutDir "packages_$Name.png"

if (Test-Path (Join-Path $OutDir "classes_$Name.dot")) {
    & $dotCmd -Tpng (Join-Path $OutDir "classes_$Name.dot") -o $classesPng
}
if (Test-Path (Join-Path $OutDir "packages_$Name.dot")) {
    & $dotCmd -Tpng (Join-Path $OutDir "packages_$Name.dot") -o $packagesPng
}

Write-Host "Valmis → $packagesPng, $classesPng"
