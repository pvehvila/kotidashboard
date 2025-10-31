@echo off
REM =====================================================
REM  Kotidashboard – Git Sync Script
REM  Tekee automaattisesti git pull + git add + commit + push
REM =====================================================

setlocal
set "REPO_DIR=%~dp0"
cd /d "%REPO_DIR%"

echo.
echo === Haetaan uusin versio GitHubista ===
git pull

echo.
echo === Lisätään paikalliset muutokset ===
git add -A

echo.
set /p MSG="Anna commit-viesti (ENTER = 'päivitys'): "
if "%MSG%"=="" set MSG=päivitys

echo.
echo === Tehdään commit: %MSG% ===
git commit -m "%MSG%"

echo.
echo === Työnnetään GitHubiin ===
git push

echo.
echo ✅  Synkronointi valmis.
timeout /t 3 >nul
endlocal
