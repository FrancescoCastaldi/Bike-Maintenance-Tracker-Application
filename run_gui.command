#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv-gui"
PYTHON_BIN="python3"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "Python 3 non trovato. Installare Python 3 e riprovare."
  exit 1
fi

if [ ! -d "$VENV_DIR" ]; then
  echo "Creazione dell'ambiente virtuale..."
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"

echo "Aggiornamento di pip e installazione delle dipendenze..."
python -m pip install --upgrade pip >/dev/null
if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
  python -m pip install -r "$SCRIPT_DIR/requirements.txt"
fi

echo "Avvio dell'interfaccia grafica..."
python "$SCRIPT_DIR/bike_maintenance_gui.py"
