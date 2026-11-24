# CODING_DATABASE – Individueller Codierungskatalog BMW 116i F20 (01/2012)

> Automatisch erzeugt aus `src/f20/data/catalog/*.json` (Quelle: `docs/research/raw/0[45]_*.json`) mit `python scripts/export_catalog_md.py`. Nicht von Hand bearbeiten.

**Fahrzeug:** BMW 116i F20, Produktion 24.01.2012, N13 (MEVD17.2.5), Schaltgetriebe, Radio Professional (HU_ENTRY), MFL, Sitzheizung vorn, PDC hinten (im REM), Nebelscheinwerfer, Regen-/Lichtsensor.

**Wichtig:** Kein Eintrag ist am eigenen Fahrzeug getestet. Höchster Nachweisstatus ist „Dokumentiert“. Erst nach Umsetzung in BimmerCode + Vorher/Nachher-Backup wird ein Eintrag zu „Nachgewiesen“. Es wurden keine Funktionen oder Parameter erfunden – fehlt ein Beleg, steht „Unbekannt“.

## Übersicht

| Bereich | Anzahl |
|---|---|
| 1. Empfehlenswert | 33 |
| 2. Möglich, aber rechtliche Grauzone oder mit Vorsicht | 15 |
| 3. Unklar | 36 |
| 4. Informations- und Werkstattthemen (lesend / keine Komfortcodierung) | 6 |
| 5. Nur Dokumentation | 15 |
| 6. In Deutschland nicht zulässig | 8 |
| 7. Nicht möglich bei diesem Fahrzeug (fehlende Hardware / HU_ENTRY) | 18 |
| **Gesamt** | **131** |

Legende: **BC** = BimmerCode (Standard = normale Oberfläche, Expert = Expertenmodus). Risiko/Kompatibilität/Nachweis wie in RESEARCH.md definiert.

## 1. Empfehlenswert – risikoarm, dokumentiert, wahrscheinlich kompatibel

Diese Optionen sind in Quellen belegt, passen mit hoher Wahrscheinlichkeit zu deinem F20 (01/2012, HU_ENTRY, Schaltgetriebe) und sind nach aktuellem Recherchestand rechtlich unproblematisch. **Nicht am Fahrzeug getestet.**

| Funktion | SG | Parameter (Block) | Werte | BC | Risiko | Kompat. | Nachweis |
|---|---|---|---|---|---|---|---|
| [Komfortöffnen per Fernbedienung (Fenster/SHD)](#fem_bodycomfort_open_remote) | FEM_BODY | `KOMFORTOEFFNUNG_FB`, `KOMFORTOEFFNUNG` (3053) | `aktiv` Komfortöffnen per Funkschlüssel; `nicht_aktiv` aus; `Active / Not active` BimmerCode 'Convenient opening' bzw. '… with remote control' | standard | gering | wahrscheinlich kompatibel | Dokumentiert |
| [Digitale Geschwindigkeit im Bordcomputer](#kombidigital_speed) | KOMBI | `BC_DIGITAL_V` (3000) | `nicht_aktiv` keine Digitalanzeige (Standard); `aktiv` Geschwindigkeit als Zahl im BC | standard | gering | wahrscheinlich kompatibel | Dokumentiert |
| [Komfortblinker: Anzahl Blinkzyklen (3 → 5)](#fem_bodycomfort_turn_signal_count) | FEM_BODY | `BLINKZYKLEN_ANZAHL_TIPP` (3060) | `02` 3 Blinkzyklen (Standard laut Spreadsheet F3x; Botho nennt 00); `04` 5 Blinkzyklen (Wert = Anzahl − 1) | expert | gering | wahrscheinlich kompatibel | Dokumentiert |
| [Optische Quittierung: Blinkanzahl beim Ver-/Entriegeln](#fem_bodylock_unlock_flash_count) | FEM_BODY | `QUITTBLK_SICHERN_ANZAHL`, `QUITTBLK_ENTSCHAERFEN_ANZAHL` (3060) | `QUITTBLK_SICHERN_ANZAHL = 01` 1x beim Verriegeln (Standard laut Botho); `QUITTBLK_ENTSCHAERFEN_ANZAHL = 02` 2x beim Entriegeln (Standard laut Botho); `1 time / 2 times / 3 times / Off` Auswahl in BimmerCode | standard | gering | wahrscheinlich kompatibel | Dokumentiert |
| [Radio/iDrive beim Öffnen der Fahrertür ausschalten](#fem_bodyradio_off_driver_door) | FEM_BODY | `TCM_LOGIC_R_OFF_DOOR` (3020) | `nicht_aktiv` Standard laut Botho; `aktiv` aus beim Öffnen der Fahrertür | standard | gering | wahrscheinlich kompatibel | Dokumentiert |
| [Regen-/Lichtsensor: Empfindlichkeit (Lichtautomatik)](#fem_bodyrls_sensitivity) | FEM_BODY | `RLS_DEF_FLC_SCHWELLWERT_SATZ` (3130) | `00` Standard laut Botho.xml; `03` weniger empfindlich (Botho); `unempfindlich` Wertebezeichnung in Almaretto/Kip; `Insensitive / Normal / Sensitive / Very sensitive` Auswahl in BimmerCode | standard | gering | wahrscheinlich kompatibel | Dokumentiert |
| [Sitzheizung: Temperatur der Stufen 1–3 (vorn)](#fem_bodyseat_heating_temperatures) | FEM_BODY | – | `Front seats level 1: 30–34 °C` BimmerCode; `Front seats level 2: 35–40 °C` BimmerCode; `Front seats level 3: 41–46 °C` BimmerCode; `Front backrests level 1/2/3: 30–35 / 36–41 / 42–47 °C` BimmerCode | standard | gering | wahrscheinlich kompatibel | Dokumentiert |
| [Entriegeln bei 'Zündung aus' (nach Auto-Lock)](#fem_bodyunlock_on_ignition_off) | FEM_BODY | `CLM_UNLOCK_KL15OFF_AFTER_PIA_AUTO_LOCK` (3040) | `aktiv` Standard laut Botho/Spreadsheet F3x; `nicht_aktiv` bleibt verriegelt | standard | gering | wahrscheinlich kompatibel | Dokumentiert |
| [Welcome Light: Aktivierung (Lichtschalterstellung)](#fem_bodywelcome_light_activation) | FEM_BODY | – | `Light switch on auto` nur bei Lichtschalter in AUTO; `Light switch on auto or 2` bei AUTO oder Abblendlicht-Stellung; `Not active` Welcome Light aus | standard | gering | wahrscheinlich kompatibel | Dokumentiert |
| [Welcome Light: Leuchtdauer](#fem_bodywelcome_light_duration) | FEM_BODY | `WL_TIMEOUT` (3060) | `14 (hex)` 20 s – Standard laut Botho.xml; `3C (hex)` 60 s; `5/10/15/20/30/45/60 seconds` Auswahl in BimmerCode | standard | gering | wahrscheinlich kompatibel | Dokumentiert |
| [Fensterheber bei geöffneter Tür weiter bedienbar (vorn)](#fem_bodywindow_door_open_front) | FEM_BODY | `FH_TUERAUF_STOP_MAUT` (3050) | `aktiv` Standard – Unterbrechung bei offener Tür; `nicht_aktiv` Fenster lassen sich bei offener Tür bedienen | standard | gering | wahrscheinlich kompatibel | Dokumentiert |
| [Nachwischzyklen nach dem Waschen (vorn/hinten)](#fem_bodywipe_after_wash) | FEM_BODY | `WW_ANZAHL_NACHWISCHZ_FRONT`, `WW_ANZAHL_NACHWISCHZ_HECK` (3080) | `WW_ANZAHL_NACHWISCHZ_FRONT = 03` 3 Zyklen – Standard laut Botho; `WW_ANZAHL_NACHWISCHZ_HECK = 02` 2 Zyklen – Standard; `01 … 05` 1–5 Zyklen (BimmerCode) | standard | gering | wahrscheinlich kompatibel | Dokumentiert |
| [Automatischer Reset der Durchschnittswerte](#kombiaverage_values_reset) | KOMBI | `BC_AUTORESET_ZEIT` (3000) | `After 4 hours` Reset nach 4 h Standzeit (BimmerCode; laut Sammlung werte=04); `After 8 hours` Reset nach 8 h; `After every ride` Reset nach jeder Fahrt; `Never` kein automatischer Reset (laut Sammlung werte=FF) | standard | gering | wahrscheinlich kompatibel | Dokumentiert |
| [Leerer Menüpunkt im Bordcomputer](#kombiempty_menu_item) | KOMBI | – | `Active` leere Seite vorhanden; `Not active` keine leere Seite | standard | gering | wahrscheinlich kompatibel | Dokumentiert |
| [PDC automatisch aktivieren beim Zurückrollen](#rempdc_auto_rolling_back) | REM | – | `Active / Not active` Auswahl in BimmerCode | standard | gering | wahrscheinlich kompatibel | Dokumentiert |
| [Coming Home (Heimleuchten): Standarddauer](#fem_bodycoming_home_duration) | FEM_BODY | `PIA_DEFAULT_FMH` (3064) | `14 (hex)` 20 s – Standard laut Botho.xml; `1E (hex)` 30 s | expert | gering | wahrscheinlich kompatibel | Dokumentiert |
| [Auswahl der BC-Anzeigen über iDrive](#kombibc_information_display_selection) | KOMBI | – | – | unknown | gering | wahrscheinlich kompatibel | Dokumentiert |
| [Heckklappe per Fernbedienung: Öffnungsverzögerung](#fem_bodybootlid_delay) | FEM_BODY | `CLM_TIME_DELAY_BOOTLID`, `RC_TIME_DELAY_BOOTLID` (3040, 30D0) | `CLM_TIME_DELAY_BOOTLID = wert_02` 0,3 s – Standard laut Botho; `CLM_TIME_DELAY_BOOTLID = wert_01` 0,1 s; `RC_TIME_DELAY_BOOTLID = 05 (hex)` Standard laut Botho; `0.5 s / 1 s / 5 s / 10 s / No delay` Auswahl in BimmerCode | standard | gering | wahrscheinlich kompatibel | Dokumentiert |
| [Komfortöffnen/-schließen: Verzögerung](#fem_bodycomfort_open_close_delay) | FEM_BODY | `KOMFORT_OEFFNEN`, `KOMFORT_SCHLIESSEN` (3053) | `KOMFORT_OEFFNEN = 19 (hex)` 2,5 s – Standard laut Botho/Kip; `KOMFORT_OEFFNEN = 14 (hex)` 2,0 s; `KOMFORT_SCHLIESSEN = 0F (hex)` 1,5 s – Standard; `KOMFORT_SCHLIESSEN = 0A / 00` 1,0 s / keine Verzögerung | standard | gering | wahrscheinlich kompatibel | Dokumentiert |
| [Warnblinker nach Notbremsung](#fem_bodyhazard_after_emergency_braking) | FEM_BODY | `WB_GB_ENABLE`, `WB_GB_GEFAHRENWERT_MIN` (3060) | `aktiv / 01` Warnblinker nach Gefahrenbremsung; `nicht_aktiv` aus; `Active / Not active` Auswahl in BimmerCode | standard | mittel | wahrscheinlich kompatibel | Dokumentiert |
| [Hupsignal beim Verriegeln mit laufendem Motor](#fem_bodyhorn_lock_engine_running) | FEM_BODY | `CLM_HORN_AT_SECURE` (3040) | `aktiv` Standard laut Botho; `nicht_aktiv` aus | standard | gering | wahrscheinlich kompatibel | Dokumentiert |
| [Heckwischer beim Rückwärtsgang](#fem_bodyrear_wiper_reverse) | FEM_BODY | `WW_HECKWISCHER_EIN_RUECKWGANG` (3080) | `aktiv` Standard laut Botho; `nicht_aktiv` aus | standard | gering | wahrscheinlich kompatibel | Dokumentiert |
| [Wiederverriegelung, wenn nach Entriegeln keine Tür geöffnet wird](#fem_bodyrelock_timeout) | FEM_BODY | `CLM_TIME_PIA_LOCK_AT_TIMEOUT` (3040) | `0C (hex)` 120 s – Standard laut Botho (Einheit 10 s); `03 (hex)` 30 s; `12 (hex)` 180 s (otakar); `10 s … 10 min` Auswahl in BimmerCode | standard | gering | wahrscheinlich kompatibel | Dokumentiert |
| [Welcome Light: Helligkeit](#fem_bodywelcome_light_brightness) | FEM_BODY | `WL_HELLIGKEIT` (3070) | `64 (hex)` 100 % – Standard laut Botho.xml; `32 (hex)` 50 %; `10 % … 100 %` Auswahl in BimmerCode | standard | gering | wahrscheinlich kompatibel | Dokumentiert |
| [Welcome Light: weitere Leuchten (Abblend-/Fernlicht, Standlicht, TFL, Blinker, Abbiegelicht, Sidemarker)](#fem_bodywelcome_light_components) | FEM_BODY | – (3063 (vermutlich, analog MAPPING_*_PART_OF_WL)) | `Hard on` hart einschalten; `Soft on` sanft einblenden; `Not active` nicht Teil des Welcome Lights | standard | gering | wahrscheinlich kompatibel | Dokumentiert |
| [Welcome Light nur bei Dunkelheit](#fem_bodywelcome_light_darkness_only) | FEM_BODY | – | `Active` nur bei Dunkelheit; `Not active` immer | standard | gering | wahrscheinlich kompatibel | Dokumentiert |
| [Wischerstufe im Stand automatisch zurückschalten](#fem_bodywiper_level_switch_back) | FEM_BODY | – | `Active / Not active` Auswahl in BimmerCode | standard | gering | wahrscheinlich kompatibel | Dokumentiert |
| [Reservewarnung 2 (temporär)](#kombilow_fuel_warning_2) | KOMBI | – | `50 kilometers` ab 50 km; `60 kilometers` ab 60 km; `70 kilometers` ab 70 km; `80 kilometers` ab 80 km | standard | gering | wahrscheinlich kompatibel | Dokumentiert |
| [PDC: Abschaltschwellen (Geschwindigkeit/Strecke)](#rempdc_switch_off_thresholds) | REM | `CUT_OFF_SPEED`, `CUT_OFF_SPEED_HYST` (3201) | `CUT_OFF_SPEED = 0F (hex)` 15 km/h – Standard laut Spreadsheet F3x; `CUT_OFF_SPEED_HYST = 01` Hysterese (Standard); `PDC speed switch-off threshold: 5–50 km/h` BimmerCode; `PDC distance switch-off threshold: 10–250 m` BimmerCode | standard | gering | wahrscheinlich kompatibel | Dokumentiert |
| [Automatisch verriegeln nach Anfahren: Geschwindigkeitsschwelle](#fem_bodyauto_lock_speed) | FEM_BODY | `CLM_SPEED_LIMIT_PIA_AUTO_LOCK` (3040) | `wert_04` ca. 16 km/h – Standard laut Botho; `wert_03` ca. 8 km/h (Botho); `0A (hex)` 10 km/h (ekfxisid/otakar – andere Kodierungsdarstellung) | expert | gering | wahrscheinlich kompatibel | Dokumentiert |
| [Innenlicht: Nachleuchtdauer beim Ver-/Entriegeln](#fem_bodyinterior_light_duration) | FEM_BODY | `IB_EINSCHALT_BEGR_LOK`, `IB_EINSCHALT_BEGR_ULOK` (3070) | `IB_EINSCHALT_BEGR_LOK = 08` 8 s nach Verriegeln (Standard laut Botho); `IB_EINSCHALT_BEGR_ULOK = 14 (hex)` 20 s nach Entriegeln (Standard laut Botho); `3C (hex)` 60 s | expert | gering | wahrscheinlich kompatibel | Dokumentiert |
| [Blinkquittierung beim Öffnen der Heckklappe](#fem_bodytailgate_open_flash) | FEM_BODY | `HECKKLAPPE_REVERSIEREN_BLINKEN` (3060) | `01` Standard (doppelt laut Botho); `00` einfach | expert | gering | wahrscheinlich kompatibel | Dokumentiert |
| [Reservewarnung 1 (dauerhaft)](#kombilow_fuel_warning_1) | KOMBI | – | `10 kilometers` ab 10 km Restreichweite; `20 kilometers` ab 20 km; `30 kilometers` ab 30 km; `40 kilometers` ab 40 km | standard | mittel | wahrscheinlich kompatibel | Dokumentiert |

## 2. Möglich, aber rechtliche Grauzone oder mit Vorsicht

Technisch wahrscheinlich möglich; die Einordnung nach StVO/StVZO/ECE-R48 ist unklar oder an Bedingungen geknüpft. Rechtshinweis jeweils beachten.

| Funktion | SG | Parameter (Block) | Werte | BC | Risiko | Kompat. | Nachweis |
|---|---|---|---|---|---|---|---|
| [Komfortschließen per Fernbedienung](#fem_bodycomfort_close_remote) | FEM_BODY | `KOMFORTSCHLIESSUNG_FB`, `KOMFORTSCHLIESSUNG` (3053) | `aktiv` Komfortschließen per Funkschlüssel; `nicht_aktiv` aus | standard | mittel | wahrscheinlich kompatibel | Dokumentiert |
| [Auto Start-Stop (MSA) standardmäßig aus](#fem_bodymsa_default_off) | FEM_BODY | `TCM_MSA_DEFAULT_OFF` (3023) | `nicht_aktiv` Standard – MSA beim Start aktiv; `aktiv` MSA beim Start aus | standard | mittel | wahrscheinlich kompatibel | Dokumentiert |
| [Auto Start-Stop: letzten Zustand merken](#fem_bodymsa_memory) | FEM_BODY | `TCM_MSA_MEMORY` (3023) | `nicht_aktiv` Standard laut Botho; `aktiv` letzten Zustand merken | standard | mittel | wahrscheinlich kompatibel | Dokumentiert |
| [Welcome Light: Nebelscheinwerfer einbeziehen](#fem_bodywelcome_light_fog) | FEM_BODY | `MAPPING_NEBELSCHW_L_PART_OF_WL`, `MAPPING_NEBELSCHW_R_PART_OF_WL` (3063) | `nicht_aktiv / 00` Standard – Nebelscheinwerfer nicht Teil des Welcome Lights; `soft_On` sanft einblenden; `hard_On` hart einschalten | standard | gering | wahrscheinlich kompatibel | Dokumentiert |
| [Rückleuchten mit Tagfahrlicht](#remdrl_tail_lights) | REM | `MAPPING_TAGFAHRL_H_L_OUTPUT`, `MAPPING_TAGFAHRL_H_R_OUTPUT`, `MAPPING_TAGFAHRL_H2_L_OUTPUT`, `MAPPING_TAGFAHRL_H2_R_OUTPUT` (3062) | `00 / off` Standard – aus; `sl_l / sl_r (14/15 hex)` äußere Rückleuchten links/rechts; `sl_2_l / sl_2_r (16/17 hex)` innere Rückleuchten (Heckklappe) links/rechts | standard | gering | wahrscheinlich kompatibel | Dokumentiert |
| [Tagfahrlicht: Helligkeit](#fem_bodydrl_brightness) | FEM_BODY | `MAPPING_TAGFAHRL_V_L_PWM_LEVEL_1`, `MAPPING_TAGFAHRL_V_R_PWM_LEVEL_1` (3062) | `64 (hex)` 100 % – Standard laut Botho.xml; `32 (hex)` 50 %; `10 % … 100 %` Auswahl in BimmerCode | standard | gering | wahrscheinlich kompatibel | Dokumentiert |
| [Tagfahrlicht (TFL): Modus](#fem_bodydrl_mode) | FEM_BODY | `TFL_MODUS` (3060) | `02` Standard laut Botho.xml (Wertbedeutung nicht erläutert); `TFL_S` TFL inkl. Rückleuchten (Almaretto/Kip/FDLCodes, Teil 1 von 2 mit REM); `Active / Active also with parking lights / Not active` Auswahl in BimmerCode | standard | mittel | wahrscheinlich kompatibel | Dokumentiert |
| [Nebelscheinwerfer beim Fernlicht ausschalten](#fem_bodyfog_off_with_high_beam) | FEM_BODY | `NSW_AUS_BEI_FL` (3060) | `00` Nebelscheinwerfer bleiben bei Fernlicht an (Botho: Standard 00); `01` Nebelscheinwerfer gehen bei Fernlicht aus (abgeleitet aus packetpilot 'Disable Hi-Beam Override' = 00); `Active / Not active` Auswahl in BimmerCode | standard | gering | wahrscheinlich kompatibel | Dokumentiert |
| [Abbiegelicht (Nebel) beim Rückwärtsfahren](#fem_bodycornering_fog_reverse) | FEM_BODY | `C_CLC_REV_ALWAYS_ON`, `C_CLC_REV_CURV_BOTH_ON` (3073) | `01` aktiv (Standard laut Botho.xml); `00` aus (abgeleitet, nicht explizit belegt) | expert | gering | wahrscheinlich kompatibel | Dokumentiert |
| [Abbiegelicht über Nebelscheinwerfer](#fem_bodycornering_light_via_fog) | FEM_BODY | `C_CLC_ENA`, `C_BLC_ENA`, `KL_ENABLE_LI`, `KL_ENABLE_RE`, `MAPPING_ABBIEGEL_L_OUTPUT`, `MAPPING_ABBIEGEL_R_OUTPUT` (3073, 3066, 3062) | `C_CLC_ENA/C_BLC_ENA = F020_enable (01)` aktiv; `C_CLC_ENA/C_BLC_ENA = F020_disable` aus; `KL_ENABLE_LI/RE = KL_Ein / KL_Aus` Abbiegelicht links/rechts ein/aus; `MAPPING_ABBIEGEL_L/R_OUTPUT = nsw_l / nsw_r (0B/0C)` Ausgang = Nebelscheinwerfer links/rechts | standard | mittel | wahrscheinlich kompatibel | Dokumentiert |
| [Auto Start-Stop im ECO-PRO-Modus automatisch aktivieren](#fem_bodymsa_eco_pro) | FEM_BODY | `TCM_MSA_ECO_MODE` (3023) | `aktiv` Standard laut Botho; `nicht_aktiv` kein automatisches Einschalten in ECO PRO | standard | mittel | wahrscheinlich kompatibel | Dokumentiert |
| [Lampenüberwachung vorn (Kalt-/Warmüberwachung, LED-Kennung)](#fem_bodylamp_monitoring_front) | FEM_BODY | `FRA_V_L_KALTUEBERWACHUNG`, `FRA_V_L_WARMUEBERWACHUNG`, `FRA_V_L_IS_LED`, `FRA_V_R_KALTUEBERWACHUNG`, `FRA_V_R_WARMUEBERWACHUNG`, `FRA_V_R_IS_LED`, `NSW_L_KALTUEBERWACHUNG`, `NSW_L_WARMUEBERWACHUNG`, `NSW_L_IS_LED`, `NSW_R_KALTUEBERWACHUNG`, `NSW_R_WARMUEBERWACHUNG`, `NSW_R_IS_LED` (3061) | `*_KALTUEBERWACHUNG / *_WARMUEBERWACHUNG = aktiv` Standard – Lampenausfallüberwachung; `= nicht_aktiv` Überwachung aus; `*_IS_LED = aktiv` Ausgang als LED kennzeichnen | standard | mittel | wahrscheinlich kompatibel | Dokumentiert |
| [Lampenüberwachung hinten (Blinker, Brems-, Rückfahr-, Nebelschlussleuchte)](#remlamp_monitoring_rear) | REM | `FRA_H_L_KALTUEBERWACHUNG`, `FRA_H_L_WARMUEBERWACHUNG`, `FRA_H_L_IS_LED`, `FRA_H_R_KALTUEBERWACHUNG`, `FRA_H_R_IS_LED`, `BL_L_KALTUEBERWACHUNG`, `BL_L_WARMUEBERWACHUNG`, `BL_L_IS_LED`, `BL_R_KALTUEBERWACHUNG`, `BL_R_WARMUEBERWACHUNG`, `BL_R_IS_LED`, `RFS_L_KALTUEBERWACHUNG`, `RFS_L_WARMUEBERWACHUNG`, `RFS_L_IS_LED`, `RFS_R_KALTUEBERWACHUNG`, `RFS_R_WARMUEBERWACHUNG`, `RFS_R_IS_LED` (3061) | `aktiv` Standard – Überwachung an; `nicht_aktiv` Überwachung aus; `*_IS_LED = aktiv` LED-Ausgang | standard | mittel | wahrscheinlich kompatibel | Dokumentiert |
| [Stand-/Positionslicht ('Angel Eyes'): Helligkeit](#fem_bodyparking_light_brightness) | FEM_BODY | `MAPPING_STANDL_V_L_PWM_LEVEL_STANDARD`, `MAPPING_STANDL_V_R_PWM_LEVEL_STANDARD` (3062) | `8` Standard laut Botho.xml; `32 (hex)` 50 %; `64 (hex)` 100 % | standard | gering | unbekannt | Dokumentiert |
| [Tagfahrlicht-Ein/Aus im iDrive-Menü](#hu_entrydrl_checkbox) | HU_ENTRY | `Daydriving_light` (3000) | `Perm_off` laut Tabelle Standardwert; `standard` laut Tabelle geänderter Wert (Option im iDrive) | unknown | mittel | unbekannt | Unbekannt |

## 3. Unklar – erst am Fahrzeug bzw. im BimmerCode-Expertenmodus prüfen

Kompatibilität unbekannt oder Verfahren experimentell. Vor einer Planung: Steuergerätevariante/CAFD aus Backup bzw. Diagnose bestätigen.

| Funktion | SG | Parameter (Block) | Werte | BC | Risiko | Kompat. | Nachweis |
|---|---|---|---|---|---|---|---|
| [Geschwindigkeitswarnung (Benutzereinstellung)](#kombispeed_warning) | KOMBI | – | – | unknown | gering | wahrscheinlich kompatibel | Technisch wahrscheinlich |
| [Klimaanlage: Ein/Aus-Zustand speichern](#ihkaac_memory) | IHKA | `MEMORY_OFF`, `OFF_MEMORY` (3002 (IHKA) / 3003 (IHKA_VA02)) | `aktiv` Zustand speichern (Botho: Standard aktiv bei IHKA_VA02); `nicht_aktiv` nicht speichern | standard | gering | unbekannt | Dokumentiert |
| [Klimakompressor nicht automatisch mit AUTO einschalten](#ihkaac_on_with_auto) | IHKA | `AC_NICHT_EIN_BEI_AUTO`, `AC_ON_WITH_AUTO` (3002 (IHKA) / 3003 (IHKA_VA02, IHKA3)) | `AC_NICHT_EIN_BEI_AUTO = Aktiv` A/C nicht mit AUTO (IHKA, ekfxisid F020/F030); `AC_ON_WITH_AUTO = aktiv` Standard – A/C mit AUTO (IHKA_VA02, Botho); `AC_ON_WITH_AUTO = nicht_aktiv` A/C nicht mit AUTO | standard | gering | unbekannt | Dokumentiert |
| [Umluft-Zustand speichern](#ihkarecirc_memory) | IHKA | `MEMORY_UMLUFT` (3002 (IHKA) / 3003 (IHKA_VA02)) | `nicht_aktiv` Standard laut Botho (Umluft wird zurückgesetzt); `aktiv` Umluft speichern | standard | gering | unbekannt | Dokumentiert |
| [Motoröltemperatur anzeigen](#kombioil_temperature) | KOMBI | – | – | unknown | gering | unbekannt | Dokumentiert |
| [Automatische Umluft (AUC) / Umluft-Automatik-Abschaltung](#ihkaauto_recirculation) | IHKA | `UMLUFT_AUTO_AUS`, `AC_ON_WITH_RECIRC` (3003) | `UMLUFT_AUTO_AUS = aktiv` Standard laut Botho (IHKA_VA02); `UMLUFT_AUTO_AUS = nicht_aktiv` Umluft bleibt (Botho); `AC_ON_WITH_RECIRC = nicht_aktiv → aktiv` laut Botho zusammen geändert | standard | gering | unbekannt | Dokumentiert |
| [Datum im Bordcomputer](#kombidate_in_bc) | KOMBI | – | `Active` Datum im BC; `Not active` kein Datum | standard | gering | unbekannt | Dokumentiert |
| [Start-Logo im Kombiinstrument](#kombistart_logo) | KOMBI | `BMW_LOGO`, `MPM_ENABLE`, `MPM_LOGO` (3000) | `AG` Standardwert laut Community-Tabelle (vermutlich Standard-Logo; eine Sammlung behauptet 'Alpina' – widersprüchlich); `MPM` M-Performance-Logo | standard | gering | unbekannt | Dokumentiert |
| [ECO-PRO-Anzeigen (Bonusreichweite) im Kombi](#kombieco_pro_display) | KOMBI | – | – | unknown | gering | unbekannt | Dokumentiert |
| [Lautstärke des Blinkertickens](#kombiturn_signal_tick_volume) | KOMBI | `BLINKER_VOLUME_CONTI` (300B) | `E0, F0, FF, FF` Standard laut Botho; `A0, B0, C0, FF` leiser | expert | gering | unbekannt | Dokumentiert |
| [Fensterheber bei geöffneter Tür weiter bedienbar (hinten)](#remwindow_door_open_rear) | REM | `FH_TUERAUF_STOP_MAUT` (3050) | `aktiv` Standard; `nicht_aktiv` Fenster hinten bei offener Tür bedienbar | expert | gering | unbekannt | Dokumentiert |
| [SPORT+ als zusätzlicher Fahrmodus](#kombisport_plus) | KOMBI | `FDS_MENUE_TEXT_1`, `FDS_MENUE_TEXT_2`, `FDS_MENUE_TEXT_3`, `FDS_MENUE_TEXT_4`, `FDS_MENUE_SIGNAL_1`, `FDS_MENUE_SIGNAL_2`, `FDS_MENUE_SIGNAL_3`, `FDS_MENUE_SIGNAL_4` (3000) | `menue_4` Standard laut Sammlung; `menue_3` SPORT+-Symbol/-Signal laut Sammlung; `Active` BimmerCode-Wert (2 von 2) | standard | mittel | unbekannt | Dokumentiert |
| [Sportanzeigen (Leistung/Drehmoment) im iDrive](#hu_entrysport_displays) | HU_ENTRY | `EFF_DYN_SPORT_CID` (3000) | `nicht_aktiv` Sportanzeigen aus (Standard); `aktiv` Menü Sportanzeigen sichtbar | expert | gering | unbekannt | Experimentell |
| [Komfortblinker: Profil-Standard (1x / 3x / 5x)](#fem_bodycomfort_turn_signal_default) | FEM_BODY | `PIA_DEFAULT_TIPPBLINKEN` (3064) | `00` 1 Zyklus; `01` 3 Zyklen (Standard laut Botho); `02` 5 Zyklen – laut Botho 'Don't work' | expert | gering | unbekannt | Experimentell |
| [Heimleuchten über Funkschlüssel auslösen](#fem_bodyfollow_me_home_remote) | FEM_BODY | `FOLLOWMEHOME_VIA_FFB`, `RC_DEFAULT_IDG_3RD_BUTTON_SHORT` (3060, 30D0) | `nicht_aktiv` Standard; `aktiv` Auslösung per Fernbedienung; `RC_DEFAULT_IDG_3RD_BUTTON_SHORT = 04` Kurzdruck 3. Taste = Follow-me-home (Botho, zusammen mit Panic-Alarm-Konfiguration) | expert | gering | unbekannt | Experimentell |
| [Einheitenwahl für Sportanzeigen (kW/PS, Nm/lb-ft)](#hu_entrysport_displays_unit) | HU_ENTRY | `EFF_DYN_SPORT_UNIT` (3000) | `nicht_aktiv` keine Einheitenwahl; `aktiv` Einheitenwahl im Einstellungsmenü | expert | gering | unbekannt | Experimentell |
| [Manuelle Klimaanlage (IHKR): keine dokumentierten Optionen](#ihkrno_documented_options) | IHKR | – | – | unknown | gering | unbekannt | Unbekannt |
| [MSA-Hinweis 'Auto Start-Stop aus' im Kombi ausblenden](#kombimsa_status_display) | KOMBI | `MSA_VERFUEGBARANZEIGE_ENABLE` (3000) | `aktiv` Standard laut Sammlung; `nicht_aktiv` Hinweis ausgeblendet | expert | gering | unbekannt | Experimentell |
| [Zeigertest / 'Needle Sweep' beim Start](#kombineedle_sweep) | KOMBI | – | – | unknown | gering | unbekannt | Unbekannt |
| [Gong beim Einlegen des Rückwärtsgangs](#kombireverse_gear_chime) | KOMBI | `R_GANG_AKUSTIK_ENABLE` (3000) | `aktiv` Gong aktiv (Standard laut Sammlung); `nicht_aktiv` kein Gong | expert | gering | unbekannt | Experimentell |
| [Schaltpunktanzeige / Ganganzeige (Schaltgetriebe)](#kombishift_point_and_gear_display) | KOMBI | – | – | unknown | gering | unbekannt | Unbekannt |
| [Kombi nachts weiß statt orange](#kombiwhite_night_illumination) | KOMBI | `DIM_NACHT_EIN` (3007) | `werte=32` Standard (laut Tabelle); `werte=FF` weiß bei Nacht | expert | gering | unbekannt | Experimentell |
| [PDC-Lautstärke / Absenkung der Audioquelle](#pdcvolume_and_mute) | REM | – | – | unknown | gering | unbekannt | Unbekannt |
| [Soft-On/Soft-Off (Dimmen) von Fahrlicht](#fem_bodysoft_on_off_main_lights) | FEM_BODY | – | `Soft on / Hard on` nur für Welcome-Light-Bestandteile belegt | unknown | gering | unbekannt | Unbekannt |
| [Checkbox akustische Verriegelungsbestätigung im iDrive](#hu_entryacoustic_lock_checkbox) | HU_ENTRY | `Acoustical_lock_confirm` (3000) | `nicht_aktiv` keine Checkbox; `aktiv` Checkbox im iDrive | unknown | gering | unbekannt | Unbekannt |
| [Klingelton des Telefons (Inband Ringing) / Klingeltonwahl](#hu_entryinband_ringing) | HU_ENTRY | `Inband_ringing`, `INBAND_RINGING` (3003 (HU_CIC) / 3001 (CMB_MEDIA)) | `nicht_aktiv` Fahrzeug-Klingelton; `aktiv` Klingelton des Smartphones | unknown | gering | unbekannt | Unbekannt |
| [Rechtshinweis beim iDrive-Start abschalten](#hu_entrylegal_disclaimer) | HU_ENTRY | `LEGAL_DISCLAIMER_TIME` (3001 EXBOX) | `ld_mit_timeout` Hinweis mit Timeout (Standard bei CIC/NBT); `kein_ld` kein Rechtshinweis | unknown | gering | unbekannt | Unbekannt |
| [Maximale Einschaltlautstärke](#hu_entrymax_volume_startup) | HU_ENTRY | `VOL_MAX_ON` (3002) | `19` 25 % (Standard laut Sammlung, HU_CIC); `32` bis 100 % (laut Sammlung, HU_CIC) | unknown | gering | unbekannt | Unbekannt |
| [Servicehistorie im iDrive](#hu_entryservice_history) | HU_ENTRY | `SERVICE_HISTORY` (3000) | `nicht_aktiv` aus; `aktiv` Servicehistorie anzeigen | unknown | gering | unbekannt | Unbekannt |
| [Farbe der Sportanzeigen (orange → rot/silber)](#hu_entrysport_displays_color) | HU_ENTRY | `M_VEHICLE` (3000 HMI) | `nicht_aktiv` Standardfarbe orange; `aktiv` rot/silber (M-Darstellung) | unknown | gering | unbekannt | Unbekannt |
| [SPORT-Modus im iDrive konfigurierbar](#hu_entrysport_mode_configurable) | HU_ENTRY | `Macro_fds`, `MAKRO_FDS` (3000) | `popup_only` nur Popup; `popup_and_config` Popup + Konfiguration im iDrive | unknown | gering | unbekannt | Unbekannt |
| [Reifendruck/-temperatur im iDrive](#hu_entrytpms_display) | HU_ENTRY | `RDC_SAFETY`, `RDC_DRUCK_TEMP` (3001) | `aktiv` RDC_SAFETY: Druck und Temperatur anzeigen (CIC/NBT); `druck_und_temperatur` RDC_DRUCK_TEMP: Druck + Temperatur (NBT, laut Sammlung) | unknown | gering | unbekannt | Unbekannt |
| [DAB-Radio aktivieren](#hu_entrydab_radio) | HU_ENTRY | `Radio_dab`, `Dab_laendervarianten`, `dab_standard`, `following_available`, `following_dab_fm` (3002) | `aktiv` Radio_dab/following_available aktiv; `ece` Dab_laendervarianten Europa; `dab` dab_standard | expert | mittel | unbekannt | Unbekannt |
| [Entwicklermenü (Build/Datum/Versionen)](#hu_entrydeveloper_menu) | HU_ENTRY | `ENTWICKLER_MENUE` (3000 HMI) | `nicht_aktiv` aus; `aktiv` Entwicklermenü sichtbar | expert | mittel | unbekannt | Unbekannt |
| [Geschwindigkeitsbegrenzer (LIM) über Tempomat](#kombispeed_limiter_lim) | KOMBI | `SLD_ENABLE` (3003) | `aktiv` LIM-Funktion Teil 1 (KOMBI) | expert | hoch | unbekannt | Experimentell |
| [Eigene Software / Apps auf HU_ENTRY](#hu_entrycustom_software_apps) | HU_ENTRY | – | – | unknown | hoch | unbekannt | Unbekannt |

## 4. Informations- und Werkstattthemen (lesend / keine Komfortcodierung)

| Funktion | SG | Parameter (Block) | Werte | BC | Risiko | Kompat. | Nachweis |
|---|---|---|---|---|---|---|---|
| [Motor-Live-Daten](#dmelive_data) | DME | – | – | unknown | gering | wahrscheinlich kompatibel | Dokumentiert |
| [Hardware-Identifikation HU_ENTRY (Radio Professional / HU-B)](#hu_entryplatform_identification) | HU_ENTRY | – | – | unknown | gering | wahrscheinlich kompatibel | Dokumentiert |
| [Kombi-Testmenü (verstecktes Testmenü)](#kombitest_functions) | KOMBI | – | `04` Entsperren mit Quersumme der letzten 5 FIN-Stellen; `08` Kühlmittel-, Außen-, Motoröltemperatur; `18` Korrekturfaktor Verbrauch (verändert Werte – Vorsicht); `19` Software-Reset/RAM reload | unknown | gering | wahrscheinlich kompatibel | Dokumentiert |
| [Batterietyp/-kapazität](#fem_bodybattery_type) | FEM_BODY | – | `20 Ah … 105 Ah AGM` Auswahl in BimmerCode | standard | mittel | wahrscheinlich kompatibel | Dokumentiert |
| [Software-Update gegen 'NO SIGNAL' am CID (I-Stufe)](#hu_entryistufe_update_cid_no_signal) | HU_ENTRY | – | – | unknown | mittel | wahrscheinlich kompatibel | Dokumentiert |
| [Freischaltcodes (FSC/SWT) der Headunit](#hu_entryfsc_enable_codes) | HU_ENTRY | – | – | unknown | mittel | kompatibel | Dokumentiert |

## 5. Nur Dokumentation – sicherheits- oder emissionskritisch (NICHT codieren)

Diese Einträge betreffen Airbag, Bremslicht-/Notbremssignal, Fahrdynamik (ICM/DSC), Lenkung, Motorsteuerung oder Startsperre. Sie werden nur zur Vollständigkeit dokumentiert. F20 Intelligence empfiehlt ausdrücklich keine Änderung.

| Funktion | SG | Parameter (Block) | Werte | BC | Risiko | Kompat. | Nachweis |
|---|---|---|---|---|---|---|---|
| [Fahrmodus beim Start: ECO PRO](#icmstart_in_eco_pro) | ICM | `IcmKod_B_InitEco` (3000) | `nicht_verbaut / 00` Standard – Start in COMFORT; `verbaut / 01` Start in ECO PRO | standard | mittel | wahrscheinlich kompatibel | Dokumentiert |
| [Gurtwarnung (Gong/Anzeige) Fahrer/Beifahrer](#acsmseat_belt_reminder) | ACSM | `SeatBeltReminder_SBR_Fahrer`, `SeatBeltReminder_SBR_Beifahrer`, `SBR_PreWarning_Fahrer`, `SBR_PreWarning_Beifahrer`, `Gurtzustandsanzeige_Fahrer_GWF_GZA_FA`, `Gurtzustandsanzeige_Beifahrer_GWF_GZA_BF` (3000) | `aktiv / 01` Standard; `nicht_aktiv / 00` deaktiviert | standard | sicherheitskritisch | wahrscheinlich kompatibel | Dokumentiert |
| [Gurtwarnung: Dauer](#acsmseat_belt_reminder_duration) | ACSM | `GWF_SBR_WARNDAUER` (3001) | `64 (hex)` 100 s – Standard laut Botho; `0A / 05 (hex)` 10 s / 5 s (Beispiele); `5 … 100 seconds` Auswahl in BimmerCode | standard | sicherheitskritisch | wahrscheinlich kompatibel | Dokumentiert |
| [Bremskraftanzeige: verwendete Heckleuchten](#remess_lights_mapping) | REM | `MAPPING_BRAKEFORCED_L_OUTPUT`, `MAPPING_BRAKEFORCED_R_OUTPUT` (3062) | `bl_l / bl_r` Bremsleuchte links/rechts (Standard laut Botho); `Brake lights / Not active` Auswahl in BimmerCode | standard | sicherheitskritisch | wahrscheinlich kompatibel | Dokumentiert |
| [Bremskraftanzeige / Notbremssignal: Art](#fem_bodyess_type) | FEM_BODY | `ESS_AKTIVIERBARER_AUSGANG` (3060) | `bremslicht_blinkend` Bremsleuchten blinken (Standard laut Botho.xml); `flachenvergroesserung` Flächenvergrößerung (Schreibweise laut F87-Spreadsheet); `Area enlargement / Flashing / Not active` Auswahl in BimmerCode | standard | sicherheitskritisch | wahrscheinlich kompatibel | Dokumentiert |
| [Motorstart ohne Kupplungspedal (Startsperre)](#fem_bodystart_without_clutch) | FEM_BODY | `TCM_STARTLOCK_CLUTCH` (3020) | `01 (Standard, abgeleitet)` Start nur mit getretener Kupplung; `00` Start ohne Kupplung (Bundang_Thunder) | expert | sicherheitskritisch | wahrscheinlich kompatibel | Dokumentiert |
| [SPORT-Modus individuell konfigurierbar (iDrive)](#icmsport_configurable) | ICM | `Macro_fds` (3000 (HU_CIC)) | `popup_only` Standard (HU_CIC); `popup_and_config` Konfiguration im iDrive | standard | mittel | unwahrscheinlich | Unbekannt |
| [Gurtwarnung (nur Dokumentation)](#kombiseatbelt_reminder) | KOMBI | – | – | standard | sicherheitskritisch | unbekannt | Dokumentiert |
| [SPORT+ Fahrmodus freischalten](#icmsport_plus) | ICM | `IcmKod_B_S2TBA`, `IcmKod_B_Sportlenkung` (3000) | `verbaut` laut Quellen Aktivierung (Quellen widersprechen sich, welcher Parameter nötig ist); `Active` BimmerCode 'SPORT+ driving mode (1 of 2)' (ICMQL) + '(2 of 2)' (KOMBI) | standard | sicherheitskritisch | unbekannt | Dokumentiert |
| [DSC/DTC-Entflechtung im Kombi](#kombidsc_off_unbundling) | KOMBI | `DSC_OFF_ENTFLECHTUNG_ENABLE` (3000) | `nicht_aktiv` Standard laut Botho; `aktiv` Entflechtung | expert | sicherheitskritisch | unbekannt | Experimentell |
| [Fahrmodus über Neustart merken](#icmdriving_mode_memory) | ICM | `fesallowmode4lastfunction`, `fesallowmode2lastfunction`, `feslastfunctioninterval` (300A (F15)) | `aktiv` Modus darf gemerkt werden (F15); `feslastfunctioninterval = FF` kein Zurücksetzen (F15) | expert | sicherheitskritisch | unbekannt | Experimentell |
| [Fahrpedalkennlinie je Fahrmodus](#dmethrottle_map_per_mode) | DME | – | – | unknown | sicherheitskritisch | unbekannt | Unbekannt |
| [Elektrische Lenkung (EPS): keine dokumentierten Komfortoptionen](#epsno_user_coding) | EPS | – | – | unknown | sicherheitskritisch | unbekannt | Unbekannt |
| [MSA-Speicher im DME (G-Baureihen)](#dmemsa_in_dme) | DME | `TCM_MSA_MEMORY` (3020 (DME_BAC2)) | `01 / On` Merken (G-Modelle) | expert | hoch | nicht kompatibel | Nicht kompatibel |
| [Launch Control](#dsclaunch_control) | DSC | `C_Funktion_LaunchControl` (3000) | `01` aktiv (DSC_CT01, zusammen mit EGS) | expert | sicherheitskritisch | nicht kompatibel | Nicht kompatibel |

## 6. In Deutschland nicht zulässig

Technisch teils möglich, aber nach deutscher bzw. europäischer Rechtslage unzulässig (Begründung je Eintrag).

| Funktion | SG | Parameter (Block) | Werte | BC | Risiko | Kompat. | Nachweis |
|---|---|---|---|---|---|---|---|
| [Nebelscheinwerfer mit Standlicht](#fem_bodyfog_with_parking_lights) | FEM_BODY | `NSW_EIN_AUF_LDS_STL` (3060) | `00` Standard (laut Botho in Ländern wie USA); `01` Nebelscheinwerfer auch mit Standlicht | standard | mittel | wahrscheinlich kompatibel | Dokumentiert |
| [Tachokorrektur (Vorlauf) der Anzeige](#kombispeed_correction) | KOMBI | `BC_V_KORREKTUR`, `BC_DIGITAL_V_KORREKTUR` (3000) | `aktiv` korrigierte (vorlaufende) Anzeige; `nicht_aktiv` reale Geschwindigkeit (laut Sammlung) | expert | mittel | unbekannt | Experimentell |
| [US-Sidemarker (Blinker als Dauerlicht)](#fem_bodyus_sidemarkers) | FEM_BODY | `MAPPING_SIDEMARKER_L_OUTPUT`, `MAPPING_SIDEMARKER_R_OUTPUT`, `MAPPING_SIDEMARKER_L_FUNCTION`, `MAPPING_SIDEMARKER_R_FUNCTION`, `MAPPING_SIDEMARKER_L_PWM_LEVEL_STANDARD` (3063) | `OUTPUT = off` Standard; `OUTPUT = fra_v_l / fra_v_r` Blinker vorne links/rechts als Sidemarker; `FUNCTION 01 → 04` Funktionszuordnung laut Botho; `Mirror turn signals / Off / Separate lights / Turn signals` Auswahl in BimmerCode | standard | hoch | wahrscheinlich kompatibel | Dokumentiert |
| [Notbremssignal: Verzögerungsschwelle](#fem_bodyess_activation_decel) | FEM_BODY | `ESS_AKTIVIERUNG_REALE_VERZ`, `ESS_DEAKTIVIERUNG_REALE_VERZ` (3060) | `0E (hex)` 7 m/s² – Standard laut Botho.xml (Einheit vermutlich 0,5 m/s²); `06 (hex)` 3 m/s² (Beispiel Botho); `Weak (5 m/s²) / Medium (7 m/s²) / Hard (8 m/s²)` Auswahl in BimmerCode | standard | sicherheitskritisch | wahrscheinlich kompatibel | Dokumentiert |
| [Notbremssignal: Aktivierungsgeschwindigkeit](#fem_bodyess_activation_speed) | FEM_BODY | `ESS_AKTIVIERUNG_GESCHW` (3060) | `32 (hex)` 50 km/h – Standard laut Botho.xml; `14 (hex)` 20 km/h (Beispiel Botho); `0A (hex)` 10 km/h (Beispiel ekfxisid); `5 … 50 km/h` Auswahl in BimmerCode | standard | sicherheitskritisch | wahrscheinlich kompatibel | Dokumentiert |
| [Notbremssignal: Blinkfrequenz](#remess_flash_frequency) | REM | `ESS_BLINKFREQ_1`, `ESS_BLINKFREQ_2` (3064) | `03` Standard laut Botho.xml (BimmerCode: 3 times per second); `05` erhöht (BimmerCode: 5 times per second) | standard | sicherheitskritisch | wahrscheinlich kompatibel | Dokumentiert |
| [Video über USB und zusätzliche Codecs](#hu_entryvideo_usb_codecs) | HU_ENTRY | `ENT_CODEC_OGG`, `ENT_CODEC_XVID`, `ENT_CODEC_VCD`, `API_USB_VIDEO` (3000 HMI) | `aktiv` Codec aktiv (NBT); `both` API_USB_VIDEO: Video über USB (NBT) | unknown | gering | nicht kompatibel | Nicht kompatibel |
| [Video in Motion (Video-Sperre während der Fahrt)](#hu_entryvideo_in_motion) | HU_ENTRY | `SPEEDLOCK_X_KMH_MIN`, `SPEEDLOCK_X_KMH_MAX`, `VIDEO_NUR_MIT_HANDBREMSE` (3000 HMI) | `werte=FF` Geschwindigkeitssperre aufgehoben (CIC/NBT) | unknown | mittel | nicht kompatibel | Nicht kompatibel |

## 7. Nicht möglich bei diesem Fahrzeug (fehlende Hardware / HU_ENTRY)

| Funktion | SG | Parameter (Block) | Werte | BC | Risiko | Kompat. | Nachweis |
|---|---|---|---|---|---|---|---|
| [Sitzheizung: Zustand speichern](#cfasseat_heating_memory) | CFAS | – | `15 minutes / 24 hours / Do not save / Unlimited` Auswahl in BimmerCode | standard | gering | unwahrscheinlich | Dokumentiert |
| [Spiegel beim Komfortschließen an-/ausklappen](#fem_bodymirror_fold_comfort) | FEM_BODY | `ASP_BEIKLAPPEN`, `ASP_BEIKLAPPEN_BEI_KOMFORTSCHLIESSEN`, `ASP_AUSKLAPPEN_NACH_KOMFORTSCHLIESSEN` (3110) | `ASP_BEIKLAPPEN = aktiv` Anklappmotor verbaut; `ASP_BEIKLAPPEN_BEI_KOMFORTSCHLIESSEN = aktiv` anklappen beim Komfortschließen; `ASP_AUSKLAPPEN_NACH_KOMFORTSCHLIESSEN = aktiv` ausklappen beim Komfortöffnen | standard | gering | unwahrscheinlich | Dokumentiert |
| [Bluetooth-Audio-Streaming](#hu_entrybluetooth_audio_streaming) | HU_ENTRY | – | – | unknown | gering | unwahrscheinlich | Dokumentiert |
| [Ambientelicht: Helligkeit vom Kombi entkoppeln / Helligkeit / Welcome](#fem_bodyambient_light_decoupling) | FEM_BODY | `AMBIENTE_NACHFUEHRUNG`, `AMBIENTE_HELLIGKEIT`, `WELCOME_AMBIENTE` (3070) | `AMBIENTE_NACHFUEHRUNG = aktiv` Standard – folgt Kombi-Helligkeit; `AMBIENTE_NACHFUEHRUNG = nicht_aktiv` entkoppelt; `WELCOME_AMBIENTE = aktiv` Ambiente beim Entriegeln | standard | gering | unwahrscheinlich | Dokumentiert |
| [Türgriffbeleuchtung beim Rückwärtsgang](#fem_bodydoor_handle_light_reverse) | FEM_BODY | `OVT_BEI_RUECKFAHRLICHT` (3070) | `nicht_aktiv` Standard; `aktiv` an | standard | gering | unwahrscheinlich | Dokumentiert |
| [Scheinwerferreinigungsanlage (SRA): Aktivierung/Parameter](#fem_bodyheadlight_washer) | FEM_BODY | `WW_SCHEINWERFERREINIGUNG`, `WW_ANZAHL_SPRITZIMPULSE_SRA`, `WW_SRA_SPERRZEIT`, `WW_ANZAHL_WASCHBET_ZUR_SRA` (3080) | `WW_SCHEINWERFERREINIGUNG = aktiv / nicht_aktiv` SRA an/aus; `WW_ANZAHL_SPRITZIMPULSE_SRA = 02` 2 Impulse – Standard; `WW_SRA_SPERRZEIT = 0A` 10 min – Standard; `WW_ANZAHL_WASCHBET_ZUR_SRA = 0A` jede 10. Wäsche – Standard | standard | gering | unwahrscheinlich | Dokumentiert |
| [Beifahrerspiegel absenken beim Rückwärtsgang (Bordsteinautomatik)](#fem_bodymirror_tilt_reverse) | FEM_BODY | `ASP_BORDSTEINAUTOMATIK_DELTA` (3110) | `3B (hex)` Standard laut Botho; `46 / 5A / 1E (hex)` Beispiele aus Botho/Kip/ekfxisid; `10 % … 100 %` Auswahl in BimmerCode ('Automatic mirror tilt value') | standard | gering | unwahrscheinlich | Dokumentiert |
| [Maximalwert der Verbrauchsanzeige](#kombifuel_consumption_display_max) | KOMBI | – | `20 l/100km` Skalenende 20 l/100 km; `30 l/100km` Skalenende 30 l/100 km | standard | gering | unwahrscheinlich | Dokumentiert |
| [M-Performance-Logo unten rechts im Kombi](#kombim_performance_logo) | KOMBI | – | `Not active` kein Logo; `135i` Beispielwert (Modellschriftzug) | standard | gering | unwahrscheinlich | Dokumentiert |
| [Akustische Ver-/Entriegelungsquittierung](#fzdacoustic_lock_confirmation) | FZD | `Akustische Quittierung Schaerfen`, `Akustische Quittierung Entschaerfen`, `Buzzer level high`, `Buzzer level low`, `Buzzer duration`, `Buzzer frequency` (3001, 3002) | `Akustische Quittierung Schaerfen = 00 / 01` aus (Standard laut Botho) / an; `Buzzer duration = 05/0A/0F/14` kurz / normal (Standard) / lang / sehr lang; `Active / Not active` Auswahl in BimmerCode | standard | gering | unwahrscheinlich | Dokumentiert |
| [Hintergrundfarbe der Skalen (Orange/Grau)](#kombibackground_color) | KOMBI | `HINTERGRUND_FARBE_TAG`, `HINTERGRUND_FARBE_NACHT` (3001) | `Orange` Standard; `Orange/Grau` hell-orange/graue Hintergrundlinien | expert | gering | unwahrscheinlich | Dokumentiert |
| [Spiegel: Geschwindigkeitsschwellen An-/Ausklappen](#fem_bodymirror_fold_speed) | FEM_BODY | `ASP_MAX_GESCHWINDIGKEIT_BEIKLAPPEN`, `ASP_GESCHWINDIGKEIT_AUTO_AUSKLAPPEN` (3110) | `ASP_MAX_GESCHWINDIGKEIT_BEIKLAPPEN = 14 (hex)` 20 km/h – Standard laut Botho; `ASP_GESCHWINDIGKEIT_AUTO_AUSKLAPPEN = 28 (hex)` 40 km/h – Standard; `5 … 50 km/h` Auswahl in BimmerCode | standard | mittel | unwahrscheinlich | Dokumentiert |
| [Startanimation / Logo der Headunit](#hu_entrystartup_animation) | HU_ENTRY | `STARTUP_EMBLEM` (3001) | `variant_00` BMW ConnectedDrive (Standard; ebenso 02–06); `variant_01` BMW M; `variant_07` weißes BMW-Logo; `variant_08` braunes BMW-Logo (wie HU_CIC) | unknown | gering | unwahrscheinlich | Unbekannt |
| [Warngong-Variante und Lautstärke-Popup](#hu_entrywarning_chime_volume_popup) | HU_ENTRY | – | – | unknown | gering | unwahrscheinlich | Unbekannt |
| [TFL-Ein/Aus im iDrive-Menü](#hu_entrydrl_menu) | HU_ENTRY | `Daydriving_light` (3000 (HU_CIC)) | `Perm_off` Standard (kein Menüpunkt) – HU_CIC; `standard` Menüpunkt verfügbar – HU_CIC | standard | mittel | unwahrscheinlich | Unbekannt |
| [SMS vollständig anzeigen](#hu_entryfull_text_messages) | HU_ENTRY | `PIM_Driving_Text` (3003) | `up_to_three_lines` max. drei Zeilen während der Fahrt; `whole_text` vollständiger Text | unknown | mittel | unwahrscheinlich | Unbekannt |
| [Office- und Servicemeldungen während der Fahrt lesbar](#hu_entryspeedlock_office_service_messages) | HU_ENTRY | `SERVICES_MESSAGES_SPEEDLOCK_CONDITION`, `OFFICE_MESSAGES_SPEEDLOCK_CONDITION` (3000 HMI) | `none` keine Sperre während der Fahrt | unknown | mittel | unwahrscheinlich | Unbekannt |
| [Apple CarPlay](#hu_entrycarplay) | HU_ENTRY | – | – | unknown | gering | nicht kompatibel | Nicht kompatibel |

---

## Details und Quellen

### Automatisch verriegeln nach Anfahren: Geschwindigkeitsschwelle

<a id="fem_bodyauto_lock_speed"></a>`fem_body.auto_lock_speed` · Bereich: 1 · SG **FEM_BODY** · Kategorie Verriegelung

Geschwindigkeit, ab der bei aktivierter Funktion 'Verriegeln nach Losfahren' verriegelt wird.

- **Parameter:** `CLM_SPEED_LIMIT_PIA_AUTO_LOCK` (3040)
- **Werte:** `wert_04` = ca. 16 km/h – Standard laut Botho; `wert_03` = ca. 8 km/h (Botho); `0A (hex)` = 10 km/h (ekfxisid/otakar – andere Kodierungsdarstellung)
- **Hardware:** Keine.
- **Software:** Parametername/Wertebezeichnung können je nach I-Stufe/CAFD-Version abweichen (Quellen beziehen sich auf CAFD 00000794 FEM_BODY, Serie F020/F030). Vor dem Codieren Ist-Wert in BimmerCode auslesen und Backup sichern. Die Funktion selbst wird im Fahrzeugmenü/PIA aktiviert (für HU_ENTRY wahrscheinlich, nicht verifiziert).
- **Aufwand / Risiko / Nutzen:** gering / gering / gering
- **Kompatibilität (dein F20):** wahrscheinlich kompatibel · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Hinweise:** Werte-Darstellung je CAFD unterschiedlich (wert_xx vs. hex) → Auswahlliste in BimmerCode Expert Mode prüfen.
- **Quellen:** <https://github.com/packetpilot/bmw-f/blob/master/cheats/Botho.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/ekfxisid.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/otakar.xml>

### Heckklappe per Fernbedienung: Öffnungsverzögerung

<a id="fem_bodybootlid_delay"></a>`fem_body.bootlid_delay` · Bereich: 1 · SG **FEM_BODY** · Kategorie Verriegelung

Verzögerung/Haltezeit beim Öffnen der Heckklappe mit der Fernbedienung.

- **BimmerCode:** Boot lid opening delay (standard)
- **Parameter:** `CLM_TIME_DELAY_BOOTLID`, `RC_TIME_DELAY_BOOTLID` (3040, 30D0)
- **Werte:** `CLM_TIME_DELAY_BOOTLID = wert_02` = 0,3 s – Standard laut Botho; `CLM_TIME_DELAY_BOOTLID = wert_01` = 0,1 s; `RC_TIME_DELAY_BOOTLID = 05 (hex)` = Standard laut Botho; `0.5 s / 1 s / 5 s / 10 s / No delay` = Auswahl in BimmerCode
- **Hardware:** Keine (manuelle Heckklappe).
- **Software:** Parametername/Wertebezeichnung können je nach I-Stufe/CAFD-Version abweichen (Quellen beziehen sich auf CAFD 00000794 FEM_BODY, Serie F020/F030). Vor dem Codieren Ist-Wert in BimmerCode auslesen und Backup sichern.
- **Aufwand / Risiko / Nutzen:** gering / gering / gering
- **Kompatibilität (dein F20):** wahrscheinlich kompatibel · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Hinweise:** Welcher der beiden Parameter der BimmerCode-Option entspricht, ist nicht belegt.
- **Quellen:** <https://bimmercode.app/cars/f20/> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Botho.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Almaretto.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/otakar.xml>

### Komfortöffnen/-schließen: Verzögerung

<a id="fem_bodycomfort_open_close_delay"></a>`fem_body.comfort_open_close_delay` · Bereich: 1 · SG **FEM_BODY** · Kategorie Fenster

Haltezeit der Fernbedienungstaste bis zum Start der Komfortfunktion.

- **BimmerCode:** Convenient opening delay / Convenient closing delay (standard)
- **Parameter:** `KOMFORT_OEFFNEN`, `KOMFORT_SCHLIESSEN` (3053)
- **Werte:** `KOMFORT_OEFFNEN = 19 (hex)` = 2,5 s – Standard laut Botho/Kip; `KOMFORT_OEFFNEN = 14 (hex)` = 2,0 s; `KOMFORT_SCHLIESSEN = 0F (hex)` = 1,5 s – Standard; `KOMFORT_SCHLIESSEN = 0A / 00` = 1,0 s / keine Verzögerung
- **Hardware:** Keine.
- **Software:** Parametername/Wertebezeichnung können je nach I-Stufe/CAFD-Version abweichen (Quellen beziehen sich auf CAFD 00000794 FEM_BODY, Serie F020/F030). Vor dem Codieren Ist-Wert in BimmerCode auslesen und Backup sichern.
- **Aufwand / Risiko / Nutzen:** gering / gering / gering
- **Kompatibilität (dein F20):** wahrscheinlich kompatibel · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Hinweise:** Einheit 0,1 s. Zu kurze Verzögerung kann ungewolltes Öffnen auslösen.
- **Quellen:** <https://bimmercode.app/cars/f20/> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Botho.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Kip_M3.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Almaretto.xml>

### Komfortöffnen per Fernbedienung (Fenster/SHD)

<a id="fem_bodycomfort_open_remote"></a>`fem_body.comfort_open_remote` · Bereich: 1 · SG **FEM_BODY** · Kategorie Fenster

Gedrückthalten der Entriegeln-Taste öffnet Fenster (und ggf. Schiebedach, klappt Spiegel aus).

- **BimmerCode:** Convenient opening / Convenient opening with remote control (standard)
- **Parameter:** `KOMFORTOEFFNUNG_FB`, `KOMFORTOEFFNUNG` (3053)
- **Werte:** `aktiv` = Komfortöffnen per Funkschlüssel; `nicht_aktiv` = aus; `Active / Not active` = BimmerCode 'Convenient opening' bzw. '… with remote control'
- **Hardware:** Elektrische Fensterheber (vorhanden).
- **Software:** Parametername/Wertebezeichnung können je nach I-Stufe/CAFD-Version abweichen (Quellen beziehen sich auf CAFD 00000794 FEM_BODY, Serie F020/F030). Vor dem Codieren Ist-Wert in BimmerCode auslesen und Backup sichern.
- **Aufwand / Risiko / Nutzen:** gering / gering / hoch
- **Kompatibilität (dein F20):** wahrscheinlich kompatibel · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Hinweise:** Bei EU-Fahrzeugen ggf. bereits aktiv – Ist-Wert prüfen. motor-talk-Quelle nur als Such-Snippet gelesen (Seite blockiert).
- **Quellen:** <https://bimmercode.app/cars/f20/> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Kip_M3.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Almaretto.xml> · <https://docs.google.com/spreadsheets/d/1TjoUmnkFYbzdcL8v2DF5fcMixHXSVWRexVV1g2ybG14/edit> · <https://www.motor-talk.de/forum/start-des-ersten-codierens-einstiegsfragen-t7071093.html>

### Komfortblinker: Anzahl Blinkzyklen (3 → 5)

<a id="fem_bodycomfort_turn_signal_count"></a>`fem_body.comfort_turn_signal_count` · Bereich: 1 · SG **FEM_BODY** · Kategorie Beleuchtung

Anzahl der Blinkzyklen beim Antippen des Blinkerhebels.

- **Parameter:** `BLINKZYKLEN_ANZAHL_TIPP` (3060)
- **Werte:** `02` = 3 Blinkzyklen (Standard laut Spreadsheet F3x; Botho nennt 00); `04` = 5 Blinkzyklen (Wert = Anzahl − 1)
- **Hardware:** Keine.
- **Software:** Laut Botho.xml und Almaretto.xml nur bis I-Stufe/Datenstand 3.61.x wirksam (ab 3.61.x stattdessen PIA_DEFAULT_TIPPBLINKEN, dort als 'Don't work' markiert). Ein Fahrzeug von 01/2012 ohne Software-Update hat sehr wahrscheinlich einen älteren Stand.
- **Aufwand / Risiko / Nutzen:** gering / gering / hoch
- **Kompatibilität (dein F20):** wahrscheinlich kompatibel · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Recht:** ECE R48 (Rev. 7) enthält keine Vorgabe zur Zyklenzahl beim Tippblinken; keine Rechtsproblematik bekannt.
- **Hinweise:** Nicht in der offiziellen BimmerCode-F20-Liste → Expert Mode im FEM.
- **Quellen:** <https://github.com/packetpilot/bmw-f/blob/master/cheats/Botho.xml> · <https://docs.google.com/spreadsheets/d/16O4RKIMekWFCs5jPW3T_7li0yIEvgZfFI0u3l0RmSwU/pubhtml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Bundang_Thunder.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Almaretto.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/otakar.xml>

### Coming Home (Heimleuchten): Standarddauer

<a id="fem_bodycoming_home_duration"></a>`fem_body.coming_home_duration` · Bereich: 1 · SG **FEM_BODY** · Kategorie Beleuchtung

Vorgabewert der Heimleuchten-Dauer (Follow-me-home), die nach dem Abstellen per Lichthupe ausgelöst wird.

- **Parameter:** `PIA_DEFAULT_FMH` (3064)
- **Werte:** `14 (hex)` = 20 s – Standard laut Botho.xml; `1E (hex)` = 30 s
- **Hardware:** Keine.
- **Software:** Parametername/Wertebezeichnung können je nach I-Stufe/CAFD-Version abweichen (Quellen beziehen sich auf CAFD 00000794 FEM_BODY, Serie F020/F030). Vor dem Codieren Ist-Wert in BimmerCode auslesen und Backup sichern. 'PIA'-Werte sind Vorgaben für das Fahrerprofil; die Dauer ist bei vielen F-Modellen auch im iDrive-Menü einstellbar (für HU_ENTRY nicht verifiziert).
- **Aufwand / Risiko / Nutzen:** gering / gering / mittel
- **Kompatibilität (dein F20):** wahrscheinlich kompatibel · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Hinweise:** Nicht in der offiziellen BimmerCode-F20-Liste → nur über Expert Mode.
- **Quellen:** <https://github.com/packetpilot/bmw-f/blob/master/cheats/Botho.xml>

### Warnblinker nach Notbremsung

<a id="fem_bodyhazard_after_emergency_braking"></a>`fem_body.hazard_after_emergency_braking` · Bereich: 1 · SG **FEM_BODY** · Kategorie Sicherheit

Warnblinkanlage schaltet nach einer Notbremsung (bis zum Stillstand) automatisch ein.

- **BimmerCode:** Hazard warning signal after emergency braking (standard)
- **Parameter:** `WB_GB_ENABLE`, `WB_GB_GEFAHRENWERT_MIN` (3060)
- **Werte:** `aktiv / 01` = Warnblinker nach Gefahrenbremsung; `nicht_aktiv` = aus; `Active / Not active` = Auswahl in BimmerCode
- **Hardware:** Keine.
- **Software:** Parametername/Wertebezeichnung können je nach I-Stufe/CAFD-Version abweichen (Quellen beziehen sich auf CAFD 00000794 FEM_BODY, Serie F020/F030). Vor dem Codieren Ist-Wert in BimmerCode auslesen und Backup sichern.
- **Aufwand / Risiko / Nutzen:** gering / mittel / mittel
- **Kompatibilität (dein F20):** wahrscheinlich kompatibel · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Recht:** ECE R48 6.6.7.2 erlaubt die automatische Aktivierung der Warnblinkanlage nach Deaktivierung des Notbremssignals (manuell abschaltbar) → grundsätzlich konform.
- **Hinweise:** Werkseinstellung für DE unbekannt; Ist-Wert auslesen.
- **Quellen:** <https://bimmercode.app/cars/f20/> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Bundang_Thunder.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Kip_M3.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/ekfxisid.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/packetpilot.xml>

### Hupsignal beim Verriegeln mit laufendem Motor

<a id="fem_bodyhorn_lock_engine_running"></a>`fem_body.horn_lock_engine_running` · Bereich: 1 · SG **FEM_BODY** · Kategorie Verriegelung

Warnhupe, wenn bei laufendem Motor von außen verriegelt wird.

- **BimmerCode:** Horn signal when locking the car with engine running (standard)
- **Parameter:** `CLM_HORN_AT_SECURE` (3040)
- **Werte:** `aktiv` = Standard laut Botho; `nicht_aktiv` = aus
- **Hardware:** Keine.
- **Software:** Parametername/Wertebezeichnung können je nach I-Stufe/CAFD-Version abweichen (Quellen beziehen sich auf CAFD 00000794 FEM_BODY, Serie F020/F030). Vor dem Codieren Ist-Wert in BimmerCode auslesen und Backup sichern.
- **Aufwand / Risiko / Nutzen:** gering / gering / gering
- **Kompatibilität (dein F20):** wahrscheinlich kompatibel · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Hinweise:** Warnfunktion – Deaktivieren nicht empfohlen.
- **Quellen:** <https://bimmercode.app/cars/f20/> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Botho.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Bundang_Thunder.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Kip_M3.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/ekfxisid.xml>

### Innenlicht: Nachleuchtdauer beim Ver-/Entriegeln

<a id="fem_bodyinterior_light_duration"></a>`fem_body.interior_light_duration` · Bereich: 1 · SG **FEM_BODY** · Kategorie Beleuchtung

Einschaltbegrenzung der Innenbeleuchtung nach Verriegeln bzw. Entriegeln.

- **Parameter:** `IB_EINSCHALT_BEGR_LOK`, `IB_EINSCHALT_BEGR_ULOK` (3070)
- **Werte:** `IB_EINSCHALT_BEGR_LOK = 08` = 8 s nach Verriegeln (Standard laut Botho); `IB_EINSCHALT_BEGR_ULOK = 14 (hex)` = 20 s nach Entriegeln (Standard laut Botho); `3C (hex)` = 60 s
- **Hardware:** Keine.
- **Software:** Parametername/Wertebezeichnung können je nach I-Stufe/CAFD-Version abweichen (Quellen beziehen sich auf CAFD 00000794 FEM_BODY, Serie F020/F030). Vor dem Codieren Ist-Wert in BimmerCode auslesen und Backup sichern.
- **Aufwand / Risiko / Nutzen:** gering / gering / gering
- **Kompatibilität (dein F20):** wahrscheinlich kompatibel · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Hinweise:** Botho ordnet die Parameter der Ambientebeleuchtung zu, das Spreadsheet der Innenbeleuchtung ('IB'); Wirkung am Fahrzeug prüfen. Höhere Werte = mehr Ruhestrom.
- **Quellen:** <https://github.com/packetpilot/bmw-f/blob/master/cheats/Botho.xml> · <https://docs.google.com/spreadsheets/d/16O4RKIMekWFCs5jPW3T_7li0yIEvgZfFI0u3l0RmSwU/pubhtml>

### Optische Quittierung: Blinkanzahl beim Ver-/Entriegeln

<a id="fem_bodylock_unlock_flash_count"></a>`fem_body.lock_unlock_flash_count` · Bereich: 1 · SG **FEM_BODY** · Kategorie Verriegelung

Anzahl der Blinkimpulse beim Verriegeln (Sichern) und Entriegeln (Entschärfen).

- **BimmerCode:** Turn signals flashing on locking / Turn signals flashing on unlocking (standard)
- **Parameter:** `QUITTBLK_SICHERN_ANZAHL`, `QUITTBLK_ENTSCHAERFEN_ANZAHL` (3060)
- **Werte:** `QUITTBLK_SICHERN_ANZAHL = 01` = 1x beim Verriegeln (Standard laut Botho); `QUITTBLK_ENTSCHAERFEN_ANZAHL = 02` = 2x beim Entriegeln (Standard laut Botho); `1 time / 2 times / 3 times / Off` = Auswahl in BimmerCode
- **Hardware:** Keine.
- **Software:** Parametername/Wertebezeichnung können je nach I-Stufe/CAFD-Version abweichen (Quellen beziehen sich auf CAFD 00000794 FEM_BODY, Serie F020/F030). Vor dem Codieren Ist-Wert in BimmerCode auslesen und Backup sichern.
- **Aufwand / Risiko / Nutzen:** gering / gering / mittel
- **Kompatibilität (dein F20):** wahrscheinlich kompatibel · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Quellen:** <https://bimmercode.app/cars/f20/> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Botho.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/otakar.xml>

### Radio/iDrive beim Öffnen der Fahrertür ausschalten

<a id="fem_bodyradio_off_driver_door"></a>`fem_body.radio_off_driver_door` · Bereich: 1 · SG **FEM_BODY** · Kategorie Audio

Klemme-R-Logik: Infotainment schaltet nach Motor-Aus beim Öffnen der Fahrertür ab (bzw. bleibt an).

- **BimmerCode:** Shut off iDrive system when driver door is opened (standard)
- **Parameter:** `TCM_LOGIC_R_OFF_DOOR` (3020)
- **Werte:** `nicht_aktiv` = Standard laut Botho; `aktiv` = aus beim Öffnen der Fahrertür
- **Hardware:** Keine (FEM-Logik, unabhängig von der Head-Unit-Variante).
- **Software:** Parametername/Wertebezeichnung können je nach I-Stufe/CAFD-Version abweichen (Quellen beziehen sich auf CAFD 00000794 FEM_BODY, Serie F020/F030). Vor dem Codieren Ist-Wert in BimmerCode auslesen und Backup sichern.
- **Aufwand / Risiko / Nutzen:** gering / gering / mittel
- **Kompatibilität (dein F20):** wahrscheinlich kompatibel · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Hinweise:** Ruhestrom beachten.
- **Quellen:** <https://bimmercode.app/cars/f20/> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Botho.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Bundang_Thunder.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Kip_M3.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/FDLCodes.xml>

### Heckwischer beim Rückwärtsgang

<a id="fem_bodyrear_wiper_reverse"></a>`fem_body.rear_wiper_reverse` · Bereich: 1 · SG **FEM_BODY** · Kategorie Wischer

Heckwischer wischt automatisch beim Einlegen des Rückwärtsgangs (bei laufendem Frontwischer).

- **BimmerCode:** Automatic rear wiper in reverse (standard)
- **Parameter:** `WW_HECKWISCHER_EIN_RUECKWGANG` (3080)
- **Werte:** `aktiv` = Standard laut Botho; `nicht_aktiv` = aus
- **Hardware:** Heckwischer (Serie beim F20).
- **Software:** Parametername/Wertebezeichnung können je nach I-Stufe/CAFD-Version abweichen (Quellen beziehen sich auf CAFD 00000794 FEM_BODY, Serie F020/F030). Vor dem Codieren Ist-Wert in BimmerCode auslesen und Backup sichern.
- **Aufwand / Risiko / Nutzen:** gering / gering / gering
- **Kompatibilität (dein F20):** wahrscheinlich kompatibel · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Quellen:** <https://bimmercode.app/cars/f20/> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Botho.xml>

### Wiederverriegelung, wenn nach Entriegeln keine Tür geöffnet wird

<a id="fem_bodyrelock_timeout"></a>`fem_body.relock_timeout` · Bereich: 1 · SG **FEM_BODY** · Kategorie Verriegelung

Zeit bis zur automatischen Wiederverriegelung.

- **BimmerCode:** Time until automatic lock (standard)
- **Parameter:** `CLM_TIME_PIA_LOCK_AT_TIMEOUT` (3040)
- **Werte:** `0C (hex)` = 120 s – Standard laut Botho (Einheit 10 s); `03 (hex)` = 30 s; `12 (hex)` = 180 s (otakar); `10 s … 10 min` = Auswahl in BimmerCode
- **Hardware:** Keine.
- **Software:** Parametername/Wertebezeichnung können je nach I-Stufe/CAFD-Version abweichen (Quellen beziehen sich auf CAFD 00000794 FEM_BODY, Serie F020/F030). Vor dem Codieren Ist-Wert in BimmerCode auslesen und Backup sichern.
- **Aufwand / Risiko / Nutzen:** gering / gering / gering
- **Kompatibilität (dein F20):** wahrscheinlich kompatibel · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Quellen:** <https://bimmercode.app/cars/f20/> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Botho.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/ekfxisid.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/otakar.xml>

### Regen-/Lichtsensor: Empfindlichkeit (Lichtautomatik)

<a id="fem_bodyrls_sensitivity"></a>`fem_body.rls_sensitivity` · Bereich: 1 · SG **FEM_BODY** · Kategorie Beleuchtung

Schwellwertsatz des Regen-Licht-Sensors für Fahrlicht-Automatik (BimmerCode: wirkt auf Wischer- und Lichtautomatik).

- **BimmerCode:** Rain-light-sensor sensitivity (standard)
- **Parameter:** `RLS_DEF_FLC_SCHWELLWERT_SATZ` (3130)
- **Werte:** `00` = Standard laut Botho.xml; `03` = weniger empfindlich (Botho); `unempfindlich` = Wertebezeichnung in Almaretto/Kip; `Insensitive / Normal / Sensitive / Very sensitive` = Auswahl in BimmerCode
- **Hardware:** Regen-/Lichtsensor (laut Fahrzeugbeschreibung vorhanden).
- **Software:** Parametername/Wertebezeichnung können je nach I-Stufe/CAFD-Version abweichen (Quellen beziehen sich auf CAFD 00000794 FEM_BODY, Serie F020/F030). Vor dem Codieren Ist-Wert in BimmerCode auslesen und Backup sichern.
- **Aufwand / Risiko / Nutzen:** gering / gering / mittel
- **Kompatibilität (dein F20):** wahrscheinlich kompatibel · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Recht:** Fahrer bleibt nach § 17 Abs. 1 StVO für rechtzeitiges Einschalten des Lichts verantwortlich.
- **Hinweise:** Hex-Werte und Klartextwerte widersprechen sich zwischen Quellen (otakar: '02 = highest sensitivity') → BimmerCode-Standardmodus nutzen.
- **Quellen:** <https://bimmercode.app/cars/f20/> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Botho.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Almaretto.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Kip_M3.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/otakar.xml>

### Sitzheizung: Temperatur der Stufen 1–3 (vorn)

<a id="fem_bodyseat_heating_temperatures"></a>`fem_body.seat_heating_temperatures` · Bereich: 1 · SG **FEM_BODY** · Kategorie Komfort

Zieltemperatur je Sitzheizungsstufe für Sitzfläche und Lehne.

- **BimmerCode:** Front seats temperature level 1/2/3 / Front backrests temperature level 1/2/3 (standard)
- **Parameter:** –
- **Werte:** `Front seats level 1: 30–34 °C` = BimmerCode; `Front seats level 2: 35–40 °C` = BimmerCode; `Front seats level 3: 41–46 °C` = BimmerCode; `Front backrests level 1/2/3: 30–35 / 36–41 / 42–47 °C` = BimmerCode
- **Hardware:** Sitzheizung vorn (vorhanden).
- **Software:** FEM_01.
- **Aufwand / Risiko / Nutzen:** gering / gering / mittel
- **Kompatibilität (dein F20):** wahrscheinlich kompatibel · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Hinweise:** E-Sys-Parameternamen nicht belegt. Hohe Stufen: Verbrennungsrisiko bei längerer Nutzung beachten.
- **Quellen:** <https://bimmercode.app/cars/f20/>

### Blinkquittierung beim Öffnen der Heckklappe

<a id="fem_bodytailgate_open_flash"></a>`fem_body.tailgate_open_flash` · Bereich: 1 · SG **FEM_BODY** · Kategorie Verriegelung

Anzahl der Blinkimpulse beim Öffnen der Heckklappe (Botho: einfach statt doppelt).

- **Parameter:** `HECKKLAPPE_REVERSIEREN_BLINKEN` (3060)
- **Werte:** `01` = Standard (doppelt laut Botho); `00` = einfach
- **Hardware:** Keine.
- **Software:** Parametername/Wertebezeichnung können je nach I-Stufe/CAFD-Version abweichen (Quellen beziehen sich auf CAFD 00000794 FEM_BODY, Serie F020/F030). Vor dem Codieren Ist-Wert in BimmerCode auslesen und Backup sichern.
- **Aufwand / Risiko / Nutzen:** gering / gering / gering
- **Kompatibilität (dein F20):** wahrscheinlich kompatibel · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Hinweise:** Nur eine Quelle.
- **Quellen:** <https://github.com/packetpilot/bmw-f/blob/master/cheats/Botho.xml>

### Entriegeln bei 'Zündung aus' (nach Auto-Lock)

<a id="fem_bodyunlock_on_ignition_off"></a>`fem_body.unlock_on_ignition_off` · Bereich: 1 · SG **FEM_BODY** · Kategorie Verriegelung

Nach automatischer Verriegelung werden beim Abstellen alle Türen entriegelt.

- **BimmerCode:** Unlock doors automatically (standard)
- **Parameter:** `CLM_UNLOCK_KL15OFF_AFTER_PIA_AUTO_LOCK` (3040)
- **Werte:** `aktiv` = Standard laut Botho/Spreadsheet F3x; `nicht_aktiv` = bleibt verriegelt
- **Hardware:** Keine.
- **Software:** Parametername/Wertebezeichnung können je nach I-Stufe/CAFD-Version abweichen (Quellen beziehen sich auf CAFD 00000794 FEM_BODY, Serie F020/F030). Vor dem Codieren Ist-Wert in BimmerCode auslesen und Backup sichern. Wirkt nur, wenn 'Verriegeln nach Losfahren' aktiv ist.
- **Aufwand / Risiko / Nutzen:** gering / gering / mittel
- **Kompatibilität (dein F20):** wahrscheinlich kompatibel · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Hinweise:** 'Entriegeln bei Schlüssel abziehen' ist beim F20 (Start-Stop-Taster, kein Schlüsselschacht) nicht anwendbar.
- **Quellen:** <https://bimmercode.app/cars/f20/> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Botho.xml> · <https://docs.google.com/spreadsheets/d/16O4RKIMekWFCs5jPW3T_7li0yIEvgZfFI0u3l0RmSwU/pubhtml> · <https://docs.google.com/spreadsheets/d/1TjoUmnkFYbzdcL8v2DF5fcMixHXSVWRexVV1g2ybG14/edit> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Bundang_Thunder.xml>

### Welcome Light: Aktivierung (Lichtschalterstellung)

<a id="fem_bodywelcome_light_activation"></a>`fem_body.welcome_light_activation` · Bereich: 1 · SG **FEM_BODY** · Kategorie Beleuchtung

Legt fest, in welcher Lichtschalterstellung das Welcome Light beim Entriegeln aktiv ist (nur AUTO oder AUTO bzw. Stellung 2) bzw. schaltet es ab.

- **BimmerCode:** Welcome Light activation (standard)
- **Parameter:** –
- **Werte:** `Light switch on auto` = nur bei Lichtschalter in AUTO; `Light switch on auto or 2` = bei AUTO oder Abblendlicht-Stellung; `Not active` = Welcome Light aus
- **Hardware:** Keine zusätzliche Hardware.
- **Software:** FEM_01 (BimmerCode-Bezeichnung des FEM_BODY).
- **Aufwand / Risiko / Nutzen:** gering / gering / mittel
- **Kompatibilität (dein F20):** wahrscheinlich kompatibel · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Hinweise:** E-Sys-Parametername in den gefundenen Quellen nicht eindeutig zugeordnet; nur als BimmerCode-Option belegt.
- **Quellen:** <https://bimmercode.app/cars/f20/>

### Welcome Light: Helligkeit

<a id="fem_bodywelcome_light_brightness"></a>`fem_body.welcome_light_brightness` · Bereich: 1 · SG **FEM_BODY** · Kategorie Beleuchtung

Helligkeit (PWM) der Welcome-Light-Leuchten.

- **BimmerCode:** Welcome Lights brightness (standard)
- **Parameter:** `WL_HELLIGKEIT` (3070)
- **Werte:** `64 (hex)` = 100 % – Standard laut Botho.xml; `32 (hex)` = 50 %; `10 % … 100 %` = Auswahl in BimmerCode
- **Hardware:** BimmerCode: wirkt nur bei Halogen- oder Xenon-Scheinwerfern (Halogen vorhanden).
- **Software:** Parametername/Wertebezeichnung können je nach I-Stufe/CAFD-Version abweichen (Quellen beziehen sich auf CAFD 00000794 FEM_BODY, Serie F020/F030). Vor dem Codieren Ist-Wert in BimmerCode auslesen und Backup sichern.
- **Aufwand / Risiko / Nutzen:** gering / gering / gering
- **Kompatibilität (dein F20):** wahrscheinlich kompatibel · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Hinweise:** Spreadsheet 'Coding BMW F3x' nennt Standard 0,64 → 0,94.
- **Quellen:** <https://bimmercode.app/cars/f20/> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Botho.xml> · <https://docs.google.com/spreadsheets/d/16O4RKIMekWFCs5jPW3T_7li0yIEvgZfFI0u3l0RmSwU/pubhtml>

### Welcome Light: weitere Leuchten (Abblend-/Fernlicht, Standlicht, TFL, Blinker, Abbiegelicht, Sidemarker)

<a id="fem_bodywelcome_light_components"></a>`fem_body.welcome_light_components` · Bereich: 1 · SG **FEM_BODY** · Kategorie Beleuchtung

BimmerCode bietet je Leuchtenfunktion die Einbindung ins Welcome Light: low beam, high beam 1/2, parking lights, daytime running light, front/central turn signals, cornering lights, design lights, sidemarkers.

- **BimmerCode:** Welcome Lights low beam / high beam 1 / high beam 2 / parking lights / daytime running light / front turn signals / cornering lights / sidemarkers (standard)
- **Parameter:** – (3063 (vermutlich, analog MAPPING_*_PART_OF_WL))
- **Werte:** `Hard on` = hart einschalten; `Soft on` = sanft einblenden; `Not active` = nicht Teil des Welcome Lights
- **Hardware:** Laut BimmerCode nur für Halogen-/Xenon-Scheinwerfer.
- **Software:** FEM_01.
- **Aufwand / Risiko / Nutzen:** gering / gering / gering
- **Kompatibilität (dein F20):** wahrscheinlich kompatibel · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Recht:** Blinker dauerhaft als Welcome-Light-Bestandteil: Funktion nur im Stand; für den Fahrbetrieb nicht relevant. Rechtliche Bewertung nicht gefunden.
- **Hinweise:** E-Sys-Namen außer für Nebelscheinwerfer nicht in den Quellen belegt; 'cafd_block' daher nur Vermutung.
- **Quellen:** <https://bimmercode.app/cars/f20/>

### Welcome Light nur bei Dunkelheit

<a id="fem_bodywelcome_light_darkness_only"></a>`fem_body.welcome_light_darkness_only` · Bereich: 1 · SG **FEM_BODY** · Kategorie Beleuchtung

Welcome Light nur aktivieren, wenn der Lichtsensor Dunkelheit meldet.

- **BimmerCode:** Welcome Light in darkness only (standard)
- **Parameter:** –
- **Werte:** `Active` = nur bei Dunkelheit; `Not active` = immer
- **Hardware:** Regen-/Lichtsensor (laut Fahrzeugbeschreibung vorhanden).
- **Software:** FEM_01.
- **Aufwand / Risiko / Nutzen:** gering / gering / gering
- **Kompatibilität (dein F20):** wahrscheinlich kompatibel · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Hinweise:** Nur als BimmerCode-Option belegt.
- **Quellen:** <https://bimmercode.app/cars/f20/>

### Welcome Light: Leuchtdauer

<a id="fem_bodywelcome_light_duration"></a>`fem_body.welcome_light_duration` · Bereich: 1 · SG **FEM_BODY** · Kategorie Beleuchtung

Dauer, wie lange das Welcome Light nach dem Entriegeln leuchtet.

- **BimmerCode:** Welcome Light lighting duration (standard)
- **Parameter:** `WL_TIMEOUT` (3060)
- **Werte:** `14 (hex)` = 20 s – Standard laut Botho.xml; `3C (hex)` = 60 s; `5/10/15/20/30/45/60 seconds` = Auswahl in BimmerCode
- **Hardware:** Keine.
- **Software:** Parametername/Wertebezeichnung können je nach I-Stufe/CAFD-Version abweichen (Quellen beziehen sich auf CAFD 00000794 FEM_BODY, Serie F020/F030). Vor dem Codieren Ist-Wert in BimmerCode auslesen und Backup sichern.
- **Aufwand / Risiko / Nutzen:** gering / gering / mittel
- **Kompatibilität (dein F20):** wahrscheinlich kompatibel · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Hinweise:** Wert in Sekunden (hex).
- **Quellen:** <https://bimmercode.app/cars/f20/> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Botho.xml>

### Fensterheber bei geöffneter Tür weiter bedienbar (vorn)

<a id="fem_bodywindow_door_open_front"></a>`fem_body.window_door_open_front` · Bereich: 1 · SG **FEM_BODY** · Kategorie Fenster

Standardmäßig stoppt/sperrt der Fensterheber beim Öffnen der Tür; deaktivieren erlaubt Weiterbedienung.

- **BimmerCode:** Window lifter interruption when opening a door (standard)
- **Parameter:** `FH_TUERAUF_STOP_MAUT` (3050)
- **Werte:** `aktiv` = Standard – Unterbrechung bei offener Tür; `nicht_aktiv` = Fenster lassen sich bei offener Tür bedienen
- **Hardware:** Keine.
- **Software:** Parametername/Wertebezeichnung können je nach I-Stufe/CAFD-Version abweichen (Quellen beziehen sich auf CAFD 00000794 FEM_BODY, Serie F020/F030). Vor dem Codieren Ist-Wert in BimmerCode auslesen und Backup sichern.
- **Aufwand / Risiko / Nutzen:** gering / gering / mittel
- **Kompatibilität (dein F20):** wahrscheinlich kompatibel · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Hinweise:** Einklemmschutz bleibt laut Quellen unberührt (nicht verifiziert).
- **Quellen:** <https://bimmercode.app/cars/f20/> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Botho.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Bundang_Thunder.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Almaretto.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Kip_M3.xml>

### Nachwischzyklen nach dem Waschen (vorn/hinten)

<a id="fem_bodywipe_after_wash"></a>`fem_body.wipe_after_wash` · Bereich: 1 · SG **FEM_BODY** · Kategorie Wischer

Anzahl der Nachwischzyklen nach Scheibenwäsche vorne bzw. hinten.

- **BimmerCode:** Wipe cycles after front washing / Wipe cycles after rear washing (standard)
- **Parameter:** `WW_ANZAHL_NACHWISCHZ_FRONT`, `WW_ANZAHL_NACHWISCHZ_HECK` (3080)
- **Werte:** `WW_ANZAHL_NACHWISCHZ_FRONT = 03` = 3 Zyklen – Standard laut Botho; `WW_ANZAHL_NACHWISCHZ_HECK = 02` = 2 Zyklen – Standard; `01 … 05` = 1–5 Zyklen (BimmerCode)
- **Hardware:** Keine.
- **Software:** Parametername/Wertebezeichnung können je nach I-Stufe/CAFD-Version abweichen (Quellen beziehen sich auf CAFD 00000794 FEM_BODY, Serie F020/F030). Vor dem Codieren Ist-Wert in BimmerCode auslesen und Backup sichern.
- **Aufwand / Risiko / Nutzen:** gering / gering / mittel
- **Kompatibilität (dein F20):** wahrscheinlich kompatibel · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Quellen:** <https://bimmercode.app/cars/f20/> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Botho.xml>

### Wischerstufe im Stand automatisch zurückschalten

<a id="fem_bodywiper_level_switch_back"></a>`fem_body.wiper_level_switch_back` · Bereich: 1 · SG **FEM_BODY** · Kategorie Wischer

Wischerstufe schaltet beim Anhalten automatisch eine Stufe zurück.

- **BimmerCode:** Wiper level switch back when stationary (standard)
- **Parameter:** –
- **Werte:** `Active / Not active` = Auswahl in BimmerCode
- **Hardware:** Keine.
- **Software:** FEM_01.
- **Aufwand / Risiko / Nutzen:** gering / gering / gering
- **Kompatibilität (dein F20):** wahrscheinlich kompatibel · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Hinweise:** Nur als BimmerCode-Option belegt. Die Wischer-Serviceposition ist keine Codierung (Bedienablauf laut Betriebsanleitung).
- **Quellen:** <https://bimmercode.app/cars/f20/>

### Automatischer Reset der Durchschnittswerte

<a id="kombiaverage_values_reset"></a>`kombi.average_values_reset` · Bereich: 1 · SG **KOMBI** · Kategorie Kombiinstrument

BimmerCode 'Average values reset': Durchschnittsgeschwindigkeit und -verbrauch werden nach der eingestellten Zeit automatisch zurückgesetzt. Eine nicht verifizierte Sammlung nennt BC_AUTORESET_ZEIT (3000), Hex-Stunden (04 = 4 h, FF = nie).

- **BimmerCode:** Average values reset (standard)
- **Parameter:** `BC_AUTORESET_ZEIT` (3000)
- **Werte:** `After 4 hours` = Reset nach 4 h Standzeit (BimmerCode; laut Sammlung werte=04); `After 8 hours` = Reset nach 8 h; `After every ride` = Reset nach jeder Fahrt; `Never` = kein automatischer Reset (laut Sammlung werte=FF)
- **Hardware:** laut BimmerCode KOMBI L6 BO, L7_BASIS oder L7_MID
- **Software:** BimmerCode
- **Aufwand / Risiko / Nutzen:** gering / gering / mittel
- **Kompatibilität (dein F20):** wahrscheinlich kompatibel · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Hinweise:** Die BimmerCode-Option ist dokumentiert. Der Parametername BC_AUTORESET_ZEIT stammt nur aus der nicht verifizierten Sammlung.
- **Quellen:** <https://bimmercode.app/cars/f20> · <https://raw.githubusercontent.com/Dauxdu/bmw-coding/HEAD/e-sys/02-Codings/Instrument-Cluster.md>

### Auswahl der BC-Anzeigen über iDrive

<a id="kombibc_information_display_selection"></a>`kombi.bc_information_display_selection` · Bereich: 1 · SG **KOMBI** · Kategorie Kombiinstrument

Laut BMW F30-Doku: BC-Liste mit Reichweite, Durchschnittsverbrauch, Durchschnittsgeschwindigkeit, (mit Navi) Entfernung/Ankunft/Pfeil, Datum, Speed-Limit-Info und ECO-PRO-Bonusreichweite. Was angezeigt wird, wählt man im iDrive unter 'Settings → Information Display'. Das ist eine Benutzereinstellung, keine Codierung.

- **Parameter:** –
- **Hardware:** keine
- **Software:** keine
- **Aufwand / Risiko / Nutzen:** gering / gering / mittel
- **Kompatibilität (dein F20):** wahrscheinlich kompatibel · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Hinweise:** Belegt für den F30. Ohne Navi entfallen die Navi-Einträge. Ob das Menü bei HU_ENTRY identisch heißt, ist nicht verifiziert.
- **Quellen:** <https://archive.org/download/BMWTechnicalTrainingDocuments/ST1113%20F30%20Complete%20Vehicle/06_F30%20Displays%2C%20Indicators%20and%20Controls.pdf>

### Digitale Geschwindigkeit im Bordcomputer

<a id="kombidigital_speed"></a>`kombi.digital_speed` · Bereich: 1 · SG **KOMBI** · Kategorie Kombiinstrument

Fügt der BC-Liste im Kombi-Display die aktuelle Geschwindigkeit als Zahl hinzu. Parameter BC_DIGITAL_V (Block 3000) von nicht_aktiv auf aktiv. In BimmerCode als Standardoption 'Digital speed in board computer'.

- **BimmerCode:** Digital speed in board computer (standard)
- **Parameter:** `BC_DIGITAL_V` (3000)
- **Werte:** `nicht_aktiv` = keine Digitalanzeige (Standard); `aktiv` = Geschwindigkeit als Zahl im BC
- **Hardware:** laut BimmerCode KOMBI L6 BO, L7_BASIS oder L7_MID
- **Software:** BimmerCode (Standard) oder Expertenmodus
- **Aufwand / Risiko / Nutzen:** gering / gering / hoch
- **Kompatibilität (dein F20):** wahrscheinlich kompatibel · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Hinweise:** Die Community-Tabelle schreibt 'BC_Digital_V'. Die übrigen Quellen schreiben BC_DIGITAL_V. 'likely', weil die KOMBI-Variante des 2012er F20 nicht bestätigt ist.
- **Quellen:** <https://bimmercode.app/cars/f20> · <https://docs.google.com/spreadsheets/d/16O4RKIMekWFCs5jPW3T_7li0yIEvgZfFI0u3l0RmSwU/pubhtml> · <https://raw.githubusercontent.com/Dauxdu/bmw-coding/HEAD/e-sys/02-Codings/Instrument-Cluster.md> · <https://www.scribd.com/doc/314263744/F30-Coding-Reference-Guide-v1-7>

### Leerer Menüpunkt im Bordcomputer

<a id="kombiempty_menu_item"></a>`kombi.empty_menu_item` · Bereich: 1 · SG **KOMBI** · Kategorie Kombiinstrument

BimmerCode 'Empty menu item in board computer' fügt eine leere BC-Seite hinzu (ruhiges Display).

- **BimmerCode:** Empty menu item in board computer (standard)
- **Parameter:** –
- **Werte:** `Active` = leere Seite vorhanden; `Not active` = keine leere Seite
- **Hardware:** laut BimmerCode KOMBI L6 BO, L7_BASIS oder L7_MID
- **Software:** BimmerCode
- **Aufwand / Risiko / Nutzen:** gering / gering / mittel
- **Kompatibilität (dein F20):** wahrscheinlich kompatibel · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Hinweise:** Den FDL-Parameternamen hat BimmerCode nicht veröffentlicht.
- **Quellen:** <https://bimmercode.app/cars/f20>

### Reservewarnung 1 (dauerhaft)

<a id="kombilow_fuel_warning_1"></a>`kombi.low_fuel_warning_1` · Bereich: 1 · SG **KOMBI** · Kategorie Kombiinstrument

BimmerCode 'Low fuel warning 1': Restreichweite, ab der die dauerhafte Reservewarnung erscheint.

- **BimmerCode:** Low fuel warning 1 (standard)
- **Parameter:** –
- **Werte:** `10 kilometers` = ab 10 km Restreichweite; `20 kilometers` = ab 20 km; `30 kilometers` = ab 30 km; `40 kilometers` = ab 40 km; `50 kilometers` = ab 50 km; `Not active` = keine dauerhafte Warnung
- **Hardware:** laut BimmerCode KOMBI L6 BO, L7_BASIS oder L7_MID
- **Software:** BimmerCode
- **Aufwand / Risiko / Nutzen:** gering / mittel / gering
- **Kompatibilität (dein F20):** wahrscheinlich kompatibel · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Hinweise:** 'Not active' oder sehr kleine Werte erhöhen das Risiko, mit leerem Tank liegenzubleiben. Auch Meilenwerte (10/20/30 mi) sind wählbar.
- **Quellen:** <https://bimmercode.app/cars/f20>

### Reservewarnung 2 (temporär)

<a id="kombilow_fuel_warning_2"></a>`kombi.low_fuel_warning_2` · Bereich: 1 · SG **KOMBI** · Kategorie Kombiinstrument

BimmerCode 'Low fuel warning 2': Restreichweite, ab der die temporäre Reservewarnung erscheint.

- **BimmerCode:** Low fuel warning 2 (standard)
- **Parameter:** –
- **Werte:** `50 kilometers` = ab 50 km; `60 kilometers` = ab 60 km; `70 kilometers` = ab 70 km; `80 kilometers` = ab 80 km; `90 kilometers` = ab 90 km; `Not active` = keine temporäre Warnung
- **Hardware:** laut BimmerCode KOMBI L6 BO, L7_BASIS oder L7_MID
- **Software:** BimmerCode
- **Aufwand / Risiko / Nutzen:** gering / gering / gering
- **Kompatibilität (dein F20):** wahrscheinlich kompatibel · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Hinweise:** Auch Meilenwerte (40/50 mi) sind wählbar.
- **Quellen:** <https://bimmercode.app/cars/f20>

### PDC automatisch aktivieren beim Zurückrollen

<a id="rempdc_auto_rolling_back"></a>`rem.pdc_auto_rolling_back` · Bereich: 1 · SG **REM** · Kategorie Einparkhilfe

PDC schaltet sich ein, wenn das Fahrzeug rückwärts rollt (auch ohne eingelegten Rückwärtsgang).

- **BimmerCode:** Activate PDC when rolling backwards (standard)
- **Parameter:** –
- **Werte:** `Active / Not active` = Auswahl in BimmerCode
- **Hardware:** PDC hinten (vorhanden); Steuergerät PMA_PDC oder REM_01.
- **Software:** REM_01 (bei PDC ohne eigenes Steuergerät).
- **Aufwand / Risiko / Nutzen:** gering / gering / mittel
- **Kompatibilität (dein F20):** wahrscheinlich kompatibel · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Hinweise:** Für Schaltwagen am Berg nützlich. Ob die Erkennung ohne Frontsensoren funktioniert, ist nicht belegt.
- **Quellen:** <https://bimmercode.app/cars/f20/>

### PDC: Abschaltschwellen (Geschwindigkeit/Strecke)

<a id="rempdc_switch_off_thresholds"></a>`rem.pdc_switch_off_thresholds` · Bereich: 1 · SG **REM** · Kategorie Einparkhilfe

Geschwindigkeit bzw. gefahrene Strecke, ab der PDC und seine Warnungen abschalten.

- **BimmerCode:** PDC speed switch-off threshold / PDC distance switch-off threshold / Speed switch-off threshold for visual and acoustic PDC warnings (standard)
- **Parameter:** `CUT_OFF_SPEED`, `CUT_OFF_SPEED_HYST` (3201)
- **Werte:** `CUT_OFF_SPEED = 0F (hex)` = 15 km/h – Standard laut Spreadsheet F3x; `CUT_OFF_SPEED_HYST = 01` = Hysterese (Standard); `PDC speed switch-off threshold: 5–50 km/h` = BimmerCode; `PDC distance switch-off threshold: 10–250 m` = BimmerCode
- **Hardware:** PDC hinten.
- **Software:** REM_01.
- **Aufwand / Risiko / Nutzen:** gering / gering / gering
- **Kompatibilität (dein F20):** wahrscheinlich kompatibel · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Hinweise:** Werte in hex (km/h).
- **Quellen:** <https://bimmercode.app/cars/f20/> · <https://docs.google.com/spreadsheets/d/16O4RKIMekWFCs5jPW3T_7li0yIEvgZfFI0u3l0RmSwU/pubhtml>

### Komfortschließen per Fernbedienung

<a id="fem_bodycomfort_close_remote"></a>`fem_body.comfort_close_remote` · Bereich: 2 · SG **FEM_BODY** · Kategorie Fenster

Gedrückthalten der Verriegeln-Taste schließt Fenster (und Schiebedach; klappt ggf. Spiegel an).

- **BimmerCode:** Convenient closing / Convenient closing with remote control (standard)
- **Parameter:** `KOMFORTSCHLIESSUNG_FB`, `KOMFORTSCHLIESSUNG` (3053)
- **Werte:** `aktiv` = Komfortschließen per Funkschlüssel; `nicht_aktiv` = aus
- **Hardware:** Elektrische Fensterheber mit Einklemmschutz (Serie).
- **Software:** Parametername/Wertebezeichnung können je nach I-Stufe/CAFD-Version abweichen (Quellen beziehen sich auf CAFD 00000794 FEM_BODY, Serie F020/F030). Vor dem Codieren Ist-Wert in BimmerCode auslesen und Backup sichern.
- **Aufwand / Risiko / Nutzen:** gering / mittel / hoch
- **Kompatibilität (dein F20):** wahrscheinlich kompatibel · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Recht:** Fernbetätigtes Schließen kraftbetätigter Fenster unterliegt Anforderungen an den Einklemmschutz; eine konkrete Rechtsquelle wurde nicht geprüft → [UNBEKANNT]. Nur in Sichtweite benutzen.
- **Hinweise:** Gilt nicht für Cabrios (F20 nicht betroffen).
- **Quellen:** <https://bimmercode.app/cars/f20/> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Kip_M3.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Almaretto.xml> · <https://www.motor-talk.de/forum/start-des-ersten-codierens-einstiegsfragen-t7071093.html>

### Abbiegelicht (Nebel) beim Rückwärtsfahren

<a id="fem_bodycornering_fog_reverse"></a>`fem_body.cornering_fog_reverse` · Bereich: 2 · SG **FEM_BODY** · Kategorie Beleuchtung

Nebelscheinwerfer-Abbiegelicht beim Einlegen des Rückwärtsgangs (beidseitig).

- **Parameter:** `C_CLC_REV_ALWAYS_ON`, `C_CLC_REV_CURV_BOTH_ON` (3073)
- **Werte:** `01` = aktiv (Standard laut Botho.xml); `00` = aus (abgeleitet, nicht explizit belegt)
- **Hardware:** Nebelscheinwerfer vorne; Abbiegelicht aktiv.
- **Software:** Parametername/Wertebezeichnung können je nach I-Stufe/CAFD-Version abweichen (Quellen beziehen sich auf CAFD 00000794 FEM_BODY, Serie F020/F030). Vor dem Codieren Ist-Wert in BimmerCode auslesen und Backup sichern.
- **Aufwand / Risiko / Nutzen:** gering / gering / gering
- **Kompatibilität (dein F20):** wahrscheinlich kompatibel · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Recht:** Siehe fem_body.cornering_light_via_fog.
- **Hinweise:** Nur eine Quelle (Botho.xml).
- **Quellen:** <https://github.com/packetpilot/bmw-f/blob/master/cheats/Botho.xml>

### Abbiegelicht über Nebelscheinwerfer

<a id="fem_bodycornering_light_via_fog"></a>`fem_body.cornering_light_via_fog` · Bereich: 2 · SG **FEM_BODY** · Kategorie Beleuchtung

Nebelscheinwerfer leuchten beim Abbiegen/Lenkeinschlag kurveninnen als statisches Abbiegelicht.

- **BimmerCode:** Cornering lights activation / Cornering lights deactivation (standard)
- **Parameter:** `C_CLC_ENA`, `C_BLC_ENA`, `KL_ENABLE_LI`, `KL_ENABLE_RE`, `MAPPING_ABBIEGEL_L_OUTPUT`, `MAPPING_ABBIEGEL_R_OUTPUT` (3073, 3066, 3062)
- **Werte:** `C_CLC_ENA/C_BLC_ENA = F020_enable (01)` = aktiv; `C_CLC_ENA/C_BLC_ENA = F020_disable` = aus; `KL_ENABLE_LI/RE = KL_Ein / KL_Aus` = Abbiegelicht links/rechts ein/aus; `MAPPING_ABBIEGEL_L/R_OUTPUT = nsw_l / nsw_r (0B/0C)` = Ausgang = Nebelscheinwerfer links/rechts; `off` = kein Ausgang
- **Hardware:** Nebelscheinwerfer vorne (vorhanden).
- **Software:** Parametername/Wertebezeichnung können je nach I-Stufe/CAFD-Version abweichen (Quellen beziehen sich auf CAFD 00000794 FEM_BODY, Serie F020/F030). Vor dem Codieren Ist-Wert in BimmerCode auslesen und Backup sichern. Bei Botho ist 'F020_enable' als Standard angegeben → evtl. bereits ab Werk aktiv.
- **Aufwand / Risiko / Nutzen:** mittel / mittel / mittel
- **Kompatibilität (dein F20):** wahrscheinlich kompatibel · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Recht:** ECE R48 6.20 sieht Abbiegeleuchten nach ECE R119 vor; Nebelscheinwerfer (R19) dürfen nach R48 6.3.7 nur innerhalb eines AFS Teil einer anderen Lichtfunktion sein. Ist die Funktion für dieses Fahrzeug nicht ab Werk genehmigt, ist die Nachcodierung eine rechtliche Grauzone.
- **Hinweise:** Alle sechs Parameter konsistent setzen (mehrteilige Codierung). BimmerCode fasst sie zu einer Option zusammen.
- **Quellen:** <https://bimmercode.app/cars/f20/> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Botho.xml> · <https://docs.google.com/spreadsheets/d/16O4RKIMekWFCs5jPW3T_7li0yIEvgZfFI0u3l0RmSwU/pubhtml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/ekfxisid.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Bundang_Thunder.xml>

### Tagfahrlicht: Helligkeit

<a id="fem_bodydrl_brightness"></a>`fem_body.drl_brightness` · Bereich: 2 · SG **FEM_BODY** · Kategorie Beleuchtung

PWM-Helligkeit der vorderen TFL-Leuchten links/rechts.

- **BimmerCode:** Daytime running light brightness (standard)
- **Parameter:** `MAPPING_TAGFAHRL_V_L_PWM_LEVEL_1`, `MAPPING_TAGFAHRL_V_R_PWM_LEVEL_1` (3062)
- **Werte:** `64 (hex)` = 100 % – Standard laut Botho.xml; `32 (hex)` = 50 %; `10 % … 100 %` = Auswahl in BimmerCode
- **Hardware:** Keine.
- **Software:** Parametername/Wertebezeichnung können je nach I-Stufe/CAFD-Version abweichen (Quellen beziehen sich auf CAFD 00000794 FEM_BODY, Serie F020/F030). Vor dem Codieren Ist-Wert in BimmerCode auslesen und Backup sichern.
- **Aufwand / Risiko / Nutzen:** gering / gering / gering
- **Kompatibilität (dein F20):** wahrscheinlich kompatibel · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Recht:** Absenken unter die Lichtstärke-Mindestwerte der TFL-Genehmigung (ECE R87) könnte die Typkonformität verletzen; konkrete Grenzwerte hier nicht geprüft.
- **Hinweise:** Bei Halogen-F20 ist unklar, welche Leuchte (Lichtleiter/Ring) das TFL bildet → Wirkung am Fahrzeug prüfen.
- **Quellen:** <https://bimmercode.app/cars/f20/> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Botho.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/ekfxisid.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/FDLCodes.xml>

### Tagfahrlicht (TFL): Modus

<a id="fem_bodydrl_mode"></a>`fem_body.drl_mode` · Bereich: 2 · SG **FEM_BODY** · Kategorie Beleuchtung

Grundmodus des Tagfahrlichts (aktiv / aktiv auch mit Standlicht / aus). In E-Sys-Cheats auch Variante 'TFL_S' (TFL inkl. Rückleuchten).

- **BimmerCode:** Daytime running light mode (standard)
- **Parameter:** `TFL_MODUS` (3060)
- **Werte:** `02` = Standard laut Botho.xml (Wertbedeutung nicht erläutert); `TFL_S` = TFL inkl. Rückleuchten (Almaretto/Kip/FDLCodes, Teil 1 von 2 mit REM); `Active / Active also with parking lights / Not active` = Auswahl in BimmerCode
- **Hardware:** Keine (TFL ab Werk vorhanden).
- **Software:** Parametername/Wertebezeichnung können je nach I-Stufe/CAFD-Version abweichen (Quellen beziehen sich auf CAFD 00000794 FEM_BODY, Serie F020/F030). Vor dem Codieren Ist-Wert in BimmerCode auslesen und Backup sichern.
- **Aufwand / Risiko / Nutzen:** gering / mittel / mittel
- **Kompatibilität (dein F20):** wahrscheinlich kompatibel · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Recht:** ECE R48 (Rev. 7, Abs. 6.19.7) verlangt bei typgenehmigten Fahrzeugen automatisches Einschalten des TFL; manuelles Abschalten nur unter 10 km/h zulässig. In DE besteht laut ADAC keine Pflicht, TFL zu benutzen (Neufahrzeuge müssen aber ausgerüstet sein). Dauerhaftes Wegcodieren = Abweichung vom Typgenehmigungszustand → rechtliche Grauzone.
- **Hinweise:** Wertebezeichnungen unterscheiden sich zwischen Quellen (02 vs. TFL_S) → vor Änderung Ist-Wert/Auswahlliste prüfen.
- **Quellen:** <https://bimmercode.app/cars/f20/> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Botho.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Almaretto.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Kip_M3.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/FDLCodes.xml>

### Nebelscheinwerfer beim Fernlicht ausschalten

<a id="fem_bodyfog_off_with_high_beam"></a>`fem_body.fog_off_with_high_beam` · Bereich: 2 · SG **FEM_BODY** · Kategorie Beleuchtung

Legt fest, ob die Nebelscheinwerfer beim Einschalten des Fernlichts automatisch erlöschen (US-Verhalten) oder anbleiben.

- **BimmerCode:** Fog lights off with high beam (standard)
- **Parameter:** `NSW_AUS_BEI_FL` (3060)
- **Werte:** `00` = Nebelscheinwerfer bleiben bei Fernlicht an (Botho: Standard 00); `01` = Nebelscheinwerfer gehen bei Fernlicht aus (abgeleitet aus packetpilot 'Disable Hi-Beam Override' = 00); `Active / Not active` = Auswahl in BimmerCode
- **Hardware:** Nebelscheinwerfer vorne (vorhanden).
- **Software:** Parametername/Wertebezeichnung können je nach I-Stufe/CAFD-Version abweichen (Quellen beziehen sich auf CAFD 00000794 FEM_BODY, Serie F020/F030). Vor dem Codieren Ist-Wert in BimmerCode auslesen und Backup sichern.
- **Aufwand / Risiko / Nutzen:** gering / gering / gering
- **Kompatibilität (dein F20):** wahrscheinlich kompatibel · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Recht:** ECE R48 6.3.7 verlangt, dass Nebelscheinwerfer unabhängig von Fern-/Abblendlicht schaltbar sind; Benutzung nach § 17 Abs. 3 StVO nur bei Nebel, Schneefall oder Regen.
- **Hinweise:** Bei EU-Fahrzeugen vermutlich bereits 'bleiben an' [WAHRSCHEINLICH].
- **Quellen:** <https://bimmercode.app/cars/f20/> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Botho.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/packetpilot.xml> · <https://nsai.ie/images/uploads/certification-automotive/UNECE-R48-04.pdf> · <https://www.gesetze-im-internet.de/stvo_2013/__17.html>

### Lampenüberwachung vorn (Kalt-/Warmüberwachung, LED-Kennung)

<a id="fem_bodylamp_monitoring_front"></a>`fem_body.lamp_monitoring_front` · Bereich: 2 · SG **FEM_BODY** · Kategorie Beleuchtung

Deaktiviert die Kalt- und Warmüberwachung bzw. kennzeichnet Ausgänge als LED, um Fehlermeldungen/Flackern bei LED-Nachrüstlampen zu verhindern (Blinker vorn, Nebelscheinwerfer u. a.).

- **BimmerCode:** LED conversion front turn signal / fog lights / low beam / high beam / position lights / daytime running lights / side turn signal (standard)
- **Parameter:** `FRA_V_L_KALTUEBERWACHUNG`, `FRA_V_L_WARMUEBERWACHUNG`, `FRA_V_L_IS_LED`, `FRA_V_R_KALTUEBERWACHUNG`, `FRA_V_R_WARMUEBERWACHUNG`, `FRA_V_R_IS_LED`, `NSW_L_KALTUEBERWACHUNG`, `NSW_L_WARMUEBERWACHUNG`, `NSW_L_IS_LED`, `NSW_R_KALTUEBERWACHUNG`, `NSW_R_WARMUEBERWACHUNG`, `NSW_R_IS_LED` (3061)
- **Werte:** `*_KALTUEBERWACHUNG / *_WARMUEBERWACHUNG = aktiv` = Standard – Lampenausfallüberwachung; `= nicht_aktiv` = Überwachung aus; `*_IS_LED = aktiv` = Ausgang als LED kennzeichnen
- **Hardware:** Nur sinnvoll nach Umbau auf LED-Leuchtmittel.
- **Software:** Parametername/Wertebezeichnung können je nach I-Stufe/CAFD-Version abweichen (Quellen beziehen sich auf CAFD 00000794 FEM_BODY, Serie F020/F030). Vor dem Codieren Ist-Wert in BimmerCode auslesen und Backup sichern. BimmerCode: Rücknahme nur über Backup.
- **Aufwand / Risiko / Nutzen:** mittel / mittel / gering
- **Kompatibilität (dein F20):** wahrscheinlich kompatibel · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Recht:** LED-Nachrüstlampen in Scheinwerfern sind in DE nur mit Genehmigung für das konkrete Fahrzeug zulässig; abgeschaltete Überwachung meldet defekte Lampen nicht mehr. Nur dokumentieren.
- **Hinweise:** Fahrzeug hat laut Beschreibung Halogen ohne LED-Umbau → aktuell kein Bedarf.
- **Quellen:** <https://bimmercode.app/cars/f20/> · <https://docs.google.com/spreadsheets/d/16O4RKIMekWFCs5jPW3T_7li0yIEvgZfFI0u3l0RmSwU/pubhtml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/ekfxisid.xml>

### Auto Start-Stop (MSA) standardmäßig aus

<a id="fem_bodymsa_default_off"></a>`fem_body.msa_default_off` · Bereich: 2 · SG **FEM_BODY** · Kategorie Antrieb/Fahrdynamik

MSA ist nach jedem Motorstart deaktiviert (im ECO-PRO-Modus laut BimmerCode wieder aktiv).

- **BimmerCode:** Auto Start Stop function off by default (standard)
- **Parameter:** `TCM_MSA_DEFAULT_OFF` (3023)
- **Werte:** `nicht_aktiv` = Standard – MSA beim Start aktiv; `aktiv` = MSA beim Start aus
- **Hardware:** MSA ab Werk (beim 116i Schaltgetriebe Serie laut BMW-Pressetext).
- **Software:** Parametername/Wertebezeichnung können je nach I-Stufe/CAFD-Version abweichen (Quellen beziehen sich auf CAFD 00000794 FEM_BODY, Serie F020/F030). Vor dem Codieren Ist-Wert in BimmerCode auslesen und Backup sichern. Auf G-Modellen liegt die Funktion im DME (DME_BAC2) – beim F20 laut Quellen im FEM.
- **Aufwand / Risiko / Nutzen:** gering / mittel / hoch
- **Kompatibilität (dein F20):** wahrscheinlich kompatibel · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Recht:** Typprüfwerte (Verbrauch/CO2) wurden mit aktivem MSA ermittelt. Keine Rechtsquelle gefunden, die das Umcodieren verbietet; HU prüft es nicht. Einordnung: Grauzone (Typgenehmigungs-/Emissionsbezug) – [UNBEKANNT].
- **Hinweise:** Alternative mit geringerem Eingriff: fem_body.msa_memory. Nicht beide gleichzeitig nötig.
- **Quellen:** <https://bimmercode.app/cars/f20/> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Botho.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Bundang_Thunder.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/ekfxisid.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/FDLCodes.xml>

### Auto Start-Stop im ECO-PRO-Modus automatisch aktivieren

<a id="fem_bodymsa_eco_pro"></a>`fem_body.msa_eco_pro` · Bereich: 2 · SG **FEM_BODY** · Kategorie Antrieb/Fahrdynamik

Legt fest, ob MSA beim Wechsel in ECO PRO automatisch eingeschaltet wird.

- **BimmerCode:** Auto Start Stop function in ECO mode (standard)
- **Parameter:** `TCM_MSA_ECO_MODE` (3023)
- **Werte:** `aktiv` = Standard laut Botho; `nicht_aktiv` = kein automatisches Einschalten in ECO PRO
- **Hardware:** Fahrerlebnisschalter (Serie).
- **Software:** Parametername/Wertebezeichnung können je nach I-Stufe/CAFD-Version abweichen (Quellen beziehen sich auf CAFD 00000794 FEM_BODY, Serie F020/F030). Vor dem Codieren Ist-Wert in BimmerCode auslesen und Backup sichern.
- **Aufwand / Risiko / Nutzen:** gering / mittel / gering
- **Kompatibilität (dein F20):** wahrscheinlich kompatibel · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Recht:** Siehe fem_body.msa_default_off.
- **Quellen:** <https://bimmercode.app/cars/f20/> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Botho.xml>

### Auto Start-Stop: letzten Zustand merken

<a id="fem_bodymsa_memory"></a>`fem_body.msa_memory` · Bereich: 2 · SG **FEM_BODY** · Kategorie Antrieb/Fahrdynamik

MSA-Zustand (an/aus) wird über den Motorneustart gespeichert.

- **BimmerCode:** Auto Start Stop function memory (standard)
- **Parameter:** `TCM_MSA_MEMORY` (3023)
- **Werte:** `nicht_aktiv` = Standard laut Botho; `aktiv` = letzten Zustand merken
- **Hardware:** Keine.
- **Software:** Parametername/Wertebezeichnung können je nach I-Stufe/CAFD-Version abweichen (Quellen beziehen sich auf CAFD 00000794 FEM_BODY, Serie F020/F030). Vor dem Codieren Ist-Wert in BimmerCode auslesen und Backup sichern. Spreadsheet F3x nennt abweichend 'aktiv → nicht aktiv' (vermutlich vertauscht).
- **Aufwand / Risiko / Nutzen:** gering / mittel / hoch
- **Kompatibilität (dein F20):** wahrscheinlich kompatibel · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Recht:** Siehe fem_body.msa_default_off (Grauzone, keine Rechtsquelle gefunden).
- **Hinweise:** Laut BimmerCode wird MSA im ECO-PRO-Modus trotzdem wieder aktiviert.
- **Quellen:** <https://bimmercode.app/cars/f20/> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Botho.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Bundang_Thunder.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/ekfxisid.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/FDLCodes.xml>

### Stand-/Positionslicht ('Angel Eyes'): Helligkeit

<a id="fem_bodyparking_light_brightness"></a>`fem_body.parking_light_brightness` · Bereich: 2 · SG **FEM_BODY** · Kategorie Beleuchtung

PWM-Helligkeit des vorderen Standlichts links/rechts (bei Abblendlicht bzw. Standlicht).

- **BimmerCode:** Angel Eyes brightness low beam / Angel Eyes brightness parking lights (standard)
- **Parameter:** `MAPPING_STANDL_V_L_PWM_LEVEL_STANDARD`, `MAPPING_STANDL_V_R_PWM_LEVEL_STANDARD` (3062)
- **Werte:** `8` = Standard laut Botho.xml; `32 (hex)` = 50 %; `64 (hex)` = 100 %
- **Hardware:** Unklar, ob die Halogen-Scheinwerfer des F20 Pre-LCI eine dimmbare Ring-/Lichtleiter-Standlichtfunktion haben.
- **Software:** Parametername/Wertebezeichnung können je nach I-Stufe/CAFD-Version abweichen (Quellen beziehen sich auf CAFD 00000794 FEM_BODY, Serie F020/F030). Vor dem Codieren Ist-Wert in BimmerCode auslesen und Backup sichern.
- **Aufwand / Risiko / Nutzen:** gering / gering / gering
- **Kompatibilität (dein F20):** unbekannt · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Recht:** Positionsleuchten müssen die Werte ihrer Genehmigung einhalten (zu hell = Blendung, zu dunkel = nicht konform); nicht geprüft.
- **Hinweise:** Botho beschreibt die Option für Xenon-Fahrzeuge.
- **Quellen:** <https://bimmercode.app/cars/f20/> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Botho.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/ekfxisid.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/FDLCodes.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/otakar.xml>

### Welcome Light: Nebelscheinwerfer einbeziehen

<a id="fem_bodywelcome_light_fog"></a>`fem_body.welcome_light_fog` · Bereich: 2 · SG **FEM_BODY** · Kategorie Beleuchtung

Nebelscheinwerfer leuchten als Teil des Welcome Lights (sanft oder hart eingeschaltet).

- **BimmerCode:** Welcome Lights fog lights (standard)
- **Parameter:** `MAPPING_NEBELSCHW_L_PART_OF_WL`, `MAPPING_NEBELSCHW_R_PART_OF_WL` (3063)
- **Werte:** `nicht_aktiv / 00` = Standard – Nebelscheinwerfer nicht Teil des Welcome Lights; `soft_On` = sanft einblenden; `hard_On` = hart einschalten
- **Hardware:** Nebelscheinwerfer vorne (vorhanden).
- **Software:** Parametername/Wertebezeichnung können je nach I-Stufe/CAFD-Version abweichen (Quellen beziehen sich auf CAFD 00000794 FEM_BODY, Serie F020/F030). Vor dem Codieren Ist-Wert in BimmerCode auslesen und Backup sichern.
- **Aufwand / Risiko / Nutzen:** gering / gering / mittel
- **Kompatibilität (dein F20):** wahrscheinlich kompatibel · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Recht:** Nur im Stand beim Entriegeln aktiv. § 17 Abs. 3 StVO beschränkt die Benutzung von Nebelscheinwerfern beim Fahren auf Sichtbehinderung durch Nebel, Schnee oder Regen; während der Fahrt nicht relevant, da Welcome Light endet.
- **Hinweise:** Beide Seiten (L/R) gleich codieren.
- **Quellen:** <https://bimmercode.app/cars/f20/> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Botho.xml> · <https://docs.google.com/spreadsheets/d/16O4RKIMekWFCs5jPW3T_7li0yIEvgZfFI0u3l0RmSwU/pubhtml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Bundang_Thunder.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/FDLCodes.xml>

### Tagfahrlicht-Ein/Aus im iDrive-Menü

<a id="hu_entrydrl_checkbox"></a>`hu_entry.drl_checkbox` · Bereich: 2 · SG **HU_ENTRY** · Kategorie Beleuchtung

Für HU_CIC dokumentiert: Daydriving_light (3000), Perm_off ↔ standard, fügt die Tagfahrlicht-Option im iDrive hinzu. BimmerCode 'Checkbox daytime running light (head unit)' gibt es nur für HU_NBT/HU_NBT_EVO.

- **BimmerCode:** Checkbox daytime running light (head unit) (unknown)
- **Parameter:** `Daydriving_light` (3000)
- **Werte:** `Perm_off` = laut Tabelle Standardwert; `standard` = laut Tabelle geänderter Wert (Option im iDrive)
- **Hardware:** HU_CIC bzw. HU_NBT; zusätzlich Lichtcodierung im FEM
- **Software:** -
- **Aufwand / Risiko / Nutzen:** mittel / mittel / gering
- **Kompatibilität (dein F20):** unbekannt · **Nachweis:** Unbekannt
- **Recht:** Tagfahrlicht ist für Neufahrzeuge in der EU vorgeschrieben (ECE-R48). Das Abschalten kann die Betriebserlaubnis berühren.
- **Hinweise:** Für HU_ENTRY kein Beleg. Die eigentliche Lichtlogik liegt im FEM (eigenes Dossier).
- **Quellen:** <https://docs.google.com/spreadsheets/d/16O4RKIMekWFCs5jPW3T_7li0yIEvgZfFI0u3l0RmSwU/pubhtml> · <https://bimmercode.app/cars/f20>

### Rückleuchten mit Tagfahrlicht

<a id="remdrl_tail_lights"></a>`rem.drl_tail_lights` · Bereich: 2 · SG **REM** · Kategorie Beleuchtung

Äußere und/oder innere Rückleuchtenteile leuchten zusammen mit dem TFL.

- **BimmerCode:** Daytime running light tail lights outer part / inner part (standard)
- **Parameter:** `MAPPING_TAGFAHRL_H_L_OUTPUT`, `MAPPING_TAGFAHRL_H_R_OUTPUT`, `MAPPING_TAGFAHRL_H2_L_OUTPUT`, `MAPPING_TAGFAHRL_H2_R_OUTPUT` (3062)
- **Werte:** `00 / off` = Standard – aus; `sl_l / sl_r (14/15 hex)` = äußere Rückleuchten links/rechts; `sl_2_l / sl_2_r (16/17 hex)` = innere Rückleuchten (Heckklappe) links/rechts
- **Hardware:** Keine.
- **Software:** REM_01; bei manchen Quellen zusätzlich FEM_BODY TFL_MODUS = TFL_S (Teil 1 von 2). Spreadsheet F3x nennt alternativ MAPPING_UNIVERSAL_6/7_OUTPUT (3063) samt PWM-Werten.
- **Aufwand / Risiko / Nutzen:** mittel / gering / mittel
- **Kompatibilität (dein F20):** wahrscheinlich kompatibel · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Recht:** ECE R48 6.19 regelt nur das vordere TFL; rechtliche Bewertung beleuchteter Rückleuchten tagsüber nicht gefunden → [UNBEKANNT].
- **Hinweise:** Pre-LCI-Rückleuchten des F20: Belegung (sl_l, sl_2_l) aus F20/F30-Quellen, am eigenen Fahrzeug prüfen.
- **Quellen:** <https://bimmercode.app/cars/f20/> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Botho.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/ekfxisid.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Almaretto.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/packetpilot.xml>

### Lampenüberwachung hinten (Blinker, Brems-, Rückfahr-, Nebelschlussleuchte)

<a id="remlamp_monitoring_rear"></a>`rem.lamp_monitoring_rear` · Bereich: 2 · SG **REM** · Kategorie Beleuchtung

Kalt-/Warmüberwachung und LED-Kennung der Heckleuchten-Ausgänge.

- **BimmerCode:** LED conversion brake light / rear turn signals / reversing light / rear fog light / license plate light / inner tail lights / outer tail lights / center brake light (standard)
- **Parameter:** `FRA_H_L_KALTUEBERWACHUNG`, `FRA_H_L_WARMUEBERWACHUNG`, `FRA_H_L_IS_LED`, `FRA_H_R_KALTUEBERWACHUNG`, `FRA_H_R_IS_LED`, `BL_L_KALTUEBERWACHUNG`, `BL_L_WARMUEBERWACHUNG`, `BL_L_IS_LED`, `BL_R_KALTUEBERWACHUNG`, `BL_R_WARMUEBERWACHUNG`, `BL_R_IS_LED`, `RFS_L_KALTUEBERWACHUNG`, `RFS_L_WARMUEBERWACHUNG`, `RFS_L_IS_LED`, `RFS_R_KALTUEBERWACHUNG`, `RFS_R_WARMUEBERWACHUNG`, `RFS_R_IS_LED` (3061)
- **Werte:** `aktiv` = Standard – Überwachung an; `nicht_aktiv` = Überwachung aus; `*_IS_LED = aktiv` = LED-Ausgang
- **Hardware:** Nur nach LED-Umbau.
- **Software:** REM_01.
- **Aufwand / Risiko / Nutzen:** mittel / mittel / gering
- **Kompatibilität (dein F20):** wahrscheinlich kompatibel · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Recht:** Siehe fem_body.lamp_monitoring_front; LED-Leuchtmittel brauchen eine Genehmigung.
- **Hinweise:** Nur dokumentieren. ekfxisid.xml enthält zusätzlich NSL_* (Schreibweise dort teils fehlerhaft).
- **Quellen:** <https://bimmercode.app/cars/f20/> · <https://docs.google.com/spreadsheets/d/16O4RKIMekWFCs5jPW3T_7li0yIEvgZfFI0u3l0RmSwU/pubhtml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/ekfxisid.xml>

### Komfortblinker: Profil-Standard (1x / 3x / 5x)

<a id="fem_bodycomfort_turn_signal_default"></a>`fem_body.comfort_turn_signal_default` · Bereich: 3 · SG **FEM_BODY** · Kategorie Beleuchtung

Vorgabewert der Komfortblinker-Einstellung im Fahrerprofil (PIA).

- **Parameter:** `PIA_DEFAULT_TIPPBLINKEN` (3064)
- **Werte:** `00` = 1 Zyklus; `01` = 3 Zyklen (Standard laut Botho); `02` = 5 Zyklen – laut Botho 'Don't work'
- **Hardware:** Keine.
- **Software:** Relevant für neuere I-Stufen (ab 3.61.x laut Botho).
- **Aufwand / Risiko / Nutzen:** gering / gering / gering
- **Kompatibilität (dein F20):** unbekannt · **Nachweis:** Experimentell
- **Hinweise:** Spreadsheet F3x: Werte 'einfagblinken' → 'mehrfagblinken' (Schreibweise der Quelle).
- **Quellen:** <https://github.com/packetpilot/bmw-f/blob/master/cheats/Botho.xml> · <https://docs.google.com/spreadsheets/d/16O4RKIMekWFCs5jPW3T_7li0yIEvgZfFI0u3l0RmSwU/pubhtml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/otakar.xml>

### Heimleuchten über Funkschlüssel auslösen

<a id="fem_bodyfollow_me_home_remote"></a>`fem_body.follow_me_home_remote` · Bereich: 3 · SG **FEM_BODY** · Kategorie Beleuchtung

Follow-me-home-Licht per Taste der Fernbedienung starten (Botho: 4. Taste bzw. kurzer Druck auf 3. Taste; dazu Belegung der 3. Taste in 30D0).

- **Parameter:** `FOLLOWMEHOME_VIA_FFB`, `RC_DEFAULT_IDG_3RD_BUTTON_SHORT` (3060, 30D0)
- **Werte:** `nicht_aktiv` = Standard; `aktiv` = Auslösung per Fernbedienung; `RC_DEFAULT_IDG_3RD_BUTTON_SHORT = 04` = Kurzdruck 3. Taste = Follow-me-home (Botho, zusammen mit Panic-Alarm-Konfiguration)
- **Hardware:** Schlüssel mit passender Tastenbelegung; EU-Schlüssel hat i. d. R. 3 Tasten (Heckklappe auf 3. Taste).
- **Software:** Parametername/Wertebezeichnung können je nach I-Stufe/CAFD-Version abweichen (Quellen beziehen sich auf CAFD 00000794 FEM_BODY, Serie F020/F030). Vor dem Codieren Ist-Wert in BimmerCode auslesen und Backup sichern.
- **Aufwand / Risiko / Nutzen:** mittel / gering / gering
- **Kompatibilität (dein F20):** unbekannt · **Nachweis:** Experimentell
- **Hinweise:** Quelle beschreibt Kombination mit RC_PANIC_ALARM (setzt Alarmanlage voraus). Ohne Panic-Belegung auf EU-Schlüssel ungetestet → experimentell.
- **Quellen:** <https://github.com/packetpilot/bmw-f/blob/master/cheats/Botho.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/ekfxisid.xml>

### Soft-On/Soft-Off (Dimmen) von Fahrlicht

<a id="fem_bodysoft_on_off_main_lights"></a>`fem_body.soft_on_off_main_lights` · Bereich: 3 · SG **FEM_BODY** · Kategorie Beleuchtung

Sanftes Auf-/Abdimmen der Hauptlichtfunktionen. In den Quellen nur als Wert 'Soft on' für Welcome-Light-Bestandteile belegt.

- **Parameter:** –
- **Werte:** `Soft on / Hard on` = nur für Welcome-Light-Bestandteile belegt
- **Hardware:** Unbekannt.
- **Software:** Unbekannt.
- **Aufwand / Risiko / Nutzen:** mittel / gering / gering
- **Kompatibilität (dein F20):** unbekannt · **Nachweis:** Unbekannt
- **Hinweise:** Kein Parameter für Fahrlicht-Soft-On/Off gefunden → nicht codieren.
- **Quellen:** <https://bimmercode.app/cars/f20/>

### Checkbox akustische Verriegelungsbestätigung im iDrive

<a id="hu_entryacoustic_lock_checkbox"></a>`hu_entry.acoustic_lock_checkbox` · Bereich: 3 · SG **HU_ENTRY** · Kategorie Verriegelung

Für HU_CIC dokumentiert: Acoustical_lock_confirm (3000) aktiv bietet im iDrive die akustische Bestätigung beim Ver-/Entriegeln an (Werks-Alarmanlage nötig). BimmerCode-Checkbox nur für HU_NBT/HU_NBT_EVO.

- **BimmerCode:** Checkbox acoustical lock confirmation (head unit) (unknown)
- **Parameter:** `Acoustical_lock_confirm` (3000)
- **Werte:** `nicht_aktiv` = keine Checkbox; `aktiv` = Checkbox im iDrive
- **Hardware:** Werks-Alarmanlage; HU_CIC bzw. HU_NBT
- **Software:** -
- **Aufwand / Risiko / Nutzen:** mittel / gering / gering
- **Kompatibilität (dein F20):** unbekannt · **Nachweis:** Unbekannt
- **Hinweise:** Für HU_ENTRY kein Beleg. BimmerCode bietet zusätzlich 'Acoustical lock/unlock confirmation' (nicht Headunit) an. Das gehört ins Dossier Verriegelung.
- **Quellen:** <https://docs.google.com/spreadsheets/d/16O4RKIMekWFCs5jPW3T_7li0yIEvgZfFI0u3l0RmSwU/pubhtml> · <https://bimmercode.app/cars/f20>

### Eigene Software / Apps auf HU_ENTRY

<a id="hu_entrycustom_software_apps"></a>`hu_entry.custom_software_apps` · Bereich: 3 · SG **HU_ENTRY** · Kategorie Sonstiges

(1) Normales Codieren ändert nur vorhandene Parameter. (2) Software lässt sich laut BMW-Doku nur über Ethernet FEM→HU per Update flashen (BMW-Software via ISTA/P). Ein öffentlich dokumentierter Weg für eigene Software existiert nicht. (3) Gezeigte Methoden: keine öffentliche Evidenz gefunden. Ein NBT-EVO-Toolkit nennt HU_ENTRY als 'different SoC', auf das seine Methoden nicht passen.

- **Parameter:** –
- **Hardware:** -
- **Software:** -
- **Aufwand / Risiko / Nutzen:** hoch / hoch / gering
- **Kompatibilität (dein F20):** unbekannt · **Nachweis:** Unbekannt
- **Hinweise:** Klare Aussage: Für die 2012er HU_ENTRY ist keine öffentliche Methode bekannt, eigene Software oder Apps zu installieren. Betriebssystem und SoC sind nicht öffentlich dokumentiert.
- **Quellen:** <https://archive.org/download/BMWTechnicalTrainingDocuments/ST1113%20F30%20Complete%20Vehicle/07_F30_Entertainment_and_Communication1.pdf> · <https://raw.githubusercontent.com/vandelayautollc/nbt-evo-toolkit/HEAD/docs/00-platform-overview.md>

### DAB-Radio aktivieren

<a id="hu_entrydab_radio"></a>`hu_entry.dab_radio` · Bereich: 3 · SG **HU_ENTRY** · Kategorie Audio

Für HU_CIC (3002) mit 'partly' funktionierend dokumentiert: Radio_dab, Dab_laendervarianten, dab_standard, following_available, following_dab_fm. Voraussetzung ist ein DAB-Tuner. Laut Forum-Snippet muss bei vorhandener, aber inaktiver DAB-Hardware ggf. DAB in den VO. Ein Snippet berichtet Erfolg bei HU_ENTRYNAV mit DAB.

- **Parameter:** `Radio_dab`, `Dab_laendervarianten`, `dab_standard`, `following_available`, `following_dab_fm` (3002)
- **Werte:** `aktiv` = Radio_dab/following_available aktiv; `ece` = Dab_laendervarianten Europa; `dab` = dab_standard
- **Hardware:** DAB-Tuner-Hardware zwingend
- **Software:** ggf. VO-Änderung (E-Sys)
- **Aufwand / Risiko / Nutzen:** hoch / mittel / mittel
- **Kompatibilität (dein F20):** unbekannt · **Nachweis:** Unbekannt
- **Hinweise:** Die BMW-Doku erwähnt für die HU-B nur einen AM/FM-Doppeltuner. Ohne DAB-Hardware nicht möglich. In der Tabelle bei HU_CIC mit Nebenwirkungen (Senderspeicher). Für HU_ENTRY unbelegt.
- **Quellen:** <https://docs.google.com/spreadsheets/d/16O4RKIMekWFCs5jPW3T_7li0yIEvgZfFI0u3l0RmSwU/pubhtml> · <https://f30.bimmerpost.com/forums/showthread.php?t=939303>

### Entwicklermenü (Build/Datum/Versionen)

<a id="hu_entrydeveloper_menu"></a>`hu_entry.developer_menu` · Bereich: 3 · SG **HU_ENTRY** · Kategorie iDrive

Für HU_CIC dokumentiert: ENTWICKLER_MENUE=aktiv zeigt ein Entwicklermenü mit Datum, Build und Versionen im iDrive.

- **Parameter:** `ENTWICKLER_MENUE` (3000 HMI)
- **Werte:** `nicht_aktiv` = aus; `aktiv` = Entwicklermenü sichtbar
- **Hardware:** belegt nur für HU_CIC
- **Software:** BimmerCode-Expertenmodus / E-Sys
- **Aufwand / Risiko / Nutzen:** mittel / mittel / gering
- **Kompatibilität (dein F20):** unbekannt · **Nachweis:** Unbekannt
- **Hinweise:** Für HU_ENTRY kein Beleg. Für versteckte Tastenkombinationen der HU_ENTRY wurde ebenfalls kein Beleg gefunden.
- **Quellen:** <https://docs.google.com/spreadsheets/d/1G_C7954Z4094jLdbR0QjqXQYY6w6-rToothcTUPb5Fs/edit> · <https://raw.githubusercontent.com/Dauxdu/bmw-coding/HEAD/e-sys/02-Codings/Head-Unit/iDrive-Features.md>

### Klingelton des Telefons (Inband Ringing) / Klingeltonwahl

<a id="hu_entryinband_ringing"></a>`hu_entry.inband_ringing` · Bereich: 3 · SG **HU_ENTRY** · Kategorie Audio

Für HU_CIC (3003) dokumentiert: Inband_ringing=aktiv nutzt den Klingelton des Telefons. Eine Sammlung nennt INBAND_RINGING und RINGTONE im CMB_MEDIA (3001). BimmerCode 'Ringtone' gibt es für Combox_Media bzw. HU_NBT/HU_NBT_EVO.

- **BimmerCode:** Ringtone (unknown)
- **Parameter:** `Inband_ringing`, `INBAND_RINGING` (3003 (HU_CIC) / 3001 (CMB_MEDIA))
- **Werte:** `nicht_aktiv` = Fahrzeug-Klingelton; `aktiv` = Klingelton des Smartphones
- **Hardware:** HU_CIC oder Combox_Media bzw. HU_NBT; für HU_ENTRY mit 6NH unbelegt
- **Software:** -
- **Aufwand / Risiko / Nutzen:** mittel / gering / gering
- **Kompatibilität (dein F20):** unbekannt · **Nachweis:** Unbekannt
- **Hinweise:** Für HU_ENTRY kein Beleg. Funktioniert laut einer Sammlung mit iPhone, nicht mit Android (nicht verifiziert).
- **Quellen:** <https://docs.google.com/spreadsheets/d/16O4RKIMekWFCs5jPW3T_7li0yIEvgZfFI0u3l0RmSwU/pubhtml> · <https://raw.githubusercontent.com/Dauxdu/bmw-coding/HEAD/e-sys/02-Codings/Head-Unit/iDrive-Features.md> · <https://bimmercode.app/cars/f20>

### Rechtshinweis beim iDrive-Start abschalten

<a id="hu_entrylegal_disclaimer"></a>`hu_entry.legal_disclaimer` · Bereich: 3 · SG **HU_ENTRY** · Kategorie iDrive

Bei HU_CIC und HU_NBT dokumentiert: LEGAL_DISCLAIMER_TIME (3001 EXBOX) von ld_mit_timeout auf kein_ld entfernt den Rechtshinweis beim Start. BimmerCode 'Warning at startup' gibt es nur für HU_NBT/HU_NBT_EVO. Ob HU_ENTRY ohne Navi überhaupt einen solchen Hinweis zeigt und den Parameter hat, ist nicht belegt.

- **BimmerCode:** Warning at startup (unknown)
- **Parameter:** `LEGAL_DISCLAIMER_TIME` (3001 EXBOX)
- **Werte:** `ld_mit_timeout` = Hinweis mit Timeout (Standard bei CIC/NBT); `kein_ld` = kein Rechtshinweis
- **Hardware:** belegt nur für HU_CIC/HU_NBT
- **Software:** BimmerCode-Expertenmodus / E-Sys
- **Aufwand / Risiko / Nutzen:** mittel / gering / gering
- **Kompatibilität (dein F20):** unbekannt · **Nachweis:** Unbekannt
- **Hinweise:** Für HU_ENTRY unbelegt. Nur anfassen, wenn der Parameter im eigenen CAFD vorhanden ist.
- **Quellen:** <https://docs.google.com/spreadsheets/d/1G_C7954Z4094jLdbR0QjqXQYY6w6-rToothcTUPb5Fs/edit> · <https://docs.google.com/spreadsheets/d/1UreLsK1PwycTWeW6OL71HOoVpLtKtfwRMRSvlsiC8JY/edit> · <https://bimmercode.app/cars/f20>

### Maximale Einschaltlautstärke

<a id="hu_entrymax_volume_startup"></a>`hu_entry.max_volume_startup` · Bereich: 3 · SG **HU_ENTRY** · Kategorie Audio

BimmerCode 'Maximum volume at startup' (10–50 %) gibt es nur für HU_NBT/HU_NBT_EVO. Eine nicht verifizierte Sammlung nennt für HU_CIC VOL_MAX_ON in Block 3002 (Standard 19 = 25 %).

- **BimmerCode:** Maximum volume at startup (unknown)
- **Parameter:** `VOL_MAX_ON` (3002)
- **Werte:** `19` = 25 % (Standard laut Sammlung, HU_CIC); `32` = bis 100 % (laut Sammlung, HU_CIC)
- **Hardware:** belegt für HU_CIC (Sammlung) und HU_NBT/EVO (BimmerCode)
- **Software:** -
- **Aufwand / Risiko / Nutzen:** mittel / gering / gering
- **Kompatibilität (dein F20):** unbekannt · **Nachweis:** Unbekannt
- **Hinweise:** Für HU_ENTRY kein Beleg. Hohe Einschaltlautstärke kann das Gehör gefährden bzw. erschrecken.
- **Quellen:** <https://raw.githubusercontent.com/Dauxdu/bmw-coding/HEAD/e-sys/02-Codings/Head-Unit/iDrive-Features.md> · <https://bimmercode.app/cars/f20>

### Servicehistorie im iDrive

<a id="hu_entryservice_history"></a>`hu_entry.service_history` · Bereich: 3 · SG **HU_ENTRY** · Kategorie iDrive

BimmerCode 'Service history' gibt es nur für HU_NBT/HU_NBT_EVO. Eine nicht verifizierte Sammlung nennt SERVICE_HISTORY (3000) für HU_NBT/HU_CIC.

- **BimmerCode:** Service history (unknown)
- **Parameter:** `SERVICE_HISTORY` (3000)
- **Werte:** `nicht_aktiv` = aus; `aktiv` = Servicehistorie anzeigen
- **Hardware:** laut BimmerCode HU_NBT/HU_NBT_EVO
- **Software:** -
- **Aufwand / Risiko / Nutzen:** mittel / gering / gering
- **Kompatibilität (dein F20):** unbekannt · **Nachweis:** Unbekannt
- **Hinweise:** Für HU_ENTRY kein Beleg.
- **Quellen:** <https://raw.githubusercontent.com/Dauxdu/bmw-coding/HEAD/e-sys/02-Codings/Head-Unit/iDrive-Features.md> · <https://bimmercode.app/cars/f20>

### Sportanzeigen (Leistung/Drehmoment) im iDrive

<a id="hu_entrysport_displays"></a>`hu_entry.sport_displays` · Bereich: 3 · SG **HU_ENTRY** · Kategorie iDrive

Schaltet das Menü 'Sportanzeigen' unter Fahrzeuginfo frei. Laut Forum-Snippet erzeugt EFF_DYN_SPORT_CID=aktiv im HU_ENTRY-Block 3000 das Menü. Ein Nutzer mit HU_ENTRY ohne Navi berichtet, dass Leistung und Drehmoment im Betrieb auf 0 bleiben. Andere melden Erfolg (X3 ohne Navi, HU_ENTRYNAV). Die Anzeige hängt davon ab, ob die DME die Daten liefert (bei einigen Dieseln nicht).

- **BimmerCode:** Sport displays (expert)
- **Parameter:** `EFF_DYN_SPORT_CID` (3000)
- **Werte:** `nicht_aktiv` = Sportanzeigen aus (Standard); `aktiv` = Menü Sportanzeigen sichtbar
- **Hardware:** HU_ENTRY (für HU_ENTRY nur per Forum belegt); DME muss Leistungs-/Drehmomentdaten liefern
- **Software:** BimmerCode-Expertenmodus, falls HU_ENTRY dort codierbar ist. Die BimmerCode-Standardoption gilt nur für HU_NBT/HU_NBT_EVO.
- **Aufwand / Risiko / Nutzen:** mittel / gering / mittel
- **Kompatibilität (dein F20):** unbekannt · **Nachweis:** Experimentell
- **Hinweise:** Forenseiten waren blockiert, Auswertung nur über Suchmaschinen-Snippets. Für HU_CIC ist Block 3000 dokumentiert. Für den N13 gibt es keinen Beleg, dass die Werte geliefert werden. Vorher prüfen, ob der Parameter im eigenen CAFD existiert.
- **Quellen:** <https://www.2addicts.com/forums/showthread.php?t=1083314> · <https://f30.bimmerpost.com/forums/showthread.php?t=1138487> · <https://www.bimmerfest.com/threads/power-and-torque-meters-in-sport-display.723339/> · <https://docs.google.com/spreadsheets/d/16O4RKIMekWFCs5jPW3T_7li0yIEvgZfFI0u3l0RmSwU/pubhtml> · <https://bimmercode.app/cars/f20>

### Farbe der Sportanzeigen (orange → rot/silber)

<a id="hu_entrysport_displays_color"></a>`hu_entry.sport_displays_color` · Bereich: 3 · SG **HU_ENTRY** · Kategorie iDrive

Bei HU_NBT dokumentiert: M_VEHICLE=aktiv ändert die Farbe der Sportanzeige. BimmerCode bietet 'Sport displays color' nur für HU_NBT/HU_NBT_EVO an.

- **BimmerCode:** Sport displays color (unknown)
- **Parameter:** `M_VEHICLE` (3000 HMI)
- **Werte:** `nicht_aktiv` = Standardfarbe orange; `aktiv` = rot/silber (M-Darstellung)
- **Hardware:** laut BimmerCode HU_NBT oder HU_NBT_EVO
- **Software:** -
- **Aufwand / Risiko / Nutzen:** mittel / gering / gering
- **Kompatibilität (dein F20):** unbekannt · **Nachweis:** Unbekannt
- **Hinweise:** Für HU_ENTRY kein Beleg. Ohne funktionierende Sportanzeigen ohnehin ohne Nutzen.
- **Quellen:** <https://docs.google.com/spreadsheets/d/1UreLsK1PwycTWeW6OL71HOoVpLtKtfwRMRSvlsiC8JY/edit> · <https://bimmercode.app/cars/f20>

### Einheitenwahl für Sportanzeigen (kW/PS, Nm/lb-ft)

<a id="hu_entrysport_displays_unit"></a>`hu_entry.sport_displays_unit` · Bereich: 3 · SG **HU_ENTRY** · Kategorie iDrive

Bei HU_CIC dokumentiert: EFF_DYN_SPORT_UNIT=aktiv blendet in den iDrive-Einstellungen die Einheitenwahl für die Sportanzeige ein. Laut Forum-Snippets blieb die Anzeige bei manchen trotzdem in kW/Nm.

- **Parameter:** `EFF_DYN_SPORT_UNIT` (3000)
- **Werte:** `nicht_aktiv` = keine Einheitenwahl; `aktiv` = Einheitenwahl im Einstellungsmenü
- **Hardware:** Sportanzeigen müssen funktionieren (siehe hu_entry.sport_displays)
- **Software:** BimmerCode-Expertenmodus / E-Sys
- **Aufwand / Risiko / Nutzen:** mittel / gering / gering
- **Kompatibilität (dein F20):** unbekannt · **Nachweis:** Experimentell
- **Hinweise:** Nur für HU_CIC belegt. Für HU_ENTRY unbekannt.
- **Quellen:** <https://docs.google.com/spreadsheets/d/16O4RKIMekWFCs5jPW3T_7li0yIEvgZfFI0u3l0RmSwU/pubhtml> · <https://docs.google.com/spreadsheets/d/1G_C7954Z4094jLdbR0QjqXQYY6w6-rToothcTUPb5Fs/edit>

### SPORT-Modus im iDrive konfigurierbar

<a id="hu_entrysport_mode_configurable"></a>`hu_entry.sport_mode_configurable` · Bereich: 3 · SG **HU_ENTRY** · Kategorie Antrieb/Fahrdynamik

Für HU_CIC dokumentiert: Macro_fds (3000) popup_only → popup_and_config. bmw-syndikat führt für F20/F21 MAKRO_FDS / Icmkod_b_sportsindividualisierbar ('Sportmodus konfigurierbar machen'). BimmerCode bietet 'SPORT driving mode configurable' (1 von 2, 2 von 2 im ICMQL) an.

- **BimmerCode:** SPORT driving mode configurable (unknown)
- **Parameter:** `Macro_fds`, `MAKRO_FDS` (3000)
- **Werte:** `popup_only` = nur Popup; `popup_and_config` = Popup + Konfiguration im iDrive
- **Hardware:** Fahrerlebnisschalter; Teil 2 im ICMQL
- **Software:** -
- **Aufwand / Risiko / Nutzen:** mittel / gering / gering
- **Kompatibilität (dein F20):** unbekannt · **Nachweis:** Unbekannt
- **Hinweise:** Die BimmerCode-Liste zeigt für Teil 1 kein Steuergerät an. Ob Teil 1 HU_ENTRY betrifft, ist unklar. Bei einem 116i ohne adaptive Dämpfer/Lenkung ist der Nutzen gering.
- **Quellen:** <https://docs.google.com/spreadsheets/d/16O4RKIMekWFCs5jPW3T_7li0yIEvgZfFI0u3l0RmSwU/pubhtml> · <https://www.bmw-syndikat.de/bmwsyndikatforum/bmw_codieren_datenbank.asp?goto=83> · <https://bimmercode.app/cars/f20>

### Reifendruck/-temperatur im iDrive

<a id="hu_entrytpms_display"></a>`hu_entry.tpms_display` · Bereich: 3 · SG **HU_ENTRY** · Kategorie iDrive

Für HU_CIC/HU_NBT dokumentiert: RDC_SAFETY (3001) aktiv zeigt Druck und Temperatur. Eine Sammlung nennt für HU_NBT RDC_DRUCK_TEMP (druck → druck_und_temperatur). BimmerCode 'Tire pressure control' gibt es nur für HU_NBT/HU_NBT_EVO. Voraussetzung sind RDC-Sensoren.

- **BimmerCode:** Tire pressure control (unknown)
- **Parameter:** `RDC_SAFETY`, `RDC_DRUCK_TEMP` (3001)
- **Werte:** `aktiv` = RDC_SAFETY: Druck und Temperatur anzeigen (CIC/NBT); `druck_und_temperatur` = RDC_DRUCK_TEMP: Druck + Temperatur (NBT, laut Sammlung)
- **Hardware:** RDC-Sensoren (nicht nur Reifenpannenanzeige); HU_CIC/HU_NBT
- **Software:** -
- **Aufwand / Risiko / Nutzen:** mittel / gering / gering
- **Kompatibilität (dein F20):** unbekannt · **Nachweis:** Unbekannt
- **Hinweise:** Erst prüfen, ob das Auto RDC-Sensoren hat. Für HU_ENTRY kein Beleg.
- **Quellen:** <https://docs.google.com/spreadsheets/d/1UreLsK1PwycTWeW6OL71HOoVpLtKtfwRMRSvlsiC8JY/edit> · <https://docs.google.com/spreadsheets/d/1G_C7954Z4094jLdbR0QjqXQYY6w6-rToothcTUPb5Fs/edit> · <https://raw.githubusercontent.com/Dauxdu/bmw-coding/HEAD/e-sys/02-Codings/Head-Unit/iDrive-Features.md> · <https://bimmercode.app/cars/f20>

### Klimaanlage: Ein/Aus-Zustand speichern

<a id="ihkaac_memory"></a>`ihka.ac_memory` · Bereich: 3 · SG **IHKA** · Kategorie Klima

Letzter A/C-Zustand bleibt nach Neustart erhalten.

- **BimmerCode:** Air Conditioning setting memory (standard)
- **Parameter:** `MEMORY_OFF`, `OFF_MEMORY` (3002 (IHKA) / 3003 (IHKA_VA02))
- **Werte:** `aktiv` = Zustand speichern (Botho: Standard aktiv bei IHKA_VA02); `nicht_aktiv` = nicht speichern
- **Hardware:** Klimaautomatik (IHKA).
- **Software:** Name je Variante: MEMORY_OFF (IHKA/IHKA_VA02) bzw. OFF_MEMORY (IHKA_CBF, andere Baureihen).
- **Aufwand / Risiko / Nutzen:** gering / gering / mittel
- **Kompatibilität (dein F20):** unbekannt · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Quellen:** <https://bimmercode.app/cars/f20/> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Botho.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/ekfxisid.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Bundang_Thunder.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Almaretto.xml>

### Klimakompressor nicht automatisch mit AUTO einschalten

<a id="ihkaac_on_with_auto"></a>`ihka.ac_on_with_auto` · Bereich: 3 · SG **IHKA** · Kategorie Klima

Beim Drücken von AUTO schaltet die Klimaanlage (Kompressor) nicht automatisch ein.

- **BimmerCode:** Air Conditioning on in AUTO mode (standard)
- **Parameter:** `AC_NICHT_EIN_BEI_AUTO`, `AC_ON_WITH_AUTO` (3002 (IHKA) / 3003 (IHKA_VA02, IHKA3))
- **Werte:** `AC_NICHT_EIN_BEI_AUTO = Aktiv` = A/C nicht mit AUTO (IHKA, ekfxisid F020/F030); `AC_ON_WITH_AUTO = aktiv` = Standard – A/C mit AUTO (IHKA_VA02, Botho); `AC_ON_WITH_AUTO = nicht_aktiv` = A/C nicht mit AUTO
- **Hardware:** Klimaautomatik (IHKA). Bei manueller Klimaanlage (IHKR) nicht verfügbar.
- **Software:** Parametername hängt von der IHKA-Variante ab (IHKA_CBF/VA01/VA02).
- **Aufwand / Risiko / Nutzen:** gering / gering / mittel
- **Kompatibilität (dein F20):** unbekannt · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Hinweise:** Ob das Fahrzeug IHKA oder IHKR hat, ist offen.
- **Quellen:** <https://bimmercode.app/cars/f20/> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Botho.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/ekfxisid.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Bundang_Thunder.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Almaretto.xml>

### Automatische Umluft (AUC) / Umluft-Automatik-Abschaltung

<a id="ihkaauto_recirculation"></a>`ihka.auto_recirculation` · Bereich: 3 · SG **IHKA** · Kategorie Klima

Automatische Umluftsteuerung über Schadstoffsensor bzw. Verhalten der Umluft-Automatik.

- **BimmerCode:** Automatic Air Recirculation (standard)
- **Parameter:** `UMLUFT_AUTO_AUS`, `AC_ON_WITH_RECIRC` (3003)
- **Werte:** `UMLUFT_AUTO_AUS = aktiv` = Standard laut Botho (IHKA_VA02); `UMLUFT_AUTO_AUS = nicht_aktiv` = Umluft bleibt (Botho); `AC_ON_WITH_RECIRC = nicht_aktiv → aktiv` = laut Botho zusammen geändert
- **Hardware:** IHKA_VA02; AUC-Funktion setzt i. d. R. einen Schadstoffsensor voraus (nicht verifiziert).
- **Software:** IHKA_VA02.
- **Aufwand / Risiko / Nutzen:** gering / gering / gering
- **Kompatibilität (dein F20):** unbekannt · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Hinweise:** Bedeutung der Parameter in den Quellen nur knapp beschrieben → vorsichtig.
- **Quellen:** <https://bimmercode.app/cars/f20/> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Botho.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/ekfxisid.xml>

### Umluft-Zustand speichern

<a id="ihkarecirc_memory"></a>`ihka.recirc_memory` · Bereich: 3 · SG **IHKA** · Kategorie Klima

Letzte Umluft-Einstellung bleibt nach Neustart erhalten.

- **BimmerCode:** Air circulation setting memory (standard)
- **Parameter:** `MEMORY_UMLUFT` (3002 (IHKA) / 3003 (IHKA_VA02))
- **Werte:** `nicht_aktiv` = Standard laut Botho (Umluft wird zurückgesetzt); `aktiv` = Umluft speichern
- **Hardware:** Klimaautomatik (IHKA).
- **Software:** IHKA-Variante prüfen.
- **Aufwand / Risiko / Nutzen:** gering / gering / mittel
- **Kompatibilität (dein F20):** unbekannt · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Recht:** Dauer-Umluft kann Scheibenbeschlag fördern (Sicht) – bewusst nutzen.
- **Quellen:** <https://bimmercode.app/cars/f20/> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Botho.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/ekfxisid.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Bundang_Thunder.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Almaretto.xml>

### Manuelle Klimaanlage (IHKR): keine dokumentierten Optionen

<a id="ihkrno_documented_options"></a>`ihkr.no_documented_options` · Bereich: 3 · SG **IHKR** · Kategorie Klima

Für IHKR wurden weder in der BimmerCode-F20-Liste noch in den Cheat-Dateien Codieroptionen gefunden.

- **Parameter:** –
- **Hardware:** IHKR.
- **Software:** Unbekannt.
- **Aufwand / Risiko / Nutzen:** gering / gering / gering
- **Kompatibilität (dein F20):** unbekannt · **Nachweis:** Unbekannt
- **Hinweise:** BimmerCode listet Klimaoptionen nur für IHKA_CBF, IHKA_VA01, IHKA_VA02.
- **Quellen:** <https://bimmercode.app/cars/f20/>

### Datum im Bordcomputer

<a id="kombidate_in_bc"></a>`kombi.date_in_bc` · Bereich: 3 · SG **KOMBI** · Kategorie Kombiinstrument

BimmerCode 'Date in board computer' aktiviert bzw. deaktiviert die Datumsanzeige im BC. Laut F30-Doku gehört 'Date' zur BC-Liste.

- **BimmerCode:** Date in board computer (standard)
- **Parameter:** –
- **Werte:** `Active` = Datum im BC; `Not active` = kein Datum
- **Hardware:** laut BimmerCode KOMBI L7_BASIS oder L7_MID
- **Software:** BimmerCode
- **Aufwand / Risiko / Nutzen:** gering / gering / gering
- **Kompatibilität (dein F20):** unbekannt · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Hinweise:** Hängt von der KOMBI-Variante ab.
- **Quellen:** <https://bimmercode.app/cars/f20> · <https://archive.org/download/BMWTechnicalTrainingDocuments/ST1113%20F30%20Complete%20Vehicle/06_F30%20Displays%2C%20Indicators%20and%20Controls.pdf>

### ECO-PRO-Anzeigen (Bonusreichweite) im Kombi

<a id="kombieco_pro_display"></a>`kombi.eco_pro_display` · Bereich: 3 · SG **KOMBI** · Kategorie Kombiinstrument

Laut BMW F30-Doku zeigt das Kombi mit erweitertem Funktionsumfang (6WA) im ECO-PRO-Modus u. a. die Bonusreichweite an. 'ECO PRO bonus range' ist Teil der BC-Liste. Codierparameter wurden nicht gefunden.

- **Parameter:** –
- **Hardware:** ECO-PRO-Modus (Fahrerlebnisschalter); Darstellung in der Doku für 6WA beschrieben
- **Software:** keine
- **Aufwand / Risiko / Nutzen:** gering / gering / gering
- **Kompatibilität (dein F20):** unbekannt · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Hinweise:** Der Umfang beim Basis-Kombi des F20 ist unbekannt. Keine Codieroption.
- **Quellen:** <https://archive.org/download/BMWTechnicalTrainingDocuments/ST1113%20F30%20Complete%20Vehicle/06_F30%20Displays%2C%20Indicators%20and%20Controls.pdf>

### MSA-Hinweis 'Auto Start-Stop aus' im Kombi ausblenden

<a id="kombimsa_status_display"></a>`kombi.msa_status_display` · Bereich: 3 · SG **KOMBI** · Kategorie Kombiinstrument

Eine nicht verifizierte Sammlung (F-Serie) nennt MSA_VERFUEGBARANZEIGE_ENABLE (KOMBI 3000), aktiv → nicht_aktiv, um den MSA-Hinweis zu entfernen.

- **Parameter:** `MSA_VERFUEGBARANZEIGE_ENABLE` (3000)
- **Werte:** `aktiv` = Standard laut Sammlung; `nicht_aktiv` = Hinweis ausgeblendet
- **Hardware:** Auto Start-Stop (MSA)
- **Software:** BimmerCode-Expertenmodus / E-Sys
- **Aufwand / Risiko / Nutzen:** mittel / gering / gering
- **Kompatibilität (dein F20):** unbekannt · **Nachweis:** Experimentell
- **Hinweise:** Nur eine, nicht verifizierte Quelle. Die MSA-Abschaltung selbst ist eine FEM-/DME-Codierung (BimmerCode: FEM_01) und gehört ins andere Dossier.
- **Quellen:** <https://raw.githubusercontent.com/Dauxdu/bmw-coding/HEAD/e-sys/02-Codings/Instrument-Cluster.md>

### Zeigertest / 'Needle Sweep' beim Start

<a id="kombineedle_sweep"></a>`kombi.needle_sweep` · Bereich: 3 · SG **KOMBI** · Kategorie Kombiinstrument

Für das F-Serien-KOMBI wurde keine Codierung für einen Zeigertest beim Start gefunden. Das einzige dokumentierte Selbsttest-Element ist Testfunktion 02 'Systemtest' im Testmenü (Inhalt nicht beschrieben).

- **Parameter:** –
- **Hardware:** -
- **Software:** -
- **Aufwand / Risiko / Nutzen:** gering / gering / gering
- **Kompatibilität (dein F20):** unbekannt · **Nachweis:** Unbekannt
- **Hinweise:** Keine Quelle gefunden.

### Motoröltemperatur anzeigen

<a id="kombioil_temperature"></a>`kombi.oil_temperature` · Bereich: 3 · SG **KOMBI** · Kategorie Kombiinstrument

Laut BMW F30-Doku zeigen beim F30 die kleinen Rundinstrumente die Öltemperatur, und Testfunktion 08 zeigt 'Coolant temperature, ambient temperature, engine oil temperature'. Eine Codierung für eine dauerhafte Öltemperaturanzeige beim F20 wurde nicht gefunden.

- **Parameter:** –
- **Hardware:** F-Serien-Kombi; Öltemperatursignal der DME
- **Software:** keine (Testmenü)
- **Aufwand / Risiko / Nutzen:** gering / gering / mittel
- **Kompatibilität (dein F20):** unbekannt · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Hinweise:** 'documented' bezieht sich auf den F30. Ob das F20-Kombi eine Öltemperaturanzeige hat und ob der N13 den Wert liefert, ist unbekannt.
- **Quellen:** <https://archive.org/download/BMWTechnicalTrainingDocuments/ST1113%20F30%20Complete%20Vehicle/06_F30%20Displays%2C%20Indicators%20and%20Controls.pdf>

### Gong beim Einlegen des Rückwärtsgangs

<a id="kombireverse_gear_chime"></a>`kombi.reverse_gear_chime` · Bereich: 3 · SG **KOMBI** · Kategorie Kombiinstrument

Eine nicht verifizierte Sammlung nennt R_GANG_AKUSTIK_ENABLE (KOMBI 3000), aktiv → nicht_aktiv.

- **Parameter:** `R_GANG_AKUSTIK_ENABLE` (3000)
- **Werte:** `aktiv` = Gong aktiv (Standard laut Sammlung); `nicht_aktiv` = kein Gong
- **Hardware:** -
- **Software:** BimmerCode-Expertenmodus / E-Sys
- **Aufwand / Risiko / Nutzen:** mittel / gering / gering
- **Kompatibilität (dein F20):** unbekannt · **Nachweis:** Experimentell
- **Hinweise:** Ob ein Schaltgetriebe-F20 überhaupt einen R-Gang-Gong hat, ist nicht belegt.
- **Quellen:** <https://raw.githubusercontent.com/Dauxdu/bmw-coding/HEAD/e-sys/02-Codings/Instrument-Cluster.md>

### Schaltpunktanzeige / Ganganzeige (Schaltgetriebe)

<a id="kombishift_point_and_gear_display"></a>`kombi.shift_point_and_gear_display` · Bereich: 3 · SG **KOMBI** · Kategorie Kombiinstrument

Für den F20 mit Schaltgetriebe wurden keine Codierparameter für Schaltpunkt- oder Ganganzeige gefunden. BMW-Handbücher anderer Modelle führen eine 'Schaltpunktanzeige' als Werksfunktion.

- **Parameter:** –
- **Hardware:** Schaltgetriebe
- **Software:** -
- **Aufwand / Risiko / Nutzen:** gering / gering / gering
- **Kompatibilität (dein F20):** unbekannt · **Nachweis:** Unbekannt
- **Hinweise:** Keine Quelle für Codieroptionen. Nicht codieren, ohne einen Parameter im eigenen CAFD zu identifizieren.

### Geschwindigkeitsbegrenzer (LIM) über Tempomat

<a id="kombispeed_limiter_lim"></a>`kombi.speed_limiter_lim` · Bereich: 3 · SG **KOMBI** · Kategorie Antrieb/Fahrdynamik

Eine nicht verifizierte Sammlung nennt KOMBI 3003 SLD_ENABLE=aktiv plus im ICM SLD_Funktion=aktiv, C_Umschaltung_ACC_DCC=zugelassen und LDM_SET_Taste=nur_SET__O (alle vier nötig). Die 'Set'-Taste arbeitet dann als LIM-Taste.

- **Parameter:** `SLD_ENABLE` (3003)
- **Werte:** `aktiv` = LIM-Funktion Teil 1 (KOMBI)
- **Hardware:** Tempomat; ICM-Codierung zusätzlich nötig
- **Software:** BimmerCode-Expertenmodus / E-Sys (KOMBI + ICM)
- **Aufwand / Risiko / Nutzen:** hoch / hoch / mittel
- **Kompatibilität (dein F20):** unbekannt · **Nachweis:** Experimentell
- **Recht:** Eingriff in eine Fahrerassistenzfunktion. Fehlfunktion kann sicherheitsrelevant sein.
- **Hinweise:** Die ICM-Parameter (SLD_Funktion, C_Umschaltung_ACC_DCC, LDM_SET_Taste) stehen hier nur im Text. Einzige Quelle ist nicht verifiziert. Ausstattung mit Tempomat am Auto prüfen.
- **Quellen:** <https://raw.githubusercontent.com/Dauxdu/bmw-coding/HEAD/e-sys/02-Codings/Instrument-Cluster.md>

### Geschwindigkeitswarnung (Benutzereinstellung)

<a id="kombispeed_warning"></a>`kombi.speed_warning` · Bereich: 3 · SG **KOMBI** · Kategorie Kombiinstrument

In BMW-Handbüchern anderer Modelle (z. B. X3) ist die Geschwindigkeitswarnung eine iDrive-Benutzereinstellung (Fahrzeugeinstellungen → Geschwindigkeitswarnung → 'Warnen bei'). Keine Codierung nötig.

- **Parameter:** –
- **Hardware:** keine
- **Software:** keine
- **Aufwand / Risiko / Nutzen:** gering / gering / mittel
- **Kompatibilität (dein F20):** wahrscheinlich kompatibel · **Nachweis:** Technisch wahrscheinlich
- **Hinweise:** Für F20/HU_ENTRY nicht direkt belegt. Im Bordhandbuch des Autos prüfen.
- **Quellen:** <https://www.manualslib.com/manual/2549622/Bmw-X3.html?page=148>

### SPORT+ als zusätzlicher Fahrmodus

<a id="kombisport_plus"></a>`kombi.sport_plus` · Bereich: 3 · SG **KOMBI** · Kategorie Antrieb/Fahrdynamik

BimmerCode 'SPORT+ driving mode (2 von 2)' im KOMBI fügt SPORT+ hinzu. Teil 1 muss im ICMQL aktiviert werden. Eine nicht verifizierte Sammlung nennt für die Kombi-Anzeige FDS_MENUE_TEXT_1…4 und FDS_MENUE_SIGNAL_1…4 (menue_4 → menue_3).

- **BimmerCode:** SPORT+ driving mode (2 of 2) (standard)
- **Parameter:** `FDS_MENUE_TEXT_1`, `FDS_MENUE_TEXT_2`, `FDS_MENUE_TEXT_3`, `FDS_MENUE_TEXT_4`, `FDS_MENUE_SIGNAL_1`, `FDS_MENUE_SIGNAL_2`, `FDS_MENUE_SIGNAL_3`, `FDS_MENUE_SIGNAL_4` (3000)
- **Werte:** `menue_4` = Standard laut Sammlung; `menue_3` = SPORT+-Symbol/-Signal laut Sammlung; `Active` = BimmerCode-Wert (2 von 2)
- **Hardware:** laut BimmerCode KOMBI L6 BO, L7_BASIS oder L7_MID + ICMQL (Teil 1)
- **Software:** BimmerCode
- **Aufwand / Risiko / Nutzen:** gering / mittel / gering
- **Kompatibilität (dein F20):** unbekannt · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Recht:** SPORT+ verändert u. a. die DSC-Eingriffsschwellen. Fahrsicherheit beachten.
- **Hinweise:** 'documented' bezieht sich auf die BimmerCode-Option. Die FDS_MENUE_*-Namen sind nicht verifiziert. Ob das ICM des Autos als ICMQL erkannt wird, ist offen.
- **Quellen:** <https://bimmercode.app/cars/f20> · <https://raw.githubusercontent.com/Dauxdu/bmw-coding/HEAD/e-sys/02-Codings/Instrument-Cluster.md>

### Start-Logo im Kombiinstrument

<a id="kombistart_logo"></a>`kombi.start_logo` · Bereich: 3 · SG **KOMBI** · Kategorie Kombiinstrument

Ändert das Logo beim Hochfahren des Kombis. Community-Tabelle: BMW_LOGO (3000) AG → MPM (M Performance). bmw-syndikat (F20/F21 gelistet): BMW_LOGO, MPM_ENABLE, MPM_LOGO. BimmerCode 'Start logo' bietet die Werte 50d, 135i, 140i, 235i, 240i, 340i, AG, M Performance, M2, M3, M4, M4 GTS und PHEV.

- **BimmerCode:** Start logo (standard)
- **Parameter:** `BMW_LOGO`, `MPM_ENABLE`, `MPM_LOGO` (3000)
- **Werte:** `AG` = Standardwert laut Community-Tabelle (vermutlich Standard-Logo; eine Sammlung behauptet 'Alpina' – widersprüchlich); `MPM` = M-Performance-Logo
- **Hardware:** laut BimmerCode KOMBI L7_BASIS oder L7_MID
- **Software:** BimmerCode
- **Aufwand / Risiko / Nutzen:** gering / gering / gering
- **Kompatibilität (dein F20):** unbekannt · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Hinweise:** Hängt von der KOMBI-Variante ab (BimmerCode nennt L6 BO hier nicht). Werte für MPM_ENABLE/MPM_LOGO wurden nicht gefunden.
- **Quellen:** <https://bimmercode.app/cars/f20> · <https://docs.google.com/spreadsheets/d/16O4RKIMekWFCs5jPW3T_7li0yIEvgZfFI0u3l0RmSwU/pubhtml> · <https://www.bmw-syndikat.de/bmwsyndikatforum/bmw_codieren_datenbank.asp?goto=83> · <https://raw.githubusercontent.com/Dauxdu/bmw-coding/HEAD/e-sys/02-Codings/Instrument-Cluster.md>

### Lautstärke des Blinkertickens

<a id="kombiturn_signal_tick_volume"></a>`kombi.turn_signal_tick_volume` · Bereich: 3 · SG **KOMBI** · Kategorie Kombiinstrument

Lautstärkekennlinie des Blinkergeräuschs im Kombi.

- **Parameter:** `BLINKER_VOLUME_CONTI` (300B)
- **Werte:** `E0, F0, FF, FF` = Standard laut Botho; `A0, B0, C0, FF` = leiser
- **Hardware:** Quelle bezieht sich auf KOMBI L7_MID; Kombi-Variante des Fahrzeugs (2012) unbekannt.
- **Software:** KOMBI-Variante prüfen.
- **Aufwand / Risiko / Nutzen:** gering / gering / gering
- **Kompatibilität (dein F20):** unbekannt · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Hinweise:** Nur eine Quelle; Mehrbyte-Wert.
- **Quellen:** <https://github.com/packetpilot/bmw-f/blob/master/cheats/Botho.xml>

### Kombi nachts weiß statt orange

<a id="kombiwhite_night_illumination"></a>`kombi.white_night_illumination` · Bereich: 3 · SG **KOMBI** · Kategorie Kombiinstrument

Community-Tabelle: DIM_NACHT_EIN (Block 3007) von werte 32 auf FF. Das Kombi bleibt nachts weiß. Laut Tabelle wird damit auch die Nachtumschaltung des Navis deaktiviert.

- **Parameter:** `DIM_NACHT_EIN` (3007)
- **Werte:** `werte=32` = Standard (laut Tabelle); `werte=FF` = weiß bei Nacht
- **Hardware:** KOMBI mit TFT; Fahrzeug der Tabelle nicht genannt (F-Serie)
- **Software:** BimmerCode-Expertenmodus / E-Sys
- **Aufwand / Risiko / Nutzen:** mittel / gering / gering
- **Kompatibilität (dein F20):** unbekannt · **Nachweis:** Experimentell
- **Hinweise:** Für den 2012er F20-KOMBI nicht belegt. Eine helle Anzeige kann nachts blenden.
- **Quellen:** <https://docs.google.com/spreadsheets/d/16O4RKIMekWFCs5jPW3T_7li0yIEvgZfFI0u3l0RmSwU/pubhtml> · <https://raw.githubusercontent.com/Dauxdu/bmw-coding/HEAD/e-sys/02-Codings/Instrument-Cluster.md>

### PDC-Lautstärke / Absenkung der Audioquelle

<a id="pdcvolume_and_mute"></a>`pdc.volume_and_mute` · Bereich: 3 · SG **REM** · Kategorie Einparkhilfe

Lautstärke des PDC-Signals bzw. Absenkung des Radios während PDC.

- **Parameter:** –
- **Hardware:** PDC.
- **Software:** Bei neueren Head-Units laut Betriebsanleitungen ein iDrive-Klangmenü-Punkt; für HU_ENTRY unbekannt.
- **Aufwand / Risiko / Nutzen:** gering / gering / gering
- **Kompatibilität (dein F20):** unbekannt · **Nachweis:** Unbekannt
- **Hinweise:** Kein Codierparameter gefunden → nicht codieren; ggf. im Radio-Klangmenü nachsehen.

### Fensterheber bei geöffneter Tür weiter bedienbar (hinten)

<a id="remwindow_door_open_rear"></a>`rem.window_door_open_rear` · Bereich: 3 · SG **REM** · Kategorie Fenster

Wie vorne, für die hinteren Türen (REM).

- **Parameter:** `FH_TUERAUF_STOP_MAUT` (3050)
- **Werte:** `aktiv` = Standard; `nicht_aktiv` = Fenster hinten bei offener Tür bedienbar
- **Hardware:** Nur 5-Türer mit elektrischen Fensterhebern hinten.
- **Software:** REM_01.
- **Aufwand / Risiko / Nutzen:** gering / gering / gering
- **Kompatibilität (dein F20):** unbekannt · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Hinweise:** Karosserievariante (3-/5-Türer) des Fahrzeugs nicht angegeben.
- **Quellen:** <https://github.com/packetpilot/bmw-f/blob/master/cheats/Botho.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Almaretto.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Kip_M3.xml>

### Motor-Live-Daten

<a id="dmelive_data"></a>`dme.live_data` · Bereich: 4 · SG **DME** · Kategorie Antrieb/Fahrdynamik

Live-Daten (Sensorwerte), Datenlogging und Fehlerspeicher sind keine Codierung, sondern Diagnosefunktionen der separaten App BimmerLink (gleicher Hersteller).

- **Parameter:** –
- **Hardware:** OBD-Adapter (wie für BimmerCode).
- **Software:** BimmerLink-App (separat).
- **Aufwand / Risiko / Nutzen:** gering / gering / mittel
- **Kompatibilität (dein F20):** wahrscheinlich kompatibel · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Hinweise:** Welche Messwerte für den N13 konkret angeboten werden, ist auf der Website nicht aufgeschlüsselt → [UNBEKANNT].
- **Quellen:** <https://bimmerlink.app/>

### Batterietyp/-kapazität

<a id="fem_bodybattery_type"></a>`fem_body.battery_type` · Bereich: 4 · SG **FEM_BODY** · Kategorie Sonstiges

Typ und Kapazität der 12-V-Batterie; nur nach Batterietausch ändern, danach Batterie registrieren (BimmerLink).

- **BimmerCode:** Battery type (standard)
- **Parameter:** –
- **Werte:** `20 Ah … 105 Ah AGM` = Auswahl in BimmerCode
- **Hardware:** Nur bei geänderter Batterie.
- **Software:** Registrierung separat (BimmerLink o. Ä.).
- **Aufwand / Risiko / Nutzen:** gering / mittel / gering
- **Kompatibilität (dein F20):** wahrscheinlich kompatibel · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Hinweise:** Falscher Typ → falsche Ladestrategie.
- **Quellen:** <https://bimmercode.app/cars/f20/> · <https://bimmerlink.app/>

### Freischaltcodes (FSC/SWT) der Headunit

<a id="hu_entryfsc_enable_codes"></a>`hu_entry.fsc_enable_codes` · Bereich: 4 · SG **HU_ENTRY** · Kategorie Sonstiges

Laut BMW SI B65 09 16 benötigt die ENTRY-Headunit Freischaltcodes ('REQUIRES ENABLE CODES FSC/SWT'). Relevant bei Tausch, Nachrüstung oder Programmierung, nicht für normales Codieren.

- **Parameter:** –
- **Hardware:** HU_ENTRY
- **Software:** ISTA/E-Sys bzw. Werkstatt bei Tausch/Programmierung
- **Aufwand / Risiko / Nutzen:** hoch / mittel / gering
- **Kompatibilität (dein F20):** kompatibel · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Hinweise:** Informationseintrag. Relevant vor allem für einen späteren Headunit-Retrofit (z. B. NBT), der hier nicht untersucht wurde.
- **Quellen:** <https://static.nhtsa.gov/odi/tsbs/2018/MC-10154755-9999.pdf>

### Software-Update gegen 'NO SIGNAL' am CID (I-Stufe)

<a id="hu_entryistufe_update_cid_no_signal"></a>`hu_entry.istufe_update_cid_no_signal` · Bereich: 4 · SG **HU_ENTRY** · Kategorie Sonstiges

BMW SI B65 10 12: Bei HU-B ('also called Radio Professional or ENTRY head unit') im F30 aus SOP bis 07/2012 bleibt das CID sporadisch dunkel und zeigt 'NO SIGNAL' (Fehler B7F8C3). Abhilfe: Fahrzeugtest mit ISTA, ggf. Headunit tauschen, dann mit ISTA/P programmieren auf I-Stufe F020-12-11-504 oder höher.

- **Parameter:** –
- **Hardware:** HU-B/HU_ENTRY, frühe Produktion
- **Software:** ISTA/P (Werkstatt) bzw. Programmierung; nicht mit BimmerCode
- **Aufwand / Risiko / Nutzen:** hoch / mittel / mittel
- **Kompatibilität (dein F20):** wahrscheinlich kompatibel · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Hinweise:** Das SI gilt für den F30. Der F20 läuft auf derselben F020-Baureihen-Plattform (I-Stufe F020-...). Relevanz daher wahrscheinlich, aber nicht für den F20 belegt. Nur bei Symptomen relevant. Vorher die aktuelle I-Stufe auslesen.
- **Quellen:** <https://static.nhtsa.gov/odi/tsbs/2013/MC-10149314-9999.pdf>

### Hardware-Identifikation HU_ENTRY (Radio Professional / HU-B)

<a id="hu_entryplatform_identification"></a>`hu_entry.platform_identification` · Bereich: 4 · SG **HU_ENTRY** · Kategorie Sonstiges

Informationseintrag, keine Codierung. BMW nennt für SA663 Radio Professional CD im F30 (SOP bis 7/2013) die 'ENTRY CONTI – Entry Media by Continental'. Die spätere 'ENTRY HU-B1' (Entry Media/Entry Navigation) stammt von Magneti Marelli (u. a. F22/F30 ab 7/2014). Die BMW-Schulungsunterlage beschreibt die Basic Headunit (HU-B) so: 6,5"-CID über APIX, Controller mit nur fünf Funktionstasten, AM/FM-Doppeltuner, Telefon (6NH) in der Headunit, kein SD-Slot, nicht reparierbar, Ethernet FEM→HU nur für Software-Updates.

- **Parameter:** –
- **Hardware:** Radio Professional (SA663), HU_ENTRY
- **Software:** keine
- **Aufwand / Risiko / Nutzen:** gering / gering / mittel
- **Kompatibilität (dein F20):** wahrscheinlich kompatibel · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Hinweise:** Die Herstellerangabe (Continental) gilt laut SI für den F30 (US-Markt). Für den F20 aus 01/2012 ist sie wahrscheinlich, aber nicht belegt. Betriebssystem und SoC sind nicht öffentlich dokumentiert.
- **Quellen:** <https://static.nhtsa.gov/odi/tsbs/2018/MC-10154755-9999.pdf> · <https://static.nhtsa.gov/odi/tsbs/2013/MC-10149314-9999.pdf> · <https://archive.org/download/BMWTechnicalTrainingDocuments/ST1113%20F30%20Complete%20Vehicle/07_F30_Entertainment_and_Communication1.pdf>

### Kombi-Testmenü (verstecktes Testmenü)

<a id="kombitest_functions"></a>`kombi.test_functions` · Bereich: 4 · SG **KOMBI** · Kategorie Kombiinstrument

Offiziell dokumentiert (BMW ST1113, F30): Klemme 15 EIN, Reset-Taste im Kombi 10 s halten. Frei zugänglich sind nur die Funktionen 01–04. Die Entsperrung erfolgt über Testfunktion 04 mit der Quersumme der letzten fünf FIN-Stellen. Funktionen: 01 Identifikation, 02 Systemtest, 03 Testende, 04 Entsperren, 05 Momentanverbrauch, 06 Reichweite/Verbrauch, 07 Tankgeber, 08 Kühlmittel/Außen/Motoröl-Temperatur, 09 BC-Mittelwerte, 10 Tacho/Drehzahlmesser, 11 Bordnetzspannung, 12 Akustik, 13 Fehlerspeicher, 14 LCD dimmen, 15 PWM dimmen, 16 CBS, 17 Check-Control, 18 Korrekturfaktor Verbrauch, 19 Software-Reset/RAM reload.

- **Parameter:** –
- **Werte:** `04` = Entsperren mit Quersumme der letzten 5 FIN-Stellen; `08` = Kühlmittel-, Außen-, Motoröltemperatur; `18` = Korrekturfaktor Verbrauch (verändert Werte – Vorsicht); `19` = Software-Reset/RAM reload
- **Hardware:** F-Serien-Kombi mit Reset-Taste
- **Software:** keine (Bedienung am Kombi)
- **Aufwand / Risiko / Nutzen:** gering / gering / mittel
- **Kompatibilität (dein F20):** wahrscheinlich kompatibel · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Hinweise:** Belegt für den F30. Für den F20 (gleiche Kombi-Generation) wahrscheinlich, aber nicht verifiziert. Beenden: Kl. 15 aus, Taste > 10 s, Testfunktion 03 und dann 19. Beim Verlassen wird wieder gesperrt. Die E-Serien-Nummerierung aus Drittquellen gilt nicht.
- **Quellen:** <https://archive.org/download/BMWTechnicalTrainingDocuments/ST1113%20F30%20Complete%20Vehicle/06_F30%20Displays%2C%20Indicators%20and%20Controls.pdf>

### Gurtwarnung (Gong/Anzeige) Fahrer/Beifahrer

<a id="acsmseat_belt_reminder"></a>`acsm.seat_belt_reminder` · Bereich: 5 · SG **ACSM** · Kategorie Sicherheit

Akustische und optische Gurtwarnung, Vorwarnung beim Abschnallen, Gurtzustandsanzeige im Kombi.

- **BimmerCode:** Seat belt reminder driver seat / passenger seat / Seat belt indicator … (standard)
- **Parameter:** `SeatBeltReminder_SBR_Fahrer`, `SeatBeltReminder_SBR_Beifahrer`, `SBR_PreWarning_Fahrer`, `SBR_PreWarning_Beifahrer`, `Gurtzustandsanzeige_Fahrer_GWF_GZA_FA`, `Gurtzustandsanzeige_Beifahrer_GWF_GZA_BF` (3000)
- **Werte:** `aktiv / 01` = Standard; `nicht_aktiv / 00` = deaktiviert
- **Hardware:** ACSM_4B/ACSM_4C.
- **Software:** ACSM-Variante des Fahrzeugs prüfen (Quellen: ACSM_4B für F020/F030).
- **Aufwand / Risiko / Nutzen:** gering / sicherheitskritisch / gering
- **Kompatibilität (dein F20):** wahrscheinlich kompatibel · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Recht:** Sicherheitsfunktion; Gurtpflicht nach § 21a StVO bleibt. Deaktivieren nicht empfohlen – nur dokumentiert.
- **Hinweise:** NICHT codieren.
- **Quellen:** <https://bimmercode.app/cars/f20/> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Botho.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Bundang_Thunder.xml> · <https://docs.google.com/spreadsheets/d/16O4RKIMekWFCs5jPW3T_7li0yIEvgZfFI0u3l0RmSwU/pubhtml>

### Gurtwarnung: Dauer

<a id="acsmseat_belt_reminder_duration"></a>`acsm.seat_belt_reminder_duration` · Bereich: 5 · SG **ACSM** · Kategorie Sicherheit

Dauer der akustischen Gurtwarnung.

- **BimmerCode:** Seat belt reminder duration (standard)
- **Parameter:** `GWF_SBR_WARNDAUER` (3001)
- **Werte:** `64 (hex)` = 100 s – Standard laut Botho; `0A / 05 (hex)` = 10 s / 5 s (Beispiele); `5 … 100 seconds` = Auswahl in BimmerCode
- **Hardware:** ACSM_4B/4C.
- **Software:** ACSM-Variante prüfen.
- **Aufwand / Risiko / Nutzen:** gering / sicherheitskritisch / gering
- **Kompatibilität (dein F20):** wahrscheinlich kompatibel · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Recht:** Siehe acsm.seat_belt_reminder.
- **Hinweise:** Nur dokumentieren.
- **Quellen:** <https://bimmercode.app/cars/f20/> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Botho.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/ekfxisid.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Bundang_Thunder.xml> · <https://docs.google.com/spreadsheets/d/16O4RKIMekWFCs5jPW3T_7li0yIEvgZfFI0u3l0RmSwU/pubhtml>

### MSA-Speicher im DME (G-Baureihen)

<a id="dmemsa_in_dme"></a>`dme.msa_in_dme` · Bereich: 5 · SG **DME** · Kategorie Antrieb/Fahrdynamik

Bei G-Modellen liegt TCM_MSA_MEMORY im DME (DME_BAC2/DME_DDE8xx), nicht im FEM.

- **Parameter:** `TCM_MSA_MEMORY` (3020 (DME_BAC2))
- **Werte:** `01 / On` = Merken (G-Modelle)
- **Hardware:** G-Baureihe mit B-Motor.
- **Software:** –
- **Aufwand / Risiko / Nutzen:** hoch / hoch / gering
- **Kompatibilität (dein F20):** nicht kompatibel · **Nachweis:** Nicht kompatibel
- **Recht:** DME-Codierung ist emissionsrelevant; Forum warnt vor Sperrung des DME bei neueren Softwareständen.
- **Hinweise:** Für F20/N13 gilt fem_body.msa_memory (FEM).
- **Quellen:** <https://github.com/packetpilot/bmw-f/blob/master/cheats/Bundang_Thunder.xml> · <https://f90.bimmerpost.com/forums/showthread.php?p=29809376>

### Fahrpedalkennlinie je Fahrmodus

<a id="dmethrottle_map_per_mode"></a>`dme.throttle_map_per_mode` · Bereich: 5 · SG **DME** · Kategorie Antrieb/Fahrdynamik

Laut BMW-Pressematerial verändert ECO PRO das Ansprechverhalten des Fahrpedals; SPORT schärft die Kennlinie. Keine Codieroption dokumentiert.

- **Parameter:** –
- **Hardware:** –
- **Software:** –
- **Aufwand / Risiko / Nutzen:** hoch / sicherheitskritisch / gering
- **Kompatibilität (dein F20):** unbekannt · **Nachweis:** Unbekannt
- **Recht:** Eingriffe in die Motorsteuerung sind emissions- und typgenehmigungsrelevant → NICHT codieren.
- **Hinweise:** Nur Beschreibung der Serienfunktion; Kennlinie ist keine Codieroption.
- **Quellen:** <https://newsroom.bmwgroup.com/global/the-new-bmw-1-series>

### Launch Control

<a id="dsclaunch_control"></a>`dsc.launch_control` · Bereich: 5 · SG **DSC** · Kategorie Antrieb/Fahrdynamik

Launch-Control-Funktion im DSC (mit EGS).

- **Parameter:** `C_Funktion_LaunchControl` (3000)
- **Werte:** `01` = aktiv (DSC_CT01, zusammen mit EGS)
- **Hardware:** Automatikgetriebe (EGS) erforderlich – Fahrzeug hat Schaltgetriebe.
- **Software:** DSC_CT01 + EGS.
- **Aufwand / Risiko / Nutzen:** mittel / sicherheitskritisch / gering
- **Kompatibilität (dein F20):** nicht kompatibel · **Nachweis:** Nicht kompatibel
- **Recht:** Fahrdynamik-/Antriebseingriff, nur dokumentieren.
- **Hinweise:** Für Handschalter nicht anwendbar.
- **Quellen:** <https://github.com/packetpilot/bmw-f/blob/master/cheats/Bundang_Thunder.xml>

### Elektrische Lenkung (EPS): keine dokumentierten Komfortoptionen

<a id="epsno_user_coding"></a>`eps.no_user_coding` · Bereich: 5 · SG **EPS** · Kategorie Sicherheit

Für die EPS des F20 wurden keine Komfort-Codierungen gefunden; 'IcmKod_B_Sportlenkung' (ICM) setzt Variable Sportlenkung voraus.

- **Parameter:** –
- **Hardware:** –
- **Software:** –
- **Aufwand / Risiko / Nutzen:** hoch / sicherheitskritisch / gering
- **Kompatibilität (dein F20):** unbekannt · **Nachweis:** Unbekannt
- **Recht:** Lenkung = sicherheitskritisch → nicht codieren.
- **Hinweise:** Nur dokumentiert.

### Bremskraftanzeige / Notbremssignal: Art

<a id="fem_bodyess_type"></a>`fem_body.ess_type` · Bereich: 5 · SG **FEM_BODY** · Kategorie Beleuchtung

Art der Bremskraftanzeige bei starker Bremsung: Blinken (Notbremssignal) oder Flächenvergrößerung.

- **BimmerCode:** Brake Force Display type (standard)
- **Parameter:** `ESS_AKTIVIERBARER_AUSGANG` (3060)
- **Werte:** `bremslicht_blinkend` = Bremsleuchten blinken (Standard laut Botho.xml); `flachenvergroesserung` = Flächenvergrößerung (Schreibweise laut F87-Spreadsheet); `Area enlargement / Flashing / Not active` = Auswahl in BimmerCode
- **Hardware:** Keine.
- **Software:** Parametername/Wertebezeichnung können je nach I-Stufe/CAFD-Version abweichen (Quellen beziehen sich auf CAFD 00000794 FEM_BODY, Serie F020/F030). Vor dem Codieren Ist-Wert in BimmerCode auslesen und Backup sichern. BimmerCode: zusätzlich REM 'Brake Force Display lights' = Brake lights.
- **Aufwand / Risiko / Nutzen:** mittel / sicherheitskritisch / gering
- **Kompatibilität (dein F20):** wahrscheinlich kompatibel · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Recht:** Notbremssignal nach ECE R48 6.23: alle Leuchten blinken phasengleich mit 4,0 ± 1,0 Hz, Aktivierung nur über 50 km/h; Abweichungen verletzen die Typgenehmigung. 'Not active' entfernt eine Sicherheitsfunktion.
- **Hinweise:** Sicherheitsrelevant – nur dokumentieren, Werkseinstellung belassen.
- **Quellen:** <https://bimmercode.app/cars/f20/> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Botho.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/ekfxisid.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Kip_M3.xml> · <https://docs.google.com/spreadsheets/d/1TjoUmnkFYbzdcL8v2DF5fcMixHXSVWRexVV1g2ybG14/edit>

### Motorstart ohne Kupplungspedal (Startsperre)

<a id="fem_bodystart_without_clutch"></a>`fem_body.start_without_clutch` · Bereich: 5 · SG **FEM_BODY** · Kategorie Sicherheit

Hebt die Startbedingung 'Kupplung getreten' beim Schaltgetriebe auf.

- **Parameter:** `TCM_STARTLOCK_CLUTCH` (3020)
- **Werte:** `01 (Standard, abgeleitet)` = Start nur mit getretener Kupplung; `00` = Start ohne Kupplung (Bundang_Thunder)
- **Hardware:** Schaltgetriebe (vorhanden).
- **Software:** Parametername/Wertebezeichnung können je nach I-Stufe/CAFD-Version abweichen (Quellen beziehen sich auf CAFD 00000794 FEM_BODY, Serie F020/F030). Vor dem Codieren Ist-Wert in BimmerCode auslesen und Backup sichern.
- **Aufwand / Risiko / Nutzen:** gering / sicherheitskritisch / gering
- **Kompatibilität (dein F20):** wahrscheinlich kompatibel · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Recht:** Start mit eingelegtem Gang kann das Fahrzeug ungewollt bewegen. Nur dokumentieren, NICHT codieren.
- **Hinweise:** F87-Spreadsheet nennt beim M2 eine BimmerCode-Standardoption 'Start engine without clutch'; für den F20 nicht in der offiziellen Liste.
- **Quellen:** <https://github.com/packetpilot/bmw-f/blob/master/cheats/Bundang_Thunder.xml> · <https://docs.google.com/spreadsheets/d/1TjoUmnkFYbzdcL8v2DF5fcMixHXSVWRexVV1g2ybG14/edit>

### Fahrmodus über Neustart merken

<a id="icmdriving_mode_memory"></a>`icm.driving_mode_memory` · Bereich: 5 · SG **ICM** · Kategorie Antrieb/Fahrdynamik

Letzten Fahrmodus nach Motorneustart beibehalten. Belegt nur für F15 (ICMQL 300A).

- **Parameter:** `fesallowmode4lastfunction`, `fesallowmode2lastfunction`, `feslastfunctioninterval` (300A (F15))
- **Werte:** `aktiv` = Modus darf gemerkt werden (F15); `feslastfunctioninterval = FF` = kein Zurücksetzen (F15)
- **Hardware:** Unbekannt für F20.
- **Software:** Für F20-ICM-Stände nicht belegt.
- **Aufwand / Risiko / Nutzen:** mittel / sicherheitskritisch / gering
- **Kompatibilität (dein F20):** unbekannt · **Nachweis:** Experimentell
- **Recht:** ICM = Fahrdynamik → nur dokumentieren.
- **Hinweise:** Nur F15-Quelle; Übertragbarkeit auf F20 (2012) unbekannt.
- **Quellen:** <https://github.com/packetpilot/bmw-f/blob/master/cheats/Almaretto.xml>

### SPORT-Modus individuell konfigurierbar (iDrive)

<a id="icmsport_configurable"></a>`icm.sport_configurable` · Bereich: 5 · SG **ICM** · Kategorie Antrieb/Fahrdynamik

Menüpunkt 'SPORT konfigurieren' (Fahrwerk/Antrieb getrennt).

- **BimmerCode:** SPORT driving mode configurable (1 of 2) / (2 of 2) (standard)
- **Parameter:** `Macro_fds` (3000 (HU_CIC))
- **Werte:** `popup_only` = Standard (HU_CIC); `popup_and_config` = Konfiguration im iDrive
- **Hardware:** Head-Unit HU_NBT/NBT_EVO (BimmerCode) bzw. HU_CIC (Spreadsheet); Fahrzeug hat HU_ENTRY.
- **Software:** ICMQL + Head-Unit.
- **Aufwand / Risiko / Nutzen:** mittel / mittel / gering
- **Kompatibilität (dein F20):** unwahrscheinlich · **Nachweis:** Unbekannt
- **Hinweise:** BimmerCode-Standardoption setzt laut offizieller Liste HU_NBT/HU_NBT_EVO voraus; für Radio Professional (HU_ENTRY) kein Parameter belegt → mit BimmerCode-Standardmodus nicht verfügbar, Expert-Äquivalent unbekannt.
- **Quellen:** <https://bimmercode.app/cars/f20/> · <https://docs.google.com/spreadsheets/d/16O4RKIMekWFCs5jPW3T_7li0yIEvgZfFI0u3l0RmSwU/pubhtml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/ruben_17non.xml>

### SPORT+ Fahrmodus freischalten

<a id="icmsport_plus"></a>`icm.sport_plus` · Bereich: 5 · SG **ICM** · Kategorie Antrieb/Fahrdynamik

Fügt SPORT+ hinzu (u. a. andere DSC/DTC-Strategie). BimmerCode: zweiteilig ICM + KOMBI.

- **BimmerCode:** SPORT+ driving mode (1 of 2) / SPORT+ driving mode (2 of 2) (standard)
- **Parameter:** `IcmKod_B_S2TBA`, `IcmKod_B_Sportlenkung` (3000)
- **Werte:** `verbaut` = laut Quellen Aktivierung (Quellen widersprechen sich, welcher Parameter nötig ist); `Active` = BimmerCode 'SPORT+ driving mode (1 of 2)' (ICMQL) + '(2 of 2)' (KOMBI)
- **Hardware:** Ab Werk beim F20 nur mit Sport Line + Variabler Sportlenkung (laut BMW-Pressematerial, Such-Snippet). IcmKod_B_Sportlenkung beschreibt Sportlenkung-Hardware.
- **Software:** ICMQL + KOMBI; BimmerCode: 'Use a backup to revert'.
- **Aufwand / Risiko / Nutzen:** mittel / sicherheitskritisch / gering
- **Kompatibilität (dein F20):** unbekannt · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Recht:** Eingriff in DSC/Fahrdynamik-Abstimmung: sicherheitskritisch; Abweichung vom Auslieferungszustand mit möglichen Folgen für Betriebserlaubnis/Versicherung. NUR DOKUMENTIEREN.
- **Hinweise:** Forum: RPA-Fehler nach Codierung möglich. Nicht empfehlen.
- **Quellen:** <https://bimmercode.app/cars/f20/> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Bundang_Thunder.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/ekfxisid.xml> · <https://f30.bimmerpost.com/forums/showthread.php?p=18141876> · <https://bmw-icom-a2-wifi.blogspot.com/2017/11/how-to-code-non-sport-bmw-320i-to-sport.html>

### Fahrmodus beim Start: ECO PRO

<a id="icmstart_in_eco_pro"></a>`icm.start_in_eco_pro` · Bereich: 5 · SG **ICM** · Kategorie Antrieb/Fahrdynamik

Fahrzeug startet immer im ECO-PRO-Modus statt COMFORT.

- **BimmerCode:** Start in ECO mode (standard)
- **Parameter:** `IcmKod_B_InitEco` (3000)
- **Werte:** `nicht_verbaut / 00` = Standard – Start in COMFORT; `verbaut / 01` = Start in ECO PRO
- **Hardware:** Fahrerlebnisschalter (Serie laut BMW-Pressetext).
- **Software:** ICMQL (BimmerCode-Bezeichnung).
- **Aufwand / Risiko / Nutzen:** gering / mittel / gering
- **Kompatibilität (dein F20):** wahrscheinlich kompatibel · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Hinweise:** ICM ist fahrdynamikrelevant → nur dokumentieren; vergleichsweise harmlos, da nur Startmodus.
- **Quellen:** <https://bimmercode.app/cars/f20/> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Botho.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Bundang_Thunder.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Almaretto.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/ekfxisid.xml>

### DSC/DTC-Entflechtung im Kombi

<a id="kombidsc_off_unbundling"></a>`kombi.dsc_off_unbundling` · Bereich: 5 · SG **KOMBI** · Kategorie Sicherheit

KOMBI-Parameter zur getrennten Anzeige/Logik von DSC OFF und DTC.

- **Parameter:** `DSC_OFF_ENTFLECHTUNG_ENABLE` (3000)
- **Werte:** `nicht_aktiv` = Standard laut Botho; `aktiv` = Entflechtung
- **Hardware:** Quelle: KOMBI L7_MID.
- **Software:** –
- **Aufwand / Risiko / Nutzen:** gering / sicherheitskritisch / gering
- **Kompatibilität (dein F20):** unbekannt · **Nachweis:** Experimentell
- **Recht:** DSC-bezogen → sicherheitskritisch, nur dokumentieren.
- **Hinweise:** Botho selbst: 'intérêt à valider' (Nutzen unklar).
- **Quellen:** <https://github.com/packetpilot/bmw-f/blob/master/cheats/Botho.xml>

### Gurtwarnung (nur Dokumentation)

<a id="kombiseatbelt_reminder"></a>`kombi.seatbelt_reminder` · Bereich: 5 · SG **KOMBI** · Kategorie Sicherheit

Die Anzeige erfolgt im Kombi. Laut BimmerCode liegt die Codierung aber im Airbag-Steuergerät ACSM (ACSM_4B/ACSM_4C): Initial seat belt reminder after start, Seat belt indicator (Fahrer/Beifahrer/Fond), Seat belt reminder distance/driver/duration/passenger/speed. Eine Community-Tabelle (F30 2012, E-Sys) nennt im ACSM (3000 Ausstattungsflags) SeatBeltReminder_SBR_Fahrer und SeatBeltReminder_SBR_Beifahrer (aktiv → nicht_aktiv).

- **BimmerCode:** Seat belt reminder driver seat (standard)
- **Parameter:** –
- **Hardware:** ACSM_4B oder ACSM_4C (nicht KOMBI)
- **Software:** BimmerCode
- **Aufwand / Risiko / Nutzen:** gering / sicherheitskritisch / gering
- **Kompatibilität (dein F20):** unbekannt · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Recht:** Sicherheitsfunktion. Das Abschalten wird nicht empfohlen und kann Betriebserlaubnis und Versicherungsschutz berühren. Die Gurtpflicht nach § 21a StVO bleibt unberührt.
- **Hinweise:** Nur zur Dokumentation. Die exakten Parameter gehören zum ACSM und stehen deshalb hier im Text statt in function_names. Ob das ACSM des 2012er F20 als ACSM_4B/4C erkannt wird, ist offen.
- **Quellen:** <https://bimmercode.app/cars/f20> · <https://docs.google.com/spreadsheets/d/1G_C7954Z4094jLdbR0QjqXQYY6w6-rToothcTUPb5Fs/edit>

### Bremskraftanzeige: verwendete Heckleuchten

<a id="remess_lights_mapping"></a>`rem.ess_lights_mapping` · Bereich: 5 · SG **REM** · Kategorie Beleuchtung

Ordnet die Bremskraftanzeige/das Notbremssignal den Bremsleuchten zu.

- **BimmerCode:** Brake Force Display lights (standard)
- **Parameter:** `MAPPING_BRAKEFORCED_L_OUTPUT`, `MAPPING_BRAKEFORCED_R_OUTPUT` (3062)
- **Werte:** `bl_l / bl_r` = Bremsleuchte links/rechts (Standard laut Botho); `Brake lights / Not active` = Auswahl in BimmerCode
- **Hardware:** Almaretto/Kip: Blinken der äußeren Leuchten 'LED only'.
- **Software:** REM_01.
- **Aufwand / Risiko / Nutzen:** gering / sicherheitskritisch / gering
- **Kompatibilität (dein F20):** wahrscheinlich kompatibel · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Recht:** Siehe fem_body.ess_type (ECE R48 6.23).
- **Hinweise:** Werkseinstellung belassen.
- **Quellen:** <https://bimmercode.app/cars/f20/> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Botho.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Almaretto.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Kip_M3.xml>

### Notbremssignal: Verzögerungsschwelle

<a id="fem_bodyess_activation_decel"></a>`fem_body.ess_activation_decel` · Bereich: 6 · SG **FEM_BODY** · Kategorie Sicherheit

Verzögerung, ab der das Notbremssignal aktiviert bzw. deaktiviert wird.

- **BimmerCode:** Brake Force Display activation brake force (standard)
- **Parameter:** `ESS_AKTIVIERUNG_REALE_VERZ`, `ESS_DEAKTIVIERUNG_REALE_VERZ` (3060)
- **Werte:** `0E (hex)` = 7 m/s² – Standard laut Botho.xml (Einheit vermutlich 0,5 m/s²); `06 (hex)` = 3 m/s² (Beispiel Botho); `Weak (5 m/s²) / Medium (7 m/s²) / Hard (8 m/s²)` = Auswahl in BimmerCode
- **Hardware:** Keine.
- **Software:** Parametername/Wertebezeichnung können je nach I-Stufe/CAFD-Version abweichen (Quellen beziehen sich auf CAFD 00000794 FEM_BODY, Serie F020/F030). Vor dem Codieren Ist-Wert in BimmerCode auslesen und Backup sichern.
- **Aufwand / Risiko / Nutzen:** gering / sicherheitskritisch / gering
- **Kompatibilität (dein F20):** wahrscheinlich kompatibel · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Recht:** ECE R48 6.23.7.3.1 knüpft die Aktivierung an das Notbrems-Logiksignal nach R13/R13-H; eine niedrigere Schwelle weicht davon ab → in DE nicht zulässig.
- **Hinweise:** Nicht empfehlen.
- **Quellen:** <https://bimmercode.app/cars/f20/> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Botho.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/ekfxisid.xml> · <https://nsai.ie/images/uploads/certification-automotive/UNECE-R48-04.pdf>

### Notbremssignal: Aktivierungsgeschwindigkeit

<a id="fem_bodyess_activation_speed"></a>`fem_body.ess_activation_speed` · Bereich: 6 · SG **FEM_BODY** · Kategorie Sicherheit

Mindestgeschwindigkeit, ab der das Notbremssignal ausgelöst wird.

- **BimmerCode:** Brake Force Display activation speed (standard)
- **Parameter:** `ESS_AKTIVIERUNG_GESCHW` (3060)
- **Werte:** `32 (hex)` = 50 km/h – Standard laut Botho.xml; `14 (hex)` = 20 km/h (Beispiel Botho); `0A (hex)` = 10 km/h (Beispiel ekfxisid); `5 … 50 km/h` = Auswahl in BimmerCode
- **Hardware:** Keine.
- **Software:** Parametername/Wertebezeichnung können je nach I-Stufe/CAFD-Version abweichen (Quellen beziehen sich auf CAFD 00000794 FEM_BODY, Serie F020/F030). Vor dem Codieren Ist-Wert in BimmerCode auslesen und Backup sichern.
- **Aufwand / Risiko / Nutzen:** gering / sicherheitskritisch / gering
- **Kompatibilität (dein F20):** wahrscheinlich kompatibel · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Recht:** ECE R48 6.23.7.3.1: Aktivierung nur oberhalb 50 km/h. Absenken = Abweichung von der Typgenehmigung → in DE nicht zulässig.
- **Hinweise:** Nicht empfehlen.
- **Quellen:** <https://bimmercode.app/cars/f20/> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Botho.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/ekfxisid.xml> · <https://nsai.ie/images/uploads/certification-automotive/UNECE-R48-04.pdf>

### Nebelscheinwerfer mit Standlicht

<a id="fem_bodyfog_with_parking_lights"></a>`fem_body.fog_with_parking_lights` · Bereich: 6 · SG **FEM_BODY** · Kategorie Beleuchtung

Erlaubt das Einschalten der Nebelscheinwerfer bereits in Lichtschalterstellung Standlicht.

- **BimmerCode:** Fog lights with parking lights (standard)
- **Parameter:** `NSW_EIN_AUF_LDS_STL` (3060)
- **Werte:** `00` = Standard (laut Botho in Ländern wie USA); `01` = Nebelscheinwerfer auch mit Standlicht
- **Hardware:** Nebelscheinwerfer vorne.
- **Software:** Parametername/Wertebezeichnung können je nach I-Stufe/CAFD-Version abweichen (Quellen beziehen sich auf CAFD 00000794 FEM_BODY, Serie F020/F030). Vor dem Codieren Ist-Wert in BimmerCode auslesen und Backup sichern.
- **Aufwand / Risiko / Nutzen:** gering / mittel / gering
- **Kompatibilität (dein F20):** wahrscheinlich kompatibel · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Recht:** Nebelscheinwerfer dürfen nach § 17 Abs. 3 StVO nur bei erheblicher Sichtbehinderung durch Nebel, Schnee oder Regen eingeschaltet sein; als Tagfahrlicht-Ersatz unzulässig (Verwarnungsgeld laut bussgeldkatalog.org). Codierung selbst ändert die Schaltlogik → Grauzone; Nutzung nur bestimmungsgemäß.
- **Hinweise:** Häufig als 'US-Feature' bezeichnet. Für den Alltag kein Mehrwert.
- **Quellen:** <https://bimmercode.app/cars/f20/> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Botho.xml> · <https://www.gesetze-im-internet.de/stvo_2013/__17.html> · <https://www.bussgeldkatalog.org/tagfahrlicht-nebelscheinwerfer/>

### US-Sidemarker (Blinker als Dauerlicht)

<a id="fem_bodyus_sidemarkers"></a>`fem_body.us_sidemarkers` · Bereich: 6 · SG **FEM_BODY** · Kategorie Beleuchtung

Vordere Blinker bzw. Seitenblinker leuchten gedimmt als Seitenmarkierung mit Standlicht/TFL.

- **BimmerCode:** US sidemarkers / US sidemarker brightness / US sidemarker light function (standard)
- **Parameter:** `MAPPING_SIDEMARKER_L_OUTPUT`, `MAPPING_SIDEMARKER_R_OUTPUT`, `MAPPING_SIDEMARKER_L_FUNCTION`, `MAPPING_SIDEMARKER_R_FUNCTION`, `MAPPING_SIDEMARKER_L_PWM_LEVEL_STANDARD` (3063)
- **Werte:** `OUTPUT = off` = Standard; `OUTPUT = fra_v_l / fra_v_r` = Blinker vorne links/rechts als Sidemarker; `FUNCTION 01 → 04` = Funktionszuordnung laut Botho; `Mirror turn signals / Off / Separate lights / Turn signals` = Auswahl in BimmerCode
- **Hardware:** Keine (nutzt vorhandene Blinker).
- **Software:** Parametername/Wertebezeichnung können je nach I-Stufe/CAFD-Version abweichen (Quellen beziehen sich auf CAFD 00000794 FEM_BODY, Serie F020/F030). Vor dem Codieren Ist-Wert in BimmerCode auslesen und Backup sichern.
- **Aufwand / Risiko / Nutzen:** mittel / hoch / gering
- **Kompatibilität (dein F20):** wahrscheinlich kompatibel · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Recht:** In DE unzulässig: ECE R48 6.5.7 verlangt, dass Fahrtrichtungsanzeiger unabhängig von anderen Leuchten schalten; dauerhaft leuchtende Blinker entsprechen nicht der EU-Genehmigung. Forum-Erfahrungen: 'in D offiziell nicht erlaubt'. Risiko: Mängel bei HU, Bußgeld, Erlöschen der Betriebserlaubnis.
- **Hinweise:** NICHT empfehlen.
- **Quellen:** <https://bimmercode.app/cars/f20/> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Botho.xml> · <https://nsai.ie/images/uploads/certification-automotive/UNECE-R48-04.pdf> · <https://www.motor-talk.de/forum/programmierung-auf-us-tagfahrlicht-t829021.html>

### Video in Motion (Video-Sperre während der Fahrt)

<a id="hu_entryvideo_in_motion"></a>`hu_entry.video_in_motion` · Bereich: 6 · SG **HU_ENTRY** · Kategorie iDrive

Dokumentiert für HU_CIC/HU_NBT: SPEEDLOCK_X_KMH_MIN/MAX auf FF, VIDEO_NUR_MIT_HANDBREMSE (CIC) usw. Laut Sammlung unterstützt HU_ENTRY kein Video in Motion. Radio Professional hat ohnehin keine Video-Quelle.

- **BimmerCode:** Video in motion (unknown)
- **Parameter:** `SPEEDLOCK_X_KMH_MIN`, `SPEEDLOCK_X_KMH_MAX`, `VIDEO_NUR_MIT_HANDBREMSE` (3000 HMI)
- **Werte:** `werte=FF` = Geschwindigkeitssperre aufgehoben (CIC/NBT)
- **Hardware:** HU_CIC/HU_NBT mit Videoquelle
- **Software:** -
- **Aufwand / Risiko / Nutzen:** mittel / mittel / gering
- **Kompatibilität (dein F20):** nicht kompatibel · **Nachweis:** Nicht kompatibel
- **Recht:** Video während der Fahrt im Sichtbereich des Fahrers ist in Deutschland unzulässig (§ 23 Abs. 1a StVO).
- **Hinweise:** Die Aussage 'HU_ENTRY does not support Video in Motion' stammt aus einer nicht verifizierten GitHub-Sammlung. Sie ist plausibel, weil die Hardware kein Video abspielt.
- **Quellen:** <https://raw.githubusercontent.com/Dauxdu/bmw-coding/HEAD/e-sys/02-Codings/Head-Unit/Video-in-Motion.md> · <https://docs.google.com/spreadsheets/d/16O4RKIMekWFCs5jPW3T_7li0yIEvgZfFI0u3l0RmSwU/pubhtml> · <https://bimmercode.app/cars/f20>

### Video über USB und zusätzliche Codecs

<a id="hu_entryvideo_usb_codecs"></a>`hu_entry.video_usb_codecs` · Bereich: 6 · SG **HU_ENTRY** · Kategorie iDrive

Für HU_NBT dokumentiert: ENT_CODEC_OGG, ENT_CODEC_XVID, ENT_CODEC_VCD aktiv, API_USB_VIDEO none → both. BimmerCode 'Video via USB' und 'Additional video codecs and formats' gibt es nur für HU_NBT/HU_NBT_EVO.

- **BimmerCode:** Video via USB (unknown)
- **Parameter:** `ENT_CODEC_OGG`, `ENT_CODEC_XVID`, `ENT_CODEC_VCD`, `API_USB_VIDEO` (3000 HMI)
- **Werte:** `aktiv` = Codec aktiv (NBT); `both` = API_USB_VIDEO: Video über USB (NBT)
- **Hardware:** HU_NBT/HU_NBT_EVO
- **Software:** -
- **Aufwand / Risiko / Nutzen:** mittel / gering / gering
- **Kompatibilität (dein F20):** nicht kompatibel · **Nachweis:** Nicht kompatibel
- **Recht:** Videowiedergabe während der Fahrt ist unzulässig (§ 23 Abs. 1a StVO).
- **Hinweise:** HU_ENTRY wird bei BimmerCode nicht als Voraussetzung genannt. Die HU-B hat laut BMW-Doku keine Videofunktion beschrieben.
- **Quellen:** <https://bimmercode.app/cars/f20> · <https://docs.google.com/spreadsheets/d/1UreLsK1PwycTWeW6OL71HOoVpLtKtfwRMRSvlsiC8JY/edit>

### Tachokorrektur (Vorlauf) der Anzeige

<a id="kombispeed_correction"></a>`kombi.speed_correction` · Bereich: 6 · SG **KOMBI** · Kategorie Kombiinstrument

Eine nicht verifizierte Sammlung (F-Serie) nennt BC_V_KORREKTUR in KOMBI 3000: nicht_aktiv zeigt die reale Geschwindigkeit ohne Korrektur. Aus der E-Serie sind BC_V_KORREKTUR und BC_DIGITAL_V_KORREKTUR bekannt. Laut Forum hatte BC_V_KORREKTUR bei US-Fahrzeugen keine Wirkung.

- **Parameter:** `BC_V_KORREKTUR`, `BC_DIGITAL_V_KORREKTUR` (3000)
- **Werte:** `aktiv` = korrigierte (vorlaufende) Anzeige; `nicht_aktiv` = reale Geschwindigkeit (laut Sammlung)
- **Hardware:** KOMBI
- **Software:** BimmerCode-Expertenmodus / E-Sys
- **Aufwand / Risiko / Nutzen:** mittel / mittel / gering
- **Kompatibilität (dein F20):** unbekannt · **Nachweis:** Experimentell
- **Recht:** Der Tacho darf nach UN-ECE-R39 nie weniger als die tatsächliche Geschwindigkeit anzeigen. Analog-Tachowerte (z. B. K_ZAHL_TACHO) nicht verändern.
- **Hinweise:** F-Serien-Beleg nur aus nicht verifizierter Sammlung. Nicht empfohlen.
- **Quellen:** <https://raw.githubusercontent.com/Dauxdu/bmw-coding/HEAD/e-sys/02-Codings/Instrument-Cluster.md> · <https://5series.net/forums/e60-discussion-2/true-speed-150479>

### Notbremssignal: Blinkfrequenz

<a id="remess_flash_frequency"></a>`rem.ess_flash_frequency` · Bereich: 6 · SG **REM** · Kategorie Sicherheit

Blinkfrequenz der Heckleuchten beim Notbremssignal.

- **BimmerCode:** Brake Force Display flashing frequency (standard)
- **Parameter:** `ESS_BLINKFREQ_1`, `ESS_BLINKFREQ_2` (3064)
- **Werte:** `03` = Standard laut Botho.xml (BimmerCode: 3 times per second); `05` = erhöht (BimmerCode: 5 times per second)
- **Hardware:** Laut Almaretto/Kip nur für LED-Leuchten.
- **Software:** REM_01.
- **Aufwand / Risiko / Nutzen:** gering / sicherheitskritisch / gering
- **Kompatibilität (dein F20):** wahrscheinlich kompatibel · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Recht:** ECE R48 6.23.7.1: 4,0 ± 1,0 Hz, bei Glühlampen 4,0 +0/−1 Hz. 5 Hz liegt an der Obergrenze bzw. bei Glühlampen außerhalb → in DE nicht empfehlenswert/unzulässig.
- **Hinweise:** Ob die Bremsleuchten des F20 Pre-LCI Glühlampen oder LED sind, ist hier nicht verifiziert.
- **Quellen:** <https://bimmercode.app/cars/f20/> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Botho.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Almaretto.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Kip_M3.xml> · <https://nsai.ie/images/uploads/certification-automotive/UNECE-R48-04.pdf>

### Sitzheizung: Zustand speichern

<a id="cfasseat_heating_memory"></a>`cfas.seat_heating_memory` · Bereich: 7 · SG **CFAS** · Kategorie Komfort

Merkt sich die Sitzheizungsstufe über den Neustart (15 min / 24 h / unbegrenzt).

- **BimmerCode:** Seat heating/cooling setting memory (standard)
- **Parameter:** –
- **Werte:** `15 minutes / 24 hours / Do not save / Unlimited` = Auswahl in BimmerCode
- **Hardware:** Sitzmodul CFAS_PLX_1/CBFS_PLX_1 (elektrische Sitze mit Memory) – bei manuellen Sitzen nicht vorhanden.
- **Software:** Für FEM-gesteuerte Sitzheizung keine Speicherfunktion dokumentiert.
- **Aufwand / Risiko / Nutzen:** gering / gering / mittel
- **Kompatibilität (dein F20):** unwahrscheinlich · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Hinweise:** Sitzausstattung (elektrisch/Memory?) nicht angegeben; vermutlich manuell → [NICHT KOMPATIBEL].
- **Quellen:** <https://bimmercode.app/cars/f20/>

### Ambientelicht: Helligkeit vom Kombi entkoppeln / Helligkeit / Welcome

<a id="fem_bodyambient_light_decoupling"></a>`fem_body.ambient_light_decoupling` · Bereich: 7 · SG **FEM_BODY** · Kategorie Beleuchtung

Ambientelicht-Helligkeit unabhängig von der Instrumentenhelligkeit; Grundhelligkeit; Ambientelicht beim Entriegeln.

- **BimmerCode:** Ambient lighting brightness / Ambient lighting brightness decoupling from instrument cluster (standard)
- **Parameter:** `AMBIENTE_NACHFUEHRUNG`, `AMBIENTE_HELLIGKEIT`, `WELCOME_AMBIENTE` (3070)
- **Werte:** `AMBIENTE_NACHFUEHRUNG = aktiv` = Standard – folgt Kombi-Helligkeit; `AMBIENTE_NACHFUEHRUNG = nicht_aktiv` = entkoppelt; `WELCOME_AMBIENTE = aktiv` = Ambiente beim Entriegeln
- **Hardware:** Ambientebeleuchtung (Sonderausstattung) – für dieses Fahrzeug nicht angegeben.
- **Software:** Parametername/Wertebezeichnung können je nach I-Stufe/CAFD-Version abweichen (Quellen beziehen sich auf CAFD 00000794 FEM_BODY, Serie F020/F030). Vor dem Codieren Ist-Wert in BimmerCode auslesen und Backup sichern.
- **Aufwand / Risiko / Nutzen:** gering / gering / gering
- **Kompatibilität (dein F20):** unwahrscheinlich · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Hinweise:** Ohne Ambientelicht wirkungslos.
- **Quellen:** <https://bimmercode.app/cars/f20/> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Botho.xml> · <https://docs.google.com/spreadsheets/d/16O4RKIMekWFCs5jPW3T_7li0yIEvgZfFI0u3l0RmSwU/pubhtml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Kip_M3.xml>

### Türgriffbeleuchtung beim Rückwärtsgang

<a id="fem_bodydoor_handle_light_reverse"></a>`fem_body.door_handle_light_reverse` · Bereich: 7 · SG **FEM_BODY** · Kategorie Beleuchtung

Türgriff-LEDs leuchten beim Einlegen des Rückwärtsgangs.

- **BimmerCode:** Door handle lights when reverse gear is engaged (standard)
- **Parameter:** `OVT_BEI_RUECKFAHRLICHT` (3070)
- **Werte:** `nicht_aktiv` = Standard; `aktiv` = an
- **Hardware:** Türgriffbeleuchtung (Teil von Licht-/Ambientepaketen) – für dieses Fahrzeug nicht angegeben.
- **Software:** Parametername/Wertebezeichnung können je nach I-Stufe/CAFD-Version abweichen (Quellen beziehen sich auf CAFD 00000794 FEM_BODY, Serie F020/F030). Vor dem Codieren Ist-Wert in BimmerCode auslesen und Backup sichern.
- **Aufwand / Risiko / Nutzen:** gering / gering / gering
- **Kompatibilität (dein F20):** unwahrscheinlich · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Quellen:** <https://bimmercode.app/cars/f20/> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Botho.xml> · <https://docs.google.com/spreadsheets/d/16O4RKIMekWFCs5jPW3T_7li0yIEvgZfFI0u3l0RmSwU/pubhtml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Bundang_Thunder.xml>

### Scheinwerferreinigungsanlage (SRA): Aktivierung/Parameter

<a id="fem_bodyheadlight_washer"></a>`fem_body.headlight_washer` · Bereich: 7 · SG **FEM_BODY** · Kategorie Wischer

Ein/Aus der SRA, Spritzimpulse, Sperrzeit, Waschvorgänge bis zur SRA-Auslösung.

- **BimmerCode:** Headlight washers / Number of washing operations for headlight cleaning / Headlight cleaning blocking time (standard)
- **Parameter:** `WW_SCHEINWERFERREINIGUNG`, `WW_ANZAHL_SPRITZIMPULSE_SRA`, `WW_SRA_SPERRZEIT`, `WW_ANZAHL_WASCHBET_ZUR_SRA` (3080)
- **Werte:** `WW_SCHEINWERFERREINIGUNG = aktiv / nicht_aktiv` = SRA an/aus; `WW_ANZAHL_SPRITZIMPULSE_SRA = 02` = 2 Impulse – Standard; `WW_SRA_SPERRZEIT = 0A` = 10 min – Standard; `WW_ANZAHL_WASCHBET_ZUR_SRA = 0A` = jede 10. Wäsche – Standard
- **Hardware:** Scheinwerferreinigungsanlage – bei Halogen-Scheinwerfern üblicherweise nicht verbaut.
- **Software:** Parametername/Wertebezeichnung können je nach I-Stufe/CAFD-Version abweichen (Quellen beziehen sich auf CAFD 00000794 FEM_BODY, Serie F020/F030). Vor dem Codieren Ist-Wert in BimmerCode auslesen und Backup sichern.
- **Aufwand / Risiko / Nutzen:** gering / gering / gering
- **Kompatibilität (dein F20):** unwahrscheinlich · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Hinweise:** Hardware-blockiert, falls keine SRA-Düsen vorhanden.
- **Quellen:** <https://bimmercode.app/cars/f20/> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Botho.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/packetpilot.xml>

### Spiegel beim Komfortschließen an-/ausklappen

<a id="fem_bodymirror_fold_comfort"></a>`fem_body.mirror_fold_comfort` · Bereich: 7 · SG **FEM_BODY** · Kategorie Komfort

Außenspiegel klappen beim Komfortschließen an und beim Komfortöffnen wieder aus; Variante 'Fold/unfold automatically' bei jedem Ver-/Entriegeln.

- **BimmerCode:** Fold mirrors with convenient closing / Unfold mirrors with convenient opening / Fold/unfold mirrors automatically (standard)
- **Parameter:** `ASP_BEIKLAPPEN`, `ASP_BEIKLAPPEN_BEI_KOMFORTSCHLIESSEN`, `ASP_AUSKLAPPEN_NACH_KOMFORTSCHLIESSEN` (3110)
- **Werte:** `ASP_BEIKLAPPEN = aktiv` = Anklappmotor verbaut; `ASP_BEIKLAPPEN_BEI_KOMFORTSCHLIESSEN = aktiv` = anklappen beim Komfortschließen; `ASP_AUSKLAPPEN_NACH_KOMFORTSCHLIESSEN = aktiv` = ausklappen beim Komfortöffnen
- **Hardware:** Elektrisch anklappbare Außenspiegel – laut Fahrzeugbeschreibung NICHT angegeben. Spreadsheet F3x: 'does not work if you dont have foldable mirrors'.
- **Software:** Parametername/Wertebezeichnung können je nach I-Stufe/CAFD-Version abweichen (Quellen beziehen sich auf CAFD 00000794 FEM_BODY, Serie F020/F030). Vor dem Codieren Ist-Wert in BimmerCode auslesen und Backup sichern.
- **Aufwand / Risiko / Nutzen:** gering / gering / mittel
- **Kompatibilität (dein F20):** unwahrscheinlich · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Hinweise:** Hardware-blockiert, falls keine Anklappspiegel vorhanden (Spiegeltaster in der Tür prüfen). ASP_BEIKLAPPEN ohne Motor nicht setzen.
- **Quellen:** <https://bimmercode.app/cars/f20/> · <https://docs.google.com/spreadsheets/d/16O4RKIMekWFCs5jPW3T_7li0yIEvgZfFI0u3l0RmSwU/pubhtml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Kip_M3.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Almaretto.xml> · <https://www.motor-talk.de/forum/start-des-ersten-codierens-einstiegsfragen-t7071093.html>

### Spiegel: Geschwindigkeitsschwellen An-/Ausklappen

<a id="fem_bodymirror_fold_speed"></a>`fem_body.mirror_fold_speed` · Bereich: 7 · SG **FEM_BODY** · Kategorie Komfort

Maximale Geschwindigkeit zum Anklappen und Geschwindigkeit für automatisches Ausklappen.

- **BimmerCode:** Mirror folding speed threshold / Mirror unfolding speed threshold (standard)
- **Parameter:** `ASP_MAX_GESCHWINDIGKEIT_BEIKLAPPEN`, `ASP_GESCHWINDIGKEIT_AUTO_AUSKLAPPEN` (3110)
- **Werte:** `ASP_MAX_GESCHWINDIGKEIT_BEIKLAPPEN = 14 (hex)` = 20 km/h – Standard laut Botho; `ASP_GESCHWINDIGKEIT_AUTO_AUSKLAPPEN = 28 (hex)` = 40 km/h – Standard; `5 … 50 km/h` = Auswahl in BimmerCode
- **Hardware:** Elektrisch anklappbare Außenspiegel.
- **Software:** Parametername/Wertebezeichnung können je nach I-Stufe/CAFD-Version abweichen (Quellen beziehen sich auf CAFD 00000794 FEM_BODY, Serie F020/F030). Vor dem Codieren Ist-Wert in BimmerCode auslesen und Backup sichern.
- **Aufwand / Risiko / Nutzen:** gering / mittel / gering
- **Kompatibilität (dein F20):** unwahrscheinlich · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Recht:** Angeklappte Spiegel während der Fahrt: Sicht nach hinten eingeschränkt – hohe Anklappschwellen nicht empfehlen.
- **Hinweise:** Hardware-abhängig.
- **Quellen:** <https://bimmercode.app/cars/f20/> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Botho.xml> · <https://docs.google.com/spreadsheets/d/16O4RKIMekWFCs5jPW3T_7li0yIEvgZfFI0u3l0RmSwU/pubhtml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Kip_M3.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/ekfxisid.xml>

### Beifahrerspiegel absenken beim Rückwärtsgang (Bordsteinautomatik)

<a id="fem_bodymirror_tilt_reverse"></a>`fem_body.mirror_tilt_reverse` · Bereich: 7 · SG **FEM_BODY** · Kategorie Komfort

Rechter Außenspiegel neigt sich beim Einlegen des Rückwärtsgangs; Neigungswert einstellbar.

- **BimmerCode:** Automatic mirror tilt / Automatic mirror tilt value (standard)
- **Parameter:** `ASP_BORDSTEINAUTOMATIK_DELTA` (3110)
- **Werte:** `3B (hex)` = Standard laut Botho; `46 / 5A / 1E (hex)` = Beispiele aus Botho/Kip/ekfxisid; `10 % … 100 %` = Auswahl in BimmerCode ('Automatic mirror tilt value')
- **Hardware:** BimmerCode: Anklappspiegel erforderlich; Spreadsheet F3x: Spiegel-Memory erforderlich.
- **Software:** Parametername/Wertebezeichnung können je nach I-Stufe/CAFD-Version abweichen (Quellen beziehen sich auf CAFD 00000794 FEM_BODY, Serie F020/F030). Vor dem Codieren Ist-Wert in BimmerCode auslesen und Backup sichern.
- **Aufwand / Risiko / Nutzen:** gering / gering / gering
- **Kompatibilität (dein F20):** unwahrscheinlich · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Hinweise:** Hardware-abhängig.
- **Quellen:** <https://bimmercode.app/cars/f20/> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Botho.xml> · <https://docs.google.com/spreadsheets/d/16O4RKIMekWFCs5jPW3T_7li0yIEvgZfFI0u3l0RmSwU/pubhtml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Kip_M3.xml>

### Akustische Ver-/Entriegelungsquittierung

<a id="fzdacoustic_lock_confirmation"></a>`fzd.acoustic_lock_confirmation` · Bereich: 7 · SG **FZD** · Kategorie Verriegelung

Quittungston der Alarmanlage beim Ver-/Entriegeln inkl. Lautstärke, Dauer und Frequenz.

- **BimmerCode:** Acoustical lock/unlock confirmation / Confirmation sound duration / Confirmation sound volume (standard)
- **Parameter:** `Akustische Quittierung Schaerfen`, `Akustische Quittierung Entschaerfen`, `Buzzer level high`, `Buzzer level low`, `Buzzer duration`, `Buzzer frequency` (3001, 3002)
- **Werte:** `Akustische Quittierung Schaerfen = 00 / 01` = aus (Standard laut Botho) / an; `Buzzer duration = 05/0A/0F/14` = kurz / normal (Standard) / lang / sehr lang; `Active / Not active` = Auswahl in BimmerCode
- **Hardware:** Diebstahlwarnanlage (Alarmsirene) erforderlich (BimmerCode: 'car has to be equipped with an alarm system'); Steuergerät FZD__07 oder CANS2. Für dieses Fahrzeug nicht angegeben.
- **Software:** FZD__07; ggf. zusätzlich iDrive-Checkbox (nur HU_NBT/NBT_EVO belegt).
- **Aufwand / Risiko / Nutzen:** mittel / gering / gering
- **Kompatibilität (dein F20):** unwahrscheinlich · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Hinweise:** Hardware-blockiert ohne Alarmanlage. Parameternamen enthalten Leerzeichen (so in Botho.xml dokumentiert).
- **Quellen:** <https://bimmercode.app/cars/f20/> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Botho.xml> · <https://github.com/packetpilot/bmw-f/blob/master/cheats/Bundang_Thunder.xml>

### Bluetooth-Audio-Streaming

<a id="hu_entrybluetooth_audio_streaming"></a>`hu_entry.bluetooth_audio_streaming` · Bereich: 7 · SG **HU_ENTRY** · Kategorie Audio

BimmerCode: 'Bluetooth audio streaming' (1 von 2) benötigt HU_NBT/HU_NBT_EVO, (2 von 2) Combox_Media. Laut BMW-Doku (F30) ist der Anschluss externer Audioplayer per Bluetooth eine Combox-Funktion. Bei 6NH ist das Telefon in der Headunit realisiert. Forenaussagen zu 6NH ohne Combox widersprechen sich (nur Snippets).

- **BimmerCode:** Bluetooth audio streaming (unknown)
- **Parameter:** –
- **Hardware:** laut BimmerCode HU_NBT/HU_NBT_EVO + Combox_Media; mit Combox ab Werk vorhanden (wahrscheinlich)
- **Software:** -
- **Aufwand / Risiko / Nutzen:** hoch / gering / hoch
- **Kompatibilität (dein F20):** unwahrscheinlich · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Hinweise:** 'documented' bezieht sich auf die Voraussetzung (Combox bzw. NBT), nicht auf eine HU_ENTRY-Codierung. Erst FA prüfen: ob 6NH, 6NS, 6NL oder eine Combox verbaut ist. Ohne Combox ist kein dokumentierter Codierweg bekannt.
- **Quellen:** <https://bimmercode.app/cars/f20> · <https://archive.org/download/BMWTechnicalTrainingDocuments/ST1113%20F30%20Complete%20Vehicle/07_F30_Entertainment_and_Communication1.pdf> · <https://www.motor-talk.de/forum/audio-streaming-ueber-bluetooth-nachruesten-codieren-t6554084.html> · <https://www.motor-talk.de/forum/radio-bmw-professional-audio-streaming-t5102516.html> · <https://www.motor-talk.de/forum/bluetooth-audio-streaming-t5135224.html>

### Apple CarPlay

<a id="hu_entrycarplay"></a>`hu_entry.carplay` · Bereich: 7 · SG **HU_ENTRY** · Kategorie iDrive

BimmerCode 'CarPlay fullscreen mode' gibt es nur für HU_NBT_EVO, und zwar abhängig von der iDrive-Softwareversion. Für HU_ENTRY gibt es keinen Codierweg. Das NBT-EVO-Toolkit schließt HU_ENTRY aus ('different SoC').

- **BimmerCode:** CarPlay fullscreen mode (unknown)
- **Parameter:** –
- **Hardware:** HU_NBT_EVO
- **Software:** -
- **Aufwand / Risiko / Nutzen:** hoch / gering / hoch
- **Kompatibilität (dein F20):** nicht kompatibel · **Nachweis:** Nicht kompatibel
- **Hinweise:** Nur per Headunit-Tausch bzw. Nachrüstlösung denkbar. Das wurde hier nicht untersucht.
- **Quellen:** <https://bimmercode.app/cars/f20> · <https://raw.githubusercontent.com/vandelayautollc/nbt-evo-toolkit/HEAD/docs/00-platform-overview.md>

### TFL-Ein/Aus im iDrive-Menü

<a id="hu_entrydrl_menu"></a>`hu_entry.drl_menu` · Bereich: 7 · SG **HU_ENTRY** · Kategorie Beleuchtung

Checkbox im Lichtmenü zum Ein-/Ausschalten des TFL. Belegt nur für HU_NBT/HU_NBT_EVO (BimmerCode) und HU_CIC (Parameter Daydriving_light).

- **BimmerCode:** Checkbox daytime running light (standard)
- **Parameter:** `Daydriving_light` (3000 (HU_CIC))
- **Werte:** `Perm_off` = Standard (kein Menüpunkt) – HU_CIC; `standard` = Menüpunkt verfügbar – HU_CIC
- **Hardware:** Head-Unit NBT/NBT EVO bzw. CIC; Fahrzeug hat Radio Professional (HU_ENTRY).
- **Software:** Für HU_ENTRY kein Parameter dokumentiert.
- **Aufwand / Risiko / Nutzen:** gering / mittel / gering
- **Kompatibilität (dein F20):** unwahrscheinlich · **Nachweis:** Unbekannt
- **Recht:** Siehe fem_body.drl_mode (ECE R48 6.19.7).
- **Hinweise:** BimmerCode-Standardoption setzt laut offizieller Liste HU_NBT/HU_NBT_EVO voraus; für HU_ENTRY (Radio Professional) keine Quelle gefunden → wahrscheinlich nicht verfügbar. Alternative: TFL direkt im FEM_BODY (TFL_MODUS). Siehe auch Katalog 04 (hu_entry.drl_checkbox).
- **Quellen:** <https://bimmercode.app/cars/f20/> · <https://docs.google.com/spreadsheets/d/16O4RKIMekWFCs5jPW3T_7li0yIEvgZfFI0u3l0RmSwU/pubhtml>

### SMS vollständig anzeigen

<a id="hu_entryfull_text_messages"></a>`hu_entry.full_text_messages` · Bereich: 7 · SG **HU_ENTRY** · Kategorie iDrive

Für HU_NBT dokumentiert: PIM_Driving_Text von up_to_three_lines auf whole_text. Die BimmerCode-Option 'Display full text messages' gibt es nur für HU_NBT/HU_NBT_EVO.

- **BimmerCode:** Display full text messages (unknown)
- **Parameter:** `PIM_Driving_Text` (3003)
- **Werte:** `up_to_three_lines` = max. drei Zeilen während der Fahrt; `whole_text` = vollständiger Text
- **Hardware:** laut BimmerCode HU_NBT/HU_NBT_EVO; Nachrichtenfunktion
- **Software:** -
- **Aufwand / Risiko / Nutzen:** mittel / mittel / gering
- **Kompatibilität (dein F20):** unwahrscheinlich · **Nachweis:** Unbekannt
- **Recht:** Lesen während der Fahrt kann gegen § 23 Abs. 1a StVO verstoßen.
- **Hinweise:** Für HU_ENTRY kein Beleg.
- **Quellen:** <https://docs.google.com/spreadsheets/d/1UreLsK1PwycTWeW6OL71HOoVpLtKtfwRMRSvlsiC8JY/edit> · <https://bimmercode.app/cars/f20>

### Office- und Servicemeldungen während der Fahrt lesbar

<a id="hu_entryspeedlock_office_service_messages"></a>`hu_entry.speedlock_office_service_messages` · Bereich: 7 · SG **HU_ENTRY** · Kategorie iDrive

Für HU_NBT dokumentiert: SERVICES_MESSAGES_SPEEDLOCK_CONDITION und OFFICE_MESSAGES_SPEEDLOCK_CONDITION auf 'none'. Office-Funktionen setzen laut BMW-Doku eine Combox voraus.

- **Parameter:** `SERVICES_MESSAGES_SPEEDLOCK_CONDITION`, `OFFICE_MESSAGES_SPEEDLOCK_CONDITION` (3000 HMI)
- **Werte:** `none` = keine Sperre während der Fahrt
- **Hardware:** HU_NBT; Office nur mit Combox (6NL o. Ä.)
- **Software:** -
- **Aufwand / Risiko / Nutzen:** mittel / mittel / gering
- **Kompatibilität (dein F20):** unwahrscheinlich · **Nachweis:** Unbekannt
- **Recht:** Bedienen und Lesen während der Fahrt kann gegen § 23 Abs. 1a StVO verstoßen.
- **Hinweise:** Für HU_ENTRY nicht belegt.
- **Quellen:** <https://docs.google.com/spreadsheets/d/1UreLsK1PwycTWeW6OL71HOoVpLtKtfwRMRSvlsiC8JY/edit> · <https://archive.org/download/BMWTechnicalTrainingDocuments/ST1113%20F30%20Complete%20Vehicle/07_F30_Entertainment_and_Communication1.pdf>

### Startanimation / Logo der Headunit

<a id="hu_entrystartup_animation"></a>`hu_entry.startup_animation` · Bereich: 7 · SG **HU_ENTRY** · Kategorie iDrive

STARTUP_EMBLEM ist für HU_NBT dokumentiert (Knoten 3001, variant_00 bis variant_09). Laut bmw-syndikat funktioniert es nur mit HU_NBT, nicht mit HU_CIC. Ein zweiter Datenbankeintrag nennt STARTUP_EMBLEM für die 'Headunit Entrynav' (spätere ENTRY-Navigation), ohne Werte. BimmerCode bietet 'Start animation' nur für HU_NBT/HU_NBT_EVO an.

- **BimmerCode:** Start animation (unknown)
- **Parameter:** `STARTUP_EMBLEM` (3001)
- **Werte:** `variant_00` = BMW ConnectedDrive (Standard; ebenso 02–06); `variant_01` = BMW M; `variant_07` = weißes BMW-Logo; `variant_08` = braunes BMW-Logo (wie HU_CIC); `variant_09` = 'Merry XMas'
- **Hardware:** belegt für HU_NBT; Hinweis auf HU_ENTRYNAV; nicht für HU_ENTRY (2012, ohne Navi)
- **Software:** -
- **Aufwand / Risiko / Nutzen:** mittel / gering / gering
- **Kompatibilität (dein F20):** unwahrscheinlich · **Nachweis:** Unbekannt
- **Hinweise:** Die Werte gelten für HU_NBT. Für die 2012er HU_ENTRY gibt es keinen Beleg. Methoden zum Austausch von Boot-Logos per USB beziehen sich auf NBT/EVO.
- **Quellen:** <https://www.bmw-syndikat.de/bmwsyndikatforum/bmw_codieren_datenbank.asp?goto=83> · <https://docs.google.com/spreadsheets/d/1UreLsK1PwycTWeW6OL71HOoVpLtKtfwRMRSvlsiC8JY/edit> · <https://bimmercode.app/cars/f20>

### Warngong-Variante und Lautstärke-Popup

<a id="hu_entrywarning_chime_volume_popup"></a>`hu_entry.warning_chime_volume_popup` · Bereich: 7 · SG **HU_ENTRY** · Kategorie Audio

Die BimmerCode-Optionen 'Warning chime' (BMW/BMW i/Mini/Rolls-Royce) und 'Volume popup' gibt es nur für HU_NBT/HU_NBT_EVO. Für HU_ENTRY sind keine Parameter dokumentiert.

- **BimmerCode:** Warning chime / Volume popup (unknown)
- **Parameter:** –
- **Hardware:** laut BimmerCode HU_NBT/HU_NBT_EVO
- **Software:** -
- **Aufwand / Risiko / Nutzen:** mittel / gering / gering
- **Kompatibilität (dein F20):** unwahrscheinlich · **Nachweis:** Unbekannt
- **Hinweise:** Auch für geschwindigkeitsabhängige Lautstärke und Gong-/PDC-Lautstärke wurden für HU_ENTRY keine Parameter gefunden.
- **Quellen:** <https://bimmercode.app/cars/f20>

### Hintergrundfarbe der Skalen (Orange/Grau)

<a id="kombibackground_color"></a>`kombi.background_color` · Bereich: 7 · SG **KOMBI** · Kategorie Kombiinstrument

Community-Tabelle: HINTERGRUND_FARBE_TAG und HINTERGRUND_FARBE_NACHT (Block 3001), Orange → Orange/Grau. Laut Tabelle 'Only for instrument cluster high'. bmw-syndikat führt das für den F10 mit Kombi 6WA.

- **Parameter:** `HINTERGRUND_FARBE_TAG`, `HINTERGRUND_FARBE_NACHT` (3001)
- **Werte:** `Orange` = Standard; `Orange/Grau` = hell-orange/graue Hintergrundlinien
- **Hardware:** Kombi High (6WA)
- **Software:** BimmerCode-Expertenmodus / E-Sys
- **Aufwand / Risiko / Nutzen:** mittel / gering / gering
- **Kompatibilität (dein F20):** unwahrscheinlich · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Hinweise:** Nur relevant, falls das Auto 6WA hat.
- **Quellen:** <https://docs.google.com/spreadsheets/d/16O4RKIMekWFCs5jPW3T_7li0yIEvgZfFI0u3l0RmSwU/pubhtml> · <https://www.bmw-syndikat.de/bmwsyndikatforum/bmw_codieren_datenbank.asp?goto=83>

### Maximalwert der Verbrauchsanzeige

<a id="kombifuel_consumption_display_max"></a>`kombi.fuel_consumption_display_max` · Bereich: 7 · SG **KOMBI** · Kategorie Kombiinstrument

BimmerCode 'Fuel consumption display maximum value': Skalenendwert der Momentanverbrauchsanzeige.

- **BimmerCode:** Fuel consumption display maximum value (standard)
- **Parameter:** –
- **Werte:** `20 l/100km` = Skalenende 20 l/100 km; `30 l/100km` = Skalenende 30 l/100 km
- **Hardware:** laut BimmerCode nur KOMBI L7_MID
- **Software:** BimmerCode
- **Aufwand / Risiko / Nutzen:** gering / gering / gering
- **Kompatibilität (dein F20):** unwahrscheinlich · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Hinweise:** Hängt von der KOMBI-Variante ab.
- **Quellen:** <https://bimmercode.app/cars/f20>

### M-Performance-Logo unten rechts im Kombi

<a id="kombim_performance_logo"></a>`kombi.m_performance_logo` · Bereich: 7 · SG **KOMBI** · Kategorie Kombiinstrument

BimmerCode 'M Performance logo': modellspezifisches Logo unten rechts. Werte: Not active, 135i, 140i, 235i, 240i, 340i, 50d, 550d, PHEV.

- **BimmerCode:** M Performance logo (standard)
- **Parameter:** –
- **Werte:** `Not active` = kein Logo; `135i` = Beispielwert (Modellschriftzug)
- **Hardware:** laut BimmerCode nur KOMBI L7_MID
- **Software:** BimmerCode
- **Aufwand / Risiko / Nutzen:** gering / gering / gering
- **Kompatibilität (dein F20):** unwahrscheinlich · **Nachweis:** Dokumentiert (nicht am Fahrzeug getestet)
- **Hinweise:** Die KOMBI-Variante L7_MID ist für einen 2012er F20 ohne 6WA eher unwahrscheinlich (nicht belegt). Ein falscher Modellschriftzug ist optisch irreführend.
- **Quellen:** <https://bimmercode.app/cars/f20>

