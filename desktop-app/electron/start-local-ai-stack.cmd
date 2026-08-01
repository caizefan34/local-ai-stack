@echo off
rem Local AI Stack desktop launcher (Electron).
rem Falls back to installing the Electron runtime on first run.
setlocal
cd /d "%~dp0"

if not exist "node_modules\electron\dist\electron.exe" (
  where npm >nul 2>nul
  if errorlevel 1 (
    echo [Local AI Stack] Node.js/npm not found. Install Node.js from https://nodejs.org first.
    pause
    exit /b 1
  )
  echo [Local AI Stack] First run: installing Electron runtime, about 100 MB, please wait...
  call npm install --no-audit --no-fund
  if errorlevel 1 (
    echo [Local AI Stack] npm install failed. Check network and retry.
    pause
    exit /b 1
  )
)

start "" "%~dp0node_modules\electron\dist\electron.exe" .
exit /b 0
