"""Read-only-Schutz (Positivliste).

Prinzipien
==========
1. Es existiert im gesamten Projekt kein Code-Pfad, der Schreib-, Lösch-,
   Reset-, Routine-, Security-Access- oder Flash-Dienste erzeugt.
2. Zusätzlich prüft diese Richtlinie *jede* ausgehende Nachricht – auch
   Rohdaten, die über Hex-Eingaben im Expertenmodus entstehen könnten –
   gegen eine Positivliste. Alles, was nicht explizit erlaubt ist, wird
   blockiert (Default-Deny).
3. Die Richtlinie kennt keinen Schalter „Schreiben erlauben“. Eine spätere
   Schreibfunktion erfordert eine separate, begutachtete Codeänderung
   (siehe SECURITY.md, Abschnitt „Voraussetzungen für Schreibzugriffe“).

Diese Datei ist sicherheitskritisch. Änderungen nur mit Tests
(tests/test_safety_policy.py) und Eintrag in CHANGELOG.md.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field


class ReadOnlyViolation(PermissionError):
    """Eine Nachricht hätte das Fahrzeug oder den Adapter verändern können."""


# --- UDS (ISO 14229-1) -------------------------------------------------------

#: Erlaubte UDS-Dienste mit erlaubten Subfunktionen (None = Dienst ohne Subfunktion).
UDS_ALLOWED: dict[int, tuple[str, frozenset[int] | None]] = {
    # DiagnosticSessionControl – nur Default Session (0x01). Keine Extended-,
    # Programming- oder Coding-Session.
    0x10: ("DiagnosticSessionControl (nur Default Session)", frozenset({0x01})),
    # ReadDTCInformation – ausschließlich lesende Subfunktionen
    0x19: (
        "ReadDTCInformation",
        frozenset({
            0x01,  # reportNumberOfDTCByStatusMask
            0x02,  # reportDTCByStatusMask
            0x03,  # reportDTCSnapshotIdentification
            0x04,  # reportDTCSnapshotRecordByDTCNumber
            0x06,  # reportDTCExtDataRecordByDTCNumber
            0x0A,  # reportSupportedDTC
        }),
    ),
    # ReadDataByIdentifier – liest Datenkennungen (DIDs)
    0x22: ("ReadDataByIdentifier", None),
    # TesterPresent – nur zeroSubFunction (0x00) bzw. mit suppressPosRsp (0x80)
    0x3E: ("TesterPresent", frozenset({0x00, 0x80})),
}

#: Explizit verbotene Dienste (zur Dokumentation und für klare Fehlermeldungen).
UDS_FORBIDDEN: dict[int, str] = {
    0x11: "ECUReset – setzt Steuergeräte zurück",
    0x14: "ClearDiagnosticInformation – löscht Fehlerspeicher",
    0x23: "ReadMemoryByAddress – unkontrollierter Speicherzugriff (v1 gesperrt)",
    0x24: "ReadScalingDataByIdentifier",
    0x27: "SecurityAccess – Entsperren geschützter Funktionen",
    0x28: "CommunicationControl – kann Buskommunikation abschalten",
    0x29: "Authentication",
    0x2A: "ReadDataByPeriodicIdentifier",
    0x2C: "DynamicallyDefineDataIdentifier – verändert ECU-Zustand",
    0x2E: "WriteDataByIdentifier – SCHREIBT Daten (Codierung)",
    0x2F: "InputOutputControlByIdentifier – steuert Aktoren",
    0x31: "RoutineControl – startet Routinen (Codierung, Prüfsummen, Löschen)",
    0x34: "RequestDownload – Flashen",
    0x35: "RequestUpload",
    0x36: "TransferData – Flashen",
    0x37: "RequestTransferExit – Flashen",
    0x38: "RequestFileTransfer",
    0x3D: "WriteMemoryByAddress – SCHREIBT Speicher",
    0x83: "AccessTimingParameter",
    0x84: "SecuredDataTransmission",
    0x85: "ControlDTCSetting – schaltet Fehlerspeicherung ab",
    0x86: "ResponseOnEvent",
    0x87: "LinkControl – ändert Baudrate",
}

# --- OBD-II (SAE J1979 / ISO 15031-5) ---------------------------------------

#: Erlaubte OBD-Modi (alle rein lesend).
OBD_ALLOWED_MODES: dict[int, str] = {
    0x01: "Aktuelle Daten",
    0x02: "Freeze-Frame-Daten",
    0x03: "Gespeicherte abgasrelevante Fehlercodes",
    0x06: "Testergebnisse On-Board-Monitoring",
    0x07: "Unbestätigte (pending) Fehlercodes",
    0x09: "Fahrzeuginformationen (VIN, CALID, CVN)",
    0x0A: "Permanente Fehlercodes",
}

OBD_FORBIDDEN_MODES: dict[int, str] = {
    0x04: "Fehlerspeicher löschen / MIL zurücksetzen",
    0x05: "O2-Sensor-Tests (nicht CAN) – nicht benötigt",
    0x08: "Steuerung von On-Board-Systemen (Aktortests)",
}

# --- ELM327 / STN AT-Befehle -------------------------------------------------
# Nur flüchtige Konfigurationsbefehle und lesende Abfragen. Ausgeschlossen sind
# insbesondere Befehle, die das EEPROM des Adapters beschreiben (AT PP …,
# AT @3, AT M1), die Baudrate ändern (AT BRD/BRT) oder Bus-Monitoring
# mit unbegrenzter Ausgabe starten.
_AT_ALLOWED_PATTERNS: tuple[tuple[str, str], ...] = (
    (r"Z", "Reset (flüchtig)"),
    (r"WS", "Warmstart"),
    (r"D", "Defaults (flüchtig)"),
    (r"I", "Versionskennung lesen"),
    (r"@1", "Gerätebeschreibung lesen"),
    (r"@2", "Geräte-ID lesen"),
    (r"RV", "Bordspannung am OBD-Stecker lesen"),
    (r"DPN?", "Aktuelles Protokoll lesen"),
    (r"E[01]", "Echo"),
    (r"L[01]", "Zeilenvorschub"),
    (r"S[01]", "Leerzeichen"),
    (r"H[01]", "Header anzeigen"),
    (r"AL", "Lange Nachrichten erlauben"),
    (r"NL", "Normale Nachrichtenlänge"),
    (r"SP[0-9A-C]", "Protokoll setzen (flüchtig)"),
    (r"SPA[0-9A-C]", "Protokoll setzen mit Auto-Fallback (flüchtig)"),
    (r"TP[0-9A-C]", "Protokoll versuchen"),
    (r"TPA[0-9A-C]", "Protokoll versuchen mit Auto-Fallback"),
    (r"SH[0-9A-F]{3}", "CAN-Header (11 Bit)"),
    (r"SH[0-9A-F]{6}", "Header (3 Byte)"),
    (r"SH[0-9A-F]{8}", "CAN-Header (29 Bit)"),
    (r"CEA([0-9A-F]{2})?", "CAN Extended Address setzen/aus"),
    (r"CER[0-9A-F]{2}", "CAN Extended Rx Address (STN/neuere ELM)"),
    (r"CRA([0-9A-FX]{3}|[0-9A-FX]{8})?", "CAN-Empfangsfilter"),
    (r"CF[0-9A-F]{3}", "CAN-ID-Filter"),
    (r"CM[0-9A-F]{3}", "CAN-ID-Maske"),
    (r"CAF[01]", "CAN Auto-Formatierung"),
    (r"CFC[01]", "CAN Flow Control an/aus"),
    (r"FCSH[0-9A-F]{3}", "Flow-Control-Header"),
    (r"FCSD([0-9A-F]{2}){1,5}", "Flow-Control-Daten"),
    (r"FCSM[0-2]", "Flow-Control-Modus"),
    (r"AT[0-2]", "Adaptives Timing"),
    (r"ST[0-9A-F]{2}", "Timeout"),
    (r"R[01]", "Antworten an/aus"),
    (r"CS", "CAN-Status lesen"),
    (r"PC", "Protokoll schließen"),
    (r"D[01]", "DLC anzeigen"),
)

_STN_ALLOWED_PATTERNS: tuple[tuple[str, str], ...] = (
    (r"I", "STN-Identifikation"),
    (r"DI", "STN-Hardware-ID"),
    (r"SN", "STN-Seriennummer"),
)

_AT_RE = [(re.compile(rf"^{p}$"), d) for p, d in _AT_ALLOWED_PATTERNS]
_STN_RE = [(re.compile(rf"^{p}$"), d) for p, d in _STN_ALLOWED_PATTERNS]


def _normalize_cmd(cmd: str) -> str:
    return re.sub(r"\s+", "", cmd).upper()


@dataclass
class PolicyDecision:
    allowed: bool
    reason: str


@dataclass
class ReadOnlyPolicy:
    """Prüft jede ausgehende Nachricht. Es gibt bewusst keinen Write-Modus."""

    #: Lesen der Codierdaten-DIDs (0x3000–0x3FFF) erlauben. Lesen verändert
    #: nichts, wird aber separat freigeschaltet, weil es große Antworten erzeugt.
    allow_coding_read: bool = True
    #: Maximale Länge einer UDS-Anfrage in Byte (Lese-Anfragen sind kurz).
    max_request_len: int = 8
    audit: list[tuple[str, str, bool, str]] = field(default_factory=list)

    # -- AT ---------------------------------------------------------------
    def check_at(self, cmd: str) -> str:
        """Gibt den normalisierten Befehl zurück oder wirft ReadOnlyViolation."""
        c = _normalize_cmd(cmd)
        if c.startswith("AT"):
            body, table = c[2:], _AT_RE
        elif c.startswith("ST"):
            body, table = c[2:], _STN_RE
        else:
            self._log("AT", c, False, "kein AT/ST-Befehl")
            raise ReadOnlyViolation(f"Kein gültiger Adapterbefehl: {cmd!r}")
        for rx, desc in table:
            if rx.match(body):
                self._log("AT", c, True, desc)
                return c
        self._log("AT", c, False, "nicht auf Positivliste")
        raise ReadOnlyViolation(
            f"Adapterbefehl {c!r} ist nicht auf der Positivliste "
            "(mögliche EEPROM-/Baudraten-/Monitor-Änderung)."
        )

    # -- UDS --------------------------------------------------------------
    def check_uds(self, payload: bytes, target: int | None = None) -> PolicyDecision:
        tgt = f"ECU 0x{target:02X}" if target is not None else "ECU ?"
        if not payload:
            return self._deny("UDS", payload, "leere Anfrage")
        if len(payload) > self.max_request_len:
            return self._deny("UDS", payload, f"Anfrage zu lang ({len(payload)} Byte) für Lesedienste")
        sid = payload[0]
        if sid in UDS_FORBIDDEN:
            return self._deny("UDS", payload, f"Dienst 0x{sid:02X} verboten: {UDS_FORBIDDEN[sid]} ({tgt})")
        if sid not in UDS_ALLOWED:
            return self._deny("UDS", payload, f"Dienst 0x{sid:02X} nicht auf Positivliste ({tgt})")
        name, subs = UDS_ALLOWED[sid]
        if subs is not None:
            if len(payload) < 2:
                return self._deny("UDS", payload, f"{name}: Subfunktion fehlt")
            if payload[1] not in subs:
                return self._deny("UDS", payload, f"{name}: Subfunktion 0x{payload[1]:02X} nicht erlaubt")
        if sid == 0x22:
            if len(payload) != 3:
                return self._deny("UDS", payload, "ReadDataByIdentifier: genau eine DID pro Anfrage erlaubt")
            did = (payload[1] << 8) | payload[2]
            if 0x3000 <= did <= 0x3FFF and not self.allow_coding_read:
                return self._deny("UDS", payload, f"Lesen der Codier-DID 0x{did:04X} nicht freigegeben")
        return self._allow("UDS", payload, f"{name} → {tgt}")

    def enforce_uds(self, payload: bytes, target: int | None = None) -> None:
        d = self.check_uds(payload, target)
        if not d.allowed:
            raise ReadOnlyViolation(d.reason)

    # -- OBD --------------------------------------------------------------
    def check_obd(self, payload: bytes) -> PolicyDecision:
        if not payload:
            return self._deny("OBD", payload, "leere Anfrage")
        if len(payload) > 7:
            return self._deny("OBD", payload, "Anfrage zu lang")
        mode = payload[0]
        if mode in OBD_FORBIDDEN_MODES:
            return self._deny("OBD", payload, f"OBD-Modus 0x{mode:02X} verboten: {OBD_FORBIDDEN_MODES[mode]}")
        if mode not in OBD_ALLOWED_MODES:
            return self._deny("OBD", payload, f"OBD-Modus 0x{mode:02X} nicht auf Positivliste")
        return self._allow("OBD", payload, OBD_ALLOWED_MODES[mode])

    def enforce_obd(self, payload: bytes) -> None:
        d = self.check_obd(payload)
        if not d.allowed:
            raise ReadOnlyViolation(d.reason)

    # -- intern -----------------------------------------------------------
    def _allow(self, kind: str, payload: bytes, reason: str) -> PolicyDecision:
        self._log(kind, payload.hex().upper(), True, reason)
        return PolicyDecision(True, reason)

    def _deny(self, kind: str, payload: bytes, reason: str) -> PolicyDecision:
        self._log(kind, payload.hex().upper(), False, reason)
        return PolicyDecision(False, reason)

    def _log(self, kind: str, msg: str, ok: bool, reason: str) -> None:
        self.audit.append((kind, msg, ok, reason))
        if len(self.audit) > 5000:
            del self.audit[:1000]


DEFAULT_POLICY = ReadOnlyPolicy()
