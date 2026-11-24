# 06 – HU_ENTRY (Radio Professional) im Expertenmodus: Kandidatenparameter, Bluetooth und ICM-Flags

Fahrzeug: BMW 116i F20, Bauzeit 01/2012, N13, Schaltgetriebe, Radio Professional (Steuergerät **HU_ENTRY**, ohne Navi, 6,5"-CID, iDrive-Controller), Deutschland.
Grundlage: der dekodierte HU_ENTRY-Codierstand des Halters (`CAFD_000000F9_007_007_001`) und die Backup-Differenzen aus `BACKUP_ANALYSIS.md`.
Werkzeug des Halters: BimmerCode inkl. Expertenmodus. Recherchestand: 24.11.2026.
Maschinenlesbarer Katalog: `06_idrive_hu_entry_expert.json` (30 Einträge, Präfix `hu_entry.x_` bzw. `icm.x_`).

## Evidenz-Tags

| Tag | Bedeutung |
|---|---|
| **[DOK]** | In einer zitierten Quelle dokumentiert, an diesem Auto **nicht** getestet. |
| **[WAHRSCHEINLICH]** | Aus dokumentierten Fakten abgeleitet, nicht direkt für HU_ENTRY/F20 belegt. |
| **[EXPERIMENTELL]** | Einzelne oder widersprüchliche Forenberichte bzw. nicht verifizierte Sammlungen, oft für HU_CIC/HU_NBT statt HU_ENTRY. |
| **[NICHT KOMPATIBEL]** | Laut Quellen auf dieser Hardware nicht möglich. |
| **[UNBEKANNT]** | Keine belastbare Quelle gefunden. |

> **Methodik und Grenzen:** bimmerpost/1addicts/2addicts (Zugangsprüfung), bimmerfest (Weiterleitung auf eine Bezahl-Bot-Schranke), motor-talk und 1erforum (HTTP 403) waren **nicht abrufbar**. Aussagen aus diesen Foren beruhen auf **Suchmaschinen-Snippets** und sind so gekennzeichnet. Vollständig gelesen habe ich: Community-Cheat-Sheets (OpenCAFDMap `definitions/community-cheatsheets`, identisch mit packetpilot/bmw-f `cheats`), Dauxdu/bmw-coding, drei öffentliche Google-Tabellen (CSV-Export), die BimmerCode-F20-Seite, den bmw-syndikat-Datenbankeintrag, den bmw-syndikat-Thread zu BT-Streaming, die FISCON-Produktseite, die Servicemenü-Anleitungen (oemnavigations, keepyourcarsafe) und die UN-ECE-R48-Änderung (Amend. 10) als PDF.
> Der Wortlaut von § 23 StVO auf gesetze-im-internet.de war nicht abrufbar (HTTP 503). Ich stütze mich dort auf Sekundärquellen.
> **Grundsatz:** Ein Parameter im CAFD beweist **nicht**, dass die Funktion auf HU_ENTRY ohne passende Hardware, Software oder Freischaltung (FSC) wirkt.

---

## 1. Kurzfazit

1. **Wichtigster neuer Befund:** Die CAFD-ID **000000F9** ist in mehreren Cheat-Sheets dem **HU_CIC/HU_CICHB** zugeordnet, u. a. „ekfxisid“ für **F020/F030**. Der HU_ENTRY verwendet also sehr wahrscheinlich den **CIC-Parameterkatalog** [WAHRSCHEINLICH]. Deshalb stehen M-Drive-, DVD-Speedlock-, Logic7- oder Entwickler-Parameter im CAFD, auch wenn die Hardware fehlt.
   Bestätigung auf Byte-Ebene: Die Backup-Änderung **Block 3000, Byte 7, 0x5B → 0x6B** (Bits 4–5 von 01 auf 10) entspricht genau der Lage von `MACRO_FDS` (Byte 7, Maske 0x30) im F020/F030-Sheet, nämlich `only_popup` → `popup_and_config`. [DOK für die Lage im Sheet; Übereinstimmung am Auto nachgewiesen]
2. **Bluetooth (Block 3003): Audio-Streaming lässt sich auf diesem HU_ENTRY nicht per Codierung freischalten.** [NICHT KOMPATIBEL]
   - Die eigene Codierung zeigt `PHONE_TYPE = no_phone`, `MICROPHONE = no_microphone` und `USB_AVAILABLE = nicht_aktiv`. Das spricht stark für ein Auto **ohne 6NH** [WAHRSCHEINLICH].
   - Laut Foren braucht HU_ENTRY für Freisprechen ein BMW-FSC (AppID 0x82, an die Fahrgestellnummer gebunden), ein Mikrofon und eine FA-/VO-Änderung. Für A2DP-Streaming braucht ENTRY zusätzlich eine **Combox**.
   - Die vier vom Halter gesetzten Schalter (`CDMM_BLUETOOTH_AUDIO`, `BT_MODUL_ON_OFF`, `AUDIO_PLAYER_ON_OFF`, `BASIC_VR_ON_OFF`) bleiben daher sehr wahrscheinlich ohne Wirkung. → Auf die Backup-Werte zurücksetzen.
3. **ICM-Flags des Halters sind identifiziert:**
   - Byte 28 (00 → 01) = `IcmKod_B_Sportlenkung = verbaut`. Die Community nutzt das als SPORT+-Freischaltung, Teil 1.
   - Byte 36, Bit 3 (00 → 08) = `IcmKod_B_InitEco = verbaut` = **„Start in ECO mode“**. [DOK]
   - `Sportlenkung verbaut` ohne 2VL: Ein Hardwareschaden ist nicht dokumentiert. Foren melden aber DSC-/RPA-Fehlermeldungen. Ohne KOMBI-Teil 2 (vom Halter zurückgesetzt) ist kein Nutzen erkennbar. Der Eingriff betrifft die Fahrdynamik. → **Empfehlung: zurücksetzen.** [EXPERIMENTELL]
4. **Am ehesten lohnend (risikoarm, rückgängig zu machen):**
   - Servicemenü per Controller-Sequenz (Parameter steht schon auf `aktiv`) [EXPERIMENTELL/WAHRSCHEINLICH].
   - `VOL_MAX_ON` moderat anheben [EXPERIMENTELL].
   - Tests von `HIST_GAS_CONSUMP`, `SETTINGS_INFO_DISPLAY`, `SERVICE_HISTORY` [UNBEKANNT → einfach ausprobieren].
   - Sportanzeigen: Menü erscheint wahrscheinlich, Werte stehen laut Berichten auf HU_ENTRY ohne Navi auf 0 [EXPERIMENTELL].
5. **Ohne Hardware wirkungslos bzw. nicht sinnvoll:** Video/Speedlock (zudem § 23 Abs. 1a StVO), USB/Albumcover, DAB (Tuner fehlt vermutlich), Logic7/B&O-Menüs, M-Drive/M-Digitaltacho, Colour-Switch (nur NBT_EVO belegt). [NICHT KOMPATIBEL bzw. EXPERIMENTELL]

---

## 2. CAFD-Familie und Abgleich mit den Backups

| Beobachtung | Quelle | Status |
|---|---|---|
| `cafd id="000000F9" name="HU_CICHB" series="F020,F030"` (ekfxisid) sowie HU_CICHB-Einträge bei Almaretto, aknight720, Bundang_Thunder (F01/F10) und HU_CIC (F010, F025) | OpenCAFDMap community-cheatsheets | [DOK] |
| Im F020/F030-Sheet: `MACRO_FDS` 3000/Byte 7/Maske 0x30; `EFF_DYN_SPORT_CID` 3000/Byte 47/0x10; `EFF_DYN_SPORT_UNIT` 3000/Byte 61/0x04; `SPEEDLOCK_X_KMH_MIN/MAX` 3000/Byte 23/24 | ekfxisid.xml | [DOK] (Offsets können je CAFD-Version abweichen) |
| HU-Backup-Diff Block 3000, Byte 7: 0x5B → 0x6B | BACKUP_ANALYSIS.md | passt zu `MACRO_FDS` only_popup → popup_and_config [WAHRSCHEINLICH, sehr gute Übereinstimmung] |
| ICMQL `0000067B`: `IcmKod_B_Sportlenkung` Byte 28 (Maske 0xFF); `IcmKod_B_InitEco` Byte 36 (Maske 0x08) | ekfxisid, Almaretto, Botho, Bundang_Thunder | [DOK] |
| ICM-Backup-Diff: Byte 28 00 → 01, Byte 36 00 → 08 | BACKUP_ANALYSIS.md | passt exakt zu beiden Flags |
| `SPEEDLOCK_X_KMH_*` Standard „3_kmh“ (HU_CIC-Tabelle: „3_kmh = 3 or 8_kmh = 8“) | Google-Tabelle (NL) | passt zum Ist-Wert 3_kmh |

**Konsequenz:** Funktionsbeschreibungen für **HU_CIC** treffen auf die Parameter*namen* und *-werte* im HU_ENTRY-CAFD wahrscheinlich zu. Ob die Funktion auf HU_ENTRY *wirkt*, hängt aber von Software und Hardware der ENTRY-Headunit ab. Für HU_ENTRY selbst gibt es fast keine Erfahrungsberichte.

---

## 3. TELEFON (Block 3003) – Kernfrage Bluetooth

### 3.1 Befunde

| # | Aussage | Quelle | Tag |
|---|---|---|---|
| 1 | Basic-Headunit (HU-B, „Radio Professional“): Bei **6NH** ist die Telefonfunktion **in der Headunit** realisiert. Eine Combox gibt es nur mit **6NL** bzw. Navigation. BT-Audio-Streaming, Albumcover, Office usw. sind **Combox-Funktionen**. | BMW ST1113 F30 Entertainment & Communication (US-F30) | [DOK] für F30 US, für F20 [WAHRSCHEINLICH] |
| 2 | „It appears the HU_ENTRY needs a FSC code to enable USB and Bluetooth. AppID 129 (0x81) – USB music, AppID 130 (0x82) – Bluetooth handsfree.“ FSC sind an die Fahrgestellnummer gebunden und nur über BMW AG erhältlich. Dazu kommt eine VO-Codierung des HU_ENTRY. | bimmerpost „Upgrading from HU_ENTRY no BT to HU_ENTRY with BT+USB“ (Snippet) | [EXPERIMENTELL] |
| 3 | „With CHAMP2 or ENTRY head units you must have a standalone Combox in order to have A2DP BT streaming.“ HU_ENTRY mit 6NH lässt sich nicht auf Streaming codieren. **ENTRYNAV** hat die Combox-Funktionen integriert, also Codierung auf 6NS möglich. | bimmerpost „EBT coding F20?“ / „People who coded 6NH to 6NK“, bimmerfest (Snippets) | [EXPERIMENTELL] |
| 4 | F30 2013, HU_ENTRY (DAB) + 6NH, Combox Telematik nachgerüstet, FA 6NH → 6NK: Die HU ließ sich danach **nicht mehr codieren** (Fehler beim Codieren). | digital-kaos (Snippet) | [EXPERIMENTELL] |
| 5 | F20/F21: „Mit dem Professional Radio und Bluetooth-Freisprecheinrichtung ist kein Streaming möglich“, es braucht SA **6NS**. Ein 2014er Fahrzeug streamt ohne Codierung. | bmw-syndikat-Thread (gelesen), motor-talk (Snippet) | [EXPERIMENTELL]; Jahrgangsabhängigkeit wahrscheinlich (ENTRYNAV ab 07/2014) |
| 6 | Eigene Codierung: `PHONE_TYPE = no_phone`, `MICROPHONE = no_microphone`, `USB_AVAILABLE = nicht_aktiv`. Diese Werte werden normalerweise per VO aus dem Fahrzeugauftrag berechnet. | Halter-CAFD | [WAHRSCHEINLICH] keine 6NH ab Werk |
| 7 | In den Backups des Halters taucht **kein Combox-Steuergerät** (CMB_MEDIA) auf. Die Backups enthalten aber nur die gesicherten Steuergeräte. | BACKUP_ANALYSIS.md | [WAHRSCHEINLICH], in der BimmerCode-Steuergeräteliste prüfen |
| 8 | BimmerCode „Bluetooth audio streaming“ gibt es nur für HU_NBT/HU_NBT_EVO bzw. Combox_Media, **nicht** für HU_ENTRY. | bimmercode.app/cars/f20 | [DOK] |

### 3.2 Urteil

- **Enthält ein F20-HU_ENTRY ohne 6NH Bluetooth-Hardware?** Physisch **[UNBEKANNT]**. Es wurde keine Quelle gefunden, die Platine oder Bestückung beschreibt. Sicher ist: Selbst wenn ein BT-Funkteil vorhanden wäre, ist die Funktion über **FSC 0x82** gesperrt. Dieses FSC vergibt nur BMW, gebunden an die Fahrgestellnummer. Zusätzlich fehlen Mikrofon (`no_microphone`), USB-Kabelsatz und eine FA-konsistente VO-Codierung.
- **BT-Audio-Streaming nur per Codierung?** **Nein** [NICHT KOMPATIBEL]. Für die 2012er HU_ENTRY verlangen alle Quellen eine **Combox**. Selbst Fahrzeuge **mit** 6NH konnten laut Foren nicht auf Streaming codiert werden. Erfolgsberichte betreffen HU_ENTRYNAV (ab 07/2014), HU_CIC/NBT oder Fahrzeuge mit Combox.
- **Was wäre nötig?**
  - Für Freisprechen: 6NH-Hardware (Headunit-Variante/FSC 0x82, Mikrofon, ggf. USB mit FSC 0x81), FA-Änderung und VO mit E-Sys.
  - Für Streaming zusätzlich: Combox Media (CMB_MEDIA) mit FA 6NK/6NL; 6NS laut Foren nur für NBT bzw. ENTRYNAV.
  - Aufwand hoch, mit dem Risiko „HU nicht mehr codierbar“ (Befund 4).
  - Realistische Alternativen: Nachrüst-Freisprechanlage (FISCON Pro nennt „1er – F20, F21“ mit Radio Professional und A2DP, Bedingung LWL/MOST-Schnittstelle am Radio und spezielle Codierung; **Herstellerangabe, nicht geprüft**), AUX oder Headunit-Tausch.
- **Empfehlung:** Die vier 3003-Schalter auf die Backup-Werte zurücksetzen. `PHONE_TYPE`/`MICROPHONE` **nicht** von Hand ändern.

### 3.3 Hardwarevariante selbst feststellen (ohne Werkstatt)

1. **iDrive:** Gibt es im Hauptmenü den Punkt „Telefon“ und unter Einstellungen einen Punkt „Bluetooth“? Ohne 6NH ist beides vermutlich nicht vorhanden [WAHRSCHEINLICH].
2. **USB-Buchse** in Mittelkonsole oder Armlehne: 6NH heißt „Freisprecheinrichtung mit **USB-Schnittstelle**“. Fehlt die Buchse, passt das zu `USB_AVAILABLE = nicht_aktiv`.
3. **Mikrofon** am Dachhimmel bzw. im Bereich Innenleuchte/Sonnenblende Fahrerseite (1erforum-Snippet). FISCON sieht für sein Mikrofon den Einbauplatz in der Innenleuchte vor.
4. **Fahrzeugauftrag (FA):** mit E-Sys auslesen und auf **6NH / 6NS / 6NK / 6NL** prüfen. Was **6FL** und **6VC** bedeuten, ließ sich nicht belegen [UNBEKANNT]; mit einem FA-Decoder bzw. ETK nachschlagen. Die Fahrgestellnummer dabei nur privat verwenden.
5. **FSC-Liste** der Headunit (E-Sys, FSC-Extended): Sind AppID **0x81/0x82** vorhanden?
6. **Steuergeräteliste** in BimmerCode/E-Sys: Taucht **CMB_MEDIA** (Combox) auf?
7. **Teilenummer** auf dem Etikett der Headunit (Ausbau nötig) und Abgleich im ETK. Teilenummern für die BT-Variante habe ich nicht gefunden [UNBEKANNT].

### 3.4 Weitere Parameter in 3003

| Parameter | Ist | Bedeutung laut Quellen | Für dieses Auto |
|---|---|---|---|
| `PHONE_TYPE` | no_phone | Telefontyp, aus FA berechnet | Hinweis „keine 6NH“ [WAHRSCHEINLICH]; nicht ändern |
| `MICROPHONE` | no_microphone | Mikrofonkonfiguration | dto. |
| `INBAND_RINGING` | ? | Klingelton des Handys über die Lautsprecher (nur iPhone); HU_CIC 3003, Combox 3001 | ohne Telefon wirkungslos [WAHRSCHEINLICH] |
| `RINGTONE` | ? | Auswahl des BMW-Klingeltons, wenn Inband aus | dto. |

---

## 4. ICM-Flags des Halters

### 4.1 `IcmKod_B_InitEco = verbaut` – [DOK]
- Bedeutung: Nach jedem Motorstart ist **ECO PRO** aktiv statt COMFORT. BimmerCode-Standardoption **„Start in ECO mode“** (ICMQL). Mehrere Cheat-Sheets nennen ICMQL 3000, Byte 36, Maske 0x08, genau die Änderung im Backup.
- Risiko gering, rückgängig zu machen. Wer lieber in COMFORT startet, setzt `nicht_verbaut`. ECO PRO ist beim F20 Serie.

### 4.2 `IcmKod_B_Sportlenkung = verbaut` – [EXPERIMENTELL], sicherheitsrelevant
- **Wortbedeutung:** „Sportlenkung verbaut“, also Variable Sportlenkung (SA 2VL) [WAHRSCHEINLICH]. SPORT+ ist ab Werk beim F20 an bestimmte Ausstattungen gebunden: laut 1erforum-Snippet u. a. 2TB, 2VL, 2VF, 7AC, 337. Laut Bericht 05 (BMW-Presse-Snippet) Sport Line mit Variabler Sportlenkung. Die Angaben sind uneinheitlich.
- **Nutzung in der Community:**
  - Koreanisches Sheet: „Sport+ mode activation → KOMBI“.
  - Dauxdu: „ICMKOD_B_SPORTLENKUNG → aktiv // Sport+ mode“.
  - BimmerCode nennt für SPORT+ „(1 of 2)“ im ICMQL und „(2 of 2)“ im KOMBI, mit dem Hinweis, das nicht zu nutzen, wenn SPORT+ ab Werk vorhanden ist.
  - Dass BimmerCode „(1 of 2)“ genau dieses Byte setzt, ist [WAHRSCHEINLICH], aber nicht bestätigt.
- **Gemeldete Nebenwirkungen (nur Snippets):**
  - Reifendruck- (RPA) und DSC-Fehlermeldungen, nach Neustart gelöscht.
  - „Car throws many errors“.
  - „Wer Sportlenkung im ICM codiert, muss sie auch im DSC codieren.“
  - Ohne KOMBI-Teil erscheint SPORT+ nicht oder ist nicht wählbar.
- **Zustand am Auto:** Die KOMBI-Änderungen vom 27./28.06.2025 hat der Halter zurückgesetzt. SPORT+ ist daher vermutlich **nicht** nutzbar, das ICM-Flag aber gesetzt [WAHRSCHEINLICH].
- **Schädlich ohne 2VL?**
  - Ein Hardwareschaden ist **nirgends dokumentiert**.
  - **Unbekannt** ist, ob ICM/DSC die Kennung auch für Lenkübersetzung oder Lenkwinkelberechnung nutzen. Das wäre bei einer mechanisch variablen Zahnstange denkbar, ist aber nicht belegt [UNBEKANNT].
  - SPORT+ selbst bedeutet laut Foren DSC im Traktionsmodus (DTC), also weniger Stabilitätsregelung.
  - **Bewertung: Risiko sicherheitskritisch, Nutzen gering.** → Auf `nicht_verbaut` zurücksetzen (Backup-Wert) und den Fehlerspeicher von ICM/DSC/RPA prüfen.

### 4.3 Zusammenhang mit `MACRO_FDS = popup_and_config`
- „SPORT konfigurierbar“ braucht laut BimmerCode und Foren **zwei** Teile:
  - HU: `MACRO_FDS`. Die BimmerCode-Standardoption gibt es nur für HU_NBT/NBT_EVO.
  - ICM: `IcmKod_B_SportIndividualisierbar = ein/01`, in BimmerCode „SPORT driving mode configurable (2 of 2)“.
  - Nur mit dem HU-Teil erscheint das Menü, die Auswahl lässt sich aber nicht treffen (NBT-Bericht, Snippet). Bei manchen ICM-Ständen heißt die Variable `QdmKfvSportIndividualisierbarDep`.
- Der Halter hat **nicht** SportIndividualisierbar gesetzt, sondern Sportlenkung. Für die Konfigurierbarkeit ist Sportlenkung laut Quellen nicht der richtige Schalter [EXPERIMENTELL].
- HU_ENTRY: Es gibt keinen Erfahrungsbericht. Der bmw-syndikat-Eintrag (F20 gelistet) nennt nur ICM + HU_NBT. → [UNBEKANNT]
- Optionen:
  - (a) `MACRO_FDS` auf `only_popup` zurücksetzen, oder
  - (b) zusätzlich ICM „SPORT driving mode configurable (2 of 2)“ testen. Das ist ein ICM-Eingriff, Risiko mittel. Beim 116i ohne adaptive Dämpfer/2VL betrifft „Fahrwerk/Lenkung“ vermutlich nur die EPS-Kennlinie [UNBEKANNT].

---

## 5. HMI-Block 3000 – Parameter im Einzelnen

| Parameter (Ist) | Funktion laut Quellen | HU_ENTRY-Evidenz | Tag / Empfehlung |
|---|---|---|---|
| `SERVICE_MENUE` (aktiv) | Verstecktes Servicemenü. Ohne Navi: im Hauptmenü Controller **≥ 10 s nach links** halten, dann 3 Rasten rechts, 3 links, 1 rechts, 1 links, 1 rechts drehen, einmal drücken. Danach steht „Service“ als letzter Punkt unter „Einstellungen“. Bei CIC/Navi Prof. stattdessen nach oben/vorne halten. Inhalt (CIC): GPS/Navi, Telefon/BMW Services, Gracenote, TV; laut bimmerfest-Nutzer nur Anzeige. | Kein direkter Bericht. Laut BMW ist der Basic-Controller „nur nach links/rechts kippbar“, was zur Links-Variante passt. | [EXPERIMENTELL]/[WAHRSCHEINLICH]. **Ausprobieren**, nichts verstellen. Nicht verwechseln mit dem KOMBI-Testmenü (Bericht 04). |
| `ENTWICKLER_MENUE` (nicht_aktiv) | HU_CIC F30 2012: Entwicklermenü in den Einstellungen mit Datum/Build/Versionen; wird per Codierung eingeblendet, keine Tastenkombination. HU_NBT F020/F030 ebenfalls gelistet. | Keiner | [EXPERIMENTELL]. Inhalt auf ENTRY unbekannt, also nur ansehen. Nutzen gering. |
| `EFF_DYN_SPORT_CID`, `EFF_DYN_SPORT_UNIT` (nicht_aktiv) | Menü „Sportanzeigen“ (Leistung/Drehmoment) bzw. Einheitenwahl | HU_ENTRY ohne Navi (2addicts, bimmerpost; Snippets): Menü erscheint, **Werte bleiben 0**. HU_ENTRYNAV funktioniert. Diesel bzw. ältere Motoren liefern teils keine Daten. N13 unbelegt. | [EXPERIMENTELL], Kompatibilität unwahrscheinlich. Gefahrloser Test. |
| `M_DIGITAL_TACHO`, `M_DIGITAL_TACHO_EINH` (nicht_aktiv) | M-Digitaltacho in der Informationsanzeige bzw. Einheiten | F30 2012 HU_CIC: Checkbox erscheint, **ohne Funktion**. M2: an die EfficientDynamics-Anzeige gekoppelt. | [EXPERIMENTELL], unwahrscheinlich. Für einen Digitaltacho stattdessen KOMBI `BC_DIGITAL_V` nutzen (Bericht 04). |
| `MDRIVE`, `MDRIVE_CONFIG` (1_menu), `M_KEY_SETTINGS` (nicht_aktiv) | M-Drive-Menü, M1/M2-Belegung, M-Tasten | F30 HU_CIC: Menü erscheint, **nicht wählbar**. M2: 2_menu ergibt M1/M2. | [EXPERIMENTELL], ohne M-Hardware sinnlos. |
| `MACRO_FDS` (popup_and_config; Original only_popup) | SPORT-Pop-up mit Konfiguration | Siehe 4.3 | [EXPERIMENTELL]/[UNBEKANNT] |
| `FDS_POPUP_DEACTIVATE` (aktiv), `ECO_FDS_POPUP` (nicht_aktiv) | Checkbox „Fahrmodus-Pop-up aus“ wird angeboten (Snippet, Standard aktiv). ECO_FDS_POPUP gehört zur ECO-PRO-Nachrüstung bei HU_CIC, Wirkung unklar. | Keiner | [EXPERIMENTELL]; kein Handlungsbedarf |
| `HIST_GAS_CONSUMP` (nicht_aktiv), `HIST_CONSUMP_AVERAGE`, `HIST_GAS_CONSUMP_SCALE_1..4` | Verbrauchshistorie bzw. -grafik. Nur als `aktiv` in einer HU_NBT-Liste ohne Beschreibung. Ein HU_CIC-ECO-Bericht: „Fuel Consumption Graphs worked in all modes“, Parameter unklar. | Keiner | [UNBEKANNT]. Test von `HIST_GAS_CONSUMP` risikoarm, **Skalenwerte nicht ändern**. |
| `EFF_DYN_SYS_CID` (aktiv), `ECO_MODE`, `ECO_TIPPS`, `ECO_LIMIT` | EfficientDynamics-/ECO-PRO-Anzeigen und -Tipps; ECO_LIMIT vermutlich die ECO-PRO-Tempovorgabe (unbelegt) | ECO PRO ist F20-Serie | [EXPERIMENTELL]; Werksumfang, nicht ändern |
| `OELSTANDSMENUE` (nicht_aktiv), `OELSTAND_OENS` (aktiv) | Ölstandsmenü bzw. Umschaltung alte → neue Darstellung (HU_CIC, bimmerfest-Snippet; auf älterem F10 erfolglos) | Keiner | [EXPERIMENTELL]. Erst prüfen, ob „Motorölstand“ unter Fahrzeugstatus schon angezeigt wird. |
| `COLOUR_SWITCH` (nicht_aktiv), `COLOUR_SWITCH_LINES` (6 Optionen) | NBT_EVO G11/G30: 01 Sport, 02 Urban, 03 Modern, 04 Luxury („Ambiente“). F25/G20: Farbwahl der Ambientebeleuchtung. | Keiner; Ambiente-Hardware fehlt vermutlich | [EXPERIMENTELL], unwahrscheinlich |
| `HIGH_END_AUDIO_MENUE` (kein_menue), `L7_SURROUND_CONFIG`, `LOGIC7_SYMBOL` | B&O-Menü (volle_insz) statt L7-Checkbox; L7-Schieberegler („kaum mehr als ein/aus“); L7-Symbol | Keiner; Logic7 = Harman-Kardon-Signalverarbeitung | [EXPERIMENTELL]. Ohne HK-Verstärker nur Kosmetik. |
| `DAYDRIVING_LIGHT` (perm_off, 3 Optionen) | perm_off → standard: Menüpunkt „Tagfahrlicht“ ein/aus (HU_CIC „Yes“; HU_NBT werte=02). Die Funktion selbst liegt im FEM. | Keiner | [EXPERIMENTELL]. **Rechtlich:** siehe Abschnitt 8. |
| `COMFORT_OPENING`, `KEY_CONF_COMFORT`, `KEY_CONF_UNLOCK_VEHICLE`, `SETTINGS_DOORLOCKING`, `DOOR_LOCKING_SELECTABLE` | Menüpunkte Türen/Schlüssel; COMFORT_OPENING (HU_NBT, „en cours de test“): Doppelklick öffnet die Fenster zu 75 % | Keiner | [UNBEKANNT]. Funktionen liegen im FEM. |
| `SETTINGS_TIP_BLINKING`, `SETTINGS_HOMELIGHT_PERIOD` | Menüpunkte Komfortblinken bzw. Heimleuchtdauer (Namensdeutung) | Keiner | [UNBEKANNT] |
| `SETTINGS_INFO_DISPLAY` (nicht_aktiv), `SETTINGS_LIMIT` | Informationsanzeige: Auswahl der BC-Inhalte im Kombi über das iDrive (HU_NBT 3001, Standard aktiv). LIMIT ohne Quelle. | Keiner | [EXPERIMENTELL]. Test risikoarm; leer oder nicht wählbar → zurück. |
| `SPEEDLOCK_X_KMH_MIN/MAX` (3_kmh), `SPEEDLOCK_FREISCHALTMENU`, `SL01_VIDEO` … `SL21` | Tempo-Schwelle der Fahrsperre; FF hebt sie auf. SLxx sperren einzelne Funktionen (HU_NBT z. B. SL06/07/21 = Bedienungsanleitung). FREISCHALTMENU nur für HU_MGU belegt (plus Tastenkombination). | HU_ENTRY: **kein Video in Motion** (Dauxdu) | [NICHT KOMPATIBEL] für Video; **nicht ändern** (§ 23 Abs. 1a StVO) |
| `CDMM_VIDEO`, `VIDEO_NUR_MIT_HANDBREMSE`, `CDMM_USB`, `USB_AVAILABLE` (nicht_aktiv), `CDMM_USB_COVER_ART`, `PICTURE_ALBUM_ARTS` | Video, USB-Audio, Albumcover | USB braucht FSC 0x81 und 6NH-Hardware; Cover = Combox-Funktion; Video via USB nur NBT | [NICHT KOMPATIBEL] |
| `FAS_INSZENIERUNG` | – | – | [UNBEKANNT]; nicht ändern |
| `LEGAL_DISCLAIMER_TIME` (kein_ld) | Rechtshinweis beim Start aus bzw. mit Timeout | Steht bereits auf kein_ld | Kein Handlungsbedarf |
| `MODE_HARDKEY` (more_sources) | – (Wertname deutet auf die Quellenwahl der MODE-Taste hin) | – | [UNBEKANNT] |
| `ONBOARDCOMPUTER_DATE`, `TRAVEL_BC`, `EXTENDED_CC_MESSAGES` | – (Namensdeutung: Datum im BC, Reise-BC, erweiterte CC-Meldungen) | – | [UNBEKANNT] |
| `SERVICE_HISTORY` | Servicehistorie unter Fahrzeuginfo (HU_NBT/HU_CIC-Sammlungen; BimmerCode nur NBT) | Keiner | [EXPERIMENTELL]; gefahrloser Test |

---

## 6. AUDIO (Block 3002)

- **`RADIO_DAB` (nicht_aktiv):** Alle Quellen verlangen einen **DAB-Tuner** in der Headunit (SA 654, erkennbar an DAB-Buchsen an der Rückseite, Band III gelb), dazu DAB-Antenne/-Diversity, Leitungen und eine FA- und VO-Anpassung. Bei HU_CIC brachte die Codierung allein nur „partly“ etwas (mehr FM-Sender, keine DAB-Sender). → Ohne Tuner zwecklos [WAHRSCHEINLICH]. Ob dieses Auto DAB hat, ist [UNBEKANNT]; `RADIO_DAB = nicht_aktiv` spricht eher dagegen.
- **`VOL_MAX_ON`:** Maximale Einschaltlautstärke. Standard hex 19 (≈ 25 %), 1E ≈ 30 %, 28 ≈ 40 %. Für hex 32 widersprechen sich die Quellen (50 % bzw. 100 %). Belegt für HU_CIC/HU_CICHB/HU_NBT; HU_ENTRY teilt die CAFD-ID mit HU_CICHB. → [EXPERIMENTELL], Kompatibilität wahrscheinlich. Moderat erhöhen.
- **`TIME_OUT_GONG`:** keine Quelle gefunden [UNBEKANNT].

## 7. APIX (Block 3005) – Display-Dimmung

- Einziger Bericht: G05/HU_MGU, `APIX_CID_UND_ZIN` → `DIM_CURVE_X2` von 0x1F,0xC0 auf 0x00,0x00. Danach dimmte das Display tagsüber nicht mehr ab (bimmerpost-Snippet). [EXPERIMENTELL]
- Für HU_ENTRY bzw. die F-Serie gibt es **keine dokumentierte sichere Einstellung**. Wenn überhaupt: nur einen Stützpunkt ändern, Originalbytes notieren und bei Dunkelheit prüfen (Blendung). Die Bedeutung von `DIM_FADE_*` ist [UNBEKANNT].

---

## 8. Rechtliche Hinweise

- **Tagfahrlicht (`DAYDRIVING_LIGHT`):** UN-ECE R48 (Rev. 12, Amend. 10) verlangt:
  - 6.19.7.1: Das TFL schaltet sich automatisch ein, sobald der Antrieb betriebsbereit ist.
  - 6.19.7.2: Manuelles Abschalten ist nur zulässig, wenn es sich oberhalb von **15 km/h** bzw. nach **100 m** automatisch wieder einschaltet. Ältere Fassungen nannten 10 km/h.
  - Ein dauerhaft per iDrive abschaltbares TFL entspricht dem aktuellen Wortlaut nicht.
  - Welche Fassung für die Typgenehmigung des 2012er F20 galt und was das für die Betriebserlaubnis bedeutet, ist [UNBEKANNT]. Im Zweifel einen Sachverständigen fragen.
- **Speedlock/Video:**
  - § 23 Abs. 1a StVO: Ein Gerät mit Bildschirm darf während der Fahrt nur genutzt werden, wenn dafür ein kurzer, den Verhältnissen angepasster Blick genügt.
  - Die OLG-Karlsruhe-Entscheidung zu einem eingebauten Touchscreen (200 €, 2 Punkte, 1 Monat Fahrverbot; Sekundärquelle) zeigt, dass auch Fahrzeugdisplays erfasst sind.
  - Speedlock nicht aufheben. Auf HU_ENTRY gibt es ohnehin keine Videoquelle.
- **ICM/SPORT+:** Eingriff in die Fahrdynamik bzw. das DSC-Verhalten, Folgen für Betriebserlaubnis und Versicherung möglich. Nur dokumentieren, nicht empfehlen.

---

## 9. Empfehlungen (Reihenfolge)

1. **Backup** der aktuellen Codierung anlegen (HU_ENTRY, ICM) und ein Ladegerät anschließen.
2. **Zurücksetzen (Backup-Werte):**
   - HU 3003: `CDMM_BLUETOOTH_AUDIO`, `BT_MODUL_ON_OFF`, `AUDIO_PLAYER_ON_OFF`, `BASIC_VR_ON_OFF`.
   - ICM: `IcmKod_B_Sportlenkung` → nicht_verbaut.
   - Optional: `MACRO_FDS` → only_popup, falls das Konfigurationsmenü nicht funktioniert.
   - `IcmKod_B_InitEco` nach eigenem Geschmack belassen oder zurücksetzen.
3. **Ohne Codierung testen:** Servicemenü-Sequenz (Abschnitt 5), KOMBI-Testmenü (Bericht 04).
4. **Einzeltests mit geringem Risiko** (immer nur einen Parameter ändern, Ergebnis notieren):
   - `VOL_MAX_ON` (z. B. 1E/28)
   - `HIST_GAS_CONSUMP` → aktiv
   - `SETTINGS_INFO_DISPLAY` → aktiv
   - `SERVICE_HISTORY` → aktiv
   - `EFF_DYN_SPORT_CID` → aktiv (Erwartung: Werte 0)
5. **Nicht anfassen:** Speedlock/SLxx, `PHONE_TYPE`/`MICROPHONE`, `DIM_CURVE_*` (höchstens sehr vorsichtig), `FAS_INSZENIERUNG` und alle Parameter mit unbekannter Bedeutung.

---

## 10. Offene Fragen

1. Hat der HU_ENTRY ohne 6NH ein bestücktes BT-Funkteil? (Platinenfoto bzw. Teilenummernvergleich)
2. Welche SA stehen im FA? (6NH/6NS/6NK/6NL, 654 DAB; Bedeutung von 6FL/6VC)
3. Welche FSC (AppIDs) sind im HU_ENTRY hinterlegt? (E-Sys FSC-Extended)
4. Liefert die N13-DME Leistungs- und Drehmomentwerte an die HU? Funktioniert die Sportanzeige auf HU_ENTRY überhaupt?
5. Wertet HU_ENTRY `MACRO_FDS = popup_and_config` aus? Ist im ICMQL dieses CAFD-Stands `IcmKod_B_SportIndividualisierbar` oder `QdmKfvSportIndividualisierbarDep` vorhanden?
6. Nutzt das ICM `IcmKod_B_Sportlenkung` auch für Lenkwinkel oder Lenkübersetzung (DSC-Modell)? Sind nach der Änderung Fehler im ICM/DSC/RPA-Speicher abgelegt?
7. Wie heißen die dritte `DAYDRIVING_LIGHT`-Option, die übrigen `HIGH_END_AUDIO_MENUE`-Optionen und die sechs `COLOUR_SWITCH_LINES`-Optionen (in BimmerCode ablesen)?
8. Wie heißen SL02 … SL21 genau, und was sperren sie auf HU_ENTRY?
9. Zeigt das iDrive bereits „Motorölstand“ (OENS-Variante)?
10. Was bewirken `FAS_INSZENIERUNG`, `MODE_HARDKEY`, `TRAVEL_BC`, `ONBOARDCOMPUTER_DATE`, `EXTENDED_CC_MESSAGES`, `TIME_OUT_GONG`, `SETTINGS_LIMIT`, `DIM_FADE_*`?

---

## 11. Quellen

**BMW/Normen (Primär):**
- BMW ST1113 „F30 Entertainment and Communication“: https://archive.org/download/BMWTechnicalTrainingDocuments/ST1113%20F30%20Complete%20Vehicle/07_F30_Entertainment_and_Communication1.pdf (über Bericht 04 ausgewertet)
- UN-ECE R48 Rev. 12 Amend. 10 (6.19.7.x): https://www.marklines.com/statics/unece/pdf_202102/R048r12am10e.pdf (PDF gelesen)
- § 23 StVO: https://www.gesetze-im-internet.de/stvo_2013/__23.html (nicht abrufbar, HTTP 503); Sekundärquelle: https://www.wbs.legal/verkehrsrecht/olg-karlsruhe-zu-tesla-achtung-vor-ablenkung-durch-touchscreen-50874/

**Hersteller-Tool:**
- BimmerCode F20/F21: https://bimmercode.app/cars/f20 (gelesen)

**Community-Sammlungen (gelesen):**
- OpenCAFDMap community-cheatsheets (gleiche Dateien wie packetpilot/bmw-f „cheats“):
  - https://raw.githubusercontent.com/shamair28/OpenCAFDMap/HEAD/definitions/community-cheatsheets/ekfxisid.xml
  - https://raw.githubusercontent.com/shamair28/OpenCAFDMap/HEAD/definitions/community-cheatsheets/Almaretto.xml
  - https://raw.githubusercontent.com/shamair28/OpenCAFDMap/HEAD/definitions/community-cheatsheets/Botho.xml
  - https://raw.githubusercontent.com/shamair28/OpenCAFDMap/HEAD/definitions/community-cheatsheets/Bundang_Thunder.xml
  - https://raw.githubusercontent.com/shamair28/OpenCAFDMap/HEAD/definitions/community-cheatsheets/jokinawa.xml
  - https://github.com/packetpilot/bmw-f
- Dauxdu/bmw-coding:
  - https://raw.githubusercontent.com/Dauxdu/bmw-coding/HEAD/e-sys/02-Codings/Transmission/Sport-Mode.md
  - https://raw.githubusercontent.com/Dauxdu/bmw-coding/HEAD/e-sys/02-Codings/Head-Unit/iDrive-Features.md
  - https://raw.githubusercontent.com/Dauxdu/bmw-coding/HEAD/e-sys/02-Codings/Head-Unit/Video-in-Motion.md
  - https://raw.githubusercontent.com/Dauxdu/bmw-coding/HEAD/e-sys/02-Codings/Lighting/Daytime-Running-Lights.md
- Google-Tabellen (CSV-Export gelesen):
  - Community-Tabelle mit HU_CIC/NBT/ICM-Testergebnissen: https://docs.google.com/spreadsheets/d/16O4RKIMekWFCs5jPW3T_7li0yIEvgZfFI0u3l0RmSwU/pubhtml
  - Autoescaner, F30 2012 mit E-Sys: https://docs.google.com/spreadsheets/d/1G_C7954Z4094jLdbR0QjqXQYY6w6-rToothcTUPb5Fs/edit
  - X5 F15: https://docs.google.com/spreadsheets/d/1UreLsK1PwycTWeW6OL71HOoVpLtKtfwRMRSvlsiC8JY/edit
- bmw-syndikat Codier-Datenbank „Sportmodus konfigurierbar“: https://www.bmw-syndikat.de/bmwsyndikatforum/bmw_codieren_datenbank.asp?goto=140 (gelesen)
- bmw-syndikat „F21 – BJ 2013 – Bluetooth Streaming möglich?“: https://www.bmw-syndikat.de/bmwsyndikatforum/topic385314_F21_-_BJ_2013_-_Bluetooth_Streaming_moeglich__1er_BMW_-_F20___F21___F22___F23.html (gelesen)
- Servicemenü-Anleitungen (gelesen):
  - https://oemnavigations.com/blogs/news/idrive-hack-idrive-hidden-menu-in-your-bmw-a-step-by-step-guide
  - https://www.keepyourcarsafe.co.uk/blogs/coding-diagnostics/cic-equipped-vehicles-entering-the-service-menu
- FISCON Pro (Herstellerangabe): https://www.fiscon-mobile.de/products/pro_bmw.php?brand=pro (gelesen)

**Nur über Suchmaschinen-Snippets ausgewertet (Seite blockiert):**
- Bluetooth/FSC/Combox:
  - https://f30.bimmerpost.com/forums/showthread.php?t=1038266
  - https://f30.bimmerpost.com/forums/showthread.php?t=1138857
  - https://f30.bimmerpost.com/forums/showthread.php?t=851042
  - https://www.digital-kaos.co.uk/forums/showthread.php/1073089-BMW-F30-enhanced-bluetooth-coding-using-combox-Telematik-and-HU-ENTRY
  - https://www.bimmerfest.com/threads/coding-enhanced-bluetooth.762586/
  - https://www.motor-talk.de/forum/neues-radio-professional-ohne-bluetooth-audio-t4896587.html
  - https://www.1erforum.de/threads/bmw-6nh-freisprecheinrichtung-mit-usb-schnittstelle.162412/
  - https://www.motor-talk.de/forum/bluetooth-nachruesten-freischalten-t5631177.html
- Sportanzeigen:
  - https://www.2addicts.com/forums/showthread.php?t=1083314
  - https://f30.bimmerpost.com/forums/showthread.php?t=1138487
  - https://www.bimmerfest.com/threads/power-and-torque-meters-in-sport-display.723339/
- SPORT konfigurierbar / SPORT+:
  - https://www.bimmerfest.com/threads/configuring-sport-mode-tight-steering.837758/
  - https://f30.bimmerpost.com/forums/showthread.php?t=1086229
  - https://f30.bimmerpost.com/forums/showthread.php?t=920617
  - https://www.bimmerfest.com/threads/sport-in-manual-transmission.1376579/
  - https://www.bimmerfest.com/threads/code-sport-for-f20.1306289/
  - https://www.1erforum.de/threads/sport-plus-sport.128486/
- Servicemenü: https://www.bimmerfest.com/threads/entering-in-the-hidden-idrive-menu-settings.594175/
- M-Drive/M-Digitaltacho, FDS-Pop-up:
  - https://f87.bimmerpost.com/forums/showthread/1723947/enabling-m1-m2-buttons-on-og-m2
  - https://www.bimmerfest.com/threads/what-coding-brings-back-the-graphics-of-mode-selection.762239/
  - https://x3.xbimmers.com/forums/showthread.php?t=715297&page=36
  - https://www.2addicts.com/forums/showthread.php?t=997749&page=20
- ECO PRO/Verbrauchshistorie:
  - https://www.bimmerfest.com/forums/archive/index.php/t-642231.html
  - https://f30.bimmerpost.com/forums/showthread/1512884/add-nav-directions-to-instrument-cluster?p=29760649
- Ölstand: https://www.bimmerfest.com/threads/oil-level-check-vehicle-information-in-idrive.644882/
- Audio-Menüs:
  - https://f15.bimmerpost.com/forums/showthread.php?t=1033991&page=40
  - https://www.bimmerfest.com/threads/bang-olufsen-menu.645805/
- Colour-Switch: https://x3.xbimmers.com/forums/showthread.php?t=1718810
- DAB:
  - https://www.bimmerfest.com/threads/coding-dab-radio.749171/
  - https://www.1erforum.de/threads/dab-nachruestung.108629/
  - https://www.f10-forum.de/forum/thread/6268-dab-nachr%C3%BCsten/
  - https://www.motor-talk.de/forum/entry-hu-durch-eine-neue-gebrauchte-ersetzen-wie-programmieren-t7469542.html
- Display-Dimmung: https://g05.bimmerpost.com/beta/showthread?p=28546502
