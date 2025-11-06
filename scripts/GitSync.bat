@echo off
setlocal enabledelayedexpansion
REM Kotidashboard – turvallinen push Windowsilta

REM Aja repo-juuresta
cd /d "%~dp0"

REM 1) Varmista että olet feature-branchissa tai mainissa
for /f "delims=" %%b in ('git rev-parse --abbrev-ref HEAD') do set BRANCH=%%b

echo Current branch: %BRANCH%
echo.

REM 2) Hae uusin ja rebasea paikallinen historia origin/mainin paalle
git fetch --prune
git rebase origin/main || goto :rebased

:rebased
if errorlevel 1 (
  echo Rebase epäonnistui. Korjaa konfliktit ja aja skripti uudestaan.
  exit /b 1
)

REM 3) Näytä tilanne ja pyydä viesti (tai käytä oletusta)
git status -s
echo.
set /p MSG="Commit-viesti (enter=paivitys): "
if "%MSG%"=="" set "MSG=paivitys"

REM 4) Lisää vain tarkoitukselliset muutokset
git add -A

REM 5) Commitoi jos on muutoksia
git diff --cached --quiet
if %errorlevel%==0 (
  echo Ei muutoksia. Ohitetaan commit.
) else (
  git commit -m "%MSG%"
)

REM 6) Pushaa aina fast-forward / rebase-politiikalla
git push --set-upstream origin %BRANCH%

echo.
echo ✅ Valmis.
timeout /t 2 >nul
endlocal
