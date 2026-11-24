"""Kommandozeile `f20` – alle Befehle sind lesend.

Beispiele:
  f20 backup import ~/Downloads/BimmerCode        # Backups in den Tresor übernehmen + analysieren
  f20 backup history                              # Was wurde wann geändert (mit Parameternamen)?
  f20 backup atlas                                # Klartext-Codierung aller SG → private/
  f20 catalog search digital                      # Katalog durchsuchen
  f20 catalog export                              # Codierplan (BimmerCode-Anleitung) als Markdown
  f20 sim                                         # Demo-Diagnose gegen den Simulator
  f20 adapter scan                                # passiver BLE-Scan + serielle Ports (sendet nichts ans Auto)
  f20 diag --ble <ID> --confirm "ICH BIN AM FAHRZEUG"   # realer LESE-Test (nur am Fahrzeug!)
  f20 serve                                       # lokale Oberfläche/API auf 127.0.0.1
  f20 mcp                                         # MCP-Server (stdio) für Claude Code
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from pathlib import Path

from . import APP_NAME, __version__


def _print(obj) -> None:
    print(json.dumps(obj, ensure_ascii=False, indent=1, default=str))


def _svc():
    from .backup.service import BackupService
    from .store import Store
    return BackupService(Store())


def cmd_backup(a) -> int:
    svc = _svc()
    if a.action == "import":
        rows = svc.import_path(Path(a.path))
        print(f"{len(rows)} Datei(en) verarbeitet, {len(svc.store.list_backups())} eindeutige Backups im Tresor.")
        return 0
    if a.action == "list":
        from .backup.personal import own_backups
        rows = own_backups(svc) if not a.all else svc.store.list_backups()
        for b in rows:
            s = svc.summary(b["id"], privacy=True)
            print(f"{s['id']:3d}  {s['ecu_identifier'] or '-':8s} {s['diag_address'] or '':5s} {s['sgbm'] or '':28s} "
                  f"{(s['created_at'] or '')[:16]}  {s['vehicle']}")
        return 0
    if a.action == "verify":
        rep = svc.vault.verify(svc.store.list_backups())
        bad = [r for r in rep if not r["ok"]]
        print(f"{len(rep) - len(bad)}/{len(rep)} Tresordateien in Ordnung.")
        for r in bad:
            print("  FEHLER:", r)
        return 1 if bad else 0
    if a.action == "history":
        from .backup.personal import explained_history
        for e in explained_history(svc):
            print(f"\n{e['ecu_identifier']} (CAFD {e['cafd']})")
            for st in e["steps"]:
                if st["identical"]:
                    print(f"  {st['from_date'][:16]} → {st['to_date'][:16]}: keine Änderung")
                    continue
                for c in st["changes"]:
                    if c.get("signature"):
                        continue
                    params = ", ".join(f"{p['name']}: {p['before']} → {p['after']}" for p in c.get("parameters", [])) \
                        or f"Byte {c['byte']}: {c['before']} → {c['after']}"
                    print(f"  {st['to_date'][:16]}  [{c['block']}] {params}")
        return 0
    if a.action == "atlas":
        from .backup.personal import write_private_reports
        from .coding.catalog import Catalog
        out = Path(a.out or "private")
        _print(write_private_reports(svc, Catalog.load(), out))
        print(f"Geschrieben nach {out}/ (PARAMETER_ATLAS.md, atlas.json, catalog_crossref.json) – NICHT einchecken.")
        return 0
    if a.action == "compare":
        _print(svc.compare(int(a.a), int(a.b)))
        return 0
    return 2


def cmd_catalog(a) -> int:
    from .coding.catalog import LABELS_DE, bimmercode_instructions, default_catalog
    cat = default_catalog()
    if a.action == "search":
        for e in cat.search(q=a.query or "", ecu=a.ecu, only_recommendable=a.recommend):
            print(f"{e['score']:4d}  {e['ecu']:9s} {e['id']:44s} {LABELS_DE['risk'][e['risk']]:>18s}  {e['title_de']}")
        return 0
    if a.action == "show":
        _print(cat.get(a.query))
        return 0
    if a.action == "export":
        ids = a.ids or [e["id"] for e in cat.search(only_recommendable=True)][:10]
        print(bimmercode_instructions([(cat.get(i), None, None) for i in ids if cat.get(i)]))
        return 0
    return 2


def cmd_sim(a) -> int:
    from .session import DiagnosticSession
    from .store import Store
    s = DiagnosticSession(Store())
    s.start("demo")
    s.wait_status({"live", "error", "stopped"}, 20)
    time.sleep(a.seconds)
    snap = s.snapshot()
    s.stop()
    print("DEMO – alle Werte sind fiktiv.")
    _print({k: snap[k] for k in ("status", "adapter", "dtcs", "unavailable", "derived", "findings")} |
           {"ecus": [(e["name"], e["address"], e["responded"]) for e in snap["ecus"]],
            "latest": {k: v["value"] for k, v in snap["latest"].items()}})
    return 0


def cmd_adapter(a) -> int:
    from .transport.serial_tcp import list_serial_candidates
    print("Serielle Kandidaten:", list_serial_candidates() or "keine")
    try:
        from .transport.ble import scan
        devs = asyncio.run(scan(a.timeout))
        for d in devs:
            print(f"  {'★' if d['obd_candidate'] else ' '} {d['name'] or '(ohne Namen)':24s} {d['id']}  RSSI {d['rssi']}  {d['service_uuids']}")
    except Exception as exc:  # noqa: BLE001
        print("BLE-Scan nicht möglich:", exc)
    print("Hinweis: Scan ist passiv – es wurde nichts an Adapter oder Fahrzeug gesendet.")
    return 0


def cmd_diag(a) -> int:
    from .session import REAL_CONFIRMATION, DiagnosticSession
    from .store import Store
    if (a.confirm or "").strip().upper() != REAL_CONFIRMATION:
        print(f"Abbruch: Realer Test nur mit --confirm \"{REAL_CONFIRMATION}\" und nur am Fahrzeug (Zündung an).")
        return 3
    spec = {"type": "ble", "address": a.ble} if a.ble else {"type": "serial", "port": a.serial} if a.serial else \
        {"type": "tcp", "host": a.tcp.split(":")[0], "port": int((a.tcp.split(":") + ["35000"])[1])} if a.tcp else None
    if not spec:
        print("Adapter angeben: --ble <ID> | --serial /dev/cu.xxx | --tcp 192.168.0.10:35000")
        return 2
    s = DiagnosticSession(Store())
    s.start("real", spec, a.confirm, identify=True, live=a.live > 0)
    # 1) Identifikation abwarten (max. 180 s), 2) optional Live-Daten für a.live Sekunden
    status = s.wait_status({"live", "stopped", "error", "disconnected"}, 180)
    if status == "live" and a.live:
        time.sleep(a.live)
    snap = s.snapshot()
    s.stop()
    _print({k: snap[k] for k in ("status", "error", "adapter", "dtcs", "obd_dtcs", "supported_pids", "unavailable",
                                 "derived", "findings")} | {"ecus": snap["ecus"], "log": snap["log"]})
    return 0 if snap["status"] in ("stopped", "live") else 1


def cmd_serve(a) -> int:
    from .web.server import serve
    serve(a.port, open_browser=not a.no_browser)
    return 0


def cmd_mcp(_a) -> int:
    from .mcp_server.server import main as mcp_main
    mcp_main()
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="f20", description=f"{APP_NAME} {__version__} – read-only")
    sub = p.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("backup", help="Backup Center")
    b.add_argument("action", choices=["import", "list", "verify", "history", "atlas", "compare"])
    b.add_argument("path", nargs="?")
    b.add_argument("--out")
    b.add_argument("--all", action="store_true", help="auch ausgeschlossene Fremdfahrzeuge zeigen")
    b.add_argument("-a")
    b.add_argument("-b")
    b.set_defaults(fn=cmd_backup)
    c = sub.add_parser("catalog", help="Codierungskatalog")
    c.add_argument("action", choices=["search", "show", "export"])
    c.add_argument("query", nargs="?")
    c.add_argument("--ecu")
    c.add_argument("--recommend", action="store_true")
    c.add_argument("--ids", nargs="*")
    c.set_defaults(fn=cmd_catalog)
    s = sub.add_parser("sim", help="Demo-Diagnose gegen den Simulator")
    s.add_argument("--seconds", type=float, default=2.0)
    s.set_defaults(fn=cmd_sim)
    ad = sub.add_parser("adapter", help="Adapter finden (passiv)")
    ad.add_argument("action", choices=["scan"])
    ad.add_argument("--timeout", type=float, default=8.0)
    ad.set_defaults(fn=cmd_adapter)
    d = sub.add_parser("diag", help="REALER Lesetest am Fahrzeug (nur mit Bestätigung)")
    d.add_argument("--ble")
    d.add_argument("--serial")
    d.add_argument("--tcp")
    d.add_argument("--confirm")
    d.add_argument("--live", type=int, default=0, help="Sekunden Live-Daten nach der Identifikation")
    d.set_defaults(fn=cmd_diag)
    sv = sub.add_parser("serve", help="Lokale Oberfläche/API")
    sv.add_argument("--port", type=int, default=8720)
    sv.add_argument("--no-browser", action="store_true")
    sv.set_defaults(fn=cmd_serve)
    m = sub.add_parser("mcp", help="MCP-Server (stdio) für Claude Code")
    m.set_defaults(fn=cmd_mcp)
    a = p.parse_args(argv)
    return a.fn(a)


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
