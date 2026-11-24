# F20 Intelligence

Persönliche, **rein lesende** Analyse-, Diagnose- und Codierungsplanungs-Software für einen
BMW 116i F20 (01/2012, N13, Schaltgetriebe, Radio Professional/HU_ENTRY). Privates Projekt,
nicht kommerziell. Codierungen setzt der Besitzer selbst in **BimmerCode** um.

> ⚠️ Dieses Repository ist öffentlich. Fahrzeugdaten (FIN, Backups, Diagnosen) liegen ausschließlich
> lokal in `$F20_HOME` bzw. `private/` und werden nie eingecheckt.

## Was die Software kann (Stand 0.1.0)

| Bereich | Funktion | Status |
|---|---|---|
| Backup Center | BimmerCode-`.cod`-Backups lesen (NSKeyedArchiver-bplist), SHA-256-Tresor, Fahrzeugtrennung per FIN, Duplikaterkennung, Byte-/Bit-Vergleich, Änderungshistorie | ✅ mit echten Backups nachgewiesen |
| Klartext-Codierung | Aktuelle Codierung aller Steuergeräte mit Parameternamen (lokale OpenCAFDMap-Tabellen, Layout-Prüfung) | ✅ (Namen: dokumentiert, Werte: aus Backup) |
| Coding Studio | Katalog mit 131+ Optionen inkl. Quellen, Risiko, Rechtslage (StVO/ECE), Abgleich mit dem eigenen Fahrzeug, BimmerCode-Anleitung als Export | ✅ offline |
| Lernmodus | Parameterzuordnung aus eigenen Vorher/Nachher-Backups | ✅ |
| Diagnose | ELM327 über BLE/Bluetooth Classic/WLAN, BMW-UDS (0x6F1, Extended Addressing), SG-Identifikation (SVK, CAFD), Fehlerspeicher aller SG, OBD-II-Livedaten | ✅ im Simulator · ⏳ Realtest ausstehend |
| Sicherheit | Positivliste für Diagnosedienste, kein Schreibpfad, Bestätigungspflicht für Realbetrieb | ✅ 115 Tests |
| Claude | Lokaler MCP-Server (11 lesende Werkzeuge) | ✅ |
| Oberfläche | Lokale Web-API + Grundgerüst der Premium-Dark-UI | ⏸️ auf Wunsch zurückgestellt |

## Schnellstart (macOS)
```bash
./scripts/setup_macos.sh                 # venv + Abhängigkeiten (kostenlos)
source .venv/bin/activate
f20 backup import ~/Downloads/BimmerCode # .cod-Dateien (iPhone → Dateien-App → AirDrop)
f20 backup history                       # Was wurde wann geändert?
f20 backup atlas                         # Klartext-Codierung → private/ (benötigt Namenstabellen, s. u.)
f20 catalog search --recommend           # empfehlenswerte Codierungen
f20 sim                                  # Demo-Diagnose ohne Fahrzeug (fiktive Daten)
f20 adapter scan                         # Adapter finden (passiv)
f20 diag --ble <ID> --confirm "ICH BIN AM FAHRZEUG"   # realer LESE-Test, nur am Fahrzeug
claude mcp add f20 -- "$PWD/scripts/f20-mcp"          # Claude Code anbinden (oder .mcp.json)
```
Namenstabellen (optional, Rechtslage unklar – Entscheidung des Besitzers): `scripts/fetch_opencafdmap.sh`.

## Dokumentation
[ARCHITECTURE](ARCHITECTURE.md) · [RESEARCH](RESEARCH.md) · [VEHICLE_PROFILE](VEHICLE_PROFILE.md) ·
[BACKUP_ANALYSIS](BACKUP_ANALYSIS.md) · [CODING_DATABASE](CODING_DATABASE.md) ·
[ADAPTER_COMPATIBILITY](ADAPTER_COMPATIBILITY.md) · [SECURITY](SECURITY.md) · [TEST_REPORT](TEST_REPORT.md) ·
[ROADMAP](ROADMAP.md) · [KNOWN_LIMITATIONS](KNOWN_LIMITATIONS.md) · [CHANGELOG](CHANGELOG.md) · [CLAUDE](CLAUDE.md)

## Lizenzen Dritter
bleak (MIT), pyserial (BSD-3), mcp (MIT) – optional. Formatwissen zu `.cod` aus OpenCAFDMap (MIT, eigene
Neuimplementierung). Namenstabellen werden **nicht** mitgeliefert.
