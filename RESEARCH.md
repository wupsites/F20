# RESEARCH – Zusammenfassung der technischen Grundlagenforschung

Detailberichte mit Einzelnachweisen und Quellenlisten: `docs/research/raw/`.
Nachweisstufen: **Nachgewiesen** (am eigenen Fahrzeug/Backup) · **Dokumentiert** (Quelle, nicht am Fahrzeug
getestet) · **Wahrscheinlich** · **Experimentell** · **Nicht kompatibel** · **Unbekannt**.

| Bericht | Inhalt |
|---|---|
| `01_architektur_protokoll.md` | F20-Bussysteme, ECU-Adressen, UDS über D-CAN, Identifikations-DIDs, SVK, Codierdaten-Lesen, Signatur |
| `02_dateiformate_opensource.md` | BimmerCode-.cod, NCD (S-Record), CAFD, FA, SGBM-ID, Open-Source-Projekte inkl. Lizenzen |
| `03_adapter_kommunikation.md` | BimmerCode-Adapter, BLE-UUIDs, ELM327-Sequenzen, Klone, macOS, Bibliotheken |
| `04_hu_entry_kombi.{md,json}` | iDrive (HU_ENTRY) und Kombi: Codieroptionen, versteckte Menüs |
| `05_karosserie_komfort_antrieb.{md,json}` | FEM/REM/IHKA/ICM/DSC/DME/ACSM: Licht, Komfort, Fahrmodi, Rechtslage |
| `06_idrive_hu_entry_expert.{md,json}` | Expertenparameter der eigenen HU_ENTRY (aus dem Backup) – Wirkung/Nachweis |
| `07_kombi_expert.{md,json}` | Expertenparameter des eigenen Kombis – Wirkung/Nachweis |

## Kernergebnisse

### Architektur & Protokoll (Bericht 01)
* ZGW (Gateway) ist im FEM integriert (Adresse 0x10), FEM_BODY 0x40, REM 0x72 (PDC integriert), KOMBI 0x60,
  HU_ENTRY 0x63, DME 0x12 (MEVD17.2.5 für N13), DSC 0x29, EPS 0x30, ICM 0x1C, ACSM 0x01, IHKA 0x78, ZBE 0x67,
  FZD 0x56 – **Dokumentiert** (EdiabasLib/ISTA-abgeleitete Listen); 7 davon **Nachgewiesen** über Backups.
* UDS über D-CAN: 500 kBit/s, 11 Bit, ISO-TP Extended Addressing (Tester 0x6F1, ECU antwortet 0x600+Adr. mit
  0xF1), DLC 8 mit 0x00-Padding, funktional 0xDF – **Dokumentiert**.
* Lesend nutzbar: F190 FIN, F150 SGBD-Index (3 Byte), F101 SVK, F18A/B/C, F186, 100B I-Stufe, 37FE CPS,
  3F06 Fahrzeugauftrag (ZGW), 1700 km-Stand (FEM), 3F0E…3F24 SG-Listen je Bus (ZGW), 19 02 0C Fehlerspeicher.
* SVK-Layout: 4 Byte Kopf + 13 Byte Kopfblock (Programmierdatum BCD, km/10) + n × 8 Byte SGBM-IDs.
* Codierdaten sind **signiert** (Fehlerort „Signatur für Daten ungültig“; Signaturblock in Backups
  **nachgewiesen**) → eigenes Schreiben ist ohne Signaturkenntnis unmöglich bzw. riskant.

### Dateiformate & Open Source (Bericht 02)
* `.cod` (iOS) = NSKeyedArchiver-bplist mit FIN, `codingECU` (identifier, address, CAFD-Liste) und
  `codingData` (CAFDIdentifier, Datenblöcke) – **Nachgewiesen** an 22 eigenen Dateien.
* `0F1820`/`0F1650` sind BimmerCodes SG-Kennungen (Format wie SGBD-Index F150) → 0F1820 = HU_ENTRY,
  0F1650 = ICM – **Nachgewiesen**.
* NCD = Motorola-S-Record (S0 mit CAFD-ID/Version, S2 mit `DID<<8|Offset`) – **Dokumentiert** (E-Sys-Handbuch).
* CAFD-Dateien sind BMW-Eigentum (PSdZData, verschlüsselt); öffentlich: OpenCAFDMap (Code MIT, `names/` CC0 –
  nur G-Serie; `definitions/untrimmed` = BMW-Namen, Rechtslage unklar, lokal mit Freigabe genutzt).
* „OpenCAFDMap“ existiert (MIT, aktiv); „BIT-Tuning“ konnte nicht als Open-Source-Projekt gefunden werden.
  EdiabasLib GPL-3.0, python-OBD GPL-2.0, udsoncan/can-isotp/bleak/mcp MIT, python-can LGPL-3.0.

### Adapter (Bericht 03) → ADAPTER_COMPATIBILITY.md
### Codierungen (Berichte 04–07) → CODING_DATABASE.md
* BimmerCodes offizielle F20-Liste enthält **keine** HU_ENTRY-Optionen; viele iDrive-Funktionen setzen NBT voraus.
* Die eigene HU_ENTRY-CAFD enthält jedoch zahlreiche Expertenparameter (u. a. `EFF_DYN_SPORT_CID`,
  `SERVICE_MENUE`, `ENTWICKLER_MENUE`, `HIST_GAS_CONSUMP`, `MACRO_FDS`, Bluetooth-Parameter) → Bericht 06.
* Rechtslage DE: US-Sidemarker, Nebelscheinwerfer mit Standlicht, veränderte Notbremssignal-Schwellen,
  Video während der Fahrt, Tachokorrektur nach unten → unzulässig.

## Was über BimmerCode hinausgeht (Bewertung)
| Möglichkeit | Status |
|---|---|
| Änderungshistorie aus Backups mit Parameternamen | **Nachgewiesen** |
| Klartext-Gesamtcodierung aller SG, Katalog-Abgleich mit aktuellen Werten | **Nachgewiesen** (Namen: Dokumentiert) |
| Fehlerspeicher aller SG, SVK/I-Stufe, Fahrzeugauftrag (SA-Codes), km-Abgleich KOMBI/FEM, PDC-Rohwerte (REM D645–D64D) | **Dokumentiert**, Realtest ausstehend |
| OBD-Livedaten mit Verbrauchs-/Ladedruckschätzung | Simulator ✔, Realtest ausstehend |
| Eigenes Schreiben/Codieren, Flashen, VO-Codierung, FSC, eigene HU-Apps | **Nicht möglich/ nicht vorgesehen** (Signatur, Adapter, Recht, kein Nachweis) |
