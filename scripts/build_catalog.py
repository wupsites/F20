#!/usr/bin/env python3
"""Erzeugt src/f20/data/catalog/*.json aus den Recherche-Rohdaten (docs/research/raw/*.json).

Validiert jeden Eintrag (Schema, Enums, Quellenpflicht) und bricht bei Fehlern ab.
Aufruf: python scripts/build_catalog.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from f20.coding.catalog import validate_entry  # noqa: E402

SOURCES = {
    "hu_entry_kombi.json": ROOT / "docs/research/raw/04_hu_entry_kombi.json",
    "karosserie_komfort_antrieb.json": ROOT / "docs/research/raw/05_karosserie_komfort_antrieb.json",
}


def main() -> int:
    out_dir = ROOT / "src/f20/data/catalog"
    out_dir.mkdir(parents=True, exist_ok=True)
    total, errors = 0, []
    for name, src in SOURCES.items():
        entries = json.loads(src.read_text(encoding="utf-8"))
        for e in entries:
            for err in validate_entry(e):
                errors.append(f"{src.name}:{e.get('id')}: {err}")
        doc = {"_meta": {"generated_from": str(src.relative_to(ROOT)), "count": len(entries),
                         "note": "Automatisch erzeugt – nicht von Hand bearbeiten; Rohdaten in docs/research/raw ändern."},
               "entries": entries}
        (out_dir / name).write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        total += len(entries)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"{total} Einträge geschrieben nach {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
