# KNOWN_LIMITATIONS

| # | Einschränkung | Auswirkung | Umgang |
|---|---|---|---|
| 1 | Kein Realtest am Fahrzeug durchgeführt | Adapter-/Diagnosepfad nur im Simulator geprüft; Simulator bildet *dokumentierte Annahmen* ab | lesender Realtest mit Zustimmung des Besitzers |
| 2 | Adaptermodell unbekannt | BLE-Profil/Klonverhalten (ATCEA, FCSM) offen | `f20 adapter scan`, Modell notieren |
| 3 | Parameternamen aus Drittquelle (OpenCAFDMap, BMW-Herkunft, Rechtslage unklar) | Namen „Dokumentiert“, nicht „Nachgewiesen“; nicht mitgeliefert | nur lokal nach Freigabe |
| 4 | Layout-Tabellen für FEM 004_228_010 unvollständig (Blöcke 0x3020/0x3040/0x3050/0x3053/0x3060) | z. B. `BLINKZYKLEN_ANZAHL_TIPP`, `WL_TIMEOUT` nicht eindeutig lokalisierbar | Feldabgleich (markiert) bzw. BimmerCode-Expertenmodus |
| 5 | Mehrwertige Wertlabels können aus anderen CAFD-Versionen stammen | einzelne Labels (z. B. `BAUART`) evtl. unpassend | Rohwert (Hex) immer mit angeben |
| 6 | Android-Backups (`.dat`, Java-Serialisierung) | nur erkannt, nicht dekodiert | bei Bedarf ergänzen |
| 7 | E-Serie-Backups (`ESeriesCodingECU`) | nur Rohdaten/Diff, keine Namen | Fremdfahrzeug, ausgeschlossen |
| 8 | ELM327 kann keine Multi-Frame-Anfragen senden | irrelevant für Lesen; Blocker für eigenes Schreiben | Schreiben nicht vorgesehen |
| 9 | Codierdaten signiert (128-Byte-Signaturblock) | eigenes Schreiben ohne Signaturverfahren unmöglich | Codierung nur über BimmerCode |
| 10 | BMW-Fehlertexte nicht frei verfügbar | DTCs als Hex-Code + Statusbits | ggf. später aus freien Quellen ergänzen |
| 11 | BMW-spezifische Live-DIDs der DME nicht offen dokumentiert | Live-Daten nur über Standard-OBD (Öltemp. evtl. nicht verfügbar) | Anzeige „nicht verfügbar“ |
| 12 | Web-Oberfläche zurückgestellt | Bedienung per CLI/MCP | auf Wunsch fortsetzen |
| 13 | Swift/SwiftUI in der Cloud-Umgebung nicht baubar | Python-Stack gewählt | späteres natives Frontend möglich |
| 14 | Einmal versehentlich FIN in einem Test-Commit (behoben per Force-Push, 2026-11-24) | alter Commit evtl. per direkter SHA noch kurz auf GitHub abrufbar | Repository auf privat stellen |
