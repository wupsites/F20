"""Virtueller F20 für Tests und Demomodus (fiktive Daten!)."""

from __future__ import annotations

import math
import random
import time
from dataclasses import dataclass, field

from ..transport.isotp import TESTER_ADDRESS, CanFrame, segment
from ..uds.svk import SgbmId

#: Fiktive FIN – enthält bewusst die in echten FINs unzulässigen Buchstaben I und O.
DEMO_VIN = "DEMO0F20SIM000001"

WRITE_LIKE_SERVICES = {0x11, 0x14, 0x27, 0x28, 0x2C, 0x2E, 0x2F, 0x31, 0x34, 0x35, 0x36, 0x37, 0x3D, 0x85}


@dataclass
class VirtualEcu:
    address: int
    name: str
    dids: dict[int, bytes] = field(default_factory=dict)
    dtcs: list[tuple[int, int]] = field(default_factory=list)  # (3-Byte-Code, Status)
    slow_dids: set[int] = field(default_factory=set)            # antworten zuerst mit NRC 0x78
    received: list[bytes] = field(default_factory=list)
    write_attempts: list[bytes] = field(default_factory=list)

    def handle(self, req: bytes) -> list[bytes]:
        """Gibt eine Liste von Antworten zurück (z. B. [7F 22 78, 62 …])."""
        self.received.append(req)
        sid = req[0]
        if sid in WRITE_LIKE_SERVICES:
            # Zweite Verteidigungslinie: Simulator protokolliert jeden Versuch.
            self.write_attempts.append(req)
            return [bytes([0x7F, sid, 0x11])]
        if sid == 0x22 and len(req) == 3:
            did = (req[1] << 8) | req[2]
            if did not in self.dids:
                return [bytes([0x7F, 0x22, 0x31])]
            ok = bytes([0x62, req[1], req[2]]) + self.dids[did]
            if did in self.slow_dids:
                return [bytes([0x7F, 0x22, 0x78]), ok]
            return [ok]
        if sid == 0x3E and len(req) >= 2:
            return [] if req[1] & 0x80 else [b"\x7E\x00"]
        if sid == 0x10 and len(req) >= 2:
            if req[1] == 0x01:
                return [b"\x50\x01\x00\x32\x01\xF4"]
            return [bytes([0x7F, 0x10, 0x12])]
        if sid == 0x19 and len(req) >= 3 and req[1] in (0x02, 0x0A):
            mask = req[2] if req[1] == 0x02 else 0xFF
            body = b"".join(c.to_bytes(3, "big") + bytes([s]) for c, s in self.dtcs if s & mask)
            return [bytes([0x59, req[1], 0xFF]) + body]
        return [bytes([0x7F, sid, 0x11])]


class VirtualEngine:
    """Einfaches, deterministisches Motormodell (fiktiv, nur für die Demo)."""

    def __init__(self, seed: int = 20, t0: float | None = None) -> None:
        self.rng = random.Random(seed)
        self.t0 = time.monotonic() if t0 is None else t0
        self.fixed_t: float | None = None

    def t(self) -> float:
        return self.fixed_t if self.fixed_t is not None else time.monotonic() - self.t0

    def state(self) -> dict:
        t = self.t()
        n = self.rng.uniform(-1, 1)
        cycle = t % 120
        if cycle < 20:
            speed = 0.0
        elif cycle < 60:
            speed = 30 + 60 * math.sin((cycle - 20) / 40 * math.pi / 2)
        elif cycle < 100:
            speed = 90 - 20 * math.sin((cycle - 60) / 40 * math.pi)
        else:
            speed = max(0.0, 90 * (1 - (cycle - 100) / 20))
        gear_ratio = 0 if speed < 1 else (52 if speed < 25 else 32 if speed < 45 else 24 if speed < 70 else 19)
        rpm = 720 + 15 * n if speed < 1 else max(1100.0, speed * gear_ratio)
        accel = 0.0 if speed < 1 else max(0.0, math.cos(cycle / 120 * 2 * math.pi))
        load = 18 + 4 * n if speed < 1 else min(95.0, 25 + 55 * accel)
        coolant = 20 + 72 * (1 - math.exp(-t / 300))
        return {
            "rpm": rpm, "speed": speed, "load": load,
            "coolant": coolant, "iat": 24 + 3 * accel,
            "maf": rpm * load / 6000 * 2.0,
            "map": 30 + load * 0.7,
            "throttle": 3 + load * 0.6,
            "stft": 1.5 * n, "ltft": 2.3,
            "lambda": 1.0 + 0.015 * n,
            "voltage": 14.2 + 0.1 * n,
            "timing": 12 + 10 * (1 - load / 100),
            "baro": 99, "ambient": 9, "run_time": t, "fuel_level": 62.0,
        }


def _b(v: float, lo: int = 0, hi: int = 255) -> int:
    return max(lo, min(hi, int(round(v))))


class VirtualCar:
    """Virtueller D-CAN-Bus: BMW-UDS (0x6F1, Extended Addressing) + OBD-II."""

    #: Im Demomodus unterstützte OBD-PIDs (bewusst OHNE 0x5C Öltemperatur und
    #: 0x5E Kraftstoffrate, um die Anzeige „nicht verfügbar“ zu demonstrieren).
    DEMO_PIDS = [0x01, 0x03, 0x04, 0x05, 0x06, 0x07, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F,
                 0x10, 0x11, 0x1C, 0x1F, 0x20, 0x21, 0x2F, 0x33, 0x34, 0x40, 0x42,
                 0x44, 0x46]

    def __init__(self, ecus: dict[int, VirtualEcu], engine: VirtualEngine | None = None,
                 dme_address: int = 0x12, obd_dtcs: dict[int, list[str]] | None = None) -> None:
        self.ecus = ecus
        self.engine = engine or VirtualEngine()
        self.dme_address = dme_address
        self.ignition_on = True
        self.obd_dtcs = obd_dtcs or {0x03: [], 0x07: [], 0x0A: []}
        self._awaiting: dict[int, tuple[int, list[bytes]]] = {}
        self.drop_consecutive = False
        self.bus_log: list[CanFrame] = []

    # ---------------------------------------------------------------- Bus
    def receive(self, can_id: int, data: bytes) -> list[CanFrame]:
        self.bus_log.append(CanFrame(can_id, bytes(data)))
        if not self.ignition_on:
            return []
        if can_id == 0x6F1 and data:
            return self._bmw(data)
        if can_id == 0x7DF and data:
            return self._obd_request(data)
        if can_id == 0x7E0 and data and (data[0] >> 4) == 3:
            return self._continue(0x7E8)
        return []

    def _continue(self, resp_id: int) -> list[CanFrame]:
        pend = self._awaiting.pop(resp_id, None)
        if not pend:
            return []
        frames = pend[1]
        if self.drop_consecutive and frames:
            frames = frames[1:]
        return [CanFrame(resp_id, f) for f in frames]

    def _bmw(self, data: bytes) -> list[CanFrame]:
        target, rest = data[0], data[1:]
        if not rest:
            return []
        resp_id = 0x600 + target
        pci = rest[0] >> 4
        if pci == 0x3:  # Flow Control vom Tester (muss Extended Address der ECU tragen)
            if resp_id in self._awaiting:
                return self._continue(resp_id)
            return []
        ecu = self.ecus.get(target)
        if ecu is None or pci != 0x0:
            return []
        length = rest[0] & 0x0F
        req = bytes(rest[1:1 + length])
        out: list[CanFrame] = []
        for resp in ecu.handle(req):
            frames = segment(resp, TESTER_ADDRESS)
            out.append(CanFrame(resp_id, frames[0]))
            if len(frames) > 1:
                self._awaiting[resp_id] = (target, frames[1:])
        return out

    # ---------------------------------------------------------------- OBD
    def _obd_request(self, data: bytes) -> list[CanFrame]:
        length = data[0] & 0x0F
        req = bytes(data[1:1 + length])
        resp = self._obd_answer(req)
        if resp is None:
            return []
        frames = segment(resp, None)
        if len(frames) > 1:
            self._awaiting[0x7E8] = (0, frames[1:])
        return [CanFrame(0x7E8, frames[0])]

    def _obd_answer(self, req: bytes) -> bytes | None:
        mode = req[0]
        if mode == 0x01 and len(req) >= 2:
            pid = req[1]
            enc = self._encode_pid(pid)
            return None if enc is None else bytes([0x41, pid]) + enc
        if mode in (0x03, 0x07, 0x0A):
            codes = self.obd_dtcs.get(mode, [])
            body = b"".join(_encode_obd_dtc(c) for c in codes)
            return bytes([mode + 0x40, len(codes)]) + body
        if mode == 0x09 and len(req) >= 2 and req[1] == 0x02:
            vin = self.ecus.get(self.dme_address, VirtualEcu(0, "")).dids.get(0xF190, DEMO_VIN.encode())
            return b"\x49\x02\x01" + vin
        return None

    def _encode_pid(self, pid: int) -> bytes | None:
        if pid in (0x00, 0x20, 0x40, 0x60):
            bits = 0
            for p in self.DEMO_PIDS:
                if pid < p <= pid + 0x20:
                    bits |= 1 << (31 - (p - pid - 1))
            return bits.to_bytes(4, "big") if pid == 0x00 or pid in self.DEMO_PIDS else None
        if pid not in self.DEMO_PIDS:
            return None
        s = self.engine.state()
        if pid == 0x01:
            return bytes([0x00, 0x07, 0xE5, 0x00])
        if pid == 0x03:
            return bytes([0x02 if s["coolant"] > 40 else 0x01, 0x00])
        if pid == 0x04:
            return bytes([_b(s["load"] * 255 / 100)])
        if pid == 0x05:
            return bytes([_b(s["coolant"] + 40)])
        if pid == 0x06:
            return bytes([_b(s["stft"] * 128 / 100 + 128)])
        if pid == 0x07:
            return bytes([_b(s["ltft"] * 128 / 100 + 128)])
        if pid == 0x0B:
            return bytes([_b(s["map"])])
        if pid == 0x0C:
            v = _b(s["rpm"] * 4, 0, 0xFFFF)
            return v.to_bytes(2, "big")
        if pid == 0x0D:
            return bytes([_b(s["speed"])])
        if pid == 0x0E:
            return bytes([_b((s["timing"] + 64) * 2)])
        if pid == 0x0F:
            return bytes([_b(s["iat"] + 40)])
        if pid == 0x10:
            return _b(s["maf"] * 100, 0, 0xFFFF).to_bytes(2, "big")
        if pid == 0x11:
            return bytes([_b(s["throttle"] * 255 / 100)])
        if pid == 0x1C:
            return bytes([0x06])  # EOBD
        if pid == 0x1F:
            return _b(s["run_time"], 0, 0xFFFF).to_bytes(2, "big")
        if pid == 0x21:
            return b"\x00\x00"
        if pid == 0x2F:
            return bytes([_b(s["fuel_level"] * 255 / 100)])
        if pid == 0x33:
            return bytes([_b(s["baro"])])
        if pid == 0x34:
            lam = _b(s["lambda"] * 65536 / 2, 0, 0xFFFF)
            return lam.to_bytes(2, "big") + b"\x80\x00"
        if pid == 0x42:
            return _b(s["voltage"] * 1000, 0, 0xFFFF).to_bytes(2, "big")
        if pid == 0x44:
            return _b(1.0 * 65536 / 2, 0, 0xFFFF).to_bytes(2, "big")
        if pid == 0x46:
            return bytes([_b(s["ambient"] + 40)])
        return None

    # ------------------------------------------------------------ Prüfung
    def all_write_attempts(self) -> list[tuple[int, bytes]]:
        return [(a, w) for a, e in self.ecus.items() for w in e.write_attempts]


def _encode_obd_dtc(code: str) -> bytes:
    letter = "PCBU".index(code[0])
    b1 = (letter << 6) | (int(code[1]) << 4) | int(code[2], 16)
    b2 = int(code[3:5], 16)
    return bytes([b1, b2])


def _svk(*sgbm: str) -> bytes:
    entries = [SgbmId.parse(s) for s in sgbm]
    head = bytes([0x01, 0x01]) + len(entries).to_bytes(2, "big")
    # 13-Byte-Kopfblock (DEMO): PROG_DATUM 2012-01-24 (BCD), unbekannt, PROG_KM/10, Rest 0
    head += bytes([0x12, 0x01, 0x24, 0x8A]) + (1234).to_bytes(2, "big") + bytes(7)
    return head + b"".join(e.to_bytes() for e in entries)


def build_demo_car(seed: int = 20) -> VirtualCar:
    """Erzeugt den Demo-F20. Adressen entsprechen der ECU-Wissensbasis
    (src/f20/data/ecus.json); alle Inhalte sind FIKTIV."""
    vin = DEMO_VIN.encode()
    ecus = {
        0x40: VirtualEcu(0x40, "FEM_BODY", {
            0xF190: vin, 0xF150: bytes.fromhex("DE0040"),
            0xF18C: b"DEMO-FEM-0001",
            0xF101: _svk("HWEL_0000DE40_001_000_000", "BTLD_0000DE41_001_000_000",
                         "SWFL_0000DE42_001_000_000", "CAFD_0000DE43_001_000_000"),
        }, dtcs=[(0xDE0001, 0x28)]),
        0x60: VirtualEcu(0x60, "KOMBI", {
            0xF190: vin, 0xF150: bytes.fromhex("DE0060"), 0xF18C: b"DEMO-KOMBI-01",
            0xF101: _svk("HWEL_0000DE60_001_000_000", "SWFL_0000DE61_001_000_000",
                         "CAFD_0000DE62_001_000_000"),
        }),
        0x63: VirtualEcu(0x63, "HU_ENTRY", {
            0xF190: vin, 0xF150: bytes.fromhex("DE0063"), 0xF18C: b"DEMO-HU-00001",
            0xF101: _svk("HWEL_0000DE63_001_000_000", "BTLD_0000DE64_001_000_000",
                         "SWFL_0000DE65_001_000_000", "CAFD_000000F9_007_007_001"),
        }, slow_dids={0xF101}),
        0x72: VirtualEcu(0x72, "REM", {
            0xF190: vin, 0xF150: bytes.fromhex("DE0072"),
            0xF101: _svk("HWEL_0000DE72_001_000_000", "CAFD_0000DE73_001_000_000"),
        }),
        0x12: VirtualEcu(0x12, "DME", {
            0xF190: vin, 0xF150: bytes.fromhex("DE0012"),
            0xF101: _svk("HWEL_0000DE12_001_000_000", "SWFL_0000DE13_001_000_000",
                         "CAFD_0000DE14_001_000_000"),
        }, dtcs=[(0xDE0012, 0x24)]),
        0x10: VirtualEcu(0x10, "ZGW", {0xF190: vin, 0xF150: bytes.fromhex("DE0010")}),
        0x56: VirtualEcu(0x56, "FZD", {0xF150: bytes.fromhex("DE0056")}),
        0x67: VirtualEcu(0x67, "ZBE", {0xF150: bytes.fromhex("DE0067")}),
        0x30: VirtualEcu(0x30, "EPS", {0xF150: bytes.fromhex("DE0030")}),
        0x1C: VirtualEcu(0x1C, "ICM", {0xF150: bytes.fromhex("DE001C")}),
        0x29: VirtualEcu(0x29, "DSC", {0xF150: bytes.fromhex("DE0029")}),
        0x01: VirtualEcu(0x01, "ACSM", {0xF150: bytes.fromhex("DE0001")}),
        0x78: VirtualEcu(0x78, "IHKA", {0xF150: bytes.fromhex("DE0078")}),
    }
    return VirtualCar(ecus, VirtualEngine(seed), obd_dtcs={0x03: [], 0x07: [], 0x0A: []})
