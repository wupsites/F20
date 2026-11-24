"""Backup Center: Import, Analyse, Fahrzeugzuordnung, Vergleich, Lernmodus."""

from __future__ import annotations

from pathlib import Path

from ..store import Store
from .cod import CodBackup, CodFormatError, clean_upload_name, parse_cod
from .diff import diff_blocks, diff_bytes, hexdump
from .forensic import analyze_bytes
from .integrity import Vault, create_workcopy
from .mapping import Function, decode_blocks, learned_functions, load_tsv

#: Kennungen aus dem Projektauftrag, nach denen forensisch gesucht wird.
KNOWN_IDS = ["0F1820", "0F1650", "000000F9"]


def mask_vin(vin: str | None) -> str | None:
    if not vin:
        return vin
    return vin[:3] + "•" * (len(vin) - 7) + vin[-4:] if len(vin) >= 8 else "•" * len(vin)


class BackupService:
    def __init__(self, store: Store, vault: Vault | None = None) -> None:
        self.store = store
        self.vault = vault or Vault()
        self.imported_functions: list[Function] = []

    # ------------------------------------------------------------ Import
    def import_path(self, path: Path | str) -> list[dict]:
        p = Path(path).expanduser()
        files = sorted(x for x in p.rglob("*") if x.is_file() and x.suffix.lower() in (".cod", ".dat")) if p.is_dir() else [p]
        return [self._import_entry(self.vault.import_file(f)) for f in files]

    def import_bytes(self, name: str, data: bytes) -> dict:
        return self._import_entry(self.vault.import_bytes(name, data))

    def _import_entry(self, entry) -> dict:
        entry.original_name = clean_upload_name(entry.original_name)
        alias = {"name": entry.original_name, "ts": _filename_ts(entry.original_name)}
        existing = self.store.backup_by_sha(entry.sha256)
        if existing:
            # Byteidentischer Inhalt unter anderem Dateinamen/Zeitpunkt: als Alias vermerken,
            # Metadaten des Erstimports NICHT überschreiben.
            meta = existing["meta"]
            aliases = meta.setdefault("aliases", [])
            if alias not in aliases:
                aliases.append(alias)
                aliases.sort(key=lambda a: a["ts"] or 0)
                self.store.update_backup_meta(existing["id"], vehicle_key=existing["vehicle_key"],
                                              fmt=existing["format"], meta=meta)
            return self.store.get_backup(existing["id"])
        data = Vault.read_verified(entry.path, entry.sha256)
        meta, fmt, vehicle_key = self._analyze(data, entry.original_name)
        meta["aliases"] = [alias]
        bid = self.store.add_backup(sha256=entry.sha256, original_name=entry.original_name,
                                    source_path=entry.source_path, source_mtime=entry.source_mtime,
                                    size=entry.size, vault_path=str(entry.path), vehicle_key=vehicle_key,
                                    fmt=fmt, meta=meta)
        return self.store.get_backup(bid)

    def _analyze(self, data: bytes, name: str) -> tuple[dict, str, str | None]:
        meta: dict = {}
        fmt = "unknown"
        vin = None
        try:
            cod = parse_cod(data, name)
            meta["cod"] = cod.to_dict()
            fmt = "bimmercode-ios-cod"
            vin = cod.vin
        except CodFormatError as exc:
            meta["cod_error"] = str(exc)
            if data.startswith(b"\xac\xed\x00\x05"):
                fmt = "bimmercode-android-dat"
        forensic = analyze_bytes(data, name, KNOWN_IDS)
        meta["forensic_summary"] = {
            "container": forensic["container"], "entropy_total": forensic["entropy_total"],
            "assessment": forensic["assessment"], "patterns": forensic["patterns"],
            "filename_info": forensic.get("filename_info"),
        }
        if not vin:
            fin = forensic.get("filename_info", {}).get("vins") or forensic["patterns"]["bmw_vins"]
            vin = fin[0] if fin else None
        return meta, fmt, vin

    def reanalyze_all(self) -> int:
        n = 0
        for b in self.store.list_backups():
            data = Vault.read_verified(b["vault_path"], b["sha256"])
            meta, fmt, vk = self._analyze(data, b["original_name"])
            self.store.update_backup_meta(b["id"], vehicle_key=vk, fmt=fmt, meta=meta)
            n += 1
        return n

    # ------------------------------------------------------------ Zugriff
    def load(self, backup_id: int) -> tuple[dict, bytes]:
        b = self.store.get_backup(backup_id)
        if b is None:
            raise KeyError(f"Backup {backup_id} unbekannt")
        return b, Vault.read_verified(b["vault_path"], b["sha256"])

    def load_cod(self, backup_id: int) -> tuple[dict, CodBackup]:
        b, data = self.load(backup_id)
        return b, parse_cod(data, b["original_name"])

    def forensic(self, backup_id: int) -> dict:
        b, data = self.load(backup_id)
        return analyze_bytes(data, b["original_name"], KNOWN_IDS)

    def summary(self, backup_id: int, privacy: bool = False) -> dict:
        b = self.store.get_backup(backup_id)
        if b is None:
            raise KeyError(backup_id)
        cod = b["meta"].get("cod") or {}
        return {
            "id": b["id"], "name": _mask_name(b["original_name"], b.get("vehicle_key")) if privacy else b["original_name"],
            "sha256": b["sha256"], "size": b["size"], "format": b["format"],
            "vehicle": mask_vin(b.get("vehicle_key")) if privacy else b.get("vehicle_key"),
            "ecu_identifier": cod.get("ecu_identifier"), "diag_address": cod.get("diag_address"),
            "sgbm": cod.get("sgbm"), "cafds": cod.get("cafds"), "created_at": cod.get("created_at"),
            "blocks": cod.get("blocks"), "assessment": b["meta"].get("forensic_summary", {}).get("assessment"),
            "error": b["meta"].get("cod_error"),
        }

    # ------------------------------------------------------------ Fahrzeuge
    def vehicles(self, privacy: bool = False) -> list[dict]:
        groups: dict[str, list[dict]] = {}
        for b in self.store.list_backups():
            groups.setdefault(b.get("vehicle_key") or "UNBEKANNT", []).append(b)
        out = []
        for key, items in sorted(groups.items()):
            ecus = sorted({(b["meta"].get("cod") or {}).get("ecu_identifier") or "?" for b in items})
            dates = sorted(filter(None, ((b["meta"].get("cod") or {}).get("created_at") for b in items)))
            out.append({
                "vehicle_key": mask_vin(key) if privacy and key != "UNBEKANNT" else key,
                "backup_count": len(items), "ecu_identifiers": ecus,
                "first_backup": dates[0] if dates else None, "last_backup": dates[-1] if dates else None,
                "confidence": "hoch (FIN im Backup-Inhalt)" if key != "UNBEKANNT" and any(
                    (b["meta"].get("cod") or {}).get("vin") for b in items) else
                ("mittel (FIN nur im Dateinamen)" if key != "UNBEKANNT" else "keine FIN gefunden"),
                "backup_ids": [b["id"] for b in items],
            })
        return out

    # ------------------------------------------------------------ Vergleich
    def compare(self, a_id: int, b_id: int) -> dict:
        ba, da = self.load(a_id)
        bb, db = self.load(b_id)
        res: dict = {"a": self.summary(a_id), "b": self.summary(b_id)}
        try:
            ca, cb = parse_cod(da, ba["original_name"]), parse_cod(db, bb["original_name"])
            res["same_vehicle"] = bool(ca.vin and ca.vin == cb.vin)
            res["same_scope"] = ca.scope_key == cb.scope_key
            res["block_diff"] = diff_blocks(ca.blocks, cb.blocks)
            res["warnings"] = []
            if not res["same_vehicle"]:
                res["warnings"].append("Backups stammen von unterschiedlichen Fahrzeugen.")
            if not res["same_scope"]:
                res["warnings"].append("Unterschiedliches Steuergerät oder unterschiedliche CAFD-Version – "
                                       "Byte-Positionen sind nicht direkt vergleichbar.")
        except CodFormatError:
            res["file_diff"] = diff_bytes(da, db)
        return res

    def timeline(self) -> list[dict]:
        """Änderungsverlauf je Fahrzeug/Steuergerät/CAFD-Version (chronologisch)."""
        import datetime as _dt
        groups: dict[str, list[tuple[int, int, str, CodBackup]]] = {}
        for b in self.store.list_backups():
            if b["format"] != "bimmercode-ios-cod":
                continue
            _, cod = self.load_cod(b["id"])
            scope = cod.scope_key if cod.ecu_identifier else f"{_ecu_from_name(b['original_name'])}|E-Serie|"
            for a in b["meta"].get("aliases") or [{"name": b["original_name"], "ts": cod.filename_ts}]:
                groups.setdefault(f"{cod.vin}|{scope}", []).append((a["ts"] or 0, b["id"], a["name"], cod))
        out = []
        for key, items in sorted(groups.items()):
            items.sort(key=lambda x: x[0])
            steps = []
            for (pts, pid, pname, prev), (cts, cid, cname, cur) in zip(items, items[1:]):
                d = diff_blocks(prev.blocks, cur.blocks)
                steps.append({"from": pid, "to": cid, "from_name": pname, "to_name": cname,
                              "from_date": _dt.datetime.fromtimestamp(pts, _dt.timezone.utc).isoformat() if pts else None,
                              "to_date": _dt.datetime.fromtimestamp(cts, _dt.timezone.utc).isoformat() if cts else None,
                              "identical": d["identical"], "changed_blocks": sorted(d["blocks"]),
                              "changed_bytes": d["changed_bytes"], "changed_bits": d["changed_bits"],
                              "detail": d["blocks"]})
            vin, _, scope = key.partition("|")
            out.append({"vehicle": vin, "scope": scope, "backups": [i[1] for i in items],
                        "events": [{"ts": i[0], "backup": i[1], "name": i[2]} for i in items], "steps": steps})
        return out

    # ------------------------------------------------------------ Lernmodus
    def learn(self, before_id: int, after_id: int, label: str, note: str | None = None) -> list[dict]:
        """Speichert die Bit-Änderungen zwischen zwei Backups als Zuordnung für ``label``.

        Voraussetzung: gleiches Fahrzeug, gleiches Steuergerät, gleiche CAFD-Version und
        zwischen beiden Backups wurde in BimmerCode genau EINE Option geändert.
        """
        _, a = self.load_cod(before_id)
        _, b = self.load_cod(after_id)
        if a.scope_key != b.scope_key or a.vin != b.vin:
            raise ValueError("Lernmodus nur für Backups desselben Fahrzeugs, Steuergeräts und derselben CAFD-Version")
        d = diff_blocks(a.blocks, b.blocks)
        saved = []
        for block, bd in d["blocks"].items():
            for ch in bd.get("changes", []):
                mask = int(ch["xor"], 16)
                oid = self.store.add_observation(label=label, scope=f"{a.scope_key}#{block}",
                                                 byte_offset=ch["offset"], mask=mask, before=int(ch["a"], 16),
                                                 after=int(ch["b"], 16), backup_a=before_id, backup_b=after_id,
                                                 note=note)
                saved.append({"id": oid, "block": block, **ch})
        return saved

    # ------------------------------------------------------------ Dekodierung
    def import_names(self, path: Path | str) -> int:
        funcs = load_tsv(path)
        self.imported_functions.extend(funcs)
        return len(funcs)

    def decode(self, backup_id: int) -> dict:
        _, cod = self.load_cod(backup_id)
        learned = learned_functions(self.store.list_observations())
        learned = [f for f in learned if f.cafd_id == (cod.cafd_id or "")]
        results = []
        for cafd_id, _ver in cod.cafds or [(cod.cafd_id, cod.cafd_version)]:
            if cafd_id:
                results += decode_blocks(cod.blocks, cafd_id, learned + self.imported_functions)
        return {"backup_id": backup_id, "sgbm": cod.sgbm, "parameters": results,
                "mapped": len(results), "blocks": {k: len(v) for k, v in cod.blocks.items()},
                "note": None if results else
                "Keine Zuordnung für diese CAFD vorhanden. Nutze den Lernmodus (Vorher/Nachher-Backup) "
                "oder importiere eine Namenstabelle (TSV)."}

    def hex_view(self, backup_id: int, block: str | None, offset: int = 0, length: int = 512) -> dict:
        b, data = self.load(backup_id)
        if block:
            _, cod = self.load_cod(backup_id)
            buf = cod.blocks.get(block.upper())
            if buf is None:
                raise KeyError(f"Datenblock {block} nicht vorhanden")
        else:
            buf = data
        return {"backup_id": backup_id, "block": block, "size": len(buf), "rows": hexdump(buf, offset, length)}

    def simulate(self, backup_id: int, block: str, start: int, end: int, mask: int, value_hex: str) -> dict:
        """Virtuelle Codierung: setzt einen Wert in einer KOPIE des Datenblocks (nur im Speicher).

        Es wird nichts gespeichert und nichts an ein Fahrzeug gesendet. Ergebnis:
        neuer Blockinhalt + Bit-Diff gegenüber dem Original.
        """
        _, cod = self.load_cod(backup_id)
        orig = cod.blocks.get(block.upper())
        if orig is None:
            raise KeyError(f"Datenblock {block} nicht vorhanden")
        if not (0 <= start <= end < len(orig)):
            raise ValueError("Byte-Bereich außerhalb des Datenblocks")
        new = bytearray(orig)
        value = bytes.fromhex(value_hex.zfill(2 * (end - start + 1)) if end > start else value_hex.zfill(2))
        if start == end:
            shift = (mask & -mask).bit_length() - 1 if mask else 0
            v = (value[-1] << shift) & mask
            if v >> shift != value[-1]:
                raise ValueError("Wert passt nicht in die Bitmaske")
            new[start] = (orig[start] & ~mask & 0xFF) | v
        else:
            if len(value) != end - start + 1:
                raise ValueError("Wertlänge passt nicht zum Byte-Bereich")
            for i, vb in enumerate(value):
                new[start + i] = (orig[start + i] & ~mask & 0xFF) | (vb & mask)
        return {"backup_id": backup_id, "block": block.upper(), "simulated": True,
                "written_to_vehicle": False, "diff": diff_bytes(orig, bytes(new)),
                "new_block_hex": bytes(new).hex().upper()}

    def make_workcopy(self, backup_id: int, note: str | None = None) -> dict:
        b = self.store.get_backup(backup_id)
        path = create_workcopy(b["vault_path"], b["sha256"], b["original_name"])
        wid = self.store.add_workcopy(backup_id, str(path), note)
        return {"id": wid, "path": str(path), "backup_id": backup_id}


def _ecu_from_name(name: str) -> str:
    from .cod import FN_RE
    m = FN_RE.search(name)
    return m.group("ecu") if m else "?"


def _filename_ts(name: str) -> int | None:
    from .cod import FN_RE
    m = FN_RE.search(name)
    return int(m.group("ts")) if m else None


def _mask_name(name: str, vin: str | None) -> str:
    return name.replace(vin, mask_vin(vin)) if vin and vin in name else name
