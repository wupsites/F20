"""Katalog, Diagnosesitzung, Web-API (inkl. Schutzmechanismen) und MCP-Werkzeuge."""

import json
import threading
import time
import urllib.error
import urllib.request

import pytest

from f20.coding.catalog import Catalog, bimmercode_instructions, validate_entry


def test_catalog_valid_and_sourced():
    cat = Catalog.load()
    assert len(cat.entries) >= 100
    for e in cat.entries:
        assert validate_entry(e) == []
        if e["evidence"] == "documented":
            assert e["sources"]


def test_safety_ecus_never_recommended():
    cat = Catalog.load()
    for e in cat.search(only_recommendable=True):
        assert not e["safety_ecu"] and e["risk"] in ("low", "medium")


def test_export_contains_checklist():
    cat = Catalog.load()
    md = bimmercode_instructions([(cat.get("kombi.digital_speed"), "aktiv", None)])
    assert "Backup" in md and "BC_DIGITAL_V" in md or "Digitale Geschwindigkeit" in md


def test_demo_session_and_real_guard():
    from f20.session import DiagnosticSession
    from f20.store import Store
    s = DiagnosticSession(Store())
    with pytest.raises(PermissionError):
        s.start("real", {"type": "ble", "address": "x"}, confirmation="ja")
    s.start("demo")
    assert s.wait_status({"live"}, 20) == "live"
    time.sleep(0.6)
    snap = s.snapshot()
    s.stop()
    assert snap["demo"] and snap["latest"].get("rpm")
    assert any(u["key"] == "oil_temp" for u in snap["unavailable"])
    assert s.state.status == "stopped"


def test_session_disconnect_reported():
    from f20.session import DiagnosticSession
    from f20.store import Store
    s = DiagnosticSession(Store())
    s.start("demo", {"faults": {"disconnect_after_writes": 30}})
    assert s.wait_status({"disconnected", "error"}, 20) == "disconnected"


@pytest.fixture
def server():
    from f20.web.server import make_server
    srv = make_server(0)
    port = srv.server_address[1]
    srv.RequestHandlerClass.port = port
    th = threading.Thread(target=srv.serve_forever, daemon=True)
    th.start()
    yield f"http://127.0.0.1:{port}"
    srv.shutdown()


def _req(url, method="GET", data=None, headers=None):
    r = urllib.request.Request(url, method=method, data=data, headers=headers or {})
    try:
        with urllib.request.urlopen(r, timeout=10) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


def test_api_basics(server):
    st, body = _req(server + "/api/status")
    assert st == 200 and json.loads(body)["read_only"] is True
    st, body = _req(server + "/api/catalog?q=digital")
    assert st == 200 and json.loads(body)["count"] >= 1
    st, body = _req(server + "/api/safety")
    assert any(f["sid"] == "0x2E" for f in json.loads(body)["uds_forbidden"])
    st, _ = _req(server + "/")
    assert st == 200


def test_api_csrf_and_host_protection(server):
    st, _ = _req(server + "/api/session/start", "POST", b'{"mode":"demo"}', {"Content-Type": "application/json"})
    assert st == 403                                         # ohne X-F20-Header
    st, _ = _req(server + "/api/status", headers={"Host": "evil.example:80"})
    assert st == 421                                         # DNS-Rebinding-Schutz
    st, body = _req(server + "/api/session/start", "POST", b'{"mode":"real","adapter":{"type":"ble","address":"x"}}',
                    {"X-F20": "1"})
    assert st == 403 and "ICH BIN AM FAHRZEUG" in json.loads(body)["error"]


def test_api_import_backup(server):
    from f20.backup.cod import build_test_cod
    data = build_test_cod("DEMO0F20SIM000001", "0F1820", 0x63, "000000F9", (7, 7, 1), {0x3000: b"\x00" * 8})
    st, body = _req(server + "/api/backups/import", "POST", data,
                    {"X-F20": "1", "X-Filename": "0F1820-DEMO0F20SIM000001-1600000000.cod"})
    assert st == 200 and json.loads(body)["sgbm"] == "CAFD_000000F9_007_007_001"
    st, body = _req(server + "/api/backups")
    assert json.loads(body)["items"][0]["vehicle"].startswith("DEM")


def test_mcp_tools_read_only(isolated_home):
    from f20.mcp_server.tools import TOOL_NAMES, F20Tools
    t = F20Tools()
    assert t.safety_policy()["read_only"]
    assert t.latest_diagnosis()["mode"] == "none"
    assert t.live_snapshot()["available"] is False
    assert t.coding_options("digital")["count"] >= 1
    assert "hits" in t.research("ATCEA")
    (isolated_home / "mcp_consent.json").write_text(json.dumps({"catalog": False}))
    with pytest.raises(PermissionError):
        t.coding_options("x")
    for name in TOOL_NAMES:
        assert not any(w in name for w in ("write", "set", "code_", "flash", "clear", "delete"))
