"""Persönliche Auswertung: eigenes Fahrzeug, aktuelle Codierung im Klartext, Katalog-Abgleich.

* Fremdfahrzeuge (z. B. Testbackups am Auto eines Kollegen) werden über
  ``$F20_HOME/vehicle.local.json`` → ``excluded_vins`` dauerhaft ausgeschlossen.
* Parameternamen stammen aus lokal abgelegten OpenCAFDMap-Tabellen
  (``$F20_HOME/mappings/opencafdmap``) – nur nach Freigabe des Besitzers,
  niemals im Repository.
"""

from __future__ import annotations

import json
from pathlib import Path

from ..coding.catalog import Catalog, load_json_data
from ..paths import f20_home
from .layouts import CafdNames, decode_with_names
from .service import BackupService


def local_vehicle() -> dict:
    p = f20_home() / "vehicle.local.json"
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except ValueError:
            return {}
    return {}


def own_vin() -> str | None:
    return local_vehicle().get("vin")


def excluded_vins() -> set[str]:
    return set(local_vehicle().get("excluded_vins", []))


def mappings_dir() -> Path:
    return f20_home() / "mappings" / "opencafdmap"


def load_names(cafd_id: str) -> CafdNames | None:
    for sub in ("merged", "bmw"):
        p = mappings_dir() / sub / f"{cafd_id}.tsv.gz"
        if p.exists():
            return CafdNames.load(p, cafd_id)
    return None


def own_backups(svc: BackupService) -> list[dict]:
    vin, excl = own_vin(), excluded_vins()
    out = []
    for b in svc.store.list_backups():
        vk = b.get("vehicle_key")
        if vk in excl:
            continue
        if vin and vk != vin:
            continue
        out.append(b)
    return out


def latest_by_ecu(svc: BackupService) -> dict[str, dict]:
    """Pro Steuergerätekennung das zeitlich jüngste Backup des eigenen Fahrzeugs."""
    best: dict[str, tuple[int, dict]] = {}
    for b in own_backups(svc):
        cod = b["meta"].get("cod") or {}
        ident = cod.get("ecu_identifier")
        if not ident:
            continue
        ts = max((a.get("ts") or 0) for a in b["meta"].get("aliases", [{"ts": 0}]))
        if ident not in best or ts > best[ident][0]:
            best[ident] = (ts, b)
    return {k: v[1] for k, v in best.items()}


def ecu_name_for_address(addr: str | None) -> str | None:
    if not addr:
        return None
    for e in load_json_data("ecus.json")["ecus"]:
        if e["address"].lower() == addr.lower():
            return e["name"]
    return None


def atlas(svc: BackupService) -> dict:
    """Vollständige Klartext-Codierung aller Steuergeräte (jüngster Stand je SG)."""
    result: dict = {"vin_masked": None, "ecus": {}}
    vin = own_vin()
    if vin:
        result["vin_masked"] = vin[:3] + "…" + vin[-4:]
    for ident, b in sorted(latest_by_ecu(svc).items()):
        _, cod = svc.load_cod(b["id"])
        name = ecu_name_for_address(f"0x{cod.diag_address:02X}" if cod.diag_address is not None else None) or ident
        entry = {"identifier": ident, "address": f"0x{cod.diag_address:02X}", "sgbm": cod.sgbm,
                 "backup_id": b["id"], "backup_date": max(a["ts"] for a in b["meta"]["aliases"]),
                 "blocks": {}, "names_source": None}
        for cafd_id, _ver in cod.cafds:
            names = load_names(cafd_id)
            if not names:
                continue
            entry["names_source"] = names.source
            dec = decode_with_names({k: v for k, v in cod.blocks.items()
                                     if k in names.layouts or k in names.groups}, names)
            for addr, blk in dec["blocks"].items():
                blk["cafd_id"] = cafd_id
                entry["blocks"][addr] = blk
        result["ecus"][name] = entry
    return result


def catalog_crossref(at: dict, catalog: Catalog) -> list[dict]:
    """Prüft für jede Katalogoption, ob ihre Parameter im eigenen Steuergerät existieren."""
    index: dict[tuple[str, str], list[dict]] = {}
    for ecu, e in at["ecus"].items():
        for addr, blk in e["blocks"].items():
            for f in blk["functions"]:
                index.setdefault((ecu, f["name"]), []).append({**f, "block": addr, "confidence": blk["layout"].get("confidence")})
    from .layouts import all_names
    table_names: dict[str, set[str]] = {}
    for ecu, e in at["ecus"].items():
        names: set[str] = set()
        for cafd_id in {blk.get("cafd_id") for blk in e["blocks"].values()}:
            n = load_names(cafd_id) if cafd_id else None
            if n:
                names |= all_names(n)
        table_names[ecu] = names
    out = []
    for c in catalog.entries:
        hits = []
        for fn in c["function_names"]:
            for h in index.get((c["ecu"], fn), []):
                hits.append({"function": fn, "block": h["block"], "value_hex": h["value_hex"],
                             "value_label": h["value_label"], "options": h["options"],
                             "layout_confidence": h["confidence"], "field_match": h.get("field_match", False)})
        ecu_known = c["ecu"] in at["ecus"]
        status, reason = None, None
        if not c["function_names"]:
            reason = "Katalogeintrag ohne Parameternamen (nur BimmerCode-Oberfläche)"
        elif not ecu_known:
            reason = "Kein Backup dieses Steuergeräts vorhanden"
        elif hits:
            status = "present"
        else:
            blk = (c.get("cafd_block") or "")[:4].upper()
            blocks = at["ecus"][c["ecu"]]["blocks"]
            if blk and blk not in blocks:
                status, reason = "absent", f"Datenblock {blk} existiert in deinem Steuergerät nicht"
            elif any(fn in table_names.get(c["ecu"], set()) for fn in c["function_names"]):
                status, reason = "unknown", ("Name existiert in anderen CAFD-Versionen, Position für deine Version "
                                             "nicht eindeutig – im BimmerCode-Expertenmodus prüfen")
            else:
                conf = blocks.get(blk, {}).get("layout", {}).get("confidence") if blk else None
                if conf == "hoch":
                    status, reason = "absent", "Vollständiges Layout des Blocks enthält diesen Parameter nicht"
                else:
                    status, reason = "unknown", "Parameter nicht in den Namenstabellen gefunden"
        out.append({"id": c["id"], "ecu": c["ecu"], "title_de": c["title_de"], "function_names": c["function_names"],
                    "ecu_in_backups": ecu_known, "status": status, "reason": reason,
                    "present": True if status == "present" else (False if status == "absent" else None),
                    "hits": hits})
    return out


def explained_history(svc: BackupService) -> list[dict]:
    """Änderungshistorie des eigenen Fahrzeugs; geänderte Bits mit Parameternamen (falls Tabellen vorhanden)."""
    from .layouts import choose_layout
    vin, excl = own_vin(), excluded_vins()
    out = []
    for t in svc.timeline():
        if t["vehicle"] in excl or (vin and t["vehicle"] != vin):
            continue
        parts = t["scope"].split("|")
        cafd = parts[1] if len(parts) > 1 else ""
        names = load_names(cafd) if cafd else None
        steps = []
        for s in t["steps"]:
            changes = []
            if not s["identical"]:
                _, before = svc.load_cod(s["from"])
                _, after = svc.load_cod(s["to"])
                for blk, d in s["detail"].items():
                    group = names.groups.get(blk) if names else None
                    if group == "SIGNATURE":
                        changes.append({"block": blk, "group": group, "signature": True})
                        continue
                    lay = None
                    if names:
                        lay, _info = choose_layout(names, blk, before.blocks[blk])
                    for ch in d.get("changes", []):
                        xo = int(ch["xor"], 16)
                        fns = [f for f in (lay.functions if lay else []) if f.start <= ch["offset"] <= f.end
                               and (f.mask & xo or f.end > f.start)]
                        changes.append({
                            "block": blk, "group": group, "byte": ch["offset"], "before": ch["a"], "after": ch["b"],
                            "parameters": [{"name": f.name, "before": f.label(f.extract(before.blocks[blk])) or f.extract(before.blocks[blk]),
                                            "after": f.label(f.extract(after.blocks[blk])) or f.extract(after.blocks[blk])} for f in fns],
                        })
            steps.append({"from_date": s["from_date"], "to_date": s["to_date"], "identical": s["identical"],
                          "changes": changes})
        out.append({"ecu_identifier": parts[0], "cafd": cafd, "steps": steps})
    return out


def write_private_reports(svc: BackupService, catalog: Catalog, out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    at = atlas(svc)
    (out_dir / "atlas.json").write_text(json.dumps(at, ensure_ascii=False, indent=1), encoding="utf-8")
    xref = catalog_crossref(at, catalog)
    (out_dir / "catalog_crossref.json").write_text(json.dumps(xref, ensure_ascii=False, indent=1), encoding="utf-8")
    # Markdown-Atlas
    L = ["# PARAMETER-ATLAS – aktuelle Codierung deines F20 (PRIVAT, nicht im Repository)", "",
         f"Fahrzeug: {at['vin_masked']} · Quelle Parameternamen: OpenCAFDMap (lokal, nach Freigabe)", "",
         "Layout-Konfidenz je Block: hoch / mittel / niedrig (siehe src/f20/backup/layouts.py).", ""]
    for ecu, e in at["ecus"].items():
        L += [f"## {ecu} ({e['identifier']}, {e['address']}, {e['sgbm']})", ""]
        for addr, blk in sorted(e["blocks"].items()):
            if not blk["functions"]:
                continue
            L += [f"### Block {addr} – {blk['group']} (Konfidenz: {blk['layout'].get('confidence')})", "",
                  "| Parameter | Byte | Maske | Wert | Bedeutung | Optionen |", "|---|---|---|---|---|---|"]
            for f in blk["functions"]:
                opts = ", ".join(o["label"] for o in f["options"])[:120]
                L.append(f"| `{f['name']}` | {f['start']}{'' if f['end'] == f['start'] else '–' + str(f['end'])} | "
                         f"{f['mask']} | `{(f['value_hex'] or '')[:24]}` | {f['value_label'] or ''} | {opts} |")
            L.append("")
    (out_dir / "PARAMETER_ATLAS.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    present = sum(1 for x in xref if x["present"])
    return {"ecus": len(at["ecus"]), "catalog_present": present,
            "catalog_checked": sum(1 for x in xref if x["present"] is not None)}
