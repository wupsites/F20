#!/usr/bin/env bash
# Lädt OpenCAFDMap-Namenstabellen für die CAFDs der eigenen Backups in $F20_HOME (NICHT ins Repository).
# Rechtslage: Die Tabellen unter definitions/untrimmed enthalten BMWs eigene Parameternamen aus älteren
# PSdZData-Ständen – Herkunft/Lizenz unklar. Nutzung nur nach eigener Entscheidung, nur privat.
set -euo pipefail
cd "$(dirname "$0")/.."
PY=".venv/bin/python"; [ -x "$PY" ] || PY=python3
HOME_DIR="$("$PY" -c 'from f20.paths import f20_home; print(f20_home())' 2>/dev/null || echo "$HOME/.local/share/f20-intelligence")"
IDS="${*:-$("$PY" - <<'EOF'
from f20.backup.service import BackupService
from f20.store import Store
ids = set()
for b in BackupService(Store()).store.list_backups():
    for c in (b["meta"].get("cod") or {}).get("cafds") or []:
        ids.add(c["id"])
print(" ".join(sorted(ids)))
EOF
)}"
[ -n "$IDS" ] || { echo "Keine CAFD-IDs gefunden – zuerst 'f20 backup import' ausführen."; exit 1; }
BASE="https://raw.githubusercontent.com/shamair28/OpenCAFDMap/main/definitions/untrimmed"
for sub in bmw merged; do mkdir -p "$HOME_DIR/mappings/opencafdmap/$sub"; done
for id in $IDS; do
  curl -sf -o "$HOME_DIR/mappings/opencafdmap/bmw/$id.tsv.gz" "$BASE/bmw/$id.tsv.gz" && echo "bmw/$id ok" || echo "bmw/$id fehlt"
  curl -sf -o "$HOME_DIR/mappings/opencafdmap/merged/$id.tsv.gz" "$BASE/$id.tsv.gz" && echo "merged/$id ok" || echo "merged/$id fehlt"
done
