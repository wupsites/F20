# TEST_REPORT

Stand: 2026-11-24 · Python 3.13.18 · pytest 9.2 · Ergebnis: **115 bestanden, 0 fehlgeschlagen**
Ausführen: `.venv/bin/python -m pytest`

| Datei | Tests | Abgedeckt |
|---|---|---|
| `test_safety_policy.py` | 73 | Erlaubte Lesedienste; **jeder** gesperrte UDS-Dienst; Codier-/Programmier-/Extended-Session gesperrt; fehlerhafte/zusammengesetzte Anfragen; OBD-Modi 04/05/08 gesperrt; AT-Positivliste (EEPROM-, Baudraten-, Monitorbefehle gesperrt); Audit-Log |
| `test_transport_sim.py` | 15 | ISO-TP Extended Addressing (Roundtrip, fehlender Consecutive Frame); ELM-Zeilenparser (mit/ohne Leerzeichen, >8 Byte abgelehnt); Init-Sequenz für BMW; SVK-Ident (CAFD_000000F9_007_007_001); NRC 0x78 responsePending; Negativantwort; **Schreibversuche erreichen das Fahrzeug nie** (0 gesendete Zeilen, 0 Schreibversuche im Simulator); Rohzeilen-Injektion blockiert; Klon ohne ATCEA; Raw-ISO-TP-Fallback; fehlende Flow Control erkannt; Verbindungsabbruch; CAN ERROR / NO DATA; nicht unterstützte PIDs als „nicht verfügbar“; Fehlerspeicher |
| `test_decoders.py` | 6 | SAE-J1979-Formeln; Support-Bitmasken; OBD-DTCs; UDS-DTC-Statusbits; SGBM-ID; SVK-Layout (dokumentierter Kopf) |
| `test_backup.py` | 12 | .cod-Parser (Struktur, Ablehnung fremder Formate, Upload-Präfix); **Originale bleiben unverändert** (SHA-256 + mtime); Tresor 0444 + Verifikation; Manipulation erkannt; Duplikate als Aliase; Fahrzeugtrennung; Timeline/Bit-Diff; Lernmodus (inkl. Sperre über Fahrzeuggrenzen); Simulation ohne Tresoränderung; FIN-Maskierung; Layout-Hash/Layoutwahl/Wertlabels; Ausschluss von Fremdfahrzeugen |
| `test_app.py` | 9 | Katalog (Schema, Quellenpflicht); sicherheitskritische SG nie empfohlen; Export; Demo-Sitzung + **Realmodus-Sperre**; Verbindungsabbruch in der Sitzung; Web-API; **CSRF-/Host-Header-Schutz**, Realstart über API ohne Bestätigung abgelehnt; Backup-Upload; MCP-Werkzeuge lesend + Freigabesteuerung |

## Zusätzlich manuell geprüft
* MCP-Server über stdio mit dem offiziellen MCP-Client (11 Werkzeuge, Aufrufe `backup_history`,
  `current_coding`, `coding_options`, `latest_diagnosis`, `live_snapshot`, `vehicle_profile`, `research`).
* CLI: `f20 backup history`, `f20 sim`, `f20 diag` ohne Bestätigung → Abbruch (Exit 3).
* Reale Backups: 22 Dateien importiert, Originale vor/nach SHA-256-identisch, 17 eindeutige Inhalte.

## Nicht getestet (bewusst)
* Realer Adapter / reales Fahrzeug (ausstehend, nur mit Zustimmung des Besitzers am Fahrzeug).
* BLE unter macOS (CoreBluetooth) – Code-Pfad vorhanden, in Linux-CI nicht ausführbar.
* Web-Oberfläche (JavaScript) – zurückgestellt.
