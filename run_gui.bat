@echo off
setlocal ENABLEDELAYEDEXPANSION

set "VENV_DIR=.venv-gui"

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python non trovato. Installare Python 3 e riprovare.
    exit /b 1
)

if not exist "%VENV_DIR%\Scripts\python.exe" (
    echo Creazione dell'ambiente virtuale...
    python -m venv "%VENV_DIR%"
)

call "%VENV_DIR%\Scripts\activate.bat"

echo Aggiornamento di pip e installazione delle dipendenze...
python -m pip install --upgrade pip >nul
if exist requirements.txt (
    python -m pip install -r requirements.txt
)

echo Avvio dell'interfaccia grafica...
python bike_maintenance_gui.py

endlocal
