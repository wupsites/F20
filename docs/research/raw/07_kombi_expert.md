# 07 – KOMBI im BimmerCode-Expertenmodus: Kandidatenparameter aus dem eigenen Backup

Fahrzeug: BMW 116i F20, Baujahr 01/2012, N13, Schaltgetriebe, Basis-Kombiinstrument „KOMBI", Radio Professional (HU_ENTRY, ohne Navigation), Markt Deutschland.
Grundlage: das vom Halter dekodierte KOMBI-Backup **CAFD_00000760_006_000_052**. Alle hier besprochenen Parameter **sind in diesem CAFD vorhanden**. Offen ist, was sie bewirken und ob das Basis-Kombi sie darstellt.
Werkzeug: BimmerCode inkl. Expertenmodus.
Recherchestand: 24.11.2026.

## Evidenz-Tags

| Tag | Bedeutung |
|---|---|
| **[DOK]** | In einer zitierten Quelle dokumentiert (oft für F30/F22/E6x, nicht für den F20). An diesem Auto **nicht** getestet. |
| **[WAHRSCHEINLICH]** | Aus dokumentierten Fakten für eng verwandte Fahrzeuge abgeleitet oder aus eindeutigen Parameternamen plus belegtem Funktionsprinzip. |
| **[EXPERIMENTELL]** | Nur Einzelberichte, nicht verifizierte Sammlungen oder reine Namensdeutung mit Teilbeleg. Ergebnis unsicher. |
| **[NICHT KOMPATIBEL]** | Laut Quelle für diese Hardware nicht möglich. |
| **[UNBEKANNT]** | Keine belastbare Quelle gefunden. Namensdeutungen sind ausdrücklich als Vermutung markiert. |

> **Methodik und Grenzen**
> - Die exakten Parameternamen (z. B. `CBS_STATUS_HU`, `KL_PREDRIVE_*`, `EDA_SYMBOL_*`, `GOODBYE_SCREEN`, `TNK_SCHWELLE_RESERVE`) liefern in der Websuche **keinen einzigen Treffer**. Die meisten Aussagen stützen sich deshalb auf BMW-Schulungsunterlagen zum **Funktionsprinzip** und auf BimmerCode-Optionen mit passendem Wertebereich.
> - bimmerpost, 2addicts, motor-talk und carwiki.de (HTTP 403) sowie manualmachine.com (403) waren nicht abrufbar. Aussagen von dort beruhen auf **Suchmaschinen-Snippets** und sind entsprechend markiert.
> - Die GitHub-API ist für diese Sitzung gesperrt. Aus `packetpilot/bmw-f` ließ sich per raw nur `cheats/jokinawa.xml` laden: Es beschreibt ein G-Serien-Kombi (DKOMBI4, Baureihe S18A) und ist hier nicht verwertbar. Ein Repository „OpenCAFDMap" wurde nicht gefunden.
> - Abgerufen und ausgewertet wurden: BMW ST1113 „F30 Displays, Indicators and Controls", BMW ST402 „E6x Driver Information Systems", BMW ST502 „E90 Driver Info Systems" (alle archive.org), BMW-TIS/SI-Seiten auf workshop-manuals.com, die BimmerCode-Liste F20, Dauxdu/bmw-coding (raw), zwei Community-Tabellen und ein i3-BimmerCode-Dokument (Google Docs), eine F22-Handbuchseite (manualslib) und Anhang I der RL 2014/45/EU.

---

## 1. Kurzfazit

**Lohnend und mit geringem Risiko:**
1. **HU-Termin („Fahrzeuguntersuchung") in der Serviceanzeige** – `CBS_STATUS_HU` sperre → anzeige. **[WAHRSCHEINLICH]** Das Kombi ist der CBS-Master; „gesetzliche Fahrzeuguntersuchung" und „Abgasuntersuchung" sind dokumentierte CBS-Umfänge, die länderspezifisch „codiert oder ausgeblendet" werden **[DOK E6x/E60]**. Einen F20-spezifischen Beleg für genau diesen Parameter gibt es nicht. Nach dem Umcodieren muss vermutlich noch ein Termin gesetzt werden (iDrive „Servicebedarf" oder ISTA „CBS-Korrektur"). `CBS_STATUS_AU` auf **sperre** lassen: In Deutschland ist die AU seit 2010 Teil der HU.
2. **Reichweitenwarnungen** – `CC_RW_WARNUNG` (50 km) und `CC_RW_WARNUNG_2` (90 km) entsprechen nach Wertebereich den BimmerCode-Standardoptionen „Low fuel warning 1/2" **[DOK BimmerCode, Zuordnung WAHRSCHEINLICH]**.
3. **BC-Autoreset** – `BC_AUTORESET_ZEIT` (04 = 4 h) → z. B. „Never" **[DOK BimmerCode]**.
4. **Digitaltacho** – `BC_DIGITAL_V` **[DOK]**. Der Halter hat ihn bereits getestet und zurückgesetzt. Eine weitere Digitalanzeige gibt es im Basis-Kombi nach Recherche nicht.
5. Bereits aktiv, keine Aktion nötig: Leerzeile (`BC_LEERZEILE`), Datum (`BC_DATUM`), ECO-PRO-Bonusreichweite digital (`ECO_RW_DIGITAL_ENABLE`).

**Experimentell, aber harmlos testbar:** ECO-PRO-Fahrtipps (`EDA_ENABLE` + `EDA_SYMBOL_*`) **[EXPERIMENTELL]**, Rückwärtsgang-Gong (`R_GANG_AKUSTIK_ENABLE`) **[EXPERIMENTELL]**, Begrüßungs-/Abschiedsbild (`WELCOME_SCREEN_DELAY`, `GOODBYE_SCREEN`) **[UNBEKANNT]**, `FDS_MENUE` **[UNBEKANNT]**.

**Funktioniert nicht:** Speed Limit Info (`SPEED_LIMIT`, `VZA_ENABLE`) – Kamera und Kombi „high" nötig **[NICHT KOMPATIBEL]**. GPS-Uhr (`GPS_UHR`) – ohne Navigation keine GPS-Quelle **[WAHRSCHEINLICH nicht kompatibel]**. Start-/M-Logo – laut BimmerCode nur KOMBI L7_BASIS/L7_MID; `BMW_LOGO` steht nicht in der Kandidatenliste **[DOK, für dieses Auto unwahrscheinlich]**. Needle Sweep – kein Parameter gefunden **[UNBEKANNT]**.

**Sicherheitsrelevant – nur dokumentieren, nicht ändern:** `KL_PREDRIVE_*`/`PREDRIVE_*` (Lampentest beim Start), `DTC_OFF_ENABLE`, `GURT_FOND_STATUS`, `SITZ_L_UEBERWACHUNG`, die Ausstattungsflags `DSC_MIT_RPA`, `LDM_VERBAUT`, `FDS_ENABLE`, die Tankkalibrierung (`TNK_VOLL_ANZEIGE`, `TNK_RW_VERBRAUCH`), `BC_V_KORREKTUR` (Tacho-Recht) und SPORT+ (DSC-Abstimmung).

---

## 2. Vorbemerkungen

- **„Parameter vorhanden" heißt nicht „Funktion vorhanden".** Ein Beispiel: `DIG_KVA_BEREICH` steht im CAFD, BimmerCode bietet die zugehörige Option aber nur für KOMBI **L7_MID** an **[DOK BimmerCode]**. Vermutlich teilen sich mehrere Kombi-Hardwarestände einen Parametersatz. **[UNBEKANNT]**, nicht belegt.
- **Welche Kombi-Variante hat das Auto?** BimmerCode unterscheidet L6 BO, L7_BASIS und L7_MID. `BC_DATUM = aktiv` passt zu „Date in board computer", das BimmerCode nur für L7_BASIS/L7_MID anbietet **[DOK]**. Zeigt das Auto das Datum im BC tatsächlich, spricht das für mindestens L7_BASIS. Den Variantennamen am besten direkt in BimmerCode ablesen.
- **Basis-Kombi laut BMW (F30, gleiche Familie) [DOK]:** TFT-Display 2,7" mit 320 × 120 Pixeln. Verbaut wird es nur **ohne** Professional-Navigation (609), Spurverlassenswarnung (5AD), HUD (610) und **Speed Limit Info (8TH)**. Der Momentanverbrauch erscheint unten im Drehzahlmesser. Das Kombi „high" (6WA, 5,7", 640 × 160) zeigt zusätzlich Energierückgewinnung, ECO-PRO-Fahrtipps und Verbrauchshistorie.
- **Regel für alle Tests:** vorher ein BimmerCode-Backup anlegen, Ladegerät anschließen, nur **einen** Parameter je Durchgang ändern und Ausgangswert und Ergebnis notieren. Eine VO-Codierung in der Werkstatt setzt Expertenänderungen zurück.

---

## 3. Übersicht nach Block

### 3000 Anzeige_Konfiguration

| Parameter | aktueller Wert | Funktion (Quelle) | Tag | Empfehlung |
|---|---|---|---|---|
| `BC_DIGITAL_V` | nicht_aktiv | Digitaltacho im BC; BimmerCode „Digital speed in board computer" | [DOK] | optional; Halter hat getestet |
| `BC_LEERZEILE` | aktiv | Leerer BC-Eintrag; BimmerCode „Empty menu item…" (Zuordnung über den Namen) | [DOK] | bereits aktiv |
| `BC_DATUM` | aktiv | Datum im BC; BimmerCode „Date in board computer" (L7_BASIS/L7_MID) | [DOK] | bereits aktiv |
| `BC_AUTORESET_ZEIT` | 04 (4 h) | Autoreset der Durchschnittswerte; BimmerCode 4 h/8 h/jede Fahrt/nie; laut GitHub FF = nie | [DOK] | nach Wunsch |
| `BC_V_KORREKTUR` | aktiv | laut GitHub-Sammlung nicht_aktiv = reale Geschwindigkeit | [EXPERIMENTELL] | **nicht ändern** (ECE R39) |
| `FDS_MENUE` | kein_menue | Namensdeutung: Fahrmodus-Menü im Kombi; Wirkung von menue_1/2 ohne Beleg | [UNBEKANNT] | Testergebnis menue_1 dokumentieren |
| `HINTERGRUNDBILD_ENABLE` | nicht_aktiv | Namensdeutung: Hintergrundbild. Die verwandte Hintergrundfarbe gilt laut Community-Tabelle nur für das Kombi „high" | [UNBEKANNT] | geringer Nutzen |
| `LISTEN_ANZEIGE`, `ENTERTAINMENT_DISP` | aktiv | Namensdeutung: Listen und Entertainment im Kombi | [UNBEKANNT] | bereits aktiv |
| `SPEED_LIMIT` | nicht_aktiv | Speed Limit Info im BC (F30-BC-Liste enthält „Speed limit information") | [NICHT KOMPATIBEL] | nicht codieren |
| `WARNUNG_GESCHW_LIMIT` | nicht_aktiv | unklar: SLI-Warnung oder Geschwindigkeitswarnung | [UNBEKANNT] | erst iDrive-Menü prüfen |
| `GPS_UHR` | nicht_aktiv | GPS-Uhrsynchronisation (BimmerCode i3: „GPS clock synchronization") | [DOK i3] / für HU_ENTRY [WAHRSCHEINLICH] wirkungslos | Test harmlos |
| `R_GANG_AKUSTIK_ENABLE` | nicht_aktiv | Gong beim Einlegen von R (GitHub; F30-Cheat-Sheet nur als Snippet) | [EXPERIMENTELL] | optional testen |
| `SITZ_L_UEBERWACHUNG` | (nicht übermittelt) | Namensdeutung: Sitz-/Gurtüberwachung links | [UNBEKANNT] | **nur dokumentieren** |
| `DIG_KVA_BEREICH` | 20_l/100km | Skalenende der Verbrauchsanzeige; BimmerCode 20/30 l/100 km, nur L7_MID | [DOK] | am Basis-Kombi vermutlich wirkungslos |
| `RW_GELB_ANZEIGE` | (nicht übermittelt) | Namensdeutung: Reichweite gelb | [UNBEKANNT] | – |
| `DTC_OFF_ENABLE` | aktiv | Namensdeutung: Anzeige des DTC-Modus (DSC) | [UNBEKANNT] | **nicht ändern** |
| `CC_OPTIMIERUNG_ENABLE`, `CC_15_EIN` | (nicht übermittelt) | Check-Control-Verhalten; Bedeutung offen | [UNBEKANNT] | nicht ändern |
| `GURT_FOND_STATUS` | 3_sitze | Namensdeutung: Gurtstatus für 3 Fondsitze | [UNBEKANNT] | **nur dokumentieren** |
| `BC_ANSCHLAG_REICHWEITE_KM` | 800_km | Namensdeutung: Obergrenze der Reichweitenanzeige | [UNBEKANNT] | – |
| `KL_PREDRIVE_*`, `PREDRIVE_START_MIT_OBD`, `PREDRIVE_ABB_MOT` | (je Leuchte) | Lampentest beim Start (Pre-Drive-Check), siehe 4.2 | Prinzip [DOK], Parameter [UNBEKANNT] | **nicht ändern** |
| `CC_TEMPERATURWARNUNG` | nicht_aktiv | unklar, ob Glättewarnung; siehe 4.6 | [UNBEKANNT] | erst Verhalten bei +3 °C beobachten |
| `CC_RW_WARNUNG` / `CC_RW_WARNUNG_2` | 50_km / 90_km | Reichweitenwarnung 1/2; BimmerCode „Low fuel warning 1" (10–50 km), „… 2" (50–90 km) | [WAHRSCHEINLICH] | nach Wunsch, nicht zu knapp |

### 3003 FZG_Ausstattung

| Parameter | aktueller Wert | Funktion | Tag | Empfehlung |
|---|---|---|---|---|
| `FDS_ENABLE` | – | Ausstattungsflag Fahrerlebnisschalter (Namensdeutung) | [UNBEKANNT] | nicht ändern |
| `REKU_ENABLE` | keine_anz | Anzeige der Energierückgewinnung; laut F30 nur im Kombi „high" | [WAHRSCHEINLICH] unwahrscheinlich | Test harmlos, Nutzen gering |
| `LDM_VERBAUT` | – | Namensdeutung: Längsdynamikmanagement (Tempomat mit Bremsfunktion) verbaut | [UNBEKANNT] | **nicht ändern** |
| `DSC_MIT_RPA` | – | Namensdeutung: DSC mit Reifenpannenanzeige | [UNBEKANNT] | **nicht ändern** |
| `VZA_ENABLE` | – | Speed Limit Info (Kamera) | [NICHT KOMPATIBEL] | nicht codieren |

### 3005 Tank

| Parameter | aktueller Wert | Funktion | Tag | Empfehlung |
|---|---|---|---|---|
| `TNK_SCHWELLE_RESERVE` | 9_liter (7/8/9/12) | Namensdeutung: Reserveschwelle in Litern | [UNBEKANNT] | nicht senken |
| `TNK_RESERVE_WARNUNG_ENABLE` | nicht_aktiv | Namensdeutung: volumenbasierte Reservewarnung | [UNBEKANNT] | ggf. Test (nur aktivieren, nicht senken) |
| `TNK_RW_VERBRAUCH` | 6l/100km | Namensdeutung: Verbrauchsannahme für die Reichweitenberechnung | [UNBEKANNT] | **nicht ändern** |
| `TNK_VOLL_ANZEIGE` | – | Kalibrierparameter der Tankanzeige (i3 REx: zusammen mit TNK_LITER/OHM geändert) | [DOK i3] | **nicht ändern** |

### 3008 PIA_Einheiten

| Parameter | aktueller Wert | Funktion | Tag |
|---|---|---|---|
| `KI_PIA_SPEED_LIMIT`, `KI_PIA_ANKUNFT`, `KI_PIA_DISTANZ`, `KI_PIA_MEMO` (nicht_aktiv), `KI_PIA_SPA` (aktiv), `KI_PIA_ANALOG_RW_KVA`, `KI_LETZTE_BC` | s. links | Vermutung: welche Kombi-Einstellungen pro Schlüssel/Profil gespeichert werden. SPA = Schaltpunktanzeige (Namensdeutung). Ankunft und Distanz brauchen Navigation. | [UNBEKANNT] |

### 3009 CBS_Konfiguration → Abschnitt 4.1

### 300B KI_Parameter

| Parameter | aktueller Wert | Funktion | Tag |
|---|---|---|---|
| `GOODBYE_SCREEN` | 0E (hex = 14) | Namensdeutung: Abschiedsanzeige (Dauer?) | [UNBEKANNT] |
| `WELCOME_SCREEN_DELAY` | 04 | Namensdeutung: Verzögerung der Begrüßungsanzeige | [UNBEKANNT] |
| `WARNING_INDICATION_TIMEOUT_ENABLE` | – | Namensdeutung: automatisches Ausblenden von Warnhinweisen | [UNBEKANNT] – nicht ändern |

### 300C ECO_FDS → Abschnitte 4.3 und 4.4

### 3007 KI_Dimmung
Die Parameterliste des Blocks wurde nicht übermittelt. Laut Community-Tabelle macht `DIM_NACHT_EIN` (32 → FF) die Kombi-Anzeige nachts weiß statt orange und schaltet zugleich die Navi-Nachtumschaltung ab **[EXPERIMENTELL]**. Ob der Parameter im eigenen CAFD steht, ist offen. Dimmwerte nur maßvoll ändern, weil eine zu helle Anzeige nachts blendet.

---

## 4. Details

### 4.1 CBS: HU- und AU-Termin in der Serviceanzeige (`CBS_STATUS_*`, Block 3009)

**Belegt (andere Baureihen):**
- Das Kombi ist der **CBS-Master** und zeigt die CBS-Umfänge im Display. Die zehn Typen umfassen u. a. „Vehicle Check" (Fahrzeug-Check), „**Statutory vehicle inspection**" (HU) und „**Emissions test**" (AU). **[DOK, BMW ST402 E6x]**
- BMW-TIS (E60, CBS-Diagnose): „Legally prescribed vehicle inspection (country-specific): Coding or blanking out – Interval for calculating the target date"; dasselbe gilt für die AU. „The target date is calculated on the basis of the date of first registration." Die Standarddaten werden bei der ersten Auslieferungsinspektion (Pre-Delivery-Check) gesetzt. **[DOK]**
- BMW-SI 00 04 06 (E82, 06/2006): Die AU-Anzeige im CBS „can be activated and deactivated". Der Standard „depends on the market". Der Weg führt über das Diagnosesystem: Servicefunktionen → Wartung → CBS-Fahrzeugdaten-Korrektur (SCBS_6004) → Hauptuntersuchung bzw. Abgasuntersuchung → aktivieren/deaktivieren und neues Datum eingeben. **[DOK, E-Serie]**
- F-/G-Serie in Deutschland: Laut CarWiki (nur Snippet, Seite gesperrt) ist „Fahrzeuguntersuchung" unter „Fahrzeugstatus → Servicebedarf" der HU-Termin, den man selbst einträgt. Die Erinnerung verschwindet erst, wenn man ein neues Datum setzt. Datum und Uhrzeit im Auto müssen stimmen. **[EXPERIMENTELL, Snippet]**

**Ableitung für dieses Auto:** `CBS_STATUS_HU = sperre` entspricht sehr wahrscheinlich dem „blanking out" der HU. Mit **anzeige** wird der HU-Umfang vermutlich wieder eingeblendet. **[WAHRSCHEINLICH]** Für den F20 ist das nicht direkt belegt.
- `erprobung` heißt wörtlich „Erprobung"; vermutlich ein BMW-interner Testzustand. **Nicht verwenden.** [UNBEKANNT]
- Nach dem Umcodieren fehlt eventuell noch ein gültiger Termin. Ob das Radio Professional (HU_ENTRY) im Menü „Servicebedarf" eine Datumseingabe anbietet, ist **[UNBEKANNT]**. Sonst bleibt die ISTA-Funktion „CBS-Korrektur".
- `CBS_STATUS_AU`: auf **sperre** lassen. In Deutschland ist die AU seit 2010 Bestandteil der HU (allgemein bekannt, hier nicht gesondert belegt). Ein zweiter Termin würde nur doppelt erinnern.
- `CBS_STATUS_FZGCHK_INTERN` (Fahrzeug-Check, [DOK] als CBS-Typ), `CBS_STATUS_UEBERGABE` (vermutlich Übergabedurchsicht) und `CBS_STATUS_EINF_KONTR` (vermutlich Einfahrkontrolle) sind [UNBEKANNT]. **Nicht ändern**, weil ausgeblendete Wartungsumfänge fällige Arbeiten verschleiern.
- **Rechtlich:** Die Anzeige ist nur eine Erinnerung. Maßgeblich bleibt die HU-Frist nach § 29 StVZO (Prüfplakette).

### 4.2 Pre-Drive-Check (`KL_PREDRIVE_*`, `PREDRIVE_START_MIT_OBD`, `PREDRIVE_ABB_MOT`) – sicherheitskritisch

**Was „Predrive" ist [DOK, BMW ST402 E6x; ST502 E90]:**
- Der Pre-Drive-Check dient „as a check of internal functions in the instrument cluster" und der „monitoring of the live signals from all control units that may emit Check-Control messages".
- „The most important indicator and warning lights are activated for 4 seconds when terminal 15 is switched ON. Exception: … airbags actuated when terminal R is switched ON."
- Liste beim E6x: Gurtwarnung, Airbag, ABS, allgemeine Bremswarnung, Abgas-Warnleuchte, DSC, Aktivlenkung, ACC.
- „If a fault occurs during the pre-drive check, the check is interrupted for the system in question. The indicator and warning lights for this system remain on. The Check-Control system issues the appropriate message."

**Deutung der F20-Parameter:** `KL_PREDRIVE_F1_AIRBAG`, `…F2_GURT`, `…F13_ABS`, `…F52_DSC` usw. legen vermutlich fest, welche Leuchte am Lampentest teilnimmt. Die Nummern sehen nach Leuchten-IDs aus. `PREDRIVE_START_MIT_OBD` (Start mit OBD-Bezug, etwa der Abgas-Warnleuchte?) und `PREDRIVE_ABB_MOT` (Abbruch bei Motorstart?) sind reine Namensdeutungen. **[UNBEKANNT]**

**Kann man den Lampentest ändern?** Technisch wohl ja, denn die Parameter sind vorhanden. **Empfehlung: nicht ändern.**
- Der Lampentest ist die einzige Möglichkeit für den Fahrer zu sehen, dass eine Warnleuchte funktioniert. Ob eine abgewählte Leuchte bei einem echten Fehler weiter aufleuchtet, ist **[UNBEKANNT]**.
- Die HU bewertet laut RL 2014/45/EU Anhang I u. a.: 4.9.1 „Kontrollleuchten funktionieren nicht", 1.6 ABS „Warnvorrichtung schadhaft", 7.1.6 „SRS-Störungsanzeige (MIL) weist auf Fehler im System hin", 7.12 ESP-Störungsanzeige sowie 8.2.1.2 OBD. **[DOK]** Ein unterdrückter Lampentest kann also bei der HU auffallen.

### 4.3 ECO-PRO-Fahrtipps (`EDA_ENABLE`, `EDA_SYMBOL_*`, Block 300C)

- **[DOK, BMW 2er F22, Handbuch II/15]:** Im Kombi gibt es Effizienzanzeige und ECO-PRO-Tipps, wenn die ECO-PRO-Anzeige aktiviert ist (Einstellungen → Kombiinstrument → „ECO PRO Info"). Die Tipps lauten: Gas wegnehmen oder später beschleunigen; auf die gewählte ECO-PRO-Geschwindigkeit verzögern; Steptronic von M/S nach D; „follow shifting instructions" (Steptronic/Schaltgetriebe); „Manual transmission: engage neutral for engine stop".
- **[DOK, F30]:** ECO-PRO-Fahrtipps werden für das Kombi mit erweitertem Umfang (6WA) gezeigt.
- **Zuordnung [WAHRSCHEINLICH, Namensdeutung]:** `EDA_SYMBOL_LAST` = Gas wegnehmen, `…GESCHW` = Geschwindigkeit, `…G_PROG` = Getriebeprogramm (nur Steptronic, für dieses Auto irrelevant), `…GANG` = Schaltempfehlung, `…KUPPLUNG` = Leerlauf/Kupplung für den Motorstopp.
- **Für dieses Auto [EXPERIMENTELL]:** Unklar ist, ob das 2012er Basis-Kombi die Symbole darstellt und ob HU_ENTRY die Einstellung „ECO PRO Info" anbietet. Ein Test ist risikoarm: `EDA_ENABLE` aktiv, dann `EDA_SYMBOL_GANG`, `…KUPPLUNG`, `…LAST`, `…GESCHW` aktiv, und anschließend im ECO-PRO-Modus fahren.
- `ECO_RW_DIGITAL_ENABLE` = aktiv: Die Bonusreichweite ist laut F30 ein BC-Eintrag **[DOK]**. `ECO_RW_ANALOG_ENABLE` (nicht_aktiv) ist **[UNBEKANNT]**.

### 4.4 Fahrerlebnisschalter / SPORT+ (`FDS_MENUE`, `FDS_MENUE_SIGNAL_x`, `FDS_MENUE_TEXT_x`, `FDS_GELB`, `FDS_SIGNAL_VARIANTE`)

- BimmerCode „SPORT+ driving mode (2 of 2)" liegt im KOMBI, Teil 1 im ICMQL. **[DOK]** Laut GitHub-Sammlung werden dafür `FDS_MENUE_TEXT_1…4`/`FDS_MENUE_SIGNAL_1…4` von menue_4 auf menue_3 gesetzt (dort Block 3000, im eigenen CAFD Block 300C). **[EXPERIMENTELL]**
- SPORT+ ändert die DSC-Abstimmung, ist also fahrdynamisch relevant. Ob der ICMQL des 116i SPORT+ hergibt, ist ungeprüft.
- `FDS_MENUE` (kein_menue/menue_1/menue_2), `FDS_GELB` und `FDS_SIGNAL_VARIANTE`: **[UNBEKANNT]**. Bitte das Ergebnis des menue_1-Tests des Halters nachtragen.

### 4.5 Tank und Reichweitenwarnungen

- **Reichweitenwarnungen:** BimmerCode bietet für den F20 „Low fuel warning 1" (10–50 km oder nicht aktiv) und „Low fuel warning 2" (50–90 km oder nicht aktiv). **[DOK]** Die aktuellen Werte `CC_RW_WARNUNG = 50_km` und `CC_RW_WARNUNG_2 = 90_km` liegen genau an den Bereichsgrenzen. Die Zuordnung ist daher **[WAHRSCHEINLICH]**. Ein F22-Nutzer beschreibt das zweistufige, reichweitenbasierte Prinzip (Snippet, 2addicts). Spätere Warnungen erhöhen das Risiko, liegen zu bleiben.
- `TNK_SCHWELLE_RESERVE` / `TNK_RESERVE_WARNUNG_ENABLE`: Namensdeutung als volumenbasierte Reservewarnung in Litern. **[UNBEKANNT]** Höchstens aktivieren, die Schwelle nicht senken.
- `TNK_VOLL_ANZEIGE`: Beim i3 REx wird der Parameter zusammen mit `TNK_LITER_RECHTS`/`TNK_OHM_RECHTS` geändert, um die Tankanzeige an einen anderen Tank anzupassen. Er ist also Teil der Tankkalibrierung. **[DOK i3]** `TNK_RW_VERBRAUCH` (6 l/100 km) ist dem Namen nach eine Verbrauchsannahme für die Reichweite. **Beide nicht ändern.**

### 4.6 Temperaturwarnung (`CC_TEMPERATURWARNUNG`)

Ein F10-Handbuch (535i, Snippet) beschreibt eine Außentemperaturwarnung bei **+3 °C** mit Signal und Kombi-Meldung („Ice warning, refer to External temperature warning"). **[DOK, anderes Modell]** Ob `CC_TEMPERATURWARNUNG` diese Warnung ist, ist **[UNBEKANNT]**. Zuerst beobachten: Warnt das Auto bei +3 °C bereits, steuert der Parameter etwas anderes. Ein Test ist risikoarm.

### 4.7 Speed Limit Info, GPS-Uhr, Navigationsbezüge

- Speed Limit Info (8TH) gehört laut BMW F30 zu den Ausstattungen, die das Kombi „high" erfordern. Das Basis-Kombi wird nur ohne 8TH verbaut. **[DOK]** Ohne Frontkamera und Navigation fehlt die Datenquelle. **[NICHT KOMPATIBEL]** Das gilt für `SPEED_LIMIT`, `VZA_ENABLE` und vermutlich `KI_PIA_SPEED_LIMIT`.
- `GPS_UHR`: Für den i3 dokumentiert BimmerCode im Kombi „GPS clock synchronization" **[DOK i3]**. Ohne Navigation kommt keine GPS-Zeit **[WAHRSCHEINLICH]**. Ein Test ist harmlos.
- `KI_PIA_ANKUNFT`/`KI_PIA_DISTANZ` beziehen sich auf Navigationswerte und sind ohne Navi wirkungslos. **[WAHRSCHEINLICH]**

### 4.8 Schaltpunktanzeige (SPA) und PIA

- BMW beschreibt für Schaltgetriebe eine Schaltpunktanzeige mit Gangempfehlung. Bei einem F11 von 2012 ließ sie sich im iDrive abschalten, beim F10 fand der Nutzer die Option nicht (bmw-syndikat, Snippet). **[EXPERIMENTELL]** `KI_PIA_SPA = aktiv` deutet darauf hin, dass die SPA-Einstellung pro Profil gespeichert wird. Die Deutung von „PIA" als Personalisierung ist **[UNBEKANNT]**.
- Empfehlung: zuerst im iDrive nach einer SPA-Option suchen. Dafür ist keine Codierung nötig.

### 4.9 Needle Sweep, Start-/M-Logo, Digitaltacho

- **Needle Sweep/Zeigertest:** Weder in der Kandidatenliste noch in F-Serien-Quellen gibt es einen Parameter. BimmerCode listet für den F20 keinen Needle Sweep. **[UNBEKANNT]** Das Kombi-Testmenü (Reset-Taste 10 s, F30-Doku: 02 Systemtest, 10 Tacho/Drehzahlmesser) ist kein Start-Sweep. Ob die Zeiger dabei ausschlagen, ist nicht beschrieben.
- **Start-Logo/M-Performance-Logo:** „Start logo" verlangt laut BimmerCode KOMBI L7_BASIS oder L7_MID, „M Performance logo" nur L7_MID. **[DOK]** `BMW_LOGO` steht nicht in der Kandidatenliste. Wenn der Parameter im Backup fehlt, ist das Logo am vorhandenen Kombi **nicht codierbar** **[WAHRSCHEINLICH]**. Das deckt sich mit der früheren Recherche (andere Kombi-Hardware nötig).
- **Digitaltacho:** Nur `BC_DIGITAL_V`. **[DOK]** Ohne HUD gibt es keine weitere Digitalanzeige.

---

## 5. Sicherheitsrelevante Parameter (nur dokumentieren)

| Parameter | Grund |
|---|---|
| `KL_PREDRIVE_*`, `PREDRIVE_START_MIT_OBD`, `PREDRIVE_ABB_MOT` | Lampentest von Airbag, Gurt, ABS, DSC usw.; HU-relevant (RL 2014/45/EU Anhang I) |
| `DTC_OFF_ENABLE` | Anzeige des DSC/DTC-Modus |
| `GURT_FOND_STATUS`, `SITZ_L_UEBERWACHUNG` | Gurt-/Sitzüberwachung |
| `DSC_MIT_RPA`, `LDM_VERBAUT`, `FDS_ENABLE` | Ausstattungsflags; falsche Werte können Warnungen (Reifenpanne) unterdrücken |
| `WARNING_INDICATION_TIMEOUT_ENABLE`, `CC_OPTIMIERUNG_ENABLE`, `CC_15_EIN` | Check-Control-Verhalten, Bedeutung offen |
| `TNK_VOLL_ANZEIGE`, `TNK_RW_VERBRAUCH`, `TNK_SCHWELLE_RESERVE` (senken) | falsche Tank-/Reichweitenanzeige, Liegenbleiben |
| `BC_V_KORREKTUR` | Tacho darf nie zu wenig anzeigen (UN-ECE R39) |
| `FDS_MENUE_SIGNAL_x`/`FDS_MENUE_TEXT_x` (SPORT+) | geänderte DSC-Abstimmung |
| `CBS_STATUS_FZGCHK_INTERN`, `…UEBERGABE`, `…EINF_KONTR` | ausgeblendete Wartungsumfänge |

---

## 6. Vorschlag für die Testreihenfolge (je ein Parameter, mit Backup)

1. `CBS_STATUS_HU` → anzeige. Danach im iDrive „Servicebedarf" prüfen, ob „Fahrzeuguntersuchung" erscheint und ein Datum eingegeben werden kann. Falls nicht: zurück auf sperre.
2. `BC_AUTORESET_ZEIT` nach Wunsch (BimmerCode-Standardoption).
3. `CC_RW_WARNUNG`/`_2` nur nach Wunsch und nicht unter etwa 50/90 km.
4. ECO-PRO-Tipps: `EDA_ENABLE` → aktiv, dann die Symbole für Schaltgetriebe.
5. Optional: `R_GANG_AKUSTIK_ENABLE`, `CC_TEMPERATURWARNUNG` (nach Beobachtung), `WELCOME_SCREEN_DELAY`/`GOODBYE_SCREEN`.

---

## 7. Offene Fragen

1. Welchen KOMBI-Variantennamen zeigt BimmerCode für CAFD_00000760 (L6 BO, L7_BASIS, L7_MID)? Wird das Datum im BC tatsächlich angezeigt?
2. Erscheint nach `CBS_STATUS_HU = anzeige` der HU-Eintrag? Bietet HU_ENTRY eine Datumseingabe, oder ist ISTA „CBS-Korrektur" nötig? Was bedeutet `erprobung` genau?
3. Was hat der Test mit `FDS_MENUE = menue_1` gezeigt? Was mit `BC_DIGITAL_V = aktiv`?
4. Warnt das Auto bei +3 °C schon heute (Deutung von `CC_TEMPERATURWARNUNG`)?
5. Stellt das Basis-Kombi ECO-PRO-Tipps (`EDA_*`) dar, und bietet HU_ENTRY „ECO PRO Info" an?
6. Welche Werte und Optionen haben `RW_GELB_ANZEIGE`, `CC_15_EIN`, `CC_OPTIMIERUNG_ENABLE`, `SITZ_L_UEBERWACHUNG`, `WARNING_INDICATION_TIMEOUT_ENABLE`, `FDS_GELB`, `FDS_SIGNAL_VARIANTE`, `TNK_VOLL_ANZEIGE` und die `KL_PREDRIVE_*`-Liste?
7. Enthält das Backup `BMW_LOGO`/`MPM_*` oder `DIM_NACHT_EIN` (Block 3007)?
8. Welche Einheit haben `GOODBYE_SCREEN` (0E) und `WELCOME_SCREEN_DELAY` (04)?

---

## 8. Quellen

**Primär (BMW):**
- BMW ST1113 „F30 Displays, Indicators and Controls" (Basis- und High-Kombi, BC-Liste, ECO PRO, Service- und Testfunktionen): https://archive.org/download/BMWTechnicalTrainingDocuments/ST1113%20F30%20Complete%20Vehicle/06_F30%20Displays%2C%20Indicators%20and%20Controls.pdf
- BMW ST402 „E6x Driver Information Systems" (Pre-Drive-Check, CBS-Typen inkl. HU/AU, Kombi als CBS-Master): https://ia801005.us.archive.org/11/items/BMWTechnicalTrainingDocuments/ST402%20Body%20Electronics%20III/09%20E6x%20Driver%20Information.pdf
- BMW ST502 „E90 Driver Info Systems" (Pre-Drive-Check bei Klemme 15): https://ia801005.us.archive.org/11/items/BMWTechnicalTrainingDocuments/ST502%20E90%20Complete%20Vehicle/07_E90%20Driver%20Info%20Systems.pdf
- BMW-TIS E60 „Diagnosis for Condition Based Service" (HU/AU „coding or blanking out"): https://workshop-manuals.com/bmw/5_series_e60/m5_s85_sal/2_repair_instructions/61__general_electrical_system/0__troubleshooting/4_ra__diagnosis_for_condition_based_service/page_2139/
- BMW-SI 00 04 06 „Changed Emissions Test Indicator BMW Condition Based Service" (E82): https://workshop-manuals.com/bmw/1_series_e82/123d_n47s_coupe/1_service_information/00__maintenance_and_general_data/11_si__changed_emissions_test_indicator_bmw_condition_based_service/
- BMW-Handbuch 2er (F22, II/15), ECO-PRO-Tipps: https://www.manualslib.com/manual/979414/Bmw-2-Series.html?page=168
- BMW-Handbuch 535i (F10), Außentemperaturwarnung (nur Snippet): https://www.manualslib.com/manual/889993/Bmw-535i.html?page=75

**Hersteller-Tool und Sammlungen (abgerufen):**
- BimmerCode F20/F21: https://bimmercode.app/cars/f20
- BimmerCode-Optionen i3 (GPS-Uhr, TNK_VOLL_ANZEIGE): https://docs.google.com/document/d/1WCF3FbD3U6G_0k4f107EkoiVbEX0SPbbmvcelDQSSGk/export?format=pdf
- Dauxdu/bmw-coding (nicht verifiziert): https://raw.githubusercontent.com/Dauxdu/bmw-coding/HEAD/e-sys/02-Codings/Instrument-Cluster.md
- Community-Tabelle F-Serie (BC_Digital_V, DIM_NACHT_EIN, HINTERGRUND_FARBE, BMW_LOGO): https://docs.google.com/spreadsheets/d/16O4RKIMekWFCs5jPW3T_7li0yIEvgZfFI0u3l0RmSwU/pubhtml
- packetpilot/bmw-f, `cheats/jokinawa.xml` (G-Serie, nicht verwertbar): https://raw.githubusercontent.com/packetpilot/bmw-f/master/cheats/jokinawa.xml

**Recht:**
- RL 2014/45/EU, Anhang I (Mängel bei Warnleuchten/MIL): https://gesetze.legal/eu/rl_2014_45_eu/anhang_i

**Nur Suchmaschinen-Snippets (Seiten gesperrt):**
- CarWiki „Fahrzeuguntersuchung im Servicebedarf": https://carwiki.de/bmw-fahrzeuguntersuchung-servicebedarf/
- 2addicts (F22, zweistufige Reichweitenwarnung): https://www.2addicts.com/forums/showthread.php?p=18847146
- bimmerpost F30-Cheat-Sheet (Rückwärtsgang-Gong): https://f30.bimmerpost.com/forums/showthread.php?p=16525413
- bmw-syndikat „Schaltpunktanzeige deaktivieren" (F10/F11): https://www.bmw-syndikat.de/bmwsyndikatforum/topic_p357635_Schaltpunktanzeige_deaktivieren_5er_BMW_-_F10___F11___F07_GT.html
