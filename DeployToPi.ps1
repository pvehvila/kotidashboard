param(
    [string]$RepoPath = "C:\HomeDashboard",
    [string]$PiHost = "raspberrypi5.local", # tai Pi:n IP esim. 192.168.1.45
    [string]$User = "admin",
    [int]$Port = 22,
    [string]$Branch = "main",
    [switch]$SkipGit,
    [switch]$UseGitSyncBat
)

$ErrorActionPreference = "Stop"
$stopwatch = [System.Diagnostics.Stopwatch]::StartNew()

function Say($msg)  { Write-Host ("[{0}] {1}" -f (Get-Date).ToString("HH:mm:ss"), $msg) -ForegroundColor Cyan }
function Warn($msg) { Write-Host ("[{0}] {1}" -f (Get-Date).ToString("HH:mm:ss"), $msg) -ForegroundColor Yellow }
function Fail($msg) { Write-Host ("[{0}] {1}" -f (Get-Date).ToString("HH:mm:ss"), $msg) -ForegroundColor Red; exit 1 }

if (-not (Get-Command git -ErrorAction SilentlyContinue)) { Fail "git ei loydy PATH:ista." }
if (-not (Get-Command ssh -ErrorAction SilentlyContinue)) { Fail "ssh ei loydy PATH:ista." }

if (-not (Test-Path $RepoPath)) { Fail "RepoPath ei loydy: $RepoPath" }
Set-Location $RepoPath

# 1) Git-push Windowsista
if (-not $SkipGit) {
    Say "Git: varmistetaan, etta haara '$Branch' on ajantasalla"

    if ($UseGitSyncBat -and (Test-Path "$RepoPath\GitSync.bat")) {
        Say "Ajetaan GitSync.bat (rebase-tyylinen push)..."
        & "$RepoPath\GitSync.bat"
    } else {
        $currentBranch = (git rev-parse --abbrev-ref HEAD).Trim()
        if ($currentBranch -ne $Branch) {
            Warn "Olet haarassa '$currentBranch'. Jatketaan silti tassa haarassa."
        }

        git fetch --prune
        try { git rebase ("origin/{0}" -f $Branch) } catch { Fail "Rebase epaonnistui. Korjaa konfliktit ja aja skripti uudelleen." }

        git add -A
        git diff --cached --quiet
        if ($LASTEXITCODE -ne 0) {
            $msg = "Deploy: paivitys " + (Get-Date -Format "yyyy-MM-dd HH:mm")
            git commit -m $msg | Out-Null
            Say ("Commit tehty: {0}" -f $msg)
        } else {
            Say "Ei committoitavaa."
        }

        git push --set-upstream origin $currentBranch
    }
} else {
    Warn "Ohitetaan Git-push (SkipGit kaytossa)."
}

# 2) Aja update.sh Pi:lla
Say ("SSH: ajetaan ~/HomeDashboard/update.sh Pi:lla ({0}@{1}:{2})..." -f $User, $PiHost, $Port)
$sshCmd = @(
    "ssh",
    "-o","StrictHostKeyChecking=accept-new",
    "-p", $Port,
    ("{0}@{1}" -f $User, $PiHost),
    "bash -lc '~/HomeDashboard/update.sh'"
)
Write-Host ("`n> " + ($sshCmd -join ' ')) -ForegroundColor DarkGray

$proc = Start-Process -FilePath $sshCmd[0] -ArgumentList $sshCmd[1..($sshCmd.Count-1)] -NoNewWindow -PassThru -Wait
if ($proc.ExitCode -ne 0) { Fail ("update.sh palautti virheen ({0})." -f $proc.ExitCode) }

# 3) Health-check
try {
    $healthUrl = ("http://{0}:8787/_stcore/health" -f $PiHost)
    Say ("Health-check: {0}" -f $healthUrl)
    $resp = Invoke-WebRequest -Uri $healthUrl -UseBasicParsing -TimeoutSec 5
    if ($resp.StatusCode -eq 200) {
        Write-Host "OK: Health 200" -ForegroundColor Green
    } else {
        Warn ("Health vastasi koodilla {0}. Avaa selaimessa: http://{1}:8787" -f $resp.StatusCode, $PiHost)
    }
} catch {
    Warn ("Health ei vastannut. Avaa selaimessa: http://{0}:8787" -f $PiHost)
}

$stopwatch.Stop()
Say ("Valmis. Kesto: {0:n1} s" -f $stopwatch.Elapsed.TotalSeconds)
