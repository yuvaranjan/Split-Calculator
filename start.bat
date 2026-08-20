@echo off
setlocal
cd /d "%~dp0"

set "PORT=8000"
start "Split calculator" "http://127.0.0.1:%PORT%/"

where py >nul 2>&1
if %errorlevel% equ 0 (
  py server.py
  goto :eof
)

where python >nul 2>&1
if %errorlevel% equ 0 (
  python server.py
  goto :eof
)

echo Python was not found. Install Python, then run this file again.
pause
