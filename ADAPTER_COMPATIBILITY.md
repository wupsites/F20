# ADAPTER_COMPATIBILITY – OBD-Adapter, ELM327, Bluetooth und macOS

Quelle: `docs/research/raw/03_adapter_kommunikation.md` (mit Einzelnachweisen). Stand 2026-11-24.
**Der eigene Adapter ist noch nicht identifiziert.** Nichts davon ist am Fahrzeug getestet.

## 1. Welcher Adapter kommt infrage?
Der Adapter funktioniert mit BimmerCode auf dem iPhone → er nutzt **BLE**, **MFi-Bluetooth-Classic**
(z. B. OBDLink MX+) oder **WLAN**. BimmerCode-iOS-Liste (dokumentiert): UniCarScan UCSI-2100,
OBDLink CX (BLE, STN2310), OBDLink MX+ (Classic/MFi, STN2255), vLinker BM+/MC+ (MC+ dual, BLE-Name
„vLinker MC-IOS“), Veepeak OBDCheck BLE/BLE+, NEXAS NexLink.

**Bitte notieren:** Aufdruck/Modell des Adapters und der Name in BimmerCode bzw. iPhone-Bluetooth.

## 2. BLE-GATT-Profile (implementiert in `transport/ble.py`, Auswahl automatisch)
| Familie | Service | Notify | Write | Nachweis |
|---|---|---|---|---|
| OBDLink CX / WgSoft | FFF0 | FFF1 | FFF2 | Dokumentiert |
| Deep OBD | FFE0 | FFE1 | FFE2 | Dokumentiert (EdiabasLib) |
| Carly / HM-10 | FFE0 | FFE1 | FFE1 | Dokumentiert (EdiabasLib) |
| vLinker | E7810A71-73AE-499D-8C15-FAA9AEF0C3F2 | BEF8D6C9-…-BD58C1009F9F | dieselbe | Dokumentiert, Quellen teils widersprüchlich |
| diverse | 18F0 | 2AF0 | 2AF1 | Wahrscheinlich |
| Microchip Transparent UART | 49535343-FE7D-… | 49535343-1E4D-… | 49535343-8841-… | Dokumentiert |
Fallback: generische Suche nach einem Dienst mit Notify- und Write-Characteristic. Schreiben in 20-Byte-Blöcken
(bzw. MTU−3). OBDLink CX: Bonding nur in den ersten 5 Minuten nach Einstecken.

## 3. ELM327-Sequenz für BMW F-Serie (D-CAN, Extended Addressing)
```
ATZ  ATE0  ATL0  ATS1  ATH1  ATAL  ATSP6  ATST64        # Grundinit, CAN 11 Bit 500 kBit/s
ATSH6F1                                                 # Tester-ID
ATCRA6xx                                                # nur Antworten der Ziel-ECU (0x600+Adresse)   (ab v1.3)
ATCEAxx                                                 # Extended Address = ECU-Adresse              (ab v1.4)
ATFCSH6F1  ATFCSDxx300000  ATFCSM1                      # eigene Flow Control (Datenblatt-Beispiel)   (ab v1.1)
22F190                                                  # z. B. FIN lesen
```
Erwartete Antwort (ATH1/ATS1): `6xx F1 10 LL 62 F1 90 …` (First Frame), `6xx F1 21 …` (Consecutive Frames).
CAN-Frames sind max. 8 Byte; BMW nutzt DLC 8 mit 0x00-Padding. ELM327 ≥ v2.1 wartet bei `7F xx 78`
bis 5 s; zusätzlich wiederholt die Software die Anfrage.

## 4. Klone und Einschränkungen
| Merkmal | Auswirkung | Umgang |
|---|---|---|
| „ELM327 v1.5“ | Version existiert bei Elm Electronics nicht → Klon | Warnung, Funktionsprüfung per `?` |
| kein `ATCEA` | BMW-Steuergeräte nicht erreichbar | experimenteller Raw-ISO-TP-Modus (CAF0, eigene FC), standardmäßig aus |
| kein `ATFCSM` | Multi-Frame-Antworten unvollständig | wird erkannt und gemeldet |
| keine Multi-Frame-**Sendung** | betrifft nur Schreiben (nicht implementiert) | – |
| STN-Chips (OBDLink) | zusätzliche `ST…`-Befehle (z. B. `STCAF`, `STPX`) | nur `STI/STDI/STSN` (lesend) erlaubt |

## 5. macOS
* BLE über `bleak` (CoreBluetooth). Beim ersten Scan Bluetooth-Berechtigung für Terminal/Python erteilen.
* macOS zeigt UUIDs statt MAC-Adressen. BimmerCode/iPhone vorher trennen (nur eine Verbindung gleichzeitig).
* Bluetooth Classic SPP: nach Kopplung `/dev/cu.<Name>`; Zugriff über `pyserial`.
* WLAN-Adapter: TCP `192.168.0.10:35000`.

## 6. Bibliotheken – Bewertung
| Bibliothek | Ergebnis |
|---|---|
| python-OBD 0.7.3 (GPL-2.0) | verwirft Frames mit `F1` → **keine BMW-UDS**; für Mode 01 nutzbar, aber nicht nötig |
| python-can 4.6.1 / can-isotp 2.0.7 | kein ELM327-Backend; setzen Roh-CAN voraus (unter macOS nicht verfügbar) |
| udsoncan 1.26.1 (MIT) | eigene Connection-Klasse möglich; derzeit nicht nötig |
| bleak 3.1.0 (MIT) | **verwendet** |
| EdiabasLib (GPL-3.0) | Referenz für Sequenzen/Profile; Code nicht übernommen |
Entscheidung: eigene, schlanke ELM327-UDS-Schicht (`transport/elm327.py`) mit Positivliste.

## 7. Erster Realtest (nur mit Zustimmung, am Fahrzeug)
1. `f20 adapter scan` (passiv) → Adapter-ID notieren.
2. Zündung an, Motor aus, Ladegerät empfohlen.
3. `f20 diag --ble <ID> --confirm "ICH BIN AM FAHRZEUG"` → Identifikation aller SG, Fehlerspeicher, OBD-PIDs.
4. Ergebnis wird lokal gespeichert; Claude kann es per MCP (`latest_diagnosis`) auswerten.
