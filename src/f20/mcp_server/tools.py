"""Lesende Werkzeuge für den lokalen MCP-Server (Claude ↔ F20 Intelligence).

Grundsätze:
* Ausschließlich lesend: Kein Werkzeug sendet etwas an Adapter oder Fahrzeug,
  keines verändert Backups, Datenbank oder Dateien.
* Freigabe: Datenkategorien lassen sich in ``$F20_HOME/mcp_consent.json`` abschalten
  (Standard: alles freigegeben außer der vollständigen FIN, die immer maskiert wird).
* Nur das eigene Fahrzeug; ausgeschlossene Fremdfahrzeuge werden nie ausgegeben.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from ..analysis import consumption_hints, derived_values, engine_findings
from ..backup.personal import atlas, catalog_crossref, explained_history, own_backups, own_vin
from ..backup.service import BackupService, mask_vin
from ..coding.catalog import LABELS_DE, default_catalog, load_json_data
from ..paths import f20_home
from ..safety.policy import OBD_ALLOWED_MODES, UDS_ALLOWED, UDS_FORBIDDEN
from ..store import Store

REPO_ROOT = Path(__file__).resolve().parents[3]
CATEGORIES = ("vehicle", "ecus", "catalog", "coding", "backups", "diagnosis", "live", "research")


def _consent() -> dict:
    p = f20_home() / "mcp_consent.json"
    base = {c: True for c in CATEGORIES}
    if p.exists():
        try:
            base.update({k: bool(v) for k, v in json.loads(p.read_text(encoding="utf-8")).items() if k in base})
        except ValueError:
            pass
    return base


def _require(cat: str) -> None:
    if not _consent().get(cat, False):
        raise PermissionError(f"Datenkategorie '{cat}' ist in mcp_consent.json nicht freigegeben")


class F20Tools:
    def __init__(self, store: Store | None = None) -> None:
        self.store = store or Store()
        self.svc = BackupService(self.store)
        self.catalog = default_catalog()
        self._atlas: dict | None = None

    def _get_atlas(self) -> dict:
        if self._atlas is None:
            self._atlas = atlas(self.svc)
        return self._atlas

    # ------------------------------------------------------------ Fahrzeug
    def vehicle_profile(self) -> dict:
        """Fahrzeugprofil mit Nachweisstatus je Angabe (FIN maskiert)."""
        _require("vehicle")
        prof = load_json_data("vehicle_profile.json")
        return {"vin_masked": mask_vin(own_vin()), "fields": prof["fields"],
                "evidence_scale": LABELS_DE["evidence"]}

    def list_ecus(self) -> dict:
        """Steuergeräte des F20 mit Adresse, Rolle, Sicherheitsrelevanz und Nachweis des Verbaus."""
        _require("ecus")
        return load_json_data("ecus.json")

    # ------------------------------------------------------------ Katalog
    def coding_options(self, query: str = "", ecu: str = "", category: str = "", only_recommendable: bool = False,
                       max_risk: str = "", limit: int = 60) -> dict:
        """Codierungskatalog durchsuchen. Liefert je Option Risiko, Kompatibilität, Nachweis und – falls aus
        dem Backup bekannt – den aktuellen Wert im Fahrzeug."""
        _require("catalog")
        res = self.catalog.search(q=query, ecu=ecu or None, category=category or None,
                                  max_risk=max_risk or None, only_recommendable=only_recommendable)
        status = self._crossref_index() if _consent().get("coding") else {}
        out = []
        for e in res[:limit]:
            s = status.get(e["id"], {})
            out.append({"id": e["id"], "ecu": e["ecu"], "title_de": e["title_de"], "risk": e["risk"],
                        "compatibility": e["compatibility"], "evidence": e["evidence"], "benefit": e["benefit"],
                        "bimmercode_mode": e["bimmercode_mode"], "legal_note": e.get("legal_note_de"),
                        "in_car": s.get("status"), "current": [(h["function"], h["value_label"] or h["value_hex"])
                                                             for h in s.get("hits", [])][:3]})
        return {"count": len(res), "returned": len(out), "options": out}

    def coding_option_detail(self, option_id: str) -> dict:
        """Alle Details einer Katalogoption inkl. Quellen und aktuellem Wert im Fahrzeug."""
        _require("catalog")
        e = self.catalog.get(option_id)
        if not e:
            return {"error": f"Unbekannte Option {option_id}"}
        out = {k: v for k, v in e.items() if not k.startswith("_")}
        if _consent().get("coding"):
            out["in_car"] = self._crossref_index().get(option_id)
        return out

    def _crossref_index(self) -> dict:
        try:
            return {x["id"]: x for x in catalog_crossref(self._get_atlas(), self.catalog)}
        except Exception:  # noqa: BLE001
            return {}

    # ------------------------------------------------------------ Codierung (Klartext)
    def current_coding(self, ecu: str, search: str = "", block: str = "", limit: int = 150) -> dict:
        """Aktuelle Codierung eines Steuergeräts im Klartext (aus dem jüngsten Backup).
        ecu: FEM_BODY, REM, KOMBI, HU_ENTRY, IHKA, ICM, ACSM. search: Teilstring im Parameternamen."""
        _require("coding")
        at = self._get_atlas()
        e = at["ecus"].get(ecu.upper())
        if not e:
            return {"error": f"Kein Backup/keine Namen für {ecu}", "available": sorted(at["ecus"])}
        rx = re.compile(re.escape(search), re.I) if search else None
        rows = []
        for addr, blk in sorted(e["blocks"].items()):
            if block and addr != block.upper():
                continue
            for f in blk["functions"]:
                if rx and not rx.search(f["name"]):
                    continue
                if f["name"] in ("UNBELEGT", "(unbenannt)", "nicht_belegen"):
                    continue
                rows.append({"block": addr, "group": blk["group"], "name": f["name"], "value": f["value_label"] or f["value_hex"],
                             "options": [o["label"] for o in f["options"]][:12], "field_match": f.get("field_match"),
                             "layout_confidence": blk["layout"].get("confidence")})
        return {"ecu": ecu.upper(), "sgbm": e["sgbm"], "names_source": e["names_source"],
                "note": "Werte aus dem jüngsten BimmerCode-Backup; Namen aus lokal hinterlegten Tabellen.",
                "total": len(rows), "parameters": rows[:limit]}

    # ------------------------------------------------------------ Backups
    def backup_history(self) -> dict:
        """Was wurde wann geändert? Änderungshistorie des eigenen Fahrzeugs mit Parameternamen."""
        _require("backups")
        return {"history": explained_history(self.svc)}

    def list_backups(self) -> dict:
        """Backups des eigenen Fahrzeugs (Fremdfahrzeuge ausgeschlossen)."""
        _require("backups")
        return {"backups": [self.svc.summary(b["id"], privacy=True) for b in own_backups(self.svc)]}

    # ------------------------------------------------------------ Diagnose / Live
    def latest_diagnosis(self) -> dict:
        """Letzte gespeicherte Diagnosesitzung (Steuergeräte, Fehlerspeicher). Demo-Sitzungen sind markiert."""
        _require("diagnosis")
        real = self.store.latest_diagnosis("real")
        if real:
            return {"mode": "real", **real}
        demo = self.store.latest_diagnosis("demo")
        return {"mode": "none" if not demo else "demo_only",
                "note": "Noch keine reale Diagnose. Demo-Daten sind fiktiv und nicht auf das Fahrzeug übertragbar.",
                "demo": demo}

    def live_snapshot(self) -> dict:
        """Zuletzt gespeicherte Messwerte (nur reale Sitzungen) mit abgeleiteten Größen und Auffälligkeiten."""
        _require("live")
        rows = self.store.latest_readings("real")
        if not rows:
            return {"available": False, "note": "Keine realen Messwerte gespeichert. Live-Test am Fahrzeug nötig."}
        values = {r["key"]: r["value"] for r in rows}
        return {"available": True, "readings": rows, "derived": derived_values(values),
                "findings": engine_findings(values), "consumption_hints": consumption_hints(values)}

    # ------------------------------------------------------------ Wissen
    def research(self, query: str, max_hits: int = 12) -> dict:
        """Durchsucht die Projektdokumentation und Recherche-Berichte (mit Quellen) nach einem Begriff."""
        _require("research")
        files = sorted(REPO_ROOT.glob("*.md")) + sorted((REPO_ROOT / "docs").rglob("*.md"))
        rx = re.compile(re.escape(query), re.I)
        hits = []
        for f in files:
            try:
                lines = f.read_text(encoding="utf-8").splitlines()
            except OSError:
                continue
            for i, ln in enumerate(lines):
                if rx.search(ln):
                    hits.append({"file": str(f.relative_to(REPO_ROOT)), "line": i + 1,
                                 "context": "\n".join(lines[max(0, i - 2): i + 3])[:700]})
                    if len(hits) >= max_hits:
                        return {"query": query, "hits": hits}
        return {"query": query, "hits": hits}

    def safety_policy(self) -> dict:
        """Welche Diagnosedienste erlaubt bzw. gesperrt sind (Read-only-Garantie)."""
        return {"read_only": True,
                "uds_allowed": {f"0x{k:02X}": v[0] for k, v in UDS_ALLOWED.items()},
                "uds_forbidden": {f"0x{k:02X}": v for k, v in UDS_FORBIDDEN.items()},
                "obd_allowed": {f"0x{k:02X}": v for k, v in OBD_ALLOWED_MODES.items()},
                "note": "Der MCP-Server selbst kommuniziert nie mit dem Fahrzeug."}


TOOL_NAMES = ["vehicle_profile", "list_ecus", "coding_options", "coding_option_detail", "current_coding",
              "backup_history", "list_backups", "latest_diagnosis", "live_snapshot", "research", "safety_policy"]
