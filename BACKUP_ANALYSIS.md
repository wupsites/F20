# BACKUP_ANALYSIS – Forensische Analyse der BimmerCode-Backups

Stand: 2026-11-24 · Werkzeug: `f20.backup` (Parser, Tresor, Diff) · Originale unverändert (SHA-256 vor/nach Analyse identisch)

> **Datenschutz:** Dieses Repository ist öffentlich. Fahrgestellnummern sind hier maskiert
> (`WBA…8606`, `WBA…4254`). Die Backups selbst liegen ausschließlich lokal im Tresor
> `$F20_HOME/vault/originals/` (schreibgeschützt, benannt nach SHA-256) und sind per `.gitignore`
> vom Repository ausgeschlossen.

## 1. Dateiformat (nachgewiesen)

| Merkmal | Befund | Nachweis |
|---|---|---|
| Container | Binäre Apple Property List `bplist00`, Archiver `NSKeyedArchiver` | **Nachgewiesen** (alle 22 Dateien) |
| Verschlüsselung | keine | **Nachgewiesen** |
| Wurzelobjekt | Klasse `CodingSession` mit `VIN`, `codingECU`, `codingData` | **Nachgewiesen** |
| F-Serie | `codingECU` = `CodingECU` mit `identifier` (z. B. `0F1820`), `address` (Diagnoseadresse), `identifiers.CAFD`/`BTLD` (`CodingECUIdentifier`: identifier, main/sub/patchVersion) | **Nachgewiesen** |
| E-Serie | `codingECU` = `ESeriesCodingECU` mit `data`, `series`, `address` (kein CAFD) | **Nachgewiesen** |
| Codierdaten | `codingData.mutableCodingDataBlocks` = Liste `CodingDataBlock {blockAddress, data}`; F-Serie: Blockadressen 0x3000 ff. (= UDS-DIDs der Codierdaten) | **Nachgewiesen** |
| CAFD-Kennung | `codingData.CAFDIdentifier` = 14 Hex-Zeichen: 8 CAFD-ID + 3 × 2 Hex Version | **Nachgewiesen** |
| Dateiname | `<SG-Kennung>-<FIN>-<Unix-Zeit>.cod` – die Zeit steht nur im Namen, nicht im Inhalt | **Nachgewiesen** |
| Signaturblock | je SG ein Block mit Kopf `00 00 00 20` + 128 Byte (KOMBI: `00 00 00 10` + 64 Byte), ändert sich bei *jedem* Schreibvorgang → Codierdaten sind signiert | **Nachgewiesen**; Deutung als NCD-Signatur: Dokumentiert (E-Sys-Handbuch, nbt-coding) |

Quellen Formatbeschreibung: OpenCAFDMap `ocm/cod_import.py`, `ocm/bc_tool.py` (MIT, geprüft 2026-11-24);
siehe `docs/research/raw/02_dateiformate_opensource.md`.

## 2. Inventar und Fahrzeugtrennung

22 Dateien → **17 inhaltlich verschiedene** Backups (5 Dateien sind byteidentische Wiederholungen).
Die Trennung erfolgt über die FIN im Inhalt (`VIN`) **und** im Dateinamen – beide stimmen bei allen Dateien überein
→ Zuordnung **nachgewiesen**.

### Fahrzeug A – dein BMW 116i F20 (`WBA…8606`), Backups vom 27./28.06.2025

| Kennung | Adresse | Steuergerät | CAFD | Blöcke | Backups |
|---|---|---|---|---|---|
| `0F16B0` | 0x40 | **FEM_BODY** | CAFD_00000794_004_228_010 | 57 | 3 (1 Duplikat) |
| `0F16C0` | 0x72 | **REM** | CAFD_000007A1_005_028_006 | 29 | 2 (identisch) |
| `0F1630` | 0x60 | **KOMBI** | CAFD_00000760_006_000_052 | 14 | 3 (1 Duplikat) |
| `0F1650` | 0x1C | **ICM** (Fahrdynamik) | CAFD_0000067B_002_003_139 | 3 | 2 |
| `0F17C0` | 0x78 | **IHKA** (Klimaautomatik) | CAFD_00000A3F_005_001_013 | 5 | 2 |
| `0F1820` | 0x63 | **HU_ENTRY** | CAFD_000000F9_007_007_001 | 8 | 2 |
| `0F16E0` | 0x01 | **ACSM** (Airbag) | CAFD_00000911_003_001_001 | 39 | 1 |

Zuordnung Kennung → Steuergerät über die im Backup gespeicherte Diagnoseadresse und die dokumentierten
F20-Adressen (RESEARCH.md): **nachgewiesen** für die Adresse, Steuergerätename **dokumentiert**.

Damit beantwortet: **`0F1820` = HU_ENTRY** (CAFD_000000F9_007_007_001 bestätigt) und **`0F1650` = ICM**.
Neu nachgewiesen: Das Fahrzeug hat eine **Klimaautomatik (IHKA)**.
Hinweis: Im HU-Block 0x3003 steht der Klartext `BMW <letzte 5 FIN-Ziffern>` – typisch für den
Bluetooth-Gerätenamen der Freisprechfunktion (Deutung: wahrscheinlich, nicht nachgewiesen).

### Fahrzeug B – zweites Fahrzeug, E-Serie (`WBA…4254`), Backups 16.03.2026 und 25.05.2026

| SG-Name (BimmerCode) | Adresse | Backups | Änderung |
|---|---|---|---|
| `CAS3C08` | 0x40 | 2 (identisch) | keine |
| `FRM2_E89C09` | 0x72 | 1 | – |
| `KMBI_PL2C08` | 0x60 | 2 | Block 0x3B02: Byte 5 und Byte 8 jeweils `0x20 → 0x00` (je Bit 5 gelöscht) |
| `MRS5CDC21` | 0x01 | 2 (identisch) | keine |

Die FRM-Variante `FRM2_E89…` deutet auf einen **E89 (Z4)** hin (wahrscheinlich, nicht nachgewiesen).
Fahrzeug B wird im Weiteren nicht betrachtet.

## 3. Änderungshistorie Fahrzeug A (Byte-/Bit-Ebene)

Signaturblöcke (FEM 0x37FD, KOMBI 0x37F1, ICM 0x3002, IHKA 0x3004, HU 0x3401) ändern sich bei jedem
Schreiben und sind unten ausgeblendet. Zeiten in UTC.

| SG | Zeitraum | Block | Byte | vorher → nachher | Bits | Stand heute |
|---|---|---|---|---|---|---|
| FEM_BODY | 27.06. 15:20 → 28.06. 03:22 | 0x3023 | 0 | `00 → 10` | Bit 4 gesetzt | **zurückgesetzt** 03:29 (wieder Original) |
| KOMBI | 27.06. 15:53 → 28.06. 03:33 | 0x3000 | 0 / 1 | `0A → 1A` / `48 → 4A` | Bit 4 / Bit 1 | **zurückgesetzt** 03:38 (wieder Original) |
| KOMBI | 27.06. 15:53 → 28.06. 03:33 | 0x300C | 0–3 | `42 34 76 FF → 51 42 34 76` | Liste um Eintrag `51` vorne erweitert | **zurückgesetzt** 03:38 |
| ICM | 27.06. 15:51 → 28.06. 03:29 | 0x3000 | 28 / 36 | `00 → 01` / `00 → 08` | Bit 0 / Bit 3 | **aktiv** (kein späteres Backup) |
| IHKA | 27.06. 15:49 → 28.06. 03:30 | 0x3002 | 0 | `00 → 02` | Bit 1 | **aktiv** |
| HU_ENTRY | 27.06. 15:55 → 28.06. 03:25 | 0x3000 | 7 | `5B → 6B` | Bit 4 gelöscht, Bit 5 gesetzt | **aktiv** |
| HU_ENTRY | 27.06. 15:55 → 28.06. 03:25 | 0x3003 | 1 / 5 / 6 | `00 → 40` / `18 → 9C` / `10 → 13` | Bit 6 / Bits 2,7 / Bits 0,1 | **aktiv** |
| REM | 27.06. 15:58 → 28.06. 03:36 | – | – | identisch | – | unverändert |

### Deutung (Hypothesen – noch NICHT nachgewiesen)

| Änderung | Mögliche Bedeutung | Begründung | Status |
|---|---|---|---|
| FEM 0x3023 Byte 0 Bit 4 | Start-Stopp-Einstellung (`TCM_MSA_MEMORY` / `TCM_MSA_DEFAULT_OFF`) | Katalog: beide MSA-Parameter liegen in FEM-Block 3023 | Hypothese |
| KOMBI 0x3000 + 0x300C | Digitaltacho (`BC_DIGITAL_V`, dokumentiert in Block 3000) bzw. BC-Anzeigenliste | Block passt; Listenverschiebung in 0x300C passt zu „Anzeige hinzufügen“ | Hypothese |
| ICM 0x3000 | Fahrmodus-/SPORT+-bezogene Einstellung | Katalog: SPORT+ Teil 1 und Fahrmodus-Optionen liegen im ICM | Hypothese – **sicherheitsrelevant** |
| IHKA 0x3002 Byte 0 | Klima-Gedächtnis (AC/Umluft/AUTO) | IHKA-Optionen laut Katalog | Hypothese |
| HU 0x3000 Byte 7 | z. B. Sportanzeigen (`EFF_DYN_SPORT_CID`, dokumentiert in Block 3000) | Block passt | Hypothese |

**Achtung ICM:** Im Fahrdynamik-Steuergerät sind 2 Bits geändert und nicht zurückgesetzt, während die
KOMBI-Änderung zurückgenommen wurde. Falls es sich um SPORT+ handelte (benötigt laut Quellen KOMBI- und
ICM-Teil), könnte ein inkonsistenter Zustand vorliegen. Empfehlung: genaue Bedeutung klären
(siehe Abschnitt 4) – im Zweifel ICM mit BimmerCode auf das Backup vom 27.06.2025 15:51 zurücksetzen.

## 4. Exakte Entschlüsselung – Optionen

1. **Erinnerung/Lernmodus (rechtlich unbedenklich):** Du nennst, was du am 27./28.06.2025 in BimmerCode
   geändert hast → `f20 backup learn` ordnet die Bits dauerhaft zu.
2. **OpenCAFDMap-Namenstabellen:** Für **alle 7** CAFD-Versionen existieren öffentliche Tabellen
   (`definitions/untrimmed/<CAFD>.tsv.gz`, geprüft 2026-11-24). Sie enthalten BMWs eigene Parameternamen
   aus älteren PSdZData-Ständen. **Rechtslage unklar** (Herkunft BMW-Daten). Nutzung nur nach deiner
   Entscheidung, nur lokal, ohne Einchecken ins Repository.
3. **Am Fahrzeug:** Expertenmodus in BimmerCode zeigt Parameternamen und aktuelle Werte je Block –
   Abgleich mit den hier gefundenen Byte-Positionen.

## 5. Reproduktion

```bash
f20 backup import <Ordner mit .cod>     # Tresor + Analyse
f20 backup timeline                     # Änderungsverlauf
f20 backup compare <id_a> <id_b>        # Byte/Bit-Vergleich
```
