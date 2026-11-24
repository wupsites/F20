"""Import und Auswahl von Datenblock-Layouts im OpenCAFDMap-Paketformat (untrimmed).

Format (OpenCAFDMap ocm/untrimmed.py, MIT, geprüft 2026-11-24)::

    kind  address  layout_hash  start  end  mask  value_hex  name
    G = Gruppenname, F = Funktion, V = Wertname, R/S = Zusatzinfos

``layout_hash`` = md5(";".join(f"{start}:{end}:{mask}") der geordneten Funktionen)[:16].

Diese Tabellen werden NICHT mit dem Projekt ausgeliefert (Rechtslage unklar,
BMW-Herkunft). Der Besitzer lädt sie selbst (scripts/fetch_opencafdmap.sh) in
$F20_HOME/mappings/opencafdmap/. Da die CAFD-Datei selbst fehlt, wird das
passende Layout je Datenblock *bewertet* und mit Konfidenz ausgegeben:

1. Hash-Konsistenz: Die F-Zeilen eines Layouts ergeben exakt dessen Hash → Layout vollständig.
2. Blocklänge: größtes ``end`` muss kleiner als die Blocklänge sein; ideal = Blocklänge − 1.
3. Werteplausibilität: Anteil der Funktionen, deren aktueller Wert in den bekannten Werten liegt.
"""

from __future__ import annotations

import gzip
import hashlib
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from .mapping import Function


def norm_mask(m: str) -> str:
    s = (m or "").strip().lower()
    if s.endswith("b") and set(s[:-1]) <= {"0", "1"} and s[:-1]:
        return s
    try:
        return format(int(s, 16), "08b") + "b"
    except ValueError:
        return s


def layout_hash(funcs: list[tuple[int, int, str]]) -> str:
    s = ";".join(f"{int(st)}:{int(en)}:{norm_mask(mk)}" for st, en, mk in funcs)
    return hashlib.md5(s.encode("ascii")).hexdigest()[:16]


@dataclass
class Layout:
    address: str
    hash: str
    functions: list[Function] = field(default_factory=list)
    complete: bool = False

    @property
    def max_end(self) -> int:
        return max((f.end for f in self.functions), default=-1)


@dataclass
class CafdNames:
    cafd_id: str
    source: str
    groups: dict[str, str] = field(default_factory=dict)
    layouts: dict[str, dict[str, Layout]] = field(default_factory=lambda: defaultdict(dict))

    @classmethod
    def load(cls, path: Path | str, cafd_id: str | None = None) -> "CafdNames":
        p = Path(path)
        raw = p.read_bytes()
        text = (gzip.decompress(raw) if p.suffix == ".gz" else raw).decode("utf-8", "replace")
        cid = (cafd_id or p.name.split(".")[0]).upper()
        obj = cls(cid, f"OpenCAFDMap {p.parent.name}/{p.name}")
        order: dict[tuple[str, str], list[tuple[int, int, str]]] = defaultdict(list)
        for line in text.splitlines():
            if not line or line.startswith("#"):
                continue
            cols = (line.split("\t") + [""] * 8)[:8]
            kind, addr, lh, st, en, mk, vh, name = (c.strip() for c in cols)
            addr = addr.upper()
            if kind == "G":
                if lh in ("*", "") or addr not in obj.groups:
                    obj.groups[addr] = name
                continue
            if kind not in ("F", "V") or not st or not en:
                continue
            try:
                st_i, en_i = int(st), int(en)
                mask_i = int(norm_mask(mk)[:-1], 2)
            except ValueError:
                continue
            lay = obj.layouts[addr].get(lh)
            if lay is None:
                lay = obj.layouts[addr][lh] = Layout(addr, lh)
            fn = next((f for f in lay.functions if (f.start, f.end, f.mask) == (st_i, en_i, mask_i)), None)
            if fn is None:
                fn = Function(cid, addr, st_i, en_i, mask_i, "", "", obj.source)
                lay.functions.append(fn)
                order[(addr, lh)].append((st_i, en_i, norm_mask(mk)))
            if kind == "F":
                fn.name = name
            elif vh:
                fn.values[vh.upper().zfill(2)] = name
        for (addr, lh), funcs in order.items():
            obj.layouts[addr][lh].complete = layout_hash(funcs) == lh
        return obj


def _value_hex(f: Function, block: bytes) -> str | None:
    return f.extract(block)


def score_layout(lay: Layout, block: bytes) -> dict:
    n = len(lay.functions)
    fits = lay.max_end < len(block)
    known = matched = 0
    for f in lay.functions:
        if f.values:
            known += 1
            v = _value_hex(f, block) if fits else None
            if v is not None and (v.upper() in f.values or v.upper().lstrip("0").zfill(2) in f.values):
                matched += 1
    plaus = matched / known if known else 0.0
    exact_len = fits and lay.max_end == len(block) - 1
    score = (100 if fits else -1000) + (40 if exact_len else 0) + (25 if lay.complete else 0) + 60 * plaus
    return {"hash": lay.hash, "functions": n, "max_end": lay.max_end, "fits": fits, "exact_len": exact_len,
            "complete": lay.complete, "plausibility": round(plaus, 3), "score": round(score, 1)}


def choose_layout(names: CafdNames, address: str, block: bytes) -> tuple[Layout | None, dict]:
    cands = names.layouts.get(address.upper(), {})
    if not cands:
        return None, {"candidates": 0}
    scored = sorted(((score_layout(l, block), l) for l in cands.values()), key=lambda x: -x[0]["score"])
    best_s, best = scored[0]
    second = scored[1][0]["score"] if len(scored) > 1 else None
    if not best_s["fits"]:
        conf = "keine"
    elif best_s["exact_len"] and best_s["plausibility"] >= 0.9 and (second is None or best_s["score"] - second >= 10):
        conf = "hoch"
    elif best_s["plausibility"] >= 0.75:
        conf = "mittel"
    else:
        conf = "niedrig"
    return (best if best_s["fits"] else None), {"candidates": len(cands), "best": best_s, "second_score": second,
                                                "confidence": conf}


def field_matches(names: CafdNames, address: str, block: bytes, exclude: set[tuple[int, int, int]]) -> list[Function]:
    """Namen aus ALLEN Layouts eines Blocks, deren Position (start, end, mask) in jedem Layout,
    das diese Position kennt, denselben Namen trägt (OpenCAFDMap-Prinzip 'field_match').
    Ergebnis ist schwächer belegt als ein exakt passendes Layout und wird markiert."""
    seen: dict[tuple[int, int, int], list[Function]] = {}
    for lay in names.layouts.get(address.upper(), {}).values():
        for f in lay.functions:
            seen.setdefault((f.start, f.end, f.mask), []).append(f)
    out = []
    for key, fs in seen.items():
        if key in exclude or key[1] >= len(block):
            continue
        named = {f.name for f in fs if f.name and f.name not in ("UNBELEGT", "nicht_belegen")}
        if len(named) != 1:
            continue
        merged = Function(fs[0].cafd_id, address, key[0], key[1], key[2], named.pop(), "field_match", fs[0].source)
        for f in fs:
            for k, v in f.values.items():
                merged.values.setdefault(k, v)
        out.append(merged)
    return out


def decode_with_names(blocks: dict[str, bytes], names: CafdNames) -> dict:
    out = {"cafd_id": names.cafd_id, "source": names.source, "blocks": {}}
    for addr, block in sorted(blocks.items()):
        lay, info = choose_layout(names, addr, block)
        entry = {"group": names.groups.get(addr), "length": len(block), "layout": info, "functions": []}
        funcs: list[tuple[Function, bool]] = [(f, False) for f in lay.functions] if lay else []
        exact = bool(info.get("best", {}).get("exact_len")) and info.get("confidence") == "hoch"
        if not exact and names.layouts.get(addr.upper()):
            covered = {(f.start, f.end, f.mask) for f, _ in funcs if f.name}
            # unbenannte/fehlende Felder des gewählten Layouts durch Feldabgleich ergänzen
            funcs = [(f, fm) for f, fm in funcs if f.name]
            funcs += [(f, True) for f in field_matches(names, addr, block, covered)]
        for f, fm in sorted(funcs, key=lambda x: (x[0].start, -x[0].mask)):
            v = f.extract(block)
            entry["functions"].append({
                "name": f.name or "(unbenannt)", "start": f.start, "end": f.end, "mask": f"{f.mask:08b}",
                "value_hex": v, "value_label": f.label(v) if v else None, "field_match": fm,
                "options": [{"hex": k, "label": n} for k, n in sorted(f.values.items())],
            })
        out["blocks"][addr] = entry
    return out


def all_names(names: CafdNames) -> set[str]:
    return {f.name for lays in names.layouts.values() for lay in lays.values() for f in lay.functions if f.name}
