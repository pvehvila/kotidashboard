param(
  [string]$Proj = "C:\Users\pekkoveh\Dev\kotidashboard",
  [string]$Name = "Kotidashboard",
  [string[]]$Files = @(".\ui.py",".\api.py",".\utils.py",".\config.py",".\main.py")
)

$pyreverse = "C:\Python3115\Scripts\pyreverse.exe"
$dot       = "C:\Program Files\Graphviz\bin\dot.exe"

Set-Location $Proj
$env:PYTHONPATH = "$PWD;$env:PYTHONPATH"

& $pyreverse -o dot -p $Name $Files
& $dot -Tpng "packages_$Name.dot" -o "packages_$Name.png"
& $dot -Tpng "classes_$Name.dot"  -o "classes_$Name.png"

Write-Host "Valmis → packages_$Name.png, classes_$Name.png" -ForegroundColor Green
