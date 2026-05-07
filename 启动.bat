@echo off
cd /d "%~dp0"

if not exist "venv\Scripts\python.exe" (
    echo [1/3] Creating virtual env...
    python -m venv venv
    echo [2/3] Installing dependencies...
    venv\Scripts\python -m pip install -r requirements.txt -q
) else (
    echo venv already exists, skipping setup
)

echo [3/3] Starting Talent Helper...
echo.
venv\Scripts\python main.py
pause
