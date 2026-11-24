"""Fehlerklassen der Adapterkommunikation."""

from __future__ import annotations


class AdapterError(Exception):
    """Basisklasse für Adapterfehler."""


class AdapterTimeout(AdapterError):
    """Adapter hat nicht rechtzeitig mit dem Prompt '>' geantwortet."""


class AdapterDisconnected(AdapterError):
    """Verbindung zum Adapter verloren (BLE getrennt, Port geschlossen …)."""


class AdapterUnsupported(AdapterError):
    """Adapter kennt den Befehl nicht ('?') – z. B. alter ELM327-Klon."""


class NoData(AdapterError):
    """Keine Antwort vom Fahrzeug ('NO DATA')."""


class BusError(AdapterError):
    """CAN-/Busfehler laut Adapter (CAN ERROR, BUS ERROR, BUFFER FULL …)."""


class NegativeResponse(AdapterError):
    """UDS-Negativantwort 0x7F."""

    def __init__(self, service: int, nrc: int, text: str):
        self.service = service
        self.nrc = nrc
        super().__init__(f"Negativantwort auf 0x{service:02X}: NRC 0x{nrc:02X} ({text})")
