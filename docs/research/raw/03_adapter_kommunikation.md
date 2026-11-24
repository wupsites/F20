# 03 – OBD-Adapter, ELM327-Protokoll, Bluetooth (Classic vs. BLE) und macOS-Konnektivität

Stand der Recherche: 2026-11-24. Fahrzeug: BMW 116i F20, Bj. 01/2012, N13-Motor, Schaltgetriebe.
Ziel: **ausschließlich lesender** Zugriff vom MacBook (macOS) über den vorhandenen Bluetooth-OBD-Adapter, der bereits mit BimmerCode auf dem iPhone funktioniert (Modell noch unbekannt).

Evidenz-Tags:
- **[DOK]** – in einer zitierten Quelle dokumentiert (Quellennummer in eckigen Klammern, z. B. [Q3])
- **[WAHRSCHEINLICH]** – abgeleitet / plausibel, aber nicht direkt belegt
- **[UNBEKANNT]** – konnte nicht verifiziert werden

---

## 0. Kurzfassung

1. Ein iPhone kann nur mit **BLE-**, **MFi-Bluetooth-Classic-** oder **WLAN-Adaptern** reden. Da der Besitzer von einem *Bluetooth*-Adapter spricht, ist sein Adapter mit hoher Wahrscheinlichkeit ein **BLE-Adapter** (OBDLink CX, vLinker MC+/BM+ im BLE-Modus, Veepeak OBDCheck BLE/BLE+, UniCarScan UCSI-2100, ggf. NEXAS NexLink) oder ein **OBDLink MX+** (Bluetooth Classic mit MFi) [WAHRSCHEINLICH, Begründung in Abschnitt 2].
2. BLE-ELM327-Adapter emulieren eine serielle Schnittstelle über herstellerspezifische GATT-Services. Verifiziert sind u. a. **FFF0/FFF1(notify)/FFF2(write)** (OBDLink CX, „WgSoft“), **FFE0/FFE1(notify)/FFE2 bzw. FFE1(write)** (Deep OBD, Carly) und **E7810A71-…/BEF8D6C9-… (notify+write)** (vLinker laut EdiabasLib) [DOK, Q4, Q5, Q12]. Das konkrete Profil des eigenen Adapters **muss per GATT-Scan ermittelt werden**.
3. BMW F-Serie über D-CAN: Tester sendet auf **CAN-ID 0x6F1**, erstes Datenbyte = **Zieladresse** (DME = **0x12**), Antwort kommt auf **0x600 + Steuergeräteadresse** (DME → **0x612**) mit **0xF1** als erstem Datenbyte (ISO-TP „extended addressing“) [DOK, Q6, Q13]. Mit einem echten ELM327 ≥ v1.4 lässt sich das über `ATSH6F1`, `ATCEA12`, `ATFCSH6F1`, `ATFCSD12300000`, `ATFCSM1` abbilden [DOK, Q2, Q6].
4. Ein ELM327 segmentiert beim **Senden** keine Multi-Frame-Nachrichten automatisch (nur Empfang + Flow Control) [WAHRSCHEINLICH]; EdiabasLib baut First/Consecutive Frames für Requests selbst [DOK, Q6]; STN-Chips (OBDLink) können es mit `STCSEGT1` / `STPX` [DOK, Q3]. Für reines Lesen (z. B. `22 xx xx`) reichen Single Frames.
5. **python-OBD** (0.7.3) ist für Mode-01-PIDs über eine serielle Schnittstelle brauchbar (über BLE nur mit einer BLE→PTY-Brücke wie `ble-serial`), sein CAN-Parser **verwirft aber BMW-Frames mit Extended Addressing** [DOK, Q15]. **udsoncan + can-isotp** brauchen rohe CAN-Frames (python-can hat **kein** ELM327-Backend) [DOK, Q17, Q18]. Pragmatisch: **eigene dünne ELM327-Transportschicht** (BLE via `bleak`), optional mit eigener `udsoncan.BaseConnection`.

---

## 1. Fahrzeugkontext und Annahmen

| Punkt | Aussage | Tag |
|---|---|---|
| DME des N13 im F20 116i | Bosch **MEVD17.2.5** wird von mehreren (Sekundär-)Quellen für N13/F20 genannt; kein offizielles BMW/Bosch-Dokument gefunden | [WAHRSCHEINLICH] [Q20] |
| Diagnose-Bus am OBD-Stecker | D-CAN, 11-bit-IDs, 500 kbit/s (ELM-Protokoll 6 = „ISO 15765-4 CAN (11 bit ID, 500 kbaud)“) | Protokoll-Definition [DOK, Q2]; D-CAN 500k bei BMW F-Serie [WAHRSCHEINLICH] |
| BMW-Adressierung | Request CAN-ID 0x600 + Tester (0xF1) = **0x6F1**, Zieladresse im 1. Datenbyte; Antwort auf 0x600 + SG-Adresse | [DOK, Q13; im Code von EdiabasLib: `canHeader = 0x600 | sourceAddr`, Q6] |
| DME-Adresse | **0x12** | [DOK, Q13] (Beispiel aus G29, für F20 [WAHRSCHEINLICH] identisch) |
| ELM327 seit 2007er BMW | EdiabasLib unterstützt ELM327 nur für D-CAN („BMW vehicles starting from 3/2007“) | [DOK, Q8] |
| Getriebe-SG | Schaltgetriebe → kein EGS; auf OBD-Funktionalanfragen antwortet vermutlich nur die DME (7E8) | [WAHRSCHEINLICH] |

---

## 2. Von BimmerCode unterstützte Adapter (bimmercode.app/adapters)

Die Seite hat drei Reiter: **iOS adapters**, **Android adapters**, **Desktop adapters** [DOK, Q1]. Die folgende Liste wurde direkt aus dem HTML extrahiert (Abruf 2026-11-24).

### 2.1 Reiter „iOS adapters“ (relevant, da der Besitzer BimmerCode auf dem iPhone nutzt)

| Adapter (Name laut BimmerCode) | Baureihen laut BimmerCode | Funk-Technik | Chipsatz | Typischer Gerätename | Tags |
|---|---|---|---|---|---|
| UniCarScan **UCSI-2100** Bluetooth | All Series | BLE (iOS-tauglich ⇒ BLE oder MFi) | unbekannt | unbekannt | Liste [DOK, Q1]; Technik [WAHRSCHEINLICH BLE]; Chip/Name [UNBEKANNT] |
| **OBDLink CX** Bluetooth („Made for BimmerCode“) | All Series | **BLE** („OBD to BLE“) | **STN2310** | Model Number im Device-Information-Service: „OBDLink CX“; Advertising-Name nicht dokumentiert | [DOK, Q1, Q3, Q4]; Advertising-Name [UNBEKANNT] |
| **OBDLink MX+** Bluetooth | All Series | Bluetooth (Classic); laut FRPM „Supports iOS devices“ ⇒ MFi | **STN2255** (OoP) / **STN2256** (aktiv) | unbekannt | Liste/Chip [DOK, Q1, Q3]; „Classic + MFi“ [WAHRSCHEINLICH] |
| **vLinker BM+** Bluetooth | E 2008+, F, G, I, R 2008+ | vermutlich Dual-Mode (Classic + BLE), iOS nutzt BLE | Vgate-eigen, unbekannt | vermutlich „vLinker BM…“ | Liste [DOK, Q1]; Rest [WAHRSCHEINLICH]/[UNBEKANNT] |
| **vLinker MC+** Bluetooth | E 2008+, F, G, I, R 2008+ | **Bluetooth 3.0 + BLE 4.0** (Dual-Mode) | Vgate-eigen, unbekannt | BLE-Name „**vLinker MC-IOS**“, Classic-Name „vLinker MC-Android“ | Liste [DOK, Q1]; BT3.0+BLE4.0 [DOK, Q10]; Namen [DOK, Q11 (Forum)] |
| **Veepeak OBDCheck BLE** Bluetooth | E 2008+, F, I, R 2008+ | BLE (laut Produktname) | unbekannt | unbekannt | Liste [DOK, Q1]; Rest [WAHRSCHEINLICH]/[UNBEKANNT] |
| **Veepeak OBDCheck BLE+** Bluetooth | E 2008+, F, I, R 2008+ | BLE (laut Produktname) | unbekannt | unbekannt | wie oben |
| **NEXAS NexLink** | E 2008+, F, I, R 2008+ | Technik auf der Seite nicht angegeben; im iOS-Reiter ⇒ BLE/MFi/WLAN | unbekannt | unbekannt | Liste [DOK, Q1]; Rest [UNBEKANNT] |
| UniCarScan UCSI-3000 **ENET Wi-Fi**, MHD ENET Wi-Fi, bm3 ENET Wi-Fi, DITUPA, Exctool, BMDiag, KIES ENET Wi-Fi, xA Ultra Wi-Fi, ENET-Kabel + Ethernet-Adapter | F, G, I (xA: F, G) | WLAN/Ethernet (ENET = HSFZ über Ethernet, **kein** ELM327) | – | – | Liste [DOK, Q1]; ENET = HSFZ/DoIP [DOK, Q8] |
| MHD Universal Wi-Fi; vLinker BM Wi-Fi; vLinker MC Wi-Fi | E 2008+, F, G, I, R 2008+ | WLAN (ELM-artig) | – | – | [DOK, Q1] |
| MHD Wi-Fi, THOR Wi-Fi | E, R | WLAN | – | – | [DOK, Q1] |

### 2.2 Nur im Reiter „Android adapters“ bzw. „Desktop adapters“

- Android: zusätzlich **OBDLink LX** (STN1155, „OBD to Bluetooth“, Classic SPP), **OBDLink SX/EX** (USB), **vLinker BM** / **vLinker MC** (ohne „+“), DCAN-USB-Kabel; vLinker BM+/MC+ erscheinen dort als „All Series“ [DOK, Q1, Q3].
- Desktop: OBDLink SX, OBDLink EX, ENET-Kabel, DCAN-USB-Kabel [DOK, Q1].
- **Nicht (mehr) gelistet** sind auf der aktuellen Seite: vLinker FS, UCSI-2000, Carista, Veepeak-Classic-Modelle [DOK – Fehlen auf Q1 am Abrufdatum].

### 2.3 Ableitung für den Adapter des Besitzers

- iOS erlaubt Apps nur BLE (CoreBluetooth), MFi-zertifiziertes Bluetooth Classic (External Accessory / iAP2) oder WLAN. Generisches Bluetooth-Classic-SPP ist für iOS-Apps nicht nutzbar [WAHRSCHEINLICH – allgemein bekannte iOS-Plattformeinschränkung].
- Da der Besitzer „Bluetooth“ sagt (nicht WLAN), kommen in Frage:
  - **BLE**: OBDLink CX, vLinker MC+/BM+ (BLE-Seite), Veepeak OBDCheck BLE/BLE+, UCSI-2100, ggf. NexLink → **auf dem Mac via CoreBluetooth/`bleak`** [WAHRSCHEINLICH].
  - **MFi-Classic**: OBDLink MX+ → auf dem Mac **wahrscheinlich** als klassisches SPP-Gerät koppelbar (`/dev/cu.*`) [WAHRSCHEINLICH; nicht verifiziert, ob MX+ am Mac SPP anbietet].
- **Erster praktischer Schritt**: BLE-Scan vom Mac (Abschnitt 8) und Blick in „Systemeinstellungen → Bluetooth“ (Classic-Geräte erscheinen dort, BLE-UART-Adapter meist nicht).

---

## 3. BLE-GATT-„UART“-Profile von ELM327-artigen Adaptern

Alle 16-bit-UUIDs sind Kurzformen der Bluetooth-Basis-UUID `0000xxxx-0000-1000-8000-00805F9B34FB`. FFF0/FFE0 sind **nicht** bei der Bluetooth SIG registriert, also herstellerspezifisch [DOK für FFF0-Hinweis via Nordic-DevZone-Suchtreffer, sonst WAHRSCHEINLICH].

### 3.1 UUID-Tabelle

| Familie / Quelle | Service-UUID | Notify (Adapter → Host) | Write (Host → Adapter) | Belege / Tag |
|---|---|---|---|---|
| **OBDLink CX** (offizielle Herstellerdoku) | `0000FFF0-0000-1000-8000-00805F9B34FB` | `0000FFF1-…` (Notify) | `0000FFF2-…` (Write **und** Write Without Response) | [DOK, Q4]; zusätzlich 180A Device Information, FEF5 „internal use only“ [DOK, Q4] |
| „WgSoft“ (EdiabasLib, Android) | `0000fff0-…` | `0000fff1-…` | `0000fff2-…` | [DOK, Q5] |
| „Deep OBD“ (EdiabasLib, Android + Windows) | `0000ffe0-…` | `0000ffe1-…` | `0000ffe2-…` | [DOK, Q5, Q5b] |
| „Carly“ (EdiabasLib) / HM-10-artige Module | `0000ffe0-…` | `0000ffe1-…` | `0000ffe1-…` (dieselbe Characteristic) | [DOK, Q5]; HM-10-Zuordnung [WAHRSCHEINLICH] |
| **vLinker** (EdiabasLib) | `e7810a71-73ae-499d-8c15-faa9aef0c3f2` | `bef8d6c9-9c21-4c9e-b632-bd58c1009f9f` | `bef8d6c9-9c21-4c9e-b632-bd58c1009f9f` (dieselbe) | [DOK, Q5] |
| vLinker – abweichende Angabe | `E7810A71-…` | `BE781A71-73AE-499D-8C15-FAA9AEF0C3F2` | dieselbe | steht in `react-native-bluetooth-obd-manager` 1.0.4 [Q21], **widerspricht EdiabasLib** → als unzuverlässig betrachten [UNBEKANNT] |
| 18F0-Profil (ESPHome-Komponente, Adapter vermutlich vLinker MC+) | `18F0` | `2AF0` („rx_char_uuid“) | `2AF1` („tx_char_uuid“) | Konfiguration [DOK, Q14]; Zuordnung notify/write und zum vLinker [WAHRSCHEINLICH] |
| FFF0 mit FFF1 read / FFF2 write (Python-Bibliothek `elm327-obdii`, Default-Konfig) | – | `0000fff1-…` | `0000fff2-…` | [DOK, Q22] |
| Microchip/ISSC „Transparent UART“ (BM70/RN4870) | `49535343-FE7D-4AE5-8FA9-9FAFD205E455` | `49535343-1E4D-4BD9-BA61-23C647249616` (TX: Notify, Write, WwR) | `49535343-8841-43F4-A8D4-ECBE34729BB3` (RX: Write, WwR) | [DOK, Q23]; Verwendung in OBD-Adaptern [UNBEKANNT] |
| Nordic UART Service | `6E400001-B5A3-F393-E0A9-E50E24DCCA9E` | `6E400003-B5A3-F393-E0A9-E50E24DCCA9E` | `6E400002-B5A3-F393-E0A9-E50E24DCCA9E` | Zuordnung write=…02 / read=…03 [DOK, Q16 (ble-serial)]; Verwendung in OBD-Adaptern [UNBEKANNT] |

**Wichtig:** Hersteller wechseln die BLE-Module zwischen Hardware-Revisionen; derselbe Produktname kann verschiedene Profile haben (vgl. vLinker: E7810A71 vs. 18F0) [WAHRSCHEINLICH]. → **Immer per GATT-Discovery prüfen.**

### 3.2 Generische Auto-Erkennung (Vorbild EdiabasLib) [DOK, Q5b]

EdiabasLib (`BtLeGattSpp.cs`, Windows/InTheHand) probiert zuerst die bekannten Profile und fällt sonst auf eine Heuristik zurück: Pro Service genau **eine** Characteristic mit *Notify* (= Lese-Kanal) und genau **eine** mit *Write* (= Schreib-Kanal); ist es dieselbe Characteristic, muss sie *Read|Write|Notify* haben. Gibt es mehrere Kandidaten, wird der Service verworfen.

### 3.3 Schreiben, MTU, Chunking

| Aspekt | Befund | Tag |
|---|---|---|
| Notify einschalten | EdiabasLib (Android) schreibt den CCCD `00002902-…` mit EnableNotificationValue; unter Windows `StartNotificationsAsync()` | [DOK, Q5, Q5b] |
| Chunk-Größe | EdiabasLib: `MaxWriteLength = 20` Bytes pro Write | [DOK, Q5, Q5b] |
| Write-Typ | EdiabasLib: **Write with Response** (`WriteValueWithResponseAsync` bzw. `GattWriteType.Default`), wartet pro Chunk auf Bestätigung (Timeout 2 s) | [DOK, Q5, Q5b] |
| OBDLink CX | max. MTU 247; >20 Byte ohne MTU-Handling kann scheitern; **keine Queued Writes**; pro Chunk auf Write-Response warten; Notifications puffern (Push-Modell); Bonding nur in den ersten **5 min nach Power-on**, Legacy-PIN **123456**; Verbindung immer verschlüsselt; iOS-MTU ausgehandelt (iOS 10: 185) | [DOK, Q4] |
| ble-serial | Default-MTU für Senden 20 Byte, Option `--write-with-response` | [DOK, Q16] |
| Antwort-Fragmentierung | Notifications zerschneiden ELM-Antworten beliebig → Bytestrom puffern bis zum Prompt `>` (0x3E); EdiabasLib erkennt Antwortende genau am `>` | Prompt-Erkennung [DOK, Q6]; Fragmentierung [WAHRSCHEINLICH] |
| Praxis | ELM-Kommandos sind kurz (z. B. `ATCEA12\r` = 8 Byte, `22F190\r` = 7 Byte) → 20-Byte-Chunks genügen; Write-with-Response ist robuster, Write-without-Response schneller | [WAHRSCHEINLICH] |

---

## 4. ELM327-Befehle: Semantik und Firmware-Version der Einführung

Quelle: ELM327-Datenblatt **ELM327DSK** (dokumentiert Firmware bis „ELM327 v2.2“), Abschnitte „AT Command Summary“, „AT Command Descriptions“ und „Version History“ [DOK, Q2]. Ältere Revision ELM327DSI ebenfalls geprüft [Q2b].

| Befehl | Bedeutung | eingeführt | Tag |
|---|---|---|---|
| `ATZ` | Reset all | v1.0 | [DOK, Q2] |
| `ATD` | Set all to defaults (setzt u. a. CEA zurück) | v1.0 | [DOK, Q2] |
| `ATE0` | Echo aus (Default E1) | v1.0 | [DOK, Q2] |
| `ATL0` | Linefeeds aus | v1.0 | [DOK, Q2] |
| `ATS0` / `ATS1` | Leerzeichen in Ausgabe aus/an | **v1.3** | [DOK, Q2] |
| `ATH1` | Header anzeigen – zeigt die *komplette* Nachricht inkl. **PCI-Bytes**; überschreibt bei CAF1 die Empfangsformatierung („appear much like in the CAF0 mode“) | v1.0 | [DOK, Q2] |
| `ATAL` | Allow Long (>7 Byte senden, unbegrenzt empfangen) | v1.0 | [DOK, Q2] |
| `ATSP6` | Protokoll 6 = ISO 15765-4 CAN 11 bit, 500 kbaud | v1.0 (SP) | [DOK, Q2] |
| `ATSH xyz` | CAN-ID (11 bit) für Requests | v1.0 | [DOK, Q2] |
| `ATCAF0/1` | CAN Auto Formatting (PCI erzeugen/entfernen; Padding auf 8 Byte) | v1.0 | [DOK, Q2] |
| `ATCF hhh` / `ATCM hhh` | ID-Filter / -Maske | v1.0 | [DOK, Q2] |
| `ATCFC0/1` | automatische Flow Control aus/an (Default an; nie beim Monitoring) | v1.0 | [DOK, Q2] |
| `ATST hh` | Timeout hh × 4 ms (CAN mit CTM5: ×20 ms), Default 32 (≈200 ms), `00` = Default | v1.0 | [DOK, Q2] |
| `ATMA` | Monitor all | v1.0 | [DOK, Q2] |
| `ATBI` | Bypass Initialization | v1.0 | [DOK, Q2] |
| `ATFC SH` / `ATFC SD` / `ATFC SM` | Flow-Control-Header / -Daten (1–5 Bytes) / -Modus (0 = auto, 1 = ID+Daten vom User, 2 = nur Daten vom User) | **v1.1** | [DOK, Q2] |
| `ATAT0/1/2` | Adaptive Timing aus/auto1/auto2 | **v1.2** | [DOK, Q2] |
| Protokolle B/C, `PP 2C/2D` | benutzerdefinierte CAN-Protokolle | v1.2 | [DOK, Q2] |
| `ATCRA hhh` | Receive-Filter auf genau eine ID | **v1.3** | [DOK, Q2] |
| `ATCRA` (ohne Argument, Reset) | Filter auf Default | **v1.4b** | [DOK, Q2] |
| `ATCRA` mit `X`-Wildcards | | **v2.0** | [DOK, Q2] |
| `ATD0/D1`, `ATV0/V1`, `ATJE`, `ATRA`, `AT@2/@3` | DLC-Anzeige, variable DLC, … | v1.3 | [DOK, Q2] |
| `ATCEA hh` / `ATCEA` | **CAN Extended Address** hh als 1. Datenbyte einfügen + Empfangsfilter auf Tester-Adresse im 1. Byte / ausschalten | **v1.4** | [DOK, Q2] |
| `ATPB xx yy` | Protokoll-B-Optionen/Baudrate ohne PP-Änderung | **v1.4** | [DOK, Q2] |
| `ATTA hh` | Tester-Adresse (wird von CEA-Empfangsfilter genutzt; Default F1) | v1.4 | [DOK, Q2] |
| `ATCSM0/1` | CAN Silent Monitoring aus/an | **v1.4b** | [DOK, Q2] |
| `ATCTM1/5` | CAN-Timer-Multiplikator | **v2.1** | [DOK, Q2] |
| „Response pending“ (`7F xx 78`) → Timeout automatisch 5 s | | **v2.1** | [DOK, Q2] |
| `ATCER hh` | abweichende Extended-Rx-Adresse | **v2.2** | [DOK, Q2] |
| „v1.5“ | „**Elm Electronics never made a v1.5**“ (ebenso keine v1.4a) | – | [DOK, Q2] |

Damit sind die Vermutungen aus der Aufgabenstellung bestätigt: `ATCEA` = v1.4, `ATFCSH/FCSD/FCSM` = v1.1, `ATCRA` = v1.3 [DOK, Q2].

### 4.1 Protokoll B (USER1) – PP 2C Bitbelegung [DOK, Q2]

`b7` TX-ID-Länge (0 = 29 bit, 1 = 11 bit) · `b6` Datenlänge (0 = fix 8 Byte, 1 = variable DLC) · `b5` RX-ID-Länge · `b4` Baudraten-Multiplikator 8/7 · `b3` reserviert · `b2..b0` Datenformat: `000` none, `001` ISO 15765-4, `010` SAE J1939. PP 2D = Baudraten-Divisor (Default 04 = 125 kbps).
→ `ATPB C1 01` = 11 bit, variable DLC, ISO-15765-Formatierung, Divisor 01 (= 500 kbps [WAHRSCHEINLICH, abgeleitet aus Default 04 = 125 kbps]); `ATPB C0 01` = dasselbe **ohne** Formatierung (Rohframes).

### 4.2 Extended Addressing laut Datenblatt (Abschnitt „Using CAN Extended Addresses“) [DOK, Q2]

Das Datenblatt-Beispiel entspricht strukturell exakt dem BMW-Schema (dort 7B0/7C0, Ziel 04, Tester F1):

```
>AT PB 81 0A        (Beispiel dort: 11 bit, ISO 15765, 50 kbps – für BMW NICHT übernehmen)
>AT CRA 7C0         nur Antworten von ID 7C0 annehmen
>AT SH 7B0          Request-ID
>AT FC SH 7B0       eigene Flow Control: Header ...
>AT FC SD 04 30 FF 00   ... Daten inkl. Zieladresse als 1. Byte
>AT FC SM1          FC-Modus 1 (User definiert ID + Daten)
>AT CEA 04          Zieladresse 04 als 1. Datenbyte einfügen
>AT SP B
>AT BI
```
Das Datenblatt sagt ausdrücklich, dass die Flow Control bei Extended Addressing „not quite the same as the one for OBD systems“ ist und man daher **eigene FC-Nachrichten definieren muss** [DOK, Q2]. Die CEA-Empfangslogik akzeptiert nur Frames, deren 1. Datenbyte die Tester-Adresse (Default F1, `ATTA`) ist, zusätzlich zu CF/CM/CRA [DOK, Q2]. „The ELM327 will only send Flow Control messages if the protocol’s data format is ISO15765-4“ [DOK, Q2].

---

## 5. BMW F-Serie: UDS über D-CAN mit Extended Addressing

### 5.1 Frame-Layout

```
Request  (Tester → DME):  ID 0x6F1  Daten: 12 | PCI | UDS-Payload ... | Padding
Response (DME → Tester):  ID 0x612  Daten: F1 | PCI | UDS-Payload ... | Padding
```
Beispiel (Kühlmitteltemperatur, G29/B-Motor, DID 0x4300): Request `6F1: 12 03 22 43 00 CC CC CC CC`, Response `612: F1 05 62 43 00 0D BA CC` [DOK, Q13 – Achtung: die dort angegebene Umrechnung ist arithmetisch inkonsistent; DID für MEVD17.2.5 [UNBEKANNT]].

Nutzdaten pro Frame mit Extended Addressing: SF max. 6 Byte UDS-Payload (8 − Adressbyte − PCI), FF 5 Byte, CF 6 Byte [DOK: EdiabasLib nutzt genau diese Werte – `dataLength <= 6` → SF, FF `telLen = 5`, CF `telLen > 6 → 6`, Q6].

### 5.2 Wie EdiabasLib (Deep OBD) es macht – `EdElmInterface.cs` [DOK, Q6]

**Init-Sequenz (`Elm327InitCommands`)**, jeweils mit `OK`-Prüfung; Einträge mit Versionsnummer sind optional (Fehlschlag wird nur geloggt):

```
ATD            Defaults
ATE0           Echo aus
ATSH6F1        Request-ID 0x6F1
ATCF600        Filter 0x600 ...
ATCM700        ... Maske 0x700  → alle IDs 0x600–0x6FF
ATPBC001       Protokoll B: 11 bit, variable DLC, KEINE Formatierung, Divisor 01
ATSPB          Protokoll B aktivieren
ATAT0          Adaptive Timing aus
ATSTFF         Timeout maximal
ATAL           Allow long
ATH1           Header an
ATS0           keine Leerzeichen
ATL0           keine Linefeeds
ATCSM0   (opt.) Silent Monitoring aus
ATCTM5   (opt.) Timer-Multiplikator 5
ATJE     (opt.) „used for fake ELM detection“
(auskommentiert: ATPP2COFF „reject fake elms“, ATPPS „some BT chips have a short buffer“)
```

**Erkennung von Adaptertyp/Klonen:**
- `AT@1` → enthält „CARLY-UNIVERSAL“ ⇒ Transporttyp *Carly*.
- `AT#1` (Hersteller-String; **kein** Befehl aus der ELM-Befehlsübersicht → herstellerspezifisch [WAHRSCHEINLICH]) → enthält „WGSOFT“ und `AT@1`-Version < 2.4 ⇒ Transporttyp *WgSoft*.
- `STI` → enthält „STN“ ⇒ OBDLink/STN, dann `STIX` (erweiterte Version) – nur geloggt.
- Nicht-Standard-Typen (Carly/WgSoft) bekommen zusätzlich `ATGB1` (Binärmodus, optional), `ATSH6F1`, `ATFCSH6F1`, `ATPBC101` (ISO-15765-Formatierung, variable DLC), `ATBI`.

**Standard-Transport (echte/kompatible ELM327) – ISO-TP komplett in Software:**
- Header wird pro Request nur bei Änderung gesetzt: `ATSH` + `0x600 | Quelladresse` (= 6F1).
- Senden: komplette 8-Byte-Rohframes als Hex-String, z. B. SF `12 03 22 xx xx 00 00 00`.
  Multi-Frame-Request: FF (`12 1L LL d d d d d`), dann **Warten auf FC** des Steuergeräts (CTS/Wait/BS/STmin auswerten), dann CFs (`12 2n …`) mit `Thread.Sleep(max(STmin, 50 ms))`.
- Timeout pro Frame: `ATSTFF` wenn Antwort erwartet, `ATST00` sonst.
- Empfang: Zeile = 3 Hex-Zeichen CAN-ID + Datenbytes (Regex `^[0-9a-fA-F]{3,19}$`, ungerade Länge). Kommt der Prompt `>` bevor die Nachricht komplett ist, schaltet EdiabasLib mit **`ATMA`** in den Monitor-Modus, um die restlichen CFs mitzulesen; Abbruch des Monitorings durch Senden von Leerzeichen (Antwort „STOPPED“).
- Flow Control beim Empfang **selbst gesendet**: `12 30 03 00 00 00 00 00` (BS = **3**, STmin = 0) – d. h. das Steuergerät pausiert nach je 3 CFs und wartet auf die nächste FC. Das drosselt die Datenrate für langsame ELM-Klone [DOK, Q6; Interpretation „drosselt“ WAHRSCHEINLICH].
- Zusammenbau: FF-Länge 12 bit, Sequenzzähler der CFs wird geprüft; Ergebnis wird als BMW-FAST-Telegramm (Länge/Ziel/Quelle/Checksumme) an EDIABAS gereicht.

**„Full transport“ (Carly/WgSoft) – ISO-TP im Adapter:** pro Request
```
ATSH6F1          (nur bei Wechsel)
ATFCSH6F1        (nur bei Wechsel)
ATFCSD<ZZ>30<BS><ST>   ZZ = Zieladresse, BS = 00, ST = 00 (Carly: 02)
ATCEA<ZZ>
ATFCSM1
<UDS-Payload als Hex>  (ELM fügt Adresse + PCI ein)
```
Funktionale Requests (Adressbyte mit `0xC0`-Flag) werden in Einzel-Requests an alle Adressen aus der GROBNAME-Tabelle aufgelöst.

### 5.3 Empfohlene Init-Sequenz (für eigenes Tool, nur lesend)

**Variante A – echter ELM327 ≥ v1.4 bzw. STN-Chip, ISO-TP-Empfang im Adapter („CEA-Modus“)**

```
ATZ              Reset (Antwort: Versionsstring, z. B. "ELM327 v1.5")      [DOK Semantik]
ATE0             Echo aus                                                    v1.0
ATL0             keine Linefeeds                                             v1.0
ATS1             Leerzeichen AN für Debug (später ATS0 für Geschwindigkeit)  v1.3
ATH1             Header an → CAN-ID + Adressbyte + PCI sichtbar              v1.0
ATAL             Allow long                                                  v1.0
ATI / AT@1       Version/Beschreibung protokollieren                         v1.0
STI              nur informativ: STN-Erkennung ("?" bei Nicht-STN)           [DOK Q3, Q6]
ATSP6            ISO 15765-4, 11 bit, 500 kbit/s                             v1.0
ATAT1            (Default) oder ATAT0 + großzügiges ATST                     v1.2
ATST64           Timeout 0x64 × 4 ms = 400 ms (ggf. höher)                   v1.0
--- optional: Bus-Check mit Standard-OBD, solange noch kein CEA aktiv ---
ATSH7DF
0100             → "7E8 06 41 00 xx xx xx xx ..."  (Bitmaske PIDs 01–20)
--- auf BMW-UDS zur DME (0x12) umschalten ---
ATSH6F1          Request-ID                                                  v1.0
ATCRA612         nur Antworten der DME (0x612)                               v1.3
ATCEA12          Zieladresse 0x12 als 1. Datenbyte, Rx-Filter auf F1         v1.4
ATFCSH6F1        FC-Header                                                   v1.1
ATFCSD12300000   FC-Daten: Adresse 12, CTS (30), BS 00, STmin 00             v1.1
ATFCSM1          FC-Modus 1 (User-definiert)                                 v1.1
22F190           Beispiel: UDS ReadDataByIdentifier VIN (DID F190)           (DID-Unterstützung [WAHRSCHEINLICH])
```
Zurück zu Standard-OBD: `ATCEA` (aus), `ATCRA` (Reset, v1.4b) oder `ATCF7E8`/`ATCM7F8`, `ATFCSM0`, `ATSH7DF` [DOK Semantik, Q2].

Hinweise:
- Alternativ zu `ATSP6` kann – wie bei EdiabasLib „full transport“ – `ATPBC101` + `ATSPB` + `ATBI` verwendet werden (variable DLC statt Padding auf 8 Byte) [DOK, Q6]. Ob die N13-DME gepaddete 8-Byte-Frames (Protokoll 6) akzeptiert: [WAHRSCHEINLICH ja, da ISO 15765-4 Padding vorsieht; am Auto zu prüfen].
- Bei Klonen, die `ATCEA`/`ATFCSD`/`ATFCSM` mit `?` quittieren → Variante B.
- Nur Single-Frame-Requests (≤ 6 Byte UDS-Payload) senden; das genügt für `22 hhhh` (3 Byte), `22 hhhh hhhh` (5 Byte), `19 02 FF` (3 Byte), `3E 00`, `10 01` [WAHRSCHEINLICH; Byte-Zählung].

**Variante B – „Rohframe-Modus“ nach EdiabasLib-Vorbild (für Klone ohne CEA)**: Init wie in 5.2, Frames inkl. Adressbyte und PCI selbst bauen, FC (`12 30 03 00 …`) selbst senden, restliche CFs mit `ATMA` mitlesen. Funktioniert nachweislich in Deep OBD [DOK, Q6], ist aber timing-kritisch (Latenz BLE + Prompt-Handling) [WAHRSCHEINLICH].

**Variante C – OBDLink (STN)**: zusätzlich/alternativ ST-Befehle [DOK, Q3]:
- `STCAF 1, <tt>` – Adressierungsformat 1 = „Extended with target address“ (Beispiel im FRPM: `STCAF 1, F2`).
- `STCFCPA <txid> [ext], <rxid> [ext]` – Flow-Control-Adresspaar (Beispiel: `STCFCPA 7E0 F2, 7E8 A2`); für BMW sinngemäß `STCFCPA 6F1 12, 612 F1` [WAHRSCHEINLICH – Syntax nach FRPM-Beispiel, nicht getestet].
- `STCSEGT1` / `STCSEGR1` – Segmentierung für **gesendete** bzw. empfangene Multi-Frame-Nachrichten.
- `STPX h:<id>, d:<hex>, x:<ext>, t:<timeout>, r:<count>` – beliebige Nachricht senden; `x` = ISO-15765-Extended-Address (überschreibt ATCEA); Max. Nachrichtengröße MX+/EX/STN21xx 4 KB, LX/MX/SX 2 KB.
- `STI` → z. B. „STN2232 v5.10.3“; OBDLink CX = STN2310.

### 5.4 Erwartetes Antwortformat (Multi-Frame, Header an)

Mit `ATH1`, `ATS1`, `ATCAF1`, `ATCEA12`, Request `22F190` (VIN, 17 Zeichen ⇒ 3 + 17 = 20 = 0x14 Byte UDS-Antwort), *illustrativ*:

```
612 F1 10 14 62 F1 90 57 42 41      FF: PCI 10 14 → Länge 0x014; 5 Nutzbytes (62 F1 90 'W' 'B' 'A' – 3 VIN-Bytes)
612 F1 21 xx xx xx xx xx xx         CF #1: 6 Nutzbytes
612 F1 22 xx xx xx xx xx xx         CF #2: 6 Nutzbytes
612 F1 23 xx xx xx [pad pad pad]    CF #3: 3 Nutzbytes + Padding
>
```
- Mit H1 werden die Bytes „wie empfangen“ gezeigt (inkl. Adressbyte F1, PCI, ggf. Padding); das Datenblatt-Beispiel zeigt genau dieses Bild (`7C0 F1 10 16 61 A2 01 02 05` / `7C0 F1 20 …`) [DOK, Q2].
- Mit `ATH0` (CAF1) stattdessen Längenzeile + Segmentnummern: `014` / `0: 62 F1 90 57 42 41` / `1: …` [DOK Format, Q2].
- Mit `ATS0` (wie EdiabasLib): `612F1101462F190574241` – erste 3 Hex-Zeichen = CAN-ID, Rest Bytes [DOK, Q6].
- Die vom ELM gesendete FC (`6F1 12 30 00 00 …`) erscheint normalerweise nicht in der Ausgabe; „FC:“-Zeilen nur beim Monitoring [DOK für Monitoring, Q2; sonst WAHRSCHEINLICH].
- Single-Frame-Antwort: `612 F1 05 62 hh hh dd dd …`; negative Antwort: `612 F1 03 7F 22 NRC` (z. B. NRC 31 requestOutOfRange) [WAHRSCHEINLICH, ISO 14229].
- Response Pending `7F 22 78`: ELM ≥ v2.1 verlängert das Timeout automatisch auf 5 s [DOK, Q2]; bei Klonen [UNBEKANNT] → eigenes Timeout-Handling.
- Reassemblierung im Host: pro Zeile ID (3 Hex), Byte 0 muss `F1` sein, dann PCI: `0L` SF (L Bytes), `1L LL` FF (12-bit-Länge, 5 Bytes), `2n` CF (Sequenz n = 1..F,0,…; max 6 Bytes) bis Länge erreicht; Padding verwerfen [DOK – identische Logik in EdiabasLib, Q6].
- Fehlertexte: `NO DATA`, `STOPPED`, `DATA ERROR`, `BUFFER FULL`, `CAN ERROR`, `?` (unbekannter Befehl) [DOK, Q2, Q6].

### 5.5 Bekannte Einschränkungen billiger ELM327-Klone

| Befund | Tag |
|---|---|
| Eine echte „v1.5“ gibt es nicht; Klone melden sich oft als „v1.5“ oder „v2.1“ | [DOK, Q2] |
| EdiabasLib empfiehlt ELM327 1.4b, 1.5 und **originale** 2.1 auf **PIC18F25K80** (ohne MCP2515); „There are fake PIC18F25K80 processors with version 1.5, these will not work!“; „ARM based adapters are in most cases not 100 % ELM327 compatible“ | [DOK, Q8, Q9] |
| EdiabasLib behandelt `ATCSM0`, `ATCTM5`, `ATJE` als optional (werden von vielen Adaptern nicht unterstützt) und nutzt `ATJE` zur Fake-Erkennung | [DOK, Q6] |
| Kommentar im Code: „some BT chips have a short buffer“ (ATPPS-Test schlägt fehl) | [DOK, Q6] |
| Klone ohne funktionierendes `ATCEA`/`ATFCSD`/`ATFCSM` | [WAHRSCHEINLICH – häufige Berichte; nicht für konkrete Modelle verifiziert] |
| Auswirkungen (a) **Multi-Frame lesen**: ohne korrekte FC (mit Adressbyte 12) sendet die DME nach dem FF keine CFs → nur erstes Frame / `NO DATA`; im Rohmodus drohen `BUFFER FULL` und verlorene CFs (BLE-Latenz) | [WAHRSCHEINLICH] |
| Auswirkungen (b) **Multi-Frame senden**: ELM327 segmentiert nicht selbst; Rohmodus mit manuellem FF/FC/CF nötig (EdiabasLib) bzw. STN `STCSEGT1` | EdiabasLib/STN [DOK, Q6, Q3]; „ELM segmentiert nicht“ [WAHRSCHEINLICH – Datenblatt beschreibt nur FC beim Empfang] |

Für das Vorhaben (nur Lesen) ist (a) kritisch, (b) praktisch irrelevant.

---

## 6. Standard-OBD-II (SAE J1979) am F20

### 6.1 Adressierung
- Funktionale Anfrage **0x7DF**, physikalisch 0x7E0…, Antwort Motor-SG **0x7E8** (zweites SG 7E9 …) [DOK, Q2].
- Init: `ATSP6` (oder `ATSP0` Auto-Suche), `ATH1`, Header Default 7DF [DOK, Q2].
- Unterstützte PIDs **müssen am Auto** aus den Bitmasken von `0100`, `0120`, `0140`, `0160` (… `01A0`/`01C0`) gelesen werden; Antwortformat z. B. `7E8 06 41 00 BE 3E B8 11` [DOK Format, Q2].

### 6.2 Typische Mode-01-PIDs und Umrechnung

Formeln nach python-OBD-Decodern [DOK, Q15b] (A,B,… = Datenbytes nach `41 PID`). **Unterstützung durch die N13/MEVD17.2.5-DME konnte nicht verifiziert werden** – es wurde kein belastbarer Scan gefunden (Bimmerpost blockiert Abruf, RaceChrono-Forum nicht ladbar) [UNBEKANNT].

| PID | Größe | Formel | Unterstützung N13 |
|---|---|---|---|
| 04 | Calculated load | A·100/255 % | [UNBEKANNT – WAHRSCHEINLICH ja, Pflicht-PID-typisch] |
| 05 | Kühlmitteltemp. | A − 40 °C | [UNBEKANNT – WAHRSCHEINLICH ja] |
| 06/07 | STFT/LTFT Bank 1 | (A − 128)·100/128 % | [UNBEKANNT] |
| 0B | Saugrohrdruck MAP | A kPa (max 255 kPa – Ladedruck > 155 kPa rel. abgeschnitten) | [UNBEKANNT] |
| 0C | Drehzahl | (256A + B)/4 rpm | [UNBEKANNT – WAHRSCHEINLICH ja] |
| 0D | Geschwindigkeit | A km/h | [UNBEKANNT – WAHRSCHEINLICH ja] |
| 0F | Ansauglufttemp. | A − 40 °C | [UNBEKANNT] |
| 10 | Luftmasse MAF | (256A + B)/100 g/s | [UNBEKANNT] |
| 11 | Drosselklappe | A·100/255 % | [UNBEKANNT] |
| 24 / 34 | Breitband-Lambda S1 (Spannung / Strom) | python-OBD: Spannung (256C + D)·8/65535 V; Strom (256C + D)/256 − 128 mA | [UNBEKANNT] |
| 42 | Steuergerätespannung | (256A + B)/1000 V | [UNBEKANNT] |
| 46 | Umgebungstemp. | A − 40 °C | [UNBEKANNT] |
| 5C | Öltemperatur | A − 40 °C | [UNBEKANNT – bei BMW oft **nicht** per Mode 01, Öltemp. üblicherweise über herstellerspezifische Dienste; Forenberichte, nicht N13-spezifisch, Q24] |
| 5E | Kraftstoffverbrauch | (256A + B)·0,05 L/h | [UNBEKANNT] |

### 6.3 BMW-spezifische Live-Werte (UDS 0x22 an DME 0x12)
- Apps wie BimmerLink / Deep OBD lesen Werte wie Öltemperatur oder Ladedruck nicht über J1979, sondern herstellerspezifisch an der DME [WAHRSCHEINLICH für BimmerLink (proprietär); DOK für Deep OBD, das EDIABAS-SGBD-Jobs nutzt, Q7].
- Deep OBD benötigt dafür die **„ECU files“** (≈ 2,5 GB, beim ersten Start extrahiert) – das sind EDIABAS-Beschreibungsdateien; daraus ergeben sich die Requests [DOK, Q7]. Rechtliche Weiterverwendbarkeit dieser Dateien / der darin enthaltenen DID-Tabellen: [UNBEKANNT] – es wurde **keine offene, explizit frei lizenzierte DID-Tabelle** für MEVD17.2.5 gefunden [UNBEKANNT].
- Öffentlich dokumentiertes Beispiel: DID **0x4300** Kühlmitteltemperatur (G29, B-Motor) [DOK, Q13], Gültigkeit für MEVD17.2.5 [UNBEKANNT].
- Normierte DIDs nach ISO 14229-1 (z. B. **F190** VIN, F18C Seriennummer, F187/F18A Teilenummer/Lieferant) sind die sichersten ersten Lesetests [WAHRSCHEINLICH].
- Eigenes, vorsichtiges Abtasten mit `0x22` liefert NRC `0x31` für nicht unterstützte DIDs [WAHRSCHEINLICH]; nur lesende Dienste verwenden (Whitelist `0x22`, `0x19`, `0x3E`, `0x10 01`); **niemals** `0x2E`, `0x2F`, `0x31`, `0x14`, `0x11`, `0x27`, `0x28`, `0x85`, `0x34–0x37`.

---

## 7. Bluetooth-Technologien im Vergleich (für den Mac)

| Technik | Am iPhone (BimmerCode) | Am Mac | Python-Weg | Tag |
|---|---|---|---|---|
| BLE (GATT-UART) | ja | CoreBluetooth; **nicht** in Systemeinstellungen koppeln, sondern direkt aus der App verbinden | `bleak` (direkt) oder `ble-serial` → PTY → `pyserial` | [DOK, Q16, Q19]; „nicht koppeln“ [WAHRSCHEINLICH] |
| Bluetooth Classic SPP | nur MFi (z. B. MX+) | Koppeln in Systemeinstellungen → `/dev/cu.<Name>` | `pyserial` 3.5 | `/dev/cu.*` & Stabilitätsprobleme [DOK als Anwenderberichte, Q25]; MX+ am Mac [WAHRSCHEINLICH] |
| WLAN (ELM327-Wi-Fi) | ja | Mac tritt dem Adapter-AP bei | TCP `192.168.0.10:35000` (häufigster Default; Varianten 192.168.0.11, 192.168.0.123) | [DOK, Q26]; pyserial `socket://`-URL [WAHRSCHEINLICH] |

---

## 8. macOS-Spezifika

### 8.1 BLE mit `bleak`
- Aktuelle Version: **bleak 3.1.0** (Upload 2026-11-07), `requires_python >= 3.10` [DOK, Q19b].
- CoreBluetooth kennt **keine MAC-Adressen**; bleak liefert eine **UUID** als `address`, die **nur auf dem Mac gilt, der gescannt hat** [DOK, Q19].
- **Datenschutz/Berechtigung**: macOS zeigt beim ersten Bluetooth-Zugriff einen Dialog; bei Ablehnung `BleakBluetoothNotAvailableError`, Rechte nur manuell unter *Systemeinstellungen → Datenschutz & Sicherheit → Bluetooth* änderbar; gebündelte Apps brauchen `NSBluetoothAlwaysUsageDescription` [DOK, Q19]. Beim Start aus dem Terminal erhält die **Terminal-App** (bzw. iTerm/VS Code) die Berechtigung [WAHRSCHEINLICH].
- `service_uuids`-Filter beim Scan nötig auf macOS ≥ 12.0 < 12.3; passives Scannen auf macOS nicht unterstützt [DOK, Q19].
- **Kein Pairing-API**: `pair()`/`unpair()` → `NotImplementedError`; macOS fragt beim ersten Zugriff auf geschützte Characteristic, Lese-/Schreibvorgänge können dabei lange blockieren → Timeouts großzügig wählen [DOK, Q19]. Relevanz: OBDLink CX verlangt Bonding (nur 5 min nach Power-on möglich) [DOK, Q4].
- `client.mtu_size` liefert die ATT-MTU; `write_gatt_char(..., response=True/False)` [DOK, Q19].
- Ein BLE-Peripheral akzeptiert typischerweise nur **eine** Central-Verbindung → iPhone-Bluetooth/BimmerCode vorher trennen [WAHRSCHEINLICH].

Skizze (API-Details gegen bleak 3.x prüfen – [WAHRSCHEINLICH]):
```python
import asyncio
from bleak import BleakScanner, BleakClient

async def dump():
    for d in await BleakScanner.discover(timeout=8.0):
        print(d.address, d.name)                     # address = macOS-UUID
    async with BleakClient("<UUID aus dem Scan>") as c:
        print("MTU", c.mtu_size)
        for s in c.services:
            print("S", s.uuid)
            for ch in s.characteristics:
                print("  C", ch.uuid, ch.properties)  # notify / write / write-without-response
asyncio.run(dump())
```

### 8.2 Bluetooth Classic SPP
- Nach dem Koppeln erscheint ein serielles Gerät `/dev/tty.<Name>` / `/dev/cu.<Name>`; Apple dokumentiert SPP als serielle Emulation, empfiehlt aber RFCOMM-API für neue Software [DOK als Suchtreffer-Auszug, Q25].
- Anwenderberichte zu Monterey/Sequoia: Port öffnet, aber keine Daten bis Neustart von `bluetoothd`; Wiederverbinden erst nach Entfernen/Neukoppeln [DOK als Forenberichte, Q25] – Zuverlässigkeit daher [UNBEKANNT] für den konkreten Adapter.
- `pyserial` 3.5 (seit 2020 unverändert) [DOK, Q19b].

### 8.3 WLAN-Adapter
- Häufigster Default `192.168.0.10:35000`, aber nicht universell [DOK, Q26]. Während der Verbindung hat der Mac meist kein Internet über WLAN [WAHRSCHEINLICH]. Für dieses Projekt nachrangig (Adapter ist Bluetooth).

---

## 9. Python-Bibliotheken – Eignung

| Bibliothek | Version (PyPI) | Befund | Tag |
|---|---|---|---|
| **python-OBD** (`obd`) | 0.7.3 (2025-04-07) | Öffnet den Port mit `serial.serial_for_url` → braucht serielles Gerät/URL; Init `ATZ`, `ATE0`, `ATH1`, `ATL0`, `AT RV`, `ATSP0`/`ATTP`; pro Command optionaler Header via `AT SH` | [DOK, Q15] |
| python-OBD + BMW-Extended-Addressing | – | CAN-Parser erwartet das PCI-Byte als **erstes** Datenbyte und interpretiert 11-bit-IDs nach 7Ex-Schema; ein Frame `612 F1 10 …` hätte PCI-Typ `0xF0` → „Dropping frame carrying unknown PCI frame type“. Kein `ATCEA`-Support ⇒ **für BMW-UDS ungeeignet**, für Mode 01 brauchbar | [DOK aus Quellcode, Q15] |
| python-OBD über BLE | – | nur über BLE-Serial-Brücke, z. B. **ble-serial 3.0.0**: erstellt auf Linux/macOS ein PTY mit Symlink `/tmp/ttyBLE`, Optionen `-d`, `-s`, `-r`, `-w`, `-m MTU` (Default 20), `--write-with-response`; auf macOS Geräte-ID statt MAC | [DOK, Q16]; Zusammenspiel mit python-OBD [WAHRSCHEINLICH] |
| **udsoncan** | 1.26.1 (2026-06-25) | Connections: `SocketConnection`, `IsoTPSocketConnection` (Linux-Kernel-ISO-TP), `PythonIsoTpConnection`/`V1`/`V2` (can-isotp), `J2534Connection`, `QueueConnection`, `FakeConnection`, `SyncAioIsotpConnection`; abstrakte `BaseConnection` mit `open`, `close`, `specific_send`, `specific_wait_frame`, `empty_rxqueue`, `is_open` ⇒ **eigene ELM327-Connection möglich** | [DOK, Q17] |
| **can-isotp** | 2.0.7 (2025-05-14) | arbeitet auf rohen CAN-Frames (python-can-Bus) | [WAHRSCHEINLICH] (Paketbeschreibung „Module enabling the IsoTP protocol“ [DOK, Q19b]) |
| **python-can** | 4.6.1 (2025-08-12) | Backend-Liste ohne ELM327 (u. a. socketcan, slcan, serial, pcan, kvaser, vector, gs_usb …) | [DOK, Q18] |
| SocketCAN auf macOS | – | nicht verfügbar (Linux-Kernel-Feature) | [WAHRSCHEINLICH] |

### 9.1 Pragmatische Architektur (Empfehlung)

```
┌───────────────────────────────────────────────┐
│ App / CLI (Live-Werte, Fehlerspeicher lesen)  │
├───────────────────────────────────────────────┤
│ UDS-Schicht (minimal selbst ODER udsoncan     │
│   mit eigener BaseConnection) + WHITELIST:    │
│   0x22, 0x19, 0x3E, 0x10 01 – sonst Exception │
├───────────────────────────────────────────────┤
│ BMW-ISO-TP-über-ELM: CEA-Modus (Variante A)   │
│   bzw. Rohframe-Modus (Variante B),           │
│   Reassemblierung der H1-Zeilen, NRC 0x78     │
├───────────────────────────────────────────────┤
│ ELM327-Zeilenprotokoll: Befehl + '\r',        │
│   lesen bis '>', Fehlertexte, Klon-Erkennung  │
├───────────────────────────────────────────────┤
│ Transport: BLE (bleak, notify→Puffer,         │
│   20-Byte-Writes) | Serial (pyserial) | TCP   │
└───────────────────────────────────────────────┘
```
Begründung: python-OBD kann kein Extended Addressing, udsoncan/can-isotp brauchen Roh-CAN; eine eigene dünne Schicht nach Vorbild von EdiabasLib ist überschaubar (≈ einige hundert Zeilen) und vollständig kontrollierbar [WAHRSCHEINLICH].

---

## 10. Offene Fragen (am echten Adapter / Auto zu klären)

1. **Adaptermodell**: Aufdruck/Verpackung; BLE-Advertising-Name, Hersteller-Daten, Service-UUIDs (Scan mit bleak). Erscheint er zusätzlich als Classic-Gerät?
2. **GATT-Profil**: Service-/Characteristic-UUIDs **mit Properties** (notify / write / write-without-response), Device-Information-Service (Firmware), Bonding/PIN nötig?
3. **MTU** am Mac (`mtu_size`) und ob Write-without-Response zuverlässig ist.
4. **Firmware-Identität**: `ATI`, `AT@1`, `AT@2`, `STI`/`STIX` (STN?), ggf. `AT#1`; Reaktion auf `ATPPS`, `ATJE`, `ATCSM0`, `ATCTM5`.
5. **Befehlsunterstützung**: Antwort `OK` vs. `?` auf `ATS0`, `ATAL`, `ATCRA612`, `ATCEA12`, `ATFCSH6F1`, `ATFCSD12300000`, `ATFCSM1`, `ATPBC101`, `ATSPB`, `ATBI`, `ATCAF0`, `ATMA`.
6. **Multi-Frame-Test**: `22F190` (VIN) an DME 0x12 – kommt die vollständige Antwort (FF + CFs)? Gibt es `BUFFER FULL`/Lücken?
7. **Standard-OBD**: Bitmasken `0100`/`0120`/`0140`/`0160` von 7E8; antworten weitere SGs?
8. **DME-Typ**: tatsächlich MEVD17.2.5? (z. B. über Identifikations-DIDs/SVK – konkrete DIDs [UNBEKANNT]).
9. **BMW-DIDs** für Öltemperatur, Ladedruck etc. an MEVD17.2.5 – Quelle mit klarer Lizenz suchen oder vorsichtig per NRC-Auswertung ermitteln.
10. Timing: benötigte `ATST`-Werte, Auftreten von Response Pending (`7F 22 78`).
11. Muss die iPhone-Verbindung (BimmerCode) getrennt werden, damit der Mac verbinden kann?
12. Bei MX+/Classic: erscheint `/dev/cu.*` stabil nach Neustart/Wiederverbinden?

---

## Quellen

- **[Q1]** BimmerCode – OBD Adapters (Reiter iOS/Android/Desktop): https://bimmercode.app/adapters/
- **[Q2]** ELM Electronics – ELM327 Datenblatt (ELM327DSK, Firmware bis v2.2), u. a. AT Command Summary, Descriptions, „Using CAN Extended Addresses“, „Altering Flow Control Messages“, „Multiline Responses“, „Response Pending Messages“, „Version History“: https://www.elmelectronics.com/wp-content/uploads/2017/01/ELM327DS.pdf
- **[Q2b]** ELM327-Datenblatt ältere Revision (ELM327DSI), Kopie: https://cdn.sparkfun.com/assets/learn_tutorials/8/3/ELM327DS.pdf
- **[Q3]** OBD Solutions – OBDLink Family Reference and Programming Manual (FRPM, Revision E, 28.03.2025): Gerätetabelle (STN1155 = LX, STN2255/2256 = MX+, STN2310 = CX), STPX, STCAF, STCFCPA, STCSEGT/STCSEGR, STI/STIX: https://www.scantool.net/scantool/downloads/234/stn1100-frpm.pdf
- **[Q4]** OBDLink CX Adapter Notes (GATT-Services FFF0/FFF1/FFF2, FEF5, 180A, MTU 247, Bonding, PIN 123456): https://support.obdlink.com/support/solutions/articles/43000746707-obdlink-cx-adapter-notes
- **[Q5]** EdiabasLib – `BtLeGattSppAndroid.cs` (UUID-Liste Deep OBD/Carly/WgSoft/vLinker, CCCD, 20-Byte-Writes): https://raw.githubusercontent.com/uholeschak/ediabaslib/master/EdiabasLib/EdiabasLib/BtLeGattSppAndroid.cs
- **[Q5b]** EdiabasLib – `BtLeGattSpp.cs` (Windows, Auto-Erkennung, WriteWithResponse): https://raw.githubusercontent.com/uholeschak/ediabaslib/master/EdiabasLib/EdiabasLib/BtLeGattSpp.cs
- **[Q6]** EdiabasLib – `EdElmInterface.cs` (Init-Sequenz, Klon-/Typerkennung, ISO-TP in Software, ATCEA/ATFCSD-Modus): https://raw.githubusercontent.com/uholeschak/ediabaslib/master/EdiabasLib/EdiabasLib/EdElmInterface.cs
- **[Q6b]** EdiabasLib – `EdBluetoothInterface.cs` (Einbindung BtLeGattSpp): https://raw.githubusercontent.com/uholeschak/ediabaslib/master/EdiabasLib/EdiabasLib/EdBluetoothInterface.cs
- **[Q7]** Deep OBD for BMW and VAG (ECU files ≈ 2,5 GB, Adapter): https://raw.githubusercontent.com/uholeschak/ediabaslib/master/docs/Deep_OBD_for_BMW_and_VAG.md
- **[Q8]** EdiabasLib – Supported adapter types: https://raw.githubusercontent.com/uholeschak/ediabaslib/master/docs/AdapterTypes.md
- **[Q9]** EdiabasLib – README (empfohlene ELM327-Versionen): https://raw.githubusercontent.com/uholeschak/ediabaslib/master/README.md
- **[Q10]** Vgate vLinker MC+ (BT 3.0 + BLE 4.0), manuals.plus: https://manuals.plus/asin/B0C2GT4KR3 (sowie https://manuals.plus/asin/B088LW211V)
- **[Q11]** Vgate-Forum / ABRP zu „vLinker MC-IOS“ (BLE) vs. „vLinker MC-Android“: https://forum.vgatemall.com/printthread.php?tid=6643 , https://abrp.upvoty.com/b/report-a-bug/vlinker-mc-android-option-not-showing-in-the-bluetooth-connections-list/
- **[Q12]** (Zusammenfassend) EdiabasLib-UUIDs siehe Q5; OBDLink-UUIDs siehe Q4
- **[Q13]** BMW D-CAN Enhanced PIDs (0x6F1/0x612, DME 0x12, DID 0x4300 Beispiel): https://thesecretingredient.neocities.org/bmw
- **[Q14]** Home Assistant Community – ESPHome-Komponente BLE ELM327 (18F0/2AF0/2AF1): https://community.home-assistant.io/t/custom-esphome-component-for-ble-elm327-obd2/1011293
- **[Q15]** python-OBD Quellcode: https://raw.githubusercontent.com/brendan-w/python-OBD/master/obd/elm327.py , https://raw.githubusercontent.com/brendan-w/python-OBD/master/obd/obd.py , https://raw.githubusercontent.com/brendan-w/python-OBD/master/obd/protocols/protocol_can.py
- **[Q15b]** python-OBD Commands/Decoders: https://raw.githubusercontent.com/brendan-w/python-OBD/master/obd/commands.py , https://raw.githubusercontent.com/brendan-w/python-OBD/master/obd/decoders.py , https://raw.githubusercontent.com/brendan-w/python-OBD/master/obd/UnitsAndScaling.py
- **[Q16]** ble-serial (PyPI-Beschreibung, v3.0.0): https://pypi.org/project/ble-serial/
- **[Q17]** udsoncan `connections.py`: https://raw.githubusercontent.com/pylessard/python-udsoncan/master/udsoncan/connections.py
- **[Q18]** python-can Backends: https://raw.githubusercontent.com/hardbyte/python-can/main/can/interfaces/__init__.py
- **[Q19]** bleak – macOS-Backend-Doku: https://bleak.readthedocs.io/en/latest/backends/macos.html
- **[Q19b]** PyPI JSON (Versionen/Upload-Daten): https://pypi.org/pypi/bleak/json , https://pypi.org/pypi/obd/json , https://pypi.org/pypi/udsoncan/json , https://pypi.org/pypi/can-isotp/json , https://pypi.org/pypi/ble-serial/json , https://pypi.org/pypi/python-can/json , https://pypi.org/pypi/pyserial/json
- **[Q20]** MEVD17.2.5 / N13 (Sekundärquellen): https://www.ecutesting.com/common-faults/bmw/mevd1725-ecu-fault/ , https://www.manualslib.com/manual/2957777/Bmw-N13.html
- **[Q21]** react-native-bluetooth-obd-manager 1.0.4 (`KNOWN_ELM327_TARGETS`): https://unpkg.com/react-native-bluetooth-obd-manager@1.0.4/lib/commonjs/constants/index.js
- **[Q22]** elm327-obdii (PyPI, v0.0.6): https://pypi.org/project/elm327-obdii/
- **[Q23]** Microchip – Transparent UART Service UUIDs: https://onlinedocs.microchip.com/oxy/GUID-26457D23-798C-47B0-9F40-C5DA6E995C6F-en-US-2/GUID-4346AC32-EFE5-4C3D-9D47-59BDC6EF7B7C.html , https://developerhelp.microchip.com/xwiki/bin/view/products/wireless-connectivity/ble/bm70/bm70-compact-demo-board-users-guide/transparent-uart
- **[Q24]** Öltemperatur bei BMW über Torque/Herstellerdienste (nicht N13-spezifisch, Forenberichte): https://torque-bhp.com/community/main-forum/bmw-e90-oil-temp-readings/ , https://n-cars.net/forums/threads/i-finally-found-the-oil-temperature-pid.8469/page-2
- **[Q25]** macOS Bluetooth-Seriell (Anwenderberichte/Apple-Doku): https://community.st.com/t5/others-stm32-mcus-related/rn4678-macos-rfcomm-spp-reconnect-port-opens-but-no-data-until/td-p/838349 , https://forum.arduino.cc/t/macos-monterey-cant-reconnect-to-hc-05-bluetooth-without-remove-re-add/1016587 , https://dsnutter.github.io/setting-up-mac-with-minicom-elm32x-obd-II-device , https://developer.apple.com/mac/library/documentation/DeviceDrivers/Conceptual/Bluetooth/BT_Develop_BT_Apps/BT_Develop_BT_Apps.html
- **[Q26]** Car Scanner – WLAN-Konfiguration (192.168.0.10:35000) und Varianten: https://www.carscanner.info/wifi/ , https://www.elektroda.com/news/news3886733.html , https://apps.apple.com/us/app/scanmaster-for-elm327-obd-2/id1323914943

Nicht abrufbar (Bot-Schutz / Ladefehler): f30.bimmerpost.com (Thread zu PIDs), racechrono.com/forum (Thread „Help with custom PID's over OBD“), api.github.com (Codesuche). Die GitHub-Repos SwiftOBD2 / AndrOBD / ELMduino wurden aus Zeitgründen nicht ausgewertet; die BLE-UUIDs wurden stattdessen gegen EdiabasLib und die offizielle OBDLink-Doku verifiziert.
