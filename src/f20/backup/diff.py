"""Byte- und Bitvergleich von Codierdaten."""

from __future__ import annotations

import difflib


def bits_of(x: int) -> list[int]:
    return [i for i in range(8) if x & (1 << i)]


def diff_bytes(a: bytes, b: bytes, max_changes: int = 5000) -> dict:
    """Vergleich zweier Byte-Folgen.

    Gleiche Länge: positionsgenauer Vergleich mit geänderten Bits.
    Unterschiedliche Länge: Ausrichtung per SequenceMatcher (Einfügungen/Löschungen).
    """
    out: dict = {"len_a": len(a), "len_b": len(b), "identical": a == b, "changes": [], "ops": []}
    if a == b:
        return out
    if len(a) == len(b):
        for i, (x, y) in enumerate(zip(a, b)):
            if x != y:
                xo = x ^ y
                out["changes"].append({
                    "offset": i, "a": f"{x:02X}", "b": f"{y:02X}", "xor": f"{xo:02X}",
                    "bits": bits_of(xo), "a_bin": f"{x:08b}", "b_bin": f"{y:08b}",
                })
                if len(out["changes"]) >= max_changes:
                    out["truncated"] = True
                    break
        out["changed_bytes"] = len(out["changes"])
        out["changed_bits"] = sum(len(c["bits"]) for c in out["changes"])
        return out
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        out["ops"].append({"op": tag, "a_range": [i1, i2], "b_range": [j1, j2],
                           "a_hex": a[i1:i2][:64].hex().upper(), "b_hex": b[j1:j2][:64].hex().upper()})
        if len(out["ops"]) >= max_changes:
            out["truncated"] = True
            break
    return out


def diff_blocks(a: dict[str, bytes], b: dict[str, bytes]) -> dict:
    """Vergleich zweier Codierdatensätze (Datenblock-Adresse → Bytes)."""
    res = {"only_a": sorted(set(a) - set(b)), "only_b": sorted(set(b) - set(a)), "blocks": {}}
    total_bytes = total_bits = 0
    for k in sorted(set(a) & set(b)):
        d = diff_bytes(a[k], b[k])
        if not d["identical"]:
            res["blocks"][k] = d
            total_bytes += d.get("changed_bytes", 0)
            total_bits += d.get("changed_bits", 0)
    res["changed_blocks"] = len(res["blocks"])
    res["changed_bytes"] = total_bytes
    res["changed_bits"] = total_bits
    res["identical"] = not res["blocks"] and not res["only_a"] and not res["only_b"]
    return res


def hexdump(data: bytes, offset: int = 0, length: int = 512, width: int = 16) -> list[dict]:
    rows = []
    end = min(len(data), offset + length)
    for i in range(offset - offset % width, end, width):
        chunk = data[i:min(i + width, end)]
        rows.append({
            "offset": i,
            "hex": [f"{c:02X}" for c in chunk],
            "ascii": "".join(chr(c) if 32 <= c < 127 else "." for c in chunk),
        })
    return rows
