# CLAUDE.md – Arbeitsanweisungen für Claude-Code-Sitzungen (PROJECT F20)

## Projekt
Private, nicht-kommerzielle Analyse-/Diagnose-Software für **einen** BMW 116i F20 (Produktion 01/2012,
N13, Schaltgetriebe, Radio Professional = HU_ENTRY). Ziel: Fahrzeug verstehen, Codierungen planen
(Umsetzung durch den Besitzer in **BimmerCode**), Diagnose/Live-Daten lesend, Claude-Anbindung per MCP.
Sprache der Doku und UI: **Deutsch**.

## Harte Regeln (nicht verhandelbar)
1. **Read-only.** Kein Code-Pfad darf Schreib-, Lösch-, Reset-, Routine-, Security-Access-, Session-Wechsel-
   (außer 0x10 0x01) oder Flash-Dienste erzeugen. Positivliste: `src/f20/safety/policy.py`. Änderungen daran
   nur mit Tests (`tests/test_safety_policy.py`) und CHANGELOG-Eintrag. Siehe SECURITY.md.
2. **Kein realer Fahrzeugkontakt durch Claude.** Reale Verbindungen startet ausschließlich der Besitzer
   (`f20 diag … --confirm "ICH BIN AM FAHRZEUG"`). Claude führt `diag` nie selbst aus.
3. **Sicherheitskritische SG nur dokumentieren:** DME, DSC, EPS, ICM, ACSM (Airbag), Bremslicht/Notbremssignal,
   Wegfahrsperre, km-Stand, Emissionen. Nie zur Änderung raten.
4. **Datenschutz:** Repository ist **öffentlich**. Niemals FIN/VIN, Backups (`*.cod`), Datenbank, Atlas
   (`private/`) oder OpenCAFDMap-Namenstabellen einchecken. FIN in Doku nur maskiert (`WBA…8606`).
   Vor jedem Commit: `git diff --cached | grep -E "WBA[A-HJ-NPR-Z0-9]{14}"` muss leer sein
   (Ausnahme: öffentlicher EdiabasLib-Trace `WBAJM71000B055940` in docs/research/raw/01).
5. **Nichts erfinden.** Jede Aussage trägt einen Nachweisstatus (verified/documented/likely/experimental/
   incompatible/unknown). „Dokumentiert“ ≠ „am Fahrzeug getestet“.
6. **Originale nie verändern.** Backups nur über den Tresor (`f20.backup.integrity.Vault`, SHA-256, 0444).

## Fahrzeug-Fakten (Stand 2026-11-24, aus Backups nachgewiesen)
| Kennung | Adresse | SG | CAFD |
|---|---|---|---|
| 0F16B0 | 0x40 | FEM_BODY | CAFD_00000794_004_228_010 |
| 0F16C0 | 0x72 | REM (PDC integriert) | CAFD_000007A1_005_028_006 |
| 0F1630 | 0x60 | KOMBI | CAFD_00000760_006_000_052 |
| 0F1650 | 0x1C | ICM | CAFD_0000067B_002_003_139 |
| 0F17C0 | 0x78 | IHKA (Klimaautomatik) | CAFD_00000A3F_005_001_013 |
| 0F1820 | 0x63 | HU_ENTRY | CAFD_000000F9_007_007_001 |
| 0F16E0 | 0x01 | ACSM | CAFD_00000911_003_001_001 |
Fremdfahrzeug `WBA…4254` (E-Serie-1er eines Kollegen) ist ausgeschlossen (`$F20_HOME/vehicle.local.json`).

## Lokale Daten (nicht im Repo)
`$F20_HOME` (macOS: `~/Library/Application Support/F20 Intelligence`, Linux: `~/.local/share/f20-intelligence`):
`vault/originals/` (Backups, 0444), `f20.sqlite3`, `vehicle.local.json` (FIN, excluded_vins),
`mappings/opencafdmap/{bmw,merged}/<CAFD>.tsv.gz` (Namenstabellen, Freigabe des Besitzers 2026-11-24),
`mcp_consent.json`. Persönliche Berichte: `private/` im Repo-Ordner (gitignored).

## Entwicklung
```bash
python3 -m venv .venv && .venv/bin/pip install -e ".[dev,mcp,ble,serial]"
.venv/bin/python -m pytest            # muss grün sein
.venv/bin/python scripts/build_catalog.py && .venv/bin/python scripts/export_catalog_md.py
f20 backup history | f20 backup atlas | f20 sim | f20 mcp
```
Katalog-Rohdaten: `docs/research/raw/0[4-7]_*.json` → `scripts/build_catalog.py` → `src/f20/data/catalog/`.

## Wichtige Dateien
`src/f20/safety/policy.py` · `src/f20/transport/elm327.py` (BMW Extended Addressing 0x6F1) ·
`src/f20/backup/cod.py` (BimmerCode .cod = NSKeyedArchiver-bplist) · `src/f20/backup/layouts.py`
(Namenstabellen/Layoutwahl) · `src/f20/backup/personal.py` · `src/f20/mcp_server/tools.py`.

## Offene Punkte
Siehe ROADMAP.md und KNOWN_LIMITATIONS.md. Nächster Meilenstein: lesender Realtest am Fahrzeug
(Adapter identifizieren → `f20 adapter scan` → `f20 diag`).
