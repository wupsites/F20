# ARCHITECTURE

## Stack-Entscheidung
| Option | Bewertung |
|---|---|
| **Python 3.10+ (gewählt)** | Kern ohne Laufzeitabhängigkeiten, vollständig testbar (auch in Linux-CI), `bleak` nutzt auf macOS nativ CoreBluetooth, MCP-SDK verfügbar, `plistlib` liest `.cod` direkt |
| Swift/SwiftUI | nativste macOS-Oberfläche, aber in dieser Entwicklungsumgebung nicht bau-/testbar; später als Frontend auf derselben lokalen API möglich |
| Tauri/Rust | gute Apps, aber höhere Komplexität; kein Vorteil für BLE/MCP |
| SQLite | lokale Datenhaltung (Standardbibliothek) |

Oberfläche: lokale Web-App (Standardbibliothek-HTTP-Server, 127.0.0.1) mit HTML/CSS/JS ohne CDN; optional
als natives Fenster über `pywebview` (WKWebView). Auf Wunsch des Besitzers vorerst zurückgestellt.

## Module
```
src/f20/
├── safety/policy.py        Positivliste UDS/OBD/AT (Default-Deny), Audit-Log
├── transport/
│   ├── elm327.py           ELM327/STN-Protokoll, BMW Extended Addressing, ISO-TP, Fehlerbilder
│   ├── isotp.py            Frame-Parser, Reassemblierung (Ext. Addressing 0xF1)
│   ├── ble.py              bleak (CoreBluetooth), GATT-UART-Profile, passiver Scan
│   └── serial_tcp.py       Bluetooth-Classic/USB (pyserial), WLAN (TCP)
├── sim/                    virtueller ELM327 + virtueller F20 (fiktive Daten, Fehlerinjektion)
├── uds/                    Diagnoseclient (Ident, SVK, DTC), NRC, SVK-/DTC-Decoder
├── obd/pids.py             SAE-J1979-Dekodierung
├── backup/
│   ├── cod.py              BimmerCode .cod (NSKeyedArchiver) – generischer Unarchiver
│   ├── integrity.py        Tresor (SHA-256, 0444), Arbeitskopien
│   ├── forensic.py         generische Forensik für unbekannte Formate
│   ├── diff.py             Byte-/Bit-Vergleich, Hexdump
│   ├── mapping.py          Lernmodus/TSV-Zuordnungen
│   ├── layouts.py          OpenCAFDMap-Paketformat, Layout-Hash, Layoutwahl, Feldabgleich
│   ├── personal.py         eigenes Fahrzeug, Atlas, Katalog-Abgleich, Historie mit Namen
│   └── service.py          Backup Center (Import, Vergleich, Timeline, Simulation)
├── coding/catalog.py       Katalog laden/validieren/suchen, Bewertung, BimmerCode-Export
├── analysis.py             abgeleitete Größen (Ladedruck, Verbrauch), Faustregel-Befunde
├── session.py              Diagnosesitzung (Thread + asyncio), Demo/Real, Live-Polling
├── store.py                SQLite (Backups, Sitzungen, Messwerte, Änderungen, Plan, Lernmodus)
├── web/server.py           lokale API + statische UI (127.0.0.1, Host-/CSRF-Schutz, SSE)
├── mcp_server/             lesender MCP-Server (stdio) für Claude Code
└── cli.py                  Kommandozeile `f20`
```

## Datenfluss
```
iPhone BimmerCode ──(.cod via AirDrop)──► f20 backup import ──► Tresor (SHA-256) ──► SQLite-Metadaten
                                                                      │
                     OpenCAFDMap-Tabellen (lokal, optional) ──► layouts.py ──► Atlas / Historie / Katalog-Abgleich
                                                                      │
OBD-Adapter ◄─BLE/SPP/TCP─► transport ◄─ elm327 (Positivliste) ◄─ uds/obd ◄─ session ──► SQLite (Messwerte, DTC)
                                                                      │
                                Claude Code ◄──stdio── mcp_server (nur lesen gespeicherter Daten)
```

## BMW-Diagnosetransport (dokumentiert, Simulator-getestet)
D-CAN 500 kBit/s, 11 Bit. Tester 0x6F1, 1. Datenbyte = ECU-Adresse; Antwort 0x600+Adresse mit 0xF1.
ELM: `ATSH6F1`, `ATCRA6xx`, `ATCEAxx`, `ATFCSH6F1`, `ATFCSDxx300000`, `ATFCSM1`. Standard-OBD über 0x7DF/0x7E8.

## Erweiterbarkeit
* Neue Katalogeinträge: `docs/research/raw/*.json` → `scripts/build_catalog.py` (Schema-Validierung).
* Neue Adapterprofile: `transport/ble.py: KNOWN_UART_PROFILES`.
* Neue lesende DIDs: `uds/client.py: IDENT_DIDS` (Positivliste erlaubt jede einzelne DID per 0x22).
