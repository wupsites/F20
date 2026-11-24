"""Virtueller ELM327-Adapter (Byte-Transport) für Tests und Demomodus.

Emuliert die für dieses Projekt relevanten AT-Befehle und das
Ausgabeformat (Header, Leerzeichen, Prompt '>') sowie typische Fehlerbilder
günstiger Klone (fehlendes ATCEA/ATFCSM, Verbindungsabbrüche, Busfehler).

Das Verhalten bei Extended Addressing (ATCEA + manuelle Flow Control) bildet
die im Projekt dokumentierte *Annahme* ab und ist an einem echten Adapter
zu bestätigen (siehe ADAPTER_COMPATIBILITY.md).
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field

from ..transport.base import ByteTransport
from ..transport.errors import AdapterDisconnected
from ..transport.isotp import CanFrame
from .car import VirtualCar


@dataclass
class SimFaults:
    version: str = "ELM327 v2.1"
    description: str = "F20 Simulator (DEMO)"
    stn: str | None = None              # z. B. "STN2120 v5.6.5" für OBDLink-Emulation
    supports_cea: bool = True
    supports_fc_manual: bool = True
    disconnect_after_writes: int | None = None
    latency: float = 0.0
    forced_responses: list[str] = field(default_factory=list)  # für nächste Datenanfragen
    voltage: float = 12.6


class VirtualElm327(ByteTransport):
    name = "simulator"

    def __init__(self, car: VirtualCar, faults: SimFaults | None = None) -> None:
        self.car = car
        self.faults = faults or SimFaults()
        self._open = False
        self._inbuf = bytearray()
        self._out = bytearray()
        self._writes = 0
        self.received_lines: list[str] = []
        self._reset()

    # ------------------------------------------------------------ Transport
    async def open(self) -> None:
        self._open = True

    async def close(self) -> None:
        self._open = False

    @property
    def is_open(self) -> bool:
        return self._open

    def describe(self) -> dict:
        return {"transport": "simulator", "version": self.faults.version, "demo": True}

    async def write(self, data: bytes) -> None:
        if not self._open:
            raise AdapterDisconnected("Simulator getrennt")
        self._writes += 1
        if self.faults.disconnect_after_writes is not None and self._writes > self.faults.disconnect_after_writes:
            self._open = False
            raise AdapterDisconnected("Simulierter Verbindungsabbruch")
        self._inbuf.extend(data)
        while b"\r" in self._inbuf:
            idx = self._inbuf.index(b"\r")
            line = self._inbuf[:idx].decode("ascii", "replace")
            del self._inbuf[: idx + 1]
            self._out.extend(self._process(line).encode("ascii"))

    async def read(self, timeout: float) -> bytes:
        if not self._open:
            raise AdapterDisconnected("Simulator getrennt")
        if self.faults.latency:
            await asyncio.sleep(min(self.faults.latency, timeout))
        if not self._out:
            await asyncio.sleep(min(timeout, 0.01))
            if not self._open:
                raise AdapterDisconnected("Simulator getrennt")
            return b""
        data = bytes(self._out)
        self._out.clear()
        return data

    # ------------------------------------------------------------ ELM-Logik
    def _reset(self) -> None:
        self.echo = True
        self.linefeed = False
        self.spaces = True
        self.headers = False
        self.protocol = "0"
        self.header = 0x7DF
        self.cea: int | None = None
        self.cra: int | None = None
        self.caf = True
        self.cfc = True
        self.fcsm = 0
        self.fcsh: int | None = None
        self.fcsd = b""

    def _nl(self) -> str:
        return "\r\n" if self.linefeed else "\r"

    def _reply(self, cmd: str, body: str) -> str:
        nl = self._nl()
        prefix = (cmd + nl) if self.echo else ""
        return f"{prefix}{body}{nl}{nl}>"

    def _process(self, raw: str) -> str:
        self.received_lines.append(raw)
        cmd = raw.strip().upper().replace(" ", "")
        if not cmd:
            return ">"
        if cmd.startswith("AT"):
            return self._reply(raw.strip(), self._at(cmd[2:]))
        if cmd.startswith("ST"):
            if self.faults.stn and cmd == "STI":
                return self._reply(raw.strip(), self.faults.stn)
            return self._reply(raw.strip(), "?")
        try:
            payload = bytes.fromhex(cmd)
        except ValueError:
            return self._reply(raw.strip(), "?")
        return self._reply(raw.strip(), self._data(payload))

    def _at(self, c: str) -> str:
        f = self.faults
        if c in ("Z", "WS"):
            self._reset()
            return f"{self._nl()}{f.version}"
        if c == "D":
            self._reset()
            return "OK"
        if c == "I":
            return f.version
        if c == "@1":
            return f.description
        if c == "RV":
            return f"{f.voltage:.1f}V"
        if c in ("E0", "E1"):
            self.echo = c == "E1"
            return "OK"
        if c in ("L0", "L1"):
            self.linefeed = c == "L1"
            return "OK"
        if c in ("S0", "S1"):
            self.spaces = c == "S1"
            return "OK"
        if c in ("H0", "H1"):
            self.headers = c == "H1"
            return "OK"
        if c in ("AL", "NL", "AT0", "AT1", "AT2", "PC", "CFC1", "CFC0") or c.startswith("ST"):
            if c.startswith("CFC"):
                self.cfc = c == "CFC1"
            return "OK"
        if c.startswith("SP") and len(c) in (3, 4):
            self.protocol = c[-1]
            return "OK"
        if c in ("DPN",):
            return "A6" if self.protocol == "0" else self.protocol
        if c.startswith("SH") and len(c) == 5:
            self.header = int(c[2:], 16)
            return "OK"
        if c.startswith("CEA"):
            if not f.supports_cea:
                return "?"
            self.cea = int(c[3:], 16) if len(c) == 5 else None
            return "OK"
        if c.startswith("CRA"):
            self.cra = int(c[3:], 16) if len(c) == 6 else None
            return "OK"
        if c in ("CAF0", "CAF1"):
            self.caf = c == "CAF1"
            return "OK"
        if c.startswith("FCSM"):
            if not f.supports_fc_manual:
                return "?"
            self.fcsm = int(c[4:])
            return "OK"
        if c.startswith("FCSH"):
            if not f.supports_fc_manual:
                return "?"
            self.fcsh = int(c[4:], 16)
            return "OK"
        if c.startswith("FCSD"):
            if not f.supports_fc_manual:
                return "?"
            self.fcsd = bytes.fromhex(c[4:])
            return "OK"
        if c == "CS":
            return "T:00 R:00"
        return "?"

    def _fmt(self, fr: CanFrame) -> str:
        sep = " " if self.spaces else ""
        data = sep.join(f"{b:02X}" for b in fr.data)
        if self.headers:
            return f"{fr.can_id:03X}{sep}{data}"
        return data

    def _accept(self, fr: CanFrame) -> bool:
        if self.cra is not None:
            return fr.can_id == self.cra
        if self.header == 0x7DF:
            return 0x7E8 <= fr.can_id <= 0x7EF
        return True

    def _data(self, payload: bytes) -> str:
        if self.faults.forced_responses:
            return self.faults.forced_responses.pop(0)
        if self.protocol not in ("0", "6"):
            return "NO DATA"
        search = "SEARCHING..." + self._nl() if self.protocol == "0" else ""
        if self.caf:
            room = 7 - (1 if self.cea is not None else 0)
            if len(payload) > room:
                return "?"
            data = (bytes([self.cea]) if self.cea is not None else b"") + bytes([len(payload)]) + payload
        else:
            if len(payload) > 8:
                return "?"
            data = payload
        frames = [fr for fr in self.car.receive(self.header, data) if self._accept(fr)]
        # Automatische Flow Control des Adapters (nur mit CAF1/CFC1)
        guard = 0
        while self.caf and self.cfc and frames and guard < 8:
            last = frames[-1]
            d = last.data
            if self.cea is not None and d and d[0] == 0xF1:
                d = d[1:]
            if not d or (d[0] >> 4) != 0x1:
                break
            if self.fcsm == 1 and self.fcsh is not None:
                fc_id, fc_data = self.fcsh, self.fcsd
            else:
                fc_id, fc_data = last.can_id - 8, b"\x30\x00\x00"
            more = [fr for fr in self.car.receive(fc_id, fc_data) if self._accept(fr)]
            if not more:
                break
            frames += more
            guard += 1
        if not frames:
            return search + "NO DATA"
        return search + self._nl().join(self._fmt(fr) for fr in frames)
