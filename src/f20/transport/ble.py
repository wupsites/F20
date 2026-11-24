"""Bluetooth-Low-Energy-Transport über ``bleak`` (macOS: CoreBluetooth).

ELM327-kompatible BLE-Adapter stellen einen „seriellen“ GATT-Dienst bereit:
eine Characteristic für Benachrichtigungen (Adapter → Mac) und eine zum
Schreiben (Mac → Adapter). Die bekannten UUID-Profile stehen in
:data:`KNOWN_UART_PROFILES` (Quellen: ADAPTER_COMPATIBILITY.md). Unbekannte
Adapter werden über eine generische Suche (Notify + Write im selben Dienst)
unterstützt.

macOS-Hinweise:
* Beim ersten Scan fragt macOS nach der Bluetooth-Berechtigung für das
  Terminal bzw. die Python-App (Systemeinstellungen → Datenschutz & Sicherheit
  → Bluetooth).
* macOS liefert keine MAC-Adressen, sondern pro Mac stabile UUIDs.
* Ein BLE-Adapter kann nur mit *einem* Gerät gleichzeitig verbunden sein –
  BimmerCode auf dem iPhone vorher schließen / Bluetooth am iPhone aus.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass

from .base import ByteTransport
from .errors import AdapterDisconnected, AdapterError


@dataclass(frozen=True)
class UartProfile:
    name: str
    service: str
    notify: str
    write: str
    evidence: str


def _u16(x: str) -> str:
    return f"0000{x.lower()}-0000-1000-8000-00805f9b34fb"


#: Bekannte GATT-UART-Profile. Nachweisstatus siehe ADAPTER_COMPATIBILITY.md.
KNOWN_UART_PROFILES: list[UartProfile] = [
    # documented: OBDLink-CX-Supportseite, EdiabasLib ("WgSoft")
    UartProfile("FFF0 (OBDLink CX, WgSoft u. a.)", _u16("fff0"), _u16("fff1"), _u16("fff2"), "documented"),
    # documented: EdiabasLib (Deep OBD) – Write auf FFE2
    UartProfile("FFE0 (Deep OBD)", _u16("ffe0"), _u16("ffe1"), _u16("ffe2"), "documented"),
    # documented: EdiabasLib (Carly) – Notify und Write auf derselben Characteristic
    UartProfile("FFE0 (Carly / HM-10-Stil)", _u16("ffe0"), _u16("ffe1"), _u16("ffe1"), "documented"),
    # documented: EdiabasLib (vLinker) – Notify/Write auf derselben Characteristic; Quellen teils widersprüchlich
    UartProfile("E7810A71 (vLinker)", "e7810a71-73ae-499d-8c15-faa9aef0c3f2",
                "bef8d6c9-9c21-4c9e-b632-bd58c1009f9f", "bef8d6c9-9c21-4c9e-b632-bd58c1009f9f", "documented"),
    # likely: ESPHome-Konfiguration mit (vermutlich) vLinker
    UartProfile("18F0 (diverse ELM-BLE)", _u16("18f0"), _u16("2af0"), _u16("2af1"), "likely"),
    # documented: Microchip-Dokumentation
    UartProfile("Microchip Transparent UART", "49535343-fe7d-4ae5-8fa9-9fafd205e455",
                "49535343-1e4d-4bd9-ba61-23c647249616", "49535343-8841-43f4-a8d4-ecbe34729bb3", "documented"),
    # likely: generisches Nordic-UART-Profil (nicht für OBD-Adapter belegt)
    UartProfile("Nordic UART Service", "6e400001-b5a3-f393-e0a9-e50e24dcca9e",
                "6e400003-b5a3-f393-e0a9-e50e24dcca9e", "6e400002-b5a3-f393-e0a9-e50e24dcca9e", "likely"),
]


def _require_bleak():
    try:
        import bleak  # noqa: F401
        return bleak
    except ImportError as exc:  # pragma: no cover - abhängig von Installation
        raise AdapterError("Paket 'bleak' fehlt: pip install 'f20-intelligence[ble]'") from exc


async def scan(timeout: float = 8.0) -> list[dict]:
    """Passiver BLE-Scan. Verbindet sich mit nichts und sendet nichts ans Fahrzeug."""
    bleak = _require_bleak()
    found = await bleak.BleakScanner.discover(timeout=timeout, return_adv=True)
    known = {p.service for p in KNOWN_UART_PROFILES}
    out = []
    for _addr, (dev, adv) in found.items():
        uuids = [u.lower() for u in (adv.service_uuids or [])]
        name = dev.name or adv.local_name or ""
        hint = any(u in known for u in uuids) or any(
            k in name.upper() for k in ("OBD", "ELM", "VLINK", "V-LINK", "VEEPEAK", "OBDLINK", "CARISTA", "UNICAR", "IOS-", "KONNWEI", "VGATE")
        )
        out.append({
            "id": dev.address, "name": name, "rssi": adv.rssi,
            "service_uuids": uuids, "obd_candidate": hint,
        })
    out.sort(key=lambda d: (not d["obd_candidate"], -(d["rssi"] or -999)))
    return out


class BleTransport(ByteTransport):
    name = "ble"

    def __init__(self, address: str, connect_timeout: float = 15.0) -> None:
        self.address = address
        self.connect_timeout = connect_timeout
        self._client = None
        self._queue: asyncio.Queue[bytes] = asyncio.Queue()
        self._write_uuid: str | None = None
        self._write_response = False
        self._profile: str | None = None
        self._chunk = 20
        self._disconnected = False

    def describe(self) -> dict:
        return {"transport": "ble", "address": self.address, "profile": self._profile,
                "write_chunk": self._chunk}

    @property
    def is_open(self) -> bool:
        return bool(self._client and self._client.is_connected and not self._disconnected)

    def _on_disconnect(self, _client) -> None:
        self._disconnected = True

    async def open(self) -> None:
        bleak = _require_bleak()
        self._client = bleak.BleakClient(self.address, disconnected_callback=self._on_disconnect,
                                         timeout=self.connect_timeout)
        await self._client.connect()
        self._disconnected = False
        notify_uuid, write_uuid, profile = self._select_characteristics()
        self._write_uuid, self._profile = write_uuid, profile
        char = self._client.services.get_characteristic(write_uuid)
        props = set(char.properties) if char else set()
        self._write_response = "write-without-response" not in props
        mtu = getattr(self._client, "mtu_size", 23) or 23
        self._chunk = max(20, min(180, mtu - 3))
        await self._client.start_notify(notify_uuid, self._on_notify)

    def _select_characteristics(self) -> tuple[str, str, str]:
        services = self._client.services
        for p in KNOWN_UART_PROFILES:
            svc = services.get_service(p.service)
            if svc and svc.get_characteristic(p.notify) and svc.get_characteristic(p.write):
                return p.notify, p.write, p.name
        # Generische Suche: Dienst mit Notify- und Write-Characteristic
        for svc in services:
            notify = [c for c in svc.characteristics if {"notify", "indicate"} & set(c.properties)]
            write = [c for c in svc.characteristics if {"write", "write-without-response"} & set(c.properties)]
            if notify and write:
                return notify[0].uuid, write[0].uuid, f"generisch ({svc.uuid})"
        raise AdapterError("Kein serieller GATT-Dienst gefunden – ist das ein ELM327-BLE-Adapter?")

    def _on_notify(self, _char, data: bytearray) -> None:
        self._queue.put_nowait(bytes(data))

    async def write(self, data: bytes) -> None:
        if not self.is_open:
            raise AdapterDisconnected("BLE-Verbindung getrennt")
        for i in range(0, len(data), self._chunk):
            await self._client.write_gatt_char(self._write_uuid, data[i:i + self._chunk],
                                               response=self._write_response)

    async def read(self, timeout: float) -> bytes:
        if self._disconnected:
            raise AdapterDisconnected("BLE-Verbindung getrennt")
        try:
            first = await asyncio.wait_for(self._queue.get(), timeout)
        except asyncio.TimeoutError:
            if self._disconnected:
                raise AdapterDisconnected("BLE-Verbindung getrennt") from None
            return b""
        chunks = [first]
        while not self._queue.empty():
            chunks.append(self._queue.get_nowait())
        return b"".join(chunks)

    async def close(self) -> None:
        if self._client is not None:
            try:
                await self._client.disconnect()
            finally:
                self._client = None
