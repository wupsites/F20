"""Parameterzuordnungen für Codierdaten (Position → Bedeutung).

Quellen, nach Vertrauen geordnet:
1. **Gelernt** – aus eigenen Vorher/Nachher-Backups (Lernmodus). Rechtlich
   unbedenklich: eigene Fahrzeugdaten, eigene Beobachtung.
2. **Importiert** – Namenstabellen im OpenCAFDMap-TSV-Format, die der Nutzer
   selbst bereitstellt. Dieses Projekt liefert KEINE BMW-Originalnamen mit;
   die Rechtslage solcher Dateien muss der Nutzer selbst beurteilen
   (siehe RESEARCH.md, Abschnitt „Rechtslage Parameterzuordnungen“).

TSV-Format (OpenCAFDMap CONTRIBUTING.md, geprüft 2026-11-24):
    cafd_id  address  start  end  mask  value_hex  name  comment
    mask binär mit Suffix „b“ (z. B. 11111111b), start/end = Byte-Index im Datenblock.
"""

from __future__ import annotations

import csv
import gzip
import io
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Function:
    cafd_id: str
    address: str
    start: int
    end: int
    mask: int
    name: str
    comment: str = ""
    source: str = ""
    values: dict[str, str] = field(default_factory=dict)  # value_hex → Bezeichnung

    def extract(self, block: bytes) -> str | None:
        """Liest den Rohwert (Hex) dieser Funktion aus einem Datenblock."""
        if self.end >= len(block) or self.start > self.end:
            return None
        raw = bytearray(block[self.start:self.end + 1])
        if self.start == self.end:
            v = raw[0] & self.mask
            # Wert auf niederwertigstes Bit der Maske verschieben
            shift = (self.mask & -self.mask).bit_length() - 1 if self.mask else 0
            return f"{v >> shift:02X}"
        if self.mask != 0xFF:
            raw = bytearray(b & self.mask for b in raw)
        return raw.hex().upper()

    def label(self, value_hex: str | None) -> str | None:
        if value_hex is None:
            return None
        return self.values.get(value_hex.upper())


def _parse_mask(s: str) -> int:
    s = s.strip()
    if not s:
        return 0xFF
    if s.lower().endswith("b"):
        return int(s[:-1], 2)
    if s.lower().startswith("0x"):
        return int(s, 16)
    return int(s)


def load_tsv(path: Path | str, source: str | None = None) -> list[Function]:
    p = Path(path)
    raw = p.read_bytes()
    if p.suffix == ".gz":
        raw = gzip.decompress(raw)
    text = raw.decode("utf-8-sig")
    funcs: dict[tuple, Function] = {}
    reader = csv.reader(io.StringIO(text), delimiter="\t")
    for row in reader:
        if not row or row[0].startswith("#") or row[0].strip().lower() == "cafd_id":
            continue
        row = row + [""] * (8 - len(row))
        cafd_id, address, start, end, mask, value_hex, name, comment = (c.strip() for c in row[:8])
        if not start or not end:
            continue  # Gruppenzeile
        try:
            key = (cafd_id.upper(), address.upper(), int(start), int(end), _parse_mask(mask))
        except ValueError:
            continue
        f = funcs.get(key)
        if f is None:
            f = Function(key[0], key[1], key[2], key[3], key[4], name if not value_hex else "",
                         comment if not value_hex else "", source or p.name)
            funcs[key] = f
        if value_hex:
            f.values[value_hex.upper().zfill(2)] = name
        elif name:
            f.name = name
            f.comment = comment
    return list(funcs.values())


def decode_blocks(blocks: dict[str, bytes], cafd_id: str, functions: list[Function]) -> list[dict]:
    out = []
    for f in functions:
        if f.cafd_id != cafd_id.upper():
            continue
        block = blocks.get(f.address)
        if block is None:
            continue
        v = f.extract(block)
        out.append({
            "address": f.address, "start": f.start, "end": f.end, "mask": f"{f.mask:08b}b",
            "name": f.name or "(unbenannt)", "value_hex": v, "value_label": f.label(v),
            "alternatives": [{"hex": k, "label": lbl} for k, lbl in sorted(f.values.items())],
            "comment": f.comment, "source": f.source,
        })
    return out


def learned_functions(observations: list[dict]) -> list[Function]:
    """Wandelt gespeicherte Lernmodus-Beobachtungen in Funktionen um."""
    funcs: dict[tuple, Function] = {}
    for o in observations:
        # scope = "<SG-Kennung>|<CAFD-ID>|<Version>#<Datenblock>"
        scope, _, block = (o.get("scope") or "").partition("#")
        parts = scope.split("|")
        cafd_id = parts[1] if len(parts) > 1 else ""
        key = (cafd_id, block, o["byte_offset"], o["mask"])
        f = funcs.get(key)
        if f is None:
            f = Function(cafd_id, block, o["byte_offset"], o["byte_offset"], o["mask"], o["label"],
                         "gelernt aus eigenem Backup-Vergleich", "Lernmodus")
            funcs[key] = f
        shift = (o["mask"] & -o["mask"]).bit_length() - 1 if o["mask"] else 0
        f.values.setdefault(f"{(o['before'] & o['mask']) >> shift:02X}", "vorher")
        f.values[f"{(o['after'] & o['mask']) >> shift:02X}"] = f"nachher ({o['label']})"
    return list(funcs.values())
