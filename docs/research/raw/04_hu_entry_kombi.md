# 04 – HU_ENTRY (Radio Professional / iDrive) und KOMBI (F20, 2012): Codier- und Technikrecherche

Fahrzeug: BMW 116i F20, Produktion 24.01.2012, N13 (136 PS), Schaltgetriebe, Radio Professional mit iDrive-Controller und 6,5"-Display (Steuergerät **HU_ENTRY**, ohne Navigation; CAFD laut Halter `CAFD_000000F9`, Version 007.007.001 – **hier nicht verifiziert**), Multifunktionslenkrad, Kombiinstrument „KOMBI" der ersten F20-Generation.
Werkzeug des Halters: BimmerCode (Vollversion inkl. Expertenmodus).
Recherchestand: 24.11.2026.

## Evidenz-Tags

| Tag | Bedeutung |
|---|---|
| **[DOK]** | In einer zitierten Quelle dokumentiert. An diesem Auto **nicht** getestet. |
| **[WAHRSCHEINLICH]** | Aus dokumentierten Fakten für eng verwandte Fahrzeuge/Geräte abgeleitet. Nicht direkt für F20/HU_ENTRY belegt. |
| **[EXPERIMENTELL]** | Nur Einzel- bzw. widersprüchliche Forenberichte oder nicht verifizierte Sammlungen. Ergebnis unsicher. |
| **[NICHT KOMPATIBEL]** | Laut Quelle für diese Hardware nicht möglich (fehlende Hardware oder anderes Steuergerät). |
| **[UNBEKANNT]** | Keine belastbare Quelle gefunden. |

> **Wichtig zur Methodik:** bimmerpost/2addicts/1addicts (Zugangsprüfung), bimmerfest (Bezahl-Bot-Sperre), motor-talk und obdeleven (HTTP 403) sowie scribd/slideshare (Inhalt lädt nicht) waren **nicht abrufbar**. Was aus diesen Foren stammt, beruht auf Suchmaschinen-Snippets und ist jeweils so gekennzeichnet. Diese Aussagen sind schwächer belegt als die BMW-Dokumente.
> Archivkopien gesperrter Threads habe ich bewusst nicht abgerufen.

---

## 1. Kurzfazit

1. **BimmerCode bietet laut offizieller F20-Liste keine einzige Headunit-Option für HU_ENTRY an.** Jede iDrive-Option (Startanimation, Sportanzeigen, Warnhinweis beim Start, Lautstärke-Popup, Servicehistorie, Reifendruckanzeige, Volltext-SMS, Max.-Lautstärke beim Start, Warngong, Klingelton, BT-Audio, Video) verlangt **HU_NBT oder HU_NBT_EVO**, teils zusätzlich eine Combox. [DOK] Für HU_ENTRY bleibt höchstens der Expertenmodus. Ob BimmerCode HU_ENTRY dort überhaupt anbietet, ist **[UNBEKANNT]** und muss in der App geprüft werden.
2. **Sportanzeigen auf HU_ENTRY (ohne Navi):** Laut Forum (nur Snippet) erzeugt `EFF_DYN_SPORT_CID = aktiv` im Block 3000 das Menü „Sportanzeigen". Ein Nutzer mit HU_ENTRY ohne Navi meldet jedoch, dass die Leistungs- und Drehmomentanzeige auf 0 bleibt. Andere melden Erfolg (X3 ohne Navi, HU_ENTRYNAV). Die Datenlieferung hängt vom Motor ab. Für den N13 gibt es keinen Beleg. → **[EXPERIMENTELL]**
3. **Startanimation/Boot-Logo der Headunit:** `STARTUP_EMBLEM` ist nur für HU_NBT (Block 3001, variant_00–09) dokumentiert, mit einem Hinweis auf „Headunit Entrynav" (die spätere ENTRY-Navigation ab 2014). Für die 2012er HU_ENTRY ohne Navi gibt es keinen Beleg. → **[UNBEKANNT]**, eher unwahrscheinlich.
4. **KOMBI:** Digitaltacho im Bordcomputer (`BC_DIGITAL_V`, Block 3000) ist mehrfach dokumentiert und in BimmerCode als Standardoption gelistet. Dazu kommen BimmerCode-Optionen wie leerer BC-Menüpunkt, Auto-Reset der Durchschnittswerte, Reservewarnungen 1/2 und SPORT+ (2 von 2). Start-Logo, Datum im BC und M-Performance-Logo verlangen laut BimmerCode KOMBI-Varianten **L7_BASIS/L7_MID**. Ob der 2012er KOMBI dazu gehört, ist **[UNBEKANNT]**.
5. **KOMBI-Testmenü („Geheimmenü") ist offiziell von BMW dokumentiert** (F30-Schulungsunterlage ST1113): Reset-Taste im Kombi 10 s halten (Klemme 15 an). Die Testfunktionen ab Nr. 5 werden über Testfunktion 04 mit der **Quersumme der letzten fünf Stellen der Fahrgestellnummer** entsperrt. Es gibt 19 Testfunktionen, darunter Nr. 08 „Kühlmittel-, Außen-, **Motoröltemperatur**". [DOK] für F30, für F20 [WAHRSCHEINLICH].
6. **Eigene Software/Apps auf HU_ENTRY:** Es gibt keinen öffentlichen Nachweis für eine Methode. Ein NBT-EVO-Toolkit nennt HU_ENTRY ausdrücklich als „anderes SoC", auf das seine Methoden nicht passen. → **[UNBEKANNT] / keine gezeigte Methode**

---

## 2. Abgrenzung der Headunits (wichtig – nicht verwechseln)

Quelle, wo nicht anders angegeben: BMW SI B65 09 16 „Radio/Navigation/Head Unit Identification" (Feb. 2019, US-Ausgabe; NHTSA-Kopie).

| Bezeichnung | Hersteller laut BMW | SA | Fahrzeuge/Zeitraum (laut SI, US-Markt) | Relevanz für diesen F20 |
|---|---|---|---|---|
| CHAMP2 (CIC Basic 2) | Alpine | 663 Radio Professional | E70/E71, F10/F25 bis 7/2013 | **Nicht** dieses Auto (E-Serie/F10/F25) |
| RAD2 / RAD2+ | Alpine / Continental | 663 | E90/E8x usw. | Nicht dieses Auto |
| **ENTRY CONTI – „Entry Media by Continental"** | **Continental** | **663 Radio Professional CD** | „F30 from SOP to 7/2013" | **[WAHRSCHEINLICH] die Hardware dieses F20** (gleiche Plattform, Bauzeit 01/2012). Für F20 nicht explizit gelistet, weil der F20 in den USA nicht verkauft wurde. |
| ENTRY – „Head Unit Basic HU-B1, Entry Media or Entry Navigation by Magneti Marelli" | Magneti Marelli | 645/650/663, 606 Navigation Business, 6UP | F22/F30/F32 usw. ab 7/2014, F25 ab 8/2013 | Spätere Generation, inkl. **ENTRYNAV** – nicht dieses Auto |
| ENTRY EVO – Head Unit Basic 2 (HU-B2) | Alpine | 645 Radio Professional | später (EVO-Generation) | Nicht dieses Auto |
| CIC / NBT / NBT EVO | – | 609 Navigation Professional | – | Nicht dieses Auto. Die meisten Cheat-Sheet-Einträge gelten für **diese** Geräte. |

BMW SI B65 10 12 (Jan. 2013) bestätigt die Namensgleichheit: „Headunit-Basic (HU-B), also called Radio Professional or ENTRY head unit". [DOK]

> Die Steuergerätebezeichnung in E-Sys/BimmerCode für dieses Auto ist laut Halter `HU_ENTRY`. Die spätere Marelli-Navi-Variante erscheint in Foren als `HU_ENTRYNAV`. Erfolgsberichte von ENTRYNAV gelten **nicht** automatisch für die 2012er HU_ENTRY.

---

## 3. HU_ENTRY: Hardware und Plattform

Quelle: BMW-Schulungsunterlage ST1113 „F30 Entertainment and Communication" (archive.org, Text „via BIMMERPOST") sowie SI B65 09 16. Die Unterlage beschreibt die US-F30-Ausstattung. Für den europäischen F20 gilt sie **[WAHRSCHEINLICH]** analog.

- **Gerät:** „Basic headunit (HU-B)", Einstiegsradio ohne Navigation. [DOK]
- **Display:** zentrales Informationsdisplay (CID) mit **6,5"**. Es hängt nicht am Bus, sondern über **APIX** (Automotive Pixel Link, 1 Gbit/s) direkt an der Headunit und wird auch von ihr mit Strom versorgt. [DOK]
- **Controller:** „The controller of the Basic headunit has only five function buttons and can only be toggled to the left and right." [DOK]
- **Radio:** AM/FM-Doppeltuner mit Phasen-Diversity. DAB ist **nicht** erwähnt; es wäre eine separate Option. [DOK]/[UNBEKANNT]
- **Telefon:** Bei der Standard-Freisprecheinrichtung **6NH** („Hands-free Bluetooth system with USB interface") ist die Telefonfunktion **in der Headunit realisiert**. Kontakte liegen im internen Speicher, es gibt keine SD-Karte. Eine **Combox** kommt nur mit Option **6NL** (BMW Assist mit erweitertem Bluetooth/USB) bzw. mit Navigation 609. [DOK] (US-F30). Zu den europäischen Codes 6NS/6NK wurden keine Primärquellen gefunden. → [UNBEKANNT], FA (Fahrzeugauftrag) auslesen.
- **Combox-Funktionen (nur mit Combox):** Bluetooth-Audio-Streaming, mehrere gekoppelte Geräte, Kontakte mit Bildern, Albumcover, Office (E-Mail, Kalender, Notizen), vom Kunden selbst durchführbare Software-Updates. [DOK]
- **AUX/USB:** AUX-In vorhanden. USB-Audio-Schnittstelle in der Mittelkonsole, ohne Combox an die Headunit angeschlossen, mit Combox an die Combox. [DOK]
- **Service:** „The Basic headunit does not contain any components that are replaceable by a BMW Service agent". Die Ethernet-Verbindung FEM→Headunit dient „solely to update the headunit's software". [DOK]
- **Freischaltungen:** Laut SI B65 09 16 „REQUIRES ENABLE CODES FSC/SWT". Relevant bei Tausch oder Nachrüstung. [DOK]
- **Betriebssystem/SoC:** **[UNBEKANNT]** – nicht öffentlich dokumentiert. Das NBT-EVO-Toolkit (GitHub) führt `HU_ENTRY*` nur als „Entry / EntryNav — different SoC".
- **Bekannter Fehler (F30 SOP–07/2012):** CID dunkel, „NO SIGNAL", Fehler B7F8C3. Abhilfe: Fahrzeug mit ISTA/P programmieren, I-Stufe **F020-12-11-504 oder höher**, sonst Headunit tauschen (SI B65 10 12). Gilt für F30. Für einen F20 aus 01/2012 auf derselben F020-Plattform **[WAHRSCHEINLICH]** relevant.

---

## 4. BimmerCode: offizielle F20/F21-Liste (bimmercode.app/cars/f20)

### 4.1 iDrive/Headunit-Optionen und ihre Voraussetzungen [DOK]

| BimmerCode-Option | Werte | Voraussetzung laut BimmerCode | HU_ENTRY? |
|---|---|---|---|
| Start animation (2 Varianten) | ALPINA, BMW 1/2, BMW i, Christmas, Connected Drive, M, MINI, Rolls-Royce … | HU_NBT bzw. HU_NBT_EVO | **Nein** (nicht gelistet) |
| Sport displays / Sport displays color | Active/Not active; Orange/Red | HU_NBT oder HU_NBT_EVO | **Nein** (nicht gelistet) |
| Warning at startup (Rechtshinweis) | Not active | HU_NBT oder HU_NBT_EVO | Nein |
| Volume popup | Active/Not active | HU_NBT oder HU_NBT_EVO | Nein |
| Service history | Active/Not active | HU_NBT oder HU_NBT_EVO | Nein |
| Tire pressure control | Druck / Temperatur+Druck / aus | HU_NBT oder HU_NBT_EVO | Nein |
| Display full text messages | Active | HU_NBT oder HU_NBT_EVO | Nein |
| xView, Rear view camera zoom, Video via USB, Additional video codecs, Video in motion, CarPlay fullscreen | – | HU_NBT / HU_NBT_EVO | Nein |
| Maximum volume at startup | 10–50 % | HU_NBT oder HU_NBT_EVO | Nein |
| Warning chime | BMW/BMW i/Mini/Rolls-Royce | HU_NBT oder HU_NBT_EVO | Nein |
| Ringtone | 2 Varianten | Combox_Media bzw. HU_NBT/NBT_EVO | Nein (nur mit Combox_Media, Combox-Variante) |
| Bluetooth audio streaming (1 von 2 / 2 von 2) | Active | (1) HU_NBT/NBT_EVO, (2) Combox_Media | Nein |
| Checkbox acoustical lock confirmation / Checkbox daytime running light (head unit) | Active/Not active | HU_NBT oder HU_NBT_EVO | Nein |
| Shut off iDrive system when driver door is opened | Active/Not active | **FEM_01** (nicht Headunit) | Ja, sofern FEM_01 – gehört ins FEM-Dossier |

**Ergebnis:** Für HU_ENTRY gibt es in der offiziellen BimmerCode-Liste **keine** Headunit-Komfortoption. Alles Weitere wäre Expertenmodus (FDL-Parameter), siehe Abschnitt 5.

### 4.2 KOMBI-Optionen [DOK]

| BimmerCode-Option | Werte | Voraussetzung |
|---|---|---|
| Digital speed in board computer | Active/Not active | KOMBI L6 BO, L7_BASIS oder L7_MID |
| Empty menu item in board computer | Active/Not active | KOMBI L6 BO, L7_BASIS oder L7_MID |
| Average values reset | After 4 hours / After 8 hours / After every ride / Never | KOMBI L6 BO, L7_BASIS oder L7_MID |
| Low fuel warning 1 (dauerhaft) | 10/20/30/40/50 km bzw. 10/20/30 mi, Not active | KOMBI L6 BO, L7_BASIS oder L7_MID |
| Low fuel warning 2 (temporär) | 50/60/70/80/90 km bzw. 40/50 mi, Not active | KOMBI L6 BO, L7_BASIS oder L7_MID |
| SPORT+ driving mode (2 von 2) | Active (zusätzlich Teil 1 im ICMQL nötig) | KOMBI L6 BO, L7_BASIS oder L7_MID |
| Date in board computer | Active/Not active | KOMBI L7_BASIS oder L7_MID |
| Start logo | 50d, 135i, 140i, 235i, 240i, 340i, AG, M Performance, M2, M3, M4, M4 GTS, PHEV | KOMBI L7_BASIS oder L7_MID |
| M Performance logo (unten rechts) | Not active, 135i, 140i, 235i, 240i, 340i, 50d, 550d, PHEV | KOMBI L7_MID |
| Fuel consumption display maximum value | 20 / 30 l/100 km | KOMBI L7_MID |
| HUD-Optionen | – | KOMBI L6 BO (+ HUD-Hardware, beim F20 nicht relevant) |
| Seat belt reminder (diverse) | – | **ACSM_4B/ACSM_4C** (Airbag-Steuergerät, nicht KOMBI) |

**Offene Kernfrage:** Welche dieser KOMBI-Varianten meldet BimmerCode für den 2012er F20-KOMBI? Die Bedeutung der Kürzel L6/L7/BO/BASIS/MID ist nicht öffentlich dokumentiert. Interpretationen habe ich bewusst weggelassen. → In der App nach dem Verbinden ablesen.

---

## 5. HU_ENTRY: Codierparameter (FDL) im Einzelnen

Allgemein: Fast alle öffentlich dokumentierten Headunit-Parameter stammen von **HU_CIC** oder **HU_NBT**. Ob sie im HU_ENTRY-CAFD existieren, ist ohne Blick in den eigenen CAFD nicht belegbar.
**Empfehlung:** Den CAFD des eigenen HU_ENTRY in BimmerCode (Expertenmodus) bzw. E-Sys durchsehen und nur Parameter anfassen, die dort tatsächlich vorkommen.

| # | Funktion | Parameter (exakt wie zitiert) | Block | Werte | Belegt für | HU_ENTRY (dieses Auto) |
|---|---|---|---|---|---|---|
| 5.1 | Sportanzeigen (Leistung/Drehmoment) | `EFF_DYN_SPORT_CID` | 3000 | nicht_aktiv → aktiv | HU_CIC (Tabelle); HU_ENTRY laut Forum-Snippet | **[EXPERIMENTELL]**: Das Menü erscheint laut Snippet, bei HU_ENTRY ohne Navi aber Anzeige teils 0. Daten hängen vom Motor ab (bei Dieseln teils keine). N13 unbelegt. |
| 5.2 | Einheiten Sportanzeige (kW/PS, Nm/lb-ft) | `EFF_DYN_SPORT_UNIT` | 3000 | nicht_aktiv → aktiv | HU_CIC | [EXPERIMENTELL]: Snippets berichten, dass die Einheit trotzdem kW/Nm blieb. |
| 5.3 | Farbe Sportanzeige (orange → rot) | `M_VEHICLE` | 3000 HMI | nicht_aktiv → aktiv | HU_NBT | [UNBEKANNT] |
| 5.4 | Rechtshinweis beim Start | `LEGAL_DISCLAIMER_TIME` | 3001 EXBOX | ld_mit_timeout → kein_ld | HU_CIC, HU_NBT | [UNBEKANNT]: Ob HU_ENTRY ohne Navi überhaupt einen Startdisclaimer zeigt, ist offen. |
| 5.5 | Startanimation/Logo | `STARTUP_EMBLEM` | 3001 (EXBOX) | variant_00…variant_09 (00/02–06 ConnectedDrive, 01 M, 07 weiß, 08 braun wie CIC, 09 „Merry XMas") | HU_NBT; Hinweis auf „Headunit Entrynav" ohne Werte | [UNBEKANNT], eher unwahrscheinlich. BimmerCode bietet es nur für NBT/NBT_EVO an. |
| 5.6 | Video in Motion | `SPEEDLOCK_X_KMH_MIN`, `SPEEDLOCK_X_KMH_MAX` (werte=FF), `VIDEO_NUR_MIT_HANDBREMSE` | 3000 | – | HU_CIC/HU_NBT | **[NICHT KOMPATIBEL]**: Laut Sammlung unterstützt HU_ENTRY kein Video in Motion. Es gibt ohnehin keine Video-Quelle (kein DVD/Video-USB). Rechtlich in DE unzulässig während der Fahrt. |
| 5.7 | Office/Service-Meldungen während der Fahrt | `SERVICES_MESSAGES_SPEEDLOCK_CONDITION`, `OFFICE_MESSAGES_SPEEDLOCK_CONDITION` | 3000 HMI | → none | HU_NBT | [UNBEKANNT]. Office setzt laut BMW eine Combox voraus. |
| 5.8 | Volltext-SMS | `PIM_Driving_Text` | 3003 | up_to_three_lines → whole_text | HU_NBT | [UNBEKANNT]/unwahrscheinlich |
| 5.9 | BT-Audio-Streaming | (BimmerCode-UI-Option, Combox) | – | – | HU_NBT + Combox_Media | Ohne Combox: laut BMW-Doku Combox-Funktion; Forenaussagen widersprüchlich (Snippets). → **[UNBEKANNT]**, eher nicht codierbar. Mit Combox: ab Werk vorhanden [WAHRSCHEINLICH]. |
| 5.10 | Eigener Klingelton (Inband) | `Inband_ringing` / `INBAND_RINGING` | 3003 (HU_CIC) bzw. 3001 (CMB_MEDIA) | nicht_aktiv → aktiv | HU_CIC, CMB_MEDIA | [UNBEKANNT] für HU_ENTRY mit 6NH |
| 5.11 | Max. Lautstärke beim Start | `VOL_MAX_ON` | 3002 | z. B. 19 (=25 %) → höher | HU_CIC (nicht verifizierte GitHub-Sammlung) | [UNBEKANNT] |
| 5.12 | Reifendruck/Temperatur im iDrive | `RDC_SAFETY` (HU_CIC/NBT, 3001); `RDC_DRUCK_TEMP` (HU_NBT, 3001) | 3001 | nicht_aktiv → aktiv; druck → druck_und_temperatur | HU_CIC/HU_NBT | [UNBEKANNT]. Setzt RDC-Sensoren voraus; prüfen, ob das Auto nur Reifenpannenanzeige hat. |
| 5.13 | DAB | `Radio_dab`, `Dab_laendervarianten`, `dab_standard`, `following_available`, `following_dab_fm` | 3002 | z. B. nicht aktiv → aktiv / ece / dab | HU_CIC („partly" funktionierend) | [UNBEKANNT]: nur mit DAB-Tuner-Hardware. Ein Forum-Snippet berichtet Erfolg bei HU_ENTRYNAV mit DAB. |
| 5.14 | Entwicklermenü (Build/Datum/Versionen) | `ENTWICKLER_MENUE` | 3000 HMI | nicht aktiv → aktiv | HU_CIC | [UNBEKANNT] |
| 5.15 | Servicehistorie im iDrive | `SERVICE_HISTORY` | 3000 | nicht_aktiv → aktiv | HU_NBT/HU_CIC (nicht verifizierte Sammlung) | [UNBEKANNT] |
| 5.16 | Tagfahrlicht-Checkbox im iDrive | `Daydriving_light` | 3000 | Perm_off ↔ standard | HU_CIC | [UNBEKANNT] |
| 5.17 | Akustische Verriegelungsbestätigung (Checkbox) | `Acoustical_lock_confirm` | 3000 | nicht aktiv → aktiv | HU_CIC (benötigt Werks-Alarmanlage) | [UNBEKANNT] |
| 5.18 | SPORT-Modus konfigurierbar | `Macro_fds` (HU_CIC) bzw. `MAKRO_FDS` (bmw-syndikat, F20 gelistet) | 3000 | popup_only → popup_and_config | HU_CIC/HU_NBT | [UNBEKANNT] für HU_ENTRY |
| 5.19 | Video über USB, Codecs | `ENT_CODEC_OGG`, `ENT_CODEC_XVID`, `ENT_CODEC_VCD`, `API_USB_VIDEO` | 3000 HMI | – | HU_NBT | **[NICHT KOMPATIBEL]** (BimmerCode: nur NBT/NBT_EVO) |
| 5.20 | CarPlay | – | – | – | HU_NBT_EVO | **[NICHT KOMPATIBEL]** |

### Weitere Punkte aus dem Auftrag

- **Datums-/Zeitformat, Einheiten:** Das sind normale Benutzereinstellungen im iDrive bzw. Kombi. Codierparameter für HU_ENTRY wurden nicht gefunden. → [UNBEKANNT]
- **Geschwindigkeitsabhängige Lautstärke, Gong-/PDC-Lautstärke:** Für HU_ENTRY wurden keine dokumentierten Parameter gefunden. BimmerCode „Warning chime" ist NBT-only. → [UNBEKANNT]
- **RDS:** Keine Codierquelle. Eine Radio-Settings-Sammlung nennt nur HU_NBT-Parameter (`RADIO_COUNTRY`, `FM_DEEMPHASIS`, `ANZEIGE_FREQ`), ohne Blocknummer. → für HU_ENTRY [UNBEKANNT]
- **ECO PRO im iDrive:** Factory-Funktion. Keine HU_ENTRY-Codierparameter gefunden. → [UNBEKANNT]
- **Versteckte Service-/Diagnosemenüs der Headunit (Tastenkombination):** Kein Nachweis für HU_ENTRY gefunden. Der NBT-Weg „Controller nach oben halten → Speedlock-Menü" setzt `SPEEDLOCK_FREISCHALTMENU` voraus und gilt für NBT. → [UNBEKANNT]

### Bekanntes Risiko beim Codieren von HU_ENTRY [DOK, nur Snippet]

Ein 228i-Halter (F22) codierte HU_ENTRY in E-Sys mit „einfachen" Änderungen. Nach „CODE FDL" startete die Headunit mit deutscher Oberfläche und ihm fremden Optionen (Bluetooth/DAB fehlten). Der CAFD war in E-Sys nicht mehr grün markiert, und „Code" war ausgegraut. Die Wiederherstellung gelang laut Thread nur mit Anleitung aus dem Forum.
**Konsequenz:** Vor jeder HU_ENTRY-Änderung ein vollständiges Backup anlegen (BimmerCode-Backup bzw. FA + Original-FDL), ein Ladegerät anschließen und nur einzelne Parameter ändern.

---

## 6. Eigene Software/Apps auf HU_ENTRY – strikte Trennung

| Ebene | Stand |
|---|---|
| (1) Normales Codieren (FDL/VO über BimmerCode/E-Sys) | Möglich, siehe Abschnitt 5. Ändert nur vorhandene Parameter und installiert keine Software. [DOK] |
| (2) Theoretische Softwaremodifikation | Es gibt einen Software-Update-Pfad: Ethernet FEM→HU „solely to update the headunit's software", also Flashen per ISTA/P mit BMW-signierter Software. Für eigene, unsignierte Software oder Apps ist **kein öffentlich dokumentierter Weg** bekannt. OS und SoC sind nicht öffentlich dokumentiert. [UNBEKANNT] |
| (3) Tatsächlich gezeigte Methoden | **Keine öffentliche Evidenz gefunden.** Das NBT-EVO-Toolkit (QNX auf TI OMAP usw.) schließt HU_ENTRY ausdrücklich aus („different SoC"). Methoden für NBT/NBT EVO (z. B. Boot-Logos per USB, CarPlay-Aktivierung) gelten **nicht** für HU_ENTRY. |

Fazit: Apps, eigene Software, Video oder CarPlay auf der 2012er HU_ENTRY gibt es nach öffentlichem Wissensstand nicht. Wer so etwas will, braucht realistisch einen Headunit-Tausch (Retrofit, z. B. NBT/NBT EVO mit FSC). Das ist Aufwand „hoch" und nicht Gegenstand dieser Recherche.

---

## 7. KOMBI (Kombiinstrument, F20 2012)

### 7.1 Hardware-Kontext [DOK für F30, WAHRSCHEINLICH für F20]

Laut F30-Schulungsunterlage gibt es ein **Basis-Kombi** mit TFT 320×120 px (2,7") und ein **Kombi High (SA 6WA)** mit TFT 640×160 px (5,7"). Das Kombi High ist Pflicht bei Navigation Professional 609, Spurverlassenswarnung 5AD, HUD 610 und Speed Limit Info 8TH.
Beim F30 zeigen beide Varianten in den kleinen Rundinstrumenten Tankinhalt und Motoröltemperatur. Für den F20-Kombi ist das **nicht** belegt [UNBEKANNT].
Ein F20 mit Radio Professional ohne Navi hat **wahrscheinlich das Basis-Kombi**, es sei denn, 6WA ist separat verbaut. → FA prüfen.

### 7.2 Dokumentierte KOMBI-Parameter

| Funktion | Parameter (exakt) | Block | Werte | Quellen/Status |
|---|---|---|---|---|
| Digitaltacho im BC | `BC_DIGITAL_V` (Tabelle schreibt `BC_Digital_V`) | 3000 | nicht_aktiv → aktiv | [DOK]: F30-Referenz (Snippet), Community-Tabelle, GitHub-Sammlung. BimmerCode-Standardoption „Digital speed in board computer". |
| Tachokorrektur der Digitalanzeige | `BC_V_KORREKTUR`, `BC_DIGITAL_V_KORREKTUR` | 3000 | aktiv ↔ nicht_aktiv | [EXPERIMENTELL]: Belege überwiegend aus E-Serie. F-Serie nur in einer nicht verifizierten GitHub-Sammlung. Rechtliche Grenze beachten (Tacho darf nie weniger als die tatsächliche Geschwindigkeit anzeigen). |
| Start-Logo im Kombi | `BMW_LOGO` (+ laut bmw-syndikat `MPM_ENABLE`, `MPM_LOGO`) | 3000 | AG → MPM (Community-Tabelle); BimmerCode-Wertliste siehe 4.2 | [DOK]. Widerspruch: Eine GitHub-Sammlung behauptet „ag = Alpina". Nach BimmerCode-Liste und Tabelle ist „AG" eher das Standard-Logo. → [UNBEKANNT], was „AG" genau zeigt. |
| Weiße statt orange Kombibeleuchtung nachts | `DIM_NACHT_EIN` | 3007 | werte 32 → FF | [EXPERIMENTELL] (Community-Tabelle „Yes"; laut Tabelle wird auch die Navi-Nachtumschaltung deaktiviert) |
| Hintergrundfarbe Skala | `HINTERGRUND_FARBE_TAG`, `HINTERGRUND_FARBE_NACHT` | 3001 | Orange → Orange/Grau | [DOK], laut Tabelle „Only for instrument cluster high" (6WA) |
| BC-Auto-Reset | `BC_AUTORESET_ZEIT` | 3000 | werte=04 (4 h, hex) … FF (nie) | [EXPERIMENTELL] (nur GitHub-Sammlung). BimmerCode-UI „Average values reset" ist [DOK]. |
| SPORT+-Anzeige | `FDS_MENUE_TEXT_1…4`, `FDS_MENUE_SIGNAL_1…4` | 3000 | menue_4 → menue_3 | [EXPERIMENTELL] (GitHub-Sammlung). BimmerCode „SPORT+ driving mode (2 von 2)" ist [DOK] (+ ICMQL Teil 1). |
| MSA-„Aus"-Hinweis | `MSA_VERFUEGBARANZEIGE_ENABLE` | 3000 | aktiv → nicht_aktiv | [EXPERIMENTELL] (GitHub-Sammlung) |
| Gong beim Rückwärtsgang | `R_GANG_AKUSTIK_ENABLE` | 3000 | aktiv → nicht_aktiv | [EXPERIMENTELL] (GitHub-Sammlung) |
| Geschwindigkeitsbegrenzer LIM | `SLD_ENABLE` (KOMBI 3003) + ICM: `SLD_Funktion`, `C_Umschaltung_ACC_DCC`, `LDM_SET_Taste` | 3003 | aktiv; zugelassen; nur_SET__O | [EXPERIMENTELL] (GitHub-Sammlung). Setzt Tempomat voraus, Fahrerassistenz → Risiko hoch. |
| HUD-Startbildschirm, HUD-Blinker, Lane-Lines | `HUD_START_UP_SCREEN_ANZ_ZEIT`, `HUD_PIA_BLINKER`, `Blinker_HUD_ENABLE`, `HUD_TLC_ENABLE` | 3000/3008 | – | Nicht relevant, weil kein HUD verbaut. |

### 7.3 KOMBI-Testmenü („Geheimmenü") [DOK für F30, WAHRSCHEINLICH für F20]

Quelle: BMW ST1113 „F30 Displays, Indicators and Controls", Kap. 2.7.2 „Test functions".

- **Start:** Klemme 15 EIN, **Reset-Taste im Kombi 10 s gedrückt halten**.
- **Sperre:** „Only the first four test functions are freely accessible." Die Entsperrung erfolgt über **Testfunktion 04**: „entering the cross total of the last five digits of the vehicle identification number" (Quersumme der letzten fünf Stellen der FIN).
- **Bedienung:** Kurz drücken = weiterblättern, lang drücken = Funktion aufrufen.
- **Testfunktionen (F30):**
  01 Identifikation, 02 Systemtest, 03 Testende, 04 Testfunktionen entsperren, 05 Momentanverbrauch, 06 Reichweite/Verbrauch, 07 Tankgeberwerte, **08 Kühlmittel-, Außen-, Motoröltemperatur**, 09 BC-Durchschnittswerte, 10 Tacho/Drehzahlmesser, 11 Bordnetzspannung, 12 Akustik (Gongs auslösen), 13 Fehlerspeicher lesen („DTC"), 14 LCD dimmen, 15 PWM dimmen, 16 CBS, 17 Check-Control, **18 Korrekturfaktor Verbrauch**, **19 Software-Reset/RAM reload**.
- **Beenden:** Klemme 15 AUS, Taste > 10 s halten, Testfunktion 03 und dann 19 aufrufen. Beim Verlassen werden die Funktionen ab Nr. 5 wieder gesperrt.
- **Risiko:** Anzeigefunktionen sind harmlos. 18 (Verbrauchskorrektur) und 19 (Reset) verändern Werte bzw. setzen zurück → nur bewusst nutzen.
- **Achtung:** Die E-Serien-Nummerierung aus Drittquellen (z. B. youcanic: 19 = Lock, 07 = Kühlmittel) ist **anders** und gilt nicht für die F-Serie.

### 7.4 Weitere KOMBI-Themen

- **BC-Umfang:** Laut F30-Doku zeigt der BC Reichweite, Durchschnittsverbrauch, Durchschnittsgeschwindigkeit, (mit Navi) Entfernung/Ankunft/Pfeil, Datum, Speed-Limit-Info und ECO-PRO-Bonusreichweite. Die Auswahl erfolgt im iDrive über „Einstellungen → Informationsanzeige". [DOK F30] Ohne Navi entfallen die Navi-Einträge [WAHRSCHEINLICH]. Zusätzlich per Codierung: Digitaltacho und Leerseite (BimmerCode).
- **ECO PRO:** Bonusreichweite und ECO-PRO-Anzeigen im Kombi werden in der F30-Doku für das Kombi mit erweitertem Funktionsumfang (6WA) gezeigt. Für das Basis-Kombi ist der Umfang [UNBEKANNT].
- **Geschwindigkeitswarnung:** Das ist eine iDrive-Benutzereinstellung („Fahrzeugeinstellungen → Geschwindigkeitswarnung"). Belegt nur aus Handbüchern anderer BMW-Modelle. [WAHRSCHEINLICH] Keine Codierung nötig.
- **Schaltpunktanzeige (Schaltgetriebe), Ganganzeige:** Keine Codierparameter gefunden. → [UNBEKANNT]
- **Zeigertest/Needle Sweep:** Für F-Serie keine Codierung gefunden. Testfunktion 02 „Systemtest" ist der einzige dokumentierte Selbsttest; ob dabei die Zeiger ausschlagen, ist nicht beschrieben. → [UNBEKANNT]
- **Gurtwarnung (nur Dokumentation, sicherheitskritisch):** Laut BimmerCode liegt die Codierung im **ACSM** (ACSM_4B/ACSM_4C), nicht im KOMBI. Eine Community-Tabelle (F30 2012, E-Sys) nennt `SeatBeltReminder_SBR_Fahrer` / `SeatBeltReminder_SBR_Beifahrer` (ACSM, 3000 Ausstattungsflags, aktiv → nicht_aktiv). **Keine Empfehlung** – sicherheitsrelevant.
- **Öltemperatur/Ölstand:** Die Öltemperatur ist über Testfunktion 08 ablesbar [WAHRSCHEINLICH]. Eine Codierung für eine permanente Öltemperaturanzeige beim F20 wurde nicht gefunden. Der elektronische Ölstand wird im iDrive angezeigt (Factory-Funktion; nicht recherchiert) → [UNBEKANNT].

---

## 8. Vorgehensempfehlung (kurz)

1. In BimmerCode verbinden und notieren, welche Steuergeräte erkannt werden: Name des KOMBI (L6 BO / L7_BASIS / L7_MID / anders?) und ob **HU_ENTRY** in der Liste erscheint und im Expertenmodus codierbar ist.
2. **Backup** aller Codierungen in BimmerCode anlegen und eine stabile Spannungsversorgung (Ladegerät) anschließen.
3. Zuerst KOMBI-Standardoptionen mit geringem Risiko: Digitaltacho, Leerseite, Auto-Reset, Reservewarnungen.
4. HU_ENTRY im Expertenmodus nur nach Sichtprüfung, ob der Parameter im eigenen CAFD existiert. Immer nur einen Parameter ändern und testen. Kandidat Nr. 1: `EFF_DYN_SPORT_CID` (Ergebnis offen).
5. Testmenü (Abschnitt 7.3) ist ohne Codierung nutzbar, etwa für die Öltemperatur.

---

## 9. Offene Fragen

1. Welche KOMBI-Variante meldet BimmerCode für den F20 aus 01/2012 (L6 BO, L7_BASIS, L7_MID oder eine nicht unterstützte)? Davon hängen Start-Logo, Datum im BC und M-Performance-Logo ab.
2. Unterstützt BimmerCode HU_ENTRY (CAFD_000000F9) im Expertenmodus? Die öffentliche Liste nennt kein HU_ENTRY.
3. Ist der HU_ENTRY dieses F20 wirklich die Continental-Variante („ENTRY CONTI")? Die BMW-SI nennt sie nur für den F30 (US). Prüfung über Typschild oder ETK nach FIN.
4. Liefert die N13-DME (MEVD17.2.x) Leistungs- und Drehmomentdaten für die Sportanzeige? Kein Beleg.
5. Existieren `EFF_DYN_SPORT_CID`, `LEGAL_DISCLAIMER_TIME`, `STARTUP_EMBLEM`, `ENTWICKLER_MENUE` und `VOL_MAX_ON` überhaupt im HU_ENTRY-CAFD dieses Autos? Nur durch Auslesen klärbar.
6. Welche Telefonie-/Combox-Option ist verbaut (6NH, 6NS, 6NK, 6NL …)? Davon hängen BT-Audio, Klingelton und Office ab. Zu 6NK/6NS wurden keine Primärquellen gefunden.
7. Gelten die F30-Testfunktionen 1:1 für das F20-Kombi (Nummerierung, Öltemperatur in Nr. 08)?
8. Hat das Auto RDC-Sensoren oder nur die Reifenpannenanzeige (RPA)? Das ist relevant für jede Reifendruck-/Temperaturanzeige.
9. Ist DAB-Hardware vorhanden?
10. Ist das ISTA/P-Update gegen „NO SIGNAL" (I-Stufe ≥ F020-12-11-504) bereits erfolgt? Aktuelle I-Stufe auslesen.

---

## 10. Quellen

**Primär (BMW):**
- BMW SI B65 09 16 „Radio/Navigation/Head Unit Identification" (Feb. 2019), NHTSA-Kopie: https://static.nhtsa.gov/odi/tsbs/2018/MC-10154755-9999.pdf
- BMW SI B65 10 12 „Headunit-Basic: CID is blank and NO SIGNAL is displayed" (Jan. 2013): https://static.nhtsa.gov/odi/tsbs/2013/MC-10149314-9999.pdf
- BMW ST1113 „F30 Entertainment and Communication" (Schulungsunterlage): https://archive.org/download/BMWTechnicalTrainingDocuments/ST1113%20F30%20Complete%20Vehicle/07_F30_Entertainment_and_Communication1.pdf
- BMW ST1113 „F30 Displays, Indicators and Controls" (Schulungsunterlage, Kombi und Testfunktionen): https://archive.org/download/BMWTechnicalTrainingDocuments/ST1113%20F30%20Complete%20Vehicle/06_F30%20Displays%2C%20Indicators%20and%20Controls.pdf

**Hersteller-Tool:**
- BimmerCode, unterstützte Codierungen BMW 1er F20/F21: https://bimmercode.app/cars/f20

**Community-Sammlungen (abgerufen):**
- Community-Tabelle (F-Serie; HU_CIC, HU_NBT, KOMBI): https://docs.google.com/spreadsheets/d/16O4RKIMekWFCs5jPW3T_7li0yIEvgZfFI0u3l0RmSwU/pubhtml
- Autoescaner-Tabelle (F30 2012, E-Sys; HU_CIC, ACSM): https://docs.google.com/spreadsheets/d/1G_C7954Z4094jLdbR0QjqXQYY6w6-rToothcTUPb5Fs/edit
- Community-Tabelle (X5 F15; HU_NBT, KOMBI): https://docs.google.com/spreadsheets/d/1UreLsK1PwycTWeW6OL71HOoVpLtKtfwRMRSvlsiC8JY/edit
- bmw-syndikat Codier-Datenbank (STARTUP_EMBLEM, BMW_LOGO/MPM_*, MAKRO_FDS): https://www.bmw-syndikat.de/bmwsyndikatforum/bmw_codieren_datenbank.asp?goto=83
- GitHub Dauxdu/bmw-coding (nicht verifizierte Sammlung, mit Vorsicht):
  - https://raw.githubusercontent.com/Dauxdu/bmw-coding/HEAD/e-sys/02-Codings/Instrument-Cluster.md
  - https://raw.githubusercontent.com/Dauxdu/bmw-coding/HEAD/e-sys/02-Codings/Head-Unit/iDrive-Features.md
  - https://raw.githubusercontent.com/Dauxdu/bmw-coding/HEAD/e-sys/02-Codings/Head-Unit/Video-in-Motion.md
- GitHub vandelayautollc/nbt-evo-toolkit (Plattformübersicht): https://raw.githubusercontent.com/vandelayautollc/nbt-evo-toolkit/HEAD/docs/00-platform-overview.md
- youcanic, Hidden Menu (E-Serie, zur Abgrenzung): https://www.youcanic.com/access-bmw-hidden-menu/

**Nur über Suchmaschinen-Snippets ausgewertet (Seite blockiert oder lädt nicht):**
- 2addicts/bimmerpost „Sport display on HU_Entry enabled but not working?": https://www.2addicts.com/forums/showthread.php?t=1083314
- bimmerpost „Coding Sport Display on HU_ENTRY?": https://f30.bimmerpost.com/forums/showthread.php?t=1138487
- 2addicts/bimmerpost „Major Coding Problem. Lost Access To Hu_entry": https://www.2addicts.com/forums/showthread.php?t=1062438 (auch https://f15.bimmerpost.com/forums/showthread.php?p=31097076)
- bimmerpost „Coding DAB Radio": https://f30.bimmerpost.com/forums/showthread.php?t=939303
- bimmerfest „Power and Torque Meters in Sport Display": https://www.bimmerfest.com/threads/power-and-torque-meters-in-sport-display.723339/
- F30 Coding Reference Guide v1.7: https://www.slideshare.net/slideshow/f30codingreferenceguidev17pdf/252684326 bzw. https://www.scribd.com/doc/314263744/F30-Coding-Reference-Guide-v1-7
- motor-talk (BT-Streaming F20/F30): https://www.motor-talk.de/forum/audio-streaming-ueber-bluetooth-nachruesten-codieren-t6554084.html, https://www.motor-talk.de/forum/radio-bmw-professional-audio-streaming-t5102516.html, https://www.motor-talk.de/forum/bluetooth-audio-streaming-t5135224.html
- 5series.net „true speed" (BC_V_KORREKTUR / BC_DIGITAL_V_KORREKTUR, E-Serie): https://5series.net/forums/e60-discussion-2/true-speed-150479
- BMW X3 Handbuch (Geschwindigkeitswarnung, anderes Modell): https://www.manualslib.com/manual/2549622/Bmw-X3.html?page=148
