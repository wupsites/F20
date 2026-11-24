"""Lokale SQLite-Datenbank (Backups, Diagnosen, Messwerte, Änderungen, Planung).

Liegt unter $F20_HOME/f20.sqlite3 – niemals im Git-Repository.
"""

from __future__ import annotations

import json
import sqlite3
import threading
import time
from pathlib import Path
from typing import Any

from .paths import db_path

SCHEMA = """
PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS backups (
    id INTEGER PRIMARY KEY,
    sha256 TEXT UNIQUE NOT NULL,
    original_name TEXT NOT NULL,
    source_path TEXT,
    source_mtime REAL,
    imported_at REAL NOT NULL,
    size INTEGER NOT NULL,
    vault_path TEXT NOT NULL,
    vehicle_key TEXT,
    format TEXT,
    meta_json TEXT
);
CREATE TABLE IF NOT EXISTS diag_sessions (
    id INTEGER PRIMARY KEY,
    started_at REAL NOT NULL,
    finished_at REAL,
    mode TEXT NOT NULL,              -- 'demo' | 'real'
    adapter_json TEXT,
    summary_json TEXT
);
CREATE TABLE IF NOT EXISTS readings (
    id INTEGER PRIMARY KEY,
    session_id INTEGER NOT NULL,
    ts REAL NOT NULL,
    key TEXT NOT NULL,
    name_de TEXT,
    value_json TEXT,
    unit TEXT,
    source TEXT,
    raw_hex TEXT
);
CREATE INDEX IF NOT EXISTS idx_readings_key ON readings(key, ts);
CREATE TABLE IF NOT EXISTS ecu_identities (
    id INTEGER PRIMARY KEY,
    session_id INTEGER NOT NULL,
    address TEXT NOT NULL,
    name TEXT,
    data_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS dtc_records (
    id INTEGER PRIMARY KEY,
    session_id INTEGER NOT NULL,
    source TEXT NOT NULL,            -- ECU-Adresse oder 'OBD'
    data_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS change_log (
    id INTEGER PRIMARY KEY,
    ts REAL NOT NULL,
    kind TEXT NOT NULL,              -- 'plan' | 'applied_bimmercode' | 'reverted' | 'note'
    option_id TEXT,
    from_value TEXT,
    to_value TEXT,
    note TEXT,
    backup_before INTEGER,
    backup_after INTEGER
);
CREATE TABLE IF NOT EXISTS plan_items (
    id INTEGER PRIMARY KEY,
    option_id TEXT NOT NULL,
    target_value TEXT,
    note TEXT,
    created_at REAL NOT NULL,
    status TEXT NOT NULL DEFAULT 'planned'   -- 'planned' | 'done' | 'dropped'
);
CREATE TABLE IF NOT EXISTS mapping_observations (
    id INTEGER PRIMARY KEY,
    created_at REAL NOT NULL,
    label TEXT NOT NULL,
    scope TEXT,                      -- z. B. CAFD-ID oder Blockname
    byte_offset INTEGER NOT NULL,
    mask INTEGER NOT NULL,
    before INTEGER NOT NULL,
    after INTEGER NOT NULL,
    backup_a INTEGER,
    backup_b INTEGER,
    note TEXT
);
CREATE TABLE IF NOT EXISTS workcopies (
    id INTEGER PRIMARY KEY,
    backup_id INTEGER NOT NULL,
    path TEXT NOT NULL,
    created_at REAL NOT NULL,
    note TEXT
);
"""


class Store:
    def __init__(self, path: Path | str | None = None) -> None:
        self.path = Path(path) if path else db_path()
        self._lock = threading.RLock()
        self.conn = sqlite3.connect(str(self.path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        with self._lock:
            self.conn.executescript(SCHEMA)

    def close(self) -> None:
        self.conn.close()

    def _exec(self, sql: str, args: tuple = ()) -> sqlite3.Cursor:
        with self._lock:
            cur = self.conn.execute(sql, args)
            self.conn.commit()
            return cur

    def _all(self, sql: str, args: tuple = ()) -> list[dict]:
        with self._lock:
            return [dict(r) for r in self.conn.execute(sql, args).fetchall()]

    def _one(self, sql: str, args: tuple = ()) -> dict | None:
        rows = self._all(sql, args)
        return rows[0] if rows else None

    # ------------------------------------------------------------ Backups
    def add_backup(self, *, sha256: str, original_name: str, source_path: str | None, source_mtime: float | None,
                   size: int, vault_path: str, vehicle_key: str | None, fmt: str | None, meta: dict) -> int:
        existing = self.backup_by_sha(sha256)
        if existing:
            return existing["id"]
        cur = self._exec(
            "INSERT INTO backups(sha256, original_name, source_path, source_mtime, imported_at, size, vault_path,"
            " vehicle_key, format, meta_json) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (sha256, original_name, source_path, source_mtime, time.time(), size, vault_path, vehicle_key, fmt,
             json.dumps(meta, ensure_ascii=False)),
        )
        return int(cur.lastrowid)

    def update_backup_meta(self, backup_id: int, *, vehicle_key: str | None, fmt: str | None, meta: dict) -> None:
        self._exec("UPDATE backups SET vehicle_key=?, format=?, meta_json=? WHERE id=?",
                   (vehicle_key, fmt, json.dumps(meta, ensure_ascii=False), backup_id))

    def backup_by_sha(self, sha256: str) -> dict | None:
        return self._decode_backup(self._one("SELECT * FROM backups WHERE sha256=?", (sha256,)))

    def get_backup(self, backup_id: int) -> dict | None:
        return self._decode_backup(self._one("SELECT * FROM backups WHERE id=?", (backup_id,)))

    def list_backups(self) -> list[dict]:
        return [self._decode_backup(r) for r in self._all("SELECT * FROM backups ORDER BY original_name")]

    @staticmethod
    def _decode_backup(row: dict | None) -> dict | None:
        if row is None:
            return None
        row = dict(row)
        row["meta"] = json.loads(row.pop("meta_json") or "{}")
        return row

    # ------------------------------------------------------------ Sessions
    def start_session(self, mode: str, adapter: dict) -> int:
        cur = self._exec("INSERT INTO diag_sessions(started_at, mode, adapter_json) VALUES (?,?,?)",
                         (time.time(), mode, json.dumps(adapter, ensure_ascii=False)))
        return int(cur.lastrowid)

    def finish_session(self, session_id: int, summary: dict) -> None:
        self._exec("UPDATE diag_sessions SET finished_at=?, summary_json=? WHERE id=?",
                   (time.time(), json.dumps(summary, ensure_ascii=False), session_id))

    def list_sessions(self, limit: int = 20) -> list[dict]:
        rows = self._all("SELECT * FROM diag_sessions ORDER BY id DESC LIMIT ?", (limit,))
        for r in rows:
            r["adapter"] = json.loads(r.pop("adapter_json") or "{}")
            r["summary"] = json.loads(r.pop("summary_json") or "null")
        return rows

    def add_readings(self, session_id: int, readings: list[Any]) -> None:
        with self._lock:
            self.conn.executemany(
                "INSERT INTO readings(session_id, ts, key, name_de, value_json, unit, source, raw_hex)"
                " VALUES (?,?,?,?,?,?,?,?)",
                [(session_id, r.ts, r.key, r.name_de, json.dumps(r.value), r.unit, r.source, r.raw_hex)
                 for r in readings],
            )
            self.conn.commit()

    def latest_readings(self, mode: str | None = None) -> list[dict]:
        sql = ("SELECT r.*, s.mode FROM readings r JOIN diag_sessions s ON s.id=r.session_id "
               "WHERE r.id IN (SELECT MAX(r2.id) FROM readings r2 JOIN diag_sessions s2 ON s2.id=r2.session_id"
               + (" WHERE s2.mode=?" if mode else "") + " GROUP BY r2.key) ORDER BY r.key")
        rows = self._all(sql, (mode,) if mode else ())
        for r in rows:
            r["value"] = json.loads(r.pop("value_json"))
        return rows

    def reading_history(self, key: str, limit: int = 600) -> list[dict]:
        rows = self._all("SELECT ts, value_json FROM readings WHERE key=? ORDER BY id DESC LIMIT ?", (key, limit))
        return [{"ts": r["ts"], "value": json.loads(r["value_json"])} for r in reversed(rows)]

    def save_identity(self, session_id: int, ident: dict) -> None:
        self._exec("INSERT INTO ecu_identities(session_id, address, name, data_json) VALUES (?,?,?,?)",
                   (session_id, ident["address"], ident.get("name"), json.dumps(ident, ensure_ascii=False)))

    def save_dtcs(self, session_id: int, source: str, data: Any) -> None:
        self._exec("INSERT INTO dtc_records(session_id, source, data_json) VALUES (?,?,?)",
                   (session_id, source, json.dumps(data, ensure_ascii=False)))

    def latest_diagnosis(self, mode: str | None = None) -> dict | None:
        sql = "SELECT * FROM diag_sessions WHERE summary_json IS NOT NULL"
        args: tuple = ()
        if mode:
            sql += " AND mode=?"
            args = (mode,)
        s = self._one(sql + " ORDER BY id DESC LIMIT 1", args)
        if not s:
            return None
        sid = s["id"]
        return {
            "session": {"id": sid, "mode": s["mode"], "started_at": s["started_at"],
                        "finished_at": s["finished_at"], "adapter": json.loads(s["adapter_json"] or "{}"),
                        "summary": json.loads(s["summary_json"] or "null")},
            "ecus": [json.loads(r["data_json"]) for r in
                     self._all("SELECT data_json FROM ecu_identities WHERE session_id=? ORDER BY address", (sid,))],
            "dtcs": [{"source": r["source"], "data": json.loads(r["data_json"])} for r in
                     self._all("SELECT source, data_json FROM dtc_records WHERE session_id=?", (sid,))],
        }

    # ------------------------------------------------------------ Änderungen & Planung
    def add_change(self, kind: str, option_id: str | None = None, from_value: str | None = None,
                   to_value: str | None = None, note: str | None = None, backup_before: int | None = None,
                   backup_after: int | None = None) -> int:
        if kind not in ("plan", "applied_bimmercode", "reverted", "note"):
            raise ValueError("Ungültige Änderungsart")
        cur = self._exec(
            "INSERT INTO change_log(ts, kind, option_id, from_value, to_value, note, backup_before, backup_after)"
            " VALUES (?,?,?,?,?,?,?,?)",
            (time.time(), kind, option_id, from_value, to_value, note, backup_before, backup_after))
        return int(cur.lastrowid)

    def list_changes(self) -> list[dict]:
        return self._all("SELECT * FROM change_log ORDER BY ts DESC")

    def add_plan_item(self, option_id: str, target_value: str | None, note: str | None) -> int:
        cur = self._exec("INSERT INTO plan_items(option_id, target_value, note, created_at) VALUES (?,?,?,?)",
                         (option_id, target_value, note, time.time()))
        self.add_change("plan", option_id, None, target_value, note)
        return int(cur.lastrowid)

    def set_plan_status(self, item_id: int, status: str) -> None:
        if status not in ("planned", "done", "dropped"):
            raise ValueError("Ungültiger Status")
        self._exec("UPDATE plan_items SET status=? WHERE id=?", (status, item_id))

    def list_plan(self) -> list[dict]:
        return self._all("SELECT * FROM plan_items ORDER BY created_at")

    # ------------------------------------------------------------ Lernmodus
    def add_observation(self, *, label: str, scope: str | None, byte_offset: int, mask: int, before: int,
                        after: int, backup_a: int | None, backup_b: int | None, note: str | None = None) -> int:
        cur = self._exec(
            "INSERT INTO mapping_observations(created_at, label, scope, byte_offset, mask, before, after,"
            " backup_a, backup_b, note) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (time.time(), label, scope, byte_offset, mask, before, after, backup_a, backup_b, note))
        return int(cur.lastrowid)

    def list_observations(self, scope: str | None = None) -> list[dict]:
        if scope:
            return self._all("SELECT * FROM mapping_observations WHERE scope=? ORDER BY byte_offset", (scope,))
        return self._all("SELECT * FROM mapping_observations ORDER BY scope, byte_offset")

    # ------------------------------------------------------------ Arbeitskopien
    def add_workcopy(self, backup_id: int, path: str, note: str | None) -> int:
        cur = self._exec("INSERT INTO workcopies(backup_id, path, created_at, note) VALUES (?,?,?,?)",
                         (backup_id, path, time.time(), note))
        return int(cur.lastrowid)

    def get_workcopy(self, wc_id: int) -> dict | None:
        return self._one("SELECT * FROM workcopies WHERE id=?", (wc_id,))

    def list_workcopies(self) -> list[dict]:
        return self._all("SELECT * FROM workcopies ORDER BY id DESC")
