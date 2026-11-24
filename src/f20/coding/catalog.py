"""Codierungskatalog (offline): Laden, Validieren, Suchen, Bewerten, Exportieren.

Datenquelle: src/f20/data/catalog/*.json (erzeugt aus docs/research/raw/*.json
durch scripts/build_catalog.py). Jeder Eintrag trägt Quellen und Nachweisstatus.
Es werden keine Funktionen erfunden – fehlt ein Beleg, steht evidence=unknown.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from ..paths import DATA_DIR

REQUIRED_KEYS = (
    "id", "ecu", "category", "title_de", "description_de", "function_names", "cafd_block", "values",
    "bimmercode_label", "bimmercode_mode", "hardware_requirements_de", "software_requirements_de", "effort",
    "risk", "benefit", "compatibility", "evidence", "legal_note_de", "sources", "notes_de",
)
ENUMS = {
    "category": {"idrive", "kombi", "audio", "lighting", "comfort", "locking", "windows", "wipers", "pdc",
                 "climate", "drivetrain", "safety", "other"},
    "bimmercode_mode": {"standard", "expert", "unknown"},
    "effort": {"low", "medium", "high"},
    "risk": {"low", "medium", "high", "safety_critical"},
    "benefit": {"low", "medium", "high"},
    "compatibility": {"yes", "likely", "unlikely", "no", "unknown"},
    "evidence": {"verified", "documented", "likely", "experimental", "incompatible", "unknown"},
}
RISK_ORDER = ["low", "medium", "high", "safety_critical"]
SAFETY_ECUS = {"DME", "DSC", "EPS", "ICM", "ACSM"}

LABELS_DE = {
    "risk": {"low": "gering", "medium": "mittel", "high": "hoch", "safety_critical": "sicherheitskritisch"},
    "compatibility": {"yes": "kompatibel", "likely": "wahrscheinlich kompatibel", "unlikely": "unwahrscheinlich",
                      "no": "nicht kompatibel", "unknown": "unbekannt"},
    "evidence": {"verified": "Nachgewiesen", "documented": "Dokumentiert (nicht am Fahrzeug getestet)",
                 "likely": "Technisch wahrscheinlich", "experimental": "Experimentell",
                 "incompatible": "Nicht kompatibel", "unknown": "Unbekannt"},
    "category": {"idrive": "iDrive", "kombi": "Kombiinstrument", "audio": "Audio", "lighting": "Beleuchtung",
                 "comfort": "Komfort", "locking": "Verriegelung", "windows": "Fenster", "wipers": "Wischer",
                 "pdc": "Einparkhilfe", "climate": "Klima", "drivetrain": "Antrieb/Fahrdynamik",
                 "safety": "Sicherheit", "other": "Sonstiges"},
    "effort": {"low": "gering", "medium": "mittel", "high": "hoch"},
    "benefit": {"low": "gering", "medium": "mittel", "high": "hoch"},
}


class CatalogError(ValueError):
    pass


def validate_entry(e: dict) -> list[str]:
    errs = [f"fehlendes Feld {k}" for k in REQUIRED_KEYS if k not in e]
    for k, allowed in ENUMS.items():
        if k in e and e[k] not in allowed:
            errs.append(f"{k}={e[k]!r} ungültig")
    if e.get("evidence") in ("documented", "verified") and not e.get("sources"):
        errs.append("dokumentiert ohne Quelle")
    if not isinstance(e.get("function_names", []), list) or not isinstance(e.get("values", []), list):
        errs.append("function_names/values müssen Listen sein")
    return errs


@dataclass
class Catalog:
    entries: list[dict]

    @classmethod
    def load(cls, directory: Path | None = None) -> "Catalog":
        d = directory or (DATA_DIR / "catalog")
        entries: list[dict] = []
        seen: set[str] = set()
        for f in sorted(d.glob("*.json")):
            data = json.loads(f.read_text(encoding="utf-8"))
            items = data["entries"] if isinstance(data, dict) else data
            for e in items:
                errs = validate_entry(e)
                if errs:
                    raise CatalogError(f"{f.name}: {e.get('id')}: {'; '.join(errs)}")
                if e["id"] in seen:
                    raise CatalogError(f"Doppelte ID {e['id']}")
                seen.add(e["id"])
                e = dict(e)
                e["_file"] = f.name
                e["safety_ecu"] = e["ecu"] in SAFETY_ECUS
                e["score"] = recommendation_score(e)
                entries.append(e)
        return cls(entries)

    def get(self, entry_id: str) -> dict | None:
        return next((e for e in self.entries if e["id"] == entry_id), None)

    def search(self, q: str = "", category: str | None = None, ecu: str | None = None,
               compatibility: str | None = None, max_risk: str | None = None, evidence: str | None = None,
               mode: str | None = None, only_recommendable: bool = False) -> list[dict]:
        ql = q.lower().strip()
        out = []
        for e in self.entries:
            if category and e["category"] != category:
                continue
            if ecu and e["ecu"] != ecu:
                continue
            if compatibility and e["compatibility"] != compatibility:
                continue
            if evidence and e["evidence"] != evidence:
                continue
            if mode and e["bimmercode_mode"] != mode:
                continue
            if max_risk and RISK_ORDER.index(e["risk"]) > RISK_ORDER.index(max_risk):
                continue
            if only_recommendable and not is_recommendable(e):
                continue
            if ql:
                hay = " ".join(str(e.get(k) or "") for k in ("id", "title_de", "description_de", "bimmercode_label",
                                                             "notes_de", "ecu", "cafd_block"))
                hay += " " + " ".join(e["function_names"])
                if ql not in hay.lower():
                    continue
            out.append(e)
        return sorted(out, key=lambda e: (-e["score"], e["id"]))

    def facets(self) -> dict:
        def count(k):
            c: dict[str, int] = {}
            for e in self.entries:
                c[e[k]] = c.get(e[k], 0) + 1
            return dict(sorted(c.items()))
        return {k: count(k) for k in ("category", "ecu", "compatibility", "risk", "evidence", "bimmercode_mode")}


def is_recommendable(e: dict) -> bool:
    return (e["compatibility"] in ("yes", "likely") and e["risk"] in ("low", "medium")
            and e["evidence"] in ("verified", "documented") and e["ecu"] not in SAFETY_ECUS
            and not _legal_blocker(e))


def _legal_blocker(e: dict) -> bool:
    note = (e.get("legal_note_de") or "").lower()
    return any(w in note for w in ("nicht zulässig", "unzulässig", "nicht erlaubt", "verboten", "erlischt"))


def recommendation_score(e: dict) -> int:
    s = {"high": 30, "medium": 18, "low": 6}[e["benefit"]]
    s += {"yes": 30, "likely": 20, "unknown": 0, "unlikely": -25, "no": -60}[e["compatibility"]]
    s += {"low": 20, "medium": 8, "high": -15, "safety_critical": -60}[e["risk"]]
    s += {"verified": 25, "documented": 15, "likely": 5, "experimental": -5, "unknown": -10, "incompatible": -50}[e["evidence"]]
    s += {"low": 5, "medium": 0, "high": -5}[e["effort"]]
    if e["bimmercode_mode"] == "standard":
        s += 5
    if _legal_blocker(e):
        s -= 40
    return s


@lru_cache(maxsize=1)
def default_catalog() -> Catalog:
    return Catalog.load()


def load_json_data(name: str) -> dict:
    return json.loads((DATA_DIR / name).read_text(encoding="utf-8"))


# ------------------------------------------------------------ Export
def bimmercode_instructions(entries: list[tuple[dict, str | None, str | None]]) -> str:
    """Markdown-Anleitung für die Umsetzung in BimmerCode (manuell durch den Besitzer)."""
    lines = [
        "# Codierplan für BimmerCode", "",
        "> Erstellt von F20 Intelligence (read-only). Die Umsetzung erfolgt **manuell in BimmerCode**.",
        "> Diese Software schreibt nichts ins Fahrzeug.", "",
        "## Vor dem Start", "",
        "- [ ] Batterieladegerät/-erhaltungsgerät angeschlossen (Bordspannung stabil > 12,5 V)",
        "- [ ] Zündung an, Motor aus, Lichter und Verbraucher aus",
        "- [ ] In BimmerCode für jedes betroffene Steuergerät **zuerst ein Backup** erstellen",
        "- [ ] Backup anschließend in F20 Intelligence importieren (Backup Center) – Vorher-Stand sichern",
        "- [ ] Nur **eine** Option pro Steuergerät und Durchgang ändern (erleichtert Lernmodus und Fehlersuche)",
        "",
    ]
    by_ecu: dict[str, list] = {}
    for e, target, note in entries:
        by_ecu.setdefault(e["ecu"], []).append((e, target, note))
    for ecu, items in sorted(by_ecu.items()):
        lines += [f"## Steuergerät {ecu}", ""]
        for e, target, note in items:
            lines.append(f"### {e['title_de']}  (`{e['id']}`)")
            lines.append("")
            lines.append(f"- **Risiko:** {LABELS_DE['risk'][e['risk']]} · **Kompatibilität:** "
                         f"{LABELS_DE['compatibility'][e['compatibility']]} · **Nachweis:** "
                         f"{LABELS_DE['evidence'][e['evidence']]}")
            if e["bimmercode_mode"] == "standard" and e.get("bimmercode_label"):
                lines.append(f"- **BimmerCode (Standard):** {ecu} → „{e['bimmercode_label']}“")
            elif e["function_names"]:
                path = f"{ecu} → {e.get('cafd_block') or '?'} → {', '.join(e['function_names'])}"
                lines.append(f"- **BimmerCode Expertenmodus:** {path}")
            else:
                lines.append("- **BimmerCode:** Pfad nicht dokumentiert – in der App suchen")
            if target:
                lines.append(f"- **Zielwert:** `{target}`")
            if e["values"]:
                lines.append("- **Mögliche Werte:** " + "; ".join(f"`{v['name']}` = {v['meaning_de']}" for v in e["values"]))
            if e.get("hardware_requirements_de"):
                lines.append(f"- **Hardware:** {e['hardware_requirements_de']}")
            if e.get("legal_note_de"):
                lines.append(f"- **Rechtlicher Hinweis:** {e['legal_note_de']}")
            if e["ecu"] in SAFETY_ECUS or e["risk"] == "safety_critical":
                lines.append("- ⚠️ **Sicherheitskritisch – von F20 Intelligence ausdrücklich NICHT empfohlen.**")
            if note:
                lines.append(f"- **Notiz:** {note}")
            lines.append("- **Quellen:** " + ", ".join(e["sources"][:4]))
            lines.append("")
    lines += ["## Danach", "",
              "- [ ] Neues Backup in BimmerCode erstellen und in F20 Intelligence importieren",
              "- [ ] Backup Center → Vergleich Vorher/Nachher prüfen; ggf. Lernmodus mit Optionsnamen ausführen",
              "- [ ] Funktion am Fahrzeug testen; Änderung im Änderungsprotokoll als „umgesetzt“ markieren", ""]
    return "\n".join(lines)
