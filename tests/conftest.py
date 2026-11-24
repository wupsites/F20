import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


@pytest.fixture(autouse=True)
def isolated_home(tmp_path, monkeypatch):
    """Jeder Test bekommt ein eigenes, leeres F20_HOME – echte Fahrzeugdaten werden nie berührt."""
    home = tmp_path / "f20home"
    monkeypatch.setenv("F20_HOME", str(home))
    yield home


@pytest.fixture
def demo_elm():
    from f20.sim import SimFaults, VirtualElm327, build_demo_car
    from f20.transport.elm327 import Elm327

    def make(**faults):
        car = build_demo_car()
        t = VirtualElm327(car, SimFaults(**faults))
        return car, t, Elm327(t)
    return make
