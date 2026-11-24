"""Dekodierung der BMW-Steuergeräte-Verbaukennung (SVK, DID 0xF101).

SGBM-ID (Steuergeräte-Basismodul-ID): 8 Byte
    1 Byte Prozessklasse | 4 Byte ID | 3 Byte Version (Haupt, Neben, Patch)
Beispiel: 05 000000F9 07 07 01  →  CAFD_000000F9_007_007_001

Nachweisstatus der Struktur: siehe RESEARCH.md (Abschnitt SVK). Der Kopf der
SVK wird heuristisch bestimmt und als solcher gekennzeichnet, bis er an
echten Antworten des eigenen Fahrzeugs verifiziert ist.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

#: Prozessklassen laut SGBD-Tabelle PROZESSKLASSEN (FEM_20), Quelle:
#: https://emdzej.github.io/ediabasx-docs-sgbd/sgbd/fem_20/ – siehe RESEARCH.md §SVK.
PROCESS_CLASSES: dict[int, tuple[str, str, str]] = {
    0x01: ("HWEL", "Hardware Elektronik", "documented"),
    0x02: ("HWAP", "Hardwareausprägung", "documented"),
    0x03: ("HWFR", "Hardwarefarbe", "documented"),
    0x04: ("GWTB", "Gateway-Tabelle", "documented"),
    0x05: ("CAFD", "Codierdaten", "documented"),
    0x06: ("BTLD", "Bootloader", "documented"),
    0x07: ("FLSL", "Flashloader Slave", "documented"),
    0x08: ("SWFL", "Software", "documented"),
    0x09: ("SWFF", "Flash File Software", "documented"),
    0x0A: ("SWPF", "Prüfsoftware", "documented"),
    0x0B: ("ONPS", "Onboard-Programmiersystem", "documented"),
    0x0C: ("IBAD", "Interaktive Betriebsanleitung Daten", "documented"),
    0x0D: ("SWFK", "BEGU: Detaillierung auf SWE-Ebene", "documented"),
    0x0F: ("FAFP", "FA2FP", "documented"),
    0x10: ("FCFA", "Freischaltcode Fahrzeugauftrag", "documented"),
    0x1A: ("TLRT", "Temporäre Löschroutine", "documented"),
    0x1B: ("TPRG", "Temporäre Programmierroutine", "documented"),
    0x1C: ("BLUP", "Bootloader-Update", "documented"),
    0x1D: ("FLUP", "Flashloader-Update", "documented"),
    0xA0: ("ENTD", "Entertainment-Daten", "documented"),
    0xA1: ("NAVD", "Navigationsdaten", "documented"),
    0xA2: ("FCFN", "Freischaltcode Funktion", "documented"),
    0xC0: ("SWUP", "Software-Update-Paket", "documented"),
    0xC1: ("SWIP", "Index Software-Update-Paket", "documented"),
}

#: Kopflänge der SVK: 4 Byte (Version, PROG_TEST, Anzahl) + 13 Byte Kopfblock.
#: Abgeleitet aus realen Antworten (EdiabasLib-Trace, G31) – für F20 zu bestätigen.
SVK_HEADER_LEN = 17

_SGBM_RE = re.compile(
    r"(?P<pc>[A-Z]{4})[_ ]?(?P<id>[0-9A-Fa-f]{8})[_ ]?(?P<maj>\d{1,3})[_ .](?P<min>\d{1,3})[_ .](?P<pat>\d{1,3})"
)


@dataclass(frozen=True)
class SgbmId:
    process_class: int
    ident: int
    major: int
    minor: int
    patch: int

    @property
    def pc_name(self) -> str:
        return PROCESS_CLASSES.get(self.process_class, (f"PC{self.process_class:02X}",))[0]

    def __str__(self) -> str:
        return f"{self.pc_name}_{self.ident:08X}_{self.major:03d}_{self.minor:03d}_{self.patch:03d}"

    @classmethod
    def from_bytes(cls, b: bytes) -> "SgbmId":
        if len(b) != 8:
            raise ValueError("SGBM-ID muss 8 Byte lang sein")
        return cls(b[0], int.from_bytes(b[1:5], "big"), b[5], b[6], b[7])

    def to_bytes(self) -> bytes:
        return bytes([self.process_class]) + self.ident.to_bytes(4, "big") + bytes([self.major, self.minor, self.patch])

    @classmethod
    def parse(cls, text: str) -> "SgbmId":
        m = _SGBM_RE.search(text.upper())
        if not m:
            raise ValueError(f"Keine SGBM-ID erkannt: {text!r}")
        pc_name = m.group("pc")
        pc = next((k for k, v in PROCESS_CLASSES.items() if v[0] == pc_name), None)
        if pc is None:
            raise ValueError(f"Unbekannte Prozessklasse {pc_name}")
        return cls(pc, int(m.group("id"), 16), int(m.group("maj")), int(m.group("min")), int(m.group("pat")))

    def to_dict(self) -> dict:
        name = PROCESS_CLASSES.get(self.process_class)
        return {
            "sgbm": str(self),
            "process_class": self.pc_name,
            "process_class_de": name[1] if name else "unbekannt",
            "id": f"{self.ident:08X}",
            "version": f"{self.major:03d}.{self.minor:03d}.{self.patch:03d}",
        }


def find_sgbm_strings(text: str) -> list[SgbmId]:
    out = []
    for m in _SGBM_RE.finditer(text.upper()):
        try:
            out.append(SgbmId.parse(m.group(0)))
        except ValueError:
            continue
    return out


@dataclass
class SvkResult:
    entries: list[SgbmId]
    header_hex: str
    trailer_hex: str
    heuristic: bool
    prog_test: int | None = None
    prog_date: str | None = None
    prog_km: int | None = None

    def to_dict(self) -> dict:
        return {
            "entries": [e.to_dict() for e in self.entries],
            "header_hex": self.header_hex,
            "trailer_hex": self.trailer_hex,
            "heuristic": self.heuristic,
            "prog_test": self.prog_test,
            "prog_test_ok": None if self.prog_test is None else self.prog_test == 1,
            "prog_date": self.prog_date,
            "prog_km": self.prog_km,
            "prog_fields_evidence": "likely",
            "cafd": [str(e) for e in self.entries if e.process_class == 0x05],
        }


def _bcd_date(b: bytes) -> str | None:
    try:
        yy, mm, dd = (int(f"{x:02X}") for x in b[:3])
    except ValueError:
        return None
    if not (1 <= mm <= 12 and 1 <= dd <= 31):
        return None
    return f"20{yy:02d}-{mm:02d}-{dd:02d}"


def decode_svk(data: bytes) -> SvkResult:
    """Dekodiert die Nutzdaten von DID 0xF101 (ohne 62 F1 01).

    Layout (RESEARCH.md §SVK): [0] SVK-Version, [1] PROG_TEST (1 = IO),
    [2..3] Anzahl n, [4..16] Kopfblock (PROG_DATUM BCD YYMMDD an [4..6],
    PROG_KM/10 an [8..9] – Positionen wahrscheinlich), ab [17] n × 8 Byte SGBM-IDs.
    Weicht eine Antwort ab, wird heuristisch nach dem Eintragsbeginn gesucht.
    """
    if len(data) < 12:
        raise ValueError("SVK zu kurz")
    count = int.from_bytes(data[2:4], "big")
    for header in (SVK_HEADER_LEN, 4, 7, 8, 10, 11, 12, 13, 16):
        end = header + count * 8
        if count == 0 or end > len(data):
            continue
        entries = [SgbmId.from_bytes(data[i:i + 8]) for i in range(header, end, 8)]
        if all(e.process_class in PROCESS_CLASSES for e in entries):
            res = SvkResult(entries, data[:header].hex().upper(), data[end:].hex().upper(),
                            heuristic=header != SVK_HEADER_LEN, prog_test=data[1])
            if header == SVK_HEADER_LEN:
                res.prog_date = _bcd_date(data[4:7])
                res.prog_km = int.from_bytes(data[8:10], "big") * 10
            return res
    # Fallback: alle 8-Byte-Fenster mit bekannter Prozessklasse durchsuchen
    entries = []
    i = 4
    while i + 8 <= len(data):
        e = SgbmId.from_bytes(data[i:i + 8])
        if e.process_class in PROCESS_CLASSES and e.major < 0x100:
            entries.append(e)
            i += 8
        else:
            i += 1
    return SvkResult(entries, data[:4].hex().upper(), "", heuristic=True)
