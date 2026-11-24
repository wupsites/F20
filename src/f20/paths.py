"""Lokale Datenablage. Fahrzeugdaten verlassen den Rechner nicht."""

from __future__ import annotations

import os
import sys
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
DATA_DIR = PACKAGE_DIR / "data"          # mitgelieferte, öffentliche Wissensdaten
STATIC_DIR = PACKAGE_DIR / "web" / "static"


def f20_home() -> Path:
    """Privates Datenverzeichnis (Backups, Datenbank, Arbeitskopien).

    Reihenfolge: $F20_HOME → macOS Application Support → XDG data home.
    """
    env = os.environ.get("F20_HOME")
    if env:
        p = Path(env).expanduser()
    elif sys.platform == "darwin":
        p = Path.home() / "Library" / "Application Support" / "F20 Intelligence"
    else:
        base = os.environ.get("XDG_DATA_HOME") or str(Path.home() / ".local" / "share")
        p = Path(base) / "f20-intelligence"
    p.mkdir(parents=True, exist_ok=True)
    try:
        os.chmod(p, 0o700)
    except OSError:
        pass
    return p


def vault_dir() -> Path:
    p = f20_home() / "vault" / "originals"
    p.mkdir(parents=True, exist_ok=True)
    return p


def workcopy_dir() -> Path:
    p = f20_home() / "workcopies"
    p.mkdir(parents=True, exist_ok=True)
    return p


def db_path() -> Path:
    return f20_home() / "f20.sqlite3"


def logs_dir() -> Path:
    p = f20_home() / "logs"
    p.mkdir(parents=True, exist_ok=True)
    return p
