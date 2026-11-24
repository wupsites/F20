"""Adapter-Transporte: Simulator, BLE (bleak), Bluetooth Classic/USB (pyserial), WLAN (TCP)."""

from .base import ByteTransport
from .errors import (
    AdapterDisconnected,
    AdapterError,
    AdapterTimeout,
    AdapterUnsupported,
    BusError,
    NegativeResponse,
    NoData,
)

__all__ = [
    "ByteTransport",
    "AdapterDisconnected",
    "AdapterError",
    "AdapterTimeout",
    "AdapterUnsupported",
    "BusError",
    "NegativeResponse",
    "NoData",
]
