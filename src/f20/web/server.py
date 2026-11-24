"""Lokaler HTTP-Server für die Oberfläche (nur 127.0.0.1, nur Standardbibliothek).

Schutzmaßnahmen:
* Bindung ausschließlich an 127.0.0.1.
* Host-Header-Prüfung (Schutz gegen DNS-Rebinding).
* Zustandsändernde Anfragen (POST) brauchen den Header ``X-F20: 1``; fremde
  Webseiten können ihn ohne CORS-Freigabe nicht setzen (Schutz gegen CSRF).
* Keine Route kann Schreibbefehle an das Fahrzeug senden.
"""

from __future__ import annotations

import json
import mimetypes
import re
import threading
import time
import traceback
import urllib.parse
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from .. import APP_NAME, __version__
from ..backup.service import BackupService, mask_vin
from ..coding.catalog import LABELS_DE, bimmercode_instructions, default_catalog, load_json_data
from ..paths import STATIC_DIR, f20_home
from ..safety.policy import OBD_ALLOWED_MODES, OBD_FORBIDDEN_MODES, UDS_ALLOWED, UDS_FORBIDDEN
from ..session import REAL_CONFIRMATION, DiagnosticSession
from ..store import Store

MAX_UPLOAD = 8 * 1024 * 1024


class ApiError(Exception):
    def __init__(self, status: int, message: str) -> None:
        super().__init__(message)
        self.status = status


def _lite(e: dict) -> dict:
    keys = ("id", "ecu", "category", "title_de", "bimmercode_label", "bimmercode_mode", "risk", "benefit",
            "compatibility", "evidence", "effort", "score", "safety_ecu", "cafd_block", "function_names")
    d = {k: e[k] for k in keys}
    d["has_legal_note"] = bool(e.get("legal_note_de"))
    return d


class App:
    def __init__(self, store: Store | None = None) -> None:
        self.store = store or Store()
        self.backups = BackupService(self.store)
        self.session = DiagnosticSession(self.store)
        self.catalog = default_catalog()
        self.started = time.time()

    # ------------------------------------------------------------ Routing
    def handle(self, method: str, path: str, query: dict[str, str], body: bytes, headers) -> tuple[int, str, bytes]:
        routes = [
            ("GET", r"/api/status", self.status),
            ("GET", r"/api/vehicle", self.vehicle),
            ("GET", r"/api/ecus", self.ecus),
            ("GET", r"/api/catalog", self.catalog_list),
            ("GET", r"/api/catalog/(?P<cid>[\w.\-]+)", self.catalog_item),
            ("GET", r"/api/plan", self.plan_list),
            ("POST", r"/api/plan", self.plan_add),
            ("POST", r"/api/plan/(?P<pid>\d+)/status", self.plan_status),
            ("GET", r"/api/plan/export", self.plan_export),
            ("GET", r"/api/changes", self.changes),
            ("POST", r"/api/changes", self.change_add),
            ("GET", r"/api/backups", self.backup_list),
            ("POST", r"/api/backups/import", self.backup_import),
            ("GET", r"/api/backups/verify", self.backup_verify),
            ("GET", r"/api/backups/compare", self.backup_compare),
            ("POST", r"/api/backups/learn", self.backup_learn),
            ("GET", r"/api/backups/(?P<bid>\d+)", self.backup_detail),
            ("GET", r"/api/backups/(?P<bid>\d+)/decode", self.backup_decode),
            ("GET", r"/api/backups/(?P<bid>\d+)/hex", self.backup_hex),
            ("POST", r"/api/backups/(?P<bid>\d+)/simulate", self.backup_simulate),
            ("GET", r"/api/backups/(?P<bid>\d+)/report", self.backup_report),
            ("GET", r"/api/session", self.session_get),
            ("POST", r"/api/session/start", self.session_start),
            ("POST", r"/api/session/stop", self.session_stop),
            ("GET", r"/api/history", self.history),
            ("GET", r"/api/diagnosis/latest", self.diagnosis_latest),
            ("GET", r"/api/safety", self.safety),
            ("GET", r"/api/adapter/scan", self.adapter_scan),
        ]
        for m, pattern, fn in routes:
            if m != method:
                continue
            mt = re.fullmatch(pattern, path)
            if mt:
                result = fn(query=query, body=body, headers=headers, **mt.groupdict())
                if isinstance(result, tuple):
                    return result
                return 200, "application/json; charset=utf-8", json.dumps(result, ensure_ascii=False, default=str).encode()
        raise ApiError(404, f"Unbekannte Route {method} {path}")

    @staticmethod
    def _json(body: bytes) -> dict:
        try:
            return json.loads(body or b"{}")
        except ValueError as exc:
            raise ApiError(400, f"Ungültiges JSON: {exc}") from exc

    # ------------------------------------------------------------ Endpunkte
    def status(self, **_):
        return {"app": APP_NAME, "version": __version__, "read_only": True, "data_dir": str(f20_home()),
                "session": self.session.state.status, "session_mode": self.session.state.mode,
                "uptime_s": round(time.time() - self.started), "catalog_entries": len(self.catalog.entries),
                "backups": len(self.store.list_backups())}

    def _local_vehicle(self) -> dict:
        p = f20_home() / "vehicle.local.json"
        if p.exists():
            try:
                return json.loads(p.read_text(encoding="utf-8"))
            except ValueError:
                return {}
        return {}

    def vehicle(self, **_):
        prof = load_json_data("vehicle_profile.json")
        local = self._local_vehicle()
        vehicles = self.backups.vehicles(privacy=True)
        diag = self.store.latest_diagnosis()
        changes = self.store.list_changes()[:8]
        plan = self.store.list_plan()
        findings = self.session.snapshot()["findings"] if self.session.state.status == "live" else []
        return {"profile": prof["fields"], "vin_masked": mask_vin(local.get("vin")),
                "backup_vehicles": vehicles, "last_diagnosis": diag and {
                    "session": diag["session"], "ecu_count": sum(1 for e in diag["ecus"] if e.get("responded")),
                    "dtc_sources": len(diag["dtcs"])},
                "recent_changes": changes, "plan_open": sum(1 for p in plan if p["status"] == "planned"),
                "findings": findings, "session": self.session.state.status}

    def ecus(self, **_):
        base = load_json_data("ecus.json")
        diag = self.store.latest_diagnosis()
        idents = {e["address"]: e for e in (diag["ecus"] if diag else [])}
        dtcs = {d["source"]: d["data"] for d in (diag["dtcs"] if diag else [])}
        by_diag: dict[str, list] = {}
        for b in self.store.list_backups():
            cod = b["meta"].get("cod") or {}
            if cod.get("diag_address"):
                by_diag.setdefault(cod["diag_address"], []).append(
                    {"id": b["id"], "ecu_identifier": cod.get("ecu_identifier"), "sgbm": cod.get("sgbm"),
                     "created_at": cod.get("created_at")})
        cat_counts: dict[str, int] = {}
        for e in self.catalog.entries:
            cat_counts[e["ecu"]] = cat_counts.get(e["ecu"], 0) + 1
        out = []
        for e in base["ecus"]:
            addr = e["address"].upper().replace("0X", "0x")
            out.append({**e, "identity": idents.get(addr), "dtcs": dtcs.get(addr), "backups": by_diag.get(addr, []),
                        "catalog_entries": cat_counts.get(e["name"], 0),
                        "diagnosis_mode": diag["session"]["mode"] if diag else None})
        return {"meta": base["_meta"], "ecus": out}

    def catalog_list(self, query, **_):
        res = self.catalog.search(q=query.get("q", ""), category=query.get("category") or None,
                                  ecu=query.get("ecu") or None, compatibility=query.get("compatibility") or None,
                                  max_risk=query.get("max_risk") or None, evidence=query.get("evidence") or None,
                                  mode=query.get("mode") or None, only_recommendable=query.get("recommend") == "1")
        return {"count": len(res), "entries": [_lite(e) for e in res], "facets": self.catalog.facets(),
                "labels": LABELS_DE}

    def catalog_item(self, cid, **_):
        e = self.catalog.get(cid)
        if not e:
            raise ApiError(404, "Eintrag nicht gefunden")
        plan = [p for p in self.store.list_plan() if p["option_id"] == cid]
        return {**e, "plan": plan, "labels": LABELS_DE}

    def plan_list(self, **_):
        items = []
        for p in self.store.list_plan():
            e = self.catalog.get(p["option_id"])
            items.append({**p, "entry": _lite(e) if e else None})
        return {"items": items}

    def plan_add(self, body, **_):
        d = self._json(body)
        e = self.catalog.get(d.get("option_id", ""))
        if not e:
            raise ApiError(400, "Unbekannte Option")
        pid = self.store.add_plan_item(e["id"], d.get("target_value"), d.get("note"))
        warn = []
        if e["risk"] == "safety_critical" or e["safety_ecu"]:
            warn.append("Sicherheitskritisch – nicht empfohlen. Nur dokumentarisch geplant.")
        if e.get("legal_note_de"):
            warn.append(e["legal_note_de"])
        return {"id": pid, "warnings": warn}

    def plan_status(self, pid, body, **_):
        d = self._json(body)
        try:
            self.store.set_plan_status(int(pid), d.get("status", ""))
        except ValueError as exc:
            raise ApiError(400, str(exc)) from exc
        if d.get("status") == "done":
            item = next((p for p in self.store.list_plan() if p["id"] == int(pid)), None)
            if item:
                self.store.add_change("applied_bimmercode", item["option_id"], None, item["target_value"],
                                      d.get("note") or "in BimmerCode umgesetzt (Angabe des Besitzers)")
        return {"ok": True}

    def plan_export(self, **_):
        items = []
        for p in self.store.list_plan():
            e = self.catalog.get(p["option_id"])
            if e and p["status"] == "planned":
                items.append((e, p["target_value"], p["note"]))
        md = bimmercode_instructions(items)
        return 200, "text/markdown; charset=utf-8", md.encode()

    def changes(self, **_):
        return {"items": self.store.list_changes()}

    def change_add(self, body, **_):
        d = self._json(body)
        try:
            cid = self.store.add_change(d.get("kind", "note"), d.get("option_id"), d.get("from_value"),
                                        d.get("to_value"), d.get("note"))
        except ValueError as exc:
            raise ApiError(400, str(exc)) from exc
        return {"id": cid}

    def backup_list(self, **_):
        items = [self.backups.summary(b["id"], privacy=True) for b in self.store.list_backups()]
        try:
            timeline = self.backups.timeline()
        except Exception as exc:  # noqa: BLE001
            timeline = [{"error": str(exc)}]
        for t in timeline:
            if "vehicle" in t:
                t["vehicle"] = mask_vin(t["vehicle"])
        return {"items": items, "vehicles": self.backups.vehicles(privacy=True), "timeline": timeline}

    def backup_import(self, body, headers, **_):
        name = urllib.parse.unquote(headers.get("X-Filename", "upload.cod"))
        if not body:
            raise ApiError(400, "Leerer Upload")
        if len(body) > MAX_UPLOAD:
            raise ApiError(413, "Datei zu groß")
        b = self.backups.import_bytes(Path(name).name, body)
        return self.backups.summary(b["id"], privacy=True)

    def backup_verify(self, **_):
        return {"items": self.backups.vault.verify(self.store.list_backups())}

    def backup_compare(self, query, **_):
        try:
            return self.backups.compare(int(query["a"]), int(query["b"]))
        except (KeyError, ValueError) as exc:
            raise ApiError(400, f"Parameter a/b fehlen oder ungültig: {exc}") from exc

    def backup_learn(self, body, **_):
        d = self._json(body)
        try:
            return {"observations": self.backups.learn(int(d["before"]), int(d["after"]), str(d["label"]),
                                                       d.get("note"))}
        except (KeyError, ValueError) as exc:
            raise ApiError(400, str(exc)) from exc

    def backup_detail(self, bid, **_):
        try:
            s = self.backups.summary(int(bid), privacy=True)
            f = self.backups.forensic(int(bid))
        except KeyError as exc:
            raise ApiError(404, str(exc)) from exc
        for k in ("strings",):
            f[k] = f[k][:120]
        f.pop("entropy_windows", None)
        return {"summary": s, "forensic": f}

    def backup_decode(self, bid, **_):
        try:
            return self.backups.decode(int(bid))
        except Exception as exc:  # noqa: BLE001
            raise ApiError(400, str(exc)) from exc

    def backup_hex(self, bid, query, **_):
        try:
            return self.backups.hex_view(int(bid), query.get("block") or None, int(query.get("offset", 0)),
                                         min(4096, int(query.get("length", 512))))
        except (KeyError, ValueError) as exc:
            raise ApiError(400, str(exc)) from exc

    def backup_simulate(self, bid, body, **_):
        d = self._json(body)
        try:
            return self.backups.simulate(int(bid), d["block"], int(d["start"]), int(d.get("end", d["start"])),
                                         int(str(d.get("mask", "FF")), 16), str(d["value_hex"]))
        except (KeyError, ValueError) as exc:
            raise ApiError(400, str(exc)) from exc

    def backup_report(self, bid, **_):
        try:
            rep = {"generated_by": f"{APP_NAME} {__version__}", "generated_at": time.time(),
                   "summary": self.backups.summary(int(bid), privacy=True),
                   "decode": self.backups.decode(int(bid)), "forensic": self.backups.forensic(int(bid))}
        except Exception as exc:  # noqa: BLE001
            raise ApiError(400, str(exc)) from exc
        return 200, "application/json; charset=utf-8", json.dumps(rep, ensure_ascii=False, indent=1, default=str).encode()

    def session_get(self, **_):
        return self.session.snapshot()

    def session_start(self, body, **_):
        d = self._json(body)
        try:
            self.session.start(d.get("mode", "demo"), d.get("adapter"), d.get("confirmation"))
        except PermissionError as exc:
            raise ApiError(403, str(exc)) from exc
        except (ValueError, RuntimeError) as exc:
            raise ApiError(409, str(exc)) from exc
        return {"ok": True, "confirmation_phrase": REAL_CONFIRMATION}

    def session_stop(self, **_):
        self.session.stop()
        return {"ok": True, "status": self.session.state.status}

    def history(self, query, **_):
        return {"key": query.get("key"), "points": self.store.reading_history(query.get("key", ""), 600)}

    def diagnosis_latest(self, **_):
        return self.store.latest_diagnosis() or {}

    def safety(self, **_):
        return {
            "read_only": True,
            "uds_allowed": [{"sid": f"0x{k:02X}", "name": v[0],
                             "subfunctions": None if v[1] is None else [f"0x{s:02X}" for s in sorted(v[1])]}
                            for k, v in sorted(UDS_ALLOWED.items())],
            "uds_forbidden": [{"sid": f"0x{k:02X}", "reason": v} for k, v in sorted(UDS_FORBIDDEN.items())],
            "obd_allowed": [{"mode": f"0x{k:02X}", "name": v} for k, v in sorted(OBD_ALLOWED_MODES.items())],
            "obd_forbidden": [{"mode": f"0x{k:02X}", "reason": v} for k, v in sorted(OBD_FORBIDDEN_MODES.items())],
            "audit": [{"kind": a[0], "message": a[1], "allowed": a[2], "reason": a[3]}
                      for a in (self.session.elm.policy.audit[-80:] if self.session.elm else [])],
            "real_confirmation": REAL_CONFIRMATION,
        }

    def adapter_scan(self, **_):
        from ..transport.serial_tcp import list_serial_candidates
        out: dict = {"serial": list_serial_candidates(), "ble": [], "ble_error": None,
                     "note": "Passiver Scan – es wird nichts an das Fahrzeug gesendet."}
        try:
            import asyncio

            from ..transport.ble import scan
            out["ble"] = asyncio.run(scan(6.0))
        except Exception as exc:  # noqa: BLE001
            out["ble_error"] = f"{type(exc).__name__}: {exc}"
        return out


class Handler(BaseHTTPRequestHandler):
    app: App
    port: int
    server_version = "F20Intelligence/" + __version__

    def log_message(self, fmt, *args):  # ruhiger Server
        pass

    def _host_ok(self) -> bool:
        host = (self.headers.get("Host") or "").lower()
        return host in {f"127.0.0.1:{self.port}", f"localhost:{self.port}"}

    def _send(self, status: int, ctype: str, data: bytes, extra: dict | None = None) -> None:
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy",
                         "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; connect-src 'self'")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(data)

    def _error(self, status: int, msg: str) -> None:
        self._send(status, "application/json; charset=utf-8", json.dumps({"error": msg}, ensure_ascii=False).encode())

    def do_GET(self):  # noqa: N802
        self._dispatch("GET")

    def do_POST(self):  # noqa: N802
        self._dispatch("POST")

    def _dispatch(self, method: str) -> None:
        if not self._host_ok():
            return self._error(421, "Ungültiger Host-Header")
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = {k: v[-1] for k, v in urllib.parse.parse_qs(parsed.query).items()}
        if method == "POST" and self.headers.get("X-F20") != "1":
            return self._error(403, "Fehlender Header X-F20")
        if path == "/api/live/stream" and method == "GET":
            return self._stream()
        if not path.startswith("/api/"):
            return self._static(path)
        length = int(self.headers.get("Content-Length") or 0)
        if length > MAX_UPLOAD:
            return self._error(413, "Anfrage zu groß")
        body = self.rfile.read(length) if length else b""
        try:
            status, ctype, data = self.app.handle(method, path, query, body, self.headers)
            self._send(status, ctype, data)
        except ApiError as exc:
            self._error(exc.status, str(exc))
        except Exception as exc:  # noqa: BLE001
            traceback.print_exc()
            self._error(500, f"{type(exc).__name__}: {exc}")

    def _static(self, path: str) -> None:
        rel = "index.html" if path in ("/", "") else path.lstrip("/")
        target = (STATIC_DIR / rel).resolve()
        if not str(target).startswith(str(STATIC_DIR.resolve())) or not target.is_file():
            return self._error(404, "Nicht gefunden")
        ctype = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
        if ctype.startswith("text/") or ctype in ("application/javascript", "application/json"):
            ctype += "; charset=utf-8"
        self._send(200, ctype, target.read_bytes())

    def _stream(self) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        end = time.time() + 600
        try:
            while time.time() < end:
                snap = self.app.session.snapshot()
                snap.pop("log", None)
                payload = json.dumps(snap, ensure_ascii=False, default=str)
                self.wfile.write(f"data: {payload}\n\n".encode())
                self.wfile.flush()
                time.sleep(0.5)
        except (BrokenPipeError, ConnectionResetError):
            return


def make_server(port: int = 8720, app: App | None = None) -> ThreadingHTTPServer:
    app = app or App()
    handler = type("BoundHandler", (Handler,), {"app": app, "port": port})
    srv = ThreadingHTTPServer(("127.0.0.1", port), handler)
    srv.daemon_threads = True
    return srv


def serve(port: int = 8720, open_browser: bool = True) -> None:
    srv = make_server(port)
    url = f"http://127.0.0.1:{port}/"
    print(f"{APP_NAME} läuft auf {url}  (Strg+C beendet)")
    if open_browser:
        import webbrowser
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        srv.app_ref = None  # type: ignore[attr-defined]
        srv.server_close()
