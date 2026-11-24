# CHANGELOG

## 0.1.0 – 2026-11-24
### Hinzugefügt
- Recherche-Berichte 01–05 (Architektur/UDS, Formate/Open Source, Adapter, HU_ENTRY/KOMBI, Karosserie/Komfort/Antrieb)
- Read-only-Positivliste (`safety/policy.py`) für UDS, OBD-II und AT/ST-Befehle
- ELM327-Transport mit BMW Extended Addressing, ISO-TP, BLE (bleak), Serial, TCP; Raw-ISO-TP-Fallback (experimentell)
- Simulator (virtueller ELM327 + F20) mit Fehlerinjektion
- UDS-Client (Identifikation, SVK, DTC), OBD-II-Decoder, Diagnosesitzung mit Live-Polling
- BimmerCode-.cod-Parser, Tresor (SHA-256, 0444), forensische Analyse, Diff, Lernmodus, Simulation
- Analyse der 22 eigenen Backups (BACKUP_ANALYSIS.md); Fremdfahrzeug ausgeschlossen
- OpenCAFDMap-Layoutwahl (Hash/Länge/Plausibilität/Feldabgleich), Parameter-Atlas, Katalog-Abgleich
- Codierungskatalog (131 Einträge) + CODING_DATABASE.md + BimmerCode-Export
- MCP-Server, CLI `f20`, lokale Web-API, macOS-Setup, 115 Tests
### Behoben
- Raw-ISO-TP-Fallback sendete `ATCEA` an Adapter ohne CEA-Unterstützung
- Duplikat-Backups überschrieben Zeitstempel → jetzt als Aliase erfasst
- Echte FIN in einem Unit-Test → durch fiktive ersetzt, Commit neu geschrieben (Force-Push auf eigenem Zweig)
### Sicherheit
- Befund: ICM `IcmKod_B_Sportlenkung = verbaut` im letzten Backup (Testcodierung) → Empfehlung in SECURITY.md
