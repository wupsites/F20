"""ISO-TP (ISO 15765-2) Hilfsfunktionen für ELM327-Rohausgaben.

BMW F-Serie verwendet auf D-CAN *Extended Addressing*: Das erste Datenbyte
jedes CAN-Frames ist die Zieladresse (Tester → ECU: ECU-Adresse,
ECU → Tester: 0xF1). Danach folgt das normale ISO-TP-PCI-Byte.
Siehe docs/research/raw/01_architektur_protokoll.md.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

TESTER_ADDRESS = 0xF1

_HEX_LINE = re.compile(r"^[0-9A-F]+$")


@dataclass(frozen=True)
class CanFrame:
    can_id: int
    data: bytes

    def __str__(self) -> str:  # pragma: no cover - Debug-Hilfe
        return f"{self.can_id:03X} {self.data.hex(' ').upper()}"


def parse_elm_frame_line(line: str, header_bits: int = 11) -> CanFrame | None:
    """Parst eine ELM327-Ausgabezeile mit Headern (ATH1).

    Unterstützt Ausgaben mit und ohne Leerzeichen (ATS1/ATS0). Gibt None
    für Zeilen zurück, die keine Frames sind.
    """
    compact = line.replace(" ", "").strip().upper()
    if not compact or not _HEX_LINE.match(compact):
        return None
    hlen = 3 if header_bits == 11 else 8
    if len(compact) <= hlen or (len(compact) - hlen) % 2 != 0:
        return None
    can_id = int(compact[:hlen], 16)
    data = bytes.fromhex(compact[hlen:])
    if len(data) > 8:
        return None
    return CanFrame(can_id, data)


class IsoTpError(ValueError):
    pass


@dataclass
class _Assembly:
    expected: int
    buf: bytearray
    next_seq: int


def reassemble(frames: list[CanFrame], response_id: int, extended: bool,
               ext_address: int = TESTER_ADDRESS) -> list[bytes]:
    """Setzt ISO-TP-Nachrichten einer Antwort-CAN-ID zusammen.

    Gibt alle vollständigen Nachrichten (Payloads ohne PCI) in Reihenfolge zurück.
    ``extended``: Erstes Datenbyte ist Extended Address. Ist das erste Byte
    gleich ``ext_address`` (0xF1), wird es entfernt. Da ein gültiges PCI-Byte
    nie mit 0xF beginnt, ist diese Erkennung eindeutig – deshalb werden auch
    Adapter unterstützt, die das Adressbyte bereits selbst entfernen.
    """
    messages: list[bytes] = []
    cur: _Assembly | None = None
    for fr in frames:
        if fr.can_id != response_id:
            continue
        data = fr.data
        if extended and data and data[0] == ext_address:
            data = data[1:]
        if not data:
            continue
        pci_type = data[0] >> 4
        if pci_type == 0x0:  # Single Frame
            length = data[0] & 0x0F
            if length == 0 or length > len(data) - 1:
                raise IsoTpError(f"Ungültiger Single Frame: {data.hex()}")
            messages.append(bytes(data[1:1 + length]))
            cur = None
        elif pci_type == 0x1:  # First Frame
            if len(data) < 2:
                raise IsoTpError("First Frame zu kurz")
            length = ((data[0] & 0x0F) << 8) | data[1]
            cur = _Assembly(length, bytearray(data[2:]), 1)
        elif pci_type == 0x2:  # Consecutive Frame
            if cur is None:
                raise IsoTpError("Consecutive Frame ohne First Frame")
            seq = data[0] & 0x0F
            if seq != cur.next_seq:
                raise IsoTpError(f"Sequenzfehler: erwartet {cur.next_seq}, erhalten {seq}")
            cur.buf.extend(data[1:])
            cur.next_seq = (cur.next_seq + 1) & 0x0F
        elif pci_type == 0x3:  # Flow Control (Echo eigener FC-Frames) – ignorieren
            continue
        else:
            raise IsoTpError(f"Unbekannter PCI-Typ {pci_type:#x}")
        if cur is not None and len(cur.buf) >= cur.expected:
            messages.append(bytes(cur.buf[:cur.expected]))
            cur = None
    if cur is not None:
        raise IsoTpError(
            f"Unvollständige Multi-Frame-Antwort: {len(cur.buf)}/{cur.expected} Byte "
            "(Flow Control vom Adapter nicht korrekt?)"
        )
    return messages


def segment(payload: bytes, ext_address: int | None) -> list[bytes]:
    """Zerlegt eine Nachricht in ISO-TP-Frames (für den Simulator).

    Mit ``ext_address`` wird das Adressbyte vorangestellt (BMW-Stil).
    """
    prefix = bytes([ext_address]) if ext_address is not None else b""
    room = 8 - len(prefix)
    if len(payload) <= room - 1:
        return [prefix + bytes([len(payload)]) + payload]
    frames = []
    first_room = room - 2
    frames.append(prefix + bytes([0x10 | ((len(payload) >> 8) & 0x0F), len(payload) & 0xFF])
                  + payload[:first_room])
    rest = payload[first_room:]
    seq = 1
    while rest:
        chunk, rest = rest[:room - 1], rest[room - 1:]
        frames.append(prefix + bytes([0x20 | seq]) + chunk)
        seq = (seq + 1) & 0x0F
    return frames
