"""Parser für BimmerCode-Backups.

iOS (``.cod``): Binäre Apple-Property-List (``bplist00``) im
NSKeyedArchiver-Format. Struktur laut Quellcode des MIT-lizenzierten
Projekts OpenCAFDMap (``ocm/cod_import.py``, ``ocm/bc_tool.py``,
https://github.com/shamair28/OpenCAFDMap, geprüft am 2026-11-24):

    root (CodingSession)
      VIN                       → FIN (17 Zeichen)
      codingECU
        identifier              → BimmerCode-Steuergerätekennung, z. B. "0F1820"
        address                 → Diagnoseadresse (int, z. B. 0x63)
        identifiers.CAFD        → Liste {identifier, mainVersion, subVersion, patchVersion}
      codingData
        CAFDIdentifier          → 14 Hex-Zeichen: 8 CAFD-ID + 3×2 Version (Haupt/Neben/Patch)
        mutableCodingDataBlocks → Liste {blockAddress (int, z. B. 0x3000), data (bytes)}

Dateiname iOS: ``<identifier>-<FIN>-<Unix-Zeit>[-<tag>].cod``
Android (``.dat``): Java-Serialisierung (``AC ED 00 05``) – wird erkannt,
aber in v0.1 noch nicht dekodiert (siehe KNOWN_LIMITATIONS.md).

Dieser Parser ist eine eigenständige Neuimplementierung, liest nur und
verändert niemals Dateien. Er löst das NSKeyedArchiver-Objektgeflecht
generisch auf, damit auch bisher unbekannte Felder sichtbar werden.
"""

from __future__ import annotations

import datetime as _dt
import plistlib
import re
from dataclasses import dataclass, field
from typing import Any

FN_RE = re.compile(r"^(?P<ecu>[0-9A-F]+)-(?P<vin>[A-Z0-9]{17})-(?P<ts>\d{9,})(?:-(?P<tag>[^.]*))?\.cod$", re.I)
ANDROID_FN_RE = re.compile(r"^(?P<vin>[A-Z0-9]{17})_(?P<ecu>[A-Z0-9_]+)\.dat$", re.I)
JAVA_SERIAL_MAGIC = b"\xac\xed\x00\x05"


class CodFormatError(ValueError):
    pass


@dataclass
class CodBackup:
    platform: str
    vin: str | None
    ecu_identifier: str | None
    diag_address: int | None
    cafd_id: str | None
    cafd_version: str | None
    cafds: list[tuple[str, str]]
    blocks: dict[str, bytes]
    filename_ts: int | None = None
    filename_tag: str | None = None
    root_keys: list[str] = field(default_factory=list)
    extra: dict[str, Any] = field(default_factory=dict)
    classes: list[str] = field(default_factory=list)

    @property
    def created_at_iso(self) -> str | None:
        if not self.filename_ts:
            return None
        return _dt.datetime.fromtimestamp(self.filename_ts, _dt.timezone.utc).isoformat()

    @property
    def sgbm(self) -> str | None:
        if not self.cafd_id or not self.cafd_version:
            return None
        return f"CAFD_{self.cafd_id}_{self.cafd_version}"

    @property
    def scope_key(self) -> str:
        """Schlüssel für vergleichbare Backups (gleiches SG, gleiche CAFD-Version)."""
        return f"{self.ecu_identifier}|{self.cafd_id}|{self.cafd_version}"

    def to_dict(self, include_blocks: bool = False) -> dict:
        d = {
            "platform": self.platform,
            "vin": self.vin,
            "ecu_identifier": self.ecu_identifier,
            "diag_address": None if self.diag_address is None else f"0x{self.diag_address:02X}",
            "cafd_id": self.cafd_id,
            "cafd_version": self.cafd_version,
            "sgbm": self.sgbm,
            "cafds": [{"id": c, "version": v} for c, v in self.cafds],
            "created_at": self.created_at_iso,
            "filename_ts": self.filename_ts,
            "filename_tag": self.filename_tag,
            "block_count": len(self.blocks),
            "blocks": {k: {"length": len(v), **({"hex": v.hex().upper()} if include_blocks else {})}
                       for k, v in sorted(self.blocks.items())},
            "root_keys": self.root_keys,
            "classes": self.classes,
            "extra": self.extra,
        }
        return d


# ------------------------------------------------------------ NSKeyedArchiver
def _is_uid(x: Any) -> bool:
    return isinstance(x, plistlib.UID)


def unarchive(plist: dict, max_depth: int = 40) -> Any:
    """Löst ein NSKeyedArchiver-Plist in einfache Python-Strukturen auf."""
    if plist.get("$archiver") != "NSKeyedArchiver" or "$objects" not in plist:
        raise CodFormatError("Kein NSKeyedArchiver-Plist")
    objs = plist["$objects"]

    def classname(obj: dict) -> str | None:
        c = obj.get("$class")
        if _is_uid(c):
            cdef = objs[c.data]
            if isinstance(cdef, dict):
                return cdef.get("$classname")
        return None

    def res(x: Any, depth: int, seen: frozenset) -> Any:
        if depth > max_depth:
            return "<max depth>"
        if _is_uid(x):
            if x.data in seen:
                return f"<ref {x.data}>"
            return res(objs[x.data], depth + 1, seen | {x.data})
        if isinstance(x, str) and x == "$null":
            return None
        if isinstance(x, dict):
            cn = classname(x)
            if "NS.keys" in x and "NS.objects" in x:
                keys = [res(k, depth + 1, seen) for k in x["NS.keys"]]
                vals = [res(v, depth + 1, seen) for v in x["NS.objects"]]
                return {str(k): v for k, v in zip(keys, vals)}
            if "NS.objects" in x:
                return [res(v, depth + 1, seen) for v in x["NS.objects"]]
            if "NS.string" in x:
                return x["NS.string"]
            if "NS.bytes" in x or "NS.data" in x:
                return x.get("NS.bytes", x.get("NS.data"))
            if "NS.time" in x:
                # NSDate: Sekunden seit 2001-01-01 UTC
                return (_dt.datetime(2001, 1, 1, tzinfo=_dt.timezone.utc)
                        + _dt.timedelta(seconds=float(x["NS.time"]))).isoformat()
            out = {k: res(v, depth + 1, seen) for k, v in x.items() if k != "$class"}
            if cn:
                out["$classname"] = cn
            return out
        if isinstance(x, list):
            return [res(v, depth + 1, seen) for v in x]
        return x

    top = plist["$top"]
    root = top.get("root", next(iter(top.values()))) if isinstance(top, dict) else top
    return res(root, 0, frozenset())


def _classes(plist: dict) -> list[str]:
    out = set()
    for o in plist.get("$objects", []):
        if isinstance(o, dict) and "$classname" in o:
            out.add(o["$classname"])
    return sorted(out)


# ------------------------------------------------------------ Parser
def is_cod(data: bytes) -> bool:
    return data.startswith(b"bplist00") and b"NSKeyedArchiver" in data[-4096:] + data[:4096] or (
        data.startswith(b"bplist00") and b"codingECU" in data)


def _ver(main: Any, sub: Any, patch: Any) -> str:
    return f"{int(main):03d}_{int(sub):03d}_{int(patch):03d}"


def parse_cod(data: bytes, filename: str = "") -> CodBackup:
    if data.startswith(JAVA_SERIAL_MAGIC):
        raise CodFormatError("Android-BimmerCode-Backup (Java-Serialisierung) – Dekodierung noch nicht implementiert")
    if not data.startswith(b"bplist00"):
        raise CodFormatError("Keine binäre Property-List (bplist00) – kein iOS-BimmerCode-Backup")
    try:
        plist = plistlib.loads(data)
    except Exception as exc:  # noqa: BLE001
        raise CodFormatError(f"Plist nicht lesbar: {exc}") from exc
    root = unarchive(plist)
    if not isinstance(root, dict):
        raise CodFormatError("Unerwartete Wurzelstruktur")
    ecu = root.get("codingECU") or {}
    cd = root.get("codingData") or {}
    ident = cd.get("CAFDIdentifier")
    cafd_id = cafd_ver = None
    if isinstance(ident, str) and re.fullmatch(r"[0-9A-Fa-f]{14}", ident):
        cafd_id = ident[:8].upper()
        cafd_ver = _ver(int(ident[8:10], 16), int(ident[10:12], 16), int(ident[12:14], 16))
    cafds: list[tuple[str, str]] = []
    idents = ecu.get("identifiers") if isinstance(ecu, dict) else None
    if isinstance(idents, dict):
        arr = idents.get("CAFD")
        items = arr if isinstance(arr, list) else ([arr] if isinstance(arr, dict) else [])
        for x in items:
            try:
                cv = (f"{int(x['identifier']):08X}", _ver(x["mainVersion"], x["subVersion"], x["patchVersion"]))
            except (KeyError, TypeError, ValueError):
                continue
            if cv not in cafds:
                cafds.append(cv)
    if cafd_id and (cafd_id, cafd_ver) not in cafds:
        cafds.insert(0, (cafd_id, cafd_ver))
    blocks: dict[str, bytes] = {}
    for b in cd.get("mutableCodingDataBlocks") or []:
        if isinstance(b, dict) and "blockAddress" in b and isinstance(b.get("data"), (bytes, bytearray)):
            blocks[f"{int(b['blockAddress']):04X}"] = bytes(b["data"])
    addr = ecu.get("address") if isinstance(ecu, dict) else None
    m = FN_RE.match(filename.rsplit("/", 1)[-1]) if filename else None

    def _scalar_extra(d: dict, prefix: str) -> dict:
        out = {}
        for k, v in d.items():
            if k in ("codingECU", "codingData", "mutableCodingDataBlocks", "VIN", "$classname"):
                continue
            if isinstance(v, (str, int, float, bool)) or v is None:
                out[f"{prefix}{k}"] = v
            elif isinstance(v, (bytes, bytearray)):
                out[f"{prefix}{k}"] = {"bytes_len": len(v), "head_hex": bytes(v[:32]).hex().upper()}
            elif isinstance(v, dict):
                out.update(_scalar_extra(v, f"{prefix}{k}."))
            elif isinstance(v, list):
                out[f"{prefix}{k}"] = f"<Liste mit {len(v)} Einträgen>"
        return out

    extra = _scalar_extra(root, "")
    if isinstance(ecu, dict):
        extra.update(_scalar_extra(ecu, "codingECU."))
    if isinstance(cd, dict):
        extra.update(_scalar_extra(cd, "codingData."))
    return CodBackup(
        platform="iOS",
        vin=root.get("VIN") if isinstance(root.get("VIN"), str) else None,
        ecu_identifier=str(ecu.get("identifier")).upper() if isinstance(ecu, dict) and ecu.get("identifier") is not None else None,
        diag_address=int(addr) if isinstance(addr, int) else None,
        cafd_id=cafd_id,
        cafd_version=cafd_ver,
        cafds=cafds,
        blocks=blocks,
        filename_ts=int(m.group("ts")) if m else None,
        filename_tag=m.group("tag") if m else None,
        root_keys=sorted(k for k in root.keys() if not k.startswith("$")),
        extra=extra,
        classes=_classes(plist),
    )


def build_test_cod(vin: str, ecu_identifier: str, diag_address: int, cafd_id: str, version: tuple[int, int, int],
                   blocks: dict[int, bytes]) -> bytes:
    """Erzeugt ein synthetisches .cod-Plist in der dokumentierten Struktur – NUR für Tests.

    Das Ergebnis ist kein echtes BimmerCode-Backup und darf nicht in
    BimmerCode importiert werden.
    """
    UID = plistlib.UID
    objs: list[Any] = ["$null"]

    def add(o: Any) -> UID:
        objs.append(o)
        return UID(len(objs) - 1)

    cls_session = add({"$classname": "CodingSession", "$classes": ["CodingSession", "NSObject"]})
    cls_ecu = add({"$classname": "CodingECU", "$classes": ["CodingECU", "NSObject"]})
    cls_data = add({"$classname": "CodingData", "$classes": ["CodingData", "NSObject"]})
    cls_block = add({"$classname": "CodingDataBlock", "$classes": ["CodingDataBlock", "NSObject"]})
    cls_arr = add({"$classname": "NSMutableArray", "$classes": ["NSMutableArray", "NSArray", "NSObject"]})
    cls_dict = add({"$classname": "NSDictionary", "$classes": ["NSDictionary", "NSObject"]})
    cls_cafd = add({"$classname": "SGBMID", "$classes": ["SGBMID", "NSObject"]})
    block_uids = []
    for address, data in sorted(blocks.items()):
        d_uid = add(bytes(data))
        block_uids.append(add({"$class": cls_block, "blockAddress": address, "data": d_uid}))
    blocks_arr = add({"$class": cls_arr, "NS.objects": block_uids})
    ident = add(f"{int(cafd_id, 16):08X}{version[0]:02X}{version[1]:02X}{version[2]:02X}")
    cd = add({"$class": cls_data, "CAFDIdentifier": ident, "mutableCodingDataBlocks": blocks_arr})
    cafd_entry = add({"$class": cls_cafd, "identifier": int(cafd_id, 16), "mainVersion": version[0],
                      "subVersion": version[1], "patchVersion": version[2]})
    cafd_list = add({"$class": cls_arr, "NS.objects": [cafd_entry]})
    k_cafd = add("CAFD")
    idents = add({"$class": cls_dict, "NS.keys": [k_cafd], "NS.objects": [cafd_list]})
    ecu_ident = add(ecu_identifier)
    ecu = add({"$class": cls_ecu, "identifier": ecu_ident, "address": diag_address, "identifiers": idents})
    vin_uid = add(vin)
    root = add({"$class": cls_session, "VIN": vin_uid, "codingECU": ecu, "codingData": cd})
    plist = {"$version": 100000, "$archiver": "NSKeyedArchiver", "$top": {"root": root}, "$objects": objs}
    return plistlib.dumps(plist, fmt=plistlib.FMT_BINARY)
