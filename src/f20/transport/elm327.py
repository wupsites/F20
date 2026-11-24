"""ELM327-/STN-Protokollschicht (read-only).

Die Klasse :class:`Elm327` ist die *einzige* Stelle, an der Text an den
Adapter gesendet wird. Jede ausgehende Zeile durchläuft die
:class:`~f20.safety.ReadOnlyPolicy`:

* AT-/ST-Befehle müssen auf der Positivliste stehen.
* Hex-Nutzdaten entstehen ausschließlich in :meth:`uds_request` bzw.
  :meth:`obd_request` und werden dort vor dem Senden gegen die UDS-/OBD-
  Positivliste geprüft. Eine öffentliche Methode zum Senden beliebiger
  Rohdaten existiert nicht.

BMW-F-Serie (D-CAN, 500 kBit/s, 11 Bit):
  Tester-CAN-ID 0x6F1, Extended Addressing (1. Datenbyte = ECU-Adresse),
  Antwort der ECU auf 0x600 + Adresse mit 1. Datenbyte 0xF1.
  Quellen und Nachweisstatus: docs/research/raw/01_architektur_protokoll.md,
  docs/research/raw/03_adapter_kommunikation.md, ADAPTER_COMPATIBILITY.md.
"""

from __future__ import annotations

import asyncio
import re
import time
from dataclasses import dataclass, field
from typing import Callable

from ..safety import DEFAULT_POLICY, ReadOnlyPolicy, ReadOnlyViolation
from ..uds.nrc import nrc_text
from .base import ByteTransport
from .errors import (
    AdapterDisconnected,
    AdapterError,
    AdapterTimeout,
    AdapterUnsupported,
    BusError,
    NegativeResponse,
    NoData,
)
from .isotp import CanFrame, IsoTpError, parse_elm_frame_line, reassemble

TESTER_CAN_ID = 0x6F1
BMW_RESPONSE_BASE = 0x600
OBD_FUNCTIONAL_ID = 0x7DF

_BUS_ERRORS = (
    "CAN ERROR", "BUS ERROR", "BUFFER FULL", "BUS BUSY", "DATA ERROR",
    "<RX ERROR", "RX ERROR", "FB ERROR", "LV RESET", "STOPPED",
    "UNABLE TO CONNECT", "ACT ALERT", "ERR",
)
_NOISE = ("SEARCHING...", "SEARCHING", "BUS INIT: ...OK", "BUS INIT: OK", "OK")


@dataclass
class ElmConfig:
    response_timeout: float = 4.0      # Sekunden bis zum Prompt '>'
    reset_timeout: float = 6.0
    spaces: bool = True                # ATS1 – robuster zu parsen
    st_timeout: int = 0x64             # ATST in 4-ms-Schritten (0x64 = 400 ms)
    manual_flow_control: bool = True   # ATFCSH/ATFCSD/ATFCSM1 für Extended Addressing
    pending_retries: int = 3           # Wiederholungen bei NRC 0x78 (responsePending)
    raw_isotp_fallback: bool = False   # EXPERIMENTELL: CAF0 + eigenes ISO-TP, falls kein ATCEA


@dataclass
class AdapterInfo:
    elm_version: str | None = None
    description: str | None = None
    device_id: str | None = None
    stn_id: str | None = None
    voltage: float | None = None
    protocol: str | None = None
    supports_cea: bool | None = None
    supports_fc_manual: bool | None = None
    clone_suspected: bool = False
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return dict(self.__dict__)


@dataclass
class TraceEntry:
    t: float
    direction: str   # "TX" | "RX" | "BLOCK"
    text: str


class Elm327:
    def __init__(
        self,
        transport: ByteTransport,
        policy: ReadOnlyPolicy | None = None,
        config: ElmConfig | None = None,
        on_trace: Callable[[TraceEntry], None] | None = None,
    ) -> None:
        self.transport = transport
        self.policy = policy or DEFAULT_POLICY
        self.config = config or ElmConfig()
        self.info = AdapterInfo()
        self.trace: list[TraceEntry] = []
        self._on_trace = on_trace
        self._state: dict[str, object] = {}
        self._approved_payload: str | None = None
        self._lock = asyncio.Lock()
        self._mode: tuple | None = None
        self.raw_mode = False

    # ------------------------------------------------------------------ I/O
    def _log(self, direction: str, text: str) -> None:
        e = TraceEntry(time.time(), direction, text)
        self.trace.append(e)
        if len(self.trace) > 4000:
            del self.trace[:1000]
        if self._on_trace:
            self._on_trace(e)

    async def _send_line(self, line: str, timeout: float | None = None) -> list[str]:
        """Sendet eine bereits geprüfte Zeile und liest bis zum Prompt."""
        line = line.strip().upper()
        if line.startswith(("AT", "ST")):
            self.policy.check_at(line)  # zweite Prüfung (Defense in Depth)
        elif line != self._approved_payload:
            self._log("BLOCK", line)
            raise ReadOnlyViolation(f"Nicht freigegebene Rohdaten blockiert: {line!r}")
        self._approved_payload = None
        if not self.transport.is_open:
            raise AdapterDisconnected("Adapter nicht verbunden")
        timeout = timeout or self.config.response_timeout
        self._log("TX", line)
        await self.transport.write((line + "\r").encode("ascii"))
        buf = bytearray()
        deadline = asyncio.get_running_loop().time() + timeout
        while b">" not in buf:
            remaining = deadline - asyncio.get_running_loop().time()
            if remaining <= 0:
                self._log("RX", buf.decode("ascii", "replace"))
                raise AdapterTimeout(f"Kein Prompt nach {timeout:.1f}s auf {line!r}")
            chunk = await self.transport.read(min(remaining, 0.5))
            if chunk:
                buf.extend(chunk.replace(b"\x00", b""))
        text = buf[: buf.index(b">")].decode("ascii", "replace")
        self._log("RX", text)
        lines = [ln.strip() for ln in re.split(r"[\r\n]+", text) if ln.strip()]
        # Echo entfernen (falls ATE0 noch nicht aktiv)
        if lines and lines[0].replace(" ", "").upper() == line.replace(" ", ""):
            lines = lines[1:]
        return lines

    async def _drain(self) -> None:
        for _ in range(5):
            if not await self.transport.read(0.05):
                break

    # ------------------------------------------------------------------ AT
    async def at(self, cmd: str, *, timeout: float | None = None, optional: bool = False) -> list[str]:
        c = self.policy.check_at(cmd if cmd.upper().startswith(("AT", "ST")) else "AT" + cmd)
        lines = await self._send_line(c, timeout)
        if lines and lines[-1] == "?":
            if optional:
                raise AdapterUnsupported(c)
            raise AdapterUnsupported(f"Adapter kennt Befehl {c} nicht")
        return lines

    async def _at_cached(self, key: str, cmd: str, *, optional: bool = False) -> None:
        if self._state.get(key) == cmd:
            return
        await self.at(cmd, optional=optional)
        self._state[key] = cmd

    async def initialize(self) -> AdapterInfo:
        """Initialisiert den Adapter für CAN 11 Bit / 500 kBit/s.

        Spricht ausschließlich mit dem Adapter – noch keine Fahrzeuganfrage.
        """
        async with self._lock:
            await self._drain()
            self._state.clear()
            self._mode = None
            ident = await self.at("ATZ", timeout=self.config.reset_timeout)
            await asyncio.sleep(0.2)
            await self._drain()
            for c in ("ATE0", "ATL0", "ATS1" if self.config.spaces else "ATS0", "ATH1", "ATAL"):
                await self.at(c)
            await self.at("ATSP6")  # ISO 15765-4 CAN 11 Bit 500 kBit/s
            await self.at(f"ATST{self.config.st_timeout:02X}")
            info = AdapterInfo()
            vlines = await self.at("ATI")
            info.elm_version = (vlines[-1] if vlines else None) or (ident[-1] if ident else None)
            try:
                info.description = " ".join(await self.at("AT@1", optional=True)) or None
            except AdapterUnsupported:
                info.notes.append("AT@1 nicht unterstützt")
            try:
                info.stn_id = " ".join(await self.at("STI", optional=True)) or None
            except AdapterUnsupported:
                info.stn_id = None
            try:
                rv = " ".join(await self.at("ATRV", optional=True))
                m = re.search(r"(\d+(?:\.\d+)?)\s*V", rv)
                info.voltage = float(m.group(1)) if m else None
            except AdapterUnsupported:
                info.notes.append("ATRV nicht unterstützt")
            try:
                await self.at("ATCEA", optional=True)   # CEA aus – testet Unterstützung
                info.supports_cea = True
            except AdapterUnsupported:
                info.supports_cea = False
                info.notes.append(
                    "ATCEA (CAN Extended Addressing) nicht unterstützt – BMW-UDS über D-CAN "
                    "nur mit experimentellem Raw-ISO-TP-Modus möglich."
                )
            try:
                await self.at("ATFCSM0", optional=True)
                info.supports_fc_manual = True
            except AdapterUnsupported:
                info.supports_fc_manual = False
                info.notes.append("ATFCSM nicht unterstützt – Multi-Frame-Antworten evtl. unvollständig.")
            ver = (info.elm_version or "").upper()
            if "V1.5" in ver:
                info.clone_suspected = True
                info.notes.append("'ELM327 v1.5' wurde von Elm Electronics nie veröffentlicht → Klon.")
            elif "V2.1" in ver and not info.stn_id:
                info.clone_suspected = True
                info.notes.append("'v2.1' ist bei günstigen Adaptern häufig ein Klon (Verdacht, kein Beweis).")
            try:
                info.protocol = " ".join(await self.at("ATDPN", optional=True)) or None
            except AdapterUnsupported:
                pass
            self.info = info
            return info

    # ------------------------------------------------------------- Adressierung
    async def _select_uds_ecu(self, ecu: int) -> None:
        if not 0 <= ecu <= 0xFF:
            raise ValueError("ECU-Adresse muss 0x00–0xFF sein")
        if self._mode == ("uds", ecu, self.raw_mode):
            return
        if self.info.supports_cea is False and not self.raw_mode:
            if self.config.raw_isotp_fallback:
                self.raw_mode = True
            else:
                raise AdapterUnsupported(
                    "Adapter unterstützt kein ATCEA – BMW-Steuergeräte über D-CAN nicht erreichbar. "
                    "(Experimentellen Raw-ISO-TP-Modus nur nach Prüfung aktivieren.)"
                )
        await self._at_cached("hdr", f"ATSH{TESTER_CAN_ID:03X}")
        await self._at_cached("cra", f"ATCRA{BMW_RESPONSE_BASE + ecu:03X}")
        if self.raw_mode:
            await self._at_cached("caf", "ATCAF0")
            if self.info.supports_cea:
                await self._at_cached("cea", "ATCEA")
        else:
            await self._at_cached("caf", "ATCAF1")
            await self._at_cached("cea", f"ATCEA{ecu:02X}")
            if self.config.manual_flow_control and self.info.supports_fc_manual is not False:
                await self._at_cached("fcsh", f"ATFCSH{TESTER_CAN_ID:03X}")
                await self._at_cached("fcsd", f"ATFCSD{ecu:02X}300000")
                await self._at_cached("fcsm", "ATFCSM1")
        self._mode = ("uds", ecu, self.raw_mode)

    async def _select_obd_functional(self) -> None:
        if self._mode == ("obd",):
            return
        await self._at_cached("caf", "ATCAF1")
        if self.info.supports_cea is not False:
            await self._at_cached("cea", "ATCEA")
        if self.info.supports_fc_manual is not False:
            await self._at_cached("fcsm", "ATFCSM0")
        await self._at_cached("hdr", f"ATSH{OBD_FUNCTIONAL_ID:03X}")
        await self._at_cached("cra", "ATCRA")
        self._mode = ("obd",)

    # ------------------------------------------------------------- Anfragen
    def _check_errors(self, lines: list[str]) -> None:
        joined = " ".join(lines).upper()
        if not lines or "NO DATA" in joined:
            raise NoData("Keine Antwort vom Fahrzeug (Zündung an? Adresse korrekt?)")
        for err in _BUS_ERRORS:
            if any(ln.upper().startswith(err) for ln in lines):
                raise BusError(f"Adapter meldet: {joined}")
        if lines[-1] == "?":
            raise AdapterUnsupported("Adapter hat die Anfrage nicht verstanden")

    @staticmethod
    def _frames(lines: list[str]) -> list[CanFrame]:
        out = []
        for ln in lines:
            if ln.upper() in _NOISE:
                continue
            fr = parse_elm_frame_line(ln)
            if fr is not None:
                out.append(fr)
        return out

    async def uds_request(self, ecu: int, payload: bytes) -> bytes:
        """Sendet eine *lesende* UDS-Anfrage an eine BMW-ECU (physikalisch).

        Gibt die positive Antwort (inkl. Service-ID+0x40) zurück oder wirft
        :class:`NegativeResponse`.
        """
        self.policy.enforce_uds(payload, ecu)
        async with self._lock:
            await self._select_uds_ecu(ecu)
            resp_id = BMW_RESPONSE_BASE + ecu
            for attempt in range(self.config.pending_retries + 1):
                msgs = await (self._raw_exchange(ecu, payload) if self.raw_mode
                              else self._caf_exchange(payload, resp_id))
                final = [m for m in msgs if not (len(m) >= 3 and m[0] == 0x7F and m[2] == 0x78)]
                if final:
                    return self._validate(payload, final[-1])
                if attempt < self.config.pending_retries:
                    await asyncio.sleep(0.3 * (attempt + 1))
            raise AdapterTimeout(f"ECU 0x{ecu:02X} meldet dauerhaft 'responsePending' (NRC 0x78)")

    async def _caf_exchange(self, payload: bytes, resp_id: int) -> list[bytes]:
        hexline = payload.hex().upper()
        self._approved_payload = hexline
        lines = await self._send_line(hexline)
        self._check_errors(lines)
        try:
            return reassemble(self._frames(lines), resp_id, extended=True)
        except IsoTpError as exc:
            raise AdapterError(f"ISO-TP-Fehler: {exc}") from exc

    async def _raw_exchange(self, ecu: int, payload: bytes) -> list[bytes]:
        """EXPERIMENTELL: ISO-TP manuell mit ATCAF0 (für Adapter ohne ATCEA)."""
        if len(payload) > 6:
            raise ReadOnlyViolation("Raw-Modus unterstützt nur Single-Frame-Anfragen")
        resp_id = BMW_RESPONSE_BASE + ecu
        # BMW D-CAN: immer DLC 8 mit 0x00-Padding (RESEARCH.md §UDS über D-CAN)
        frame = (bytes([ecu, len(payload)]) + payload).ljust(8, b"\x00")
        hexline = frame.hex().upper()
        self._approved_payload = hexline
        lines = await self._send_line(hexline)
        self._check_errors(lines)
        frames = self._frames(lines)
        for _ in range(64):
            try:
                return reassemble(frames, resp_id, extended=True)
            except IsoTpError as exc:
                if "Unvollständig" not in str(exc):
                    raise AdapterError(f"ISO-TP-Fehler: {exc}") from exc
            # Flow Control manuell senden: [ECU, 0x30, BS=0, STmin=0]
            fc = bytes([ecu, 0x30, 0x00, 0x00]).ljust(8, b"\x00").hex().upper()
            self._approved_payload = fc
            more = await self._send_line(fc)
            if any("NO DATA" in ln.upper() for ln in more):
                break
            frames += self._frames(more)
        raise AdapterError("Raw-ISO-TP: Antwort unvollständig")

    def _validate(self, request: bytes, resp: bytes) -> bytes:
        if resp[0] == 0x7F:
            nrc = resp[2] if len(resp) > 2 else 0
            raise NegativeResponse(resp[1] if len(resp) > 1 else request[0], nrc, nrc_text(nrc))
        if resp[0] != (request[0] + 0x40) & 0xFF:
            raise AdapterError(f"Unerwartete Antwort {resp[:4].hex()} auf {request.hex()}")
        if request[0] == 0x22 and resp[1:3] != request[1:3]:
            raise AdapterError("Antwort-DID passt nicht zur Anfrage")
        return resp

    async def obd_request(self, payload: bytes) -> dict[int, bytes]:
        """Standard-OBD-II-Anfrage (funktional an 0x7DF). Antwort je CAN-ID."""
        self.policy.enforce_obd(payload)
        async with self._lock:
            await self._select_obd_functional()
            hexline = payload.hex().upper()
            self._approved_payload = hexline
            lines = await self._send_line(hexline)
            self._check_errors(lines)
            frames = self._frames(lines)
            result: dict[int, bytes] = {}
            for cid in sorted({f.can_id for f in frames}):
                if not 0x7E8 <= cid <= 0x7EF:
                    continue
                try:
                    msgs = reassemble(frames, cid, extended=False)
                except IsoTpError as exc:
                    raise AdapterError(f"ISO-TP-Fehler (OBD): {exc}") from exc
                for m in msgs:
                    if m and m[0] == (payload[0] + 0x40):
                        result[cid] = m
            if not result:
                raise NoData("Keine gültige OBD-Antwort")
            return result

    async def close(self) -> None:
        try:
            if self.transport.is_open:
                try:
                    await self.at("ATPC", optional=True)
                except AdapterError:
                    pass
        finally:
            await self.transport.close()
