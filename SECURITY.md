# SECURITY – Sicherheitskonzept

Die Integrität des Fahrzeugs hat oberste Priorität. F20 Intelligence ist **ausschließlich lesend**.

## 1. Mehrschichtiger Schreibschutz

| Schicht | Maßnahme | Ort | Test |
|---|---|---|---|
| Architektur | Es existiert **kein** Code zum Schreiben, Codieren, Löschen, Flashen | gesamtes Projekt | Code-Review |
| Positivliste UDS | Erlaubt nur `0x22` (1 DID), `0x19` (Lese-Subfunktionen 01/02/03/04/06/0A), `0x3E 00/80`, `0x10 01` | `safety/policy.py` | `test_safety_policy.py` |
| Sperrliste UDS | `0x11, 0x14, 0x23, 0x24, 0x27, 0x28, 0x29, 0x2A, 0x2C, 0x2E, 0x2F, 0x31, 0x34–0x38, 0x3D, 0x83–0x87` | `safety/policy.py` | parametrisiert über alle |
| OBD-II | Erlaubt Modi `01, 02, 03, 06, 07, 09, 0A`; gesperrt `04` (Fehler löschen), `05`, `08` (Aktoren) | `safety/policy.py` | ✔ |
| Adapterbefehle | Nur flüchtige AT-/ST-Befehle; gesperrt u. a. `AT PP …` (EEPROM), `AT @3` (einmalig beschreibbar), `AT BRD` (Baudrate), `AT MA` (Monitor), `AT M1` | `safety/policy.py` | ✔ |
| Sendepfad | `Elm327._send_line` sendet nur Zeilen, die zuvor die Richtlinie passiert haben (Freigabe-Token); jede Rohzeile wird erneut geprüft | `transport/elm327.py` | `test_raw_line_injection_blocked` |
| Simulator | Virtuelles Fahrzeug protokolliert jeden schreibähnlichen Dienst; Tests verlangen 0 Versuche | `sim/car.py` | `test_write_never_reaches_vehicle` |
| Realbetrieb | Reale Verbindung nur mit Eingabe „ICH BIN AM FAHRZEUG“ durch den Besitzer | `session.py`, `cli.py` | `test_demo_session_and_real_guard` |
| MCP | Werkzeuge lesen nur gespeicherte Daten; kein Werkzeug spricht mit Adapter/Fahrzeug | `mcp_server/tools.py` | `test_mcp_tools_read_only` |
| Web-API | Nur 127.0.0.1, Host-Header-Prüfung (DNS-Rebinding), POST nur mit `X-F20: 1` (CSRF) | `web/server.py` | `test_api_csrf_and_host_protection` |

## 2. Daten- und Backup-Integrität
* Originalbackups werden nur lesend geöffnet; Kopie im Tresor, benannt nach SHA-256, Rechte 0444.
* Vor jeder Analyse wird die Prüfsumme verifiziert (`Vault.read_verified`); `f20 backup verify` prüft alle.
* Virtuelle Codierung/Simulation arbeitet nur im Speicher bzw. in Arbeitskopien.

## 3. Datenschutz
* Repository ist öffentlich → keine FIN, keine Backups, keine Datenbank, keine Namenstabellen im Git.
* FIN wird in Berichten/MCP maskiert (`WBA…8606`). Fremdfahrzeuge sind ausgeschlossen.
* Keine Cloud-Dienste, keine Telemetrie. Alle Daten lokal in `$F20_HOME`.

## 4. Sicherheitskritische Steuergeräte – nur dokumentieren
DME (Motor/Emissionen), DSC, EPS (Lenkung), ICM (Fahrdynamik), ACSM (Airbag/Gurtwarnung),
Bremslicht/Notbremssignal, Wegfahrsperre (FEM/CAS-Funktionen), km-Stand. Der Katalog markiert diese als
`safety_critical`/`safety_ecu` und schließt sie von Empfehlungen aus.

**Befund 2026-11-24:** Im letzten ICM-Backup ist `IcmKod_B_Sportlenkung = verbaut` gesetzt
(vom Besitzer getestet). Empfehlung: frisches Backup erstellen; falls weiterhin gesetzt, Original-Backup
vom 27.06.2025 in BimmerCode wiederherstellen.

## 5. Voraussetzungen für künftige Schreibzugriffe (derzeit NICHT erfüllt)
Eine eigene Codierfunktion kommt nur infrage, wenn **alle** Punkte nachgewiesen sind:
1. Eindeutige Fahrzeug-/SG-Identifikation (FIN, SVK, CAFD-Version) unmittelbar vor dem Schreiben.
2. Vollständige, verifizierte Parameterzuordnung für genau diese CAFD-Version.
3. Verständnis und korrekte Behandlung der **Signatur** des Codierdatenblocks (nachgewiesen: Block
   `00 00 00 20` + 128 Byte ändert sich bei jedem Schreiben) – derzeit unbekannt → **Blocker**.
4. Adapter mit stabiler Multi-Frame-**Sendung** (ELM327 kann keine Multi-Frame-Anfragen senden) → **Blocker**
   für viele Datenblöcke.
5. Stabile Stromversorgung (Ladegerät), stabile Verbindung, getestetes Wiederherstellungsverfahren.
6. Ausdrückliche Freigabe des Besitzers je Vorgang.
Bis dahin erfolgt jede Codierung über BimmerCode.

## 6. Melden von Problemen
Privates Projekt. Sicherheitsrelevante Funde in CHANGELOG.md und hier dokumentieren.
