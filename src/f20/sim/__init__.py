"""Simulierte Testumgebung: virtueller ELM327-Adapter + virtueller F20.

ALLE Werte der Simulation sind fiktiv und als DEMO gekennzeichnet. Sie
dienen ausschließlich dem Testen der Software und dürfen niemals als
Fahrzeugdaten interpretiert werden.
"""

from .car import DEMO_VIN, VirtualCar, VirtualEcu, VirtualEngine, build_demo_car
from .elm import SimFaults, VirtualElm327

__all__ = [
    "DEMO_VIN",
    "VirtualCar",
    "VirtualEcu",
    "VirtualEngine",
    "build_demo_car",
    "SimFaults",
    "VirtualElm327",
]
