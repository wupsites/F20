"""Integrität & Tresor für Original-Backups.

* Originaldateien werden ausschließlich lesend geöffnet ('rb').
* Beim Import wird eine Kopie im Tresor ($F20_HOME/vault/originals) abgelegt,
  benannt nach ihrer SHA-256-Prüfsumme und schreibgeschützt (0444).
* Jede Analyse arbeitet auf der Tresorkopie und prüft vorher die Prüfsumme.
* Veränderungen (Hex-Editor, virtuelle Codierung) erfolgen nur in separaten
  Arbeitskopien ($F20_HOME/workcopies).
"""

from __future__ import annotations

import hashlib
import os
import shutil
import stat
from dataclasses import dataclass
from pathlib import Path

from ..paths import vault_dir, workcopy_dir


class IntegrityError(RuntimeError):
    pass


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path | str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


@dataclass
class VaultEntry:
    sha256: str
    path: Path
    size: int
    original_name: str
    source_path: str
    source_mtime: float


class Vault:
    def __init__(self, root: Path | None = None) -> None:
        self.root = Path(root) if root else vault_dir()
        self.root.mkdir(parents=True, exist_ok=True)

    def import_file(self, src: Path | str) -> VaultEntry:
        src = Path(src)
        st_before = src.stat()
        data = src.read_bytes()                 # nur lesend
        digest = sha256_bytes(data)
        suffix = src.suffix.lower() or ".bin"
        dest = self.root / f"{digest}{suffix}"
        if not dest.exists():
            tmp = dest.with_suffix(dest.suffix + ".tmp")
            tmp.write_bytes(data)
            os.chmod(tmp, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
            tmp.replace(dest)
        if sha256_file(dest) != digest:
            raise IntegrityError(f"Tresorkopie von {src.name} ist beschädigt")
        st_after = src.stat()
        if st_after.st_mtime != st_before.st_mtime or st_after.st_size != st_before.st_size:
            raise IntegrityError(f"Originaldatei {src} wurde während des Imports verändert")
        return VaultEntry(digest, dest, len(data), src.name, str(src.resolve()), st_before.st_mtime)

    def import_bytes(self, name: str, data: bytes) -> VaultEntry:
        digest = sha256_bytes(data)
        suffix = Path(name).suffix.lower() or ".bin"
        dest = self.root / f"{digest}{suffix}"
        if not dest.exists():
            tmp = dest.with_suffix(dest.suffix + ".tmp")
            tmp.write_bytes(data)
            os.chmod(tmp, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
            tmp.replace(dest)
        return VaultEntry(digest, dest, len(data), Path(name).name, "(Upload)", 0.0)

    @staticmethod
    def read_verified(path: Path | str, expected_sha256: str) -> bytes:
        data = Path(path).read_bytes()
        actual = sha256_bytes(data)
        if actual != expected_sha256:
            raise IntegrityError(f"Prüfsumme stimmt nicht: {path} (erwartet {expected_sha256[:12]}…, ist {actual[:12]}…)")
        return data

    def verify(self, entries: list[dict]) -> list[dict]:
        report = []
        for e in entries:
            p = Path(e["vault_path"])
            if not p.exists():
                report.append({"id": e["id"], "name": e["original_name"], "ok": False, "reason": "Tresordatei fehlt"})
                continue
            ok = sha256_file(p) == e["sha256"]
            writable = bool(p.stat().st_mode & (stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH))
            report.append({"id": e["id"], "name": e["original_name"], "ok": ok and not writable,
                           "reason": None if ok and not writable else
                           ("Prüfsumme abweichend" if not ok else "Schreibschutz fehlt")})
        return report


def create_workcopy(vault_path: Path | str, sha256: str, label: str) -> Path:
    data = Vault.read_verified(vault_path, sha256)
    safe = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in label)[:40] or "copy"
    dest = workcopy_dir() / f"{sha256[:12]}_{safe}_{os.getpid()}_{len(list(workcopy_dir().iterdir()))}.bin"
    dest.write_bytes(data)
    return dest


def copy_readonly(src: Path, dest: Path) -> None:
    shutil.copy2(src, dest)
    os.chmod(dest, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
