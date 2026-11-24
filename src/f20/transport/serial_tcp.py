"""Serielle (Bluetooth Classic SPP / USB) und TCP-Transporte (WLAN-Adapter)."""

from __future__ import annotations

import asyncio
import glob
import sys

from .base import ByteTransport
from .errors import AdapterDisconnected, AdapterError


def list_serial_candidates() -> list[str]:
    """Mögliche serielle Adapter. macOS: /dev/cu.* (nach Kopplung in den Systemeinstellungen)."""
    if sys.platform == "darwin":
        pats = ["/dev/cu.*"]
    else:
        pats = ["/dev/rfcomm*", "/dev/ttyUSB*", "/dev/ttyACM*"]
    out: list[str] = []
    for p in pats:
        out += sorted(glob.glob(p))
    return [p for p in out if "Bluetooth-Incoming-Port" not in p and "debug-console" not in p]


class SerialTransport(ByteTransport):
    name = "serial"

    def __init__(self, port: str, baudrate: int = 38400) -> None:
        self.port = port
        self.baudrate = baudrate
        self._ser = None

    def describe(self) -> dict:
        return {"transport": "serial", "port": self.port, "baudrate": self.baudrate}

    @property
    def is_open(self) -> bool:
        return bool(self._ser and self._ser.is_open)

    async def open(self) -> None:
        try:
            import serial  # type: ignore
        except ImportError as exc:  # pragma: no cover
            raise AdapterError("Paket 'pyserial' fehlt: pip install 'f20-intelligence[serial]'") from exc
        self._ser = await asyncio.to_thread(serial.Serial, self.port, self.baudrate, timeout=0)

    async def write(self, data: bytes) -> None:
        if not self.is_open:
            raise AdapterDisconnected("Serielle Verbindung geschlossen")
        try:
            await asyncio.to_thread(self._ser.write, data)
        except OSError as exc:
            raise AdapterDisconnected(str(exc)) from exc

    async def read(self, timeout: float) -> bytes:
        if not self.is_open:
            raise AdapterDisconnected("Serielle Verbindung geschlossen")
        loop = asyncio.get_running_loop()
        end = loop.time() + timeout
        while True:
            try:
                n = self._ser.in_waiting
                if n:
                    return await asyncio.to_thread(self._ser.read, n)
            except OSError as exc:
                raise AdapterDisconnected(str(exc)) from exc
            if loop.time() >= end:
                return b""
            await asyncio.sleep(0.01)

    async def close(self) -> None:
        if self._ser is not None:
            await asyncio.to_thread(self._ser.close)
            self._ser = None


class TcpTransport(ByteTransport):
    """WLAN-ELM327 (typisch 192.168.0.10:35000)."""

    name = "tcp"

    def __init__(self, host: str = "192.168.0.10", port: int = 35000) -> None:
        self.host, self.port = host, port
        self._r: asyncio.StreamReader | None = None
        self._w: asyncio.StreamWriter | None = None

    def describe(self) -> dict:
        return {"transport": "tcp", "host": self.host, "port": self.port}

    @property
    def is_open(self) -> bool:
        return self._w is not None and not self._w.is_closing()

    async def open(self) -> None:
        self._r, self._w = await asyncio.wait_for(asyncio.open_connection(self.host, self.port), 10)

    async def write(self, data: bytes) -> None:
        if not self.is_open:
            raise AdapterDisconnected("TCP-Verbindung geschlossen")
        self._w.write(data)
        await self._w.drain()

    async def read(self, timeout: float) -> bytes:
        if not self.is_open:
            raise AdapterDisconnected("TCP-Verbindung geschlossen")
        try:
            data = await asyncio.wait_for(self._r.read(4096), timeout)
        except asyncio.TimeoutError:
            return b""
        if data == b"":
            raise AdapterDisconnected("TCP-Gegenstelle hat geschlossen")
        return data

    async def close(self) -> None:
        if self._w is not None:
            self._w.close()
            self._w = None
