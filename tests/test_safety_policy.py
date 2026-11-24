"""Read-only-Schutz: alles, was das Fahrzeug oder den Adapter verändern könnte, wird blockiert."""

import pytest

from f20.safety import ReadOnlyPolicy, ReadOnlyViolation, UDS_FORBIDDEN

P = ReadOnlyPolicy()


@pytest.mark.parametrize("payload", [
    b"\x22\xF1\x90", b"\x22\x30\x00", b"\x19\x02\xFF", b"\x19\x02\x0C", b"\x3E\x00", b"\x3E\x80", b"\x10\x01",
])
def test_reads_allowed(payload):
    assert P.check_uds(payload, 0x40).allowed


@pytest.mark.parametrize("sid", sorted(UDS_FORBIDDEN))
def test_all_forbidden_services_blocked(sid):
    with pytest.raises(ReadOnlyViolation):
        P.enforce_uds(bytes([sid, 0x00, 0x00]), 0x40)


@pytest.mark.parametrize("payload", [
    b"\x2E\x30\x00\x01",          # WriteDataByIdentifier (Codierung)
    b"\x31\x01\x0F\x01",          # RoutineControl
    b"\x14\xFF\xFF\xFF",          # Fehlerspeicher löschen
    b"\x11\x01",                  # ECU-Reset
    b"\x27\x01",                  # SecurityAccess
    b"\x10\x02", b"\x10\x03", b"\x10\x41",  # Programmier-/Extended-/Codier-Session
    b"\x19\x14", b"\x3E\x01",     # unbekannte Subfunktionen
    b"\x22\xF1",                  # unvollständig
    b"\x22\xF1\x90\xF1\x8C",      # mehrere DIDs
    b"\xBA", b"",                 # unbekannt / leer
])
def test_dangerous_or_malformed_blocked(payload):
    assert not P.check_uds(payload, 0x40).allowed


def test_coding_read_can_be_disabled():
    p = ReadOnlyPolicy(allow_coding_read=False)
    assert not p.check_uds(b"\x22\x30\x00", 0x40).allowed
    assert p.check_uds(b"\x22\xF1\x90", 0x40).allowed


@pytest.mark.parametrize("mode", [0x04, 0x08, 0x05, 0x0B])
def test_obd_forbidden_modes(mode):
    with pytest.raises(ReadOnlyViolation):
        P.enforce_obd(bytes([mode]))


@pytest.mark.parametrize("cmd", ["ATZ", "ATE0", "ATSH6F1", "ATCEA40", "ATCEA", "ATCRA640", "ATFCSD40300000",
                                 "ATFCSM1", "ATSP6", "ATST64", "ATRV", "STI", "at sh 6f1"])
def test_at_allowed(cmd):
    P.check_at(cmd)


@pytest.mark.parametrize("cmd", ["ATPP0CSV23", "ATPP0CON", "AT@3 ABC", "ATBRD08", "ATMA", "ATM1", "STSBR500000",
                                 "ATWM8113F13E", "22F190", "ATXYZ"])
def test_at_blocked(cmd):
    with pytest.raises(ReadOnlyViolation):
        P.check_at(cmd)


def test_audit_log_records_decisions():
    p = ReadOnlyPolicy()
    p.check_uds(b"\x2E\x30\x00\x01", 0x40)
    assert p.audit[-1][2] is False and "WriteDataByIdentifier" in p.audit[-1][3]
