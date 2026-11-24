"""Nachweisstufen – jede Aussage im Projekt trägt genau eine davon.

Die Stufen entsprechen der Vorgabe des Projektauftrags (Abschnitt 10).
"""

from __future__ import annotations

from enum import Enum


class Evidence(str, Enum):
    VERIFIED = "verified"          # 1. Nachgewiesen (am eigenen Fahrzeug / in eigenen Backups)
    DOCUMENTED = "documented"      # 2. Dokumentiert, aber nicht am Fahrzeug getestet
    LIKELY = "likely"              # 3. Technisch wahrscheinlich
    EXPERIMENTAL = "experimental"  # 4. Experimentell
    INCOMPATIBLE = "incompatible"  # 5. Nicht kompatibel
    UNKNOWN = "unknown"            # 6. Unbekannt

    @property
    def label_de(self) -> str:
        return _LABELS_DE[self]

    @property
    def rank(self) -> int:
        """Kleiner = belastbarer."""
        return _ORDER.index(self)


_ORDER = [
    Evidence.VERIFIED,
    Evidence.DOCUMENTED,
    Evidence.LIKELY,
    Evidence.EXPERIMENTAL,
    Evidence.INCOMPATIBLE,
    Evidence.UNKNOWN,
]

_LABELS_DE = {
    Evidence.VERIFIED: "Nachgewiesen",
    Evidence.DOCUMENTED: "Dokumentiert, nicht am Fahrzeug getestet",
    Evidence.LIKELY: "Technisch wahrscheinlich",
    Evidence.EXPERIMENTAL: "Experimentell",
    Evidence.INCOMPATIBLE: "Nicht kompatibel",
    Evidence.UNKNOWN: "Unbekannt",
}


def parse_evidence(value: str | Evidence | None) -> Evidence:
    if isinstance(value, Evidence):
        return value
    if not value:
        return Evidence.UNKNOWN
    v = value.strip().lower()
    aliases = {
        "nachgewiesen": Evidence.VERIFIED,
        "dok": Evidence.DOCUMENTED,
        "dokumentiert": Evidence.DOCUMENTED,
        "wahrscheinlich": Evidence.LIKELY,
        "experimentell": Evidence.EXPERIMENTAL,
        "nicht kompatibel": Evidence.INCOMPATIBLE,
        "nicht_kompatibel": Evidence.INCOMPATIBLE,
        "unbekannt": Evidence.UNKNOWN,
    }
    if v in aliases:
        return aliases[v]
    try:
        return Evidence(v)
    except ValueError:
        return Evidence.UNKNOWN
