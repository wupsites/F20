"""ELM327-Schicht gegen den Simulator: Init, Extended Addressing, Multi-Frame, Fehlerbilder, Schreibschutz."""

import pytest

from f20.safety import ReadOnlyViolation
from f20.transport.errors import AdapterDisconnected, AdapterUnsupported, BusError, NegativeResponse, NoData
from f20.transport.isotp import CanFrame, IsoTpError, parse_elm_frame_line, reassemble, segment
from f20.uds.client import DiagnosticClient


def test_isotp_roundtrip_extended():
    payload = bytes(range(40))
    frames = [CanFrame(0x640, f) for f in segment(payload, 0xF1)]
    assert len(frames) > 1 and all(f.data[0] == 0xF1 for f in frames)
    assert reassemble(frames, 0x640, extended=True) == [payload]


def test_isotp_detects_missing_consecutive_frame():
    frames = [CanFrame(0x640, f) for f in segment(bytes(range(40)), 0xF1)]
    del frames[2]
    with pytest.raises(IsoTpError):
        reassemble(frames, 0x640, extended=True)


def test_parse_line_with_and_without_spaces():
    a = parse_elm_frame_line("612 F1 10 14 62 F1 90 57 42")
    b = parse_elm_frame_line("612F110146 2F1905742".replace(" ", ""))
    assert parse_elm_frame_line("612 F1 10 14 62 F1 90 57 42 41") is None   # 9 Byte > CAN-Maximum
    assert a == b and a.can_id == 0x612 and a.data[0] == 0xF1
    assert parse_elm_frame_line("NO DATA") is None


async def test_init_and_identify(demo_elm):
    car, t, elm = demo_elm()
    await t.open()
    info = await elm.initialize()
    assert info.supports_cea and info.supports_fc_manual and info.voltage == 12.6
    dc = DiagnosticClient(elm)
    ident = await dc.identify(0x63, "HU_ENTRY")
    svk = ident.fields["svk"]["value"]
    assert "CAFD_000000F9_007_007_001" in svk["cafd"] and svk["heuristic"] is False
    assert ident.fields["vin"]["value"] == "DEMO0F20SIM000001"
    # Init-Sequenz für BMW Extended Addressing
    sent = " ".join(t.received_lines)
    for cmd in ("ATSH6F1", "ATCEA63", "ATCRA663", "ATFCSH6F1", "ATFCSD63300000", "ATFCSM1"):
        assert cmd in sent


async def test_response_pending_is_handled(demo_elm):
    car, t, elm = demo_elm()
    await t.open()
    await elm.initialize()
    data = await DiagnosticClient(elm).read_did(0x63, 0xF101)   # Simulator antwortet erst mit 7F 22 78
    assert len(data) > 17


async def test_negative_response(demo_elm):
    _, t, elm = demo_elm()
    await t.open()
    await elm.initialize()
    with pytest.raises(NegativeResponse) as exc:
        await DiagnosticClient(elm).read_did(0x40, 0x1234)
    assert exc.value.nrc == 0x31


async def test_write_never_reaches_vehicle(demo_elm):
    car, t, elm = demo_elm()
    await t.open()
    await elm.initialize()
    before = len(t.received_lines)
    for payload in (b"\x2E\x30\x00\x01", b"\x31\x01\x0F\x01", b"\x14\xFF\xFF\xFF", b"\x11\x01"):
        with pytest.raises(ReadOnlyViolation):
            await elm.uds_request(0x40, payload)
    assert len(t.received_lines) == before          # keine einzige Zeile gesendet
    assert car.all_write_attempts() == []


async def test_raw_line_injection_blocked(demo_elm):
    _, t, elm = demo_elm()
    await t.open()
    with pytest.raises(ReadOnlyViolation):
        await elm._send_line("2E300001")
    assert t.received_lines == []


async def test_adapter_without_cea(demo_elm):
    _, t, elm = demo_elm(supports_cea=False, version="ELM327 v1.5")
    await t.open()
    info = await elm.initialize()
    assert info.supports_cea is False and info.clone_suspected
    with pytest.raises(AdapterUnsupported):
        await elm.uds_request(0x40, b"\x22\xF1\x90")
    # Standard-OBD funktioniert trotzdem
    res = await elm.obd_request(b"\x01\x0C")
    assert 0x7E8 in res


async def test_raw_isotp_fallback(demo_elm):
    from f20.transport.elm327 import ElmConfig
    _, t, elm = demo_elm(supports_cea=False)
    elm.config = ElmConfig(raw_isotp_fallback=True)
    await t.open()
    await elm.initialize()
    data = await DiagnosticClient(elm).read_did(0x40, 0xF190)
    assert data == b"DEMO0F20SIM000001"


async def test_missing_flow_control_detected(demo_elm):
    from f20.transport.elm327 import ElmConfig
    from f20.transport.errors import AdapterError
    _, t, elm = demo_elm()
    elm.config = ElmConfig(manual_flow_control=False)   # ELM schickt FC an falsche ID → ECU schweigt
    await t.open()
    await elm.initialize()
    with pytest.raises(AdapterError):
        await DiagnosticClient(elm).read_did(0x40, 0xF190)


async def test_disconnect(demo_elm):
    _, t, elm = demo_elm(disconnect_after_writes=12)
    await t.open()
    with pytest.raises(AdapterDisconnected):
        await elm.initialize()
        for _ in range(5):
            await elm.uds_request(0x40, b"\x22\xF1\x90")


async def test_bus_error_and_no_data(demo_elm):
    _, t, elm = demo_elm(forced_responses=["CAN ERROR"])
    await t.open()
    await elm.initialize()
    with pytest.raises(BusError):
        await elm.obd_request(b"\x01\x0C")
    car, t2, elm2 = demo_elm()
    car.ignition_on = False
    await t2.open()
    await elm2.initialize()
    with pytest.raises(NoData):
        await elm2.obd_request(b"\x01\x0C")


async def test_obd_supported_and_unavailable(demo_elm):
    _, t, elm = demo_elm()
    await t.open()
    await elm.initialize()
    dc = DiagnosticClient(elm)
    sup = await dc.obd_supported_pids()
    assert 0x0C in sup and 0x5C not in sup
    assert await dc.obd_read(0x5C) is None             # Öltemperatur: nicht verfügbar, nicht erfunden
    r = await dc.obd_read(0x0C)
    assert r.unit == "1/min" and 500 < r.value < 8000
    assert await dc.obd_vin() == "DEMO0F20SIM000001"


async def test_dtc_read(demo_elm):
    _, t, elm = demo_elm()
    await t.open()
    await elm.initialize()
    dtcs = await DiagnosticClient(elm).read_dtcs(0x40)
    assert dtcs and dtcs[0]["code"] == "DE0001" and dtcs[0]["confirmed"]
