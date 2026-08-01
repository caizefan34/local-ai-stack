@echo off
rem Local AI Stack desktop launcher (Electron).
rem Falls back to installing the Electron runtime on first run.
setlocal
cd /d "%~dp0"

if not exist "node_modules\electron\dist\electron.exe" (
  where npm >nul 2>nul
  if errorlevel 1 (
    echo [Local AI Stack] Node.js/npm not found. Please install Node.js first: https://nodejs.org
    pause
    exit /b 1
  )
  echo [Local AI Stack] First run: installing Electron runtime (~100 MB), please wait...
  call npm install --no-audit --no-fund
  if errorlevel 1 (
    echo [Local AI Stack] npm install failed. Check your network connection and retry.
    pause
    exit /b 1
  )
)

start "" "%~dp0node_modules\electron\dist\electron.exe" "%~dp0"
exit /b 0
