# ROADMAP

## Erledigt (0.1.0)
- [x] Recherche Architektur, Protokoll, Formate, Adapter, Codierungen (7 Berichte)
- [x] Read-only-Sicherheitsschicht, ELM327/UDS/OBD-Stack, Simulator mit Fehlerbildern
- [x] BimmerCode-.cod-Parser, Tresor, Diff, Lernmodus; Analyse der eigenen 22 Backups
- [x] Klartext-Entschlüsselung (Layout-Auswahl), Parameter-Atlas, Katalog-Abgleich
- [x] Codierungskatalog mit Rechtslage, CODING_DATABASE.md, BimmerCode-Export
- [x] MCP-Server (11 lesende Werkzeuge), CLI, 115 Tests

## Als Nächstes (benötigt den Besitzer)
1. [ ] Frische BimmerCode-Backups von ICM, HU_ENTRY, IHKA (Zustand nach dem Zurücksetzen prüfen)
2. [ ] Adaptermodell nennen → `f20 adapter scan` auf dem Mac
3. [ ] Lesender Realtest am Fahrzeug: Identifikation, Fehlerspeicher, FA/SA-Codes, I-Stufe, km-Abgleich, PIDs
4. [ ] Codierplan für empfohlene Optionen erstellen und in BimmerCode umsetzen; danach Vorher/Nachher-Backup
      → Lernmodus → Einträge auf „Nachgewiesen“ heben

## Danach
- [ ] Live-Dashboard (Web-UI fertigstellen oder natives SwiftUI-Frontend auf der lokalen API)
- [ ] PDC-Rohabstände (REM DIDs D645–D64D) und weitere dokumentierte Lese-DIDs
- [ ] Fahrzeugauftrag dekodieren (SA-Codes → Ausstattungsliste)
- [ ] Datenlogger + Verbrauchsanalyse über Zeit
- [ ] Android-`.dat`-Parser (falls benötigt)

## Langfristig (BimmerCode-Ersatz – Bewertung)
| Voraussetzung | Stand |
|---|---|
| SG/Codierdaten auslesen (0x22 3xxx) | technisch dokumentiert, erlaubt (lesend) |
| Parameter interpretieren | ✔ (lokale Tabellen) |
| Vollständige Sicherung | ✔ (BimmerCode-Backups) / eigenes Auslesen möglich |
| Kompatibilitätsprüfung, Simulation | ✔ |
| Signatur der Codierdaten | ✘ unbekannt → **Blocker** |
| Multi-Frame-Senden über ELM327 | ✘ → **Blocker** |
| Sichere Wiederherstellung | über BimmerCode |
Fazit: Codieren bleibt bei BimmerCode. F20 Intelligence ergänzt Analyse, Planung, Diagnose und Historie.
