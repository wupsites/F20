"""Byte-Transport-Schnittstelle (BLE, Bluetooth Classic, WLAN, Simulator)."""

from __future__ import annotations

import abc


class ByteTransport(abc.ABC):
    """Asynchroner, bidirektionaler Byte-Kanal zum OBD-Adapter."""

    name: str = "transport"

    @abc.abstractmethod
    async def open(self) -> None: ...

    @abc.abstractmethod
    async def close(self) -> None: ...

    @abc.abstractmethod
    async def write(self, data: bytes) -> None: ...

    @abc.abstractmethod
    async def read(self, timeout: float) -> bytes:
        """Liefert verfügbare Bytes; b'' bei Timeout. Wirft AdapterDisconnected."""

    @property
    @abc.abstractmethod
    def is_open(self) -> bool: ...

    def describe(self) -> dict:
        return {"transport": self.name}
