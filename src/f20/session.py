"""Diagnosesitzung: Verbindungsaufbau, Identifikation, Fehlerspeicher, Live-Daten.

Läuft in einem eigenen Thread mit eigener asyncio-Schleife, damit Web-UI und
CLI sie gleichermaßen nutzen können.

Sicherheit:
* Modus „demo“: virtueller Adapter + virtuelles Fahrzeug (fiktive Daten).
* Modus „real“: nur mit ausdrücklicher Bestätigung (REAL_CONFIRMATION),
  die der Besitzer selbst eingibt, wenn er am Fahrzeug ist. Auch im
  Realmodus sind nur lesende Dienste möglich (ReadOnlyPolicy).
"""

from __future__ import annotations

import asyncio
import threading
import time
from collections import deque
from dataclasses import dataclass, field

from .analysis import derived_values, engine_findings
from .coding.catalog import load_json_data
from .obd.pids import PIDS
from .safety import ReadOnlyPolicy
from .store import Store
from .transport.base import ByteTransport
from .transport.elm327 import Elm327, ElmConfig
from .transport.errors import AdapterDisconnected, AdapterError
from .uds.client import DiagnosticClient

REAL_CONFIRMATION = "ICH BIN AM FAHRZEUG"

#: PIDs des Live-Dashboards (Reihenfolge = Abfragepriorität).
DASHBOARD_PIDS = [0x0C, 0x0D, 0x04, 0x05, 0x5C, 0x42, 0x0B, 0x33, 0x0F, 0x10, 0x11, 0x06, 0x07,
                  0x34, 0x24, 0x44, 0x0E, 0x5E, 0x46, 0x2F, 0x1F]
FAST_PIDS = {0x0C, 0x0D, 0x04, 0x11, 0x0B, 0x10}


@dataclass
class SessionState:
    status: str = "idle"          # idle|connecting|identifying|live|stopped|error|disconnected
    mode: str | None = None
    session_id: int | None = None
    adapter: dict = field(default_factory=dict)
    error: str | None = None
    started_at: float | None = None
    ecus: list[dict] = field(default_factory=list)
    dtcs: dict = field(default_factory=dict)
    obd_dtcs: dict = field(default_factory=dict)
    supported_pids: list[int] = field(default_factory=list)
    latest: dict[str, dict] = field(default_factory=dict)
    log: deque = field(default_factory=lambda: deque(maxlen=300))


def build_transport(spec: dict) -> ByteTransport:
    kind = spec.get("type", "demo")
    if kind == "demo":
        from .sim import SimFaults, VirtualElm327, build_demo_car
        return VirtualElm327(build_demo_car(), SimFaults(**spec.get("faults", {})))
    if kind == "ble":
        from .transport.ble import BleTransport
        return BleTransport(spec["address"])
    if kind == "serial":
        from .transport.serial_tcp import SerialTransport
        return SerialTransport(spec["port"], int(spec.get("baudrate", 38400)))
    if kind == "tcp":
        from .transport.serial_tcp import TcpTransport
        return TcpTransport(spec.get("host", "192.168.0.10"), int(spec.get("port", 35000)))
    raise ValueError(f"Unbekannter Adaptertyp {kind!r}")


class DiagnosticSession:
    def __init__(self, store: Store) -> None:
        self.store = store
        self.state = SessionState()
        self._thread: threading.Thread | None = None
        self._loop: asyncio.AbstractEventLoop | None = None
        self._stop = threading.Event()
        self._lock = threading.Lock()
        self.elm: Elm327 | None = None
        self.listeners: list = []

    # ------------------------------------------------------------ Steuerung
    def start(self, mode: str, adapter: dict | None = None, confirmation: str | None = None,
              identify: bool = True, live: bool = True) -> None:
        if mode not in ("demo", "real"):
            raise ValueError("mode muss 'demo' oder 'real' sein")
        if mode == "real":
            if (confirmation or "").strip().upper() != REAL_CONFIRMATION:
                raise PermissionError(f"Realer Verbindungstest nur mit Bestätigung „{REAL_CONFIRMATION}“.")
            if not adapter or adapter.get("type") == "demo":
                raise ValueError("Für den Realmodus muss ein Adapter angegeben werden")
        else:
            adapter = {"type": "demo", **({"faults": adapter.get("faults")} if adapter and adapter.get("faults") else {})}
        with self._lock:
            if self._thread and self._thread.is_alive():
                raise RuntimeError("Es läuft bereits eine Sitzung")
            self._stop.clear()
            self.state = SessionState(status="connecting", mode=mode, adapter=dict(adapter), started_at=time.time())
            self._thread = threading.Thread(target=self._run, args=(adapter, identify, live), daemon=True,
                                            name="f20-session")
            self._thread.start()

    def stop(self, timeout: float = 5.0) -> None:
        self._stop.set()
        t = self._thread
        if t:
            t.join(timeout)

    def wait_status(self, statuses: set[str], timeout: float = 10.0) -> str:
        end = time.time() + timeout
        while time.time() < end:
            if self.state.status in statuses:
                return self.state.status
            time.sleep(0.02)
        return self.state.status

    def _log(self, text: str) -> None:
        self.state.log.append({"t": time.time(), "text": text})

    # ------------------------------------------------------------ Ablauf
    def _run(self, adapter: dict, identify: bool, live: bool) -> None:
        loop = asyncio.new_event_loop()
        self._loop = loop
        try:
            loop.run_until_complete(self._main(adapter, identify, live))
        finally:
            loop.close()
            self._loop = None

    async def _main(self, adapter: dict, identify: bool, live: bool) -> None:
        st = self.state
        transport = build_transport(adapter)
        self.elm = elm = Elm327(transport, ReadOnlyPolicy(), ElmConfig())
        st.session_id = self.store.start_session(st.mode, {k: v for k, v in adapter.items() if k != "faults"})
        summary: dict = {}
        try:
            self._log(f"Verbinde mit Adapter ({adapter.get('type')}) …")
            await transport.open()
            info = await elm.initialize()
            st.adapter.update({"info": info.to_dict(), **transport.describe()})
            self._log(f"Adapter: {info.elm_version} {info.stn_id or ''} · {info.voltage or '?'} V")
            client = DiagnosticClient(elm)
            if identify and not self._stop.is_set():
                st.status = "identifying"
                await self._identify(client)
            summary = {"ecus_found": [e["address"] for e in st.ecus if e.get("responded")],
                       "dtc_count": sum(len(v) for v in st.dtcs.values() if isinstance(v, list)),
                       "supported_pids": len(st.supported_pids)}
            self.store.finish_session(st.session_id, summary)
            if live and not self._stop.is_set():
                st.status = "live"
                await self._live(client)
            st.status = "stopped"
        except AdapterDisconnected as exc:
            st.status, st.error = "disconnected", f"Verbindung verloren: {exc}"
            self._log(st.error)
        except (AdapterError, OSError, ValueError, PermissionError) as exc:
            st.status, st.error = "error", f"{type(exc).__name__}: {exc}"
            self._log(st.error)
        finally:
            summary.setdefault("end_status", st.status)
            if st.error:
                summary["error"] = st.error
            self.store.finish_session(st.session_id, summary)
            try:
                await elm.close()
            except Exception:  # noqa: BLE001
                pass

    async def _identify(self, client: DiagnosticClient) -> None:
        st = self.state
        ecus = load_json_data("ecus.json")["ecus"]
        for e in ecus:
            if self._stop.is_set():
                return
            addr = int(e["address"], 16)
            self._log(f"Prüfe {e['name']} (0x{addr:02X}) …")
            ident = await client.identify(addr, e["name"])
            d = ident.to_dict()
            d["safety_critical"] = e["safety_critical"]
            st.ecus.append(d)
            self.store.save_identity(st.session_id, d)
            if ident.responded:
                try:
                    dt = await client.read_dtcs(addr)
                    st.dtcs[d["address"]] = dt
                    self.store.save_dtcs(st.session_id, d["address"], dt)
                except AdapterDisconnected:
                    raise
                except AdapterError as exc:
                    st.dtcs[d["address"]] = {"error": str(exc)}
        try:
            st.obd_dtcs = await client.obd_dtcs()
            self.store.save_dtcs(st.session_id, "OBD", st.obd_dtcs)
            st.supported_pids = sorted(await client.obd_supported_pids())
            self._log(f"{len(st.supported_pids)} OBD-PIDs unterstützt")
        except AdapterDisconnected:
            raise
        except AdapterError as exc:
            self._log(f"OBD nicht verfügbar: {exc}")

    async def _live(self, client: DiagnosticClient) -> None:
        st = self.state
        if client.supported_pids is None:
            client.supported_pids = set(await client.obd_supported_pids())
            st.supported_pids = sorted(client.supported_pids)
        pids = [p for p in DASHBOARD_PIDS if p in client.supported_pids]
        if not pids:
            raise AdapterError("Keine der Dashboard-PIDs wird unterstützt")
        cycle, batch, last_flush = 0, [], time.time()
        while not self._stop.is_set():
            for pid in pids:
                if self._stop.is_set():
                    break
                if cycle % 4 and pid not in FAST_PIDS:
                    continue
                try:
                    r = await client.obd_read(pid)
                except AdapterDisconnected:
                    raise
                except AdapterError as exc:
                    self._log(f"PID 0x{pid:02X}: {exc}")
                    continue
                if r is None:
                    continue
                st.latest[r.key] = r.to_dict()
                batch.append(r)
            cycle += 1
            if time.time() - last_flush > 2 and batch:
                self.store.add_readings(st.session_id, batch)
                batch, last_flush = [], time.time()
            for cb in list(self.listeners):
                try:
                    cb(self.snapshot())
                except Exception:  # noqa: BLE001
                    pass
            await asyncio.sleep(0.05 if st.mode == "real" else 0.25)
        if batch:
            self.store.add_readings(st.session_id, batch)

    # ------------------------------------------------------------ Lesen
    def snapshot(self) -> dict:
        st = self.state
        values = {k: v["value"] for k, v in st.latest.items()}
        running = (time.time() - st.started_at) / 60 if st.started_at else None
        unavailable = []
        if st.supported_pids:
            unavailable = [{"pid": f"0x{p:02X}", "key": PIDS[p].key, "name_de": PIDS[p].name_de}
                           for p in DASHBOARD_PIDS if p in PIDS and p not in st.supported_pids]
        return {
            "status": st.status, "mode": st.mode, "demo": st.mode == "demo", "session_id": st.session_id,
            "adapter": st.adapter, "error": st.error, "started_at": st.started_at,
            "ecus": st.ecus, "dtcs": st.dtcs, "obd_dtcs": st.obd_dtcs,
            "supported_pids": [f"0x{p:02X}" for p in st.supported_pids],
            "latest": st.latest, "unavailable": unavailable,
            "derived": derived_values(values),
            "findings": engine_findings(values, running) if st.mode == "real" or values else [],
            "log": list(st.log)[-40:],
        }
