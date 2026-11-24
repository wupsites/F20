# 01 – BMW F20 (2012): E/E-Architektur und Diagnoseprotokoll

Recherche-Rohbericht für ein privates, **rein lesendes** Diagnose-/Analysewerkzeug.
Fahrzeug: BMW 116i F20, Produktion 24.01.2012, N13B16 (1,6 l, 100 kW/136 PS), Schaltgetriebe,
Radio Professional (HU_ENTRY), keine Navigation, MFL, Sitzheizung vorn, PDC hinten, Nebelscheinwerfer, Regensensor.

Stand der Recherche: 24.11.2026.

## Evidenz-Kennzeichnung

| Tag | Bedeutung |
|---|---|
| **[DOK]** | In einer zitierten Quelle belegt (Quellen-Nr. in eckigen Klammern, z. B. `Q3`). |
| **[WAHRSCHEINLICH]** | Technisch naheliegend, abgeleitet oder nur indirekt belegt (z. B. aus G-Serien-Trace oder F30-Material übertragen). |
| **[UNBEKANNT]** | Konnte nicht verifiziert werden. Muss am echten Fahrzeug geprüft werden. |

Zur Belastbarkeit der Quellen:

- **Q1–Q4 (EdiabasLib/Deep OBD)** ist Open-Source-Code, der real mit BMW-Fahrzeugen arbeitet. `VehicleSeries.xml` ist laut Kopf aus ISTA-Daten generiert (Version 4.62.30). Der G31-Trace `enet.sim` ist ein **G-Serien-Mitschnitt über ENET**, kein F20-Mitschnitt. Die UDS-Inhalte (DIDs, Layouts) gelten BN2020-weit; der Transport ist anders.
- **Q5–Q14 (emdzej „EdiabasX SGBD Reference")** sind automatisch erzeugte Dokumentationen echter BMW-SGBDs (FEM_20, REM_20, ENTRY, ZGW_01, MEVD1725 usw.). Es sind jeweils **neuere Revisionen** (z. B. FEM_20 Rev. 17.000, mit SP2021-Hinweisen). Nicht jeder Job muss in der Software-Version eines 2012er-Fahrzeugs vorhanden sein.
- Foren und Händlerseiten (Q17–Q22) sind Community-Quellen. Sie gelten nur als schwache Belege und sind entsprechend markiert.

---

## 0. Kurzfassung

1. **Das zentrale Gateway (ZGM/ZGW) ist im FEM integriert.** Es hat eine eigene Diagnoseadresse **0x10**. Der Karosserieteil des FEM (FEM_BODY, mit den Funktionen von CAS, JBE und FRM) antwortet unter **0x40**. Das REM liegt unter **0x72**. [DOK Q2, Q18, Q20]
2. **Busse:** K-CAN 100 kbit/s; K-CAN2 (Body-CAN), PT-CAN (FA-CAN), PT-CAN2 und D-CAN je 500 kbit/s; FlexRay 10 Mbit/s; Ethernet 100 Mbit/s (nur OBD-Zugang zum Programmieren); dazu LIN als Sub-Bus. [DOK Q15, Q18] Ob am HU_ENTRY ein MOST-Ring hängt, ist unklar. [UNBEKANNT]
3. **UDS über D-CAN** nutzt 11-Bit-CAN mit 500 kbit/s und ISO-TP mit **Extended Addressing**:
   - Tester sendet auf **0x6F1** (0x600 | 0xF1). Das erste Datenbyte ist die Zieladresse.
   - Das Steuergerät antwortet auf **0x600 | SG-Adresse**. Das erste Datenbyte ist 0xF1.
   - Funktionale Adresse: **0xDF**.
   - Belegt in Q3 und Q4 (ELM327-Treiber und Adapter-Firmware von EdiabasLib) sowie in Q16. [DOK]
4. **Identifikations-DIDs:**
   - F190 (VIN), F150 (SGBD-Index, 3 Byte), F101 (SVK_AKTUELL), F18A/F18B/F18C, F186, 100B (I-Stufe), 37FE (CPS = VIN7), 3F06 (Fahrzeugauftrag im VCM des ZGW), 1700 (km-Stand im FEM_BODY).
   - Fehlerspeicher: 19 02 0C. Infospeicher: 22 20 00.
   - Alle belegt in SGBD-Doku und/oder G31-Trace. [DOK]
5. **0F1820 und 0F1650** haben exakt das Format von SGBD-Index-Werten (DID F150, 3 Byte; im G31-Trace z. B. 0F2040, 0F1310, 0F1FF0). Welche SGBD-Varianten dahinterstehen, ist öffentlich **nicht** auffindbar. Die Zuordnungstabelle steckt in den BMW-Gruppendateien (`G_*.grp`). [UNBEKANNT]
6. **Codierdaten** werden per `22 3xxx` gelesen. Welche Blöcke es gibt, legt die CAFD fest. Beim Schreiben ist eine **Signatur** im Spiel: FEM und HU kennen den Fehlerort „Codierung: Signatur für Daten ungültig". [DOK Q5, Q7] Der genaue Algorithmus ist unbekannt. Deshalb ist Schreiben für dieses Projekt **tabu**.
7. **CAFD_000000F9** gehört laut Forum-Snippet zur Headunit-Familie CIC/„HU_CICHB" (schwacher Beleg). Dass sie auf dem eigenen Fahrzeug am HU_ENTRY sitzt, ist plausibel und lässt sich über `22 F1 01` an 0x63 prüfen. Die Version 007.007.001 bedeutet Haupt-/Neben-/Patch-Version 7/7/1. [WAHRSCHEINLICH]

---

## 1. Bustopologie F20 (2011/2012)

### 1.1 Bussysteme und Bitraten

| Bus | Bitrate | Rolle im F20 | Evidenz |
|---|---|---|---|
| K-CAN | 100 kbit/s, 2-Draht, eindrahtig notlauffähig | Karosserie mit niedriger Datenrate, z. B. IHKA, ZBE | [DOK Q15, Q18] |
| K-CAN2 (neuere Bezeichnung: Body-CAN) | 500 kbit/s | Karosserie mit höherer Datenrate; das REM hängt an K-CAN2 | [DOK Q15, Q18]; REM-SGBD kennt „BODY-CAN Control Module Bus OFF" [DOK Q6] |
| PT-CAN (neuere Bezeichnung: FA-CAN / A-CAN) | 500 kbit/s | Antrieb und Fahrwerk, Sicherheit/Assistenz | [DOK Q15]; MEVD1725 kennt „A-/FA-CAN"-Botschaften [DOK Q9] |
| PT-CAN2 | 500 kbit/s, plus Weckleitung | Redundanz Motorsteuerung, Kraftstoffpumpe | [DOK Q15, Q18] |
| FlexRay | 10 Mbit/s je Kanal | Fahrdynamik und Motor. Der ZGW hat Sternkoppler (FEM-Hardwareoptionen `GW_STARCOUPLER1/2`) | Rate: [DOK Q15, Q18]; Sternkoppler: [DOK Q5]; F20-Knoten siehe 1.3 |
| D-CAN | 500 kbit/s, 2-Draht | Diagnose-Sub-Bus zur OBD-Buchse, endet am ZGW | [DOK Q15, Q18] |
| Ethernet (ENET am OBD) | 100 Mbit/s | Programmieren/Codieren über das ZGW. FEM-Wecksignal `ECUMA_GW_ETHERNET_OBD_ACT`, HW-Optionen `GW_ETHERNETPHY` / `GW_ETHERNETSWITCH` | [DOK Q15, Q18, Q5] |
| MOST | optisch, Ring | Infotainment. Beim F20 mit HU_ENTRY unklar, ob vorhanden | [UNBEKANNT], siehe 1.5 |
| LIN | Sub-Bus (ca. 20 kbit/s typisch) | z. B. Regen-/Licht-/Solarsensor, Schalterblöcke, Subbus-Sensoren (FEM DID 0x1600/0x16xx) | Existenz: [DOK Q5, Q15]; Bitrate: [WAHRSCHEINLICH] |
| ZSG-CAN, B2-CAN, IK-CAN, D-CAN, A-CAN | – | Diese Weck-/Busquellen nennt die FEM-SGBD (`ECUMA_GW_CAN_ZSG/FA/B/B2/IK/K/A/D/FR`). Welche davon ein 2012er-F20 physisch hat, ist offen | [DOK Q5]; Belegung im F20: [UNBEKANNT] |

Hinweis zur Nomenklatur: Neuere SGBD-Revisionen verwenden die BMW-Namen der Jahre ab etwa 2013, also „FA-CAN" (≈ PT-CAN), „Body-CAN" (≈ K-CAN2) und „Body2-CAN". [WAHRSCHEINLICH] Die Gleichsetzung ist abgeleitet. ISTA nutzt für denselben Bus je nach Stand unterschiedliche Namen.

### 1.2 Zentrales Gateway

- Das ZGM ist „als eigenständiges Steuergerät im FEM verbaut" und verbindet alle Bussysteme. Programmierdaten laufen über Ethernet und das ZGM. [DOK Q18; dort sind F20/F21/F22/F30 … getaggt]
- Diagnoseadresse des ZGW ist **0x10**. ISTA-abgeleitete Liste für Baureihe F20: `0x10 ZGW → G_ZGW`. [DOK Q2] Community-Liste: `FEM_GW [10]`. [DOK Q20, schwach]
- Das FEM integriert laut Q18 [DOK]:
  - aus dem CAS: Klemmensteuerung, EWS/Wegfahrsperre, Komfortzugang, ELV, ZV
  - aus der JBE: Fensterheber, Wisch-/Waschanlage, Klimafunktion, **Sitzheizung**, Spiegelheizung, **Regen-Licht-Solar-Beschlagsensor**
  - aus dem FRM: **Außenlicht** (inkl. Nebelscheinwerfer [WAHRSCHEINLICH]), Bremslicht, Innenlicht, Außenspiegel
  - aus dem ZGM: Gateway
- Die SGBD FEM_20 (Q5) enthält passend dazu CAS-Jobs (`STEUERN_CAS_ANLIEFERZUSTAND`, `STATUS_CAS_FREQ_TYPE` …) und speichert den **km-Stand redundant zum Kombi** (DID 0x1700). [DOK Q5]
- Die VCM-Funktion (Vehicle Configuration Management: Fahrzeugauftrag, I-Stufe, SVT) liegt im ZGW. Ein **Backup** liegt im REM: Die REM_20-SGBD hat `STATUS_VCM_VIN` (F190), `STATUS_VCM_I_STUFE_LESEN` (100B) und `VCM_DID_FA1/FA2` (0x3F1C/0x3F1D, „Fahrzeugauftrag … aus dem CAS"). [DOK Q6] EdiabasLib fällt für BN2020 entsprechend auf `G_FRM STATUS_VCM_VIN` und `G_FRM STATUS_VCM_I_STUFE_LESEN` zurück. [DOK Q1]

### 1.3 Steuergerät → Bus (F20)

| SG | Bus | Evidenz |
|---|---|---|
| FEM (ZGW + FEM_BODY) | alle (Gateway) | [DOK Q18, Q5] |
| REM | K-CAN2 / Body-CAN | [DOK Q18, Q6] |
| DME MEVD17.2.5 (N13) | FlexRay + PT-CAN (FA-CAN); PT-CAN2 vermutlich zusätzlich | FlexRay/FA-CAN: [DOK Q9, z. B. „FlexRay, Botschaft (EWS Information FEM)", „FlexRay Hardware: defekt", „A-/FA-CAN Hardware"]; PT-CAN2: [WAHRSCHEINLICH] |
| DSC | FlexRay (ggf. zusätzlich PT-CAN) | FlexRay: [DOK Q10, „Busfehler (Flexray)"]; PT-CAN: [UNBEKANNT] |
| EPS | FlexRay | [DOK Q11, „Flexray Bus OFF"] |
| ICM (ICM_QL) | FlexRay | [DOK Q12, „FlexRay Hardware Fehler", „FlexRay Knoten Synchronisationsfehler"] |
| IHKA (falls verbaut) | K-CAN | [DOK Q13, „K-CAN Botschaft …"] |
| ZBE (ZBE low) | K-CAN | [DOK Q14, „K-CAN Control Module Bus OFF"] |
| ACSM | PT-CAN oder FlexRay | [UNBEKANNT] |
| KOMBI | K-CAN/K-CAN2 und/oder PT-CAN | [UNBEKANNT] |
| HU_ENTRY | K-CAN2? MOST? (Ethernet-Jobs in der SGBD vorhanden) | [UNBEKANNT] |
| FZD | K-CAN (nur LIN-Erwähnungen in der SGBD) | [UNBEKANNT] |
| EKPS (falls vorhanden) | PT-CAN2 | [UNBEKANNT] |

Die belastbarste Methode am Fahrzeug: Das VCM des ZGW liefert Listen der SGs pro Bus (Tabelle 4.1, DIDs 0x3F0E K-CAN, 0x3F0F Body-CAN, 0x3F11 MOST, 0x3F12 FA-CAN, 0x3F13 FlexRay, 0x3F24 Ethernet). Diese Listen sollten zuerst gelesen werden. [DOK Q8; dass die DIDs im F20-ZGW identisch sind: WAHRSCHEINLICH]

### 1.4 OBD-Buchse

| Pin | Funktion | Evidenz |
|---|---|---|
| 6 / 14 | D-CAN High / Low (SAE J1962 / ISO 15765-4) | [WAHRSCHEINLICH, Normbelegung; in dieser Recherche nicht separat abgerufen] |
| 3, 11, 12, 13 | Ethernet-Paare (ISO 13400-4 „Option 1"). BMW-ENET-Kabel scheint diese Option zu nutzen | [DOK Q23 für Option 1; BMW-Bezug „appears": WAHRSCHEINLICH] |
| 8 | Ethernet-Aktivierungsleitung | [DOK Q23] |
| 16 / 4 / 5 | Kl. 30 / Masse / Signalmasse (Norm) | [WAHRSCHEINLICH] |

Laut Q16 werden auch gesetzlich vorgeschriebene OBD-II-Abfragen (0x7DF / 0x7E8) über das ZGM vermittelt. [DOK Q16, G-/F-Serie allgemein]

### 1.5 MOST beim HU_ENTRY

- Die SGBD `ENTRY` („Entry HeadUnit") enthält MOST-Jobs: `STATUS_VERSION_MOST_CONTROLLER`, Ringbruchdiagnose, `STEUERN_NWM_CONFIG_NOTOK`, „Gibt an, ob das SG den MOST-Ring geweckt hat". Sie enthält außerdem Ethernet-Jobs (`STATUS_GET_IPCONFIG`, Combox-Ethernet-Status). [DOK Q7]
- Forum-Snippet zum F30: „6NH without NAV gets you HU_ENTRY Head Unit and no Combox". [DOK Q21, schwach]
- Ob im eigenen F20 ein MOST-Ring physisch existiert (etwa nur das HU als Master ohne weitere Teilnehmer) bzw. ob das HU über K-CAN2 angebunden ist, ist **[UNBEKANNT]**. Prüfen über `22 3F 11` (VcmGetEcuListMost) an 0x10.

---

## 2. Steuergeräte-Inventar (116i, Anfang 2012)

### 2.1 Quellenlage

- **ISTA-abgeleitete SG-Liste der Baureihe F20** in EdiabasLib `VehicleSeries.xml`: Eintrag `Sr=F20, MS=F020, BT=BN2020`, 56 Einträge mit Diagnoseadresse und Gruppendatei. [DOK Q2] Das ist eine **Obermenge aller möglichen** SGs der Baureihe, keine ausstattungsbezogene Liste. Die Gruppennamen sind historisch: `G_CAS` = FEM_BODY, `G_FRM` = REM.
- **BMW-Adressen-Klartexttabelle** `TabDiagAdressen` aus der SGBD ZGW_01. [DOK Q8]
- **Community-Liste** aus einem MY2016-Fahrzeug (F-Serie), laut Autor unvollständig. [DOK Q20, schwach]
- **SGBD-Namen**, die eindeutig auf F020 verweisen: FEM_20 („Front Electronic Module"), REM_20 (Kommentar „F020_DKT_REM…"), MEVD1725 („ME V17.25 4 Zylinder N13"), DSC_20, EPS_20, ICMQL, FZD_20, IHKA20, ZBEL20 („ZBE low"), ENTRY („Entry HeadUnit"). [DOK Q5–Q14]

### 2.2 Erwartete SGs mit Adressen

„Adresse" meint die BMW-Diagnoseadresse = Extended-Address-Byte auf D-CAN. CAN-ID der Antwort = 0x600 + Adresse.

| SG (E-Sys-Name) | Adr. | Gruppe / SGBD | Verantwortung | Bus | Adresse belegt? | Verbau belegt? |
|---|---|---|---|---|---|---|
| FEM_GW / ZGW | **0x10** | G_ZGW | Zentrales Gateway, VCM (FA, I-Stufe, SVT) | alle | [DOK Q2, Q8, Q20] | [DOK Q18] |
| FEM_BODY | **0x40** | G_CAS → FEM_20 | CAS-, JBE- und FRM-Funktionen, Sitzheizung, Licht, Regensensor (LIN), Klima (IHKR) | K-CAN/K-CAN2 (+ LIN) | [DOK Q2 (G_CAS 0x40), Q20] | [DOK Q18, Q5] |
| REM | **0x72** | G_FRM → REM_20 | Heckfunktionen, Heckleuchten, Heckklappe, **PDC**, VCM-Backup | K-CAN2 | [DOK Q2 (G_FRM 0x72), Q20] | [DOK Q6, Q18] |
| DME (MEVD17.2.5) | **0x12** | G_MOTOR → MEVD1725 | Motorsteuerung N13 | FlexRay + PT-CAN | [DOK Q2, Q3-Trace, Q16] | SGBD für N13: [DOK Q9]; Verbau: [WAHRSCHEINLICH] |
| DSC | **0x29** | G_DSC → DSC_20 | ABS/DSC | FlexRay | [DOK Q2, Q20] | [WAHRSCHEINLICH] |
| EPS | **0x30** | G_EPS → EPS_20 | E-Lenkung | FlexRay | [DOK Q2, Q20] | [WAHRSCHEINLICH] |
| ICM | **0x1C** | G_ICMQL → ICMQL | Integrated Chassis Management (Quer-/Längsdynamik) | FlexRay | [DOK Q2, Q20] | [WAHRSCHEINLICH] |
| ACSM (Airbag) | **0x01** | G_AIRBAG | Crash Safety Module | [UNBEKANNT] | [DOK Q2, Q20] | [WAHRSCHEINLICH] |
| KOMBI | **0x60** | G_KOMBI | Instrumentenkombination, km-Stand (Master) | [UNBEKANNT] | [DOK Q2, Q20] | [WAHRSCHEINLICH] |
| HU_ENTRY (Radio Professional) | **0x63** | G_MMI → ENTRY | Headunit | [UNBEKANNT] | [DOK Q2 („HEADUNIT"), Q20 (HU_NBT2 [63]), Q22-Snippet (HU_ENTRYNAV [63] beim F20)] | Fahrzeugangabe |
| FZD | **0x56** | G_FZD → FZD_20 | Funktionszentrum Dach (Innenlicht, Mikro, ggf. SHD) | [UNBEKANNT] | [DOK Q2, Q20] | [WAHRSCHEINLICH] |
| ZBE (iDrive-Controller) | **0x67** | G_ZBE → ZBEL20 | Controller. Beim Radio Professional wahrscheinlich verbaut | K-CAN | [DOK Q2, Q20] | [UNBEKANNT] |
| IHKA | **0x78** | G_KLIMA → IHKA20 | **Nur** bei Klimaautomatik. Bei manueller Klima (IHKR) liegt die Funktion im FEM | K-CAN | [DOK Q2, Q20] | [UNBEKANNT] (Ausstattung prüfen) |
| EKPS | 0x17 | G_EKP | Elektronische Kraftstoffpumpensteuerung | [UNBEKANNT] | [DOK Q2] | [UNBEKANNT] |

### 2.3 Funktionen ohne eigenes SG

| Funktion | Wo | Evidenz |
|---|---|---|
| **PDC hinten** | **im REM integriert**. REM_20 hat DIDs 0xD640 (PDC-Funktionsanzeige), 0xD645–0xD64D (Abstände VL…HR), 0xD671 (PDC_STAT_SYSTEM) sowie Fehlerorte „PDC Sensoren hinten/vorn" | [DOK Q6] |
| Sitzheizung vorn | FEM (JBE-Funktion) | [DOK Q18] |
| Nebelscheinwerfer | FEM (Außenlicht aus FRM-Funktion) | [WAHRSCHEINLICH, Q18 nennt „Außenlicht"] |
| Regensensor (RLSBS) | FEM, LIN-Slave | Funktion im FEM: [DOK Q18]; LIN: [WAHRSCHEINLICH] |
| MFL | über Schaltzentrum Lenksäule (SZL). Im F20 keine eigene Adresse in der F20-Liste (0x02 „SLZ_LWS" steht nur in der generischen ZGW-Tabelle) | [UNBEKANNT] |
| Manuelle Klima (IHKR) | FEM | [WAHRSCHEINLICH, Q18 „Klimafunktion"] |

### 2.4 Nicht erwartet (Ausstattung fehlt)

Laut F20-Liste [DOK Q2] existieren diese Adressen in der Baureihe, sind beim beschriebenen 116i aber nicht zu erwarten [WAHRSCHEINLICH]:

- EGS 0x18 (Automatik)
- TBX 0x35 (Touchbox/Navi)
- COMBOX/ECALL/ATM 0x61 (laut Forum ohne Navi keine Combox [Q21, schwach])
- AMP 0x37, KAFAS 0x5D, FLA 0x5F, RDC 0x20, FRR/ACC 0x21, TRSVC 0x06, TMS_L/TMS_R 0x41/0x42 (Scheinwerfer-Treibermodule), LHM 0x43/0x44, AHM 0x71, SM_FA/BF 0x6D/0x6E, VDC 0x76, GWS 0x5E, HKFM 0x0D, PMA 0x2C, SME/EME (Hybrid) usw.

Ein Scan aller Adressen mit `22 F1 50` ist ungefährlich (rein lesend). Er ergibt die echte Liste: Ein nicht vorhandenes SG antwortet nicht, Timeout. Besser ist `22 3F 07` (VcmGetEcuListAll) am ZGW.

### 2.5 Auszug BMW-Adresstabelle `TabDiagAdressen` (ZGW_01-SGBD)

[DOK Q8]

`0x01 ACSM, 0x10 ZGW, 0x12 DME1, 0x17 EKP, 0x18 DKG, 0x1C ICM Q/L, 0x29 DSC_Mod, 0x30 EPS, 0x35 TBX, 0x37 AMP_HiFi, 0x40 CAS, 0x41/0x42 TMS_L/R, 0x56 FZD, 0x5D KAFAS, 0x60 KOMBI, 0x61 COMBOX, 0x63 HU, 0x64 „PDC in JBBF", 0x67 ZBE, 0x72 FRMFA, 0x78 IHKA, 0xDF Funktional UDS, 0xEF Funktional KWP, 0xF1 D-CAN Tester, 0xF4 Ethernet Tester, 0xF5 OBD Tester auf Ethernet, 0xFF SG unbekannt`

---

## 3. UDS (ISO 14229) über D-CAN: Transport im Detail

### 3.1 Physikalische Schicht

- **Bitrate 500 kbit/s, 11-Bit-Identifier, 2-Draht.** [DOK Q15 „D-CAN has a data transmission rate of 500 Kbps"]
- Der ELM327-Treiber von EdiabasLib setzt `ATPBC101` mit dem Kommentar „CAN B Custom Protocol 11/500 with var. DLC". [DOK Q3]

### 3.2 CAN-IDs und Extended Addressing

Belegt durch EdiabasLib `EdElmInterface.cs` und die Firmware `CanAdapterElm.X/main.c` [DOK Q3, Q4] sowie Q16 [DOK]:

| Richtung | CAN-ID | Byte 0 (Extended Address) | Byte 1 ff. |
|---|---|---|---|
| Tester → SG (physikalisch) | **0x6F1** (= 0x600 \| Quelladresse 0xF1) | Zieladresse (z. B. 0x12 DME, 0x40 FEM_BODY) | ISO-TP-PCI + UDS |
| SG → Tester | **0x600 \| SG-Adresse** (z. B. 0x612, 0x640, 0x672) | 0xF1 (Tester) | ISO-TP-PCI + UDS |
| Tester → SG (funktional) | 0x6F1 | **0xDF** („Funktional UDS") | ISO-TP-PCI + UDS |

Code-Belege:

- Senden: `can_out_msg.sid = 0x600 | source_address; data[0] = target_address;` [DOK Q4]
- ELM-Initialisierung: `ATSH6F1` (Sendeheader), `ATCF600` + `ATCM700` (Empfangsfilter 0x600–0x6FF) [DOK Q3]
- Header pro SG: `int canHeader = 0x600 | sourceAddr;` und `ATCEA<target>` (CAN Extended Address) [DOK Q3]

Beispiel aus Q16 (ReadDataByIdentifier 0x4300 an die DME, G-/F-Serie):

```
Tester → 0x6F1: 12 03 22 43 00 xx xx xx      (Byte0 = Ziel 0x12, SF Länge 3)
DME    → 0x612: F1 05 62 43 00 0D BA xx      (Byte0 = Tester 0xF1, SF Länge 5)
```

### 3.3 ISO-TP-Framing mit Extended Addressing

Nutzlast pro Frame ist um 1 Byte reduziert. [DOK Q24 Wikipedia ISO 15765-2] Die Werte unten stammen aus dem EdiabasLib-Code. [DOK Q3, Q4]

| Frame | Byte 0 | Byte 1 | Byte 2 | Bytes 3–7 | Nutzdaten |
|---|---|---|---|---|---|
| Single Frame | Adresse | `0x0L` (L = 1…6) | Daten | Daten | max. **6** Byte |
| First Frame | Adresse | `0x1H` | `LL` (12-Bit-Länge HLL) | 5 Byte Daten | 5 Byte |
| Consecutive Frame | Adresse | `0x2N` (N = 1…F, 0, …) | Daten | Daten | max. 6 Byte |
| Flow Control | Adresse **des Gegenübers** | `0x30` CTS / `0x31` Wait / `0x32` Overflow | Block Size | STmin | – |

Details aus EdiabasLib:

- **DLC immer 8, Padding 0x00.** Die Adapter-Firmware macht `memset(...,0x00)` und `dlc = 8`. Empfangene First Frames mit DLC < 8 werden verworfen. [DOK Q4] Ob die SGs DLC < 8 akzeptieren: [UNBEKANNT]. Empfehlung: immer DLC 8 mit 0x00-Padding.
- **Flow Control vom Tester** (beim Empfang langer Antworten): CAN-ID **0x6F1**, Byte 0 = **Adresse des antwortenden SG**, dann `30 BS STmin`. Die Firmware-Defaults sind `CAN_BLOCK_SIZE 0` (deaktiviert) und `CAN_MIN_SEP_TIME 0`. [DOK Q4] Der ELM-Pfad nutzt `ATFCSD <ecu>30 00 00` bzw. im Standardmodus BS = 3, ST = 0. [DOK Q3] Beispiel für eine Antwort der DME: `0x6F1: 12 30 00 00 00 00 00 00`.
- **Flow Control vom SG** (beim Senden langer Requests): Der Tester wartet auf CAN-ID 0x600 \| Ziel mit Byte 0 = 0xF1 und Byte 1 = 0x3x. Er beachtet BS und STmin; bei FS = 1 (Wait) wartet er erneut. [DOK Q3, Q4]
- **STmin-Kodierung** nach ISO 15765-2: 0x00–0x7F in ms, 0xF1–0xF9 = 100–900 µs. [DOK Q24]
- **Maximale Länge:** 12-Bit-FF-Länge, also bis 4095 Byte. EdiabasLib bildet längere BMW-FAST-Telegramme mit 2-Byte-Längenfeld ab. [DOK Q3, Q4]

Empfehlung für Linux SocketCAN (can-isotp) [WAHRSCHEINLICH, Ableitung aus den Belegen oben]:

```
tx_id = 0x6F1, rx_id = 0x600 + ECU
CAN_ISOTP_EXTEND_ADDR, ext_address = ECU
CAN_ISOTP_RX_EXT_ADDR, rx_ext_address = 0xF1
CAN_ISOTP_TX_PADDING, txpad_content = 0x00
FC-Optionen: bs = 0, stmin = 0
```

Pro Ziel-SG wird ein Socket gebraucht.

### 3.4 Funktionale Adressierung (0xDF)

- 0xDF = „Funktional UDS". 0xEF ist das KWP-Pendant (historisch). [DOK Q8]
- Im G31-Trace (über ENET) antworten auf `C3 DF F1 22 F1 90` über 20 SGs mit jeweils eigener Quelladresse (0x10, 0x22, 0x76, 0x18, 0x40, 0x29, 0x30, 0x67, …). Ebenso auf `22 37 FE`. [DOK Q3-Trace]
- Auf D-CAN geht der Request auf 0x6F1 mit Byte 0 = 0xDF. Jede Antwort kommt auf 0x600 + eigene Adresse. [WAHRSCHEINLICH: Firmware Q4 behandelt das Zielbyte generisch; ein expliziter D-CAN-Mitschnitt fehlt]
- Antwortet ein SG mehrteilig, muss der Tester **an jedes SG einzeln** Flow Control senden (Byte 0 = dessen Adresse). [WAHRSCHEINLICH, Logik in Q4]
- EdiabasLib ersetzt beim ELM327 funktionale Requests durch eine Schleife physikalischer Requests an alle Adressen der Gruppen-Tabelle (ELM327 kann nicht mehrere Antworten empfangen). [DOK Q3] Das ist für ein eigenes Tool eine robuste Alternative.

### 3.5 Sessions, Timing, Tester Present

- **Sessions** laut FEM_20-Tabelle `DIAGMODE` [DOK Q5]:

  | Wert | Session |
  |---|---|
  | 0x01 | DEFAULT |
  | 0x02 | ECUPM (Programming) |
  | 0x03 | ECUEXTDIAG (Extended) |
  | 0x04 | ECUSSDS (Safety System) |
  | 0x40 | ECUEOL |
  | **0x41** | **ECUCODE (Coding Session)** |
  | 0x42 | ECUSWT |
  | 0x43 | ECUHDD |
  | 0x4F | ECUDEVELOP |
  | 0x5F | ECUGDM (Garage Diagnose Mode) |

- **Für ein Read-only-Tool reicht die Default-Session.** Im G31-Trace werden alle Identifikations- und Codier-DIDs (22 3xxx) in der Default-Session gelesen. Ein `10 xx` vorher kommt nur vereinzelt vor (`10 01`, `10 03`, `10 42` an die DME). [DOK Q3-Trace]
- **Tester Present:** Job `DIAGNOSE_AUFRECHT` = `$3E TesterPresent $?0 suppressPosRspMsgIndication`, also `3E 00` oder `3E 80`. [DOK Q5] Die E-Sys-Klassen zeigen `TP "3E 00"`. [DOK Q25, schwach] In der Default-Session ist Tester Present nach ISO 14229 nicht nötig, denn S3 betrifft nur Nicht-Default-Sessions. [WAHRSCHEINLICH]
- **P2/P2\*:**
  - BMW-spezifische Werte stehen in den Kommunikationsparametern der SGBDs (EdiabasLib liest sie aus `INITIALISIERUNG` bzw. den Concepts 0x010F „BMW-FAST" und 0x0110 „D-CAN"). Sie sind in der öffentlichen Doku nicht enthalten. [DOK Q4-Code, Werte UNBEKANNT]
  - ISO-14229-2-Standardwerte: P2server = 50 ms, P2\*server = 5000 ms nach NRC 0x78. [WAHRSCHEINLICH, Norm nicht frei einsehbar]
  - EdiabasLib/ELM verwendet tool-seitig 2000 ms Datentimeout. [DOK Q3]
  - Empfehlung: P2-Client 1 s, nach NRC 0x78 auf 5–10 s verlängern. [WAHRSCHEINLICH]
- **Negativantwort:** `7F <SID> <NRC>`. Wichtige NRCs: 0x11, 0x12, 0x13, 0x22, **0x31 requestOutOfRange** (DID nicht vorhanden), 0x33, 0x78, 0x7E, 0x7F. [DOK Q26]

### 3.6 EDIABAS-„BMW-FAST"-Telegrammformat

Relevant beim Lesen von EdiabasLib-Logs und `.sim`-Dateien. [DOK Q3, Q4]

```
[0x80 | Len6] [Ziel] [Quelle] [UDS-Daten …] [Checksumme]
  Len6 = 0  → Länge im 4. Byte; ist dieses 0x00 → 2-Byte-Länge in Byte 4–5
  Funktionale Requests: oberste Bits 0xC0 (z. B. "C3 DF F1 22 F1 90")
```

Beispiele aus dem Trace:

- `83 01 F1 22 F1 50`: 3 Byte UDS an 0x01 von 0xF1
- `86 F1 01 62 F1 50 0F 20 40 8A`: Antwort, 0x8A = Checksumme

### 3.7 HSFZ über ENET (nur Dokumentation)

Quellen: EdiabasLib `EdInterfaceEnet.cs` [DOK Q27] und Q28 [DOK].

| Punkt | Wert |
|---|---|
| TCP-Port Diagnose | **6801** |
| UDP-Port Ident/Control | **6811**, Fahrzeugsuche per Broadcast |
| Ident-Request | `00 00 00 00 00 11` (Länge 0, Steuerwort 0x0011) |
| Header | 4 Byte Länge (Big Endian, zählt die Bytes **nach** dem 6-Byte-Header) + 2 Byte Steuerwort |
| Steuerworte | 0x0001 Diagnosedaten, 0x0002 Ack, 0x00FF Nack, 0x0011 Ident, 0x0012 Alive Check, 0x0013 Alive-Check-Antwort |
| Nutzdaten bei 0x0001 | `[Quelle][Ziel][UDS …]` |
| Tester-Adresse | **0xF4** (Ethernet-Tester); 0xF5 = „OBD Tester auf Ethernet" [DOK Q8] |
| Adressierung | 1 Byte, anders als DoIP mit 2 Byte |

Beispiel „VIN vom ZGW":

```
00 00 00 05 00 01 F4 10 22 F1 90
```

Das ZGW bestätigt zuerst mit Steuerwort 0x0002 (Echo der ersten Bytes) und schickt dann die Antwort mit 0x0001 und `10 F4 62 F1 90 …`. Auf Alive Check (0x12) antwortet der Tester mit `00 00 00 02 00 13 00 F4`. [DOK Q27]

Ob ENET am F20 vom 01/2012 funktioniert: BN2020 programmiert/codiert grundsätzlich über Ethernet [DOK Q15], und die FEM-SGBD hat OBD-Ethernet-Wecksignale [DOK Q5]. Dass der konkrete FEM-Hardwarestand das unterstützt, ist [WAHRSCHEINLICH].

---

## 4. BMW-UDS-Identifikationsdaten (read-only)

### 4.1 DID-Übersicht

Quellen:

- SGBD-Jobbeschreibungen FEM_20, REM_20, ENTRY, ZGW_01, MEVD1725 [DOK Q5–Q9]
- Reale Antworten aus dem G31-Trace [DOK Q3] (Byte-Layout real, Fahrzeug aber G-Serie)
- E-Sys-Klassennamen [DOK Q25, schwach]

| DID | Name (SGBD/E-Sys) | Antwort-Layout nach `62 <DID>` | Beleg |
|---|---|---|---|
| **F190** | VIN / FAHRGESTELLNUMMER_LANG | 17 Byte ASCII | [DOK Q5, Q8, Trace: „WBAJM71000B055940"] |
| **F150** | SGBD-Index (IDENT → `ID_SGBD_INDEX`) | **3 Byte**, z. B. `0F 20 40` (G31-ACSM) | [DOK Q5, Q10, Trace] |
| **F101** | SVK_AKTUELL | siehe 4.2 | [DOK Q5, Trace] |
| F102 / F103 / F104 … | SVK_SUPPLIER / SVK_WERK / SVK_BACKUP_01 … (F100 + SVK_ID) | wie F101 | [DOK Q5 Tabelle `SVK_ID`: 0x01 AKTUELL, 0x02 SUPPLIER, 0x03 WERK, 0x04 … BACKUP] |
| **F18A** | SystemSupplierIdentifier | 3 Byte Lieferantennummer (z. B. `00 00 96`) | [DOK Q5, Trace] |
| **F18B** | ECUManufacturingDate | 3 Byte **BCD YY MM DD** (z. B. `17 06 16` = 16.06.17) | [DOK Q5 „ID_DATUM DD.MM.YY", Trace] |
| **F18C** | ECUSerialNumber | ASCII, im Trace 10 Zeichen („0030039779") | [DOK Q5, Trace] |
| **F186** | ActiveDiagnosticSession | 1 Byte Session, optional 1 Byte Detail (Trace: `01` bzw. `01 81`) | [DOK Q5, Trace] |
| F100 | „ReadActiveSessionState" (E-Sys) | 4 Byte, Trace `01 81 00 01` | Name: [DOK Q25, schwach]; Bedeutung: [UNBEKANNT] |
| **100B** | I-Stufe (I-Level) | 3 × 8 Byte (siehe 4.4), am ZGW ggf. plus Signatur | [DOK Q8, Q6, Trace] |
| 1000 | Prüfstempel (TestStamp) | 3 Byte | [DOK Q5] |
| **37FE** | Codierprüfstempel (CPS) | bis SP2021: **VIN7** (7 ASCII), z. B. „B055940" | [DOK Q5, Trace] |
| **3F06** | VcmGetVehicleOrderReference (FA), nur am ZGW 0x10 | Länge, Version, komprimierter FA, Signatur (siehe 5.4) | [DOK Q8, Trace] |
| 3F07 | VcmGetEcuListAll (SVT-Soll) | Anzahl + Liste der Diagnoseadressen | [DOK Q8] |
| 3F08 / 3F0C / 3F0D | ActiveResponse / codierrelevante / flashfähige SGs | Liste | [DOK Q8] |
| 3F0E / 3F0F / 3F11 / 3F12 / 3F13 / 3F24 | SG-Listen K-CAN / Body-CAN / MOST / FA-CAN / FlexRay / Ethernet | Liste | [DOK Q8] |
| 3F1C / 3F1D | VCM_DID_FA1/FA2 im **REM** (FA-Backup, je 160 Byte Rohdaten) | Rohdaten | [DOK Q6] |
| **1700** | STATUS_MILEAGE am **FEM_BODY 0x40** (km redundant zum Kombi) | km, 0…16 777 214, 0xFFFFFF = ungültig. Byte-Breite (3 Byte?) | Inhalt: [DOK Q5]; Breite: [WAHRSCHEINLICH] |
| 1701 | Systemzeit am ZGW (STAT_SYSTEMZEIT_WERT) | 4 Byte (Trace `07 C2 75 1F`) | [DOK Q1, Trace] |
| 2000 | Infospeicher (sekundärer Fehlerspeicher), IS_LESEN | Liste n × (3 Byte Fehlerort + 1 Byte Status) | Job: [DOK Q5]; Layout: [WAHRSCHEINLICH aus Trace] |
| 2502 / 2503 / 2504 | Programmierzähler / max. Programmiervorgänge / Flash-Timing | – | [DOK Q5] |
| 100A / 100E | Energiesparmode / Betriebsmode | 1 Byte | [DOK Q5] |
| 1600 / 16xx | Anzahl / Seriennummern der LIN-Subbus-Sensoren | – | [DOK Q5] |
| 0xDAD6 / 0xDAD7 | Spannung Kl. 30L1 / 30L2 (FEM, REM) | Wert/10 = V | [DOK Q5, Q6] |
| 0xDAD1 / 0xDADB | Spannung Kl. 15 / Kl. 30F (REM) | V (1 Nachkommastelle) | [DOK Q6] |
| 0x460A | DME: UBATT momentan | `unsigned int × 0,015 V` | [DOK Q9] |
| 0x586A | DME: UBATT vom IBS | `× 0,00025 + 6,0 V` | [DOK Q9] |
| 0x58A1 | DME: Kilometerstand | unsigned long, 1 km | [DOK Q9] |
| 0xD670 | REM: km-Stand über Bus | unsigned long, km | [DOK Q6] |
| 0xD640 … 0xD64D, 0xD671 | REM: PDC-Status und -Abstände | Abstand 20–250 cm, 253 = kein Objekt | [DOK Q6] |
| KOMBI-km-DID | – | – | [UNBEKANNT]: Eine F20-KOMBI-SGBD wurde nicht gefunden |

Lesen ist pro Request mit **mehreren DIDs** möglich (`22 DID1 DID2 …`; die SGBD-Jobs `STATUS_LESEN` unterstützen „ein oder mehrere Stati"). [DOK Q5] Die SG-seitige Begrenzung ist [UNBEKANNT]. Empfehlung: ein DID pro Request.

### 4.2 SVK (22 F1 01): Aufbau und Dekodierung

SGBD-Ergebnisse von `SVK_LESEN` [DOK Q5]: PROG_TEST, ANZAHL_EINHEITEN, PROG_DATUM, PROG_KM (10-km-Inkremente, 10 … 655 350 km), PROZESSKLASSE, SGBM_IDENTIFIER, VERSION.

Bytelayout, abgeleitet aus 5 realen Antworten des Traces (alle Beispiele dekodieren konsistent):

```
62 F1 01
[0]      01        SVK-Version?                      [WAHRSCHEINLICH]
[1]      01        PROG_TEST (ProgDepsChecked)       [DOK Q5: 1 = IO, 2/3/4 = NIO]
[2..3]   00 09     ANZAHL_EINHEITEN (n)              [DOK Q5 + Trace]
[4..16]  13 Byte Kopfblock:
         [4..6]  18 01 30  PROG_DATUM, BCD YYMMDD (= 30.01.18)   [Position WAHRSCHEINLICH]
         [7]     8A        unbekannt (0x8A / 0x8B gesehen)       [UNBEKANNT]
         [8..9]  04 D2     PROG_KM / 10 (?) → 12 340 km          [WAHRSCHEINLICH]
         [10..16]          unbekannt (z. B. 01 00 00 10 00 00 00) [UNBEKANNT]
[17..]   n × 8 Byte:  [Prozessklasse][SGBM-ID 4 Byte][Haupt][Neben][Patch]  [DOK Trace + Q5]
```

Prozessklassen laut FEM_20-Tabelle `PROZESSKLASSEN` [DOK Q5]:

| Wert | Kürzel | Bedeutung |
|---|---|---|
| 0x01 | HWEL | Hardware Elektronik |
| 0x02 | HWAP | Hardwareausprägung |
| 0x03 | HWFR | Hardwarefarbe |
| 0x04 | GWTB | Gateway-Tabelle |
| **0x05** | **CAFD** | **Codierdaten** |
| 0x06 | BTLD | Bootloader |
| 0x07 | FLSL | Flashloader Slave |
| 0x08 | SWFL | Software |
| 0x09 | SWFF | Flash File Software |
| 0x0A | SWPF | Prüfsoftware |
| 0x0B | ONPS | Onboard-Programmiersystem |
| 0x0C | IBAD | Interaktive Betriebsanleitung Daten |
| 0x0D | SWFK | BEGU: Detaillierung auf SWE-Ebene |
| 0x0F | FAFP | FA2FP |
| 0x10 | FCFA | Freischaltcode Fahrzeugauftrag |
| 0x1A | TLRT | Temporäre Löschroutine |
| 0x1B | TPRG | Temporäre Programmierroutine |
| 0x1C | BLUP | Bootloader-Update |
| 0x1D | FLUP | Flashloader-Update |
| 0xA0 | ENTD | Entertainment-Daten |
| 0xA1 | NAVD | Navigationsdaten |
| 0xA2 | FCFN | Freischaltcode Funktion |
| 0xC0 | SWUP | Software-Update-Paket |
| 0xC1 | SWIP | Index Software-Update-Paket |
| 0x00 / 0xFF | – | ungültig |

Dekodierbeispiel (G31-ACSM, Adresse 0x01, echte Antwort) [DOK Q3-Trace]:

```
HWEL 00001B25 004.004.001   BTLD 00001B2E 004.029.000   SWFL 00001B2F 004.029.002
CAFD 00001B29 006.004.018   CAFD 00001B2A 005.009.010   CAFD 00001B2B 005.007.000
CAFD 00001B2C 002.010.013   CAFD 00001B2D 002.011.025   CAFD 00002ABF 004.000.027
```

Darstellung wie in E-Sys: `<KLASSE>_<SGBM-ID 8 hex>_<HHH>_<NNN>_<PPP>`, also Versionsbytes **dezimal** dreistellig. Ein SG kann mehrere CAFDs haben. Eine HWAP mit Version 255.255.255 kommt vor (DME, BDC). [DOK Trace]

### 4.3 SGBD-Index (22 F1 50) und die Werte 0F1820 / 0F1650

- Der Job `IDENT` liest `22 F1 50` und liefert `ID_SGBD_INDEX` („Index zur Erkennung der SG-Variante") sowie `ID_SG_ADR`. [DOK Q5]
- Die Gruppendatei (z. B. `g_zgw.grp`) ordnet „ADR XX (Hex)" + „INDEX XXXXXX (Hex)" einer Varianten-SGBD zu (Ergebnis `VARIANTE`). [DOK Q10b] Die Zuordnungstabelle ist in der öffentlichen Doku **nicht** enthalten („No tables found"). [DOK Q10b]
- Beispielwerte G31 (2017/18) [DOK Trace]:

  | SG | Index |
  |---|---|
  | ACSM 0x01 | 0F2040 |
  | ZGW 0x10 | 0F1310 |
  | DME 0x12 | 0F1FF0 |
  | DSC 0x29 | 0F2100 |
  | EPS 0x30 | 0F2020 |
  | BDC 0x40 | 0F2050 |
  | 0x56 | 0F2090 |
  | KAFAS 0x5D | 0F2160 |

- **0F1820 und 0F1650** (dezimal 989 216 bzw. 988 752) haben genau dieses Format: 3 Byte, führendes 0x0F, unteres Nibble 0. Es sind damit **sehr wahrscheinlich SGBD-Index-Werte**. [WAHRSCHEINLICH] Die konkrete Variante (z. B. „ENTRY", „FEM_20", „REM_20") ist **[UNBEKANNT]**; Websuche ohne Treffer. Auflösen lässt sich das nur mit:
  1. der Adresse, von der der Wert kam, und
  2. entweder BMW-Gruppendateien (Job `IDENTIFIKATION`) oder einer eigenen Referenztabelle, die man am Fahrzeug aufbaut.

### 4.4 I-Stufe (22 10 0B)

- Layout pro Eintrag (8 Byte): `4 Byte ASCII Baureihe | 1 Byte Jahr | 1 Byte Monat | 2 Byte laufende Nummer (Big Endian)`. Beispiel aus der SGBD: „F001-09-08-400". [DOK Q8]
- Die Antwort enthält drei Einträge: WERK, HO, HO_BACKUP. [DOK Q8, Q6]
- Am ZGW (G31) folgen danach `00 14` + 20 Byte **Signatur**. Beispiel: `53 31 35 41 11 0B 02 1C` = „S15A-17-11-540". [DOK Trace; der EdiabasLib-Job heißt `STATUS_I_STUFE_LESEN_MIT_SIGNATUR`, Q1]
- Beim F20 lautet die Baureihe vermutlich „F020", also etwa F020-12-03-5xx. [WAHRSCHEINLICH] EdiabasLib prüft mit der Regex `([A-Z0-9]{4}|[A-Z0-9]{3})-[0-9]{2}[-_](0[1-9]|1[0-2])[-_][0-9]{3}`. [DOK Q1]
- **Achtung, die Semantik ist widersprüchlich dokumentiert:**
  - ZGW_01: WERK = „Aktuelle IStufe", HO = „Letzte IStufe", HO_BACKUP = „IStufe der Auslieferung"
  - EdiabasLib: WERK = Ship (Auslieferung), HO = Current, HO_BACKUP = Backup

  Status: [UNBEKANNT]. Am Fahrzeug gegen E-Sys/ISTA-Anzeige prüfen.

### 4.5 Fehlerspeicher

- `FS_LESEN` = **`19 02 0C`** (reportDTCByStatusMask, Maske Bit 2 + 3 = pending + confirmed). [DOK Q5, Trace] Antwort: `59 02 <AvailabilityMask> { DTC_hi DTC_mid DTC_lo Status }*`. Ein leerer Speicher im Trace sieht so aus: `59 02 7F`. [DOK Trace]
- DTCs sind BMW-spezifische 3-Byte-„Fehlerorte" (z. B. FEM 0x804021). Das Statusbyte ist nach ISO 14229 bitcodiert. Bit-Bedeutungen in der SGBD: Bit 0 testFailed … Bit 3 confirmed … Bit 7 warningIndicatorRequested. [DOK Q5]
- `FS_LESEN_DETAIL` nutzt `19 04` (Snapshot), `19 06` (Extended Data) und `19 09` (Severity). [DOK Q5] Umweltbedingungen: 0x1700 KM_STAND (3 Byte), 0x1701 ABS_ZEIT (4 Byte). [DOK Q5, Q12]
- `19 0A` (reportSupportedDTC) ist ISO-Standard, aber in den BMW-Jobs nicht benutzt. Unterstützung: [UNBEKANNT]
- Infospeicher: `22 20 00`, Details `22 20 nn`. [DOK Q5]
- **Löschen** (`14 FF FF FF`, `31 01 0F 06`) ist nicht read-only und daher ausgeschlossen. [DOK Q5, Q25]

---

## 5. Codierdaten lesen, FA, I-Stufe (und zur Risikoabschätzung: Schreiben)

### 5.1 Codierdaten lesen

- Codierdaten liegen in DIDs im Bereich **0x3000–0x37FD**. Gelesen werden sie mit `22 3x xx` in der Default-Session, ohne Security Access. [DOK Trace: DeepOBD-Codierfunktion liest bei einem G31 z. B. FEM/BDC 0x40 von 3000 bis 3534, ACSM 3000–3424, KOMBI 3000–37F1]
- Welche Blöcke existieren, ist SG- und CAFD-spezifisch. Die CAFD-Datei (PSdZData) beschreibt Blöcke, Bits und Funktionsnamen. [WAHRSCHEINLICH]
- Ohne CAFD lassen sich die Rohblöcke als Backup sichern: Bereich scannen, NRC 0x31 bedeutet „nicht vorhanden". Interpretieren lassen sie sich ohne CAFD nicht. [WAHRSCHEINLICH]
- Antwortgrößen im Trace: ein Block bis ca. 130 Byte (z. B. KOMBI 3000: 0x83 Byte). [DOK Trace]

### 5.2 CPS (0x37FE)

- Bis SP2021: VIN7, 7 ASCII-Zeichen. [DOK Q5]
- Ab SP2021 zusätzlich Codierdatum (3 Byte), Tester-Nr. (3 Byte) und Lizenz-ID (5 Byte). [DOK Q5]
- Für einen F20 von 2012 ist also VIN7 zu erwarten. [WAHRSCHEINLICH]

### 5.3 CAFD-ID und -Version ermitteln

- Aus der SVK (22 F1 01) die Einträge mit Prozessklasse **0x05** nehmen: SGBM-ID plus drei Versionsbytes. [DOK Q5 + Trace]
- E-Sys wählt die passende CAFD aus PSdZData passend zur I-Stufe („Detect CAF for SWE" → „Select the CAFD matching your I-Level"). [DOK Q21-Snippet, schwach]

### 5.4 Fahrzeugauftrag (FA/VO)

- **Ort:** VCM im ZGW (0x10), DID **0x3F06** „VcmGetVehicleOrderReference". [DOK Q8; DeepOBD nutzt `G_ZGW STATUS_VCM_GET_FA`, Q1]
- **Backup:** im REM, 0x3F1C/0x3F1D. [DOK Q6] Außerdem gibt es einen CAS-Pfad `G_CAS STATUS_FAHRZEUGAUFTRAG`, beim F20 also FEM_BODY 0x40. [DOK Q1; dass FEM_20 das unterstützt: UNBEKANNT]
- **Struktur** laut SGBD-Ergebnissen [DOK Q8]:
  - STAT_FA_LAENGE
  - STAT_VERSION (bestimmt das De-/Komprimierungsverfahren)
  - ZEIT_KRITERIUM (Baustand)
  - BAUREIHE (Entwicklungsbaureihe, z. B. F020)
  - TYP_SCHLUESSEL
  - LACKCODE
  - POLSTERCODE
  - SALAPA (Sonderausstattungen)
  - E_WORTE
  - HO_WORTE
  - **SIGNATUR_LAENGE + SIGNATUR**
- **Trace-Beispiel:** `62 3F 06 00 7D 03 41 34 57 …` → Länge 0x007D, Version 0x03, dann komprimierte Daten. [DOK Trace] Das Kompressionsverfahren (6-Bit-Zeichen?) ist [UNBEKANNT]. EdiabasLib dekodiert es über den SGBD-Job `FA_STREAM2STRUCT`. [DOK Q1]
- Der FA ist **signiert**. Ein Tool darf ihn nie zurückschreiben. [DOK Q8]

### 5.5 I-Stufe / ZUSB

- I-Stufe: siehe 4.4. Schreib-Job `_STEUERN_ISTUFE` (2E 100B) existiert im REM. Für dieses Projekt ist er tabu. [DOK Q6]
- „ZUSB": In keiner der gesichteten Quellen gefunden. [UNBEKANNT]

### 5.6 Wie Codierung schreibt (nur zur Risikoabschätzung, wird nicht implementiert)

| Schritt | Dienst | Beleg |
|---|---|---|
| Coding-Session | `10 41` (DSC_CS) | [DOK Q5 DIAGMODE 0x41, Q25] |
| Security Access | `27 xx` (Seed/Key). Ob fürs Codieren pro SG nötig, ist offen | Existenz: [DOK Q25]; Notwendigkeit: [UNBEKANNT] |
| Codierung löschen | `31 01 0F 01` (RCS_EraseCoding) | [DOK Q25, schwach] |
| Codierblöcke schreiben | `2E 3x xx …` | [WAHRSCHEINLICH; E-Sys-Klasse `WDBI_CodingData`, Bytes nicht gezeigt, Q25] |
| CPS schreiben | `2E 37 FE` (VIN7) | [DOK Q25: Antwort `6E 37 FE`] |
| Fingerprint | `2E F1 5A` | [DOK Q25: `6E F1 5A`] |
| Reset | `11 01` | [DOK Q25] |

**Signatur:** FEM_20 kennt die Fehlerorte 0x804020 „Codierung: Fehler bei Codierung aufgetreten", **0x804021 „Codierung: Signatur für Daten ungültig"**, 0x804022 „Codierung passt nicht zum Fahrzeug" und 0x804023 „Unplausible Daten während Transaktion". Die HU-ENTRY-SGBD hat 0xB7F8AA „Codierung: Signatur für Daten ungültig". [DOK Q5, Q7] Daraus folgt:

- Auch 2012er-BN2020-SGs prüfen eine Signatur über die Codierdaten und vergleichen die VIN. [DOK]
- Wie die Signatur gebildet wird (NCD-Signatur, Schlüssel, ob offline berechenbar), ist **[UNBEKANNT]**.
- Drittanbieter-Apps codieren F-Serien ohne BMW-Backend, also ist sie für Pre-SP2021-SGs offenbar lokal erzeugbar. [WAHRSCHEINLICH] Erst ab SP2021 kommen Lizenz-ID und Tester-Nr. in den CPS. [DOK Q5]

**Risiko:** Falsche oder fehlende Signatur, Abbruch mitten in der Transaktion oder Unterspannung können dazu führen, dass ein SG „nicht codiert" ist. Beim FEM heißt das: Licht, ZV, Wegfahrsperre/Start. Community-Warnung: „Code Default Values" kann das Fahrzeug lahmlegen. [DOK Q22-Snippet, schwach]

**Konsequenz für das Tool:** Eine harte Allowlist nur für `22`, `19 02/04/06/09/0A`, `3E` und optional `10 01`. Hart sperren: `10 02/41/…`, `11`, `14`, `27`, `28`, `2E`, `2F`, `31`, `34–37`, `3D`, `85`, `86`.

---

## 6. CAFD_000000F9 und typische CAFD-IDs

- **Namensschema:** `cafd_<8-stellige SGBM-ID hex>.caf.<HHH>_<NNN>_<PPP>`. Forum-Erklärung: „iiiiiiii is the numeric id of the ECU to which this cafd file applies". [DOK Q19-Snippet, schwach] Das passt exakt zum SVK-Format in 4.2. [DOK]
- **000000F9:** Ein Such-Snippet („BMW CAFD ID Cheat Sheet", bimmerfest) ordnet cafd_000000f9 der Headunit **HU_CICHB** zu. Andere Threads nennen die Versionen 007_006_009, 007_001_105 und 007_006_006 im Zusammenhang mit Headunit-Codierfehlern. [DOK Q19, schwach; Thread selbst nicht abrufbar, HTTP 402]
  - Bewertung: Die Annahme „HU_ENTRY" ist **plausibel**, falls der Wert aus der SVK von Adresse 0x63 stammt. CIC, CIC-HB und ENTRY könnten sich eine HU-CAFD-Familie teilen. [WAHRSCHEINLICH]
  - Die sehr kleine SGBM-ID (0xF9 = 249) spricht für eine früh vergebene BN2020-ID; im G31-Trace liegen die IDs 2017/18 bei 0x17BC–0x46DA. [WAHRSCHEINLICH]
  - **Verifikation:** `22 F1 01` an 0x63 lesen. Steht dort `05 00 00 00 F9 07 07 01`, ist es bestätigt.
- **Version 007.007.001** = Haupt 7 / Neben 7 / Patch 1. Das Format ist belegt [DOK Q5, Trace]. Dass die Hauptversion das Datenlayout der CAFD kennzeichnet und zur SWFL passen muss, ist [WAHRSCHEINLICH]. Eine öffentliche Quelle für genau 007_007_001 gibt es nicht. [UNBEKANNT]
- **Typische CAFD-IDs** für F20-FEM_BODY, REM, KOMBI, ICM usw.: öffentlich nicht zuverlässig dokumentiert gefunden. [UNBEKANNT] Am Fahrzeug aus den SVKs auslesen.

---

## 7. Offene Fragen (am Fahrzeug verifizieren, alles rein lesend)

1. **Echte SG-Liste:**
   - `22 3F 07` an 0x10 (SVT-Soll)
   - zusätzlich Scan `22 F1 50` an allen Adressen aus 2.2/2.4
   - Klärt: ZBE vorhanden? IHKA (0x78) oder IHKR im FEM? EKPS (0x17)? COMBOX (0x61)?
2. **Bus-Zuordnung:** `22 3F 0E/0F/11/12/13/24` an 0x10. Klärt: MOST beim HU_ENTRY? Wo hängen KOMBI, ACSM, FZD, HU?
3. **SGBD-Indizes:** Werte pro Adresse sammeln. Herausfinden, von welcher Adresse 0F1820 und 0F1650 stammen.
4. **SVKs aller SGs:** Kopfblock-Bytes [7] und [10..16] deuten (Hypothesen: Programmiersystem bzw. Tester-Kennung). PROG_KM-Position bestätigen (Vergleich mit dem bekannten km-Stand).
5. **CAFD_000000F9 007.007.001** in der SVK von 0x63 bestätigen.
6. **I-Stufe** (100B) an 0x10 und 0x72 lesen:
   - Mit oder ohne Signatur?
   - Welche der drei Stufen ist Werk/aktuell/Backup? (siehe Widerspruch in 4.4)
7. **FA** (3F06) lesen. Kompressionsformat (Version-Byte) dekodieren bzw. mit E-Sys-FA vergleichen.
8. **D-CAN-Timing:**
   - P2 / NRC-0x78-Verhalten messen
   - Antworten SGs auch bei DLC < 8?
   - Welches Padding senden SGs?
   - Welche BS/STmin geben SGs in ihrem FC vor?
9. **Funktionale Adressierung** 0xDF auf D-CAN testen (nur `22 F1 90`) und Mehrfachantworten beobachten.
10. **km-Stand:**
    - Byte-Breite von 0x1700 am FEM_BODY
    - KOMBI-eigenen km-DID finden
    - Plausibilitätsvergleich mit DME 0x58A1 und REM 0xD670
11. **Spannung:** 0xDAD6 (FEM) und 0x460A (DME) gegen ein Multimeter prüfen.
12. Existieren alle in den neueren SGBD-Revisionen dokumentierten Jobs/DIDs auch in den SG-Softwareständen von 01/2012? (NRC 0x31 wäre ein harmloses Ergebnis.)
13. **ENET:** Unterstützt der FEM-Hardwarestand dieses Fahrzeugs OBD-Ethernet (Ident per UDP 6811)?
14. Bedeutung von „ZUSB" klären (keine Quelle gefunden).

---

## 8. Quellen

| Nr. | Quelle | URL |
|---|---|---|
| Q1 | EdiabasLib, `DetectVehicleBmwBase.cs` (VIN/FA/I-Stufen-Jobs, 0x1701, I-Stufen-Regex) | https://raw.githubusercontent.com/uholeschak/ediabaslib/master/EdiabasLib/BmwFileReader/DetectVehicleBmwBase.cs |
| Q2 | EdiabasLib, `VehicleSeries.zip` → `VehicleSeries.xml` (ISTA-abgeleitete SG-Listen pro Baureihe; F20: Sr=F20, MS=F020, BT=BN2020) | https://raw.githubusercontent.com/uholeschak/ediabaslib/master/EdiabasLib/BmwFileReader/VehicleSeries.zip |
| Q3 | EdiabasLib, `EdElmInterface.cs` (D-CAN: ATSH6F1, ATCF600/ATCM700, 0x600\|addr, Extended Address, FC, funktionale Adressen) | https://raw.githubusercontent.com/uholeschak/ediabaslib/master/EdiabasLib/EdiabasLib/EdElmInterface.cs |
| Q3-Trace | EdiabasLib/Deep OBD, G31-ENET-Simulationsdatei (reale Request/Response-Paare: F101, F150, F18x, 100B, 37FE, 3F06, 3xxx, 19 02 0C) | https://raw.githubusercontent.com/uholeschak/ediabaslib/master/BmwDeepObd/Xml/G31/enet.sim |
| Q4 | EdiabasLib, Adapter-Firmware `CanAdapterElm.X/main.c` (SF/FF/CF/FC, DLC 8, Padding 0x00, BS/STmin-Defaults) und `EdInterfaceObd.cs` (Concepts 0x010F/0x0110) | https://raw.githubusercontent.com/uholeschak/ediabaslib/master/EdiabasLib/CanAdapterElm/CanAdapterElm.X/main.c · https://raw.githubusercontent.com/uholeschak/ediabaslib/master/EdiabasLib/EdiabasLib/EdInterfaceObd.cs |
| Q5 | EdiabasX SGBD Reference: **FEM_20** (Front Electronic Module; IDENT/SVK/CPS/IS/DIAGMODE/PROZESSKLASSEN, 0x1700, DTC-Texte) | https://emdzej.github.io/ediabasx-docs-sgbd/sgbd/fem_20/ |
| Q6 | EdiabasX SGBD Reference: **REM_20** (PDC-DIDs, VCM-Backup 3F1C/3F1D, 100B, F190, Spannungen) | https://emdzej.github.io/ediabasx-docs-sgbd/sgbd/rem_20/ |
| Q7 | EdiabasX SGBD Reference: **ENTRY** (Entry HeadUnit; MOST-/Ethernet-Jobs, Codier-Signatur-DTC) | https://emdzej.github.io/ediabasx-docs-sgbd/sgbd/entry/ |
| Q8 | EdiabasX SGBD Reference: **ZGW_01** (VCM: 3F06/3F07/3F0x, 100B-Layout, TabDiagAdressen) | https://emdzej.github.io/ediabasx-docs-sgbd/sgbd/zgw_01/ |
| Q9 | EdiabasX SGBD Reference: **MEVD1725** („ME V17.25 4 Zylinder N13"; FlexRay/FA-CAN-DTCs, 0x460A, 0x586A, 0x58A1) | https://emdzej.github.io/ediabasx-docs-sgbd/sgbd/mevd1725/ |
| Q10 | EdiabasX SGBD Reference: **DSC_20** | https://emdzej.github.io/ediabasx-docs-sgbd/sgbd/dsc_20/ |
| Q10b | EdiabasX SGBD Reference: **G_ZGW** (Gruppendatei, IDENTIFIKATION: ADR + SGBD-Index → SGBD) | https://emdzej.github.io/ediabasx-docs-sgbd/sgbd/g_zgw/ |
| Q11 | EdiabasX SGBD Reference: **EPS_20** | https://emdzej.github.io/ediabasx-docs-sgbd/sgbd/eps_20/ |
| Q12 | EdiabasX SGBD Reference: **ICMQL** | https://emdzej.github.io/ediabasx-docs-sgbd/sgbd/icmql/ |
| Q13 | EdiabasX SGBD Reference: **IHKA20** | https://emdzej.github.io/ediabasx-docs-sgbd/sgbd/ihka20/ |
| Q14 | EdiabasX SGBD Reference: **ZBEL20** (ZBE low), **FZD_20** | https://emdzej.github.io/ediabasx-docs-sgbd/sgbd/zbel20/ · https://emdzej.github.io/ediabasx-docs-sgbd/sgbd/fzd_20/ |
| Q15 | BMW Technical Training ST1102 „Advanced Vehicle Diagnosis" (Bitraten K-CAN/K-CAN2/PT-CAN/PT-CAN2/D-CAN/FlexRay/Ethernet, Beispiele F30) | https://archive.org/download/BMWTechnicalTrainingDocuments/ST1102%20Advanced%20Vehicle%20Diagnosis/Advanced%20Vehicle%20Diagnosis.pdf |
| Q16 | „thesecretingredient" BMW F/G Enhanced PIDs (0x6F1/0x612, Extended Addressing, Beispiel-Frames, OBD über ZGM) | https://thesecretingredient.neocities.org/bmw |
| Q17 | BMW Technical Training F01 Bus Systems (ZGM, FlexRay, K-CAN2 500 kbit/s) | https://archive.org/download/BMWTechnicalTrainingDocuments/ST811%20F01%20Complete%20Vehicle/03.1_F01%20Bus%20Systems.pdf |
| Q18 | Bimmerscan: BMW Front Electronic Module (FEM) (ZGM im FEM, integrierte Funktionen, Busse, REM an K-CAN2) | https://bimmerscan.com/bmw-front-electronic-module-fem/ |
| Q19 | Bimmerfest „BMW CAFD ID Cheat Sheet" / „The secret life of cafd files" (nur als Such-Snippet; Abruf HTTP 402) | https://www.bimmerfest.com/threads/bmw-cafd-id-cheat-sheet.781953/ · https://www.bimmerfest.com/threads/the-secret-life-of-cafd-files.678682/ |
| Q20 | GitHub jokinawa/bmw-f (Community-SG-Liste mit Adressen, MY2016, unvollständig) | https://github.com/jokinawa/bmw-f |
| Q21 | Bimmerpost F30/F22-Threads zu HU_ENTRY / Combox (nur Such-Snippets; Abruf blockiert) | https://f30.bimmerpost.com/forums/showthread.php?p=23800116 |
| Q22 | Bimmerpost F20-Thread „HU_ENTRYNAV [63], ICM [1c], REM [72]" (nur Such-Snippet; Abruf blockiert) | https://f80.bimmerpost.com/forums/showthread.php?p=30789429 |
| Q23 | python-doipclient: Automotive Ethernet Primer (OBD-Ethernet-Pins Option 1: 3/11/12/13, Aktivierung Pin 8) | https://python-doipclient.readthedocs.io/en/latest/automotive_ethernet.html |
| Q24 | Wikipedia: ISO 15765-2 (Frame-Typen, FC, STmin, Extended Addressing) | https://en.wikipedia.org/wiki/ISO_15765-2 |
| Q25 | GitHub Gist brandonros „Extracted BMW F series ESYS commands" (10 41, 27, 31 01 0F 01, 6E 37 FE, 6E F1 5A …; schwacher Beleg) | https://gist.github.com/brandonros/3e4eb6b39d77e2e7469abdf44ab4c7f3 |
| Q26 | Wikipedia: Unified Diagnostic Services (SIDs, Negativantwort, NRCs) | https://en.wikipedia.org/wiki/Unified_Diagnostic_Services |
| Q27 | EdiabasLib, `EdInterfaceEnet.cs` (HSFZ: Ports 6801/6811, Header, Steuerworte, Tester 0xF4) | https://raw.githubusercontent.com/uholeschak/ediabaslib/master/EdiabasLib/EdiabasLib/EdInterfaceEnet.cs |
| Q28 | Quantex: ELM327 HSFZ (Port 6801, UDP-Discovery 6811, 6-Byte-Header, Tester F4) | https://quantexlab.com/en/develop/elm327_hsfz.html |

Nicht oder nur eingeschränkt nutzbar:

- Bimmerpost und Bimmerfest blockieren automatisierten Abruf (Cloudflare bzw. HTTP 402). Dort nur Such-Snippets verwendet.
- Das F30-GVE-Training-PDF (archive.org, ST1113) hat eine defekte Text-Codierung; es wurde nicht ausgewertet.
- Ein F20-spezifisches BMW-Trainingsdokument „Allgemeine Fahrzeugelektrik" wurde online nicht gefunden.
