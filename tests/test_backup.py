"""Backup-Parser, Tresor/Integrität, Fahrzeugtrennung, Diff, Lernmodus, Layouts."""

import gzip
import hashlib
import json
import os

import pytest

from f20.backup.cod import CodFormatError, build_test_cod, clean_upload_name, parse_cod
from f20.backup.diff import diff_blocks, diff_bytes
from f20.backup.layouts import CafdNames, choose_layout, decode_with_names, layout_hash
from f20.backup.service import BackupService, mask_vin
from f20.store import Store

A, B = "DEMO0F20SIM000001", "DEMO0E87SIM000002"
BLK = {0x3000: bytes(range(32)), 0x3010: b"\x00" * 16}


def _after():
    d = dict(BLK)
    d[0x3000] = bytes(range(16)) + bytes([16 ^ 0x04]) + bytes(range(17, 32))
    return d


@pytest.fixture
def files(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    data = {
        f"0F1820-{A}-1600000000.cod": build_test_cod(A, "0F1820", 0x63, "000000F9", (7, 7, 1), BLK),
        f"d2139e4c-0F1820-{A}-1600003600.cod": build_test_cod(A, "0F1820", 0x63, "000000F9", (7, 7, 1), _after()),
        f"0F1820-{A}-1600007200.cod": build_test_cod(A, "0F1820", 0x63, "000000F9", (7, 7, 1), BLK),  # Duplikat
        f"KMBI_PL2C08-{B}-1700000000.cod": build_test_cod(B, "KMBI", 0x60, "00000ABC", (1, 2, 3), BLK),
    }
    for n, d in data.items():
        (src / n).write_bytes(d)
    return src


def test_parse_structure():
    c = parse_cod(build_test_cod(A, "0F1820", 0x63, "000000F9", (7, 7, 1), BLK), f"0F1820-{A}-1600000000.cod")
    assert (c.vin, c.ecu_identifier, c.diag_address, c.sgbm) == (A, "0F1820", 0x63, "CAFD_000000F9_007_007_001")
    assert c.blocks["3000"] == BLK[0x3000] and c.filename_ts == 1600000000


def test_parse_rejects_non_plist():
    with pytest.raises(CodFormatError):
        parse_cod(b"\xac\xed\x00\x05xxxx")
    with pytest.raises(CodFormatError):
        parse_cod(b"hello world")


def test_upload_prefix_removed():
    assert clean_upload_name(f"d2139e4c-0F1820-{A}-1600003600.cod") == f"0F1820-{A}-1600003600.cod"
    assert clean_upload_name("normal.cod") == "normal.cod"


def test_import_keeps_originals_untouched(files):
    before = {p.name: (hashlib.sha256(p.read_bytes()).hexdigest(), p.stat().st_mtime) for p in files.iterdir()}
    svc = BackupService(Store())
    svc.import_path(files)
    after = {p.name: (hashlib.sha256(p.read_bytes()).hexdigest(), p.stat().st_mtime) for p in files.iterdir()}
    assert before == after
    rep = svc.vault.verify(svc.store.list_backups())
    assert rep and all(r["ok"] for r in rep)
    for b in svc.store.list_backups():
        assert not os.access(b["vault_path"], os.W_OK) or os.geteuid() == 0
        assert oct(os.stat(b["vault_path"]).st_mode)[-3:] == "444"


def test_duplicates_become_aliases_and_vehicles_separated(files):
    svc = BackupService(Store())
    svc.import_path(files)
    assert len(svc.store.list_backups()) == 3
    vs = {v["vehicle_key"]: v for v in svc.vehicles()}
    assert set(vs) == {A, B}
    tl = [t for t in svc.timeline() if t["vehicle"] == A][0]
    assert len(tl["events"]) == 3 and [s["identical"] for s in tl["steps"]] == [False, False]
    assert tl["steps"][0]["detail"]["3000"]["changes"][0]["bits"] == [2]


def test_tampered_vault_detected(files):
    svc = BackupService(Store())
    svc.import_path(files)
    b = svc.store.list_backups()[0]
    os.chmod(b["vault_path"], 0o644)
    with open(b["vault_path"], "ab") as fh:
        fh.write(b"x")
    assert not [r for r in svc.vault.verify(svc.store.list_backups()) if r["id"] == b["id"]][0]["ok"]


def test_learn_and_decode(files):
    svc = BackupService(Store())
    svc.import_path(files)
    ids = {b["original_name"]: b["id"] for b in svc.store.list_backups()}
    a = ids[f"0F1820-{A}-1600000000.cod"]
    b = ids[f"0F1820-{A}-1600003600.cod"]
    assert len(svc.learn(a, b, "TEST")) == 1
    p = svc.decode(b)["parameters"]
    assert p[0]["name"] == "TEST" and p[0]["value_hex"] == "01"
    with pytest.raises(ValueError):
        svc.learn(a, ids[f"KMBI_PL2C08-{B}-1700000000.cod"], "X")   # anderes Fahrzeug


def test_simulation_never_touches_vault(files):
    svc = BackupService(Store())
    svc.import_path(files)
    b = svc.store.list_backups()[0]
    h = hashlib.sha256(open(b["vault_path"], "rb").read()).hexdigest()
    r = svc.simulate(b["id"], "3000", 1, 1, 0x01, "01")
    assert r["simulated"] and not r["written_to_vehicle"] and r["diff"]["identical"]  # Bit 0 von Byte 1 (0x01) war schon gesetzt
    r = svc.simulate(b["id"], "3000", 0, 0, 0x10, "01")
    assert r["diff"]["changes"][0]["bits"] == [4]
    assert hashlib.sha256(open(b["vault_path"], "rb").read()).hexdigest() == h


def test_diff_bits():
    d = diff_bytes(b"\x00\x0F", b"\x01\x0F")
    assert d["changes"][0]["bits"] == [0] and d["changed_bits"] == 1
    assert diff_blocks({"3000": b"\x00"}, {"3000": b"\x00"})["identical"]


def test_mask_vin():
    assert mask_vin("WBA0DEMO0SIM12345") == "WBA••••••••••2345"


def test_layout_hash_and_choice(tmp_path):
    funcs = [(0, 0, "00000011b"), (0, 0, "11111100b"), (1, 1, "11111111b")]
    h = layout_hash(funcs)
    rows = ["# kind\taddress\tlayout_hash\tstart\tend\tmask\tvalue_hex\tname", "G\t3000\t*\t\t\t\t\tTEST_GROUP"]
    rows += [f"F\t3000\t{h}\t0\t0\t00000011b\t\tFUNC_A", f"V\t3000\t{h}\t0\t0\t00000011b\t01\taktiv",
             f"V\t3000\t{h}\t0\t0\t00000011b\t00\tnicht_aktiv", f"F\t3000\t{h}\t0\t0\t11111100b\t\tFUNC_B",
             f"F\t3000\t{h}\t1\t1\t11111111b\t\tFUNC_C",
             "F\t3000\tdeadbeefdeadbeef\t5\t5\t11111111b\t\tTOO_LONG"]
    p = tmp_path / "000000AA.tsv.gz"
    p.write_bytes(gzip.compress("\n".join(rows).encode()))
    names = CafdNames.load(p)
    lay, info = choose_layout(names, "3000", b"\x01\x05")
    assert lay.complete and lay.hash == h and info["best"]["fits"]
    dec = decode_with_names({"3000": b"\x01\x05"}, names)
    f = {x["name"]: x for x in dec["blocks"]["3000"]["functions"]}
    assert f["FUNC_A"]["value_label"] == "aktiv" and f["FUNC_C"]["value_hex"] == "05"


def test_personal_excludes_foreign_vehicle(files, isolated_home):
    from f20.backup.personal import own_backups
    isolated_home.mkdir(parents=True, exist_ok=True)
    (isolated_home / "vehicle.local.json").write_text(json.dumps({"vin": A, "excluded_vins": [B]}))
    svc = BackupService(Store())
    svc.import_path(files)
    assert {b["vehicle_key"] for b in own_backups(svc)} == {A}
