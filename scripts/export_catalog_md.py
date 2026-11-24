#!/usr/bin/env python3
"""Erzeugt CODING_DATABASE.md (individueller Codierungskatalog) aus src/f20/data/catalog/*.json.

Aufruf: python scripts/export_catalog_md.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from f20.coding.catalog import LABELS_DE, SAFETY_ECUS, Catalog  # noqa: E402

#: In Deutschland unzulässig (Begründung jeweils im legal_note_de des Eintrags).
NOT_ALLOWED_DE = {
    "fem_body.us_sidemarkers", "fem_body.fog_with_parking_lights", "fem_body.ess_activation_speed",
    "fem_body.ess_activation_decel", "rem.ess_flash_frequency", "hu_entry.video_in_motion",
    "hu_entry.video_usb_codecs", "kombi.speed_correction",
}
#: Rechtliche Grauzone bzw. nur mit Vorsicht.
GREY = {
    "fem_body.msa_default_off", "fem_body.msa_memory", "fem_body.msa_eco_pro", "fem_body.drl_mode",
    "fem_body.drl_brightness", "hu_entry.drl_menu", "hu_entry.drl_checkbox", "fem_body.cornering_light_via_fog",
    "fem_body.cornering_fog_reverse", "fem_body.lamp_monitoring_front", "rem.lamp_monitoring_rear",
    "fem_body.parking_light_brightness", "fem_body.fog_off_with_high_beam", "fem_body.comfort_close_remote",
    "rem.drl_tail_lights", "fem_body.welcome_light_fog", "hu_entry.speedlock_office_service_messages",
    "hu_entry.full_text_messages",
}
#: Informations-/Werkstattthemen (keine Codieroption im engeren Sinn).
INFO = {"hu_entry.istufe_update_cid_no_signal", "hu_entry.fsc_enable_codes",
        "fem_body.battery_type", "dme.live_data"} | {"hu_entry.platform_identification", "kombi.test_functions"}

SECTIONS = [
    ("recommended", "1. Empfehlenswert – risikoarm, dokumentiert, wahrscheinlich kompatibel",
     "Diese Optionen sind in Quellen belegt, passen mit hoher Wahrscheinlichkeit zu deinem F20 (01/2012, HU_ENTRY, "
     "Schaltgetriebe) und sind nach aktuellem Recherchestand rechtlich unproblematisch. **Nicht am Fahrzeug getestet.**"),
    ("grey", "2. Möglich, aber rechtliche Grauzone oder mit Vorsicht", "Technisch wahrscheinlich möglich; die Einordnung "
     "nach StVO/StVZO/ECE-R48 ist unklar oder an Bedingungen geknüpft. Rechtshinweis jeweils beachten."),
    ("check", "3. Unklar – erst am Fahrzeug bzw. im BimmerCode-Expertenmodus prüfen", "Kompatibilität unbekannt "
     "oder Verfahren experimentell. Vor einer Planung: Steuergerätevariante/CAFD aus Backup bzw. Diagnose bestätigen."),
    ("info", "4. Informations- und Werkstattthemen (lesend / keine Komfortcodierung)", ""),
    ("safety", "5. Nur Dokumentation – sicherheits- oder emissionskritisch (NICHT codieren)", "Diese Einträge betreffen "
     "Airbag, Bremslicht-/Notbremssignal, Fahrdynamik (ICM/DSC), Lenkung, Motorsteuerung oder Startsperre. "
     "Sie werden nur zur Vollständigkeit dokumentiert. F20 Intelligence empfiehlt ausdrücklich keine Änderung."),
    ("illegal", "6. In Deutschland nicht zulässig", "Technisch teils möglich, aber nach deutscher bzw. europäischer "
     "Rechtslage unzulässig (Begründung je Eintrag)."),
    ("no", "7. Nicht möglich bei diesem Fahrzeug (fehlende Hardware / HU_ENTRY)", ""),
]


def classify(e: dict) -> str:
    if e["id"] in NOT_ALLOWED_DE:
        return "illegal"
    if e["ecu"] in SAFETY_ECUS and e["id"] not in INFO or e["risk"] == "safety_critical":
        return "safety"
    if e["compatibility"] in ("no", "unlikely") or e["evidence"] == "incompatible":
        return "no"
    if e["id"] in INFO:
        return "info"
    if e["id"] in GREY:
        return "grey"
    if e["compatibility"] in ("yes", "likely") and e["evidence"] in ("verified", "documented") \
            and e["risk"] in ("low", "medium"):
        return "recommended"
    return "check"


def esc(s: str | None) -> str:
    return (s or "").replace("|", "\\|").replace("\n", " ").strip()


def params(e: dict) -> str:
    p = ", ".join(f"`{n}`" for n in e["function_names"]) or "–"
    if e.get("cafd_block"):
        p += f" ({esc(e['cafd_block'])})"
    return p


def values(e: dict) -> str:
    return "; ".join(f"`{esc(v['name'])}` {esc(v['meaning_de'])}" for v in e["values"][:4]) or "–"


def main() -> int:
    cat = Catalog.load()
    groups: dict[str, list[dict]] = {k: [] for k, _, _ in SECTIONS}
    for e in cat.entries:
        groups[classify(e)].append(e)
    L = LABELS_DE
    out = [
        "# CODING_DATABASE – Individueller Codierungskatalog BMW 116i F20 (01/2012)", "",
        "> Automatisch erzeugt aus `src/f20/data/catalog/*.json` (Quelle: `docs/research/raw/0[45]_*.json`) "
        "mit `python scripts/export_catalog_md.py`. Nicht von Hand bearbeiten.", "",
        "**Fahrzeug:** BMW 116i F20, Produktion 24.01.2012, N13 (MEVD17.2.5), Schaltgetriebe, Radio Professional "
        "(HU_ENTRY), MFL, Sitzheizung vorn, PDC hinten (im REM), Nebelscheinwerfer, Regen-/Lichtsensor.", "",
        "**Wichtig:** Kein Eintrag ist am eigenen Fahrzeug getestet. Höchster Nachweisstatus ist "
        "„Dokumentiert“. Erst nach Umsetzung in BimmerCode + Vorher/Nachher-Backup wird ein Eintrag zu "
        "„Nachgewiesen“. Es wurden keine Funktionen oder Parameter erfunden – fehlt ein Beleg, steht „Unbekannt“.", "",
        "## Übersicht", "",
        "| Bereich | Anzahl |", "|---|---|",
    ]
    for key, title, _ in SECTIONS:
        out.append(f"| {title.split(' – ')[0] if ' – ' in title else title} | {len(groups[key])} |")
    out += [f"| **Gesamt** | **{len(cat.entries)}** |", "",
            "Legende: **BC** = BimmerCode (Standard = normale Oberfläche, Expert = Expertenmodus). "
            "Risiko/Kompatibilität/Nachweis wie in RESEARCH.md definiert.", ""]
    for key, title, intro in SECTIONS:
        items = sorted(groups[key], key=lambda e: (-e["score"], e["ecu"], e["id"]))
        out += [f"## {title}", ""]
        if intro:
            out += [intro, ""]
        if not items:
            out += ["_Keine Einträge._", ""]
            continue
        out += ["| Funktion | SG | Parameter (Block) | Werte | BC | Risiko | Kompat. | Nachweis |",
                "|---|---|---|---|---|---|---|---|"]
        for e in items:
            out.append(
                f"| [{esc(e['title_de'])}](#{e['id'].replace('.', '')}) | {e['ecu']} | {params(e)} | {values(e)} | "
                f"{e['bimmercode_mode']} | {L['risk'][e['risk']]} | {L['compatibility'][e['compatibility']]} | "
                f"{L['evidence'][e['evidence']].split(' (')[0]} |")
        out.append("")
    out += ["---", "", "## Details und Quellen", ""]
    for key, title, _ in SECTIONS:
        for e in sorted(groups[key], key=lambda e: (e["ecu"], e["id"])):
            out += [f"### {esc(e['title_de'])}", "", f"<a id=\"{e['id'].replace('.', '')}\"></a>`{e['id']}` · "
                    f"Bereich: {title.split('.')[0]} · SG **{e['ecu']}** · Kategorie {L['category'][e['category']]}", ""]
            out.append(esc(e["description_de"]))
            out.append("")
            if e.get("bimmercode_label"):
                out.append(f"- **BimmerCode:** {esc(e['bimmercode_label'])} ({e['bimmercode_mode']})")
            out.append(f"- **Parameter:** {params(e)}")
            if e["values"]:
                out.append("- **Werte:** " + "; ".join(f"`{esc(v['name'])}` = {esc(v['meaning_de'])}" for v in e["values"]))
            out.append(f"- **Hardware:** {esc(e['hardware_requirements_de']) or '–'}")
            out.append(f"- **Software:** {esc(e['software_requirements_de']) or '–'}")
            out.append(f"- **Aufwand / Risiko / Nutzen:** {L['effort'][e['effort']]} / {L['risk'][e['risk']]} / "
                       f"{L['benefit'][e['benefit']]}")
            out.append(f"- **Kompatibilität (dein F20):** {L['compatibility'][e['compatibility']]} · "
                       f"**Nachweis:** {L['evidence'][e['evidence']]}")
            if e.get("legal_note_de"):
                out.append(f"- **Recht:** {esc(e['legal_note_de'])}")
            if e.get("notes_de"):
                out.append(f"- **Hinweise:** {esc(e['notes_de'])}")
            if e["sources"]:
                out.append("- **Quellen:** " + " · ".join(f"<{s}>" for s in e["sources"][:5]))
            out.append("")
    (ROOT / "CODING_DATABASE.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print({k: len(v) for k, v in groups.items()})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
