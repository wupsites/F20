#!/usr/bin/env bash
# Einrichtung von F20 Intelligence auf macOS (kostenlos, ohne Admin-Rechte).
# Voraussetzung: Python >= 3.10 (z. B. von python.org oder `brew install python`).
set -euo pipefail
cd "$(dirname "$0")/.."
PY="${PYTHON:-python3}"
"$PY" - <<'EOF' || { echo "Python >= 3.10 benötigt (python.org oder Homebrew)."; exit 1; }
import sys; assert sys.version_info >= (3, 10), sys.version
EOF
"$PY" -m venv .venv
.venv/bin/pip install --upgrade pip >/dev/null
.venv/bin/pip install -e ".[ble,serial,mcp,dev]"
chmod +x scripts/f20-mcp
echo
echo "Fertig. Nächste Schritte:"
echo "  source .venv/bin/activate"
echo "  f20 backup import ~/Pfad/zu/BimmerCode-Backups   # .cod-Dateien (Dateien-App → AirDrop auf den Mac)"
echo "  f20 backup history                               # Änderungshistorie"
echo "  f20 sim                                          # Demo ohne Fahrzeug"
echo "  f20 adapter scan                                 # Adapter finden (macOS fragt nach Bluetooth-Erlaubnis)"
echo "  claude mcp add f20 -- \"$PWD/scripts/f20-mcp\"     # Claude Code anbinden (oder .mcp.json nutzen)"
