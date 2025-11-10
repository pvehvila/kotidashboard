param(
    [string]$SourcePath = "src"
)

Write-Host "Analysoidaan hakemistoa: $SourcePath" -ForegroundColor Cyan

# 1) Luodaan väliaikainen python-tiedosto rivimäärien laskemiseen
$pyCode = @"
import os
import sys
from pathlib import Path

source = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("src")

files = []
for root, dirs, filenames in os.walk(source):
    for name in filenames:
        if name.endswith(".py"):
            p = Path(root) / name
            try:
                with p.open("r", encoding="utf-8") as f:
                    lines = sum(1 for _ in f)
            except UnicodeDecodeError:
                with p.open("r", encoding="latin-1") as f:
                    lines = sum(1 for _ in f)
            files.append((str(p.relative_to(source)), lines))

files.sort(key=lambda x: x[1], reverse=True)

print(f"{'Tiedosto':60} {'Rivit':>6}")
print("-" * 70)
for fname, loc in files:
    print(f"{fname:60} {loc:6d}")

total = sum(loc for _, loc in files)
print("-" * 70)
print(f"{'Yhteensä':60} {total:6d}")
"@

$tempPy = New-TemporaryFile
Set-Content -Path $tempPy -Value $pyCode -Encoding UTF8

Write-Host "`n=== Rivimäärät (Pythonilla) ===" -ForegroundColor Yellow
python $tempPy $SourcePath

# 2) RADON: raw
Write-Host "`n=== RADON: raw (LOC jne.) ===" -ForegroundColor Yellow
try {
    python -m radon raw $SourcePath
}
catch {
    Write-Host "radon ei ole asennettuna. Asenna: pip install radon" -ForegroundColor Red
}

# 3) RADON: cc
Write-Host "`n=== RADON: cc (funktiot ja monimutkaisuus) ===" -ForegroundColor Yellow
try {
    python -m radon cc $SourcePath -s
}
catch {
    Write-Host "radon ei ole asennettuna. Asenna: pip install radon" -ForegroundColor Red
}

# 4) siivotaan tilapäistiedosto
Remove-Item $tempPy -ErrorAction SilentlyContinue

Write-Host "`nValmis." -ForegroundColor Green
