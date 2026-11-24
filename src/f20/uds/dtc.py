"""Dekodierung von UDS-Fehlerspeichereinträgen (Service 0x19)."""

from __future__ import annotations

from dataclasses import dataclass

#: ISO 14229-1 DTCStatusMask-Bits
STATUS_BITS = [
    (0x01, "testFailed", "Fehler aktuell vorhanden"),
    (0x02, "testFailedThisOperationCycle", "Im aktuellen Fahrzyklus aufgetreten"),
    (0x04, "pendingDTC", "Unbestätigt (pending)"),
    (0x08, "confirmedDTC", "Bestätigt / gespeichert"),
    (0x10, "testNotCompletedSinceLastClear", "Test seit Löschen nicht abgeschlossen"),
    (0x20, "testFailedSinceLastClear", "Seit Löschen mindestens einmal aufgetreten"),
    (0x40, "testNotCompletedThisOperationCycle", "Test in diesem Zyklus nicht abgeschlossen"),
    (0x80, "warningIndicatorRequested", "Warnleuchte angefordert"),
]


@dataclass
class UdsDtc:
    ecu: int
    code: int          # 3 Byte (BMW: "Fehlerort" als Hex, z. B. 0x801C20)
    status: int

    @property
    def code_hex(self) -> str:
        return f"{self.code:06X}"

    @property
    def active(self) -> bool:
        return bool(self.status & 0x01)

    @property
    def confirmed(self) -> bool:
        return bool(self.status & 0x08)

    def status_flags(self) -> list[dict]:
        return [{"bit": b, "name": n, "text_de": t} for b, n, t in STATUS_BITS if self.status & b]

    def to_dict(self) -> dict:
        return {
            "ecu": f"0x{self.ecu:02X}",
            "code": self.code_hex,
            "status": f"0x{self.status:02X}",
            "active": self.active,
            "confirmed": self.confirmed,
            "flags": self.status_flags(),
            # BMW-Fehlertexte sind nicht frei verfügbar; Code wird roh angezeigt.
            "text_de": None,
        }


def decode_report_by_status(ecu: int, resp: bytes) -> tuple[int, list[UdsDtc]]:
    """Antwort 59 02 <availMask> (<DTC_H DTC_M DTC_L STATUS>)* dekodieren."""
    if len(resp) < 3 or resp[0] != 0x59 or resp[1] not in (0x02, 0x0A):
        raise ValueError(f"Keine 0x19-02/0A-Antwort: {resp[:3].hex()}")
    avail = resp[2]
    body = resp[3:]
    if len(body) % 4:
        raise ValueError(f"DTC-Liste hat ungültige Länge {len(body)}")
    out = []
    for i in range(0, len(body), 4):
        code = int.from_bytes(body[i:i + 3], "big")
        out.append(UdsDtc(ecu, code, body[i + 3]))
    return avail, out
