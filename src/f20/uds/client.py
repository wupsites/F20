"""Read-only Diagnoseclient (UDS für BMW-ECUs + Standard-OBD-II).

Alle Methoden sind lesend. Es gibt keine Methode zum Schreiben, Löschen,
Zurücksetzen oder Codieren – und die darunterliegende Schicht
(:class:`~f20.transport.elm327.Elm327`) blockiert solche Dienste zusätzlich.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from ..obd.pids import PIDS, SUPPORT_PIDS, decode_obd_dtc_list, decode_pid, decode_supported
from ..transport.elm327 import Elm327
from ..transport.errors import AdapterError, NegativeResponse, NoData
from .dtc import decode_report_by_status
from .svk import decode_svk

#: Identifikations-DIDs (ISO 14229-1 Anhang C bzw. BMW-Nutzung).
#: Nachweis/Quellen: RESEARCH.md → Abschnitt „Identifikations-DIDs“.
IDENT_DIDS: dict[int, tuple[str, str]] = {
    0xF190: ("vin", "Fahrgestellnummer (VIN)"),
    0xF150: ("sgbd_index", "SGBD-Index / Variantenkennung (BMW)"),
    0xF101: ("svk", "Steuergeräte-Verbaukennung SVK (BMW)"),
    0xF18C: ("serial", "Seriennummer des Steuergeräts"),
    0xF18B: ("manufacturing_date", "Herstelldatum"),
    0xF186: ("active_session", "Aktive Diagnosesitzung"),
}


def _ascii(data: bytes) -> str:
    return data.decode("ascii", "replace").strip("\x00 ").strip()


@dataclass
class EcuIdentity:
    address: int
    name: str | None = None
    responded: bool = False
    fields: dict[str, dict] = field(default_factory=dict)
    errors: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "address": f"0x{self.address:02X}",
            "name": self.name,
            "responded": self.responded,
            "fields": self.fields,
            "errors": self.errors,
        }


@dataclass
class Reading:
    key: str
    name_de: str
    value: object
    unit: str
    source: str
    ts: float
    raw_hex: str

    def to_dict(self) -> dict:
        return dict(self.__dict__)


class DiagnosticClient:
    def __init__(self, elm: Elm327) -> None:
        self.elm = elm
        self.supported_pids: set[int] | None = None

    # ------------------------------------------------------------- UDS
    async def read_did(self, ecu: int, did: int) -> bytes:
        resp = await self.elm.uds_request(ecu, bytes([0x22, did >> 8, did & 0xFF]))
        return resp[3:]

    async def probe(self, ecu: int) -> bool:
        """Prüft, ob eine ECU antwortet (TesterPresent, Fallback DID 0xF190)."""
        try:
            await self.elm.uds_request(ecu, b"\x3E\x00")
            return True
        except NegativeResponse:
            return True   # Negativantwort = ECU vorhanden
        except AdapterError:
            pass
        try:
            await self.read_did(ecu, 0xF190)
            return True
        except NegativeResponse:
            return True
        except AdapterError:
            return False

    async def scan(self, addresses: list[int]) -> list[int]:
        found = []
        for a in addresses:
            if await self.probe(a):
                found.append(a)
        return found

    async def identify(self, ecu: int, name: str | None = None) -> EcuIdentity:
        ident = EcuIdentity(ecu, name)
        for did, (key, label) in IDENT_DIDS.items():
            try:
                data = await self.read_did(ecu, did)
                ident.responded = True
                entry = {"did": f"0x{did:04X}", "label_de": label, "raw_hex": data.hex().upper()}
                if key == "vin":
                    entry["value"] = _ascii(data)
                elif key == "svk":
                    try:
                        entry["value"] = decode_svk(data).to_dict()
                    except ValueError as exc:
                        entry["value"] = None
                        entry["decode_error"] = str(exc)
                elif key == "serial":
                    txt = _ascii(data)
                    entry["value"] = txt if txt.isprintable() and txt else data.hex().upper()
                elif key == "sgbd_index":
                    entry["value"] = data.hex().upper()
                elif key == "active_session":
                    entry["value"] = f"0x{data[0]:02X}" if data else None
                else:
                    entry["value"] = data.hex().upper()
                ident.fields[key] = entry
            except NegativeResponse as exc:
                ident.responded = True
                ident.errors[key] = str(exc)
            except NoData as exc:
                ident.errors[key] = str(exc)
            except AdapterError as exc:
                ident.errors[key] = f"{type(exc).__name__}: {exc}"
        return ident

    async def read_dtcs(self, ecu: int, status_mask: int = 0xFF) -> list[dict]:
        resp = await self.elm.uds_request(ecu, bytes([0x19, 0x02, status_mask]))
        _, dtcs = decode_report_by_status(ecu, resp)
        return [d.to_dict() for d in dtcs]

    # ------------------------------------------------------------- OBD
    async def obd_supported_pids(self) -> set[int]:
        supported: set[int] = set()
        for base in SUPPORT_PIDS:
            if base and base not in supported:
                break
            try:
                res = await self.elm.obd_request(bytes([0x01, base]))
            except NoData:
                break
            for payload in res.values():
                supported |= decode_supported(base, payload[2:6])
        self.supported_pids = supported
        return supported

    async def obd_read(self, pid: int) -> Reading | None:
        if self.supported_pids is not None and pid not in self.supported_pids:
            return None
        res = await self.elm.obd_request(bytes([0x01, pid]))
        cid = 0x7E8 if 0x7E8 in res else min(res)
        payload = res[cid]
        if len(payload) < 2 or payload[1] != pid:
            raise AdapterError("OBD-Antwort passt nicht zur PID")
        p = PIDS.get(pid)
        value = decode_pid(pid, payload[2:])
        return Reading(
            key=p.key if p else f"pid_{pid:02X}",
            name_de=p.name_de if p else f"PID 0x{pid:02X}",
            value=value,
            unit=p.unit if p else "",
            source=f"OBD 01/{pid:02X} @0x{cid:03X}",
            ts=time.time(),
            raw_hex=payload.hex().upper(),
        )

    async def obd_dtcs(self) -> dict[str, list[str]]:
        out: dict[str, list[str]] = {}
        for mode, key in ((0x03, "stored"), (0x07, "pending"), (0x0A, "permanent")):
            try:
                res = await self.elm.obd_request(bytes([mode]))
                codes: list[str] = []
                for payload in res.values():
                    codes += decode_obd_dtc_list(payload[1:])
                out[key] = codes
            except NoData:
                out[key] = []
            except AdapterError as exc:
                out[key] = [f"Fehler: {exc}"]
        return out

    async def obd_vin(self) -> str | None:
        try:
            res = await self.elm.obd_request(b"\x09\x02")
        except AdapterError:
            return None
        payload = res.get(0x7E8) or next(iter(res.values()))
        # 49 02 <count> <17 ASCII>
        return _ascii(payload[3:]) if len(payload) > 3 else None
