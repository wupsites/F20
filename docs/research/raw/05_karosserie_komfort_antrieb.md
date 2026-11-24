# 05 – Karosserie, Komfort, Licht und (nur Doku) Fahrdynamik/Antrieb

**Fahrzeug:** BMW 116i F20, Bau 24.01.2012, N13 (136 PS), Schaltgetriebe, Halogen (angenommen), Nebelscheinwerfer, Regen-/Lichtsensor, Sichtpaket, PDC hinten, Sitzheizung vorn, MFL, Radio Professional (HU_ENTRY), Zulassung DE
**Werkzeug:** BimmerCode (Vollversion inkl. Expert Mode)
**Stand der Recherche:** 24.11.2026
**Maschinenlesbarer Katalog:** `05_karosserie_komfort_antrieb.json` (82 Einträge, gleiche IDs wie unten)

---

## 0. Evidenz-Tags und Methodik

| Tag | Bedeutung |
|---|---|
| **[DOK]** | In mindestens einer zitierten Quelle dokumentiert. **Nicht** an diesem Fahrzeug getestet. |
| **[WAHRSCHEINLICH]** | Aus Quellen ableitbar, aber für dieses Fahrzeug bzw. diese I-Stufe nicht direkt belegt. |
| **[EXPERIMENTELL]** | Nur eine Quelle, widersprüchliche Angaben oder Hinweise wie „Don't work“ / „TESTING“. |
| **[NICHT KOMPATIBEL]** | Hardware oder Steuergerät fehlt (bzw. sehr wahrscheinlich nicht vorhanden). |
| **[UNBEKANNT]** | Kein Parameter und keine belastbare Quelle gefunden. |

**Quellenlage:**
- **BimmerCode, offizielle Liste „BMW 1 Series F20, F21“** (https://bimmercode.app/cars/f20/): vollständig abgerufen. Sie nennt die Optionen des *Standardmodus* mit Klartextlabel, Werten und benötigtem Steuergerät, aber **keine** E-Sys-Parameternamen.
- **E-Sys-Cheat-Dateien (GitHub `packetpilot/bmw-f/cheats/*.xml`)**: über raw.githubusercontent.com vollständig geladen und maschinell ausgewertet. Besonders wertvoll ist `Botho.xml`, getaggt `series="F020,F030"`, mit Standardwerten. Weitere Dateien: `ekfxisid.xml` (F020/F030, koreanisch), `Bundang_Thunder.xml` (F20–F36), `Almaretto.xml`, `Kip_M3.xml` (F80/F82), `otakar.xml`, `packetpilot.xml`, `FDLCodes.xml`, `ruben_17non.xml`. Alle FEM-Einträge dort verwenden **CAFD-ID 00000794** (FEM_BODY).
- **Google-Sheets** „Coding BMW F3x“ (CSV-Export) und eine F87-Liste (CSV-Export): abgerufen.
- **UNECE-Regelung Nr. 48, Rev. 7 (2013)** als PDF (nsai.ie): abgerufen und zitiert.
- **Blockiert oder nur über Such-Snippets**: motor-talk.de (403), gesetze-im-internet.de (503), bimmerpost/f30post/1addicts (nicht abgerufen), Scribd/SlideShare (nicht lesbar), BMW-Presse-UK (Weiterleitung). Diese Quellen sind in der Quellenliste markiert.

**Grundsätzliches zur Codierung mit BimmerCode:**
- E-Sys nennt das Steuergerät **FEM_BODY**. BimmerCode zeigt es als „Front Electronic Module“ mit der Variante **FEM_01**. Beide Bezeichnungen stehen in den Cheat-Dateien für dieselbe CAFD (00000794). REM heißt in BimmerCode **REM_01**, das ICM **ICMQL**.
- **Standard vs. Expert:** Optionen aus der offiziellen F20-Liste sind „standard“. Parameter, die nur in E-Sys-Quellen vorkommen, lassen sich nur im **Expert Mode** ändern. Das BimmerCode-Handbuch warnt dazu: Expert Mode ist „intended for experienced users with specialized knowledge only“, es gibt keinen Support, und „Incorrect use … can cause serious issues“ (https://bimmercode.app/manual/).
- **Backups:** BimmerCode legt beim Auslesen automatisch Backups an. Diese gehen beim Löschen der App verloren, also vorher exportieren (Handbuch).
- **I-Stufe ist entscheidend:** Mehrere Quellen machen Funktionen von der I-Stufe abhängig. Beispiel: `BLINKZYKLEN_ANZAHL_TIPP` wirkt laut Botho.xml und Almaretto.xml nur *vor* Datenstand 3.61.x. Ein Fahrzeug von 01/2012 hat ohne Update vermutlich einen alten Stand. **Vor jeder Änderung den Ist-Wert auslesen.** Existiert ein Parameter nicht oder hat er andere Werte, nicht raten.

---

## 1. Kurzfazit – sinnvollste, belegte Optionen für dieses Fahrzeug

| # | Funktion | ECU / Parameter | Modus | Tag |
|---|---|---|---|---|
| 1 | Komfortblinker 3 → 5 | FEM_BODY 3060 `BLINKZYKLEN_ANZAHL_TIPP` = 04 | Expert | [DOK], I-Stufe beachten |
| 2 | Komfortöffnen/-schließen per Funkschlüssel | FEM_BODY 3053 `KOMFORTOEFFNUNG_FB`, `KOMFORTSCHLIESSUNG_FB` | Standard | [DOK] |
| 3 | Auto Start-Stop merken / standardmäßig aus | FEM_BODY 3023 `TCM_MSA_MEMORY` bzw. `TCM_MSA_DEFAULT_OFF` | Standard | [DOK], rechtliche Grauzone |
| 4 | Welcome Light (Dauer, Nebelscheinwerfer, Komponenten) | FEM_BODY 3060 `WL_TIMEOUT`, 3063 `MAPPING_NEBELSCHW_*_PART_OF_WL` | Standard | [DOK] |
| 5 | Heimleuchten-Dauer | FEM_BODY 3064 `PIA_DEFAULT_FMH` | Expert | [DOK] |
| 6 | Fensterheber bei offener Tür | FEM_BODY 3050 `FH_TUERAUF_STOP_MAUT` | Standard | [DOK] |
| 7 | Entriegeln bei Motor-Aus (nach Auto-Lock) | FEM_BODY 3040 `CLM_UNLOCK_KL15OFF_AFTER_PIA_AUTO_LOCK` | Standard | [DOK] |
| 8 | Blinkquittierung Ver-/Entriegeln | FEM_BODY 3060 `QUITTBLK_SICHERN_ANZAHL` / `QUITTBLK_ENTSCHAERFEN_ANZAHL` | Standard | [DOK] |
| 9 | Sitzheizungs-Temperaturstufen | FEM_01 (nur BimmerCode-Label) | Standard | [DOK] |
| 10 | Rückleuchten mit TFL | REM 3062 `MAPPING_TAGFAHRL_H*_OUTPUT` | Standard | [DOK], rechtlich [UNBEKANNT] |
| 11 | Nachwischzyklen, Heckwischer bei R | FEM_BODY 3080 `WW_ANZAHL_NACHWISCHZ_*`, `WW_HECKWISCHER_EIN_RUECKWGANG` | Standard | [DOK] |
| 12 | Radio aus bei Fahrertür | FEM_BODY 3020 `TCM_LOGIC_R_OFF_DOOR` | Standard | [DOK] |
| 13 | Lichtsensor-Empfindlichkeit | FEM_BODY 3130 `RLS_DEF_FLC_SCHWELLWERT_SATZ` | Standard | [DOK] |
| 14 | PDC beim Zurückrollen | REM_01 (nur BimmerCode-Label) | Standard | [DOK] |

Die Klimaoptionen (Speicher A/C/Umluft, A/C nicht mit AUTO) funktionieren **nur mit Klimaautomatik (IHKA)**. Ob der Wagen IHKA oder IHKR hat, ist offen.

---

## 2. A – Beleuchtung (FEM_BODY, REM)

> Wertangaben wie „14 (hex)“ sind Hex-Werte aus E-Sys-Cheats. In BimmerCode-Standard erscheinen dieselben Optionen als Klartextauswahl.

### 2.1 Welcome Light, Coming/Leaving Home, Innenlicht

| ID | Funktion | Block / Parameter | Werte (Quelle) | BimmerCode-Label | Tag / Kompatibilität |
|---|---|---|---|---|---|
| fem_body.welcome_light_activation | Aktivierung je Lichtschalterstellung | – (nur BimmerCode) | Light switch on auto / auto or 2 / Not active | Welcome Light activation | [DOK] – wahrscheinlich |
| fem_body.welcome_light_duration | Leuchtdauer | 3060 `WL_TIMEOUT` | Std. 14h = 20 s; 3C = 60 s (Botho) | Welcome Light lighting duration (5–60 s) | [DOK] – wahrscheinlich |
| fem_body.welcome_light_darkness_only | Nur bei Dunkelheit | – | Active / Not active | Welcome Light in darkness only | [DOK] |
| fem_body.welcome_light_brightness | Helligkeit | 3070 `WL_HELLIGKEIT` | Std. 64h; 32h = 50 % | Welcome Lights brightness (laut BimmerCode nur Halogen/Xenon) | [DOK] |
| fem_body.welcome_light_fog | Nebelscheinwerfer im Welcome Light | 3063 `MAPPING_NEBELSCHW_L_PART_OF_WL`, `MAPPING_NEBELSCHW_R_PART_OF_WL` | nicht_aktiv → soft_On / hard_On | Welcome Lights fog lights | [DOK], 6 Quellen |
| fem_body.welcome_light_components | Abblend-/Fernlicht, Standlicht, TFL, Blinker, Abbiegelicht, Sidemarker im Welcome Light | E-Sys-Namen nicht belegt | Hard on / Soft on / Not active | Welcome Lights low beam / high beam 1/2 / parking lights / … | [DOK] (nur BimmerCode) |
| fem_body.coming_home_duration | Heimleuchten-Standarddauer | 3064 `PIA_DEFAULT_FMH` | Std. 14h = 20 s; 1E = 30 s | – (Expert) | [DOK] (1 Quelle) |
| fem_body.follow_me_home_remote | Heimleuchten per Funkschlüssel | 3060 `FOLLOWMEHOME_VIA_FFB`, 30D0 `RC_DEFAULT_IDG_3RD_BUTTON_SHORT` | aktiv; 3rd button short = 04 | – | [EXPERIMENTELL]: Botho koppelt das an Panic-Alarm/4-Tasten-Schlüssel |
| fem_body.interior_light_duration | Innenlicht-Nachleuchtdauer ver-/entriegeln | 3070 `IB_EINSCHALT_BEGR_LOK` (Std. 08), `IB_EINSCHALT_BEGR_ULOK` (Std. 14h) | z. B. 14h / 3C | – (Expert) | [DOK] |
| fem_body.ambient_light_decoupling | Ambientelicht-Helligkeit/-Entkopplung/Welcome | 3070 `AMBIENTE_NACHFUEHRUNG`, `AMBIENTE_HELLIGKEIT`, `WELCOME_AMBIENTE` | aktiv / nicht_aktiv | Ambient lighting brightness (decoupling …) | [NICHT KOMPATIBEL] ohne Ambientelicht |
| fem_body.door_handle_light_reverse | Türgriff-LEDs beim Rückwärtsgang | 3070 `OVT_BEI_RUECKFAHRLICHT` | nicht_aktiv → aktiv | Door handle lights when reverse gear is engaged | [NICHT KOMPATIBEL] ohne Türgriffbeleuchtung |
| fem_body.soft_on_off_main_lights | Soft-On/Off für Fahrlicht | **kein Parameter gefunden** | – | – | [UNBEKANNT] |

**Leaving Home:** Beim F-Modell entspricht das dem Welcome Light beim Entriegeln (siehe oben). Ein eigener „Leaving-Home“-Parameter wurde nicht gefunden.

### 2.2 Tagfahrlicht (TFL) und Standlicht

| ID | Funktion | Block / Parameter | Werte | BimmerCode-Label | Tag |
|---|---|---|---|---|---|
| fem_body.drl_mode | TFL-Modus | 3060 `TFL_MODUS` | Botho: Std. 02; Almaretto/Kip/FDL: `TFL_S` (TFL inkl. Rückleuchten) | Daytime running light mode (Active / Active also with parking lights / Not active) | [DOK], Werte uneinheitlich |
| fem_body.drl_brightness | TFL-Helligkeit | 3062 `MAPPING_TAGFAHRL_V_L_PWM_LEVEL_1`, `…_V_R_…` | Std. 64h (100 %), 32h (50 %) | Daytime running light brightness | [DOK] |
| rem.drl_tail_lights | Rückleuchten mit TFL | REM 3062 `MAPPING_TAGFAHRL_H_L_OUTPUT`/`_H_R_` (sl_l/sl_r = 14h/15h, außen), `MAPPING_TAGFAHRL_H2_L_OUTPUT`/`_H2_R_` (sl_2_l/sl_2_r = 16h/17h, innen) | Std. 00/off | Daytime running light tail lights outer/inner part | [DOK] |
| fem_body.parking_light_brightness | Standlicht-Helligkeit | 3062 `MAPPING_STANDL_V_L_PWM_LEVEL_STANDARD`, `…_V_R_…` | Std. 8; 32h / 64h | Angel Eyes brightness low beam / parking lights | [DOK], bei Halogen [UNBEKANNT] |
| hu_entry.drl_menu | TFL-Schalter im iDrive | nur HU_CIC `Daydriving_light` (Perm_off → standard), BimmerCode nur HU_NBT/NBT_EVO | – | Checkbox daytime running light | **[UNBEKANNT]** für HU_ENTRY: BimmerCode-Standardoption nur für HU_NBT/NBT_EVO, kein HU_ENTRY-Parameter belegt → wahrscheinlich nicht verfügbar (vgl. Katalog 04) |

Das Spreadsheet „Coding BMW F3x“ nennt für die Rückleuchten mit TFL zusätzlich `MAPPING_UNIVERSAL_6_OUTPUT`/`_7_OUTPUT` (REM 3063) samt `…_PWM_LEVEL_1`. Je nach REM-Stand weicht die Belegung also ab.

### 2.3 Nebelscheinwerfer, Abbiegelicht, US-Funktionen

| ID | Funktion | Block / Parameter | Werte | BimmerCode-Label | Tag / Recht |
|---|---|---|---|---|---|
| fem_body.cornering_light_via_fog | Abbiegelicht über NSW | 3073 `C_CLC_ENA`, `C_BLC_ENA`; 3066 `KL_ENABLE_LI`, `KL_ENABLE_RE`; 3062 `MAPPING_ABBIEGEL_L_OUTPUT`, `MAPPING_ABBIEGEL_R_OUTPUT` | F020_enable/01, KL_Ein, nsw_l/nsw_r (0B/0C); Deaktivieren: F020_disable, KL_Aus, off | Cornering lights activation / deactivation (laut BimmerCode NSW nötig) | [DOK]; Botho nennt „F020_enable“ als Standard, d. h. evtl. schon ab Werk aktiv. **Recht: Grauzone** |
| fem_body.cornering_fog_reverse | NSW-Abbiegelicht beim Rückwärtsgang | 3073 `C_CLC_REV_ALWAYS_ON`, `C_CLC_REV_CURV_BOTH_ON` | Std. 01 | – | [DOK] (1 Quelle) |
| fem_body.fog_off_with_high_beam | NSW aus bei Fernlicht | 3060 `NSW_AUS_BEI_FL` | Botho: Std. 00 = bleiben an; packetpilot (US): „Disable Hi-Beam Override“ = 00 | Fog lights off with high beam | [DOK]; EU-Standard vermutlich „bleiben an“ [WAHRSCHEINLICH] |
| fem_body.fog_with_parking_lights | NSW schon mit Standlicht | 3060 `NSW_EIN_AUF_LDS_STL` | 00 → 01 | Fog lights with parking lights | [DOK]; **Recht: siehe Abschnitt 5** |
| fem_body.us_sidemarkers | Blinker als Dauer-Sidemarker | 3063 `MAPPING_SIDEMARKER_L_OUTPUT`/`_R_` (off → fra_v_l/fra_v_r), `MAPPING_SIDEMARKER_*_FUNCTION` (01 → 04), `MAPPING_SIDEMARKER_L_PWM_LEVEL_STANDARD` | – | US sidemarkers / brightness / light function | [DOK]; **in DE unzulässig** |
| – | TFL über Nebelscheinwerfer | **kein F20-Parameter gefunden** | – | – | [UNBEKANNT]; zudem nach § 17 Abs. 3 StVO unzulässig (siehe 5) |

### 2.4 Blinker, Quittierung, Bremskraftanzeige / Notbremssignal

| ID | Funktion | Block / Parameter | Werte | BimmerCode-Label | Tag |
|---|---|---|---|---|---|
| fem_body.comfort_turn_signal_count | Komfortblinker-Zyklen | 3060 `BLINKZYKLEN_ANZAHL_TIPP` | 02 = 3× (Spreadsheet; Botho nennt Std. 00), **04 = 5×** (Wert = Anzahl − 1) | – (Expert) | [DOK], 6 Quellen; laut Botho/Almaretto nur vor Datenstand 3.61.x |
| fem_body.comfort_turn_signal_default | Profil-Vorgabe 1×/3×/5× | 3064 `PIA_DEFAULT_TIPPBLINKEN` | 00 = 1, 01 = 3 (Std.), 02 = 5 | – | [EXPERIMENTELL] (Botho: „Don't work“) |
| fem_body.lock_unlock_flash_count | Blinken beim Ver-/Entriegeln | 3060 `QUITTBLK_SICHERN_ANZAHL` (Std. 01), `QUITTBLK_ENTSCHAERFEN_ANZAHL` (Std. 02) | 1/2/3/Off | Turn signals flashing on locking / unlocking | [DOK] |
| fem_body.tailgate_open_flash | Blinken beim Öffnen der Heckklappe | 3060 `HECKKLAPPE_REVERSIEREN_BLINKEN` | 01 (doppelt) → 00 (einfach) | – | [DOK] (1 Quelle) |
| fem_body.ess_type | Art der Bremskraftanzeige | 3060 `ESS_AKTIVIERBARER_AUSGANG` | `bremslicht_blinkend` (Std. laut Botho) / `flachenvergroesserung` (F87-Liste) | Brake Force Display type (Area enlargement / Flashing / Not active) | [DOK] – **sicherheitskritisch** |
| fem_body.ess_activation_speed | Aktivierungsgeschwindigkeit | 3060 `ESS_AKTIVIERUNG_GESCHW` | Std. 32h = 50 km/h | Brake Force Display activation speed | [DOK] – **R48-widrig, wenn < 50 km/h** |
| fem_body.ess_activation_decel | Verzögerungsschwelle | 3060 `ESS_AKTIVIERUNG_REALE_VERZ`, `ESS_DEAKTIVIERUNG_REALE_VERZ` | Std. 0Eh ≈ 7 m/s² | Brake Force Display activation brake force | [DOK] – nicht ändern |
| rem.ess_lights_mapping | Leuchtenzuordnung | REM 3062 `MAPPING_BRAKEFORCED_L_OUTPUT`/`_R_` | bl_l / bl_r | Brake Force Display lights | [DOK] |
| rem.ess_flash_frequency | Blinkfrequenz | REM 3064 `ESS_BLINKFREQ_1`, `ESS_BLINKFREQ_2` | Std. 03 → 05 | Brake Force Display flashing frequency (3×/5× pro s) | [DOK] – **R48: max. 5 Hz, bei Glühlampen max. 4 Hz** |
| fem_body.hazard_after_emergency_braking | Warnblinker nach Notbremsung | 3060 `WB_GB_ENABLE`, `WB_GB_GEFAHRENWERT_MIN` | aktiv / nicht_aktiv | Hazard warning signal after emergency braking | [DOK]; R48 6.6.7.2 erlaubt es |

### 2.5 Lampenüberwachung (LED-Nachrüstung) – nur Dokumentation

| ID | Bereich | Block / Parameter | Werte | Tag |
|---|---|---|---|---|
| fem_body.lamp_monitoring_front | Blinker vorn, NSW | FEM 3061 `FRA_V_L/R_KALTUEBERWACHUNG`, `FRA_V_L/R_WARMUEBERWACHUNG`, `FRA_V_L/R_IS_LED`, `NSW_L/R_KALTUEBERWACHUNG`, `NSW_L/R_WARMUEBERWACHUNG`, `NSW_L/R_IS_LED` | aktiv → nicht_aktiv bzw. IS_LED → aktiv | [DOK] |
| rem.lamp_monitoring_rear | Blinker hinten, Brems-, Rückfahr-, Nebelschlussleuchte | REM 3061 `FRA_H_L/R_*`, `BL_L/R_*`, `RFS_L/R_*` (dazu NSL_* in ekfxisid) | wie oben | [DOK] |

BimmerCode fasst das als „LED conversion …“ zusammen (Abblend-/Fernlicht, Positionslicht, TFL, Kennzeichenlicht u. a.). Diese Optionen haben nur den Wert „Active“, Rücknahme also nur über ein Backup. **Für das Fahrzeug ohne LED-Umbau gibt es keinen Bedarf.**

### 2.6 Lichtautomatik

| ID | Funktion | Block / Parameter | Werte | BimmerCode-Label | Tag |
|---|---|---|---|---|---|
| fem_body.rls_sensitivity | Empfindlichkeit Regen-/Lichtsensor | 3130 `RLS_DEF_FLC_SCHWELLWERT_SATZ` | Botho: Std. 00, 03 = weniger empfindlich; Almaretto/Kip: `unempfindlich`; otakar: 02 = „highest sensitivity“ (widersprüchlich) | Rain-light-sensor sensitivity (Insensitive / Normal / Sensitive / Very sensitive) | [DOK]; wegen widersprüchlicher Hex-Werte **BimmerCode-Standardmodus verwenden** |

---

## 3. B – Komfort (FEM_BODY, REM, FZD, IHKA, PDC, ACSM)

### 3.1 Fenster, Spiegel, Komfortfunktionen per Schlüssel

| ID | Funktion | Block / Parameter | Werte | BimmerCode-Label | Tag / Kompatibilität |
|---|---|---|---|---|---|
| fem_body.comfort_open_remote | Komfortöffnen per Funkschlüssel | 3053 `KOMFORTOEFFNUNG_FB` (+ `KOMFORTOEFFNUNG`) | aktiv | Convenient opening / … with remote control | [DOK] – wahrscheinlich (in DE evtl. schon aktiv) |
| fem_body.comfort_close_remote | Komfortschließen per Funkschlüssel | 3053 `KOMFORTSCHLIESSUNG_FB` (+ `KOMFORTSCHLIESSUNG`) | aktiv | Convenient closing / … with remote control | [DOK] – wahrscheinlich |
| fem_body.comfort_open_close_delay | Haltezeit | 3053 `KOMFORT_OEFFNEN` (Std. 19h = 2,5 s), `KOMFORT_SCHLIESSEN` (Std. 0Fh = 1,5 s) | z. B. 14h / 0Ah / 00 | Convenient opening delay / closing delay | [DOK] |
| fem_body.mirror_fold_comfort | Spiegel an-/ausklappen beim Komfortschließen | 3110 `ASP_BEIKLAPPEN`, `ASP_BEIKLAPPEN_BEI_KOMFORTSCHLIESSEN`, `ASP_AUSKLAPPEN_NACH_KOMFORTSCHLIESSEN` | aktiv | Fold mirrors with convenient closing / Unfold … / Fold/unfold mirrors automatically | **[NICHT KOMPATIBEL]** ohne elektrische Anklappspiegel |
| fem_body.mirror_fold_speed | Geschwindigkeitsschwellen | 3110 `ASP_MAX_GESCHWINDIGKEIT_BEIKLAPPEN` (Std. 14h = 20 km/h), `ASP_GESCHWINDIGKEIT_AUTO_AUSKLAPPEN` (Std. 28h = 40 km/h) | – | Mirror folding / unfolding speed threshold | hardwareabhängig |
| fem_body.mirror_tilt_reverse | Bordsteinautomatik | 3110 `ASP_BORDSTEINAUTOMATIK_DELTA` (Std. 3Bh) | – | Automatic mirror tilt (+ value) | hardwareabhängig (BimmerCode: Anklappspiegel; Spreadsheet: Spiegel-Memory) |
| fem_body.window_door_open_front | Fensterheber bei offener Tür (vorn) | FEM 3050 `FH_TUERAUF_STOP_MAUT` | aktiv → nicht_aktiv | Window lifter interruption when opening a door | [DOK] |
| rem.window_door_open_rear | dto. hinten | REM 3050 `FH_TUERAUF_STOP_MAUT` | aktiv → nicht_aktiv | – | [DOK], nur 5-Türer |

### 3.2 Verriegelung, Heckklappe, Quittierung

| ID | Funktion | Block / Parameter | Werte | BimmerCode-Label | Tag |
|---|---|---|---|---|---|
| fem_body.auto_lock_speed | Schwelle „Verriegeln nach Losfahren“ | 3040 `CLM_SPEED_LIMIT_PIA_AUTO_LOCK` | Botho: Std. wert_04 (~16 km/h), wert_03 (~8 km/h); ekfxisid/otakar: 0Ah = 10 km/h | – (Expert) | [DOK]; Wertdarstellung je CAFD verschieden |
| fem_body.unlock_on_ignition_off | Entriegeln bei Motor-Aus | 3040 `CLM_UNLOCK_KL15OFF_AFTER_PIA_AUTO_LOCK` | Std. aktiv | Unlock doors automatically | [DOK] – wirkt nur mit Auto-Lock |
| fem_body.relock_timeout | Wiederverriegelung ohne Türöffnen | 3040 `CLM_TIME_PIA_LOCK_AT_TIMEOUT` | Std. 0Ch = 120 s (Einheit 10 s) | Time until automatic lock (10 s – 10 min) | [DOK] |
| fem_body.horn_lock_engine_running | Hupe beim Verriegeln mit laufendem Motor | 3040 `CLM_HORN_AT_SECURE` | Std. aktiv | Horn signal when locking the car with engine running | [DOK] |
| fem_body.bootlid_delay | Heckklappe per Funk: Verzögerung | 3040 `CLM_TIME_DELAY_BOOTLID` (Std. wert_02), 30D0 `RC_TIME_DELAY_BOOTLID` (Std. 05) | – | Boot lid opening delay | [DOK]; welcher Parameter dem Label entspricht, ist unklar |
| fzd.acoustic_lock_confirmation | Akustische Quittierung | FZD__07 3002 `Akustische Quittierung Schaerfen` (Std. 00), 3001 `Buzzer duration`/`Buzzer level high/low`/`Buzzer frequency` | – | Acoustical lock/unlock confirmation, Confirmation sound … | **[NICHT KOMPATIBEL]** ohne Alarmanlage (BimmerCode: „car has to be equipped with an alarm system“) |

**Nicht anwendbar bzw. [UNBEKANNT]:**
- *Entriegeln beim Schlüsselabziehen:* Der F20 hat einen Start-Stopp-Knopf ohne Schlüsselschacht, die Funktion entfällt.
- *Selektive Entriegelung* (nur Fahrertür): Kein Codierparameter gefunden. Bei F-Modellen ist sie meist eine Fahrzeugeinstellung im Menü, für HU_ENTRY nicht verifiziert ([UNBEKANNT]).
- *Heckklappe per Schlüssel schließen (HKFM):* Erfordert eine elektrische Heckklappe (HKFM/HKFM2), die der F20 nicht hat → [NICHT KOMPATIBEL].

### 3.3 Auto Start-Stop (MSA), Klemmenlogik, Startsperre

| ID | Funktion | Block / Parameter | Werte | BimmerCode-Label | Tag |
|---|---|---|---|---|---|
| fem_body.msa_memory | MSA-Zustand merken | FEM 3023 `TCM_MSA_MEMORY` | Std. nicht_aktiv → aktiv | Auto Start Stop function memory | [DOK], 7 Quellen |
| fem_body.msa_default_off | MSA standardmäßig aus | FEM 3023 `TCM_MSA_DEFAULT_OFF` | nicht_aktiv → aktiv | Auto Start Stop function off by default | [DOK] |
| fem_body.msa_eco_pro | MSA in ECO PRO automatisch an | FEM 3023 `TCM_MSA_ECO_MODE` | Std. aktiv | Auto Start Stop function in ECO mode | [DOK] |
| fem_body.radio_off_driver_door | Infotainment aus bei Fahrertür | FEM 3020 `TCM_LOGIC_R_OFF_DOOR` | Std. nicht_aktiv | Shut off iDrive system when driver door is opened | [DOK]; FEM-Logik, gilt auch mit HU_ENTRY [WAHRSCHEINLICH] |
| fem_body.start_without_clutch | Start ohne Kupplung | FEM 3020 `TCM_STARTLOCK_CLUTCH` | → 00 | – | [DOK] – **sicherheitskritisch, nicht codieren** |

Laut BimmerCode wird MSA im ECO-PRO-Modus trotz „Memory“ bzw. „off by default“ wieder aktiviert. Beim F20 liegt die MSA-Logik laut allen F20/F30-Quellen im **FEM** (3023). Die oft zitierte DME-Variante (`TCM_MSA_MEMORY` in DME_BAC2) gilt nur für G-Baureihen, siehe Abschnitt 4. Das Spreadsheet „Coding BMW F3x“ führt `TCM_MSA_MEMORY` mit „aktiv → nicht aktiv“, das widerspricht allen anderen Quellen (vermutlich vertauscht).

### 3.4 Sitzheizung, Klima

| ID | Funktion | ECU / Parameter | Werte | BimmerCode-Label | Tag / Kompatibilität |
|---|---|---|---|---|---|
| fem_body.seat_heating_temperatures | Temperatur der Stufen 1–3 (Sitz/Lehne vorn) | FEM_01, E-Sys-Name nicht belegt | Sitz 30–34 / 35–40 / 41–46 °C; Lehne 30–35 / 36–41 / 42–47 °C | Front seats / Front backrests temperature level 1–3 | [DOK] – wahrscheinlich |
| cfas.seat_heating_memory | Sitzheizung speichern | CFAS_PLX_1 / CBFS_PLX_1 | 15 min / 24 h / Do not save / Unlimited | Seat heating/cooling setting memory | **[NICHT KOMPATIBEL]** ohne Sitzmodul (elektrische Memory-Sitze); für die FEM-gesteuerte Sitzheizung ist kein Speicher dokumentiert |
| ihka.ac_on_with_auto | A/C nicht automatisch mit AUTO | IHKA 3002 `AC_NICHT_EIN_BEI_AUTO` (ekfxisid, F020/F030) bzw. IHKA_VA02 3003 `AC_ON_WITH_AUTO` (Botho) | Aktiv bzw. aktiv → nicht_aktiv | Air Conditioning on in AUTO mode | [DOK]; **nur IHKA** |
| ihka.ac_memory | A/C-Zustand speichern | 3002/3003 `MEMORY_OFF` (bzw. `OFF_MEMORY` bei IHKA_CBF) | aktiv | Air Conditioning setting memory | [DOK]; nur IHKA |
| ihka.recirc_memory | Umluft speichern | 3002/3003 `MEMORY_UMLUFT` | Std. nicht_aktiv → aktiv | Air circulation setting memory | [DOK]; nur IHKA |
| ihka.auto_recirculation | AUC / Umluft-Automatik | IHKA_VA02 3003 `UMLUFT_AUTO_AUS`, `AC_ON_WITH_RECIRC` | – | Automatic Air Recirculation (nur IHKA_VA02) | [DOK]; Bedeutung knapp beschrieben |
| ihkr.no_documented_options | Manuelle Klimaanlage | – | – | – | [UNBEKANNT]: BimmerCode listet Klimaoptionen nur für IHKA_CBF/VA01/VA02 |

### 3.5 Wischer

| ID | Funktion | Block / Parameter | Werte | BimmerCode-Label | Tag |
|---|---|---|---|---|---|
| fem_body.wipe_after_wash | Nachwischzyklen vorn/hinten | 3080 `WW_ANZAHL_NACHWISCHZ_FRONT` (Std. 03), `WW_ANZAHL_NACHWISCHZ_HECK` (Std. 02) | 01–05 | Wipe cycles after front / rear washing | [DOK] |
| fem_body.rear_wiper_reverse | Heckwischer bei R | 3080 `WW_HECKWISCHER_EIN_RUECKWGANG` | Std. aktiv | Automatic rear wiper in reverse | [DOK] |
| fem_body.wiper_level_switch_back | Wischerstufe im Stand zurückschalten | nur BimmerCode | Active / Not active | Wiper level switch back when stationary | [DOK] |
| fem_body.headlight_washer | Scheinwerferreinigung | 3080 `WW_SCHEINWERFERREINIGUNG`, `WW_ANZAHL_SPRITZIMPULSE_SRA`, `WW_SRA_SPERRZEIT`, `WW_ANZAHL_WASCHBET_ZUR_SRA` | – | Headlight washers … | **[NICHT KOMPATIBEL]** ohne SRA (bei Halogen üblicherweise nicht verbaut) |

Die **Wischer-Serviceposition** ist keine Codierung, sondern ein Bedienablauf laut Betriebsanleitung.

### 3.6 PDC (hinten, im REM)

| ID | Funktion | Block / Parameter | Werte | BimmerCode-Label | Tag |
|---|---|---|---|---|---|
| rem.pdc_auto_rolling_back | PDC beim Zurückrollen | REM_01 (nur BimmerCode) | Active / Not active | Activate PDC when rolling backwards | [DOK] – wahrscheinlich; nützlich am Berg mit Schaltgetriebe |
| rem.pdc_switch_off_thresholds | Abschaltschwellen | REM 3201 `CUT_OFF_SPEED` (Std. 0Fh = 15 km/h), `CUT_OFF_SPEED_HYST` (Std. 01) | – | PDC speed/distance switch-off threshold; Speed switch-off threshold for visual and acoustic PDC warnings | [DOK] |
| pdc.volume_and_mute | PDC-Lautstärke / Radioabsenkung | **kein Parameter gefunden** | – | – | [UNBEKANNT] (bei neueren Head-Units ein Klangmenüpunkt) |

### 3.7 Warnungen, Gongs, sonstiges

| ID | Funktion | ECU / Parameter | Werte | Tag |
|---|---|---|---|---|
| acsm.seat_belt_reminder | Gurtwarnung Fahrer/Beifahrer, Vorwarnung, Kombi-Anzeige | ACSM_4B 3000 `SeatBeltReminder_SBR_Fahrer`/`_Beifahrer`, `SBR_PreWarning_Fahrer`/`_Beifahrer`, `Gurtzustandsanzeige_Fahrer_GWF_GZA_FA`/`…_Beifahrer_GWF_GZA_BF` | aktiv → nicht_aktiv | [DOK] – **sicherheitskritisch, nur Doku** |
| acsm.seat_belt_reminder_duration | Dauer der Gurtwarnung | ACSM_4B 3001 `GWF_SBR_WARNDAUER` | Std. 64h = 100 s | [DOK] – nur Doku |
| kombi.turn_signal_tick_volume | Lautstärke Blinkerticken | KOMBI L7_MID 300B `BLINKER_VOLUME_CONTI` | Std. E0,F0,FF,FF; leiser A0,B0,C0,FF | [DOK] (1 Quelle); Kombi-Variante des Wagens [UNBEKANNT] |
| fem_body.battery_type | Batterietyp | FEM_01 (nur BimmerCode) | 20 Ah … 105 Ah AGM | [DOK]; nur nach Batterietausch, danach registrieren |
| – | Tür-offen-Warnung, Gong-Lautstärken allgemein | kein Parameter gefunden | – | [UNBEKANNT] |

---

## 4. C – Fahrdynamik und Antrieb (NUR DOKUMENTATION)

> **ICM, DSC, EPS, ACSM und DME sind sicherheits- bzw. emissionsrelevant.** Die folgenden Punkte sind ausschließlich dokumentiert, nicht empfohlen.

**Serienstand laut BMW:** Der Fahrerlebnisschalter mit ECO PRO ist beim F20 Serie, ebenso die Auto Start-Stop-Funktion für Schalt- und Automatikgetriebe (BMW Newsroom, 05.06.2011). Laut BMW-Pressematerial (nur Such-Snippet, Seite nicht direkt abrufbar) gibt es SPORT+ als vierten Modus nur bei Sport Line *mit* Variabler Sportlenkung. Für einen 116i ohne diese Ausstattung sind also nur ECO PRO, COMFORT und SPORT zu erwarten [WAHRSCHEINLICH].

| ID | Funktion | ECU / Parameter | Werte | BimmerCode-Label | Bewertung |
|---|---|---|---|---|---|
| icm.start_in_eco_pro | Start immer in ECO PRO | ICM(QL) 3000 `IcmKod_B_InitEco` | nicht_verbaut (Std., COMFORT) / verbaut (ECO PRO) | Start in ECO mode | [DOK]; vergleichsweise harmlos, ICM trotzdem nur dokumentieren |
| icm.sport_plus | SPORT+ nachrüsten | ICM 3000 `IcmKod_B_S2TBA` bzw. `IcmKod_B_Sportlenkung` (Quellen widersprüchlich) + KOMBI | verbaut | SPORT+ driving mode (1 of 2) [ICMQL] + (2 of 2) [KOMBI]; „Do not use this if your car already has SPORT+“ | [DOK], **sicherheitskritisch** (DSC/DTC-Verhalten); Forum: RPA-Fehler möglich |
| icm.sport_configurable | SPORT konfigurierbar | HU_CIC `Macro_fds` (popup_only → popup_and_config); BimmerCode: HU_NBT/EVO + ICMQL | – | SPORT driving mode configurable (1 of 2/2 of 2) | BimmerCode-Standard: nur mit HU_NBT/EVO → mit HU_ENTRY nicht verfügbar; Expert-Äquivalent [UNBEKANNT] |
| icm.driving_mode_memory | Fahrmodus merken | nur F15: ICMQL 300A `fesallowmode4lastfunction` usw., `feslastfunctioninterval` | – | – | [EXPERIMENTELL]; für F20 nicht belegt |
| dme.throttle_map_per_mode | Fahrpedalkennlinie je Modus | Serienfunktion (ECO PRO passt laut BMW das Ansprechverhalten an) | – | – | [UNBEKANNT] als Codierung; DME **nicht codieren** |
| kombi.dsc_off_unbundling | DSC-/DTC-Entflechtung | KOMBI 3000 `DSC_OFF_ENTFLECHTUNG_ENABLE` | nicht_aktiv → aktiv | – | [EXPERIMENTELL] (Botho: Nutzen „à valider“) |
| dsc.launch_control | Launch Control | DSC_CT01 3000 `C_Funktion_LaunchControl` (mit EGS) | 01 | – | **[NICHT KOMPATIBEL]**: Schaltgetriebe |
| dme.msa_in_dme | MSA-Speicher im DME | DME_BAC2 3020 `TCM_MSA_MEMORY` | – | – | **[NICHT KOMPATIBEL]**: nur G-Baureihen; ein F90-Forum warnt vor DME-Sperren |
| dme.live_data | Motor-Live-Daten | keine Codierung; BimmerLink (Diagnose, Sensorwerte, CSV-Logging) | – | – | [DOK] allgemein; welche N13-Messwerte angeboten werden, ist [UNBEKANNT] |
| eps.no_user_coding | EPS | keine Komfortoptionen gefunden | – | – | [UNBEKANNT]; Lenkung nicht codieren |

**Start-Stop-Logik:** Die MSA-Bedingungen selbst (Batterie, Temperatur, Gang/Kupplung) sind keine Codieroption. Belegt sind nur die drei FEM-Schalter aus 3.3.

---

## 5. Rechtliche Einordnung (Deutschland)

> Keine Rechtsberatung. Belastbar zitiert sind UNECE R48 Rev. 7 (PDF) und, nur über Such-Snippets, § 17 StVO. Alles andere ist als Einschätzung gekennzeichnet.

| Thema | Einschätzung | Grundlage |
|---|---|---|
| **US-Sidemarker (Blinker als Dauerlicht)** | **Unzulässig.** Fahrtrichtungsanzeiger müssen „independently of the other lamps“ schalten (R48 6.5.7). Foren: „in D offiziell nicht erlaubt“. Risiko: Mangel bei der HU, Bußgeld, Erlöschen der Betriebserlaubnis. | R48 6.5.7; motor-talk (Snippet) |
| **Notbremssignal / Bremskraftanzeige** ändern | **Nicht zulässig**, wenn außerhalb R48: Blinkfrequenz 4,0 ± 1,0 Hz, bei Glühlampen 4,0 +0/−1 Hz (6.23.7.1); Aktivierung nur oberhalb 50 km/h und mit Notbrems-Logiksignal (6.23.7.3.1). 5 Hz bzw. Aktivierung unter 50 km/h verstoßen dagegen. | R48 6.23 |
| **Warnblinker nach Notbremsung** | Zulässig: R48 6.6.7.2 erlaubt die automatische Aktivierung nach Deaktivierung des Notbremssignals. | R48 6.6.7.2 |
| **Nebelscheinwerfer mit Standlicht / als TFL** | Benutzung nur bei erheblicher Sichtbehinderung durch Nebel, Schneefall oder Regen („Nur bei solcher Witterung dürfen Nebelscheinwerfer eingeschaltet sein“). Als TFL-Ersatz unzulässig, Verwarnungsgeld 20–35 € laut bussgeldkatalog.org. | § 17 Abs. 3 StVO (Snippet); bussgeldkatalog.org (Snippet) |
| **NSW bleiben bei Fernlicht an** | Technisch konform: R48 6.3.7 verlangt, dass Nebelscheinwerfer unabhängig von Fern-/Abblendlicht schaltbar sind. Benutzung weiterhin nur nach § 17 Abs. 3 StVO. | R48 6.3.7 |
| **Abbiegelicht über NSW** | **Grauzone.** Abbiegeleuchten sind in R48 6.20 als R119-Leuchten vorgesehen. NSW dürfen laut 6.3.7 nur innerhalb eines AFS Teil einer anderen Funktion sein. Ohne werkseitige Genehmigung für dieses Fahrzeug ist der Status unklar. | R48 6.20, 6.3.7 |
| **TFL abschalten / dimmen** | In DE gibt es keine Pflicht, TFL zu *benutzen* (ADAC). Für typgenehmigte Fahrzeuge verlangt R48 6.19.7.1 aber automatisches Einschalten, manuelles Ausschalten nur bis 10 km/h (6.19.7.2). Dauerhaftes Wegcodieren weicht vom Genehmigungszustand ab → **Grauzone**. Beim Dimmen Mindestlichtstärke (R87) beachten, nicht geprüft. | R48 6.19.7; ADAC (Snippet) |
| **Rückleuchten mit TFL** | [UNBEKANNT]: R48 6.19 regelt nur das vordere TFL. | – |
| **LED-Nachrüstung / Lampenüberwachung aus** | LED-Ersatzlampen in Scheinwerfern brauchen in DE eine Genehmigung für das konkrete Fahrzeug. Bei abgeschalteter Überwachung werden defekte Lampen nicht mehr gemeldet. | Einschätzung |
| **MSA standardmäßig aus / Memory** | **Grauzone:** Verbrauchs-/CO2-Typprüfwerte gelten mit aktivem MSA. Eine Vorschrift, die das Umcodieren verbietet, wurde **nicht** gefunden, die HU prüft es nicht. | [UNBEKANNT] |
| **Gurtwarnung deaktivieren** | Sicherheitsfunktion; die Gurtpflicht nach § 21a StVO bleibt. **Nicht empfohlen.** | Einschätzung |
| **SPORT+, DSC, ICM, EPS, DME** | Eingriff in sicherheits- bzw. emissionsrelevante Systeme, mögliche Folgen für Betriebserlaubnis und Versicherung. **Nur dokumentieren.** | Einschätzung |
| **Komfortschließen per Funk** | Fenster mit Einklemmschutz; eine konkrete EU-/DE-Anforderung an Fernschließen wurde nicht geprüft → [UNBEKANNT]. Nur in Sichtweite benutzen. | – |

---

## 6. Hardware-blockierte Optionen (für dieses Fahrzeug)

- **Spiegel anklappen** (Komfortschließen, automatisch, Geschwindigkeitsschwellen, Bordsteinautomatik): braucht elektrische Anklappspiegel, die nicht angegeben sind. Der Spiegelschalter in der Tür zeigt, ob vorhanden.
- **Akustische Verriegelungsquittierung / Alarmparameter** (FZD__07/CANS2): braucht eine Diebstahlwarnanlage.
- **Sitzheizung speichern:** braucht das Sitzmodul CFAS/CBFS (elektrische Memory-Sitze).
- **Ambientelicht, Türgriffbeleuchtung bei R:** braucht die entsprechende Lichtausstattung.
- **Scheinwerferreinigung:** braucht SRA-Düsen (bei Halogen üblicherweise nicht vorhanden).
- **Heckklappe per Schlüssel schließen (HKFM/HKFM2):** braucht eine elektrische Heckklappe.
- **Launch Control:** braucht Automatik/EGS.
- **TFL-Schalter im iDrive, SPORT konfigurierbar:** in BimmerCode nur für HU_NBT/NBT_EVO (bzw. in E-Sys-Quellen für CIC) belegt; der Wagen hat HU_ENTRY → wahrscheinlich nicht verfügbar ([UNBEKANNT], kein HU_ENTRY-Parameter gefunden).
- **SPORT+:** ab Werk an Sport Line + Variable Sportlenkung gebunden. `IcmKod_B_Sportlenkung` beschreibt diese Hardware.
- **Klimaoptionen:** nur mit Klimaautomatik (IHKA), nicht mit IHKR.
- **Fensterheber hinten (REM 3050):** nur beim 5-Türer.

---

## 7. Offene Fragen (am Fahrzeug klären)

1. **I-Stufe/CAFD-Stand von FEM_BODY und REM:** Hat der Wagen noch den Werksstand von 2012 oder ein späteres Update? Davon hängen `BLINKZYKLEN_ANZAHL_TIPP` und die Wertebezeichnungen (z. B. `TFL_MODUS` 02 vs. TFL_S, `CLM_SPEED_LIMIT_PIA_AUTO_LOCK` wert_xx vs. hex) ab.
2. **Klimaautomatik (IHKA, welche Variante: CBF/VA01/VA02) oder manuelle Klimaanlage (IHKR)?** BimmerCode zeigt beim Verbinden die Steuergeräteliste.
3. **Diebstahlwarnanlage vorhanden?** Davon hängen akustische Quittierung und FZD-Optionen ab.
4. **Elektrisch anklappbare Außenspiegel vorhanden?**
5. **3- oder 5-Türer?** Relevant für die hinteren Fensterheber im REM.
6. **Welche Leuchte bildet beim Halogen-Scheinwerfer TFL und Standlicht** (Ring/Lichtleiter, Glühlampe/LED)? Davon hängen Helligkeitsoptionen und ESS-Frequenz (Glühlampe → max. 4 Hz) ab.
7. **Sind Bremsleuchten und Rückleuchten beim Pre-LCI-F20 LED oder Glühlampe?** Relevant für R48 6.23.7.1.1.
8. **Ist das Abbiegelicht über NSW ab Werk schon aktiv?** Botho nennt „F020_enable“ als Standard. Ist-Wert prüfen.
9. **KOMBI-Variante** (L6 BO / L7_BASIS / L7_MID?) und **ACSM-Variante** (4B/4C): bestimmen, welche BimmerCode-Optionen erscheinen.
10. **HU_ENTRY-Menüs:** Bietet das Radio Professional Fahrzeugeinstellungen für Verriegeln nach Losfahren, Heimleuchten-Dauer und Komfortblinker? Falls ja, ist dort keine Codierung nötig.
11. **Komfortöffnen/-schließen in DE schon ab Werk aktiv?** Erst auslesen.
12. **MSA-Parameter in FEM 3023 beim Werksstand 2012 vorhanden?** Dass es sie beim frühen F20 gibt, wurde nicht explizit bestätigt.
13. **PDC „beim Zurückrollen“:** Funktioniert das mit reinem Heck-PDC im REM? Nicht belegt.

---

## 8. Quellen

**Direkt abgerufen und ausgewertet:**
- BimmerCode – Supported coding options, BMW 1 Series F20/F21: https://bimmercode.app/cars/f20/
- BimmerCode – Quick Start Guide/Manual (Expert Mode, Backups): https://bimmercode.app/manual/
- GitHub packetpilot/bmw-f, E-Sys-Cheat-Dateien (über raw.githubusercontent.com):
  - https://github.com/packetpilot/bmw-f/blob/master/cheats/Botho.xml (F020/F030, mit Standardwerten)
  - https://github.com/packetpilot/bmw-f/blob/master/cheats/ekfxisid.xml (F020/F030)
  - https://github.com/packetpilot/bmw-f/blob/master/cheats/Bundang_Thunder.xml (F20–F36)
  - https://github.com/packetpilot/bmw-f/blob/master/cheats/Almaretto.xml
  - https://github.com/packetpilot/bmw-f/blob/master/cheats/Kip_M3.xml
  - https://github.com/packetpilot/bmw-f/blob/master/cheats/otakar.xml
  - https://github.com/packetpilot/bmw-f/blob/master/cheats/packetpilot.xml
  - https://github.com/packetpilot/bmw-f/blob/master/cheats/FDLCodes.xml
  - https://github.com/packetpilot/bmw-f/blob/master/cheats/ruben_17non.xml
- GitHub brodee227/bmw-f (ECU-Liste: FEM_BODY [40], REM [72], ICM [1c], ACSM [01], IHKA3 [78]): https://github.com/brodee227/bmw-f
- Google Sheet „Coding BMW F3x“: https://docs.google.com/spreadsheets/d/16O4RKIMekWFCs5jPW3T_7li0yIEvgZfFI0u3l0RmSwU/pubhtml
- Google Sheet F87-Codierliste: https://docs.google.com/spreadsheets/d/1TjoUmnkFYbzdcL8v2DF5fcMixHXSVWRexVV1g2ybG14/edit
- UNECE Regulation No. 48, Revision 7 (E/ECE/324/Rev.1/Add.47/Rev.7, 17.01.2013): https://nsai.ie/images/uploads/certification-automotive/UNECE-R48-04.pdf
- BMW Group Newsroom „The new BMW 1 Series“ (05.06.2011): https://newsroom.bmwgroup.com/global/the-new-bmw-1-series
- BimmerLink (Live-Daten/Diagnose): https://bimmerlink.app/

**Nur über Such-Snippets (Abruf blockiert oder nicht möglich):**
- motor-talk „Start des ersten Codierens…“ (KOMFORTOEFFNUNG_FB/KOMFORTSCHLIESSUNG_FB, 3053; 403): https://www.motor-talk.de/forum/start-des-ersten-codierens-einstiegsfragen-t7071093.html
- motor-talk „Programmierung auf US Tagfahrlicht“: https://www.motor-talk.de/forum/programmierung-auf-us-tagfahrlicht-t829021.html
- § 17 StVO (503): https://www.gesetze-im-internet.de/stvo_2013/__17.html
- ADAC Tagfahrlicht: https://www.adac.de/rund-ums-fahrzeug/ausstattung-technik-zubehoer/ausstattung/tagfahrlicht/
- bussgeldkatalog.org Tagfahrlicht/Nebelscheinwerfer: https://www.bussgeldkatalog.org/tagfahrlicht-nebelscheinwerfer/
- f30.bimmerpost (SAT/Sport+, IcmKod_B_S2TBA): https://f30.bimmerpost.com/forums/showthread.php?p=18141876
- Blog „How to code non-sport BMW 320i to Sport+“: https://bmw-icom-a2-wifi.blogspot.com/2017/11/how-to-code-non-sport-bmw-320i-to-sport.html
- f90.bimmerpost (MSA im DME, G-Baureihe): https://f90.bimmerpost.com/forums/showthread.php?p=29809376
- BMW Presse UK (SPORT+ nur mit Sport Line + Variabler Sportlenkung; Weiterleitung, Inhalt nur als Snippet): https://www.press.bmwgroup.com/united-kingdom/article/detail/T0112077EN_GB/the-new-bmw-1-series
