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

### Fahrzeug B – FREMDFAHRZEUG: BMW 1er E-Serie eines Kollegen (`WBA…4254`) – AUSGESCHLOSSEN

> Laut Besitzer (2026-11-24) Testbackups am Auto eines Kollegen. Das Fahrzeug ist in
> `$F20_HOME/vehicle.local.json → excluded_vins` eingetragen und wird von allen Auswertungen
> (Atlas, Katalog-Abgleich, MCP-Server) ignoriert. Die Angaben unten dienen nur der Nachvollziehbarkeit.

| SG-Name (BimmerCode) | Adresse | Backups | Änderung |
|---|---|---|---|
| `CAS3C08` | 0x40 | 2 (identisch) | keine |
| `FRM2_E89C09` | 0x72 | 1 | – |
| `KMBI_PL2C08` | 0x60 | 2 | Block 0x3B02: Byte 5 und Byte 8 jeweils `0x20 → 0x00` (je Bit 5 gelöscht) |
| `MRS5CDC21` | 0x01 | 2 (identisch) | keine |

(Frühere Vermutung „E89 Z4“ anhand des FRM-Variantennamens ist durch die Angabe des Besitzers überholt:
E-Serie 1er.) Fahrzeug B wird im Weiteren nicht betrachtet.

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

### Deutung – mit Parameternamen entschlüsselt (Stand 2026-11-24)

Entschlüsselt mit lokal abgelegten OpenCAFDMap-Namenstabellen (Freigabe des Besitzers; nicht im Repository).
Ein Name gilt als belastbar, wenn alle plausiblen Layout-Kandidaten des Blocks an dieser Stelle denselben
Parameter führen (Verfahren: `src/f20/backup/layouts.py`). Nachweisstatus: **Dokumentiert** (Namenstabelle) +
**Nachgewiesen** (Bit-Änderung im eigenen Backup).

| SG | Parameter | vorher → nachher | Stand im letzten Backup |
|---|---|---|---|
| FEM_BODY | `TCM_MSA_DEFAULT_OFF` (Start-Stopp standardmäßig aus) | nicht_aktiv → aktiv | zurückgesetzt |
| KOMBI | `FDS_MENUE` | kein_menue → menue_1 | zurückgesetzt |
| KOMBI | `BC_DIGITAL_V` (Digitaltacho im BC) | nicht_aktiv → aktiv | zurückgesetzt |
| KOMBI | `FDS_MENUE_TEXT/SIGNAL_1…4` (Fahrmodus-Menüliste) | menue_4 → menue_3 | zurückgesetzt |
| ICM | `IcmKod_B_Sportlenkung` | nicht_verbaut → **verbaut** | **geändert** |
| ICM | `IcmKod_B_InitEco` | nicht_verbaut → **verbaut** | **geändert** |
| IHKA | `MEMORY_OFF` (Klima-Aus-Zustand merken) | NICHT_AKTIV → AKTIV | **geändert** |
| HU_ENTRY | `MACRO_FDS` | only_popup → popup_and_config | **geändert** |
| HU_ENTRY | `CDMM_BLUETOOTH_AUDIO`, `BT_MODUL_ON_OFF`, `AUDIO_PLAYER_ON_OFF`, `BASIC_VR_ON_OFF` | nicht_aktiv → aktiv | **geändert** |
| HU_ENTRY | Byte 5 Bit 2 (`CDMM_BT_DATABASE` bzw. unbelegt – Layouts uneinig) | 0 → 1 | **geändert** |

Interpretation: Getestet wurden Start-Stopp-Voreinstellung, Digitaltacho und Fahrmodus-Menü im Kombi,
konfigurierbarer Fahrmodus (HU `MACRO_FDS` + ICM), Start in ECO PRO (ICM `IcmKod_B_InitEco`),
Klima-Gedächtnis und **Bluetooth-Audio/Sprachsteuerung am iDrive**.

**Wichtig:** Laut Besitzer wurde danach alles zurückgesetzt. Die *letzten vorhandenen* Backups von
HU_ENTRY, IHKA und **ICM** zeigen jedoch den geänderten Zustand. Falls ohne neues Backup zurückgesetzt wurde,
ist das hier nicht sichtbar. **Empfehlung:** In BimmerCode je ein frisches Backup von ICM, HU_ENTRY und IHKA
erstellen und importieren. Besonders `IcmKod_B_Sportlenkung = verbaut` ohne verbaute Sportlenkung (Hardware)
sollte im sicherheitsrelevanten ICM nicht stehen bleiben; Wiederherstellung über das ICM-Backup vom
27.06.2025 15:51 (Original) in BimmerCode.

## 4. Vollständige Klartext-Codierung (Parameter-Atlas)

Für alle 7 Steuergeräte wurde die gesamte aktuelle Codierung im Klartext erzeugt
(`private/PARAMETER_ATLAS.md`, nur lokal, per `.gitignore` ausgeschlossen). Plausibilitätsprüfung der
Layoutwahl an bekannten Fahrzeugmerkmalen in der HU-Codierung: `BAUREIHE=F20`, `COUNTRY=deutschland`,
`GETRIEBETYP=handschalter`, `PDC_SENSOR_HINTEN=4_sensoren`, `PDC_SENSOR_VORN=kein_sensor`,
`DISPLAY_VARIANTE=schmales_display`, `ZYLINDERZAHL=4_zylinder`, `TYP_LENKUNG=linkslenker` – alle stimmig.

Abdeckung: Für HU_ENTRY, KOMBI, IHKA, REM, ACSM und die meisten FEM-Blöcke liegen passende Layouts vor.
Für einige FEM-Blöcke (0x3020, 0x3040, 0x3050, 0x3053, 0x3060) enthält die Tabelle das Layout der
Version 004_228_010 nicht vollständig; dort werden Namen nur per Feldabgleich ergänzt (markiert) oder fehlen.

Katalog-Abgleich (`private/catalog_crossref.json`): 45 Katalogoptionen im eigenen SG **vorhanden** (mit
aktuellem Wert), 8 nachweislich **nicht vorhanden** (u. a. Kombi-Startlogo), 40 **unbekannt**
(Namenstabelle für die Version unvollständig → im BimmerCode-Expertenmodus prüfen).

## 5. Reproduktion

```bash
f20 backup import <Ordner mit .cod>     # Tresor + Analyse
f20 backup timeline                     # Änderungsverlauf
f20 backup compare <id_a> <id_b>        # Byte/Bit-Vergleich
```
