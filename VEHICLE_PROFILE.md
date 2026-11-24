# VEHICLE_PROFILE – BMW 116i F20 (FIN `WBA…8606`)

Maschinenlesbar: `src/f20/data/vehicle_profile.json`, `src/f20/data/ecus.json`. FIN vollständig nur lokal.

| Merkmal | Wert | Quelle | Nachweis |
|---|---|---|---|
| Modell | BMW 116i, Baureihe F20 | Besitzer; HU-Codierung `BAUREIHE=F20` | Nachgewiesen (Backup) |
| Produktion | 24.01.2012 | Besitzer | Unbekannt (über FA/Zeitkriterium prüfbar) |
| Motor | N13B16, 1,6 l, 100 kW/136 PS; HU-Codierung `ZYLINDERZAHL=4_zylinder` | Besitzer; Backup | teilw. Nachgewiesen |
| DME | Bosch MEVD17.2.5 | Recherche | Wahrscheinlich |
| Getriebe | Schaltgetriebe (`GETRIEBETYP=handschalter`, KOMBI `GETRIEBE_ART=handschalter`) | Backup | Nachgewiesen |
| Lenkung | Linkslenker (`TYP_LENKUNG=linkslenker`) | Backup | Nachgewiesen |
| Land | Deutschland (`COUNTRY=deutschland`) | Backup | Nachgewiesen |
| Headunit | HU_ENTRY (Radio Professional), 0x63, CAFD_000000F9_007_007_001, `DISPLAY_VARIANTE=schmales_display` | Backup | Nachgewiesen |
| Klima | IHKA (Klimaautomatik), 0x78 | Backup | Nachgewiesen |
| PDC | hinten 4 Sensoren, vorne keine (`PDC_SENSOR_HINTEN=4_sensoren`) | Backup | Nachgewiesen |
| ICM | 0x1C, CAFD_0000067B_002_003_139 | Backup | Nachgewiesen |
| Airbag | ACSM 0x01, CAFD_00000911_003_001_001 | Backup | Nachgewiesen |
| Telefon/Bluetooth | HU: `PHONE_TYPE=no_phone`, `MICROPHONE=no_microphone`; Bluetooth-Audio-Parameter vom Besitzer testweise aktiviert | Backup | Hardware **Unbekannt** (SA 6NH über FA prüfen) |
| USB | `USB_AVAILABLE=nicht_aktiv`, AUX vorhanden (`CDMM_AUX_HU=aktiv`) | Backup | Codierung nachgewiesen |
| DAB | `RADIO_DAB=nicht_aktiv` | Backup | Hardware Unbekannt |
| MFL, Sitzheizung vorn, Nebelscheinwerfer, Regen-/Lichtsensor, Sichtpaket | Besitzer | Unbekannt (Codierung FEM/REM prüfbar) |
| Scheinwerfer | vermutlich Halogen | – | Unbekannt |

## Steuergeräte
| SG | Adresse | Kennung | CAFD | Verbau |
|---|---|---|---|---|
| FEM_BODY (inkl. ZGW 0x10) | 0x40 | 0F16B0 | CAFD_00000794_004_228_010 | Nachgewiesen |
| REM | 0x72 | 0F16C0 | CAFD_000007A1_005_028_006 | Nachgewiesen |
| KOMBI | 0x60 | 0F1630 | CAFD_00000760_006_000_052 | Nachgewiesen |
| HU_ENTRY | 0x63 | 0F1820 | CAFD_000000F9_007_007_001 | Nachgewiesen |
| IHKA | 0x78 | 0F17C0 | CAFD_00000A3F_005_001_013 | Nachgewiesen |
| ICM | 0x1C | 0F1650 | CAFD_0000067B_002_003_139 | Nachgewiesen |
| ACSM | 0x01 | 0F16E0 | CAFD_00000911_003_001_001 | Nachgewiesen |
| DME, DSC, EPS, FZD, ZBE | 0x12, 0x29, 0x30, 0x56, 0x67 | – | – | Wahrscheinlich (keine Backups) |

## Am Fahrzeug zu klären (lesender Realtest)
Fahrzeugauftrag/SA-Codes (DID 0x3F06 am ZGW), I-Stufe (0x100B), SG-Listen je Bus (0x3F0E…), km-Stand
FEM vs. KOMBI, unterstützte OBD-PIDs, Adaptermodell.
