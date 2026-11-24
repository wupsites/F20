"""OBD-, DTC- und SVK-Dekodierung."""

from f20.obd.pids import decode_obd_dtc, decode_obd_dtc_list, decode_pid, decode_supported
from f20.uds.dtc import decode_report_by_status
from f20.uds.svk import SgbmId, decode_svk


def test_pid_formulas():
    assert decode_pid(0x0C, bytes([0x1A, 0xF8])) == 1726.0      # (256*26+248)/4
    assert decode_pid(0x05, bytes([0x7B])) == 83
    assert decode_pid(0x06, bytes([0x80])) == 0.0
    assert decode_pid(0x42, bytes([0x37, 0x6E])) == 14.19
    assert decode_pid(0x10, bytes([0x01, 0xC2])) == 4.5


def test_supported_bitmask():
    assert decode_supported(0x00, bytes.fromhex("BE1FA813")) >= {0x01, 0x03, 0x04, 0x05, 0x0C, 0x0D, 0x20}


def test_obd_dtc():
    assert decode_obd_dtc(0x04, 0x20) == "P0420"
    assert decode_obd_dtc_list(bytes([0x02, 0x04, 0x20, 0xC1, 0x00])) == ["P0420", "U0100"]


def test_uds_dtc_status_bits():
    avail, dtcs = decode_report_by_status(0x40, bytes.fromhex("5902FF801C2028"))
    assert avail == 0xFF and dtcs[0].code_hex == "801C20" and dtcs[0].confirmed and not dtcs[0].active


def test_sgbm_roundtrip():
    s = SgbmId.parse("CAFD_000000F9_007_007_001")
    assert s.to_bytes().hex() == "05000000f9070701" and str(SgbmId.from_bytes(s.to_bytes())) == str(s)


def test_svk_documented_layout():
    entries = [SgbmId.parse(x) for x in ("HWEL_00001B25_004_004_001", "CAFD_00001B29_006_004_018")]
    head = bytes([0x01, 0x01, 0x00, 0x02, 0x18, 0x01, 0x30, 0x8A, 0x04, 0xD2]) + bytes(7)
    r = decode_svk(head + b"".join(e.to_bytes() for e in entries))
    assert not r.heuristic and r.prog_date == "2018-01-30" and r.prog_km == 12340
    assert r.to_dict()["cafd"] == ["CAFD_00001B29_006_004_018"]
