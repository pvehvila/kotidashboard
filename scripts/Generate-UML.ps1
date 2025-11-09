param(
    # Projektin nimi, näkyy UML-kuvien nimessä
    [string]$Name = "HomeDashboard"
)

# 1) Mene projektin juureen (skriptin yläkansio)
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjRoot  = Resolve-Path (Join-Path $ScriptDir "..")
Set-Location $ProjRoot

# 2) Missä UML-kuvat säilytetään
$OutDir = Join-Path $ProjRoot "docs\uml"
if (-not (Test-Path $OutDir)) {
    New-Item -ItemType Directory -Path $OutDir | Out-Null
}

# 3) Etsi pyreverse
$pyreverse = $null
$venvPyreverse = Join-Path $ProjRoot ".venv\Scripts\pyreverse.exe"
if (Test-Path $venvPyreverse) {
    $pyreverse = $venvPyreverse
} else {
    # luotetaan PATH:iin
    $pyreverse = "pyreverse"
}

# 4) Mitkä hakemistot analysoidaan
# useimmiten riittää src, ei haluta __pycache__ eikä tests
$Target = "src"

Write-Host "Projektin juuri: $ProjRoot"
Write-Host "UML kohdekansio: $OutDir"
Write-Host "Käytettävä pyreverse: $pyreverse"
Write-Host "Analysoitava hakemisto: $Target"
Write-Host ""

# 5) Aja pyreverse → tuottaa .dot -tiedostot
# -o dot  = graphviz
# -p name = projektin nimi
try {
    & $pyreverse -o dot -p $Name $Target
} catch {
    Write-Error "pyreverse ei löytynyt. Asenna se esim.: 'python -m pip install pylint'"
    exit 1
}

# 6) Siirrä syntyneet .dot -tiedostot docs/uml -kansioon ja tee niistä png:t
# pyreverse luo yleensä: classes_$Name.dot ja packages_$Name.dot
$classesDot  = "classes_$Name.dot"
$packagesDot = "packages_$Name.dot"

if (Test-Path $classesDot) {
    Move-Item $classesDot $OutDir -Force
}
if (Test-Path $packagesDot) {
    Move-Item $packagesDot $OutDir -Force
}

# 7) Muunna .dot → .png (vaatii Graphvizin: 'dot' komentona)
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
