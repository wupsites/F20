# 02 – Dateiformate (BimmerCode `.cod`, NCD, CAFD, FDL, FA) und Open-Source-Ökosystem

**Stand der Recherche:** 2026-11-24
**Kontext:** Privates, nicht-kommerzielles Read-only-Analysewerkzeug für einen BMW 116i F20 (Bauzeit 01/2012, Head-Unit HU_ENTRY) und die eigenen BimmerCode-Backups.
**Methode:** Websuche, Abruf von Projektseiten, PyPI-JSON-API sowie direktes Lesen von Quellcode über `raw.githubusercontent.com`. Mehrere Foren (bimmerfest über „tollbit“, bimmerpost mit „Verifying Access…“) ließen sich **nicht** abrufen. Aussagen aus diesen Foren stammen deshalb nur aus Such-Snippets und sind entsprechend markiert.

**Evidenz-Tags**
- **[DOK]**: in einer zitierten Quelle dokumentiert (Quelle im Text oder in „Quellen“).
- **[WAHRSCHEINLICH]**: aus Quellen abgeleitet oder plausibel, aber nicht direkt belegt.
- **[UNBEKANNT]**: nicht verifizierbar.

> Hinweis: Dieser Bericht ist keine Rechtsberatung. Die Aussagen zum Rechtsstatus beschreiben nur, was die Quellen sagen, und eine vorsichtige Einschätzung.

---

## 0. Kurzfazit

1. **Das `.cod`-Format ist öffentlich (durch Reverse Engineering) dokumentiert.** Das Open-Source-Projekt **OpenCAFDMap / OpenLauncher** (MIT) liest und schreibt BimmerCode-Backups. Laut seinem Code ist eine iOS-`.cod`-Datei eine **binäre Property-List (`bplist00`) im NSKeyedArchiver-Format**, die eine BimmerCode-„CodingSession“ enthält. Darin stehen VIN, ECU-Identifier, ECU-Diagnoseadresse, die CAFD-ID und -Version(en) sowie die **rohen Codierdaten-Blöcke pro Datagroup-DID** (z. B. `blockAddress` 12288 = 0x3000), einschließlich des SYSTEM-/Signaturblocks. **Parameternamen sind nicht enthalten.** Eine Verschlüsselung ist nicht erkennbar: Der Code liest die Datei direkt mit `plistlib`. [DOK]
2. **Dateiname iOS:** `<ECU>-<VIN>-<Unix-Zeit>.cod`. **Android** nutzt ein anderes Format: `<VIN>_<ECU>.dat` als Java-Serialisierung. [DOK] Der `<ECU>`-Teil (beim Besitzer `0F1820`, `0F1650`) ist BimmerCodes `codingECU.identifier`. [DOK] Dass dies der **3-Byte-SGBD-Index aus UDS-DID 0xF150** ist, ist **[WAHRSCHEINLICH]**, aber nicht direkt belegt. Für die Hypothese sprechen: Laut BMW-SGBD-Dokumentation liefert F150 den „SGBD-Index … zur Erkennung der SG-Variante“, und eine öffentliche ELM327-Beispielsitzung liefert auf `22F150` genau 3 Bytes `0F25F0`, also dasselbe Muster `0Fxxxx`.
3. **NCD (Netto-Codierdaten) ist laut E-Sys-Handbuch eine Textdatei im Motorola-S-Record-Format.** [DOK] Der Beispielauszug im Handbuch ist prüfsummenkorrekt. Er zeigt einen S0-Header mit CAFD-ID und Version (7 Bytes), S2-Records mit der 24-Bit-Adresse `DID<<8 | Offset` und max. 32 Datenbytes pro Zeile sowie einen Signatur-Datagroup. [DOK/WAHRSCHEINLICH, Details unten]
4. **CAFD-Dateien sind proprietäre BMW-Daten** (PSdZData). Sie liegen verschlüsselt vor, und seit PSdZData 54.2 sind die Funktionsnamen auf „.“ gekürzt. [DOK] Sie dürfen nicht weitergegeben werden. Seriöse Open-Source-Projekte liefern sie deshalb nicht mit. [DOK]
5. **Legal nutzbare Parameter-Mapping-Quellen** gibt es nur wenige. Die sauberste ist `names/*.tsv` von OpenCAFDMap (**CC0**), daneben die dort gebündelten Community-Cheat-Sheets (**GPL-3.0**). Hinzu kommen BimmerCodes öffentliche Modellseiten (nur Optionsnamen und ECU, keine Byte/Bit-Angaben) und vor allem **eigene Differenz-Analysen eigener Backups**. Das OpenCAFDMap-Verzeichnis `definitions/untrimmed/bmw/` enthält dagegen BMWs eigene Namen aus alten PSdZData, auch für **CAFD 000000F9**. Dessen Rechtsstatus ist **unklar**.
6. **„BIT-Tuning“** ließ sich **nicht** als Open-Source-Projekt identifizieren. **OpenCAFDMap** existiert dagegen und ist sehr aktiv (letzter Commit am 2026-11-24).

---

## Teil A – BimmerCode-Backup-Format

### A.1 Wann Backups entstehen, wo sie liegen und wie man sie exportiert

| Plattform | Erstellung | Speicherort | Export | Tag |
|---|---|---|---|---|
| iOS | „Each time a control unit is read out, a backup of the coding data for the selected control unit is automatically saved“ | Files-App → „On My iPhone“ → „BimmerCode“ → „Backups“ | über die Files-App kopieren, z. B. nach iCloud Drive oder AirDrop. Beim Löschen der App gehen die Backups verloren. | [DOK] (BimmerCode-Handbuch) |
| Android | „The first time the coding data is read from a control unit a backup is created automatically“ | `Android/data/de.appomotive.bimmercode/files/Backups` | In der App: Startbildschirm → Menü → „Backup files“ → „Export“ (Google Drive, E-Mail …). Ein Import ist ebenfalls vorhanden. | [DOK] (BimmerCode-Handbuch) |
| Desktop | wie Android | Einstellungen → „Manage files“ → Ordner `backups` | Dateisystem | [DOK]. Das Dateiformat der Desktop-Version ist [UNBEKANNT]. |

Weitere Punkte:
- iOS: Backups werden in der App nach Erstellungsdatum absteigend sortiert. Wer alle Codierungen eines Steuergeräts rückgängig machen will, wählt das **unterste** (älteste) Backup. [DOK] (Handbuch)
- iOS: Ein Forennutzer berichtet, dass der Ordner trotz „Auf meinem iPhone“ mit iCloud gesichert wird. Das ist anekdotisch, die Quelle ist nur als Such-Snippet sichtbar. [WAHRSCHEINLICH]
- Ob der Export über das Teilen-Menü (Share Sheet) direkt aus BimmerCode funktioniert, ist [UNBEKANNT]. Dokumentiert ist nur der Weg über die Files-App.
- Das offizielle FAQ (bimmercode.app/faq) sagt nur, dass sich Codierdaten nach einem Abbruch per Backup wiederherstellen lassen. Expert Mode ist dort „not available for control units that contain safety related functions“. Zum Dateiformat steht nichts im FAQ. [DOK]

### A.2 Dateinamen

Quelle: OpenCAFDMap `docs/BC_EDITOR.md` und `ocm/bc_tool.py`.

| Plattform | Muster | Regex aus `bc_tool.py` / `bc_android.py` | Tag |
|---|---|---|---|
| iOS | `<ECU>-<VIN>-<unix time>.cod`, optional mit einem Suffix `-<tag>` | `^(?P<ecu>[0-9A-F]+)-(?P<vin>[A-Z0-9]{17})-(?P<ts>\d{9,})(?:-(?P<tag>[^.]*))?\.cod$` | [DOK] |
| Android | `<VIN>_<ECU>.dat` (ohne Zeitstempel: Neue Backups überschreiben gleichnamige Dateien) | `^(?P<vin>[A-Z0-9]{17})_(?P<ecu>[0-9A-F]+)\.dat$` | [DOK] |

- Der Zeitstempel ist Unix-Zeit in Sekunden. [DOK] (`datetime.fromtimestamp(ts)`)
- `<ECU>` ist bei iOS identisch mit dem Feld `codingECU.identifier` in der Plist, bei Android mit „BimmerCode's ECU id (the <ECU> part of the file name)“. [DOK]

### A.3 Was bedeuten `0F1820` und `0F1650`?

- **Belegt:** Es handelt sich um BimmerCodes interne ECU-Kennung (`codingECU.identifier`), als Hex-String im Dateinamen. [DOK] Sie ist **nicht** die Diagnoseadresse. Diese steht separat im Feld `codingECU.address` (z. B. 0x63). [DOK] (`bc_tool.py`: `self.diag = ecu["address"]`, Ausgabe `0x%02X`)
- **Hypothese: SGBD-Index aus DID 0xF150. [WAHRSCHEINLICH]**
  - BMW-SGBDs definieren den Job `IDENT` als „$22 ReadDataByIdentifier, $F150, Sub-Parameter SGBD-Index“. Das Ergebnis `ID_SGBD_INDEX` ist ein „Index zur Erkennung der SG-Variante“. [DOK] (EdiabasX-SGBD-Referenz, z. B. EWSIKDME, RLM_1R)
  - Eine öffentliche ELM327-Beispielsitzung (Quantex) fragt bei einem BMW-Steuergerät mit `22F150` ab. Die Antwort ist `610 F1 06 62 F150 0F25F0`, das Datum also genau 3 Bytes mit führendem `0x0F`. [DOK] Die Namen des Besitzers (`0F1820`, `0F1650`) folgen exakt diesem Muster: 6 Hex-Stellen mit Präfix `0F`. [WAHRSCHEINLICH]
  - Unbelegt bleibt, dass BimmerCode genau diesen Wert als `identifier` speichert. [UNBEKANNT]
- **So lässt sich die Hypothese forensisch prüfen:**
  1. In der `.cod` die Felder `codingECU.address` (Diagnoseadresse) und `codingData.CAFDIdentifier` lesen. Damit ist geklärt, welches Steuergerät `0F1820` bzw. `0F1650` ist.
  2. Mit dem eigenen Adapter am selben Steuergerät `22 F1 50` lesen. Das ist reines Lesen und damit unkritisch. Danach die 3 Datenbytes mit dem Dateinamen vergleichen.
  3. Gegenprobe: Ändert sich der Identifier nach einem Software-Update desselben Steuergeräts, ohne dass sich die Adresse ändert? Ein SGBD-Index ändert sich typischerweise mit der SG-Variante oder Software, eine Adresse nicht. [WAHRSCHEINLICH]
- **Achtung:** Die öffentliche BimmerCode-Seite für F20/F21 (abgerufen am 2026-11-24) nennt als Head-Units nur **HU_NBT** und **HU_NBT_EVO**, **kein HU_ENTRY** und kein HU_CIC. [DOK] Möglicherweise stammen die beiden Backups also gar nicht von der Head-Unit, sondern z. B. von FEM_01 oder KOMBI. Erst Schritt 1 oben klärt das. [UNBEKANNT]

### A.4 Interner Aufbau einer iOS-`.cod`

Quelle: OpenCAFDMap, `ocm/bc_tool.py` (Klasse `Cod`) und `ocm/cod_import.py` (`read_cod`), beide MIT. Dort heißt es: „.cod = NSKeyedArchiver plist“ und „A .cod holds one ECU's coding session: VIN, ECU address, CAFD id+version, and the raw coding data blocks (blockAddress = datagroup address, e.g. 12288 = 0x3000). There are no parameter names inside.“ [DOK]

**Container:** binäre Apple Property List. Die Magic Bytes `bplist00` prüft der Code explizit. Der Inhalt ist ein NSKeyedArchiver-Objektgraph mit `$top.root`, `$objects` (Objekttabelle) und UID-Referenzen. [DOK]

**Objektgraph** (Schlüsselnamen exakt wie im Code):

```
$top.root  (BimmerCode "CodingSession")              [DOK]
├── VIN                       -> String (17 Zeichen)
├── codingECU
│   ├── identifier            -> String, z. B. "0F1820" (= <ECU> im Dateinamen)
│   ├── address               -> Integer, Diagnoseadresse (z. B. 0x63)
│   └── identifiers
│       └── CAFD              -> NSArray (oder Einzelobjekt) von
│             { identifier: Int (CAFD-ID), mainVersion: Int, subVersion: Int, patchVersion: Int }
└── codingData
    ├── CAFDIdentifier        -> String mit 14 Hex-Zeichen = 4 Byte ID + 1 Byte MV + 1 Byte SV + 1 Byte PV
    │                            Beispiel aus dem Code: "00007083225508"
    │                            -> CAFD_00007083_034_085_008 (Versionsbytes hex -> dezimal)
    └── mutableCodingDataBlocks -> NSArray von
          { blockAddress: Int (Datagroup-DID, z. B. 12288 = 0x3000), data: NSData (rohe Codierbytes) }
```

- Steuergeräte mit mehreren CAFDs (BDC: 7, ACSM: 6, FZD: 2) listen alle CAFDs in `identifiers.CAFD`. Jede Datagroup-Adresse gehört genau zu einem davon. [DOK] (Kommentar in `bc_tool.py`)
- Die **SYSTEM-Datagroups**, also die NCD-Signatur, sind als normale Blöcke enthalten. Beispiele laut Doku: „FLM2 37F1, BDC 3456, MGU 3016“. [DOK] (BC_EDITOR.md)
- Laut OpenCAFDMap berechnet BimmerCode die Signatur bei jeder Änderung neu. Ob BimmerCode beim **Restore** neu signiert oder die gespeicherten Blöcke unverändert schreibt, wissen auch die OpenCAFDMap-Autoren nicht sicher. [DOK, dass es offen ist] Für das Read-only-Projekt ist das irrelevant.
- **Verschlüsselung oder Kompression:** OpenCAFDMap liest die Datei direkt mit `plistlib.load()` ohne Entschlüsselungsschritt. Die geprüften App-Versionen speichern also unverschlüsselt. [DOK] Ob künftige App-Versionen das ändern, ist [UNBEKANNT].
- **Verhältnis zu NCD:** `cod_import.py --ncd OUTDIR` schreibt jedes Backup als E-Sys-NCD im S-Record-Format. Inhaltlich ist eine `.cod` also ein Netto-Codierdatensatz eines Steuergeräts plus Metadaten. [DOK]

**Read-only-Skizze in Python** (eigene Formulierung nach den dokumentierten Schlüsseln, ungetestet mit den Dateien des Besitzers, [WAHRSCHEINLICH] funktionsfähig):

```python
import plistlib

def read_cod(path):
    with open(path, "rb") as f:
        d = plistlib.load(f)                 # bplist00 -> dict; UIDs sind plistlib.UID
    objs = d["$objects"]
    o = lambda uid: objs[uid.data]
    root = o(d["$top"]["root"])
    ecu, cd = o(root["codingECU"]), o(root["codingData"])
    ident = o(cd["CAFDIdentifier"])          # z. B. "000000F9070701" (hypothetisch für 007_007_001)
    blocks = {}
    for ref in o(cd["mutableCodingDataBlocks"])["NS.objects"]:
        b = o(ref)
        blocks[f"{b['blockAddress']:04X}"] = bytes(o(b["data"]))
    return {
        "vin": o(root["VIN"]),
        "ecu_identifier": o(ecu["identifier"]),
        "diag_address": ecu["address"],
        "cafd": f"CAFD_{ident[:8].upper()}_{int(ident[8:10],16):03d}_{int(ident[10:12],16):03d}_{int(ident[12:14],16):03d}",
        "blocks": blocks,                    # {"3000": b"...", ...}
    }
```

Auf macOS liefert `plutil -p datei.cod` eine schnelle Sichtprüfung. [WAHRSCHEINLICH]

### A.5 Android-`.dat`

- Format: **Java-Objektserialisierung** (`ObjectOutputStream`) mit den Magic Bytes `AC ED 00 05`. [DOK] (`bc_android.py`: `MAGIC = b"\xac\xed\x00\x05"`)
- Die Klassen- und Feldnamen sind obfuskiert (z. B. `de.appomotive.bimmercode.k.b`, Felder `b..f`) und können sich zwischen App-Versionen ändern. OpenCAFDMap erkennt die Felder deshalb **an ihren Typen** [DOK]:
  - String (17 Zeichen): VIN
  - String: ECU-ID (der `<ECU>`-Teil des Dateinamens)
  - Liste von Objekten mit 4 ints: CAFDs (id, main, sub, patch)
  - Objekt mit einer Liste von (Integer-Blockadresse, `byte[]`): Codierblöcke
  - `java.util.Date`: Zeitpunkt
- Android-Backups enthalten **keine Diagnoseadresse**. [DOK]

### A.6 Was ein Backup enthält und was nicht

| Inhalt | Enthalten? | Tag |
|---|---|---|
| Rohe Codierdaten aller Datagroups eines Steuergeräts (USER und SYSTEM) | ja | [DOK] |
| VIN, CAFD-ID(s) und Version(en), ECU-Identifier, Diagnoseadresse (nur iOS) | ja | [DOK] |
| Funktions- oder Parameternamen, Wertelabels | **nein** | [DOK] |
| FA, SVT oder Software-/Flash-Daten | nein. Laut Code enthält das Backup nur die Coding-Session. Ein Gegenbeweis für FA-Inhalte wurde nicht gesucht. | [WAHRSCHEINLICH] |

### A.7 Forensische Checkliste für den Fall, dass eigene Dateien abweichen

| Prüfung | Erwartung bei `.cod` | Alternative Hypothesen |
|---|---|---|
| Erste Bytes (`xxd datei | head`) | `62 70 6C 69 73 74 30 30` = `bplist00` | `<?xml` → XML-Plist; `AC ED 00 05` → Java-Serialisierung (Android); `PK 03 04` → ZIP; `SQLite format 3\0` → SQLite; `S0` als ASCII → S-Record-NCD; `{` → JSON |
| Trailer | die letzten 32 Bytes = bplist-Trailer (offset size, ref size, Objektanzahl, Top, Offset-Tabelle) | fehlt → kein bplist |
| ASCII-Strings (`strings`) | `$archiver`, `NSKeyedArchiver`, `$objects`, `VIN`, `codingECU`, `codingData`, `CAFDIdentifier`, `mutableCodingDataBlocks`, `blockAddress`, die 17-stellige VIN | keine Strings und hohe Entropie → verschlüsselt oder komprimiert |
| Entropie | gemischt: Strukturteile niedrig, Codierblöcke mittel, Signaturblock (RSA) hoch | durchgehend ~8 bit/Byte → verschlüsselt oder komprimiert |
| Längenmuster | Blocklängen konstant pro CAFD-Version. Zwei Backups desselben SG mit gleicher CAFD-Version haben nahezu gleiche Dateigröße. | — |
| Diff zweier Backups vor und nach einer einzelnen BimmerCode-Option | wenige Bytes in einem USER-Block ändern sich, dazu der komplette Signaturblock | — |

---

## Teil B – BMW-Codierformate

### B.1 Begriffe

Quelle: E-Sys-Handbuch „Coding with E-Sys“ v1.4, BMW CoC Coding EG-75, 30.07.2007, gültig ab E-Sys 3.0.2. [DOK]

| Abk. | Bedeutung laut Handbuch |
|---|---|
| CAF | Coding Application File (Codierbeschreibung eines Steuergeräts) |
| CAFD | „Process class designation of the CAF“ |
| NCD | Net coding data (Netto-Codierdaten) |
| FDL | Function data list |
| FA | Fahrzeugauftrag (Vehicle order), auch VO genannt |
| FP | Vehicle profile (Fahrzeugprofil) |
| FA2FP | „Assignment table of vehicle order to vehicle profile“ |
| SGBM-ID | „Control unit description model identification number“ |
| SVK | Software variant code (Steuergeräte-Verbaukennung) |
| SVT | System variant table |
| TAL | Transaction list |
| SALAPA | Sonder-, Länder-, Paketausstattung |

### B.2 SGBM-ID, SVK und die Benennung `CAFD_000000F9_007_007_001`

- **CAF-Identifikator** im CAF-Header: **PK** (Prozessklasse, hier CAFD), **ID** (SGBM-ID), **MV** (Hauptversion), **SV** (Unterversion), **PV** (Patchversion). [DOK] (E-Sys-Handbuch, Kap. 3.2)
- **Prozessklassen** laut BMW-SGBD-Tabelle `PROZESSKLASSEN` [DOK]:
  - 0x01 HWEL (Hardware Elektronik), 0x02 HWAP, 0x03 HWFR, 0x04 GWTB (Gateway-Tabelle)
  - **0x05 CAFD (Codierdaten)**
  - 0x06 BTLD (Bootloader), 0x07 FLSL, 0x08 SWFL (Software ECU-Speicherimage), 0x09 SWFF, 0x0A SWPF, 0x0B ONPS, 0x0C IBAD, 0x0D SWFK
  - 0x0F FAFP (FA2FP), 0x10 FCFA, 0x1A TLRT, 0x1B TPRG, 0x1C BLUP, 0x1D FLUP
  - 0xA0 ENTD, 0xA1 NAVD, 0xA2 FCFN, 0xC0 SWUP, 0xC1 SWIP
- **SVK per UDS:** `22 F1 01` liefert die SVK. Ein Eintrag ist 8 Bytes lang: 1 Byte Prozessklasse, 4 Byte SGBM-ID, je 1 Byte MV, SV, PV. [DOK] (nbt-coding `ecu.py`, Funktion `read_cafd_id`, MIT)
- **Lesart von `CAFD_000000F9_007_007_001`:** Prozessklasse CAFD, SGBM-ID `0x000000F9`, MV 7, SV 7, PV 1. Die Versionen werden **dezimal, dreistellig** geschrieben. [DOK] (Namensschema in OpenCAFDMap `"%03d_%03d_%03d"`, E-Sys-Beispiele `CAFD_0005638F_003_025.001.ncd` und `cafd_01020304_001_000_002.ncd`)
- **Dateinamen in PSdZData:** `swe/cafd/cafd_<id klein>.caf.<MMM_SSS_PPP>`, also `cafd_000000f9.caf.007_007_001`. [DOK] (`bc_tool.py` → `defs_status`) Entschlüsselte XML heißen in nbt-coding z. B. `cafd_0000106d.caf.013_012_011.xml`. [DOK]
- **In der `.cod`:** `CAFDIdentifier` speichert ID und Versionen als Hex-Bytes. Für 007_007_001 wäre das `000000F9070701`. [WAHRSCHEINLICH] (abgeleitet)
- **Zu welchem Steuergerät gehört CAFD_000000F9?**
  - Ein Such-Snippet aus einem bimmerfest-Thread („BMW CAFD ID Cheat Sheet“) nennt „HU_CIC/ENTRY: CAFD_000000F9“. Das Forum selbst war nicht abrufbar. [WAHRSCHEINLICH]
  - Foren-Snippets berichten von E-Sys-Fehlern mit `cafd_000000f9-007_009_009` im Zusammenhang mit der Head-Unit. [WAHRSCHEINLICH]
  - **Eigene Prüfung:** Die OpenCAFDMap-Datei `definitions/untrimmed/bmw/000000F9.tsv.gz` (17.094 Zeilen) nennt diese Datagroups: 3000 „HMI“, 3001 „EXBOX“, 3002 „AUDIO_TUNER_TRAFFIC“, 3003 „TELEFON_TELEMATIK_ONLINE“, 3005 „APIX CID“. Dazu kommen Funktionen wie `WELCOME_LIGHT`, `SPRECHERWAHL1`, `LANGUAGE_4` usw. Das ist eindeutig eine **Head-Unit-CAFD**. [DOK für die Gruppennamen]
  - **Fazit:** „CAFD_000000F9 = HU_ENTRY (ggf. gemeinsam mit HU_CIC)“ ist [WAHRSCHEINLICH]. Endgültig klären lässt es sich mit `22 F1 01` an der Head-Unit oder über `CAFDIdentifier` in einem HU-Backup.

### B.3 NCD – Layout

**Primärquelle:** E-Sys-Handbuch v1.4, Kap. 2.2.2.1 [DOK]:
- „The NCD file with the net coding data read out is saved to E-Sys data directory ..\CAF.“
- „The file name of an NCD file corresponds to the name of the CAF used for read-out … with file extension ncd (e.g. CAFD_0005638F_003_025.001.ncd).“
- „The net coding data is written to the file in **Motorola S-Record format**.“

Der Beispielauszug aus dem Handbuch hat folgende Records. Alle Prüfsummen und Längenbytes wurden in dieser Recherche nachgerechnet und sind korrekt.

| Record | Adresse | Daten | Interpretation | Tag |
|---|---|---|---|---|
| `S00A0000FF000000010401F0` | 0000 | `FF000000 01 04 01` (7 B) | Header: 4 Byte CAFD-/SGBM-ID + MV, SV, PV | [WAHRSCHEINLICH]. Länge und Aufbau stimmen mit dem OpenCAFDMap-Writer überein: `bytes.fromhex(cafd) + bytes([m, s, p])`. |
| `S206300000663E25` | 0x300000 | `66 3E` | Datagroup **0x3000**, Offset 0 | [WAHRSCHEINLICH] |
| `S208300100ACE80F0F14` | 0x300100 | `AC E8 0F 0F` | Datagroup 0x3001 | [WAHRSCHEINLICH] |
| `S20C30210005FF00000001040198` | 0x302100 | `05 FF000000 01 04 01` | Datagroup 0x3021: Prozessklasse 05 (CAFD) + ID + Version, also eine SYSTEM-Datagroup mit SGBM-ID | [WAHRSCHEINLICH] (eigene Deutung) |
| `S224302200…` bis `S208302280…` | 0x302200 … 0x302283 | `00000020` + 128 Byte | Datagroup 0x3022 = **NCD-Signaturblock**: 4 Byte Länge (0x20 = 32 Worte = 128 Byte), danach eine 1024-Bit-Signatur | [WAHRSCHEINLICH] |
| `S503000EEE` | — | Anzahl 0x000E | S5-Record-Zähler | Abweichung: Im Auszug stehen nur 8 S2-Records. Vermutlich ist das Beispiel gekürzt. [UNBEKANNT] |

**Abgeleitetes Layout:**
- **Zeilenformat:** `S<Typ><Count><Adresse><Daten><Checksum>`. Die Checksumme ist das Einerkomplement der Bytesumme aus Count, Adresse und Daten. [DOK] (S-Record-Standard; im Beispiel verifiziert)
- **S0:** Adresse `0000`, Daten = SGBM-ID (4 B) + MV/SV/PV (je 1 B). [WAHRSCHEINLICH]
- **S2 (24-Bit-Adresse):** Adresse = `(Datagroup-DID << 8) + Offset`, max. **32 Datenbytes pro Record**. [DOK] (Beispiel und OpenCAFDMap-Writer: `base = int(g,16) << 8`, Chunks à 32 Byte)
- **Datagroups:** Die DIDs entsprechen den UDS-DIDs, die mit `22 xx xx` gelesen werden (z. B. 0x3000 …). [DOK] (nbt-coding: „Each USER datagroup in the CAF has an address like 3000..3005. That address is a UDS Data Identifier.“)
- **Signatur:** Laut CAF-Header gibt es einen Eintrag „NCD-Sig-Block: data identifier with which the signature of the net coding data is transferred“. [DOK] (Handbuch) In der CAF-XML heißt das Attribut `ncdSignAddress`, z. B. `"3007"` bei NBT. [DOK] (nbt-coding `caf.py`) Für Steuergeräte der NBT-Ära beschreibt nbt-coding das Verfahren so: rohe RSA-Signatur ohne Padding über den MD5 der verketteten Content-Datagroups (e = 3), mit vorangestellter Länge `(keysize//4)` als uint32 big-endian. [DOK] Das ist eine Community-Rekonstruktion, keine BMW-Doku, und passt zum `00000020`-Präfix im Handbuchbeispiel. Für ein Read-only-Tool genügt: **SYSTEM-Datagroups nicht interpretieren, sondern nur als „Signatur/Systemdaten“ kennzeichnen.**
- **Unklar [UNBEKANNT]:**
  - wie Datagroups mit mehr als 256 Byte im 24-Bit-Adressschema kodiert werden (Kollision mit der nächsten DID?)
  - ob E-Sys dafür S3-Records nutzt
  - Empfehlung: mit einer echten NCD aus eigener E-Sys-Auslesung prüfen
- **NCD-Trace-Dateinamen** (Verifikation in E-Sys): `[Position]_[FAName]_[SGBMID].ncd`, z. B. `13_Testfaxyz_cafd_01020304_001_000_002.ncd`. [DOK]

**Open-Source-Parser und -Writer für NCD:**
- OpenCAFDMap `cod_import.py`, Funktion `write_ncd` (Writer, MIT) [DOK]
- OpenCAFDMap „Compare NCD“: read-only Vergleich zweier NCDs, im E-Sys-Agenten in JavaScript, abgeglichen nach Gruppe, Byte und Maske [DOK]
- Einen eigenständigen „NcdTool“ oder „CafdTool“ als Bibliothek wurde **nicht** gefunden. [UNBEKANNT/nicht gefunden]
- Ein S-Record-Parser ist trivial selbst zu schreiben, z. B. mit dem PyPI-Paket `bincopy` oder in 30 Zeilen eigenem Code. [WAHRSCHEINLICH]

### B.4 CAFD (`.caf`) – Aufbau

- **In PSdZData verschlüsselt.** nbt-coding wirft `CafEncrypted`: „The CAF file is still encrypted (raw PSdZData); it must be decrypted by E-Sys first.“ OpenCAFDMap entschlüsselt mit E-Sys' eigenem PsdZ (`esys/decrypt.js`). [DOK]
- **Namen gekürzt:** „Current psdzdata ships CAFDs with every FDL name trimmed to `.`.“ BMW hat ab **PSdZData 54.2** alle Namen entfernt. Bis 54.1 waren sie noch enthalten. [DOK] (OpenCAFDMap README und `definitions/README.md`)
- **Logische Struktur** laut E-Sys-Handbuch, Kap. 3.2 [DOK]:
  - Header: Ersteller, Kommentar, Datum, EcuName, Speicherlayout (nur BYTE), allgemeiner Anlieferzustand, **NCD-Sig-Block**, BN2000-Flag, CodingJobList-Version
  - CAF-Identifikator: PK/ID/MV/SV/PV
  - Fahrzeugprofil-Info: FAFP mit PK/ID/MV/SV/PV
  - Daten: pro Datagroup die DID, der Name, die Länge, eine **Aktivbedingung** (Baureihe) und die **Funktionen**
  - Pro Funktion: Name, Kommentar, Speicher-Info (**Start, Ende, Größe, Maske**), Anlieferwert und **Funktionswerte**. Jeder Funktionswert hat einen Kommentar, eine **Bedingung (X-Path)**, die Werte und eine optionale Prüfschritt-ID.
  - In der FDL zusätzlich: „Ausgelesen“, also der interpretierte Wert und die gelesenen Bytes.
- **Begriffe:** Ein Funktionswert ist z. B. `aktiv` oder `nicht_aktiv`. Der zugehörige **Codierwert** ist die tatsächlich geschriebene Bytefolge (z. B. 0xFF, 0x10). [DOK]
- **XML-Form nach dem Entschlüsseln** [DOK] (nbt-coding `caf.py`):
  ```xml
  <caf ncdSignAddress="3007">
    <datagroup address="3000" datagroupClass="USER" units="98">
      <function>
        <storageInfo><start>0</start><end>0</end><mask>00000001b</mask></storageInfo>
        <defVal><unitVal position="0">00</unitVal></defVal>
        <condParam><paramName>.</paramName>
          <bool mainSeries="F010">true()</bool>
          <values><unitVal position="0">01</unitVal></values>
        </condParam>
      </function>
    </datagroup>
    <datagroup address="3007" datagroupClass="SYSTEM"> … </datagroup>
  </caf>
  ```
- **Wert extrahieren** (identisch in OpenCAFDMap `defdb.extract` und nbt-coding):
  - Einzelbyte-Feld mit Bitmaske (z. B. `00011000b`): `(byte & mask) >> lowest_set_bit(mask)`
  - Mehrbyte-Feld: `data[start:end+1]` roh als Hex
  - [DOK]
- **Open-Source-CAFD-Parser:**
  - nbt-coding `caf.py`: MIT, arbeitet nur auf **entschlüsselter** XML [DOK]
  - OpenCAFDMap `defdb.py`, `build_defdb.py`, `runtime_defs.py`: MIT, braucht E-Sys und eigene PSdZData [DOK]
  - **Kein** Projekt liefert die CAFDs selbst mit oder entschlüsselt sie ohne E-Sys. [DOK] („The repo ships no BMW data“; OpenCAFDMap lehnt PSdZData-Dateien in Beiträgen ab.)

### B.5 FDL-Codierung vs. VO/FA-Codierung

- **VO/FA-Codierung** (Standardweg): E-Sys bildet aus dem FA über die FA2FP-Tabelle das **Fahrzeugprofil (FP)**. Daraus berechnet es per CAF-Bedingungen die NCD und schreibt sie. Das Handbuch nennt das FP ausdrücklich als „the vehicle profile taken as a basis for generation of the net coding data“. [DOK] Wer das FA ändert und VO-codiert, bekommt also die werkseitig vorgesehenen Werte für die geänderte Ausstattung. [WAHRSCHEINLICH]
- **FDL-Codierung** (Expert Mode Coding): Steuergerät auslesen (ergibt NCD und FDL), einzelne Funktionswerte in der FDL ändern und codieren. Laut Handbuch von 2007 war dafür ein personalisierter **Developer Soft Token (EST)** mit Rolle ADVANCED nötig. [DOK] Eine FDL ist ein CAF, ergänzt um die ausgelesenen NCD und deren Interpretation. Ablage: `..\FDL\<CAF-Name>.fdl`. [DOK]
- **Für das Analyse-Tool:** Eine BimmerCode-`.cod` entspricht inhaltlich der **NCD**. Die **FDL-Sicht**, also Namen und Werte, entsteht erst durch die Verknüpfung mit einer CAFD-Definition oder einem Namensmapping. [DOK/WAHRSCHEINLICH]

### B.6 FA (Fahrzeugauftrag)

- **Definition:** Das FA ist im Fahrzeug gespeichert und „encodes the vehicle model, VIN and option list with which a BMW left the factory“. [DOK] (BMW-Hacking-Wiki) Es enthält die **SALAPA**-Liste aus Sonder-, Länder- und Paketausstattung, z. B. 258 Runflat oder 522 Xenon. [DOK]
- **Zeitkriterium:** „Vehicle version, in format MMYY“. Im BMW-Werkstattbeispiel: Typschlüssel `AU51`, Zeitkriterium `0901`, E-Wort `SBK1`. HO-Wort „(not used at present)“ in jenem DIS/MoDiC-Kontext. [DOK] (BMW-Werkstatthandbuch E46, ZCS/FA-Codierung; ältere Generation)
- **E-Wörter und HO-Wörter** sind zusätzliche Ausstattungs- bzw. Steuerwörter im FA, die sich im FA-Editor hinzufügen oder löschen lassen. [DOK] Ihre konkrete Semantik bei F-Modellen ist [UNBEKANNT].
- **FA-String** (Kurzform, z. B. aus E-Sys oder ISTA): Für die Sonderzeichen wurde **keine Primärquelle** gefunden. Die verbreitete Lesart, angewandt auf das Beispiel des Besitzers `F020_12_03_500#0112*1A31%0300&...$...`, ist [WAHRSCHEINLICH]:

  | Teil | Bedeutung (Hypothese) | Plausibilitätscheck |
  |---|---|---|
  | `F020_12_03_500` | Baureihe bzw. Baureihenverbund F020, gefolgt von einem Integrationsstand im I-Stufen-Stil (`F020-12-03-500`) | Format deckt sich mit der I-Step-Schreibweise. [WAHRSCHEINLICH] |
  | `#0112` | Zeitkriterium MMYY = **01/2012** | passt exakt zum Baudatum Jan 2012 [WAHRSCHEINLICH] |
  | `*1A31` | Typschlüssel | Ob 1A31 = 116i F20 ist, wurde nicht verifiziert. [UNBEKANNT] |
  | `%0300` | Lackcode (300 = Alpinweiß III) | [WAHRSCHEINLICH] |
  | `&xxxx` | Polstercode | [WAHRSCHEINLICH] |
  | `$xxx` | je ein SA-Code | [WAHRSCHEINLICH] |
  | `-xxxx` / `+xxxx` | E-Wörter / HO-Wörter | [WAHRSCHEINLICH] |

- **XML-FA** (E-Sys „FA.xml“): Die genaue Struktur wurde nicht verifiziert. [UNBEKANNT] Für die Typschlüssel-Auflösung liefert OpenCAFDMap `data/fa/` mit „8,456 type keys, built from ISTA and KIS“. [DOK] Die Herkunft aus ISTA/KIS ist rechtlich ebenfalls heikel. [WAHRSCHEINLICH]

### B.7 Rechtsstatus und legal nutzbare Mapping-Quellen

**Rechtsstatus der BMW-Daten:**
- CAFD-Dateien, PSdZData, ISTA-, KIS- und SGBD-Dateien sind **proprietäre, urheberrechtlich bzw. datenbankrechtlich geschützte BMW-Daten** und werden nur lizenziert ausgeliefert. [WAHRSCHEINLICH] Indizien:
  - Sie werden verschlüsselt ausgeliefert. [DOK]
  - Für die Bearbeitung von CAFs war im Handbuch ein EST mit Rolle EXPERT nötig. [DOK]
  - Seriöse Open-Source-Projekte schließen sie ausdrücklich aus. [DOK]
- Nach deutschem Recht kommen der Schutz als Datenbank (§ 87a ff. UrhG) und vertragliche Lizenzbedingungen in Betracht. [WAHRSCHEINLICH] Keine Rechtsberatung.
- **Die Weitergabe** entschlüsselter CAFDs, NCDs mit VIN oder BimmerCode-Backups ist zu vermeiden. OpenCAFDMap lehnt genau das in Pull-Requests ab („decrypted psdzdata files … NCDs, BimmerCode backups, FA/FP/SVT files … anything containing a VIN“). [DOK]
- **Analyse der eigenen Backups** (eigene Daten, nur lesend): Die Datenformate selbst sind nicht geschützt, nur deren Inhalte. [WAHRSCHEINLICH] Unkritisch ist es nach üblicher Einschätzung, solange keine BMW-Datenbanken eingebettet oder weitergegeben werden. Ob die Nutzungsbedingungen von BimmerCode das Reverse Engineering der App untersagen, ist [UNBEKANNT]. Hier wird ohnehin nur das Datenformat gelesen, nicht die App dekompiliert.

**Parameter-Mapping-Quellen und ihr Status:**

| Quelle | Inhalt | Lizenz / Status | Nutzen für F20 HU_ENTRY | Tag |
|---|---|---|---|---|
| OpenCAFDMap `names/*.tsv` | Community-Namen, Schlüssel = CAFD-ID + Datagroup + Byte + Maske. Aktuell vor allem G-Serie: BDC_BODY3, DKOMBI4, DME_BAC2, FLM2, FZD2, HU_MGU (+ `versioned/`, `cheatsheet/`) | **CC0** | gering, keine HU_ENTRY-Datei gesehen | [DOK] |
| OpenCAFDMap `definitions/community-cheatsheets/` | öffentliche FDL-Cheat-Sheets (XML) | **GPL-3.0**, unverändert übernommen | Inhalt für F20 nicht geprüft | [DOK] |
| OpenCAFDMap `definitions/untrimmed/bmw/<CAFD>.tsv.gz` | **BMWs eigene Namen** aus PSdZData ≤ 54.1, darunter `000000F9.tsv.gz` mit Gruppen-, Funktions- und Wertenamen | Das Repo nennt CC0 bzw. „licence stated in file“. Herkunft sind BMW-Daten, daher ist der **Rechtsstatus unklar**. | **hoch** (exakt die vermutete HU_ENTRY-CAFD), aber nur nach eigener Rechtsabwägung | [DOK]/[UNBEKANNT] |
| BimmerCode-Modellseite `bimmercode.app/cars/f20` | 204 Optionsüberschriften mit zugehöriger ECU (FEM_01, KOMBI L6/L7, HU_NBT, HU_NBT_EVO …). **Keine** Byte/Bit-Angaben, **kein HU_ENTRY**. | öffentlich lesbar, keine Lizenz zur Weiterverwendung angegeben | Plausibilitäts- und Labelquelle | [DOK] |
| **Eigene Backup-Diffs** | Option in BimmerCode umschalten, vorher und nachher sichern, diffen. Genau das macht OpenCAFDMap `cod_import.py --sheet`. | eigene Daten | **höchster legaler Wert** | [DOK] (Methode) / [WAHRSCHEINLICH] (rechtlich) |
| EdiabasX SGBD Reference (emdzej.github.io) | Doku der SGBD-Jobs, z. B. IDENT/F150 und Prozessklassen | keine Lizenzangabe. Abgeleitet aus BMW-SGBDs, „ORIGIN: BMW EA-405“. | Diagnose-DIDs, nicht Codierung | [DOK]/[UNBEKANNT] |
| Community-Repos `brodee227/bmw-f`, `jokinawa/bmw-f` | F-Serie-Codierleitfäden („work in progress“) | Lizenz nicht geprüft | gering bis mittel | [DOK] (Existenz per Suche) / [UNBEKANNT] (Lizenz) |
| Cheat-Sheets auf Scribd oder in Foren (z. B. „BimmerCode Some Cheats July 2020“, F30 Coding Reference Guide) | Listen mit Funktionsnamen | Urheberrecht der Ersteller; Weiterverwendung ungeklärt | mittel | [UNBEKANNT] |
| „FDL-Editor-Übersetzungslisten“ (DE→EN) | in Foren verbreitet | nicht gefunden oder verifiziert | — | [UNBEKANNT] |

---

## Teil C – Projekte

### C.1 Übersichtstabelle

| Name | URL | Lizenz | Stand | Nutzen für dieses Projekt | Existenz verifiziert |
|---|---|---|---|---|---|
| **OpenCAFDMap / OpenLauncher** | https://github.com/shamair28/OpenCAFDMap (Docs: https://shamair28.github.io/OpenCAFDMap-docs/; Forks u. a. roadray, manfred-mp, Inspelning) | Code **MIT**; `names/` **CC0**; Community-Cheat-Sheets **GPL-3.0**; `definitions/` je nach Datei | sehr aktiv: 145 Commits, letzter Commit **2026-11-24**, v3.0.0 am 2026-11-23, 68 Sterne | **sehr hoch**: einzige öffentliche Referenz für den `.cod`- und `.dat`-Aufbau, dazu NCD-Writer, Namens-DB und Backup-Diff-Methode. Läuft selbst nur unter Windows mit E-Sys, aber die Parser-Logik ist portabel. | **ja** (README, Code, Commits gelesen) |
| **nbt-coding** | https://github.com/adityadroid/nbt-coding | **MIT** | 32 Commits, 2026; „first real write on the car is still pending“ | **mittel**: CAF-XML-Parser, UDS-Lese-DIDs (F190, F101, 3000…), HSFZ/ENET. Enthält Schreib- und Signaturlogik, die hier **nicht** benötigt wird. Kein ELM327. | **ja** |
| **EdiabasLib / BmwDeepObd** | https://github.com/uholeschak/ediabaslib | **GPL-3.0** | 20.157 Commits, 970 Sterne, aktiv | **mittel**: Referenz für BMW-Protokolle (D-CAN, BMW-FAST) und ELM327-Nutzung. .NET/Android; macOS nicht erwähnt. ELM327 (PIC18F2480) nur „D-CAN protocol only“. | **ja** |
| **BIT-Tuning** | — | — | — | — | **nein**. Weder als Open-Source-Projekt noch als Produkt identifizierbar (2 Suchen ohne Treffer). |
| **python-OBD** (`obd`) | https://github.com/brendan-w/python-OBD | **GPL-2.0-only** | 0.7.3 vom 2025-04-07; Python ≥ 3.9 (Classifier 3.9–3.13) | **gering bis mittel**: ELM327-Handling für OBD-II-Modi. BMW-UDS mit Extended Addressing bräuchte eigene AT-Befehle. Die GPL beachten. | ja (PyPI) |
| **python-can** | https://github.com/hardbyte/python-can | **LGPL-3.0-only** | 4.6.1 vom 2025-08-12; Python ≥ 3.9 (3.9–3.14) | **gering** für ELM327: **kein ELM327-Backend** in der Backend-Liste (slcan, serial, socketcan, pcan …). | ja (PyPI + Quellcode) |
| **can-isotp** | https://github.com/pylessard/python-can-isotp | **MIT** | 2.0.7 vom 2025-05-14; Python ≥ 3.7 | **gering** mit ELM327, da der ELM327 ISO-TP selbst macht. Nützlich mit echtem CAN-Interface; unterstützt `Extended_11bits`. | ja (PyPI + Quellcode) |
| **udsoncan** | https://github.com/pylessard/python-udsoncan | **MIT** | 1.26.1 vom 2026-06-25; Python ≥ 3.7 | **mittel**: UDS-Client und -Codecs. Mit ELM327 nur über eine eigene Connection-Klasse. [WAHRSCHEINLICH] | ja (PyPI) |
| **Bleak** | https://github.com/hbldh/bleak | **MIT** | 3.1.0 vom 2026-11-07; Python ≥ 3.10 | **hoch**, falls der Adapter **BLE** ist (macOS/CoreBluetooth). Für Bluetooth-Classic-SPP-Adapter nicht zuständig. [WAHRSCHEINLICH] | ja (PyPI) |
| **ELM327-emulator** | https://github.com/Ircama/ELM327-emulator | **CC-BY-NC-SA-4.0** (laut PyPI) | 4.0.0 vom 2026-09-17; Classifier Python 3.10–3.14 | **mittel**: Tests ohne Auto; eigene BMW-Szenarien wären nötig. Die NC-Lizenz passt zu privater Nutzung. | ja (PyPI) |
| **SwiftOBD2** | https://github.com/kkonteh97/SwiftOBD2 | **MIT** | 114 Commits; iOS 14+ / macOS 11+ | **gering bis mittel**: ELM327 in Swift; Custom-PIDs nur auf der Roadmap. | ja |
| **AndrOBD** | https://github.com/fr3ts0n/AndrOBD | **GPL-3.0** | 2.048 Commits, 2,2k Sterne | **gering**: nur Android, OBD-II; UDS/BMW nicht erwähnt. | ja |
| **MCP Python SDK** (`mcp`) | https://github.com/modelcontextprotocol/python-sdk | **MIT** | **2.3.0** vom 2026-10-02; Python ≥ 3.10 (3.10–3.14) | optional: Tool-Schnittstelle für ein LLM-gestütztes Analysewerkzeug | ja (PyPI) |
| Scapy (HSFZ-Modul) | https://scapy.readthedocs.io/en/latest/api/scapy.contrib.automotive.bmw.hsfz.html | GPL-2.0 [WAHRSCHEINLICH] | — | nur für ENET/HSFZ, nicht für ELM327 | nur Suchtreffer/Doku |
| odxtools (mercedes-benz) | https://github.com/mercedes-benz/odxtools | nicht geprüft | — | gering, BMW nutzt SGBD/PSdZ statt ODX für Codierung [WAHRSCHEINLICH] | nur Suchtreffer |
| Rust: ecu_diagnostics (rnd-ash), automotive_diag (nyurik), uds-rs (japawblob) | https://github.com/rnd-ash · https://github.com/nyurik/automotive_diag · https://github.com/japawblob/uds-rs | nicht geprüft | — | gering bis mittel (UDS-Codecs) | nur Suchtreffer |
| EdiabasX SGBD Reference | https://emdzej.github.io/ediabasx-docs-sgbd/ | keine Angabe | — | Nachschlagewerk für DIDs und Prozessklassen | ja |
| BMW-Hacking-Wiki | https://antoniovazquezblanco.github.io/BMW-Hacking/ | keine Angabe gefunden | — | Glossar, FA/VO | ja |
| kdrcoding/fake-car | https://github.com/kdrcoding/fake-car | nicht geprüft | — | „pretend BMW for E-Sys“ (Windows, braucht PSdZData); für macOS/ELM327 irrelevant | nur Suchtreffer |
| NCS Dummy | Thread: bimmerforums „NCS Dummy – Taking the expert out of NCS Expert“ | Freeware, closed source [WAHRSCHEINLICH] | — | **keiner**: arbeitet mit NCS-Expert-Traces (FSW_PSW.TRC, NETTODAT.TRC). NCS Expert ist das E-Serien-Werkzeug, F-Serie (F20) wird mit E-Sys codiert. [WAHRSCHEINLICH] | ja (Suchtreffer/Thread) |
| E-Sys, ISTA, Tool32, NCS Expert (BMW) | — | **proprietär** (BMW) | — | nur als Referenzbegriffe; keine Nutzung oder Weitergabe von Daten | allgemein bekannt [WAHRSCHEINLICH] |
| BimmerCode / BimmerLink (appomotive) | https://bimmercode.app | **proprietär** | — | Datenquelle (eigene Backups) | ja |

### C.2 Wichtige Details

**OpenCAFDMap / OpenLauncher** [DOK]
- Python ≥ 3.10 mit tkinter, Windows, E-Sys mit PSdZData. Getestet mit E-Sys 25.10 (Java 11) und 3.35.3 (Java 8).
- Funktionen: Namen im E-Sys-FDL-Editor, Compare NCD (read-only), Cheat Sheet, FA Helper, DTC lesen und löschen (`14 FF FF FF`), FA/SVT-Backup, **BimmerCode Backup Editor**.
- Bestandteile mit Relevanz für dieses Projekt:
  - `ocm/bc_tool.py`: `.cod`-Parser und bplist-Offset-Mapper zum byte-genauen Patchen
  - `ocm/bc_android.py`: minimaler Java-Deserialisierer
  - `ocm/cod_import.py`: Zeitleiste und Diffs mehrerer Backups, Export als NCD
  - `ocm/defdb.py`: `extract()`
- Für ein macOS-Read-only-Tool lassen sich die **Formatkenntnisse** übernehmen. Der Code darf unter MIT wiederverwendet werden, Copyright-Hinweis beibehalten. Die E-Sys-abhängigen Teile werden nicht gebraucht.
- Hinweis: Der Editor erzeugt Backups mit **alter Signatur**. Das ist für ein Read-only-Projekt nicht relevant, nicht nachahmen.

**Realistischer Kommunikationsweg F20 ↔ ELM327 ↔ macOS**
- BMW F-Serie: CAN mit 11-Bit-IDs, 500 kbit/s. Der Tester sendet auf **0x6F1** mit **Extended Addressing**: Das erste Datenbyte ist die Ziel-ECU-Adresse. Die Antwort kommt auf **0x600 + ECU-Adresse** (z. B. 0x640, 0x610). [DOK] (Quantex-Beispiel)
- ELM327-Sequenz laut Quantex [DOK]:
  - `ATPBC101` und `ATSPB` (USER1-CAN, 11 Bit, 500 kbit/s)
  - `ATSH6F1`
  - `ATFCSH6F1`, `ATFCSD<ECU>30FF32`, `ATFCSM1`
  - `ATCRA6<ECU>`
  - `ATCEA<ECU>`
  - danach z. B. `22F150`
- Ob billige ELM327-Klone `ATCEA` beherrschen, ist [UNBEKANNT]. Laut einem OVMS-Bericht funktionierte ein BMW i3 erst mit `ATCEA07`. [DOK]
- **Nur-Lese-Dienste** für das Tool:
  - `22 F1 90` (VIN) [DOK]
  - `22 F1 01` (SVK, liefert die CAFD-ID) [DOK]
  - `22 F1 50` (SGBD-Index) [DOK]
  - `22 30 00…` (Codier-Datagroups) [DOK]
- Schreibende oder zustandsändernde Dienste meiden: `2E` (WriteDataByIdentifier), `31` (RoutineControl), `27` (SecurityAccess), `10 02/03` (Sessionwechsel), `11` (Reset), `14` (Fehlerspeicher löschen). [WAHRSCHEINLICH] (UDS-Standardsemantik)
- **Python-Stack auf macOS:**
  - BLE-Adapter: **Bleak** + eigener ELM327-Zeilenparser
  - Bluetooth-Classic-SPP-Adapter: erscheinen auf macOS als serielles Gerät (`/dev/cu.*`), also `pyserial` [WAHRSCHEINLICH]
  - UDS-Antworten selbst dekodieren oder `udsoncan`-Codecs nutzen
  - **python-can und can-isotp passen nicht direkt zu ELM327** [DOK: kein Backend] / [WAHRSCHEINLICH: ISO-TP macht der ELM selbst]

---

## Offene Fragen

1. **Ist `codingECU.identifier` (`0F1820`, `0F1650`) wirklich der F150-SGBD-Index?** Prüfen durch `22 F1 50` am jeweiligen Steuergerät. Die Adresse steht in `codingECU.address` der `.cod`. [UNBEKANNT]
2. **Von welchen Steuergeräten stammen die beiden Backups?** Die BimmerCode-F20-Seite listet kein HU_ENTRY. Gibt es HU_ENTRY-Optionen nur im Expert Mode, oder gar nicht? [UNBEKANNT]
3. **Gehört CAFD_000000F9 zu HU_ENTRY, zu HU_CIC oder zu beiden?** Laut Inhalt ist es sicher eine Head-Unit-CAFD; die genaue ECU-Variante ist nicht primär belegt. [WAHRSCHEINLICH]
4. **Hängt das `.cod`-Format von der App-Version ab?** Zum Beispiel neue Schlüssel oder künftige Verschlüsselung. Nur durch Prüfung der eigenen Dateien klärbar. [UNBEKANNT]
5. **Wie sieht die NCD-Kodierung von Datagroups über 256 Byte aus (S2 vs. S3)?** Und warum zeigt das S5-Record im Handbuchbeispiel 14 Records, obwohl nur 8 abgedruckt sind? [UNBEKANNT]
6. **Gibt es Primärquellen für die FA-String-Syntax** (`#`, `*`, `%`, `&`, `$`, `-`, `+`) **und das XML-FA-Schema?** Gefunden wurde nur die Zeitkriterium-Definition MMYY. [UNBEKANNT]
7. **Welchen Rechtsstatus haben die „untrimmed BMW names“ in OpenCAFDMap** (u. a. `000000F9.tsv.gz`)? Dürfen sie privat genutzt, aber nicht weitergegeben werden? [UNBEKANNT]
8. **Unterstützt der konkrete ELM327-Adapter des Besitzers `ATCEA`, `ATFCSD` und `ATFCSM`?** Ist er BLE oder Classic? [UNBEKANNT]
9. **Signiert BimmerCode beim Restore neu?** Für Read-only irrelevant; offen laut OpenCAFDMap. [UNBEKANNT]
10. **„BIT-Tuning“:** Woher stammt der Name? Ohne weiteren Kontext nicht auffindbar.

---

## Quellen

**BimmerCode (offiziell)**
- Handbuch / Quick Start Guide (Backups iOS/Android/Desktop): https://bimmercode.app/manual/
- FAQ: https://bimmercode.app/faq/
- F20/F21-Optionsliste: https://bimmercode.app/cars/f20
- Adapterliste: https://bimmercode.app/adapters/

**OpenCAFDMap (MIT/CC0/GPL-3.0-Teile)**
- Repository: https://github.com/shamair28/OpenCAFDMap
- Commits: https://github.com/shamair28/OpenCAFDMap/commits/main
- Backup-Editor-Doku: https://raw.githubusercontent.com/shamair28/OpenCAFDMap/main/docs/BC_EDITOR.md
- `.cod`-Parser: https://raw.githubusercontent.com/shamair28/OpenCAFDMap/main/ocm/bc_tool.py
- `.cod`-Import und NCD-Writer: https://raw.githubusercontent.com/shamair28/OpenCAFDMap/main/ocm/cod_import.py
- Android-`.dat`-Parser: https://raw.githubusercontent.com/shamair28/OpenCAFDMap/main/ocm/bc_android.py
- `extract()`: https://raw.githubusercontent.com/shamair28/OpenCAFDMap/main/ocm/defdb.py
- Definitionen und Untrimmed-Namen: https://raw.githubusercontent.com/shamair28/OpenCAFDMap/main/definitions/README.md
- CAFD-000000F9-Namen: https://raw.githubusercontent.com/shamair28/OpenCAFDMap/main/definitions/untrimmed/bmw/000000F9.tsv.gz
- Lizenz: https://raw.githubusercontent.com/shamair28/OpenCAFDMap/main/LICENSE
- Release v3.0.0: https://github.com/shamair28/OpenCAFDMap/releases/tag/v3.0.0
- Docs-Seite: https://shamair28.github.io/OpenCAFDMap-docs/

**nbt-coding (MIT)**
- https://github.com/adityadroid/nbt-coding
- https://raw.githubusercontent.com/adityadroid/nbt-coding/main/nbtcoding/caf.py
- https://raw.githubusercontent.com/adityadroid/nbt-coding/main/nbtcoding/ecu.py
- https://raw.githubusercontent.com/adityadroid/nbt-coding/main/nbtcoding/sign.py

**E-Sys / BMW-Dokumentation**
- E-Sys User Manual „Coding with E-Sys“ v1.4 (BMW CoC Coding EG-75, 30.07.2007): https://www.obdii365.com/upload/pro/e-sys_coding_vcm_user_manual_v1_4.pdf
- EdiabasX SGBD Reference (PROZESSKLASSEN, IDENT/F150): https://emdzej.github.io/ediabasx-docs-sgbd/sgbd/EWSIKDME und https://emdzej.github.io/ediabasx-docs-sgbd/sgbd/RLM_1R
- BMW-Werkstatthandbuch E46, ZCS/FA-Codierung (Zeitkriterium MMYY, E-/HO-Wort): https://workshop-manuals.com/bmw/3_series_e46/316i_n46_sal/8_si_diagnosis_encoding/10__coding_information/2_idc__bmw_displus_and_modic_iii_encoding_zcs_fa/
- BMW-Hacking-Wiki, Vehicle Order: https://antoniovazquezblanco.github.io/BMW-Hacking/general_info/vehicle_order

**ELM327 / BMW-CAN**
- Quantex ELM327-Doku (BMW Extended Addressing, Beispiel `22F150` → `0F25F0`): https://www.quantexlab.com/en/develop/elm327.html
- OVMS-Mailingliste (BMW i3, ATCEA): https://lists.openvehicles.com/archives/list/ovmsdev@lists.openvehicles.com/message/IMLSGRPCPG53OQ7I36WI3XIPTD7E6SOH/
- BMW F/G-Analyse (Gist): https://gist.github.com/brandonros/3e4eb6b39d77e2e7469abdf44ab4c7f3 (nur Suchtreffer)

**Projekte und PyPI**
- EdiabasLib: https://github.com/uholeschak/ediabaslib
- python-OBD: https://pypi.org/pypi/obd/json · https://github.com/brendan-w/python-OBD
- python-can: https://pypi.org/pypi/python-can/json · Backends: https://raw.githubusercontent.com/hardbyte/python-can/main/can/interfaces/__init__.py
- can-isotp: https://pypi.org/pypi/can-isotp/json · https://raw.githubusercontent.com/pylessard/python-can-isotp/master/isotp/address.py
- udsoncan: https://pypi.org/pypi/udsoncan/json
- bleak: https://pypi.org/pypi/bleak/json
- mcp: https://pypi.org/pypi/mcp/json
- ELM327-emulator: https://pypi.org/pypi/ELM327-emulator/json · https://github.com/Ircama/ELM327-emulator
- SwiftOBD2: https://github.com/kkonteh97/SwiftOBD2
- AndrOBD: https://github.com/fr3ts0n/AndrOBD
- Scapy HSFZ: https://scapy.readthedocs.io/en/latest/api/scapy.contrib.automotive.bmw.hsfz.html

**Foren und Dritte** (teils nur als Such-Snippet; Fetch blockiert)
- bimmerfest „BMW CAFD ID Cheat Sheet“: https://www.bimmerfest.com/threads/bmw-cafd-id-cheat-sheet.781953/ (blockiert; „HU_CIC/ENTRY: CAFD_000000F9“ nur im Snippet)
- f30.bimmerpost „Coding error. CAFD not found“: https://f30.bimmerpost.com/forums/showthread.php?t=1030908&page=9 (blockiert)
- u11.bimmerpost (iCloud-Sicherung des Backup-Ordners): https://u11.bimmerpost.com/forums/showthread.php?p=30249279 (nur Snippet)
- phtmperformance, Leitfaden zum Backup-Export (Drittanbieter): https://phtmperformance.com/journal/guides/bimmercode-backup-export/ (nur Snippet)
- NCS Dummy: https://www.bimmerforums.com/forum/showthread.php?p=19766272 (nur Snippet)
- brodee227/bmw-f: https://github.com/brodee227/bmw-f · jokinawa/bmw-f: https://github.com/jokinawa/bmw-f (nur Suchtreffer)
- kdrcoding/fake-car: https://github.com/kdrcoding/fake-car (nur Suchtreffer)
