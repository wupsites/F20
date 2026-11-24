"""Generische forensische Analyse unbekannter Backup-Dateien.

Das interne Format von BimmerCode-``.cod``-Dateien ist (Stand dieses Moduls)
nicht öffentlich dokumentiert. Statt ein Format zu *raten*, sammelt diese
Analyse überprüfbare Indizien:

* Containererkennung (ZIP, GZIP, ZLIB, Apple-Plist, JSON, XML, SQLite,
  Base64-/Hex-Text, LZFSE) inkl. rekursiver Analyse entpackter Inhalte
* Entropie gesamt und je Fenster (Kompression/Verschlüsselung erkennen)
* Druckbare Zeichenketten mit Offsets
* Muster: FIN/VIN, SGBM-IDs (CAFD_…), ECU-Namen, bekannte Kennungen
  (z. B. 0F1820) in ASCII und binär
* Strukturhypothesen (TLV mit DID-ähnlichen Tags 0x3000–0x3FFF,
  längenpräfixierte Datensätze)
* Dateinamen-Tokens

Jedes Ergebnis ist ein Indiz, kein Beweis – die Interpretation wird in
BACKUP_ANALYSIS.md mit Nachweisstatus dokumentiert.
"""

from __future__ import annotations

import base64
import binascii
import gzip
import io
import json
import math
import plistlib
import re
import sqlite3
import tempfile
import zipfile
import zlib
from collections import Counter
from pathlib import Path

from ..uds.svk import find_sgbm_strings
from .integrity import sha256_bytes

BMW_WMI = ("WBA", "WBS", "WBY", "WMW", "4US", "5UX", "5YM", "X4X", "WBX")
_VIN_RE = re.compile(r"(?:%s)[A-HJ-NPR-Z0-9]{14}" % "|".join(BMW_WMI))
_ANY_VIN_RE = re.compile(r"(?<![A-Z0-9])[A-HJ-NPR-Z0-9]{17}(?![A-Z0-9])")
_DATE_RE = re.compile(r"(20[0-3]\d)[-_.]?(0[1-9]|1[0-2])[-_.]?(0[1-9]|[12]\d|3[01])")
_HEX6_RE = re.compile(r"(?<![0-9A-Fa-f])[0-9A-Fa-f]{6}(?![0-9A-Fa-f])")

ECU_NAMES = (
    "FEM_BODY", "FEM_GW", "FEM", "BDC_BODY", "BDC", "REM", "KOMBI", "HU_ENTRY", "HU_NBT", "HU_CIC", "ENTRYNAV",
    "ENTRY_NAV", "ICM", "DSC", "DME", "DDE", "EPS", "ACSM", "IHKA", "IHKR", "FZD", "PDC", "PMA", "TRSVC", "KAFAS",
    "FLA", "ZBE", "TCB", "COMBOX", "ATM", "SAS", "EGS", "GWS", "AMP", "VDM", "SWW", "CAS", "FRM", "JBE", "ZGW",
    "FKA", "SMFA", "SMBF", "RDC", "TBX", "CON", "SZL", "EKPS", "LHM", "FLER", "FLEL", "TMS", "HKFM", "NIVI",
)
_ECU_RE = re.compile(r"(?<![A-Z0-9_])(%s)(?![A-Z0-9])" % "|".join(sorted(ECU_NAMES, key=len, reverse=True)))

MAGICS = [
    (b"PK\x03\x04", "zip"), (b"PK\x05\x06", "zip-empty"), (b"\x1f\x8b", "gzip"), (b"bplist00", "bplist"),
    (b"SQLite format 3\x00", "sqlite"), (b"bvx2", "lzfse"), (b"bvx1", "lzfse"), (b"bvxn", "lzvn"),
    (b"\x28\xb5\x2f\xfd", "zstd"), (b"BZh", "bzip2"), (b"\xfd7zXZ\x00", "xz"), (b"7z\xbc\xaf\x27\x1c", "7z"),
    (b"\x04\x22\x4d\x18", "lz4"), (b"Salted__", "openssl-enc"),
]


def entropy(data: bytes) -> float:
    if not data:
        return 0.0
    counts = Counter(data)
    n = len(data)
    return -sum(c / n * math.log2(c / n) for c in counts.values())


def windowed_entropy(data: bytes, window: int = 256) -> list[dict]:
    out = []
    for i in range(0, len(data), window):
        chunk = data[i:i + window]
        out.append({"offset": i, "entropy": round(entropy(chunk), 3), "zero_ratio": round(chunk.count(0) / max(1, len(chunk)), 3)})
    return out


def printable_strings(data: bytes, min_len: int = 4, limit: int = 2000) -> list[dict]:
    out = []
    for m in re.finditer(rb"[\x20-\x7e]{%d,}" % min_len, data):
        out.append({"offset": m.start(), "text": m.group().decode("ascii")})
        if len(out) >= limit:
            break
    # UTF-16LE-Strings
    for m in re.finditer(rb"(?:[\x20-\x7e]\x00){%d,}" % min_len, data):
        out.append({"offset": m.start(), "text": m.group().decode("utf-16le"), "encoding": "utf-16le"})
        if len(out) >= limit * 2:
            break
    return out


def parse_filename(name: str) -> dict:
    stem = Path(name).stem
    tokens = [t for t in re.split(r"[_\-\s.()\[\]]+", stem) if t]
    vins = [t for t in tokens if _VIN_RE.fullmatch(t.upper())]
    dates = ["-".join(m.groups()) for m in _DATE_RE.finditer(stem)]
    hex6 = [t.upper() for t in tokens if re.fullmatch(r"[0-9A-Fa-f]{6}", t) and not t.isdigit()]
    hex6 += [t for t in tokens if re.fullmatch(r"0[0-9A-F]{5}", t.upper()) and t.isdigit()]
    ecus = [t.upper() for t in tokens if t.upper() in ECU_NAMES]
    short_vin = [t.upper() for t in tokens if re.fullmatch(r"[A-Z]{2}\d{5}", t.upper())]
    return {"stem": stem, "tokens": tokens, "vins": vins, "short_vin_candidates": short_vin,
            "dates": dates, "hex6_ids": sorted(set(hex6)), "ecu_names": ecus,
            "sgbm": [str(s) for s in find_sgbm_strings(stem)]}


def _find_all(data: bytes, needle: bytes, limit: int = 50) -> list[int]:
    out, start = [], 0
    while len(out) < limit:
        i = data.find(needle, start)
        if i < 0:
            break
        out.append(i)
        start = i + 1
    return out


def find_known_ids(data: bytes, ids: list[str]) -> dict:
    res = {}
    for ident in ids:
        ident = ident.strip().upper()
        if not ident:
            continue
        entry = {"ascii": _find_all(data, ident.encode()), "ascii_lower": _find_all(data, ident.lower().encode())}
        if re.fullmatch(r"[0-9A-F]+", ident) and len(ident) % 2 == 0:
            entry["binary"] = _find_all(data, bytes.fromhex(ident))
        res[ident] = entry
    return res


def tlv_hypotheses(data: bytes) -> list[dict]:
    """Sucht nach Sequenzen <Tag 0x3000–0x3FFF><Länge u16 BE/LE><Daten>, die sich verketten."""
    hyps = []
    for endian in ("big", "little"):
        for start in range(0, min(len(data), 64)):
            i, chain = start, []
            while i + 4 <= len(data):
                tag = int.from_bytes(data[i:i + 2], "big")
                ln = int.from_bytes(data[i + 2:i + 4], endian)
                if not (0x3000 <= tag <= 0x3FFF) or ln == 0 or i + 4 + ln > len(data):
                    break
                chain.append({"offset": i, "tag": f"0x{tag:04X}", "length": ln})
                i += 4 + ln
            if len(chain) >= 3:
                hyps.append({"kind": f"TLV tag16/len16-{endian}", "start": start, "records": len(chain),
                             "covers_bytes": i - start, "first": chain[:8]})
    hyps.sort(key=lambda h: -h["covers_bytes"])
    return hyps[:5]


def length_prefixed_hypotheses(data: bytes) -> list[dict]:
    hyps = []
    for width, endian in ((1, "big"), (2, "big"), (2, "little"), (4, "big"), (4, "little")):
        for start in range(0, min(len(data), 32)):
            i, n, sizes = start, 0, []
            while i + width <= len(data):
                ln = int.from_bytes(data[i:i + width], endian)
                if ln == 0 or i + width + ln > len(data):
                    break
                sizes.append(ln)
                i += width + ln
                n += 1
            if n >= 3 and i == len(data):
                hyps.append({"kind": f"len{width * 8}-{endian}", "start": start, "records": n,
                             "sizes": sizes[:16]})
    return hyps[:5]


def detect_container(data: bytes) -> str | None:
    for magic, kind in MAGICS:
        if data.startswith(magic):
            return kind
    if len(data) >= 2 and data[0] == 0x78 and ((data[0] << 8) | data[1]) % 31 == 0:
        return "zlib"
    head = data[:64].lstrip()
    if head.startswith(b"<?xml") or head.startswith(b"<plist"):
        return "xml-plist" if b"<plist" in data[:512] else "xml"
    if head[:1] in (b"{", b"["):
        try:
            json.loads(data.decode("utf-8"))
            return "json"
        except (UnicodeDecodeError, ValueError):
            pass
    txt = data.strip()
    if txt and len(txt) >= 16 and re.fullmatch(rb"[0-9A-Fa-f\s]+", txt) and len(re.sub(rb"\s", b"", txt)) % 2 == 0:
        return "hex-text"
    if txt and len(txt) >= 16 and re.fullmatch(rb"[A-Za-z0-9+/=\r\n]+", txt) and len(re.sub(rb"\s", b"", txt)) % 4 == 0:
        try:
            base64.b64decode(txt, validate=False)
            return "base64-text"
        except (binascii.Error, ValueError):
            pass
    return None


def _unpack(kind: str, data: bytes) -> list[tuple[str, bytes]] | dict | None:
    try:
        if kind == "zip":
            with zipfile.ZipFile(io.BytesIO(data)) as zf:
                return [(i.filename, zf.read(i)) for i in zf.infolist()[:200] if not i.is_dir()]
        if kind == "gzip":
            return [("gunzip", gzip.decompress(data))]
        if kind == "zlib":
            return [("inflate", zlib.decompress(data))]
        if kind == "hex-text":
            return [("hex-decoded", bytes.fromhex(re.sub(r"\s", "", data.decode())))]
        if kind == "base64-text":
            return [("base64-decoded", base64.b64decode(data))]
        if kind in ("bplist", "xml-plist"):
            return {"plist": _jsonable(plistlib.loads(data))}
        if kind == "json":
            return {"json": json.loads(data.decode("utf-8"))}
        if kind == "sqlite":
            return {"sqlite": _sqlite_summary(data)}
    except Exception as exc:  # noqa: BLE001 - forensisch: Fehler dokumentieren statt abbrechen
        return {"error": f"{type(exc).__name__}: {exc}"}
    return None


def _jsonable(obj):
    if isinstance(obj, dict):
        return {str(k): _jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_jsonable(v) for v in obj]
    if isinstance(obj, bytes):
        return {"__bytes__": obj[:256].hex().upper(), "len": len(obj)}
    if hasattr(obj, "isoformat"):
        return obj.isoformat()
    return obj


def _sqlite_summary(data: bytes) -> dict:
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "copy.sqlite"
        p.write_bytes(data)
        conn = sqlite3.connect(f"file:{p}?mode=ro&immutable=1", uri=True)
        try:
            tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")]
            out = {}
            for t in tables[:50]:
                cols = [r[1] for r in conn.execute(f'PRAGMA table_info("{t}")')]
                cnt = conn.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
                out[t] = {"columns": cols, "rows": cnt}
            return out
        finally:
            conn.close()


def analyze_bytes(data: bytes, filename: str = "", known_ids: list[str] | None = None, depth: int = 0) -> dict:
    known_ids = known_ids or []
    strings = printable_strings(data)
    text_blob = "\n".join(s["text"] for s in strings).upper()
    container = detect_container(data)
    report: dict = {
        "filename": filename,
        "size": len(data),
        "sha256": sha256_bytes(data),
        "head_hex": data[:64].hex(" ").upper(),
        "container": container,
        "entropy_total": round(entropy(data), 4),
        "entropy_windows": windowed_entropy(data) if len(data) <= 1 << 20 else [],
        "strings_count": len(strings),
        "strings": strings[:300],
        "patterns": {
            "bmw_vins": sorted(set(_VIN_RE.findall(text_blob))),
            "vin_like": sorted(set(_ANY_VIN_RE.findall(text_blob)) - set(_VIN_RE.findall(text_blob)))[:20],
            "sgbm_ids": sorted({str(s) for s in find_sgbm_strings(text_blob)}),
            "ecu_names": sorted(set(_ECU_RE.findall(text_blob))),
            "dates": sorted({"-".join(m.groups()) for m in _DATE_RE.finditer(text_blob)})[:30],
            "known_ids": find_known_ids(data, known_ids),
        },
        "hypotheses": {
            "tlv": tlv_hypotheses(data) if len(data) <= 1 << 20 else [],
            "length_prefixed": length_prefixed_hypotheses(data) if len(data) <= 1 << 20 else [],
        },
        "byte_histogram_top": [{"byte": f"0x{b:02X}", "count": c} for b, c in Counter(data).most_common(8)],
        "nested": [],
        "assessment": [],
    }
    if filename:
        report["filename_info"] = parse_filename(filename)
    if container and depth < 3:
        unpacked = _unpack(container, data)
        if isinstance(unpacked, list):
            for name, child in unpacked:
                report["nested"].append(analyze_bytes(child, name, known_ids, depth + 1))
        elif isinstance(unpacked, dict):
            report["decoded"] = unpacked
    report["assessment"] = assess(report)
    return report


def assess(r: dict) -> list[str]:
    a = []
    if r["container"]:
        a.append(f"Container erkannt: {r['container']}.")
    elif r["entropy_total"] > 7.5 and r["size"] > 512:
        a.append("Sehr hohe Entropie ohne bekannte Signatur → vermutlich komprimiert oder verschlüsselt.")
    elif r["entropy_total"] < 5.0:
        a.append("Niedrige Entropie → unkomprimierte Binär- oder Textdaten wahrscheinlich.")
    p = r["patterns"]
    if p["bmw_vins"]:
        a.append(f"{len(p['bmw_vins'])} BMW-FIN(s) im Inhalt gefunden → Fahrzeugzuordnung möglich.")
    if p["sgbm_ids"]:
        a.append(f"SGBM-IDs im Klartext: {', '.join(p['sgbm_ids'][:5])}.")
    if p["ecu_names"]:
        a.append(f"Steuergerätenamen im Klartext: {', '.join(p['ecu_names'][:8])}.")
    for ident, hits in p["known_ids"].items():
        n = sum(len(v) for v in hits.values())
        if n:
            a.append(f"Kennung {ident} kommt {n}× vor (ASCII/binär).")
    if r["hypotheses"]["tlv"]:
        h = r["hypotheses"]["tlv"][0]
        a.append(f"TLV-Hypothese ({h['kind']}): {h['records']} Datensätze mit DID-ähnlichen Tags ab Offset {h['start']}.")
    return a
